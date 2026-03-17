# tests/unit/repository/test_session.py

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from meal_planner.repository.sqlalchemy.session import get_engine, get_sessionmaker


def test_get_engine_singleton() -> None:
    """Test that get_engine returns the same engine instance."""
    engine1 = get_engine()
    engine2 = get_engine()

    assert engine1 is engine2


def test_get_engine_creates_async_engine() -> None:
    """Test that get_engine creates an async engine."""
    engine = get_engine()

    # Should have url attribute (all SQLAlchemy engines have this)
    assert hasattr(engine, "url")
    assert "sqlite" in str(engine.url)


def test_get_sessionmaker_singleton() -> None:
    """Test that get_sessionmaker returns the same sessionmaker instance."""
    sm1 = get_sessionmaker()
    sm2 = get_sessionmaker()

    assert sm1 is sm2


def test_get_sessionmaker_configuration() -> None:
    """Test that sessionmaker is configured with correct settings."""
    sm = get_sessionmaker()

    # Check async settings in kw dict
    assert sm.kw.get("expire_on_commit") is False
    assert sm.kw.get("autoflush") is False
    assert sm.kw.get("future") is True

    # Check the sessionmaker repr includes AsyncSession
    assert "AsyncSession" in repr(sm)


def test_engine_url_configuration() -> None:
    """Test that engine is configured with correct database URL."""
    engine = get_engine()

    # Should be SQLite async
    url_str = str(engine.url)
    assert "sqlite" in url_str.lower()
    assert "aiosqlite" in url_str.lower()


def test_sessionmaker_bound_to_engine() -> None:
    """Test that sessionmaker is bound to the engine."""
    sm = get_sessionmaker()
    engine = get_engine()

    # Sessionmaker should have bind set
    assert sm.kw.get("bind") is engine
