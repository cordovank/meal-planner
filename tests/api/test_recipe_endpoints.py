"""HTTP-level integration tests for recipe API endpoints.

These tests exercise the full stack: HTTP request -> FastAPI routing ->
dependency injection -> service -> repository -> DB -> response.

The test_create_then_get_persists test is the most critical — it would
have caught the session ROLLBACK bug found during manual validation.
"""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Recipe CRUD
# ---------------------------------------------------------------------------


async def test_create_recipe_returns_201(client: AsyncClient):
    """POST /api/v1/recipes returns 201 with id, title, state, created_at."""
    resp = await client.post("/api/v1/recipes", json={"title": "Simple Recipe"})

    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["title"] == "Simple Recipe"
    assert data["state"] == "draft"
    assert "created_at" in data


async def test_create_then_get_persists(client: AsyncClient, sample_recipe: dict):
    """POST a recipe, then GET it — verifies data persists across requests."""
    recipe_id = sample_recipe["id"]

    resp = await client.get(f"/api/v1/recipes/{recipe_id}")

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == recipe_id
    assert data["title"] == "Test Pancakes"
    assert data["base_servings"] == 4


async def test_create_with_ingredients_then_get_has_ingredients(
    client: AsyncClient, sample_recipe: dict
):
    """Ingredients provided at creation appear on the detail view."""
    recipe_id = sample_recipe["id"]

    resp = await client.get(f"/api/v1/recipes/{recipe_id}")
    data = resp.json()

    assert len(data["ingredients"]) == 2
    names = {ing["name"] for ing in data["ingredients"]}
    assert names == {"Flour", "Eggs"}


async def test_create_minimal_recipe(client: AsyncClient):
    """POST with only title uses defaults (state=draft, base_servings=1)."""
    resp = await client.post("/api/v1/recipes", json={"title": "Minimal"})

    assert resp.status_code == 201
    data = resp.json()
    assert data["state"] == "draft"

    # Verify defaults on detail
    detail = await client.get(f"/api/v1/recipes/{data['id']}")
    assert detail.json()["base_servings"] == 1


async def test_get_nonexistent_returns_404(client: AsyncClient):
    """GET with a random UUID returns 404."""
    fake_id = str(uuid.uuid4())
    resp = await client.get(f"/api/v1/recipes/{fake_id}")

    assert resp.status_code == 404


