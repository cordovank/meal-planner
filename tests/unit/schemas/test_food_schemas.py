"""Unit tests for food/nutrition Pydantic schema validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from meal_planner.api.schemas.food import (
    FoodEntryCreateSchema,
    FoodEntryUpdateSchema,
    NutritionRecordCreateSchema,
)


def test_food_entry_create_defaults():
    """FoodEntryCreateSchema applies correct defaults."""
    schema = FoodEntryCreateSchema(name="Apple")
    assert schema.source_type == "user_created"
    assert schema.is_custom is True
    assert schema.brand is None


def test_food_entry_create_requires_name():
    """FoodEntryCreateSchema requires name."""
    with pytest.raises(ValidationError):
        FoodEntryCreateSchema()


def test_food_entry_update_all_optional():
    """FoodEntryUpdateSchema allows partial updates."""
    schema = FoodEntryUpdateSchema()
    assert schema.name is None
    assert schema.brand is None


def test_nutrition_record_create_requires_fields():
    """NutritionRecordCreateSchema requires core nutrition fields."""
    with pytest.raises(ValidationError):
        NutritionRecordCreateSchema(serving_size=100, serving_unit="g")


def test_nutrition_record_create_valid():
    """NutritionRecordCreateSchema with all required fields succeeds."""
    schema = NutritionRecordCreateSchema(
        serving_size=100,
        serving_unit="g",
        calories=165,
        protein_g=31,
        carbohydrates_g=0,
        fat_g=3.6,
        added_sugar_g=0,
        source_type="label",
    )
    assert float(schema.calories) == 165
    assert schema.fiber_g is None


def test_nutrition_record_rejects_negative_calories():
    """NutritionRecordCreateSchema rejects negative calorie values."""
    with pytest.raises(ValidationError):
        NutritionRecordCreateSchema(
            serving_size=100,
            serving_unit="g",
            calories=-10,
            protein_g=10,
            carbohydrates_g=10,
            fat_g=5,
            added_sugar_g=0,
            source_type="label",
        )


def test_nutrition_record_rejects_zero_serving_size():
    """NutritionRecordCreateSchema rejects serving_size=0 (gt=0)."""
    with pytest.raises(ValidationError):
        NutritionRecordCreateSchema(
            serving_size=0,
            serving_unit="g",
            calories=100,
            protein_g=10,
            carbohydrates_g=10,
            fat_g=5,
            added_sugar_g=0,
            source_type="label",
        )
