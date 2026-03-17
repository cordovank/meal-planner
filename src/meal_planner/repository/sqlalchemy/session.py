# ./src/meal_planner/repository/sqlalchemy/session.py

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from meal_planner.config import settings


_engine: AsyncEngine | None = None
_sessionmaker: sessionmaker | None = None


def get_engine() -> AsyncEngine:
    """Lazily create and return the async SQLAlchemy engine."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(settings.database_url, future=True, echo=settings.debug)
    return _engine


def get_sessionmaker() -> sessionmaker:
    """Lazily create and return the async sessionmaker."""
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            future=True,
        )
    return _sessionmaker


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a new async session.

    Use as a dependency in FastAPI endpoints:

        async def endpoint(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with get_sessionmaker()() as session:
        yield session
