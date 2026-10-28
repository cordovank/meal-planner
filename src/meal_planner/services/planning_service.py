"""Planning service with meal planning, batch tracking, and nutrition aggregation."""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from meal_planner.repository.sqlalchemy.models.batch import LeftoverBatch, MealPlanEntry, MealSlot
from meal_planner.repository.sqlalchemy.repositories.planning_repository import PlanningRepositoryProtocol
from meal_planner.repository.sqlalchemy.repositories.recipe_repository import RecipeRepositoryProtocol
from meal_planner.services.recipe_service import RecipeService


class PlanningService:
    """Service for weekly meal planning, batch tracking, and nutrition aggregation."""

    def __init__(
        self,
        planning_repo: PlanningRepositoryProtocol,
        recipe_service: RecipeService,
    ):
        self.planning_repo = planning_repo
        self.recipe_service = recipe_service

    # --- Meal Plan Entries ---

    async def get_entry(self, entry_id: str) -> Optional[MealPlanEntry]:
        return await self.planning_repo.get_entry_by_id(entry_id)

    async def add_meal(
        self,
        target_date: date,
        meal_slot: str,
        recipe_id: str,
        servings: float = 1.0,
        profile_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[MealPlanEntry]:
        """Add a meal to the plan for a specific date."""
        recipe = await self.recipe_service.get_recipe(recipe_id)
        if not recipe:
            return None

        entry = MealPlanEntry(
            id=str(uuid.uuid4()),
            date=target_date,
            meal_slot=meal_slot,
            recipe_id=recipe_id,
            servings=Decimal(str(servings)),
            profile_id=profile_id,
            notes=notes,
        )
        return await self.planning_repo.create_entry(entry)

    async def remove_meal(self, entry_id: str) -> bool:
        """Remove a meal from the plan."""
        entry = await self.planning_repo.get_entry_by_id(entry_id)
        if not entry:
            return False
        await self.planning_repo.delete_entry(entry_id)
        return True

    async def reschedule_meal(
        self,
        entry_id: str,
        new_date: date,
        new_slot: Optional[str] = None,
    ) -> Optional[MealPlanEntry]:
        """Move a planned meal to a different date and/or slot."""
        entry = await self.planning_repo.get_entry_by_id(entry_id)
        if not entry:
            return None

        entry.date = new_date
        if new_slot is not None:
            entry.meal_slot = new_slot
        return await self.planning_repo.update_entry(entry)

    async def get_day_plan(self, target_date: date) -> list[MealPlanEntry]:
        """Get all meal plan entries for a specific date."""
        return await self.planning_repo.list_entries_for_date(target_date)

    async def get_week_plan(self, week_start: date) -> dict:
        """Get weekly plan with entries grouped by day.

        Returns a dict with week_start, days (list of day dicts), and weekly_totals.
        """
        entries = await self.planning_repo.list_entries_for_week(week_start)

        # Group entries by date
        by_date: dict[date, list[MealPlanEntry]] = defaultdict(list)
        for entry in entries:
            by_date[entry.date].append(entry)

        days = []
        weekly_totals = _empty_nutrition()

        for i in range(7):
            current_date = week_start + timedelta(days=i)
            day_entries = by_date.get(current_date, [])

            meals = []
            day_totals = _empty_nutrition()

            for entry in day_entries:
                meal_info = await self._build_meal_info(entry)
                meals.append(meal_info)

                # Accumulate day totals
                if meal_info.get("nutrition"):
                    for key in day_totals:
                        day_totals[key] += meal_info["nutrition"].get(key, 0)

            # Accumulate weekly totals
            for key in weekly_totals:
                weekly_totals[key] += day_totals[key]

            days.append({
                "date": current_date.isoformat(),
                "meals": meals,
                "totals": {k: round(v, 2) for k, v in day_totals.items()},
            })

        return {
            "week_start": week_start.isoformat(),
            "days": days,
            "weekly_totals": {k: round(v, 2) for k, v in weekly_totals.items()},
        }

    async def _build_meal_info(self, entry: MealPlanEntry) -> dict:
        """Build a meal info dict from a plan entry including nutrition."""
        recipe = await self.recipe_service.get_recipe(entry.recipe_id)
        title = recipe.title if recipe else "Unknown Recipe"

        # Get nutrition scaled to servings
        nutrition = None
        recipe_nutrition = await self.recipe_service.get_recipe_nutrition(entry.recipe_id)
        if recipe_nutrition and recipe_nutrition.get("per_serving"):
            per_serving = recipe_nutrition["per_serving"]
            servings_factor = float(entry.servings)
            nutrition = {
                k: round(v * servings_factor, 2)
                for k, v in per_serving.items()
            }

        # Check batch info
        batch_info = None
        if entry.batch_id:
            batch = await self.planning_repo.get_batch_by_id(entry.batch_id)
            if batch:
                batch_info = {
                    "batch_id": batch.id,
                    "servings_remaining": batch.servings_remaining,
                    "initial_servings": batch.initial_servings,
                }

        return {
            "id": entry.id,
            "meal_slot": entry.meal_slot if isinstance(entry.meal_slot, str) else entry.meal_slot.value,
            "recipe_id": entry.recipe_id,
            "title": title,
            "servings": float(entry.servings),
            "nutrition": nutrition,
            "batch": batch_info,
            "profile_id": entry.profile_id,
            "notes": entry.notes,
        }

    # --- Batch Tracking ---

    async def create_batch(
        self,
        recipe_id: str,
        prepared_servings: int,
        prepared_date: Optional[date] = None,
    ) -> Optional[LeftoverBatch]:
        """Create a new leftover batch for a recipe."""
        recipe = await self.recipe_service.get_recipe(recipe_id)
        if not recipe:
            return None

        if prepared_servings < 1:
            return None

        batch = LeftoverBatch(
            id=str(uuid.uuid4()),
            recipe_id=recipe_id,
            initial_servings=prepared_servings,
            servings_remaining=prepared_servings,
            prepared_date=prepared_date or date.today(),
        )
        return await self.planning_repo.create_batch(batch)

    async def consume_batch(
        self,
        batch_id: str,
        servings_consumed: int = 1,
    ) -> Optional[LeftoverBatch]:
        """Consume servings from a batch."""
        batch = await self.planning_repo.get_batch_by_id(batch_id)
        if not batch:
            return None

        if servings_consumed < 1:
            return None

        if servings_consumed > batch.servings_remaining:
            return None

        batch.consume(servings_consumed)
        return await self.planning_repo.update_batch(batch)

    async def get_batch(self, batch_id: str) -> Optional[LeftoverBatch]:
        return await self.planning_repo.get_batch_by_id(batch_id)

    async def list_active_batches(self) -> list[LeftoverBatch]:
        return await self.planning_repo.list_active_batches()

    async def get_batches_for_recipe(self, recipe_id: str) -> list[LeftoverBatch]:
        return await self.planning_repo.get_batches_for_recipe(recipe_id)

    # --- Batch-linked meal entry ---

    async def add_meal_from_batch(
        self,
        batch_id: str,
        target_date: date,
        meal_slot: str,
        servings_consumed: int = 1,
        profile_id: Optional[str] = None,
    ) -> Optional[MealPlanEntry]:
        """Add a meal from a leftover batch and decrement servings."""
        batch = await self.planning_repo.get_batch_by_id(batch_id)
        if not batch:
            return None

        if servings_consumed > batch.servings_remaining:
            return None

        # Create the meal entry linked to the batch
        entry = MealPlanEntry(
            id=str(uuid.uuid4()),
            date=target_date,
            meal_slot=meal_slot,
            recipe_id=batch.recipe_id,
            servings=Decimal(str(servings_consumed)),
            batch_id=batch_id,
            profile_id=profile_id,
        )
        created_entry = await self.planning_repo.create_entry(entry)

        # Decrement batch
        batch.consume(servings_consumed)
        await self.planning_repo.update_batch(batch)

        return created_entry

    # --- Suggestions ---

    async def get_suggestions(
        self,
        target_date: Optional[date] = None,
        meal_slot: Optional[str] = None,
        limit: int = 10,
    ) -> dict:
        """Get recipe suggestions for meal planning.

        Returns recent recipes and available leftover batches.
        """
        # Get recent recipes
        recipes, _ = await self.recipe_service.list_recipes(limit=limit)
        recent = [
            {"recipe_id": r.id, "title": r.title}
            for r in recipes
        ]

        # Get active batches as leftover suggestions
        batches = await self.planning_repo.list_active_batches()
        leftovers = []
        for batch in batches:
            recipe = await self.recipe_service.get_recipe(batch.recipe_id)
            if recipe:
                leftovers.append({
                    "batch_id": batch.id,
                    "recipe_id": batch.recipe_id,
                    "title": recipe.title,
                    "servings_remaining": batch.servings_remaining,
                    "prepared_date": batch.prepared_date.isoformat(),
                })

        return {
            "recent": recent,
            "leftovers": leftovers,
        }


def _empty_nutrition() -> dict:
    """Return a zeroed-out nutrition dict."""
    return {
        "calories": 0.0,
        "protein_g": 0.0,
        "carbohydrates_g": 0.0,
        "fat_g": 0.0,
        "added_sugar_g": 0.0,
        "fiber_g": 0.0,
        "total_sugar_g": 0.0,
        "sodium_mg": 0.0,
        "saturated_fat_g": 0.0,
    }
