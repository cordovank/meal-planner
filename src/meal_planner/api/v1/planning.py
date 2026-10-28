"""Meal planning API endpoints."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from meal_planner.api.schemas.planning import (
    BatchConsumeSchema,
    BatchCreateSchema,
    BatchFromMealSchema,
    BatchSchema,
    MealFromBatchSchema,
    MealPlanEntryCreateSchema,
    MealPlanEntryDetailSchema,
    RescheduleSchema,
    SuggestionResponseSchema,
    WeekPlanSchema,
)
from meal_planner.repository.sqlalchemy.repositories.food_repository import SQLAlchemyFoodRepository
from meal_planner.repository.sqlalchemy.repositories.planning_repository import SQLAlchemyPlanningRepository
from meal_planner.repository.sqlalchemy.repositories.recipe_repository import SQLAlchemyRecipeRepository
from meal_planner.repository.sqlalchemy.session import get_session
from meal_planner.services.planning_service import PlanningService
from meal_planner.services.recipe_service import RecipeService

router = APIRouter(tags=["planning"])


async def get_planning_service(session: AsyncSession = Depends(get_session)) -> PlanningService:
    """Dependency for planning service."""
    planning_repo = SQLAlchemyPlanningRepository(session)
    recipe_repo = SQLAlchemyRecipeRepository(session)
    food_repo = SQLAlchemyFoodRepository(session)
    recipe_service = RecipeService(recipe_repo, food_repo=food_repo)
    return PlanningService(planning_repo, recipe_service)


# --- Suggestions (MUST be before {week_start} to avoid path collision) ---


@router.get("/api/v1/plan/suggestions", response_model=SuggestionResponseSchema)
async def get_suggestions(
    target_date: Optional[str] = Query(None),
    meal_slot: Optional[str] = Query(None),
    service: PlanningService = Depends(get_planning_service),
) -> SuggestionResponseSchema:
    """Get recipe suggestions for meal planning."""
    parsed_date = None
    if target_date:
        try:
            parsed_date = date.fromisoformat(target_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    result = await service.get_suggestions(
        target_date=parsed_date,
        meal_slot=meal_slot,
    )
    return SuggestionResponseSchema(**result)


# --- Standalone Batch Management (static paths before dynamic) ---


@router.post("/api/v1/plan/batch", status_code=status.HTTP_201_CREATED)
async def create_batch(
    data: BatchCreateSchema,
    service: PlanningService = Depends(get_planning_service),
) -> dict:
    """Create a new leftover batch."""
    batch = await service.create_batch(
        recipe_id=data.recipe_id,
        prepared_servings=data.prepared_servings,
        prepared_date=data.prepared_date,
    )
    if not batch:
        raise HTTPException(status_code=404, detail="Recipe not found or invalid servings")

    return {
        "batch_id": batch.id,
        "recipe_id": batch.recipe_id,
        "initial_servings": batch.initial_servings,
        "servings_remaining": batch.servings_remaining,
        "prepared_date": batch.prepared_date.isoformat(),
    }


@router.get("/api/v1/plan/batch/active")
async def list_active_batches(
    service: PlanningService = Depends(get_planning_service),
) -> dict:
    """List all active leftover batches."""
    batches = await service.list_active_batches()
    items = []
    for batch in batches:
        items.append({
            "id": batch.id,
            "recipe_id": batch.recipe_id,
            "initial_servings": batch.initial_servings,
            "servings_remaining": batch.servings_remaining,
            "prepared_date": batch.prepared_date.isoformat(),
        })
    return {"items": items, "total": len(items)}


@router.post("/api/v1/plan/batch/{batch_id}/consume")
async def consume_batch(
    batch_id: str,
    data: BatchConsumeSchema,
    service: PlanningService = Depends(get_planning_service),
) -> dict:
    """Consume servings from a batch."""
    batch = await service.consume_batch(
        batch_id=batch_id,
        servings_consumed=data.servings_consumed,
    )
    if not batch:
        raise HTTPException(
            status_code=404,
            detail="Batch not found or insufficient servings remaining",
        )

    return {
        "batch_id": batch.id,
        "servings_remaining": batch.servings_remaining,
        "last_consumed": date.today().isoformat(),
    }


# --- Weekly Plan (dynamic path — must come after static /plan/... paths) ---


@router.get("/api/v1/plan/{week_start}", response_model=WeekPlanSchema)
async def get_week_plan(
    week_start: str,
    service: PlanningService = Depends(get_planning_service),
) -> WeekPlanSchema:
    """Get weekly plan for a week starting on a given date."""
    try:
        start_date = date.fromisoformat(week_start)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    plan = await service.get_week_plan(start_date)
    return WeekPlanSchema(**plan)


# --- Meal Plan Entries ---


@router.post(
    "/api/v1/plan/{target_date}/meals",
    status_code=status.HTTP_201_CREATED,
)
async def add_meal(
    target_date: str,
    data: MealPlanEntryCreateSchema,
    service: PlanningService = Depends(get_planning_service),
) -> dict:
    """Add a meal to the plan for a specific date."""
    try:
        parsed_date = date.fromisoformat(target_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    entry = await service.add_meal(
        target_date=parsed_date,
        meal_slot=data.meal_slot,
        recipe_id=data.recipe_id,
        servings=data.servings,
        profile_id=data.profile_id,
        notes=data.notes,
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return {
        "id": entry.id,
        "date": entry.date.isoformat(),
        "meal_slot": entry.meal_slot if isinstance(entry.meal_slot, str) else entry.meal_slot.value,
        "recipe_id": entry.recipe_id,
        "servings": float(entry.servings),
        "created_at": entry.created_at,
    }


@router.delete(
    "/api/v1/plan/{target_date}/meals/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_meal(
    target_date: str,
    entry_id: str,
    service: PlanningService = Depends(get_planning_service),
) -> None:
    """Remove a meal from the plan."""
    success = await service.remove_meal(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Meal plan entry not found")


@router.post("/api/v1/plan/{target_date}/reschedule")
async def reschedule_meal(
    target_date: str,
    data: RescheduleSchema,
    service: PlanningService = Depends(get_planning_service),
) -> dict:
    """Move a planned meal to a different date and/or meal slot."""
    entry = await service.reschedule_meal(
        entry_id=data.meal_id,
        new_date=data.new_date,
        new_slot=data.new_slot,
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Meal plan entry not found")

    return {
        "id": entry.id,
        "date": entry.date.isoformat(),
        "meal_slot": entry.meal_slot if isinstance(entry.meal_slot, str) else entry.meal_slot.value,
        "recipe_id": entry.recipe_id,
        "servings": float(entry.servings),
    }


# --- Batch from Meal Entry ---


@router.post("/api/v1/plan/{target_date}/meals/{entry_id}/batch")
async def create_batch_from_meal(
    target_date: str,
    entry_id: str,
    data: BatchFromMealSchema,
    service: PlanningService = Depends(get_planning_service),
) -> dict:
    """Mark a planned meal as batch-prepared."""
    entry = await service.get_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Meal plan entry not found")

    try:
        parsed_date = date.fromisoformat(target_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    batch = await service.create_batch(
        recipe_id=entry.recipe_id,
        prepared_servings=data.prepared_servings,
        prepared_date=parsed_date,
    )
    if not batch:
        raise HTTPException(status_code=400, detail="Could not create batch")

    # Link the meal entry to the batch
    entry.batch_id = batch.id
    await service.planning_repo.update_entry(entry)

    return {
        "batch_id": batch.id,
        "recipe_id": batch.recipe_id,
        "initial_servings": batch.initial_servings,
        "servings_remaining": batch.servings_remaining,
        "prepared_date": batch.prepared_date.isoformat(),
    }


# --- Batch-linked meals ---


@router.post(
    "/api/v1/plan/{target_date}/meals/from-batch",
    status_code=status.HTTP_201_CREATED,
)
async def add_meal_from_batch(
    target_date: str,
    data: MealFromBatchSchema,
    service: PlanningService = Depends(get_planning_service),
) -> dict:
    """Add a meal from a leftover batch and decrement servings."""
    try:
        parsed_date = date.fromisoformat(target_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    entry = await service.add_meal_from_batch(
        batch_id=data.batch_id,
        target_date=parsed_date,
        meal_slot=data.meal_slot,
        servings_consumed=data.servings_consumed,
        profile_id=data.profile_id,
    )
    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Batch not found or insufficient servings remaining",
        )

    return {
        "id": entry.id,
        "date": entry.date.isoformat(),
        "meal_slot": entry.meal_slot if isinstance(entry.meal_slot, str) else entry.meal_slot.value,
        "recipe_id": entry.recipe_id,
        "servings": float(entry.servings),
        "batch_id": entry.batch_id,
    }
