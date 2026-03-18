"""Profile service with business logic for nutrition targets and comparisons."""

from __future__ import annotations

import uuid
from typing import Optional

from meal_planner.config import settings
from meal_planner.repository.sqlalchemy.models.profile import Profile, ProfileTarget
from meal_planner.repository.sqlalchemy.repositories.profile_repository import ProfileRepositoryProtocol


# Valid nutrient keys with their default units
VALID_NUTRIENT_KEYS = {
    "protein_g": "g",
    "carbohydrates_g": "g",
    "fat_g": "g",
    "added_sugar_g": "g",
    "fiber_g": "g",
    "sodium_mg": "mg",
    "saturated_fat_g": "g",
}

# Default tolerance values from settings
DEFAULT_TOLERANCES = {
    "protein_g": settings.protein_tolerance_default,
    "carbohydrates_g": settings.carb_tolerance_default,
    "fat_g": settings.fat_tolerance_default,
    "added_sugar_g": settings.added_sugar_tolerance_default,
}


class ProfileService:
    """Service for profile and nutrition target operations."""

    def __init__(self, profile_repo: ProfileRepositoryProtocol):
        self.profile_repo = profile_repo

    async def get_profile(self, profile_id: str) -> Optional[Profile]:
        return await self.profile_repo.get_by_id(profile_id)

    async def list_profiles(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Profile], int]:
        return await self.profile_repo.list_profiles(limit=limit, offset=offset)

    async def create_profile(
        self,
        name: str,
        calorie_target: Optional[int] = None,
        calorie_tolerance: Optional[int] = None,
        is_default: bool = False,
        targets: Optional[dict[str, dict]] = None,
        user_id: Optional[str] = None,
    ) -> Profile:
        """Create a profile with nutrition targets.

        Args:
            name: Profile display name.
            calorie_target: Daily calorie goal (optional).
            calorie_tolerance: ± tolerance for calories.
            is_default: Whether this is the default profile.
            targets: Dict of nutrient_key -> {"target": float, "tolerance": float}.
            user_id: Owner user ID (nullable in Phase 1).
        """
        if is_default:
            await self.profile_repo.clear_default()

        profile = Profile(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=name,
            calorie_target=calorie_target,
            calorie_tolerance=calorie_tolerance or settings.calorie_tolerance_default,
            is_default=is_default,
        )
        created = await self.profile_repo.create(profile)

        if targets:
            for nutrient_key, values in targets.items():
                if nutrient_key not in VALID_NUTRIENT_KEYS:
                    continue
                target_value = values.get("target", 0)
                raw_tolerance = values.get("tolerance")
                tolerance_value = (
                    raw_tolerance
                    if raw_tolerance is not None
                    else DEFAULT_TOLERANCES.get(nutrient_key, 0)
                )
                target = ProfileTarget(
                    id=str(uuid.uuid4()),
                    profile_id=created.id,
                    nutrient_key=nutrient_key,
                    target_value=target_value,
                    tolerance_value=tolerance_value,
                    unit=VALID_NUTRIENT_KEYS[nutrient_key],
                )
                await self.profile_repo.add_target(target)

        # Reload to include targets
        return await self.profile_repo.get_by_id(created.id)

    async def update_profile(
        self,
        profile_id: str,
        name: Optional[str] = None,
        calorie_target: Optional[int] = None,
        calorie_tolerance: Optional[int] = None,
        is_default: Optional[bool] = None,
        targets: Optional[dict[str, dict]] = None,
    ) -> Optional[Profile]:
        """Update a profile and optionally replace all targets."""
        profile = await self.profile_repo.get_by_id(profile_id)
        if not profile:
            return None

        if name is not None:
            profile.name = name
        if calorie_target is not None:
            profile.calorie_target = calorie_target
        if calorie_tolerance is not None:
            profile.calorie_tolerance = calorie_tolerance
        if is_default is not None and is_default:
            await self.profile_repo.clear_default()
            profile.is_default = True
        elif is_default is not None:
            profile.is_default = False

        await self.profile_repo.update(profile)

        if targets is not None:
            await self.profile_repo.remove_targets(profile_id)
            for nutrient_key, values in targets.items():
                if nutrient_key not in VALID_NUTRIENT_KEYS:
                    continue
                target_value = values.get("target", 0)
                raw_tolerance = values.get("tolerance")
                tolerance_value = (
                    raw_tolerance
                    if raw_tolerance is not None
                    else DEFAULT_TOLERANCES.get(nutrient_key, 0)
                )
                target = ProfileTarget(
                    id=str(uuid.uuid4()),
                    profile_id=profile_id,
                    nutrient_key=nutrient_key,
                    target_value=target_value,
                    tolerance_value=tolerance_value,
                    unit=VALID_NUTRIENT_KEYS[nutrient_key],
                )
                await self.profile_repo.add_target(target)

        return await self.profile_repo.get_by_id(profile_id)

    async def delete_profile(self, profile_id: str) -> bool:
        profile = await self.profile_repo.get_by_id(profile_id)
        if not profile:
            return False
        await self.profile_repo.delete(profile_id)
        return True

    async def get_default_profile(self) -> Optional[Profile]:
        return await self.profile_repo.get_default_profile()

    def compare_nutrition(
        self,
        profile: Profile,
        nutrition: dict,
        portion_size: float = 1.0,
    ) -> dict:
        """Compare recipe/meal nutrition against a profile's targets.

        Args:
            profile: Profile with loaded targets.
            nutrition: Dict with per_serving nutrition totals.
            portion_size: Number of portions being consumed.

        Returns:
            Comparison result with fit status, details, and gaps.
        """
        details = {}
        gaps = []
        statuses = []

        # Compare calorie target
        if profile.calorie_target:
            actual_cal = float(nutrition.get("calories", 0)) * portion_size
            target_cal = float(profile.calorie_target)
            tolerance_cal = float(profile.calorie_tolerance)
            status = _compute_status(actual_cal, target_cal, tolerance_cal)
            details["calories"] = {
                "actual": round(actual_cal, 2),
                "target": target_cal,
                "tolerance": tolerance_cal,
                "status": status,
            }
            statuses.append(status)
            if actual_cal < target_cal - tolerance_cal:
                gaps.append({
                    "nutrient": "calories",
                    "short_by": round(target_cal - tolerance_cal - actual_cal, 2),
                })

        # Compare macro targets
        for target in (profile.targets or []):
            nutrient_key = target.nutrient_key
            actual = float(nutrition.get(nutrient_key, 0)) * portion_size
            target_val = float(target.target_value)
            tolerance_val = float(target.tolerance_value)
            status = _compute_status(actual, target_val, tolerance_val)
            details[nutrient_key] = {
                "actual": round(actual, 2),
                "target": target_val,
                "tolerance": tolerance_val,
                "status": status,
            }
            statuses.append(status)
            if actual < target_val - tolerance_val:
                gaps.append({
                    "nutrient": nutrient_key,
                    "short_by": round(target_val - tolerance_val - actual, 2),
                })

        # Overall fit
        if not statuses:
            overall_fit = "no_targets"
        elif all(s == "within_range" for s in statuses):
            overall_fit = "within_range"
        elif any(s == "exceeding" for s in statuses):
            overall_fit = "exceeding"
        else:
            overall_fit = "approaching"

        return {
            "profile_name": profile.name,
            "fit": overall_fit,
            "details": details,
            "gaps": gaps,
        }


def _compute_status(actual: float, target: float, tolerance: float) -> str:
    """Determine fit status for a single nutrient.

    Returns: "within_range", "approaching", or "exceeding".
    """
    lower = target - tolerance
    upper = target + tolerance

    if lower <= actual <= upper:
        return "within_range"

    # Approaching: within 10% beyond tolerance boundary
    approach_margin = target * 0.1 if target > 0 else 0
    if (lower - approach_margin) <= actual <= (upper + approach_margin):
        return "approaching"

    return "exceeding"
