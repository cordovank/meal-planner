"""Unit tests for ProfileService methods using AsyncMock."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from unittest.mock import AsyncMock

from meal_planner.services.profile_service import ProfileService, _compute_status


@dataclass
class MockProfile:
    id: str = "profile-1"
    name: str = "Test"
    calorie_target: Optional[int] = 2000
    calorie_tolerance: int = 100
    is_default: bool = False
    targets: list = field(default_factory=list)
    user_id: Optional[str] = None
    created_at: str = "2026-01-01"
    updated_at: str = "2026-01-01"
    deleted_at: Optional[str] = None


@dataclass
class MockProfileTarget:
    id: str = "target-1"
    profile_id: str = "profile-1"
    nutrient_key: str = "protein_g"
    target_value: float = 150.0
    tolerance_value: float = 15.0
    unit: str = "g"


def _make_service(repo: AsyncMock) -> ProfileService:
    return ProfileService(repo)


# --- Profile CRUD ---


async def test_get_profile_not_found():
    repo = AsyncMock()
    repo.get_by_id.return_value = None
    service = _make_service(repo)
    result = await service.get_profile("missing")
    assert result is None


async def test_get_profile_found():
    repo = AsyncMock()
    repo.get_by_id.return_value = MockProfile()
    service = _make_service(repo)
    result = await service.get_profile("profile-1")
    assert result.name == "Test"


async def test_delete_profile_not_found():
    repo = AsyncMock()
    repo.get_by_id.return_value = None
    service = _make_service(repo)
    result = await service.delete_profile("missing")
    assert result is False


async def test_delete_profile_success():
    repo = AsyncMock()
    repo.get_by_id.return_value = MockProfile()
    service = _make_service(repo)
    result = await service.delete_profile("profile-1")
    assert result is True
    repo.delete.assert_awaited_once_with("profile-1")


async def test_create_profile_sets_default():
    repo = AsyncMock()
    created = MockProfile(is_default=True)
    repo.create.return_value = created
    repo.get_by_id.return_value = created
    repo.add_target.side_effect = lambda t: t
    service = _make_service(repo)

    result = await service.create_profile(
        name="Me",
        calorie_target=2000,
        is_default=True,
        targets={"protein_g": {"target": 150, "tolerance": 15}},
    )
    repo.clear_default.assert_awaited_once()
    assert result.is_default is True


async def test_create_profile_with_targets():
    repo = AsyncMock()
    created = MockProfile()
    repo.create.return_value = created
    repo.get_by_id.return_value = created
    repo.add_target.side_effect = lambda t: t
    service = _make_service(repo)

    await service.create_profile(
        name="Me",
        targets={
            "protein_g": {"target": 150, "tolerance": 15},
            "fat_g": {"target": 70},
        },
    )
    assert repo.add_target.await_count == 2


async def test_create_profile_ignores_invalid_nutrient():
    repo = AsyncMock()
    created = MockProfile()
    repo.create.return_value = created
    repo.get_by_id.return_value = created
    repo.add_target.side_effect = lambda t: t
    service = _make_service(repo)

    await service.create_profile(
        name="Me",
        targets={"invalid_nutrient": {"target": 50}},
    )
    repo.add_target.assert_not_awaited()


async def test_update_profile_not_found():
    repo = AsyncMock()
    repo.get_by_id.return_value = None
    service = _make_service(repo)
    result = await service.update_profile("missing", name="New")
    assert result is None


async def test_update_profile_replaces_targets():
    repo = AsyncMock()
    profile = MockProfile()
    repo.get_by_id.return_value = profile
    repo.update.return_value = profile
    repo.add_target.side_effect = lambda t: t
    service = _make_service(repo)

    await service.update_profile(
        "profile-1",
        targets={"protein_g": {"target": 160, "tolerance": 16}},
    )
    repo.remove_targets.assert_awaited_once_with("profile-1")
    repo.add_target.assert_awaited_once()


# --- Comparison Logic ---


def test_compute_status_within_range():
    assert _compute_status(150, 150, 15) == "within_range"
    assert _compute_status(135, 150, 15) == "within_range"
    assert _compute_status(165, 150, 15) == "within_range"


def test_compute_status_approaching():
    # Just outside tolerance but within 10% of target
    assert _compute_status(130, 150, 15) == "approaching"
    assert _compute_status(170, 150, 15) == "approaching"


def test_compute_status_exceeding():
    assert _compute_status(200, 150, 15) == "exceeding"
    assert _compute_status(50, 150, 15) == "exceeding"


def test_compare_nutrition_within_range():
    service = _make_service(AsyncMock())
    profile = MockProfile(
        calorie_target=2000,
        calorie_tolerance=100,
        targets=[MockProfileTarget(target_value=150, tolerance_value=15)],
    )
    nutrition = {"calories": 500, "protein_g": 38}
    result = service.compare_nutrition(profile, nutrition, portion_size=1.0)

    assert result["profile_name"] == "Test"
    assert "calories" in result["details"]
    assert "protein_g" in result["details"]


def test_compare_nutrition_with_gaps():
    service = _make_service(AsyncMock())
    profile = MockProfile(
        calorie_target=2000,
        calorie_tolerance=100,
        targets=[MockProfileTarget(target_value=150, tolerance_value=15)],
    )
    nutrition = {"calories": 100, "protein_g": 5}
    result = service.compare_nutrition(profile, nutrition, portion_size=1.0)

    assert len(result["gaps"]) > 0
    gap_nutrients = {g["nutrient"] for g in result["gaps"]}
    assert "calories" in gap_nutrients
    assert "protein_g" in gap_nutrients


def test_compare_nutrition_no_targets():
    service = _make_service(AsyncMock())
    profile = MockProfile(calorie_target=None, targets=[])
    nutrition = {"calories": 500}
    result = service.compare_nutrition(profile, nutrition)

    assert result["fit"] == "no_targets"


def test_compare_nutrition_portion_scaling():
    service = _make_service(AsyncMock())
    profile = MockProfile(
        calorie_target=2000,
        calorie_tolerance=100,
        targets=[],
    )
    nutrition = {"calories": 500}

    result_1 = service.compare_nutrition(profile, nutrition, portion_size=1.0)
    result_2 = service.compare_nutrition(profile, nutrition, portion_size=2.0)

    assert result_1["details"]["calories"]["actual"] == 500
    assert result_2["details"]["calories"]["actual"] == 1000
