from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()

# Sync engine for migrations / init_db
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# Async engine for application
async_engine = create_async_engine(
    settings.async_database_url,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# Session factories
SessionLocal = async_sessionmaker  # re-exported name kept for backwards compat checks
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions.

    Commits are owned by the service layer — this dependency only
    guarantees rollback on error and cleanup afterwards.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
