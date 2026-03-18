"""
Integration tests for profile service functionality.
Tests cover critical paths: CRUD operations, default profiles, target management, comparison logic.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from meal_planner.services.profile_service import ProfileService
# Import models to ensure mappers are registered
from meal_planner.repository.sqlalchemy.models.profile import Profile, ProfileTarget


@pytest.fixture
async def profile_service(db_session: AsyncSession):
    """Provide a profile service instance."""
    from meal_planner.repository.sqlalchemy.repositories.profile_repository import SQLAlchemyProfileRepository
    repo = SQLAlchemyProfileRepository(db_session)
    return ProfileService(repo)


@pytest.mark.asyncio
async def test_create_profile(profile_service: ProfileService):
    """Test creating a new profile with targets."""
    profile = await profile_service.create_profile(
        name="Test User",
        calorie_target=2000,
        targets={
            "protein_g": {"target": 150, "tolerance": 15},
            "fat_g": {"target": 70, "tolerance": 7},
        },
    )

    assert profile is not None
    assert profile.name == "Test User"
    assert profile.calorie_target == 2000
    assert len(profile.targets) == 2

    target_keys = {t.nutrient_key for t in profile.targets}
    assert "protein_g" in target_keys
    assert "fat_g" in target_keys


@pytest.mark.asyncio
async def test_get_profile(profile_service: ProfileService):
    """Test retrieving a profile by ID."""
    created = await profile_service.create_profile(
        name="Get Test", calorie_target=1800
    )
    retrieved = await profile_service.get_profile(created.id)
    assert retrieved is not None
    assert retrieved.name == "Get Test"


@pytest.mark.asyncio
async def test_update_profile(profile_service: ProfileService):
    """Test updating profile details and targets."""
    created = await profile_service.create_profile(
        name="Before Update",
        calorie_target=2000,
        targets={"protein_g": {"target": 100, "tolerance": 10}},
    )

    updated = await profile_service.update_profile(
        created.id,
        name="After Update",
        calorie_target=2200,
        targets={"fat_g": {"target": 80, "tolerance": 8}},
    )

    assert updated.name == "After Update"
    assert updated.calorie_target == 2200
    assert len(updated.targets) == 1
    assert updated.targets[0].nutrient_key == "fat_g"


@pytest.mark.asyncio
async def test_delete_profile(profile_service: ProfileService):
    """Test soft deleting a profile."""
    created = await profile_service.create_profile(name="Delete Me")
    result = await profile_service.delete_profile(created.id)
    assert result is True

    retrieved = await profile_service.get_profile(created.id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_default_profile(profile_service: ProfileService):
    """Test that only one default profile exists at a time."""
    first = await profile_service.create_profile(name="First", is_default=True)
    assert first.is_default is True

    second = await profile_service.create_profile(name="Second", is_default=True)
    assert second.is_default is True

    # First should no longer be default
    first_updated = await profile_service.get_profile(first.id)
    assert first_updated.is_default is False


@pytest.mark.asyncio
async def test_list_profiles(profile_service: ProfileService):
    """Test listing profiles."""
    await profile_service.create_profile(name="Alpha")
    await profile_service.create_profile(name="Beta")
    await profile_service.create_profile(name="Gamma")

    profiles, total = await profile_service.list_profiles()
    assert total >= 3


@pytest.mark.asyncio
async def test_compare_nutrition(profile_service: ProfileService):
    """Test comparing nutrition against profile targets."""
    profile = await profile_service.create_profile(
        name="Comparer",
        calorie_target=2000,
        calorie_tolerance=100,
        targets={
            "protein_g": {"target": 150, "tolerance": 15},
        },
    )

    nutrition = {
        "calories": 500,
        "protein_g": 40,
    }
    result = profile_service.compare_nutrition(profile, nutrition, portion_size=1.0)

    assert result["profile_name"] == "Comparer"
    assert "calories" in result["details"]
    assert "protein_g" in result["details"]
    assert result["fit"] in ("within_range", "approaching", "exceeding")
