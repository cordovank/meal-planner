"""Planning and leftover batch repository implementations."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional, Protocol

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from meal_planner.repository.sqlalchemy.models.batch import LeftoverBatch, MealPlanEntry


class PlanningRepositoryProtocol(Protocol):
    """Protocol for planning repository operations."""

    # --- MealPlanEntry ---

    async def get_entry_by_id(self, entry_id: str) -> Optional[MealPlanEntry]:
        ...

    async def list_entries_for_date(self, target_date: date) -> list[MealPlanEntry]:
        ...

    async def list_entries_for_week(
        self, week_start: date
    ) -> list[MealPlanEntry]:
        ...

    async def create_entry(self, entry: MealPlanEntry) -> MealPlanEntry:
        ...

    async def update_entry(self, entry: MealPlanEntry) -> MealPlanEntry:
        ...

    async def delete_entry(self, entry_id: str) -> None:
        ...

    # --- LeftoverBatch ---

    async def get_batch_by_id(self, batch_id: str) -> Optional[LeftoverBatch]:
        ...

    async def list_active_batches(self) -> list[LeftoverBatch]:
        ...

    async def create_batch(self, batch: LeftoverBatch) -> LeftoverBatch:
        ...

    async def update_batch(self, batch: LeftoverBatch) -> LeftoverBatch:
        ...

    async def get_batches_for_recipe(self, recipe_id: str) -> list[LeftoverBatch]:
        ...


class SQLAlchemyPlanningRepository:
    """SQLAlchemy implementation of PlanningRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # --- MealPlanEntry ---

    async def get_entry_by_id(self, entry_id: str) -> Optional[MealPlanEntry]:
        stmt = select(MealPlanEntry).where(
            (MealPlanEntry.id == entry_id) & (MealPlanEntry.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_entries_for_date(self, target_date: date) -> list[MealPlanEntry]:
        stmt = (
            select(MealPlanEntry)
            .where(
                and_(
                    MealPlanEntry.deleted_at.is_(None),
                    MealPlanEntry.date == target_date,
                )
            )
            .order_by(MealPlanEntry.meal_slot, MealPlanEntry.created_at)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_entries_for_week(
        self, week_start: date
    ) -> list[MealPlanEntry]:
        week_end = week_start + timedelta(days=6)
        stmt = (
            select(MealPlanEntry)
            .where(
                and_(
                    MealPlanEntry.deleted_at.is_(None),
                    MealPlanEntry.date >= week_start,
                    MealPlanEntry.date <= week_end,
                )
            )
            .order_by(MealPlanEntry.date, MealPlanEntry.meal_slot, MealPlanEntry.created_at)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_entry(self, entry: MealPlanEntry) -> MealPlanEntry:
        self.session.add(entry)
        await self.session.flush()
        await self.session.refresh(entry)
        return entry

    async def update_entry(self, entry: MealPlanEntry) -> MealPlanEntry:
        await self.session.merge(entry)
        await self.session.flush()
        updated = await self.get_entry_by_id(entry.id)
        return updated

    async def delete_entry(self, entry_id: str) -> None:
        entry = await self.get_entry_by_id(entry_id)
        if entry:
            entry.soft_delete()
            await self.session.flush()

    # --- LeftoverBatch ---

    async def get_batch_by_id(self, batch_id: str) -> Optional[LeftoverBatch]:
        stmt = select(LeftoverBatch).where(
            (LeftoverBatch.id == batch_id) & (LeftoverBatch.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_active_batches(self) -> list[LeftoverBatch]:
        stmt = (
            select(LeftoverBatch)
            .where(
                and_(
                    LeftoverBatch.deleted_at.is_(None),
                    LeftoverBatch.servings_remaining > 0,
                )
            )
            .order_by(LeftoverBatch.prepared_date.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_batch(self, batch: LeftoverBatch) -> LeftoverBatch:
        self.session.add(batch)
        await self.session.flush()
        await self.session.refresh(batch)
        return batch

    async def update_batch(self, batch: LeftoverBatch) -> LeftoverBatch:
        await self.session.merge(batch)
        await self.session.flush()
        updated = await self.get_batch_by_id(batch.id)
        return updated

    async def get_batches_for_recipe(self, recipe_id: str) -> list[LeftoverBatch]:
        stmt = (
            select(LeftoverBatch)
            .where(
                and_(
                    LeftoverBatch.deleted_at.is_(None),
                    LeftoverBatch.recipe_id == recipe_id,
                    LeftoverBatch.servings_remaining > 0,
                )
            )
            .order_by(LeftoverBatch.prepared_date.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
