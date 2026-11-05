import asyncio
import json
import logging
import signal
from datetime import datetime, timezone
from uuid import UUID

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sqlalchemy import select

from app.core.config import settings
from app.database.session import SessionLocal
from app.models import Notification, ProcessedEvent
from app.services.email_service import send_notification
from app.services.outbox import add_outbox_event
from app.kafka.topics import DEAD_LETTER_TOPIC, TOPICS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)
HANDLER_NAME = "notification"
MAX_ATTEMPTS = 5


def kafka_auth_config() -> dict:
    config = {"security_protocol": settings.kafka_security_protocol}
    if settings.kafka_sasl_mechanism:
        config.update(
            sasl_mechanism=settings.kafka_sasl_mechanism,
            sasl_plain_username=settings.kafka_sasl_username,
            sasl_plain_password=settings.kafka_sasl_password,
        )
    return config


async def process_notification_event(event: dict) -> None:
    event_id = UUID(event["event_id"])
    notification_id = UUID(event["payload"]["notification_id"])
    async with SessionLocal() as session:
        processed = await session.get(ProcessedEvent, {"event_id": event_id, "handler": HANDLER_NAME})
        if processed is not None:
            return
        notification = await session.get(Notification, notification_id)
        if notification is None:
            raise ValueError(f"Notification {notification_id} does not exist")
        if notification.status != "SENT":
            await send_notification(notification)
            notification.status = "SENT"
            notification.sent_at = datetime.now(timezone.utc)
            session.add(add_outbox_event(
                "notification",
                notification.id,
                "forgeform.notification.sent",
                {"notification_id": str(notification.id), "notification_type": notification.notification_type},
                event.get("correlation_id"),
            ))
        session.add(ProcessedEvent(event_id=event_id, handler=HANDLER_NAME))
        await session.commit()


async def mark_notification_failed(event: dict) -> None:
    payload = event.get("payload")
    if not isinstance(payload, dict):
        logger.warning("notification_failure_missing_payload", extra={"event_id": event.get("event_id")})
        return
    try:
        notification_id = UUID(payload.get("notification_id"))
    except (AttributeError, TypeError, ValueError):
        logger.warning("notification_failure_invalid_id", extra={"event_id": event.get("event_id")})
        return
    async with SessionLocal() as session:
        notification = await session.get(Notification, notification_id)
        if notification is not None:
            notification.status = "FAILED"
            notification.retry_count += MAX_ATTEMPTS
            session.add(add_outbox_event(
                "notification",
                notification.id,
                "forgeform.notification.failed",
                {"notification_id": str(notification.id), "notification_type": notification.notification_type},
                event.get("correlation_id"),
            ))
            await session.commit()


async def run() -> None:
    if not settings.kafka_bootstrap_servers:
        raise RuntimeError("KAFKA_BOOTSTRAP_SERVERS is required for the notification worker")
    consumer = AIOKafkaConsumer(
        TOPICS["notification.requested"],
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=f"{settings.kafka_consumer_group_id}-notifications",
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        **kafka_auth_config(),
    )
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer=lambda value: json.dumps(value, separators=(",", ":"), default=str).encode("utf-8"),
        key_serializer=lambda value: value.encode("utf-8") if value else None,
        **kafka_auth_config(),
    )
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signum in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(signum, stop_event.set)
        except NotImplementedError:
            pass
    producer_started = False
    consumer_started = False
    try:
        await producer.start()
        producer_started = True
        await consumer.start()
        consumer_started = True
        while not stop_event.is_set():
            try:
                message = await asyncio.wait_for(consumer.getone(), timeout=1)
            except TimeoutError:
                continue
            try:
                event = json.loads(message.value.decode("utf-8"))
                if not isinstance(event, dict):
                    raise ValueError("Notification event must be a JSON object")
            except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
                logger.warning(
                    "notification_event_unparseable",
                    extra={"topic": message.topic, "partition": message.partition, "offset": message.offset},
                    exc_info=True,
                )
                await consumer.commit()
                continue
            for attempt in range(1, MAX_ATTEMPTS + 1):
                try:
                    await process_notification_event(event)
                    await consumer.commit()
                    break
                except Exception as exc:
                    if attempt < MAX_ATTEMPTS:
                        logger.exception(
                            "notification_processing_retry",
                            extra={"event_id": event.get("event_id"), "attempt": attempt},
                        )
                        await asyncio.sleep(min(2 ** attempt, 30))
                        continue
                    dead_letter = {
                        "event_id": event.get("event_id"),
                        "event_type": event.get("event_type"),
                        "failed_at": datetime.now(timezone.utc).isoformat(),
                        "error_type": type(exc).__name__,
                        "payload": event,
                    }
                    try:
                        await producer.send_and_wait(DEAD_LETTER_TOPIC, dead_letter, key=str(event.get("aggregate_id", "")))
                        await mark_notification_failed(event)
                        await consumer.commit()
                    except Exception:
                        logger.exception(
                            "notification_dead_letter_failed",
                            extra={"event_id": event.get("event_id"), "attempts": attempt},
                        )
                        consumer.seek(message.topic_partition, message.offset)
                        await asyncio.sleep(min(2 ** attempt, 30))
                        break
                    logger.exception(
                        "notification_processing_dead_lettered",
                        extra={"event_id": event.get("event_id"), "attempts": attempt},
                    )
    finally:
        if consumer_started:
            await consumer.stop()
        if producer_started:
            await producer.stop()


if __name__ == "__main__":
    asyncio.run(run())
