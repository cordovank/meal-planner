"""Shared fixtures for integration tests."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Import all models so Base.metadata knows about all tables
from meal_planner.repository.sqlalchemy.models.base import Base
from meal_planner.repository.sqlalchemy.models.food import FoodEntry, NutritionRecord  # noqa: F401
from meal_planner.repository.sqlalchemy.models.profile import Profile, ProfileTarget  # noqa: F401
from meal_planner.repository.sqlalchemy.models.recipe import Recipe, RecipeIngredient, RecipeNote  # noqa: F401


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def engine():
    """Create an in-memory SQLite engine for integration tests."""
    engine = create_async_engine("sqlite+aiosqlite://", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(engine):
    """Provide an isolated database session per test."""
    async with engine.connect() as conn:
        trans = await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()
