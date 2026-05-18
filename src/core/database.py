"""Database configuration"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from core.config import AppConfig

config = AppConfig()

engine = create_async_engine(
    config.DATABASE_URL,
    echo=config.DEBUG,
    future=True,
    pool_pre_ping=True,
)

# pyrefly: ignore [no-matching-overload]
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async generator for database sessions.

    Yields:
        AsyncSession: Async database session.
    """
    async with async_session_maker() as session:
        yield session
