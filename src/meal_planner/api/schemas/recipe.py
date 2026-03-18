"""Pydantic schemas for Recipe API."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from .common import BaseSchema, TimestampedSchema, UUIDSchema


class RecipeIngredientSchema(BaseSchema):
    """Schema for recipe ingredient."""

    id: uuid.UUID
    name: str
    amount: Optional[Decimal] = None
    unit: Optional[str] = None
    food_entry_id: Optional[uuid.UUID] = None
    to_taste: bool = False
    optional: bool = False
    notes: Optional[str] = None
    sort_order: int = 0


class RecipeIngredientCreateSchema(BaseSchema):
    """Schema for creating/updating a recipe ingredient."""

    name: str
    amount: Optional[Decimal] = None
    unit: Optional[str] = None
    food_entry_id: Optional[uuid.UUID] = None
    to_taste: bool = False
    optional: bool = False
    notes: Optional[str] = None


class RecipeNoteSchema(BaseSchema):
    """Schema for recipe note."""

    id: uuid.UUID
    text: str
    created_at: datetime


class RecipeNoteCreateSchema(BaseSchema):
    """Schema for creating a recipe note."""

    text: str


class NutritionSchema(BaseSchema):
    """Schema for nutrition data."""

    calories: Decimal = 0.0
    protein_g: Decimal = 0.0
    carbohydrates_g: Decimal = 0.0
    fat_g: Decimal = 0.0
    fiber_g: Optional[Decimal] = None
    total_sugar_g: Optional[Decimal] = None
    added_sugar_g: Decimal = 0.0
    sodium_mg: Optional[Decimal] = None
    saturated_fat_g: Optional[Decimal] = None


class RecipeListItemSchema(TimestampedSchema, UUIDSchema):
    """Schema for recipe in list view."""

    title: str
    state: str
    base_servings: int
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    nutrition_per_serving: Optional[NutritionSchema] = None
    confidence: Optional[str] = None
    tags: list[str] = Field(default_factory=list)


class RecipeDetailSchema(TimestampedSchema, UUIDSchema):
    """Schema for recipe detail view."""

    title: str
    description: Optional[str] = None
    state: str
    base_servings: int
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    ingredients: list[RecipeIngredientSchema] = Field(default_factory=list)
    instructions: list[dict[str, Any]] = Field(default_factory=list)
    nutrition_total: Optional[NutritionSchema] = None
    nutrition_per_serving: Optional[NutritionSchema] = None
    characterization: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    notes: list[RecipeNoteSchema] = Field(default_factory=list)
    parent_recipe_id: Optional[uuid.UUID] = None
    version_label: Optional[str] = None


class RecipeCreateSchema(BaseSchema):
    """Schema for creating a recipe."""

    title: str
    description: Optional[str] = None
    state: str = "draft"
    base_servings: int = 1
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    ingredients: list[RecipeIngredientCreateSchema] = Field(default_factory=list)
    instructions: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class RecipeUpdateSchema(BaseSchema):
    """Schema for updating a recipe."""

    title: Optional[str] = None
    description: Optional[str] = None
    state: Optional[str] = None
    base_servings: Optional[int] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None


class RecipeScaleRequestSchema(BaseSchema):
    """Schema for scaling a recipe."""

    new_servings: int = Field(..., gt=0)


class RecipeScaleResponseSchema(BaseSchema):
    """Schema for scaled recipe response."""

    factor: float
    servings: int
    ingredients: list[RecipeIngredientSchema]


class RecipeDuplicateRequestSchema(BaseSchema):
    """Schema for duplicating a recipe."""

    title: str
    version_label: Optional[str] = None


class RecipeNutritionBreakdownSchema(BaseSchema):
    """Schema for detailed nutrition breakdown."""

    total: Optional[NutritionSchema] = None
    per_serving: Optional[NutritionSchema] = None
    by_ingredient: list[dict[str, Any]] = Field(default_factory=list)
    confidence_overall: Optional[str] = None
    characterization: list[str] = Field(default_factory=list)
    missing_data: list[str] = Field(default_factory=list)


class RecipeListResponseSchema(BaseSchema):
    """Schema for recipe list response."""

    items: list[RecipeListItemSchema] = Field(default_factory=list)
    total: int = 0
    has_more: bool = False
