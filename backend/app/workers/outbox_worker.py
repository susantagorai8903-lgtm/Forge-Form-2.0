import asyncio
import logging
import signal
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.database.session import SessionLocal
from app.kafka.producer import build_producer, publish_event
from app.models import EventOutbox

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)
MAX_RETRIES = 8
POLL_INTERVAL_SECONDS = 2


async def run() -> None:
    producer = build_producer()
    await producer.start()
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signum in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(signum, stop_event.set)
        except NotImplementedError:
            pass
    try:
        while not stop_event.is_set():
            processed = await publish_batch(producer)
            if not processed:
                try:
                    await asyncio.wait_for(stop_event.wait(), timeout=POLL_INTERVAL_SECONDS)
                except TimeoutError:
                    pass
    finally:
        await producer.stop()


async def publish_batch(producer) -> bool:
    async with SessionLocal() as session:
        async with session.begin():
            rows = (await session.scalars(
                select(EventOutbox)
                .where(EventOutbox.status == "PENDING")
                .where((EventOutbox.next_attempt_at.is_(None)) | (EventOutbox.next_attempt_at <= datetime.now(timezone.utc)))
                .order_by(EventOutbox.created_at)
                .limit(50)
                .with_for_update(skip_locked=True)
            )).all()
            if not rows:
                return False
            for row in rows:
                try:
                    await publish_event(producer, row.event_type, row.payload, str(row.aggregate_id))
                    row.status = "PUBLISHED"
                    row.published_at = datetime.now(timezone.utc)
                except Exception:
                    row.retry_count += 1
                    if row.retry_count >= MAX_RETRIES:
                        row.status = "FAILED"
                        logger.exception(
                            "outbox_event_permanently_failed",
                            extra={"event_id": str(row.event_id), "event_type": row.event_type, "retry_count": row.retry_count},
                        )
                    else:
                        row.next_attempt_at = datetime.now(timezone.utc) + timedelta(
                            seconds=min(2 ** row.retry_count, 300)
                        )
                        logger.exception(
                            "outbox_event_publish_failed",
                            extra={"event_id": str(row.event_id), "event_type": row.event_type, "retry_count": row.retry_count},
                        )
                    break
    return True


if __name__ == "__main__":
    asyncio.run(run())
