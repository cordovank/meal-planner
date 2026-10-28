"""Unit tests for planning Pydantic schemas."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from meal_planner.api.schemas.planning import (
    BatchConsumeSchema,
    BatchCreateSchema,
    BatchFromMealSchema,
    MealFromBatchSchema,
    MealPlanEntryCreateSchema,
    RescheduleSchema,
)


# --- MealPlanEntryCreateSchema ---


def test_valid_meal_plan_entry():
    schema = MealPlanEntryCreateSchema(
        meal_slot="breakfast",
        recipe_id="abc-123",
        servings=2.0,
    )
    assert schema.meal_slot == "breakfast"
    assert schema.servings == 2.0


def test_meal_plan_entry_default_servings():
    schema = MealPlanEntryCreateSchema(meal_slot="lunch", recipe_id="abc")
    assert schema.servings == 1.0


def test_meal_plan_entry_invalid_slot():
    with pytest.raises(ValidationError):
        MealPlanEntryCreateSchema(meal_slot="brunch", recipe_id="abc")


def test_meal_plan_entry_zero_servings():
    with pytest.raises(ValidationError):
        MealPlanEntryCreateSchema(meal_slot="dinner", recipe_id="abc", servings=0)


def test_meal_plan_entry_negative_servings():
    with pytest.raises(ValidationError):
        MealPlanEntryCreateSchema(meal_slot="dinner", recipe_id="abc", servings=-1)


# --- RescheduleSchema ---


def test_valid_reschedule():
    schema = RescheduleSchema(meal_id="entry-1", new_date=date(2026, 3, 20))
    assert schema.new_slot is None


def test_reschedule_with_new_slot():
    schema = RescheduleSchema(
        meal_id="entry-1", new_date=date(2026, 3, 20), new_slot="dinner"
    )
    assert schema.new_slot == "dinner"


def test_reschedule_invalid_slot():
    with pytest.raises(ValidationError):
        RescheduleSchema(meal_id="entry-1", new_date=date(2026, 3, 20), new_slot="brunch")


# --- BatchCreateSchema ---


def test_valid_batch_create():
    schema = BatchCreateSchema(recipe_id="recipe-1", prepared_servings=6)
    assert schema.prepared_servings == 6
    assert schema.prepared_date is None


def test_batch_create_with_date():
    schema = BatchCreateSchema(
        recipe_id="recipe-1",
        prepared_servings=4,
        prepared_date=date(2026, 3, 16),
    )
    assert schema.prepared_date == date(2026, 3, 16)


def test_batch_create_zero_servings():
    with pytest.raises(ValidationError):
        BatchCreateSchema(recipe_id="recipe-1", prepared_servings=0)


def test_batch_create_negative_servings():
    with pytest.raises(ValidationError):
        BatchCreateSchema(recipe_id="recipe-1", prepared_servings=-1)


# --- BatchConsumeSchema ---


def test_valid_batch_consume():
    schema = BatchConsumeSchema(servings_consumed=2)
    assert schema.servings_consumed == 2


def test_batch_consume_default():
    schema = BatchConsumeSchema()
    assert schema.servings_consumed == 1


def test_batch_consume_zero():
    with pytest.raises(ValidationError):
        BatchConsumeSchema(servings_consumed=0)


# --- BatchFromMealSchema ---


def test_valid_batch_from_meal():
    schema = BatchFromMealSchema(prepared_servings=8)
    assert schema.prepared_servings == 8


def test_batch_from_meal_zero():
    with pytest.raises(ValidationError):
        BatchFromMealSchema(prepared_servings=0)


# --- MealFromBatchSchema ---


def test_valid_meal_from_batch():
    schema = MealFromBatchSchema(batch_id="batch-1", meal_slot="lunch")
    assert schema.servings_consumed == 1


def test_meal_from_batch_invalid_slot():
    with pytest.raises(ValidationError):
        MealFromBatchSchema(batch_id="batch-1", meal_slot="brunch")
