"""Food entry and nutrition record repository implementations."""

from __future__ import annotations

from typing import Optional, Protocol

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from meal_planner.repository.sqlalchemy.models.food import (
    FoodEntry,
    NutritionRecord,
)


class FoodRepositoryProtocol(Protocol):
    """Protocol for food entry repository operations."""

    async def get_by_id(self, food_entry_id: str) -> Optional[FoodEntry]:
        ...

    async def list_food_entries(
        self,
        category: Optional[str] = None,
        is_custom: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[FoodEntry], int]:
        ...

    async def create(self, food_entry: FoodEntry) -> FoodEntry:
        ...

    async def update(self, food_entry: FoodEntry) -> FoodEntry:
        ...

    async def delete(self, food_entry_id: str) -> None:
        ...

    async def search(self, query: str, limit: int = 20) -> list[FoodEntry]:
        ...

    async def get_nutrition_records(self, food_entry_id: str) -> list[NutritionRecord]:
        ...

    async def add_nutrition_record(self, record: NutritionRecord) -> NutritionRecord:
        ...

    async def get_nutrition_record(self, record_id: str) -> Optional[NutritionRecord]:
        ...

    async def update_nutrition_record(self, record: NutritionRecord) -> NutritionRecord:
        ...

    async def remove_nutrition_record(self, record_id: str) -> None:
        ...


class SQLAlchemyFoodRepository:
    """SQLAlchemy implementation of FoodRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, food_entry_id: str) -> Optional[FoodEntry]:
        stmt = select(FoodEntry).where(
            (FoodEntry.id == food_entry_id) & (FoodEntry.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_food_entries(
        self,
        category: Optional[str] = None,
        is_custom: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[FoodEntry], int]:
        query = FoodEntry.deleted_at.is_(None)

        if category:
            query = and_(query, FoodEntry.category == category)
        if is_custom is not None:
            query = and_(query, FoodEntry.is_custom == is_custom)

        count_stmt = select(func.count(FoodEntry.id)).where(query)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        stmt = (
            select(FoodEntry)
            .where(query)
            .order_by(FoodEntry.name)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        entries = result.scalars().all()

        return entries, total

    async def create(self, food_entry: FoodEntry) -> FoodEntry:
        self.session.add(food_entry)
        await self.session.flush()
        await self.session.refresh(food_entry)
        return food_entry

    async def update(self, food_entry: FoodEntry) -> FoodEntry:
        await self.session.merge(food_entry)
        await self.session.flush()
        updated = await self.get_by_id(food_entry.id)
        return updated

    async def delete(self, food_entry_id: str) -> None:
        food_entry = await self.get_by_id(food_entry_id)
        if food_entry:
            food_entry.soft_delete()
            await self.session.flush()

    async def search(self, query: str, limit: int = 20) -> list[FoodEntry]:
        search_pattern = f"%{query}%"
        stmt = (
            select(FoodEntry)
            .where(
                and_(
                    FoodEntry.deleted_at.is_(None),
                    or_(
                        FoodEntry.name.ilike(search_pattern),
                        FoodEntry.brand.ilike(search_pattern),
                    ),
                )
            )
            .order_by(FoodEntry.name)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    # --- NutritionRecord operations ---

    async def get_nutrition_records(self, food_entry_id: str) -> list[NutritionRecord]:
        stmt = select(NutritionRecord).where(
            NutritionRecord.food_entry_id == food_entry_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_nutrition_record(self, record: NutritionRecord) -> NutritionRecord:
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def get_nutrition_record(self, record_id: str) -> Optional[NutritionRecord]:
        return await self.session.get(NutritionRecord, record_id)

    async def update_nutrition_record(self, record: NutritionRecord) -> NutritionRecord:
        await self.session.merge(record)
        await self.session.flush()
        updated = await self.session.get(NutritionRecord, record.id)
        return updated

    async def remove_nutrition_record(self, record_id: str) -> None:
        record = await self.session.get(NutritionRecord, record_id)
        if record:
            await self.session.delete(record)
            await self.session.flush()
