"""Food entry and nutrition record API endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from meal_planner.api.schemas.food import (
    FoodEntryCreateSchema,
    FoodEntryListResponseSchema,
    FoodEntrySchema,
    FoodEntryUpdateSchema,
    NutritionRecordCreateSchema,
    NutritionRecordSchema,
    NutritionRecordUpdateSchema,
)
from meal_planner.repository.sqlalchemy.repositories.food_repository import SQLAlchemyFoodRepository
from meal_planner.repository.sqlalchemy.session import get_session
from meal_planner.services.food_service import FoodService

router = APIRouter(tags=["food"])


async def get_food_service(session: AsyncSession = Depends(get_session)) -> FoodService:
    """Dependency for food service."""
    repo = SQLAlchemyFoodRepository(session)
    return FoodService(repo)


# --- FoodEntry endpoints ---


@router.get("/api/v1/food", response_model=FoodEntryListResponseSchema)
async def list_food_entries(
    category: Optional[str] = Query(None),
    is_custom: Optional[bool] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    q: Optional[str] = Query(None),
    service: FoodService = Depends(get_food_service),
) -> FoodEntryListResponseSchema:
    """List food entries with optional filtering and search."""
    if q:
        items = await service.search_food_entries(q, limit=limit)
        return FoodEntryListResponseSchema(
            items=[
                {
                    "id": entry.id,
                    "name": entry.name,
                    "brand": entry.brand,
                    "category": entry.category,
                    "source_type": entry.source_type,
                    "is_custom": entry.is_custom,
                    "created_at": entry.created_at,
                    "updated_at": entry.updated_at,
                    "deleted_at": entry.deleted_at,
                }
                for entry in items
            ],
            total=len(items),
            has_more=len(items) >= limit,
        )

    items, total = await service.list_food_entries(
        category=category, is_custom=is_custom, limit=limit, offset=offset
    )
    return FoodEntryListResponseSchema(
        items=[
            {
                "id": entry.id,
                "name": entry.name,
                "brand": entry.brand,
                "category": entry.category,
                "source_type": entry.source_type,
                "is_custom": entry.is_custom,
                "created_at": entry.created_at,
                "updated_at": entry.updated_at,
                "deleted_at": entry.deleted_at,
            }
            for entry in items
        ],
        total=total,
        has_more=(offset + limit) < total,
    )


@router.post("/api/v1/food", status_code=status.HTTP_201_CREATED)
async def create_food_entry(
    data: FoodEntryCreateSchema,
    service: FoodService = Depends(get_food_service),
) -> dict:
    """Create a new food entry in the ingredient library."""
    entry = await service.create_food_entry(
        name=data.name,
        brand=data.brand,
        category=data.category,
        source_type=data.source_type,
        source_id=data.source_id,
        is_custom=data.is_custom,
    )
    return {
        "id": entry.id,
        "name": entry.name,
        "source_type": entry.source_type,
        "is_custom": entry.is_custom,
        "created_at": entry.created_at,
    }


@router.get("/api/v1/food/{food_entry_id}", response_model=FoodEntrySchema)
async def get_food_entry(
    food_entry_id: str,
    service: FoodService = Depends(get_food_service),
) -> FoodEntrySchema:
    """Get food entry details with nutrition records."""
    entry = await service.get_food_entry(food_entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Food entry not found")

    records = await service.get_nutrition_records(food_entry_id)

    return FoodEntrySchema(
        id=entry.id,
        name=entry.name,
        brand=entry.brand,
        category=entry.category,
        source_type=entry.source_type,
        source_id=entry.source_id,
        is_custom=entry.is_custom,
        nutrition_records=[
            {
                "id": r.id,
                "food_entry_id": r.food_entry_id,
                "serving_size": r.serving_size,
                "serving_unit": r.serving_unit,
                "calories": r.calories,
                "protein_g": r.protein_g,
                "carbohydrates_g": r.carbohydrates_g,
                "fat_g": r.fat_g,
                "added_sugar_g": r.added_sugar_g,
                "fiber_g": r.fiber_g,
                "total_sugar_g": r.total_sugar_g,
                "sodium_mg": r.sodium_mg,
                "saturated_fat_g": r.saturated_fat_g,
                "source_type": r.source_type,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
                "deleted_at": r.deleted_at,
            }
            for r in records
        ],
        created_at=entry.created_at,
        updated_at=entry.updated_at,
        deleted_at=entry.deleted_at,
    )


@router.put("/api/v1/food/{food_entry_id}", response_model=dict)
async def update_food_entry(
    food_entry_id: str,
    data: FoodEntryUpdateSchema,
    service: FoodService = Depends(get_food_service),
) -> dict:
    """Update a food entry."""
    entry = await service.update_food_entry(
        food_entry_id, name=data.name, brand=data.brand, category=data.category
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Food entry not found")

    return {"id": entry.id, "name": entry.name, "brand": entry.brand, "category": entry.category}


@router.delete("/api/v1/food/{food_entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_food_entry(
    food_entry_id: str,
    service: FoodService = Depends(get_food_service),
) -> None:
    """Soft delete a food entry."""
    success = await service.delete_food_entry(food_entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Food entry not found")


# --- NutritionRecord endpoints ---


@router.post(
    "/api/v1/food/{food_entry_id}/nutrition",
    status_code=status.HTTP_201_CREATED,
)
async def add_nutrition_record(
    food_entry_id: str,
    data: NutritionRecordCreateSchema,
    service: FoodService = Depends(get_food_service),
) -> dict:
    """Add a nutrition record to a food entry."""
    record = await service.add_nutrition_record(
        food_entry_id=food_entry_id,
        serving_size=float(data.serving_size),
        serving_unit=data.serving_unit,
        calories=float(data.calories),
        protein_g=float(data.protein_g),
        carbohydrates_g=float(data.carbohydrates_g),
        fat_g=float(data.fat_g),
        added_sugar_g=float(data.added_sugar_g),
        source_type=data.source_type,
        fiber_g=float(data.fiber_g) if data.fiber_g is not None else None,
        total_sugar_g=float(data.total_sugar_g) if data.total_sugar_g is not None else None,
        sodium_mg=float(data.sodium_mg) if data.sodium_mg is not None else None,
        saturated_fat_g=float(data.saturated_fat_g) if data.saturated_fat_g is not None else None,
    )
    if not record:
        raise HTTPException(status_code=404, detail="Food entry not found")

    return {
        "id": record.id,
        "food_entry_id": record.food_entry_id,
        "calories": record.calories,
        "protein_g": record.protein_g,
        "source_type": record.source_type,
        "created_at": record.created_at,
    }


@router.put("/api/v1/food/nutrition/{record_id}")
async def update_nutrition_record(
    record_id: str,
    data: NutritionRecordUpdateSchema,
    service: FoodService = Depends(get_food_service),
) -> dict:
    """Update a nutrition record."""
    record = await service.update_nutrition_record(
        record_id=record_id,
        serving_size=float(data.serving_size) if data.serving_size is not None else None,
        serving_unit=data.serving_unit,
        calories=float(data.calories) if data.calories is not None else None,
        protein_g=float(data.protein_g) if data.protein_g is not None else None,
        carbohydrates_g=float(data.carbohydrates_g) if data.carbohydrates_g is not None else None,
        fat_g=float(data.fat_g) if data.fat_g is not None else None,
        added_sugar_g=float(data.added_sugar_g) if data.added_sugar_g is not None else None,
        source_type=data.source_type,
        fiber_g=float(data.fiber_g) if data.fiber_g is not None else None,
        total_sugar_g=float(data.total_sugar_g) if data.total_sugar_g is not None else None,
        sodium_mg=float(data.sodium_mg) if data.sodium_mg is not None else None,
        saturated_fat_g=float(data.saturated_fat_g) if data.saturated_fat_g is not None else None,
    )
    if not record:
        raise HTTPException(status_code=404, detail="Nutrition record not found")

    return {"id": record.id, "calories": record.calories, "protein_g": record.protein_g}


@router.delete(
    "/api/v1/food/nutrition/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_nutrition_record(
    record_id: str,
    service: FoodService = Depends(get_food_service),
) -> None:
    """Remove a nutrition record."""
    success = await service.remove_nutrition_record(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Nutrition record not found")
