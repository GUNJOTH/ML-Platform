from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

doris_engine = create_async_engine(
    settings.doris_url,
    pool_size=5,
    echo=settings.app_env == "development",
)

doris_session_factory = async_sessionmaker(doris_engine, expire_on_commit=False)


async def get_doris_session() -> AsyncGenerator[AsyncSession, None]:
    async with doris_session_factory() as session:
        yield session
