"""Unit tests for Pydantic recipe schema validation rules."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from meal_planner.api.schemas.recipe import (
    RecipeCreateSchema,
    RecipeIngredientCreateSchema,
    RecipeScaleRequestSchema,
    RecipeUpdateSchema,
)


def test_create_defaults():
    """RecipeCreateSchema with only title applies correct defaults."""
    schema = RecipeCreateSchema(title="Simple")

    assert schema.state == "draft"
    assert schema.base_servings == 1
    assert schema.ingredients == []
    assert schema.instructions == []
    assert schema.tags == []


def test_create_requires_title():
    """RecipeCreateSchema without title raises ValidationError."""
    with pytest.raises(ValidationError):
        RecipeCreateSchema()


def test_scale_rejects_zero():
    """RecipeScaleRequestSchema rejects new_servings=0 (gt=0 constraint)."""
    with pytest.raises(ValidationError):
        RecipeScaleRequestSchema(new_servings=0)


def test_scale_rejects_negative():
    """RecipeScaleRequestSchema rejects negative new_servings."""
    with pytest.raises(ValidationError):
        RecipeScaleRequestSchema(new_servings=-1)


def test_update_all_optional():
    """RecipeUpdateSchema succeeds with no fields (all optional for partial update)."""
    schema = RecipeUpdateSchema()

    assert schema.title is None
    assert schema.description is None
    assert schema.state is None
    assert schema.base_servings is None


def test_ingredient_create_defaults():
    """RecipeIngredientCreateSchema with only name applies boolean defaults."""
    schema = RecipeIngredientCreateSchema(name="Salt")

    assert schema.to_taste is False
    assert schema.optional is False
    assert schema.amount is None
    assert schema.unit is None
