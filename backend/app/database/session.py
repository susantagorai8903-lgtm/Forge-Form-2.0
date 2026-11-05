from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

connect_args = {"ssl": "require"} if settings.app_env == "production" and "asyncpg" in settings.database_url else {}
engine_options = {"pool_pre_ping": True, "connect_args": connect_args}
if "sqlite" not in settings.database_url:
    engine_options.update(pool_size=5, max_overflow=2, pool_recycle=300)
engine = create_async_engine(settings.database_url, **engine_options)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with SessionLocal() as session:
        yield session
