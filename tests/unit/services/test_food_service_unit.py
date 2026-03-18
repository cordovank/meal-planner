"""Unit tests for FoodService methods using AsyncMock."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from unittest.mock import AsyncMock

from meal_planner.services.food_service import FoodService


@dataclass
class MockFoodEntry:
    id: str = "food-1"
    name: str = "Chicken"
    brand: Optional[str] = None
    category: Optional[str] = "protein"
    source_type: str = "user_created"
    is_custom: bool = True


@dataclass
class MockNutritionRecord:
    id: str = "nutr-1"
    food_entry_id: str = "food-1"
    serving_size: float = 100
    serving_unit: str = "g"
    calories: float = 165
    protein_g: float = 31
    carbohydrates_g: float = 0
    fat_g: float = 3.6
    added_sugar_g: float = 0
    source_type: str = "user_confirmed"


def _make_service(repo: AsyncMock) -> FoodService:
    return FoodService(repo)


# --- FoodEntry ---


async def test_get_food_entry_not_found():
    repo = AsyncMock()
    repo.get_by_id.return_value = None
    service = _make_service(repo)
    result = await service.get_food_entry("missing")
    assert result is None


async def test_update_food_entry_not_found():
    repo = AsyncMock()
    repo.get_by_id.return_value = None
    service = _make_service(repo)
    result = await service.update_food_entry("missing", name="New")
    assert result is None


async def test_update_food_entry_applies_fields():
    repo = AsyncMock()
    entry = MockFoodEntry()
    repo.get_by_id.return_value = entry
    repo.update.return_value = entry
    service = _make_service(repo)

    result = await service.update_food_entry("food-1", name="Updated", brand="Brand")
    assert entry.name == "Updated"
    assert entry.brand == "Brand"
    repo.update.assert_awaited_once()


async def test_delete_food_entry_not_found():
    repo = AsyncMock()
    repo.get_by_id.return_value = None
    service = _make_service(repo)
    result = await service.delete_food_entry("missing")
    assert result is False


async def test_delete_food_entry_success():
    repo = AsyncMock()
    repo.get_by_id.return_value = MockFoodEntry()
    service = _make_service(repo)
    result = await service.delete_food_entry("food-1")
    assert result is True
    repo.delete.assert_awaited_once_with("food-1")


# --- NutritionRecord ---


async def test_add_nutrition_record_food_not_found():
    repo = AsyncMock()
    repo.get_by_id.return_value = None
    service = _make_service(repo)

    result = await service.add_nutrition_record(
        food_entry_id="missing",
        serving_size=100,
        serving_unit="g",
        calories=100,
        protein_g=10,
        carbohydrates_g=10,
        fat_g=5,
        added_sugar_g=0,
        source_type="estimated",
    )
    assert result is None


async def test_add_nutrition_record_success():
    repo = AsyncMock()
    repo.get_by_id.return_value = MockFoodEntry()
    repo.add_nutrition_record.side_effect = lambda r: r
    service = _make_service(repo)

    result = await service.add_nutrition_record(
        food_entry_id="food-1",
        serving_size=100,
        serving_unit="g",
        calories=165,
        protein_g=31,
        carbohydrates_g=0,
        fat_g=3.6,
        added_sugar_g=0,
        source_type="user_confirmed",
    )
    assert result is not None
    assert result.calories == 165
    assert result.food_entry_id == "food-1"


async def test_remove_nutrition_record_not_found():
    repo = AsyncMock()
    repo.get_nutrition_record.return_value = None
    service = _make_service(repo)
    result = await service.remove_nutrition_record("missing")
    assert result is False


async def test_remove_nutrition_record_success():
    repo = AsyncMock()
    repo.get_nutrition_record.return_value = MockNutritionRecord()
    service = _make_service(repo)
    result = await service.remove_nutrition_record("nutr-1")
    assert result is True
    repo.remove_nutrition_record.assert_awaited_once_with("nutr-1")
