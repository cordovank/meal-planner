"""Pydantic schemas for Food Entry and Nutrition Record API."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import Field

from .common import BaseSchema, TimestampedSchema, UUIDSchema


# --- NutritionRecord schemas ---


class NutritionRecordSchema(TimestampedSchema, UUIDSchema):
    """Schema for nutrition record in responses."""

    food_entry_id: uuid.UUID
    serving_size: Decimal
    serving_unit: str
    calories: Decimal
    protein_g: Decimal
    carbohydrates_g: Decimal
    fat_g: Decimal
    added_sugar_g: Decimal
    fiber_g: Optional[Decimal] = None
    total_sugar_g: Optional[Decimal] = None
    sodium_mg: Optional[Decimal] = None
    saturated_fat_g: Optional[Decimal] = None
    source_type: str


class NutritionRecordCreateSchema(BaseSchema):
    """Schema for creating a nutrition record."""

    serving_size: Decimal = Field(..., gt=0)
    serving_unit: str
    calories: Decimal = Field(..., ge=0)
    protein_g: Decimal = Field(..., ge=0)
    carbohydrates_g: Decimal = Field(..., ge=0)
    fat_g: Decimal = Field(..., ge=0)
    added_sugar_g: Decimal = Field(..., ge=0)
    source_type: str
    fiber_g: Optional[Decimal] = Field(None, ge=0)
    total_sugar_g: Optional[Decimal] = Field(None, ge=0)
    sodium_mg: Optional[Decimal] = Field(None, ge=0)
    saturated_fat_g: Optional[Decimal] = Field(None, ge=0)


class NutritionRecordUpdateSchema(BaseSchema):
    """Schema for updating a nutrition record (all fields optional)."""

    serving_size: Optional[Decimal] = Field(None, gt=0)
    serving_unit: Optional[str] = None
    calories: Optional[Decimal] = Field(None, ge=0)
    protein_g: Optional[Decimal] = Field(None, ge=0)
    carbohydrates_g: Optional[Decimal] = Field(None, ge=0)
    fat_g: Optional[Decimal] = Field(None, ge=0)
    added_sugar_g: Optional[Decimal] = Field(None, ge=0)
    source_type: Optional[str] = None
    fiber_g: Optional[Decimal] = Field(None, ge=0)
    total_sugar_g: Optional[Decimal] = Field(None, ge=0)
    sodium_mg: Optional[Decimal] = Field(None, ge=0)
    saturated_fat_g: Optional[Decimal] = Field(None, ge=0)


# --- FoodEntry schemas ---


class FoodEntrySchema(TimestampedSchema, UUIDSchema):
    """Schema for food entry in responses."""

    name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    source_type: str
    source_id: Optional[str] = None
    is_custom: bool = False
    nutrition_records: list[NutritionRecordSchema] = Field(default_factory=list)


class FoodEntryListItemSchema(TimestampedSchema, UUIDSchema):
    """Schema for food entry in list view (without nutrition records)."""

    name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    source_type: str
    is_custom: bool = False


class FoodEntryCreateSchema(BaseSchema):
    """Schema for creating a food entry."""

    name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    source_type: str = "user_created"
    source_id: Optional[str] = None
    is_custom: bool = True


class FoodEntryUpdateSchema(BaseSchema):
    """Schema for updating a food entry (all fields optional)."""

    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None


class FoodEntryListResponseSchema(BaseSchema):
    """Schema for food entry list response."""

    items: list[FoodEntryListItemSchema] = Field(default_factory=list)
    total: int = 0
    has_more: bool = False
