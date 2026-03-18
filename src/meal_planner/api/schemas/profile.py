"""Pydantic schemas for Profile and ProfileTarget API."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import Field, field_validator

from .common import BaseSchema, TimestampedSchema, UUIDSchema


# --- ProfileTarget schemas ---


class ProfileTargetValueSchema(BaseSchema):
    """Schema for a single nutrient target (used in create/update)."""

    target: Decimal = Field(..., gt=0)
    tolerance: Optional[Decimal] = Field(None, ge=0)


class ProfileTargetSchema(TimestampedSchema, UUIDSchema):
    """Schema for profile target in responses."""

    profile_id: uuid.UUID
    nutrient_key: str
    target_value: Decimal
    tolerance_value: Decimal
    unit: str


# --- Profile schemas ---


class ProfileSchema(TimestampedSchema, UUIDSchema):
    """Schema for profile in responses (detail view)."""

    name: str
    calorie_target: Optional[int] = None
    calorie_tolerance: int = 100
    is_default: bool = False
    targets: dict[str, dict] = Field(default_factory=dict)


class ProfileListItemSchema(TimestampedSchema, UUIDSchema):
    """Schema for profile in list view."""

    name: str
    calorie_target: Optional[int] = None
    is_default: bool = False
    targets: dict[str, dict] = Field(default_factory=dict)


class ProfileCreateSchema(BaseSchema):
    """Schema for creating a profile."""

    name: str = Field(..., min_length=1, max_length=50)
    calorie_target: Optional[int] = Field(None, gt=0)
    calorie_tolerance: Optional[int] = Field(None, ge=0)
    is_default: bool = False
    targets: Optional[dict[str, ProfileTargetValueSchema]] = None

    @field_validator("targets")
    @classmethod
    def validate_targets(cls, v):
        if v is None:
            return v
        valid_keys = {
            "protein_g", "carbohydrates_g", "fat_g", "added_sugar_g",
            "fiber_g", "sodium_mg", "saturated_fat_g",
        }
        for key in v:
            if key not in valid_keys:
                raise ValueError(f"Invalid nutrient key: {key}")
        return v


class ProfileUpdateSchema(BaseSchema):
    """Schema for updating a profile (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=50)
    calorie_target: Optional[int] = Field(None, gt=0)
    calorie_tolerance: Optional[int] = Field(None, ge=0)
    is_default: Optional[bool] = None
    targets: Optional[dict[str, ProfileTargetValueSchema]] = None

    @field_validator("targets")
    @classmethod
    def validate_targets(cls, v):
        if v is None:
            return v
        valid_keys = {
            "protein_g", "carbohydrates_g", "fat_g", "added_sugar_g",
            "fiber_g", "sodium_mg", "saturated_fat_g",
        }
        for key in v:
            if key not in valid_keys:
                raise ValueError(f"Invalid nutrient key: {key}")
        return v


class ProfileListResponseSchema(BaseSchema):
    """Schema for profile list response."""

    items: list[ProfileListItemSchema] = Field(default_factory=list)
    total: int = 0
    has_more: bool = False


class ProfileCompareRequestSchema(BaseSchema):
    """Schema for comparing a recipe against a profile."""

    recipe_id: str
    portion_size: float = Field(1.0, gt=0)


class ProfileCompareResponseSchema(BaseSchema):
    """Schema for profile comparison result."""

    profile_name: str
    fit: str
    details: dict = Field(default_factory=dict)
    gaps: list[dict] = Field(default_factory=list)
