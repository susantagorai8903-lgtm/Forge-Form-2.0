from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.main import app
from app.models import EventOutbox
from app.workers import outbox_worker


@pytest.mark.asyncio
@pytest.mark.parametrize(("retry_count", "expected_status"), [(0, "PENDING"), (7, "FAILED")])
async def test_publish_batch_stops_after_first_failure(
    client, monkeypatch, retry_count: int, expected_status: str
):
    test_sessions = app.state.test_sessions
    first_id = uuid4()
    second_id = uuid4()
    async with test_sessions() as session:
        session.add_all([
            EventOutbox(
                event_id=first_id,
                aggregate_type="test",
                aggregate_id=uuid4(),
                event_type="test.first",
                payload={},
                retry_count=retry_count,
                created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            ),
            EventOutbox(
                event_id=second_id,
                aggregate_type="test",
                aggregate_id=uuid4(),
                event_type="test.second",
                payload={},
                created_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
            ),
        ])
        await session.commit()

    published: list[str] = []

    async def fail_publish(_producer, _event_type, _payload, aggregate_id):
        published.append(aggregate_id)
        raise RuntimeError("publish failed")

    monkeypatch.setattr(outbox_worker, "SessionLocal", test_sessions)
    monkeypatch.setattr(outbox_worker, "publish_event", fail_publish)

    assert await outbox_worker.publish_batch(None) is True

    async with test_sessions() as session:
        first = await session.scalar(select(EventOutbox).where(EventOutbox.event_id == first_id))
        second = await session.scalar(select(EventOutbox).where(EventOutbox.event_id == second_id))

    assert len(published) == 1
    assert first.retry_count == retry_count + 1
    assert first.status == expected_status
    assert second.status == "PENDING"
    if expected_status == "PENDING":
        assert first.next_attempt_at is not None
    else:
        assert first.next_attempt_at is None
