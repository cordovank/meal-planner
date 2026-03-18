"""Profile management API endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from meal_planner.api.schemas.profile import (
    ProfileCompareRequestSchema,
    ProfileCompareResponseSchema,
    ProfileCreateSchema,
    ProfileListResponseSchema,
    ProfileSchema,
    ProfileUpdateSchema,
)
from meal_planner.repository.sqlalchemy.repositories.food_repository import SQLAlchemyFoodRepository
from meal_planner.repository.sqlalchemy.repositories.profile_repository import SQLAlchemyProfileRepository
from meal_planner.repository.sqlalchemy.repositories.recipe_repository import SQLAlchemyRecipeRepository
from meal_planner.repository.sqlalchemy.session import get_session
from meal_planner.services.profile_service import ProfileService
from meal_planner.services.recipe_service import RecipeService

router = APIRouter(tags=["profiles"])


async def get_profile_service(session: AsyncSession = Depends(get_session)) -> ProfileService:
    """Dependency for profile service."""
    repo = SQLAlchemyProfileRepository(session)
    return ProfileService(repo)


async def get_recipe_service(session: AsyncSession = Depends(get_session)) -> RecipeService:
    """Dependency for recipe service (used in compare endpoint)."""
    recipe_repo = SQLAlchemyRecipeRepository(session)
    food_repo = SQLAlchemyFoodRepository(session)
    return RecipeService(recipe_repo, food_repo)


def _profile_to_response(profile) -> dict:
    """Convert a Profile model to a response dict with targets."""
    targets = {}
    for t in (profile.targets or []):
        targets[t.nutrient_key] = {
            "target": float(t.target_value),
            "tolerance": float(t.tolerance_value),
            "unit": t.unit,
        }
    return {
        "id": profile.id,
        "name": profile.name,
        "calorie_target": profile.calorie_target,
        "calorie_tolerance": profile.calorie_tolerance,
        "is_default": profile.is_default,
        "targets": targets,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at,
        "deleted_at": profile.deleted_at,
    }


# --- Profile CRUD ---


@router.get("/api/v1/profiles", response_model=ProfileListResponseSchema)
async def list_profiles(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileListResponseSchema:
    """List all profiles."""
    profiles, total = await service.list_profiles(limit=limit, offset=offset)
    return ProfileListResponseSchema(
        items=[_profile_to_response(p) for p in profiles],
        total=total,
        has_more=(offset + limit) < total,
    )


@router.post("/api/v1/profiles", status_code=status.HTTP_201_CREATED)
async def create_profile(
    data: ProfileCreateSchema,
    service: ProfileService = Depends(get_profile_service),
) -> dict:
    """Create a new profile with nutrition targets."""
    targets_dict = None
    if data.targets:
        targets_dict = {
            k: {"target": float(v.target), "tolerance": float(v.tolerance) if v.tolerance is not None else None}
            for k, v in data.targets.items()
        }

    profile = await service.create_profile(
        name=data.name,
        calorie_target=data.calorie_target,
        calorie_tolerance=data.calorie_tolerance,
        is_default=data.is_default,
        targets=targets_dict,
    )
    return _profile_to_response(profile)


@router.get("/api/v1/profiles/{profile_id}", response_model=ProfileSchema)
async def get_profile(
    profile_id: str,
    service: ProfileService = Depends(get_profile_service),
) -> ProfileSchema:
    """Get profile details with targets."""
    profile = await service.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _profile_to_response(profile)


@router.put("/api/v1/profiles/{profile_id}")
async def update_profile(
    profile_id: str,
    data: ProfileUpdateSchema,
    service: ProfileService = Depends(get_profile_service),
) -> dict:
    """Update a profile and its targets."""
    targets_dict = None
    if data.targets is not None:
        targets_dict = {
            k: {"target": float(v.target), "tolerance": float(v.tolerance) if v.tolerance is not None else None}
            for k, v in data.targets.items()
        }

    profile = await service.update_profile(
        profile_id=profile_id,
        name=data.name,
        calorie_target=data.calorie_target,
        calorie_tolerance=data.calorie_tolerance,
        is_default=data.is_default,
        targets=targets_dict,
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _profile_to_response(profile)


@router.delete("/api/v1/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: str,
    service: ProfileService = Depends(get_profile_service),
) -> None:
    """Soft delete a profile."""
    success = await service.delete_profile(profile_id)
    if not success:
        raise HTTPException(status_code=404, detail="Profile not found")


# --- Profile Comparison ---


@router.post("/api/v1/profiles/{profile_id}/compare", response_model=ProfileCompareResponseSchema)
async def compare_profile(
    profile_id: str,
    data: ProfileCompareRequestSchema,
    profile_service: ProfileService = Depends(get_profile_service),
    recipe_service: RecipeService = Depends(get_recipe_service),
) -> ProfileCompareResponseSchema:
    """Compare a recipe's nutrition against a profile's targets."""
    profile = await profile_service.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    nutrition = await recipe_service.get_recipe_nutrition(data.recipe_id)
    if not nutrition:
        raise HTTPException(status_code=404, detail="Recipe not found or no nutrition data")

    per_serving = nutrition["per_serving"]
    result = profile_service.compare_nutrition(profile, per_serving, data.portion_size)

    return ProfileCompareResponseSchema(**result)
