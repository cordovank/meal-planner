# ./src/meal_planner/api/schemas/common.py

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema shared across API models."""

    model_config = ConfigDict(extra="ignore")


class UUIDSchema(BaseSchema):
    id: uuid.UUID


class TimestampedSchema(BaseSchema):
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
