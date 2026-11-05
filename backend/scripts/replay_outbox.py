import argparse
import asyncio
from uuid import UUID

from sqlalchemy import select

from app.database.session import SessionLocal
from app.models import EventOutbox


async def replay(event_id: UUID) -> None:
    async with SessionLocal() as session:
        event = await session.scalar(select(EventOutbox).where(EventOutbox.event_id == event_id))
        if event is None:
            raise ValueError(f"Outbox event {event_id} was not found")
        if event.status != "FAILED":
            raise ValueError(f"Outbox event has status {event.status}; only FAILED events may be replayed")
        event.status = "PENDING"
        event.retry_count = 0
        event.next_attempt_at = None
        await session.commit()
        print(f"Queued event {event_id} for republishing")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Requeue one permanently failed outbox event")
    parser.add_argument("event_id", type=UUID)
    asyncio.run(replay(parser.parse_args().event_id))
