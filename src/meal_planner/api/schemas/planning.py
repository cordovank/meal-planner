"""Pydantic schemas for Planning and LeftoverBatch API."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import Field, field_validator

from .common import BaseSchema, TimestampedSchema, UUIDSchema


# --- MealPlanEntry schemas ---


VALID_MEAL_SLOTS = {"breakfast", "lunch", "dinner", "snack"}


class MealPlanEntryCreateSchema(BaseSchema):
    """Schema for adding a meal to the plan."""

    meal_slot: str
    recipe_id: str
    servings: float = Field(1.0, gt=0)
    profile_id: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("meal_slot")
    @classmethod
    def validate_meal_slot(cls, v: str) -> str:
        if v not in VALID_MEAL_SLOTS:
            raise ValueError(f"Invalid meal slot: {v}. Must be one of {VALID_MEAL_SLOTS}")
        return v


class MealPlanEntrySchema(TimestampedSchema, UUIDSchema):
    """Schema for a meal plan entry in responses."""

    date: date
    meal_slot: str
    recipe_id: str
    servings: float
    batch_id: Optional[str] = None
    profile_id: Optional[str] = None
    notes: Optional[str] = None


class MealPlanEntryDetailSchema(BaseSchema):
    """Enriched meal entry with recipe title and nutrition."""

    id: str
    meal_slot: str
    recipe_id: str
    title: str
    servings: float
    nutrition: Optional[dict] = None
    batch: Optional[dict] = None
    profile_id: Optional[str] = None
    notes: Optional[str] = None


class RescheduleSchema(BaseSchema):
    """Schema for rescheduling a meal."""

    meal_id: str
    new_date: date
    new_slot: Optional[str] = None

    @field_validator("new_slot")
    @classmethod
    def validate_new_slot(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_MEAL_SLOTS:
            raise ValueError(f"Invalid meal slot: {v}. Must be one of {VALID_MEAL_SLOTS}")
        return v


# --- Day / Week plan schemas ---


class DayPlanSchema(BaseSchema):
    """Schema for a single day in the weekly plan."""

    date: str
    meals: list[MealPlanEntryDetailSchema] = Field(default_factory=list)
    totals: dict = Field(default_factory=dict)


class WeekPlanSchema(BaseSchema):
    """Schema for the weekly plan response."""

    week_start: str
    days: list[DayPlanSchema] = Field(default_factory=list)
    weekly_totals: dict = Field(default_factory=dict)


# --- LeftoverBatch schemas ---


class BatchCreateSchema(BaseSchema):
    """Schema for creating a leftover batch."""

    recipe_id: str
    prepared_servings: int = Field(..., ge=1)
    prepared_date: Optional[date] = None


class BatchConsumeSchema(BaseSchema):
    """Schema for consuming servings from a batch."""

    servings_consumed: int = Field(1, ge=1)


class BatchFromMealSchema(BaseSchema):
    """Schema for marking a planned meal as batch-prepared."""

    prepared_servings: int = Field(..., ge=1)


class BatchSchema(TimestampedSchema, UUIDSchema):
    """Schema for batch in responses."""

    recipe_id: str
    initial_servings: int
    servings_remaining: int
    prepared_date: date


class BatchDetailSchema(BaseSchema):
    """Schema for batch with recipe title."""

    batch_id: str
    recipe_id: str
    title: str
    initial_servings: int
    servings_remaining: int
    prepared_date: str


# --- Batch-linked meal entry ---


class MealFromBatchSchema(BaseSchema):
    """Schema for adding a meal from a leftover batch."""

    batch_id: str
    meal_slot: str
    servings_consumed: int = Field(1, ge=1)
    profile_id: Optional[str] = None

    @field_validator("meal_slot")
    @classmethod
    def validate_meal_slot(cls, v: str) -> str:
        if v not in VALID_MEAL_SLOTS:
            raise ValueError(f"Invalid meal slot: {v}. Must be one of {VALID_MEAL_SLOTS}")
        return v


# --- Suggestions ---


class SuggestionResponseSchema(BaseSchema):
    """Schema for planning suggestions."""

    recent: list[dict] = Field(default_factory=list)
    leftovers: list[dict] = Field(default_factory=list)
