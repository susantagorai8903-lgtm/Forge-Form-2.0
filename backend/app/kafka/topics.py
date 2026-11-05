TOPICS = {
    "booking.created": "forgeform.booking.created",
    "booking.confirmed": "forgeform.booking.confirmed",
    "booking.cancelled": "forgeform.booking.cancelled",
    "booking.updated": "forgeform.booking.updated",
    "contact.created": "forgeform.contact.created",
    "contact.updated": "forgeform.contact.updated",
    "notification.requested": "forgeform.notification.requested",
    "notification.sent": "forgeform.notification.sent",
    "notification.failed": "forgeform.notification.failed",
    "analytics.event": "forgeform.analytics.event",
    "program.updated": "forgeform.program.updated",
    "trainer.updated": "forgeform.trainer.updated",
}
DEAD_LETTER_TOPIC = "forgeform.events.dlq"


def topic_for_event(event_type: str) -> str:
    key = event_type.removeprefix("forgeform.")
    if key not in TOPICS:
        raise ValueError(f"No Kafka topic configured for event type {event_type}")
    return TOPICS[key]
