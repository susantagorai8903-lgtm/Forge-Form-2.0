import asyncio
import json
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.main import app
from app.models import Notification, ProcessedEvent
from app.workers import notification_worker
from app.core.config import settings


@pytest.mark.asyncio
async def test_notification_consumer_deduplicates_event(client, monkeypatch):
    event_id = uuid4()
    test_sessions = app.state.test_sessions
    async with test_sessions() as session:
        notification = Notification(
            idempotency_key=str(uuid4()),
            recipient="customer@example.com",
            notification_type="contact.received",
            subject="We received your enquiry",
            message="We will follow up.",
            status="PENDING",
        )
        session.add(notification)
        await session.commit()
        notification_id = notification.id

    calls = 0

    async def fake_send(_notification):
        nonlocal calls
        calls += 1

    monkeypatch.setattr(notification_worker, "SessionLocal", test_sessions)
    monkeypatch.setattr(notification_worker, "send_notification", fake_send)
    event = {
        "event_id": str(event_id),
        "event_type": "forgeform.notification.requested",
        "correlation_id": "test-correlation",
        "payload": {"notification_id": str(notification_id)},
    }
    await notification_worker.process_notification_event(event)
    await notification_worker.process_notification_event(event)

    async with test_sessions() as session:
        processed = await session.scalar(select(ProcessedEvent).where(ProcessedEvent.event_id == event_id))
        sent = await session.get(Notification, notification_id)
        assert processed is not None
        assert sent.status == "SENT"
        assert sent.sent_at is not None
    assert calls == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event",
    [
        {},
        {"payload": {}},
        {"payload": {"notification_id": "not-a-uuid"}},
    ],
)
async def test_mark_notification_failed_ignores_missing_or_invalid_ids(event):
    await notification_worker.mark_notification_failed(event)


@pytest.mark.asyncio
async def test_dead_letter_publish_failure_does_not_commit_or_stop_worker(monkeypatch):
    event_holder = []
    consumer_options = {}
    consumer_state = {"getone_calls": 0, "commits": 0, "seeks": []}

    class StopEvent:
        def __init__(self):
            self.stopped = False
            event_holder.append(self)

        def is_set(self):
            return self.stopped

        def set(self):
            self.stopped = True

    class FakeConsumer:
        def __init__(self, *_args, **kwargs):
            consumer_options.update(kwargs)

        async def start(self):
            pass

        async def stop(self):
            pass

        async def getone(self):
            consumer_state["getone_calls"] += 1
            if consumer_state["getone_calls"] == 1:
                event = {
                    "event_id": str(uuid4()),
                    "event_type": "forgeform.notification.requested",
                    "payload": {"notification_id": str(uuid4())},
                }
                return SimpleNamespace(
                    value=json.dumps(event).encode(),
                    topic="notifications",
                    partition=0,
                    offset=4,
                    topic_partition=("notifications", 0),
                )
            event_holder[0].set()
            raise TimeoutError

        async def commit(self):
            consumer_state["commits"] += 1

        def seek(self, topic_partition, offset):
            consumer_state["seeks"].append((topic_partition, offset))

    class FakeProducer:
        def __init__(self, *_args, **_kwargs):
            pass

        async def start(self):
            pass

        async def stop(self):
            pass

        async def send_and_wait(self, *_args, **_kwargs):
            raise RuntimeError("dead-letter publish failed")

    async def fail_processing(_event):
        raise RuntimeError("processing failed")

    async def no_wait(_seconds):
        pass

    monkeypatch.setattr(settings, "kafka_bootstrap_servers", "localhost:9092")
    monkeypatch.setattr(notification_worker, "AIOKafkaConsumer", FakeConsumer)
    monkeypatch.setattr(notification_worker, "AIOKafkaProducer", FakeProducer)
    monkeypatch.setattr(notification_worker, "process_notification_event", fail_processing)
    monkeypatch.setattr(
        notification_worker,
        "asyncio",
        SimpleNamespace(
            Event=StopEvent,
            get_running_loop=asyncio.get_running_loop,
            wait_for=asyncio.wait_for,
            sleep=no_wait,
        ),
    )

    await notification_worker.run()

    assert consumer_options["auto_offset_reset"] == "earliest"
    assert consumer_state["commits"] == 0
    assert consumer_state["seeks"] == [(("notifications", 0), 4)]