async def test_update_recipe(client: AsyncClient, sample_recipe: dict):
    """PUT updates recipe fields and returns updated data."""
    recipe_id = sample_recipe["id"]

    resp = await client.put(
        f"/api/v1/recipes/{recipe_id}",
        json={"title": "Updated Pancakes", "base_servings": 6},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Updated Pancakes"
    assert data["base_servings"] == 6


async def test_update_nonexistent_returns_404(client: AsyncClient):
    """PUT to a nonexistent recipe returns 404."""
    fake_id = str(uuid.uuid4())
    resp = await client.put(
        f"/api/v1/recipes/{fake_id}",
        json={"title": "Ghost Recipe"},
    )

    assert resp.status_code == 404


async def test_delete_returns_204(client: AsyncClient, sample_recipe: dict):
    """DELETE returns 204 with no body."""
    recipe_id = sample_recipe["id"]
    resp = await client.delete(f"/api/v1/recipes/{recipe_id}")

    assert resp.status_code == 204
    assert resp.content == b""


async def test_delete_then_get_returns_404(client: AsyncClient):
    """After soft-deleting a recipe, GET returns 404."""
    # Create
    create_resp = await client.post(
        "/api/v1/recipes", json={"title": "To Be Deleted"}
    )
    recipe_id = create_resp.json()["id"]

    # Delete
    del_resp = await client.delete(f"/api/v1/recipes/{recipe_id}")
    assert del_resp.status_code == 204

    # Verify gone
    get_resp = await client.get(f"/api/v1/recipes/{recipe_id}")
    assert get_resp.status_code == 404


async def test_delete_nonexistent_returns_404(client: AsyncClient):
    """DELETE on a nonexistent recipe returns 404."""
    fake_id = str(uuid.uuid4())
    resp = await client.delete(f"/api/v1/recipes/{fake_id}")

    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# List & Search
# ---------------------------------------------------------------------------


async def test_list_empty(client: AsyncClient):
    """GET /api/v1/recipes on empty DB returns empty list."""
    resp = await client.get("/api/v1/recipes")

    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["has_more"] is False


async def test_list_returns_created(client: AsyncClient):
    """Created recipes appear in the list."""
    await client.post("/api/v1/recipes", json={"title": "Recipe A"})
    await client.post("/api/v1/recipes", json={"title": "Recipe B"})

    resp = await client.get("/api/v1/recipes")
    data = resp.json()

    assert data["total"] >= 2
    titles = {item["title"] for item in data["items"]}
    assert "Recipe A" in titles
    assert "Recipe B" in titles


async def test_list_state_filter(client: AsyncClient):
    """Filtering by state returns only matching recipes."""
    await client.post(
        "/api/v1/recipes", json={"title": "Draft One", "state": "draft"}
    )
    await client.post(
        "/api/v1/recipes", json={"title": "Final One", "state": "finalized"}
    )

    resp = await client.get("/api/v1/recipes", params={"state": "finalized"})
    data = resp.json()

    titles = {item["title"] for item in data["items"]}
    assert "Final One" in titles
    assert "Draft One" not in titles


async def test_list_pagination(client: AsyncClient):
    """Pagination with limit and offset works correctly."""
    for i in range(3):
        await client.post("/api/v1/recipes", json={"title": f"Page Recipe {i}"})

    # First page
    resp1 = await client.get("/api/v1/recipes", params={"limit": 2, "offset": 0})
    data1 = resp1.json()
    assert len(data1["items"]) == 2
    assert data1["has_more"] is True

    # Second page
    resp2 = await client.get("/api/v1/recipes", params={"limit": 2, "offset": 2})
    data2 = resp2.json()
    assert len(data2["items"]) >= 1
    assert data2["has_more"] is False


async def test_search_recipes(client: AsyncClient):
    """Search by query string matches recipe titles."""
    await client.post("/api/v1/recipes", json={"title": "Chocolate Cake"})
    await client.post("/api/v1/recipes", json={"title": "Vanilla Pudding"})

    resp = await client.get("/api/v1/recipes", params={"q": "Chocolate"})
    data = resp.json()

    titles = {item["title"] for item in data["items"]}
    assert "Chocolate Cake" in titles
    assert "Vanilla Pudding" not in titles


# ---------------------------------------------------------------------------
# Scale & Duplicate
# ---------------------------------------------------------------------------


async def test_scale_recipe(client: AsyncClient):
    """Scaling doubles ingredient amounts when servings are doubled."""
    create_resp = await client.post(
        "/api/v1/recipes",
        json={
            "title": "Scale Test",
            "base_servings": 2,
            "ingredients": [
                {"name": "Butter", "amount": 4.0, "unit": "tbsp"},
                {"name": "Sugar", "amount": 1.0, "unit": "cup"},
            ],
        },
    )
    recipe_id = create_resp.json()["id"]

    resp = await client.post(
        f"/api/v1/recipes/{recipe_id}/scale",
        json={"new_servings": 4},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["factor"] == 2.0
    assert data["servings"] == 4

    amounts = {ing["name"]: float(ing["amount"]) for ing in data["ingredients"]}
    assert amounts["Butter"] == 8.0
    assert amounts["Sugar"] == 2.0


async def test_scale_nonexistent_returns_404(client: AsyncClient):
    """Scaling a nonexistent recipe returns 404."""
    fake_id = str(uuid.uuid4())
    resp = await client.post(
        f"/api/v1/recipes/{fake_id}/scale",
        json={"new_servings": 4},
    )

    assert resp.status_code == 404


async def test_duplicate_recipe(client: AsyncClient, sample_recipe: dict):
    """Duplicating a recipe returns 201 with a new ID and parent link."""
    recipe_id = sample_recipe["id"]

    resp = await client.post(
        f"/api/v1/recipes/{recipe_id}/duplicate",
        json={"title": "Pancakes Copy", "version_label": "v2"},
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] != recipe_id
    assert data["title"] == "Pancakes Copy"
    assert data["parent_recipe_id"] == recipe_id
    assert data["version_label"] == "v2"


async def test_duplicate_nonexistent_returns_404(client: AsyncClient):
    """Duplicating a nonexistent recipe returns 404."""
    fake_id = str(uuid.uuid4())
    resp = await client.post(
        f"/api/v1/recipes/{fake_id}/duplicate",
        json={"title": "Ghost Copy"},
    )

    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Ingredient Sub-resource
# ---------------------------------------------------------------------------


async def test_add_ingredient(client: AsyncClient):
    """Adding an ingredient to a recipe returns 201."""
    create_resp = await client.post(
        "/api/v1/recipes", json={"title": "Ingredient Test"}
    )
    recipe_id = create_resp.json()["id"]

    resp = await client.post(
        f"/api/v1/recipes/{recipe_id}/ingredients",
        json={"name": "Salt", "amount": 0.5, "unit": "tsp"},
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Salt"
    assert "id" in data


async def test_add_ingredient_missing_recipe_returns_404(client: AsyncClient):
    """Adding an ingredient to a nonexistent recipe returns 404."""
    fake_id = str(uuid.uuid4())
    resp = await client.post(
        f"/api/v1/recipes/{fake_id}/ingredients",
        json={"name": "Salt", "amount": 1, "unit": "tsp"},
    )

    assert resp.status_code == 404


async def test_update_ingredient(client: AsyncClient):
    """Updating an ingredient reflects the new values."""
    create_resp = await client.post(
        "/api/v1/recipes",
        json={"title": "Update Ing Test", "ingredients": [{"name": "Milk", "amount": 1, "unit": "cup"}]},
    )
    recipe_id = create_resp.json()["id"]

    # Get ingredient ID from detail
    detail = await client.get(f"/api/v1/recipes/{recipe_id}")
    ing_id = detail.json()["ingredients"][0]["id"]

    resp = await client.put(
        f"/api/v1/recipes/ingredients/{ing_id}",
        json={"name": "Oat Milk", "amount": 2, "unit": "cups"},
    )

    assert resp.status_code == 200
    assert resp.json()["name"] == "Oat Milk"


async def test_remove_ingredient(client: AsyncClient):
    """Removing an ingredient returns 204."""
    create_resp = await client.post(
        "/api/v1/recipes",
        json={"title": "Remove Ing Test", "ingredients": [{"name": "Pepper", "amount": 0.25, "unit": "tsp"}]},
    )
    recipe_id = create_resp.json()["id"]

    detail = await client.get(f"/api/v1/recipes/{recipe_id}")
    ing_id = detail.json()["ingredients"][0]["id"]

    resp = await client.delete(f"/api/v1/recipes/ingredients/{ing_id}")
    assert resp.status_code == 204


# ---------------------------------------------------------------------------
# Note Sub-resource
# ---------------------------------------------------------------------------


async def test_add_note(client: AsyncClient, sample_recipe: dict):
    """Adding a note returns 201 with text and created_at."""
    recipe_id = sample_recipe["id"]

    resp = await client.post(
        f"/api/v1/recipes/{recipe_id}/notes",
        json={"text": "Too salty last time"},
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["text"] == "Too salty last time"
    assert "id" in data
    assert "created_at" in data


async def test_remove_note(client: AsyncClient):
    """Removing a note returns 204."""
    create_resp = await client.post(
        "/api/v1/recipes", json={"title": "Note Test"}
    )
    recipe_id = create_resp.json()["id"]

    note_resp = await client.post(
        f"/api/v1/recipes/{recipe_id}/notes",
        json={"text": "A test note"},
    )
    note_id = note_resp.json()["id"]

    resp = await client.delete(f"/api/v1/recipes/notes/{note_id}")
    assert resp.status_code == 204
