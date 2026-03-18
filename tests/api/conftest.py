"""Shared fixtures for API-level tests."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Import models so Base.metadata knows about all tables
from meal_planner.repository.sqlalchemy.models.base import Base
from meal_planner.repository.sqlalchemy.models.recipe import Recipe, RecipeIngredient, RecipeNote  # noqa: F401
from meal_planner.repository.sqlalchemy.session import get_session
from meal_planner.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def engine():
    """Create an in-memory SQLite engine for all API tests."""
    engine = create_async_engine("sqlite+aiosqlite://", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(engine):
    """Provide an isolated database session per test.

    Each test gets a nested transaction that is rolled back after the test,
    so tests never pollute each other.
    """
    async with engine.connect() as conn:
        trans = await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()


@pytest.fixture
async def client(db_session):
    """Provide an httpx AsyncClient wired to the FastAPI app.

    Overrides the get_session dependency so the app uses the test
    session (in-memory SQLite) instead of the production database.
    """
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
async def sample_recipe(client):
    """Create a sample recipe via the API and return the response JSON."""
    payload = {
        "title": "Test Pancakes",
        "base_servings": 4,
        "ingredients": [
            {"name": "Flour", "amount": 2.0, "unit": "cups"},
            {"name": "Eggs", "amount": 3, "unit": "pieces"},
        ],
    }
    resp = await client.post("/api/v1/recipes", json=payload)
    assert resp.status_code == 201
    return resp.json()
