import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database.base import Base
from app.database.session import get_db
from app.main import app, request_counts
from app.models import Program, ProgramCategory


@pytest_asyncio.fixture
async def client():
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    test_sessions = async_sessionmaker(test_engine, expire_on_commit=False)

    async def override_db():
        async with test_sessions() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    app.state.test_sessions = test_sessions
    request_counts.clear()
    async with test_sessions() as session:
        category = ProgramCategory(name="Personal Training", slug="personal-training")
        session.add(category)
        await session.flush()
        session.add(Program(
            name="Personal Training", slug="personal-training", category_id=category.id,
            short_description="Individual coaching", description="Coaching", benefits=[], target_audience="",
            image_url="", is_active=True,
        ))
        await session.commit()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()
    await test_engine.dispose()
