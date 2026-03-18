"""Food entry and nutrition record service with business logic."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Optional

from meal_planner.repository.sqlalchemy.models.food import (
    FoodEntry,
    FoodSourceType,
    NutritionRecord,
    NutritionSourceType,
)
from meal_planner.repository.sqlalchemy.repositories.food_repository import FoodRepositoryProtocol


class FoodService:
    """Service for food entry and nutrition record operations."""

    def __init__(self, food_repo: FoodRepositoryProtocol):
        self.food_repo = food_repo

    # --- FoodEntry CRUD ---

    async def get_food_entry(self, food_entry_id: str) -> Optional[FoodEntry]:
        return await self.food_repo.get_by_id(food_entry_id)

    async def list_food_entries(
        self,
        category: Optional[str] = None,
        is_custom: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[FoodEntry], int]:
        return await self.food_repo.list_food_entries(
            category=category, is_custom=is_custom, limit=limit, offset=offset
        )

    async def create_food_entry(
        self,
        name: str,
        brand: Optional[str] = None,
        category: Optional[str] = None,
        source_type: str = FoodSourceType.USER_CREATED,
        source_id: Optional[str] = None,
        is_custom: bool = True,
        user_id: Optional[str] = None,
    ) -> FoodEntry:
        food_entry = FoodEntry(
            id=str(uuid.uuid4()),
            name=name,
            brand=brand,
            category=category,
            source_type=source_type,
            source_id=source_id,
            is_custom=is_custom,
            user_id=user_id,
        )
        return await self.food_repo.create(food_entry)

    async def update_food_entry(
        self,
        food_entry_id: str,
        name: Optional[str] = None,
        brand: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Optional[FoodEntry]:
        food_entry = await self.food_repo.get_by_id(food_entry_id)
        if not food_entry:
            return None

        if name is not None:
            food_entry.name = name
        if brand is not None:
            food_entry.brand = brand
        if category is not None:
            food_entry.category = category

        return await self.food_repo.update(food_entry)

    async def delete_food_entry(self, food_entry_id: str) -> bool:
        food_entry = await self.food_repo.get_by_id(food_entry_id)
        if not food_entry:
            return False
        await self.food_repo.delete(food_entry_id)
        return True

    async def search_food_entries(self, query: str, limit: int = 20) -> list[FoodEntry]:
        return await self.food_repo.search(query, limit=limit)

    # --- NutritionRecord CRUD ---

    async def get_nutrition_records(self, food_entry_id: str) -> list[NutritionRecord]:
        return await self.food_repo.get_nutrition_records(food_entry_id)

    async def add_nutrition_record(
        self,
        food_entry_id: str,
        serving_size: float,
        serving_unit: str,
        calories: float,
        protein_g: float,
        carbohydrates_g: float,
        fat_g: float,
        added_sugar_g: float,
        source_type: str,
        fiber_g: Optional[float] = None,
        total_sugar_g: Optional[float] = None,
        sodium_mg: Optional[float] = None,
        saturated_fat_g: Optional[float] = None,
    ) -> Optional[NutritionRecord]:
        food_entry = await self.food_repo.get_by_id(food_entry_id)
        if not food_entry:
            return None

        record = NutritionRecord(
            id=str(uuid.uuid4()),
            food_entry_id=food_entry_id,
            serving_size=serving_size,
            serving_unit=serving_unit,
            calories=calories,
            protein_g=protein_g,
            carbohydrates_g=carbohydrates_g,
            fat_g=fat_g,
            added_sugar_g=added_sugar_g,
            source_type=source_type,
            fiber_g=fiber_g,
            total_sugar_g=total_sugar_g,
            sodium_mg=sodium_mg,
            saturated_fat_g=saturated_fat_g,
        )
        return await self.food_repo.add_nutrition_record(record)

    async def update_nutrition_record(
        self,
        record_id: str,
        serving_size: Optional[float] = None,
        serving_unit: Optional[str] = None,
        calories: Optional[float] = None,
        protein_g: Optional[float] = None,
        carbohydrates_g: Optional[float] = None,
        fat_g: Optional[float] = None,
        added_sugar_g: Optional[float] = None,
        source_type: Optional[str] = None,
        fiber_g: Optional[float] = None,
        total_sugar_g: Optional[float] = None,
        sodium_mg: Optional[float] = None,
        saturated_fat_g: Optional[float] = None,
    ) -> Optional[NutritionRecord]:
        record = await self.food_repo.get_nutrition_record(record_id)
        if not record:
            return None

        if serving_size is not None:
            record.serving_size = serving_size
        if serving_unit is not None:
            record.serving_unit = serving_unit
        if calories is not None:
            record.calories = calories
        if protein_g is not None:
            record.protein_g = protein_g
        if carbohydrates_g is not None:
            record.carbohydrates_g = carbohydrates_g
        if fat_g is not None:
            record.fat_g = fat_g
        if added_sugar_g is not None:
            record.added_sugar_g = added_sugar_g
        if source_type is not None:
            record.source_type = source_type
        if fiber_g is not None:
            record.fiber_g = fiber_g
        if total_sugar_g is not None:
            record.total_sugar_g = total_sugar_g
        if sodium_mg is not None:
            record.sodium_mg = sodium_mg
        if saturated_fat_g is not None:
            record.saturated_fat_g = saturated_fat_g

        return await self.food_repo.update_nutrition_record(record)

    async def remove_nutrition_record(self, record_id: str) -> bool:
        record = await self.food_repo.get_nutrition_record(record_id)
        if not record:
            return False
        await self.food_repo.remove_nutrition_record(record_id)
        return True
