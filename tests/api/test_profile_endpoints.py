"""HTTP-level integration tests for profile API endpoints."""

from __future__ import annotations

import uuid

from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Profile CRUD
# ---------------------------------------------------------------------------


async def test_create_profile_returns_201(client: AsyncClient):
    """POST /api/v1/profiles returns 201 with id and name."""
    resp = await client.post(
        "/api/v1/profiles",
        json={
            "name": "Me",
            "calorie_target": 2000,
            "targets": {
                "protein_g": {"target": 150, "tolerance": 15},
            },
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["name"] == "Me"
    assert data["calorie_target"] == 2000
    assert "protein_g" in data["targets"]
    assert data["targets"]["protein_g"]["target"] == 150


async def test_create_then_get_profile(client: AsyncClient, sample_profile: dict):
    """POST then GET a profile — verifies persistence."""
    profile_id = sample_profile["id"]
    resp = await client.get(f"/api/v1/profiles/{profile_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test Profile"
    assert data["calorie_target"] == 2000
    assert "protein_g" in data["targets"]


async def test_get_nonexistent_profile_returns_404(client: AsyncClient):
    """GET with random UUID returns 404."""
    resp = await client.get(f"/api/v1/profiles/{uuid.uuid4()}")
    assert resp.status_code == 404


async def test_list_profiles(client: AsyncClient):
    """GET /api/v1/profiles returns profiles."""
    await client.post("/api/v1/profiles", json={"name": "Profile A"})
    await client.post("/api/v1/profiles", json={"name": "Profile B"})

    resp = await client.get("/api/v1/profiles")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 2


async def test_update_profile(client: AsyncClient, sample_profile: dict):
    """PUT updates profile fields and targets."""
    profile_id = sample_profile["id"]

    resp = await client.put(
        f"/api/v1/profiles/{profile_id}",
        json={
            "name": "Updated Profile",
            "calorie_target": 2200,
            "targets": {
                "protein_g": {"target": 160, "tolerance": 16},
                "carbohydrates_g": {"target": 250, "tolerance": 25},
            },
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Updated Profile"
    assert data["calorie_target"] == 2200
    assert "protein_g" in data["targets"]
    assert "carbohydrates_g" in data["targets"]
    # Old target should be gone
    assert "fat_g" not in data["targets"]


async def test_update_nonexistent_profile_returns_404(client: AsyncClient):
    """PUT to nonexistent profile returns 404."""
    resp = await client.put(
        f"/api/v1/profiles/{uuid.uuid4()}",
        json={"name": "Nope"},
    )
    assert resp.status_code == 404


async def test_delete_profile_returns_204(client: AsyncClient):
    """DELETE soft-deletes a profile."""
    create_resp = await client.post(
        "/api/v1/profiles", json={"name": "To Delete"}
    )
    profile_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/v1/profiles/{profile_id}")
    assert resp.status_code == 204

    # Verify hidden
    get_resp = await client.get(f"/api/v1/profiles/{profile_id}")
    assert get_resp.status_code == 404


async def test_delete_nonexistent_profile_returns_404(client: AsyncClient):
    """DELETE nonexistent profile returns 404."""
    resp = await client.delete(f"/api/v1/profiles/{uuid.uuid4()}")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Default Profile
# ---------------------------------------------------------------------------


async def test_create_default_profile(client: AsyncClient):
    """Creating a default profile marks it as default."""
    resp = await client.post(
        "/api/v1/profiles",
        json={"name": "Default", "is_default": True},
    )
    assert resp.status_code == 201
    assert resp.json()["is_default"] is True


async def test_only_one_default_profile(client: AsyncClient):
    """Creating a new default profile unsets the previous one."""
    resp1 = await client.post(
        "/api/v1/profiles",
        json={"name": "First Default", "is_default": True},
    )
    id1 = resp1.json()["id"]

    resp2 = await client.post(
        "/api/v1/profiles",
        json={"name": "Second Default", "is_default": True},
    )
    assert resp2.json()["is_default"] is True

    # First should no longer be default
    check = await client.get(f"/api/v1/profiles/{id1}")
    assert check.json()["is_default"] is False


# ---------------------------------------------------------------------------
# Profile with Targets
# ---------------------------------------------------------------------------


async def test_create_profile_with_multiple_targets(client: AsyncClient):
    """Profile with multiple nutrient targets persists all of them."""
    resp = await client.post(
        "/api/v1/profiles",
        json={
            "name": "Full Targets",
            "calorie_target": 1800,
            "targets": {
                "protein_g": {"target": 120, "tolerance": 12},
                "carbohydrates_g": {"target": 200, "tolerance": 20},
                "fat_g": {"target": 60, "tolerance": 6},
                "added_sugar_g": {"target": 20, "tolerance": 4},
            },
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert len(data["targets"]) == 4
    assert data["targets"]["protein_g"]["target"] == 120
    assert data["targets"]["fat_g"]["tolerance"] == 6


async def test_create_profile_with_default_tolerance(client: AsyncClient):
    """If tolerance is not provided, a default is applied."""
    resp = await client.post(
        "/api/v1/profiles",
        json={
            "name": "No Tolerance",
            "targets": {
                "protein_g": {"target": 150},
            },
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    # Should have a non-zero default tolerance
    assert data["targets"]["protein_g"]["tolerance"] > 0


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


async def test_create_profile_empty_name_returns_422(client: AsyncClient):
    """Empty name should be rejected."""
    resp = await client.post(
        "/api/v1/profiles",
        json={"name": ""},
    )
    assert resp.status_code == 422


async def test_create_profile_invalid_nutrient_key_returns_422(client: AsyncClient):
    """Invalid nutrient key should be rejected."""
    resp = await client.post(
        "/api/v1/profiles",
        json={
            "name": "Bad Key",
            "targets": {"invalid_key": {"target": 50}},
        },
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Profile Comparison
# ---------------------------------------------------------------------------


async def test_compare_profile_to_recipe(client: AsyncClient, sample_profile: dict):
    """Compare a recipe with nutrition data against a profile."""
    # Create food entry with nutrition
    food_resp = await client.post(
        "/api/v1/food", json={"name": "Test Chicken"}
    )
    food_id = food_resp.json()["id"]
    await client.post(
        f"/api/v1/food/{food_id}/nutrition",
        json={
            "serving_size": 100,
            "serving_unit": "g",
            "calories": 165,
            "protein_g": 31,
            "carbohydrates_g": 0,
            "fat_g": 3.6,
            "added_sugar_g": 0,
            "source_type": "user_confirmed",
        },
    )

    # Create recipe linked to food
    recipe_resp = await client.post(
        "/api/v1/recipes",
        json={
            "title": "Compare Test",
            "base_servings": 1,
            "ingredients": [
                {"name": "Test Chicken", "amount": 200, "unit": "g", "food_entry_id": food_id},
            ],
        },
    )
    recipe_id = recipe_resp.json()["id"]

    # Compare
    resp = await client.post(
        f"/api/v1/profiles/{sample_profile['id']}/compare",
        json={"recipe_id": recipe_id, "portion_size": 1.0},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["profile_name"] == "Test Profile"
    assert data["fit"] in ("within_range", "approaching", "exceeding")
    assert "details" in data


async def test_compare_nonexistent_profile_returns_404(client: AsyncClient):
    """Compare with nonexistent profile returns 404."""
    resp = await client.post(
        f"/api/v1/profiles/{uuid.uuid4()}/compare",
        json={"recipe_id": str(uuid.uuid4()), "portion_size": 1.0},
    )
    assert resp.status_code == 404


async def test_compare_nonexistent_recipe_returns_404(client: AsyncClient, sample_profile: dict):
    """Compare with nonexistent recipe returns 404."""
    resp = await client.post(
        f"/api/v1/profiles/{sample_profile['id']}/compare",
        json={"recipe_id": str(uuid.uuid4()), "portion_size": 1.0},
    )
    assert resp.status_code == 404
