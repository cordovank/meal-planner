# ./src/meal_planner/repository/sqlalchemy/models/base.py

from __future__ import annotations

import uuid
from datetime import datetime
from typing import ClassVar

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import DeclarativeBase, declared_attr


def _now() -> datetime:
    return datetime.utcnow()


class Base(DeclarativeBase):
    """Base declarative class with UUID primary key and audit timestamps."""

    __abstract__ = True
    __allow_unmapped__ = True

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
        index=True,
    )

    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    @declared_attr
    def __tablename__(cls) -> str:  # pragma: no cover
        return cls.__name__.lower()

    def soft_delete(self) -> None:
        """Soft delete the record by setting deleted_at timestamp."""
        self.deleted_at = _now()
