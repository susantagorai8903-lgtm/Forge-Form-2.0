import json
import logging
from typing import Any

from aiokafka import AIOKafkaProducer

from app.core.config import settings
from app.kafka.topics import topic_for_event

logger = logging.getLogger(__name__)


def build_producer() -> AIOKafkaProducer:
    config: dict[str, Any] = {
        "bootstrap_servers": settings.kafka_bootstrap_servers,
        "security_protocol": settings.kafka_security_protocol,
        "value_serializer": lambda value: json.dumps(value, separators=(",", ":"), default=str).encode("utf-8"),
        "key_serializer": lambda value: value.encode("utf-8") if value else None,
        "acks": "all",
        "enable_idempotence": True,
        "request_timeout_ms": 30000,
        "retry_backoff_ms": 500,
    }
    if settings.kafka_sasl_mechanism:
        config.update(
            sasl_mechanism=settings.kafka_sasl_mechanism,
            sasl_plain_username=settings.kafka_sasl_username,
            sasl_plain_password=settings.kafka_sasl_password,
        )
    return AIOKafkaProducer(**config)


async def publish_event(producer: AIOKafkaProducer, event_type: str, payload: dict[str, Any], aggregate_id: str) -> None:
    topic = topic_for_event(event_type)
    await producer.send_and_wait(topic, payload, key=aggregate_id)
    logger.info("kafka_event_published", extra={"topic": topic, "event_type": event_type, "aggregate_id": aggregate_id})
