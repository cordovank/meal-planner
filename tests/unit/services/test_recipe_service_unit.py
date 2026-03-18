"""Unit tests for RecipeService methods not covered by integration tests.

Uses AsyncMock for the repository to isolate service-layer logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional
from unittest.mock import AsyncMock

import pytest

from meal_planner.services.recipe_service import RecipeService


# ---------------------------------------------------------------------------
# Lightweight mocks (match ORM model interfaces)
# ---------------------------------------------------------------------------


@dataclass
class MockRecipe:
    id: str = "recipe-1"
    title: str = "Test"
    base_servings: int = 4
    state: str = "draft"
    description: Optional[str] = None
    user_id: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    parent_recipe_id: Optional[str] = None
    version_label: Optional[str] = None
    ingredients: list = field(default_factory=list)


@dataclass
class MockIngredient:
    id: str = "ing-1"
    recipe_id: str = "recipe-1"
    name: str = "Flour"
    amount: Optional[Decimal] = Decimal("2.0")
    unit: Optional[str] = "cups"
    food_entry_id: Optional[str] = None
    to_taste: bool = False
    optional: bool = False
    notes: Optional[str] = None
    sort_order: int = 0


@dataclass
class MockNote:
    id: str = "note-1"
    recipe_id: str = "recipe-1"
    text: str = "A note"


def _make_service(repo_mock: AsyncMock) -> RecipeService:
    return RecipeService(repo_mock)


# ---------------------------------------------------------------------------
# update_ingredient
# ---------------------------------------------------------------------------


async def test_update_ingredient_applies_fields():
    """All provided fields are applied to the ingredient."""
    repo = AsyncMock()
    ingredient = MockIngredient()
    repo.get_ingredient.return_value = ingredient
    repo.update_ingredient.return_value = ingredient
    service = _make_service(repo)

    result = await service.update_ingredient(
        ingredient_id="ing-1",
        name="Whole Wheat Flour",
        amount=Decimal("3.0"),
        unit="cups",
        to_taste=True,
        optional=True,
        notes="Sifted",
    )

    assert result is not None
    assert ingredient.name == "Whole Wheat Flour"
    assert ingredient.amount == Decimal("3.0")
    assert ingredient.to_taste is True
    assert ingredient.optional is True
    assert ingredient.notes == "Sifted"
    repo.update_ingredient.assert_awaited_once()


async def test_update_ingredient_not_found():
    """Returns None when the ingredient does not exist."""
    repo = AsyncMock()
    repo.get_ingredient.return_value = None
    service = _make_service(repo)

    result = await service.update_ingredient(ingredient_id="missing")
    assert result is None


# ---------------------------------------------------------------------------
# remove_ingredient
# ---------------------------------------------------------------------------


async def test_remove_ingredient_not_found():
    """Returns False when ingredient does not exist."""
    repo = AsyncMock()
    repo.get_ingredient.return_value = None
    service = _make_service(repo)

    result = await service.remove_ingredient("missing")
    assert result is False


async def test_remove_ingredient_success():
    """Returns True and calls repo.remove_ingredient."""
    repo = AsyncMock()
    repo.get_ingredient.return_value = MockIngredient()
    service = _make_service(repo)

    result = await service.remove_ingredient("ing-1")
    assert result is True
    repo.remove_ingredient.assert_awaited_once_with("ing-1")


# ---------------------------------------------------------------------------
# add_note / remove_note
# ---------------------------------------------------------------------------


async def test_add_note_recipe_not_found():
    """Returns None when the recipe does not exist."""
    repo = AsyncMock()
    repo.get_by_id.return_value = None
    service = _make_service(repo)

    result = await service.add_note(recipe_id="missing", text="hello")
    assert result is None


async def test_add_note_success():
    """Creates a note with correct text and calls repo."""
    repo = AsyncMock()
    repo.get_by_id.return_value = MockRecipe()
    repo.add_note.side_effect = lambda note: note
    service = _make_service(repo)

    result = await service.add_note(recipe_id="recipe-1", text="Great recipe")
    assert result is not None
    assert result.text == "Great recipe"
    assert result.recipe_id == "recipe-1"
    # UUID id should be set
    assert result.id is not None and len(result.id) == 36


async def test_remove_note_not_found():
    """Returns False when the note does not exist."""
    repo = AsyncMock()
    repo.get_note.return_value = None
    service = _make_service(repo)

    result = await service.remove_note("missing")
    assert result is False


async def test_remove_note_success():
    """Returns True and calls repo.remove_note."""
    repo = AsyncMock()
    repo.get_note.return_value = MockNote()
    service = _make_service(repo)

    result = await service.remove_note("note-1")
    assert result is True
    repo.remove_note.assert_awaited_once_with("note-1")


# ---------------------------------------------------------------------------
# get_recipe_with_relations
# ---------------------------------------------------------------------------


async def test_get_recipe_with_relations_not_found():
    """Returns None when the recipe does not exist."""
    repo = AsyncMock()
    repo.get_by_id.return_value = None
    service = _make_service(repo)

    result = await service.get_recipe_with_relations("missing")
    assert result is None


# ---------------------------------------------------------------------------
# scale_recipe edge cases
# ---------------------------------------------------------------------------


def test_scale_base_servings_zero():
    """When base_servings is 0, returns factor 1.0 and empty ingredients."""
    repo = AsyncMock()
    service = _make_service(repo)

    recipe = MockRecipe(base_servings=0)
    result = service.scale_recipe(recipe, 4)

    assert result["factor"] == 1.0
    assert result["ingredients"] == []


def test_scale_ingredient_amount_none():
    """Ingredients with amount=None (to_taste) stay None after scaling."""
    repo = AsyncMock()
    service = _make_service(repo)

    recipe = MockRecipe(
        base_servings=2,
        ingredients=[MockIngredient(name="Salt", amount=None, to_taste=True)],
    )
    result = service.scale_recipe(recipe, 4)

    assert result["ingredients"][0]["amount"] is None
    assert result["ingredients"][0]["to_taste"] is True


# ---------------------------------------------------------------------------
# duplicate_recipe
# ---------------------------------------------------------------------------


async def test_duplicate_not_found():
    """Returns None when the original recipe does not exist."""
    repo = AsyncMock()
    repo.get_by_id.return_value = None
    service = _make_service(repo)

    result = await service.duplicate_recipe("missing", "Copy")
    assert result is None
