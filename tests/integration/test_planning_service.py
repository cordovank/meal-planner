"""Integration tests for PlanningService with real database."""

from __future__ import annotations

import uuid
from datetime import date, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from meal_planner.repository.sqlalchemy.models.recipe import Recipe
from meal_planner.repository.sqlalchemy.repositories.planning_repository import SQLAlchemyPlanningRepository
from meal_planner.repository.sqlalchemy.repositories.recipe_repository import SQLAlchemyRecipeRepository
from meal_planner.services.planning_service import PlanningService
from meal_planner.services.recipe_service import RecipeService


async def _create_recipe(session: AsyncSession, title: str = "Integration Recipe") -> Recipe:
    """Helper to create a recipe in the DB."""
    recipe_repo = SQLAlchemyRecipeRepository(session)
    recipe = Recipe(
        id=str(uuid.uuid4()),
        title=title,
        base_servings=4,
        state="finalized",
    )
    return await recipe_repo.create(recipe)


def _make_service(session: AsyncSession) -> PlanningService:
    """Create a PlanningService wired to real repos."""
    planning_repo = SQLAlchemyPlanningRepository(session)
    recipe_repo = SQLAlchemyRecipeRepository(session)
    recipe_service = RecipeService(recipe_repo)
    return PlanningService(planning_repo, recipe_service)


# --- Meal Plan CRUD ---


async def test_add_and_retrieve_meal(db_session: AsyncSession):
    """Create a meal entry and retrieve it via day plan."""
    recipe = await _create_recipe(db_session)
    service = _make_service(db_session)
    today = date.today()

    entry = await service.add_meal(
        target_date=today,
        meal_slot="dinner",
        recipe_id=recipe.id,
        servings=2.0,
    )
    assert entry is not None

    day_entries = await service.get_day_plan(today)
    assert len(day_entries) >= 1
    assert any(e.id == entry.id for e in day_entries)


async def test_remove_meal_hides_from_plan(db_session: AsyncSession):
    """Removing a meal soft-deletes it from the day plan."""
    recipe = await _create_recipe(db_session)
    service = _make_service(db_session)
    today = date.today()

    entry = await service.add_meal(today, "lunch", recipe.id)
    assert await service.remove_meal(entry.id) is True

    day_entries = await service.get_day_plan(today)
    ids = [e.id for e in day_entries]
    assert entry.id not in ids


async def test_reschedule_meal_changes_date(db_session: AsyncSession):
    """Rescheduling moves a meal to a new date."""
    recipe = await _create_recipe(db_session)
    service = _make_service(db_session)
    today = date.today()
    tomorrow = today + timedelta(days=1)

    entry = await service.add_meal(today, "breakfast", recipe.id)
    rescheduled = await service.reschedule_meal(entry.id, tomorrow, "dinner")

    assert rescheduled is not None
    assert rescheduled.date == tomorrow
    assert rescheduled.meal_slot == "dinner"

    # Original day should no longer have it
    original_day = await service.get_day_plan(today)
    assert all(e.id != entry.id for e in original_day)


# --- Batch Tracking ---


async def test_create_and_consume_batch(db_session: AsyncSession):
    """Create a batch and consume servings from it."""
    recipe = await _create_recipe(db_session)
    service = _make_service(db_session)

    batch = await service.create_batch(recipe.id, 6, date.today())
    assert batch is not None
    assert batch.servings_remaining == 6

    updated = await service.consume_batch(batch.id, 2)
    assert updated.servings_remaining == 4


async def test_batch_soft_deleted_when_empty(db_session: AsyncSession):
    """A batch is soft-deleted when all servings are consumed."""
    recipe = await _create_recipe(db_session)
    service = _make_service(db_session)

    batch = await service.create_batch(recipe.id, 2, date.today())
    await service.consume_batch(batch.id, 2)

    # After consuming all, get_batch should return None (soft-deleted)
    result = await service.get_batch(batch.id)
    assert result is None


async def test_list_active_batches_excludes_empty(db_session: AsyncSession):
    """Active batch listing excludes fully consumed batches."""
    recipe = await _create_recipe(db_session)
    service = _make_service(db_session)

    batch = await service.create_batch(recipe.id, 1, date.today())
    await service.consume_batch(batch.id, 1)

    active = await service.list_active_batches()
    ids = [b.id for b in active]
    assert batch.id not in ids


# --- Batch-linked Meals ---


async def test_add_meal_from_batch_decrements(db_session: AsyncSession):
    """Adding a meal from a batch creates the entry and decrements remaining."""
    recipe = await _create_recipe(db_session)
    service = _make_service(db_session)
    today = date.today()

    batch = await service.create_batch(recipe.id, 4, today)
    entry = await service.add_meal_from_batch(
        batch_id=batch.id,
        target_date=today,
        meal_slot="lunch",
        servings_consumed=1,
    )

    assert entry is not None
    assert entry.batch_id == batch.id

    updated_batch = await service.get_batch(batch.id)
    assert updated_batch.servings_remaining == 3


# --- Week Plan ---


async def test_week_plan_structure(db_session: AsyncSession):
    """get_week_plan returns 7 days with correct dates."""
    service = _make_service(db_session)
    monday = date.today() - timedelta(days=date.today().weekday())

    plan = await service.get_week_plan(monday)
    assert len(plan["days"]) == 7
    assert plan["days"][0]["date"] == monday.isoformat()
    assert plan["days"][6]["date"] == (monday + timedelta(days=6)).isoformat()


async def test_week_plan_shows_added_meals(db_session: AsyncSession):
    """Meals added to a day show up in the weekly plan."""
    recipe = await _create_recipe(db_session, "Week Plan Test")
    service = _make_service(db_session)
    monday = date.today() - timedelta(days=date.today().weekday())

    await service.add_meal(monday, "breakfast", recipe.id, 1.5)
    plan = await service.get_week_plan(monday)

    monday_meals = plan["days"][0]["meals"]
    assert len(monday_meals) >= 1
    assert monday_meals[0]["title"] == "Week Plan Test"
    assert monday_meals[0]["servings"] == 1.5


# --- Suggestions ---


async def test_suggestions_include_recipes(db_session: AsyncSession):
    """Suggestions include recently created recipes."""
    recipe = await _create_recipe(db_session, "Suggestion Recipe")
    service = _make_service(db_session)

    suggestions = await service.get_suggestions()
    titles = [r["title"] for r in suggestions["recent"]]
    assert "Suggestion Recipe" in titles
