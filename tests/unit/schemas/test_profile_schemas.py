"""Unit tests for Profile Pydantic schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from meal_planner.api.schemas.profile import (
    ProfileCreateSchema,
    ProfileTargetValueSchema,
    ProfileUpdateSchema,
)


def test_create_schema_valid_minimal():
    schema = ProfileCreateSchema(name="Me")
    assert schema.name == "Me"
    assert schema.calorie_target is None
    assert schema.targets is None


def test_create_schema_valid_full():
    schema = ProfileCreateSchema(
        name="Partner",
        calorie_target=1800,
        calorie_tolerance=80,
        is_default=True,
        targets={
            "protein_g": ProfileTargetValueSchema(target=120, tolerance=12),
            "fat_g": ProfileTargetValueSchema(target=60, tolerance=6),
        },
    )
    assert schema.calorie_target == 1800
    assert len(schema.targets) == 2


def test_create_schema_name_too_long():
    with pytest.raises(ValidationError):
        ProfileCreateSchema(name="x" * 51)


def test_create_schema_name_empty():
    with pytest.raises(ValidationError):
        ProfileCreateSchema(name="")


def test_create_schema_negative_calorie_target():
    with pytest.raises(ValidationError):
        ProfileCreateSchema(name="Me", calorie_target=-100)


def test_create_schema_zero_calorie_target():
    with pytest.raises(ValidationError):
        ProfileCreateSchema(name="Me", calorie_target=0)


def test_create_schema_invalid_nutrient_key():
    with pytest.raises(ValidationError, match="Invalid nutrient key"):
        ProfileCreateSchema(
            name="Me",
            targets={"invalid_key": ProfileTargetValueSchema(target=50)},
        )


def test_target_value_must_be_positive():
    with pytest.raises(ValidationError):
        ProfileTargetValueSchema(target=0)


def test_target_tolerance_must_be_non_negative():
    with pytest.raises(ValidationError):
        ProfileTargetValueSchema(target=50, tolerance=-1)


def test_update_schema_all_optional():
    schema = ProfileUpdateSchema()
    assert schema.name is None
    assert schema.calorie_target is None
    assert schema.targets is None


def test_update_schema_partial():
    schema = ProfileUpdateSchema(name="Updated", calorie_target=2200)
    assert schema.name == "Updated"
    assert schema.calorie_target == 2200
