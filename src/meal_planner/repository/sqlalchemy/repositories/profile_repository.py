"""Profile and profile target repository implementations."""

from __future__ import annotations

from typing import Optional, Protocol

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from meal_planner.repository.sqlalchemy.models.profile import Profile, ProfileTarget


class ProfileRepositoryProtocol(Protocol):
    """Protocol for profile repository operations."""

    async def get_by_id(self, profile_id: str) -> Optional[Profile]:
        ...

    async def list_profiles(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Profile], int]:
        ...

    async def create(self, profile: Profile) -> Profile:
        ...

    async def update(self, profile: Profile) -> Profile:
        ...

    async def delete(self, profile_id: str) -> None:
        ...

    async def get_default_profile(self) -> Optional[Profile]:
        ...

    async def clear_default(self) -> None:
        ...

    async def get_targets(self, profile_id: str) -> list[ProfileTarget]:
        ...

    async def add_target(self, target: ProfileTarget) -> ProfileTarget:
        ...

    async def remove_targets(self, profile_id: str) -> None:
        ...


class SQLAlchemyProfileRepository:
    """SQLAlchemy implementation of ProfileRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, profile_id: str) -> Optional[Profile]:
        stmt = (
            select(Profile)
            .options(selectinload(Profile.targets))
            .where(
                (Profile.id == profile_id) & (Profile.deleted_at.is_(None))
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_profiles(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Profile], int]:
        query = Profile.deleted_at.is_(None)

        count_stmt = select(func.count(Profile.id)).where(query)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        stmt = (
            select(Profile)
            .options(selectinload(Profile.targets))
            .where(query)
            .order_by(Profile.name)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        profiles = result.scalars().all()

        return profiles, total

    async def create(self, profile: Profile) -> Profile:
        self.session.add(profile)
        await self.session.flush()
        await self.session.refresh(profile)
        return profile

    async def update(self, profile: Profile) -> Profile:
        await self.session.merge(profile)
        await self.session.flush()
        updated = await self.get_by_id(profile.id)
        return updated

    async def delete(self, profile_id: str) -> None:
        profile = await self.get_by_id(profile_id)
        if profile:
            profile.soft_delete()
            await self.session.flush()

    async def get_default_profile(self) -> Optional[Profile]:
        stmt = (
            select(Profile)
            .options(selectinload(Profile.targets))
            .where(
                and_(
                    Profile.deleted_at.is_(None),
                    Profile.is_default.is_(True),
                )
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def clear_default(self) -> None:
        """Unset is_default on all profiles."""
        stmt = (
            select(Profile)
            .where(
                and_(
                    Profile.deleted_at.is_(None),
                    Profile.is_default.is_(True),
                )
            )
        )
        result = await self.session.execute(stmt)
        for profile in result.scalars().all():
            profile.is_default = False
        await self.session.flush()

    async def get_targets(self, profile_id: str) -> list[ProfileTarget]:
        stmt = (
            select(ProfileTarget)
            .where(ProfileTarget.profile_id == profile_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_target(self, target: ProfileTarget) -> ProfileTarget:
        self.session.add(target)
        await self.session.flush()
        await self.session.refresh(target)
        return target

    async def remove_targets(self, profile_id: str) -> None:
        """Remove all targets for a profile (used before re-creating on update)."""
        targets = await self.get_targets(profile_id)
        for target in targets:
            await self.session.delete(target)
        await self.session.flush()
        # Expire the profile so its relationship cache is refreshed on next access
        profile = await self.session.get(Profile, profile_id)
        if profile:
            self.session.expire(profile, ["targets"])
