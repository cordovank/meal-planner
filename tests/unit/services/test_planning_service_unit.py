"""Unit tests for PlanningService methods using AsyncMock."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

from meal_planner.services.planning_service import PlanningService


@dataclass
class MockRecipe:
    id: str = "recipe-1"
    title: str = "Test Recipe"
    base_servings: int = 4
    state: str = "finalized"
    description: Optional[str] = None
    user_id: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    parent_recipe_id: Optional[str] = None
    version_label: Optional[str] = None
    ingredients: list = field(default_factory=list)


@dataclass
class MockMealPlanEntry:
    id: str = "entry-1"
    date: date = date(2026, 3, 16)
    meal_slot: str = "dinner"
    recipe_id: str = "recipe-1"
    servings: Decimal = Decimal("2.0")
    batch_id: Optional[str] = None
    profile_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: str = "2026-03-16T00:00:00"
    updated_at: str = "2026-03-16T00:00:00"
    deleted_at: Optional[str] = None


@dataclass
class MockLeftoverBatch:
    id: str = "batch-1"
    recipe_id: str = "recipe-1"
    initial_servings: int = 6
    servings_remaining: int = 6
    prepared_date: date = date(2026, 3, 16)
    created_at: str = "2026-03-16T00:00:00"
    updated_at: str = "2026-03-16T00:00:00"
    deleted_at: Optional[str] = None

    def consume(self, servings: int = 1) -> int:
        self.servings_remaining = max(0, self.servings_remaining - servings)
        if self.servings_remaining == 0:
            self.soft_delete()
        return self.servings_remaining

    def soft_delete(self) -> None:
        self.deleted_at = "2026-03-16T00:00:00"


def _make_service(
    planning_repo: AsyncMock = None,
    recipe_service: AsyncMock = None,
) -> PlanningService:
    if planning_repo is None:
        planning_repo = AsyncMock()
    if recipe_service is None:
        recipe_service = AsyncMock()
    return PlanningService(planning_repo, recipe_service)


# --- Meal Plan Entry CRUD ---


async def test_add_meal_creates_entry():
    """Adding a meal creates a plan entry when recipe exists."""
    planning_repo = AsyncMock()
    recipe_service = AsyncMock()
    recipe_service.get_recipe.return_value = MockRecipe()
    planning_repo.create_entry.side_effect = lambda e: e

    service = _make_service(planning_repo, recipe_service)
    result = await service.add_meal(
        target_date=date(2026, 3, 16),
        meal_slot="dinner",
        recipe_id="recipe-1",
        servings=2.0,
    )

    assert result is not None
    assert result.recipe_id == "recipe-1"
    assert result.meal_slot == "dinner"
    assert float(result.servings) == 2.0
    planning_repo.create_entry.assert_awaited_once()


async def test_add_meal_returns_none_for_missing_recipe():
    """Adding a meal with nonexistent recipe returns None."""
    recipe_service = AsyncMock()
    recipe_service.get_recipe.return_value = None

    service = _make_service(recipe_service=recipe_service)
    result = await service.add_meal(
        target_date=date(2026, 3, 16),
        meal_slot="lunch",
        recipe_id="missing",
    )

    assert result is None


async def test_remove_meal_success():
    """Removing an existing meal returns True."""
    planning_repo = AsyncMock()
    planning_repo.get_entry_by_id.return_value = MockMealPlanEntry()

    service = _make_service(planning_repo)
    result = await service.remove_meal("entry-1")

    assert result is True
    planning_repo.delete_entry.assert_awaited_once_with("entry-1")


async def test_remove_meal_not_found():
    """Removing a nonexistent meal returns False."""
    planning_repo = AsyncMock()
    planning_repo.get_entry_by_id.return_value = None

    service = _make_service(planning_repo)
    result = await service.remove_meal("missing")

    assert result is False


async def test_reschedule_meal_updates_date_and_slot():
    """Rescheduling changes date and optionally the slot."""
    planning_repo = AsyncMock()
    entry = MockMealPlanEntry()
    planning_repo.get_entry_by_id.return_value = entry
    planning_repo.update_entry.side_effect = lambda e: e

    service = _make_service(planning_repo)
    result = await service.reschedule_meal(
        entry_id="entry-1",
        new_date=date(2026, 3, 18),
        new_slot="lunch",
    )

    assert result is not None
    assert result.date == date(2026, 3, 18)
    assert result.meal_slot == "lunch"


async def test_reschedule_meal_not_found():
    """Rescheduling a nonexistent meal returns None."""
    planning_repo = AsyncMock()
    planning_repo.get_entry_by_id.return_value = None

    service = _make_service(planning_repo)
    result = await service.reschedule_meal("missing", date(2026, 3, 18))

    assert result is None


async def test_reschedule_keeps_slot_when_not_provided():
    """Rescheduling without new_slot keeps the original slot."""
    planning_repo = AsyncMock()
    entry = MockMealPlanEntry(meal_slot="breakfast")
    planning_repo.get_entry_by_id.return_value = entry
    planning_repo.update_entry.side_effect = lambda e: e

    service = _make_service(planning_repo)
    result = await service.reschedule_meal("entry-1", date(2026, 3, 20))

    assert result.meal_slot == "breakfast"


# --- Batch Tracking ---


async def test_create_batch_success():
    """Creating a batch for an existing recipe succeeds."""
    planning_repo = AsyncMock()
    recipe_service = AsyncMock()
    recipe_service.get_recipe.return_value = MockRecipe()
    planning_repo.create_batch.side_effect = lambda b: b

    service = _make_service(planning_repo, recipe_service)
    result = await service.create_batch(
        recipe_id="recipe-1",
        prepared_servings=6,
        prepared_date=date(2026, 3, 16),
    )

    assert result is not None
    assert result.initial_servings == 6
    assert result.servings_remaining == 6
    planning_repo.create_batch.assert_awaited_once()


async def test_create_batch_missing_recipe():
    """Creating a batch for a nonexistent recipe returns None."""
    recipe_service = AsyncMock()
    recipe_service.get_recipe.return_value = None

    service = _make_service(recipe_service=recipe_service)
    result = await service.create_batch("missing", 6)

    assert result is None


async def test_create_batch_invalid_servings():
    """Creating a batch with 0 or negative servings returns None."""
    recipe_service = AsyncMock()
    recipe_service.get_recipe.return_value = MockRecipe()

    service = _make_service(recipe_service=recipe_service)
    result = await service.create_batch("recipe-1", 0)

    assert result is None


async def test_consume_batch_decrements():
    """Consuming from a batch decrements remaining servings."""
    planning_repo = AsyncMock()
    batch = MockLeftoverBatch(servings_remaining=4)
    planning_repo.get_batch_by_id.return_value = batch
    planning_repo.update_batch.side_effect = lambda b: b

    service = _make_service(planning_repo)
    result = await service.consume_batch("batch-1", servings_consumed=2)

    assert result is not None
    assert result.servings_remaining == 2


async def test_consume_batch_not_found():
    """Consuming from a nonexistent batch returns None."""
    planning_repo = AsyncMock()
    planning_repo.get_batch_by_id.return_value = None

    service = _make_service(planning_repo)
    result = await service.consume_batch("missing")

    assert result is None


async def test_consume_batch_insufficient_servings():
    """Consuming more than remaining returns None."""
    planning_repo = AsyncMock()
    batch = MockLeftoverBatch(servings_remaining=2)
    planning_repo.get_batch_by_id.return_value = batch

    service = _make_service(planning_repo)
    result = await service.consume_batch("batch-1", servings_consumed=5)

    assert result is None


async def test_consume_batch_invalid_servings():
    """Consuming 0 or negative servings returns None."""
    planning_repo = AsyncMock()
    batch = MockLeftoverBatch(servings_remaining=4)
    planning_repo.get_batch_by_id.return_value = batch

    service = _make_service(planning_repo)
    result = await service.consume_batch("batch-1", servings_consumed=0)

    assert result is None


async def test_consume_batch_soft_deletes_when_empty():
    """Consuming all remaining servings soft-deletes the batch."""
    planning_repo = AsyncMock()
    batch = MockLeftoverBatch(servings_remaining=1)
    planning_repo.get_batch_by_id.return_value = batch
    planning_repo.update_batch.side_effect = lambda b: b

    service = _make_service(planning_repo)
    result = await service.consume_batch("batch-1", servings_consumed=1)

    assert result is not None
    assert result.servings_remaining == 0
    assert result.deleted_at is not None


# --- Batch-linked meals ---


async def test_add_meal_from_batch():
    """Adding a meal from a batch creates entry and decrements batch."""
    planning_repo = AsyncMock()
    batch = MockLeftoverBatch(servings_remaining=4)
    planning_repo.get_batch_by_id.return_value = batch
    planning_repo.create_entry.side_effect = lambda e: e
    planning_repo.update_batch.side_effect = lambda b: b

    service = _make_service(planning_repo)
    result = await service.add_meal_from_batch(
        batch_id="batch-1",
        target_date=date(2026, 3, 17),
        meal_slot="lunch",
        servings_consumed=1,
    )

    assert result is not None
    assert result.batch_id == "batch-1"
    assert result.recipe_id == "recipe-1"
    assert batch.servings_remaining == 3


async def test_add_meal_from_batch_insufficient():
    """Adding a meal from a batch with insufficient servings returns None."""
    planning_repo = AsyncMock()
    batch = MockLeftoverBatch(servings_remaining=1)
    planning_repo.get_batch_by_id.return_value = batch

    service = _make_service(planning_repo)
    result = await service.add_meal_from_batch(
        batch_id="batch-1",
        target_date=date(2026, 3, 17),
        meal_slot="lunch",
        servings_consumed=5,
    )

    assert result is None


async def test_add_meal_from_batch_not_found():
    """Adding a meal from a nonexistent batch returns None."""
    planning_repo = AsyncMock()
    planning_repo.get_batch_by_id.return_value = None

    service = _make_service(planning_repo)
    result = await service.add_meal_from_batch(
        batch_id="missing",
        target_date=date(2026, 3, 17),
        meal_slot="lunch",
    )

    assert result is None


# --- Week plan ---


async def test_get_week_plan_returns_7_days():
    """get_week_plan returns a structure with 7 days."""
    planning_repo = AsyncMock()
    recipe_service = AsyncMock()
    planning_repo.list_entries_for_week.return_value = []
    recipe_service.get_recipe_nutrition.return_value = None

    service = _make_service(planning_repo, recipe_service)
    result = await service.get_week_plan(date(2026, 3, 16))

    assert result["week_start"] == "2026-03-16"
    assert len(result["days"]) == 7


async def test_get_week_plan_includes_meals():
    """get_week_plan includes meals for days that have entries."""
    planning_repo = AsyncMock()
    recipe_service = AsyncMock()

    entry = MockMealPlanEntry(date=date(2026, 3, 16), meal_slot="dinner")
    planning_repo.list_entries_for_week.return_value = [entry]
    recipe_service.get_recipe.return_value = MockRecipe(title="Chicken Stir Fry")
    recipe_service.get_recipe_nutrition.return_value = None
    planning_repo.get_batch_by_id.return_value = None

    service = _make_service(planning_repo, recipe_service)
    result = await service.get_week_plan(date(2026, 3, 16))

    monday = result["days"][0]
    assert len(monday["meals"]) == 1
    assert monday["meals"][0]["title"] == "Chicken Stir Fry"


# --- Suggestions ---


async def test_get_suggestions_returns_recent_and_leftovers():
    """get_suggestions returns recent recipes and active batches."""
    planning_repo = AsyncMock()
    recipe_service = AsyncMock()

    recipe_service.list_recipes.return_value = ([MockRecipe()], 1)
    batch = MockLeftoverBatch()
    planning_repo.list_active_batches.return_value = [batch]
    recipe_service.get_recipe.return_value = MockRecipe()

    service = _make_service(planning_repo, recipe_service)
    result = await service.get_suggestions()

    assert len(result["recent"]) == 1
    assert len(result["leftovers"]) == 1
    assert result["leftovers"][0]["servings_remaining"] == 6
