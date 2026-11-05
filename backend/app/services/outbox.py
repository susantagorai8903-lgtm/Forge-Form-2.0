from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EventOutbox, Notification


def add_outbox_event(
    aggregate_type: str,
    aggregate_id: UUID,
    event_type: str,
    payload: dict[str, Any],
    correlation_id: str | None = None,
) -> EventOutbox:
    event_id = UUID(payload["event_id"]) if payload.get("event_id") else uuid4()
    correlation_id = correlation_id or str(uuid4())
    envelope = {
        "event_id": str(event_id),
        "event_type": event_type,
        "event_version": 1,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "aggregate_id": str(aggregate_id),
        "correlation_id": correlation_id,
        "source": "forgeform-api",
        "payload": payload,
    }
    return EventOutbox(
        event_id=event_id,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        event_type=event_type,
        payload=envelope,
    )


async def queue_notification(
    db: AsyncSession,
    aggregate_id: UUID,
    recipient: str,
    notification_type: str,
    subject: str,
    message: str,
    correlation_id: str | None = None,
) -> Notification:
    notification = Notification(
        recipient=recipient,
        notification_type=notification_type,
        subject=subject,
        message=message,
        idempotency_key=str(uuid4()),
    )
    db.add(notification)
    await db.flush()
    db.add(add_outbox_event(
        "notification",
        notification.id,
        "forgeform.notification.requested",
        {"notification_id": str(notification.id), "aggregate_id": str(aggregate_id)},
        correlation_id,
    ))
    return notification
