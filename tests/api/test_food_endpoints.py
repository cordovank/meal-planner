"""HTTP-level integration tests for food entry and nutrition record API endpoints."""

from __future__ import annotations

import uuid

from httpx import AsyncClient


# ---------------------------------------------------------------------------
# FoodEntry CRUD
# ---------------------------------------------------------------------------


async def test_create_food_entry_returns_201(client: AsyncClient):
    """POST /api/v1/food returns 201 with id and name."""
    resp = await client.post(
        "/api/v1/food",
        json={"name": "Olive Oil", "category": "fat", "is_custom": True},
    )

    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["name"] == "Olive Oil"
    assert data["is_custom"] is True


async def test_create_then_get_food_entry(client: AsyncClient, sample_food_entry: dict):
    """POST then GET a food entry — verifies persistence."""
    entry_id = sample_food_entry["id"]

    resp = await client.get(f"/api/v1/food/{entry_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Chicken Breast"
    assert data["category"] == "protein"


async def test_get_food_entry_includes_nutrition(client: AsyncClient, sample_food_entry: dict):
    """GET food entry includes its nutrition records."""
    entry_id = sample_food_entry["id"]

    resp = await client.get(f"/api/v1/food/{entry_id}")
    data = resp.json()

    assert len(data["nutrition_records"]) == 1
    nutr = data["nutrition_records"][0]
    assert float(nutr["calories"]) == 165
    assert float(nutr["protein_g"]) == 31
    assert nutr["source_type"] == "user_confirmed"


async def test_get_nonexistent_food_entry_returns_404(client: AsyncClient):
    """GET with random UUID returns 404."""
    resp = await client.get(f"/api/v1/food/{uuid.uuid4()}")
    assert resp.status_code == 404


async def test_update_food_entry(client: AsyncClient, sample_food_entry: dict):
    """PUT updates food entry fields."""
    entry_id = sample_food_entry["id"]

    resp = await client.put(
        f"/api/v1/food/{entry_id}",
        json={"name": "Grilled Chicken Breast", "brand": "Organic Farm"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Grilled Chicken Breast"
    assert data["brand"] == "Organic Farm"


async def test_delete_food_entry_returns_204(client: AsyncClient):
    """DELETE soft-deletes a food entry."""
    create_resp = await client.post(
        "/api/v1/food", json={"name": "To Delete"}
    )
    entry_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/v1/food/{entry_id}")
    assert resp.status_code == 204

    # Verify hidden
    get_resp = await client.get(f"/api/v1/food/{entry_id}")
    assert get_resp.status_code == 404


async def test_list_food_entries(client: AsyncClient):
    """GET /api/v1/food returns food entries."""
    await client.post("/api/v1/food", json={"name": "Apple"})
    await client.post("/api/v1/food", json={"name": "Banana"})

    resp = await client.get("/api/v1/food")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 2


async def test_search_food_entries(client: AsyncClient):
    """Search with ?q= filters food entries by name."""
    await client.post("/api/v1/food", json={"name": "Quinoa Grain"})
    await client.post("/api/v1/food", json={"name": "Rice White"})

    resp = await client.get("/api/v1/food", params={"q": "Quinoa"})
    data = resp.json()
    names = {item["name"] for item in data["items"]}
    assert "Quinoa Grain" in names


# ---------------------------------------------------------------------------
# NutritionRecord CRUD
# ---------------------------------------------------------------------------


async def test_add_nutrition_record_returns_201(client: AsyncClient):
    """POST nutrition record to a food entry."""
    entry_resp = await client.post(
        "/api/v1/food", json={"name": "Brown Rice"}
    )
    entry_id = entry_resp.json()["id"]

    resp = await client.post(
        f"/api/v1/food/{entry_id}/nutrition",
        json={
            "serving_size": 100,
            "serving_unit": "g",
            "calories": 112,
            "protein_g": 2.3,
            "carbohydrates_g": 24,
            "fat_g": 0.8,
            "added_sugar_g": 0,
            "source_type": "label",
            "fiber_g": 1.8,
        },
    )

    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert float(data["calories"]) == 112


async def test_add_nutrition_to_nonexistent_food_returns_404(client: AsyncClient):
    """Adding nutrition to nonexistent food entry returns 404."""
    resp = await client.post(
        f"/api/v1/food/{uuid.uuid4()}/nutrition",
        json={
            "serving_size": 100,
            "serving_unit": "g",
            "calories": 100,
            "protein_g": 10,
            "carbohydrates_g": 10,
            "fat_g": 5,
            "added_sugar_g": 0,
            "source_type": "estimated",
        },
    )
    assert resp.status_code == 404


async def test_update_nutrition_record(client: AsyncClient, sample_food_entry: dict):
    """PUT updates a nutrition record's fields."""
    entry_id = sample_food_entry["id"]

    # Get the nutrition record ID
    detail = await client.get(f"/api/v1/food/{entry_id}")
    record_id = detail.json()["nutrition_records"][0]["id"]

    resp = await client.put(
        f"/api/v1/food/nutrition/{record_id}",
        json={"calories": 170, "protein_g": 32},
    )

    assert resp.status_code == 200
    assert float(resp.json()["calories"]) == 170


async def test_remove_nutrition_record(client: AsyncClient):
    """DELETE removes a nutrition record."""
    entry_resp = await client.post("/api/v1/food", json={"name": "Temp Food"})
    entry_id = entry_resp.json()["id"]

    nutr_resp = await client.post(
        f"/api/v1/food/{entry_id}/nutrition",
        json={
            "serving_size": 1,
            "serving_unit": "piece",
            "calories": 50,
            "protein_g": 1,
            "carbohydrates_g": 10,
            "fat_g": 1,
            "added_sugar_g": 5,
            "source_type": "estimated",
        },
    )
    record_id = nutr_resp.json()["id"]

    resp = await client.delete(f"/api/v1/food/nutrition/{record_id}")
    assert resp.status_code == 204


# ---------------------------------------------------------------------------
# Recipe Nutrition Endpoint
# ---------------------------------------------------------------------------


async def test_recipe_nutrition_all_linked(client: AsyncClient):
    """Full nutrition breakdown when all ingredients are linked to food entries."""
    # Create food entry with nutrition
    food_resp = await client.post(
        "/api/v1/food", json={"name": "Test Flour"}
    )
    food_id = food_resp.json()["id"]
    await client.post(
        f"/api/v1/food/{food_id}/nutrition",
        json={
            "serving_size": 100,
            "serving_unit": "g",
            "calories": 364,
            "protein_g": 10,
            "carbohydrates_g": 76,
            "fat_g": 1,
            "added_sugar_g": 0,
            "source_type": "label",
        },
    )

    # Create recipe with ingredient linked to food entry
    recipe_resp = await client.post(
        "/api/v1/recipes",
        json={
            "title": "Nutrition Test Recipe",
            "base_servings": 2,
            "ingredients": [
                {"name": "Test Flour", "amount": 200, "unit": "g", "food_entry_id": food_id},
            ],
        },
    )
    recipe_id = recipe_resp.json()["id"]

    # Get nutrition
    resp = await client.get(f"/api/v1/recipes/{recipe_id}/nutrition")
    assert resp.status_code == 200
    data = resp.json()

    # Total should be scaled: 200g / 100g serving = 2x
    assert float(data["total"]["calories"]) == 728  # 364 * 2
    assert float(data["total"]["protein_g"]) == 20  # 10 * 2

    # Per serving (2 servings)
    assert float(data["per_serving"]["calories"]) == 364
    assert float(data["per_serving"]["protein_g"]) == 10

    # Confidence
    assert data["confidence_overall"] == "complete"
    assert data["missing_data"] == []


async def test_recipe_nutrition_with_missing_data(client: AsyncClient):
    """Nutrition shows missing_data for unlinked ingredients."""
    recipe_resp = await client.post(
        "/api/v1/recipes",
        json={
            "title": "Incomplete Nutrition Recipe",
            "base_servings": 1,
            "ingredients": [
                {"name": "Mystery Spice", "amount": 1, "unit": "tsp"},
            ],
        },
    )
    recipe_id = recipe_resp.json()["id"]

    resp = await client.get(f"/api/v1/recipes/{recipe_id}/nutrition")
    assert resp.status_code == 200
    data = resp.json()

    assert len(data["missing_data"]) == 1
    assert "Mystery Spice" in data["missing_data"][0]
    assert data["confidence_overall"] == "incomplete"


async def test_recipe_nutrition_nonexistent_returns_404(client: AsyncClient):
    """Nutrition for nonexistent recipe returns 404."""
    resp = await client.get(f"/api/v1/recipes/{uuid.uuid4()}/nutrition")
    assert resp.status_code == 404


async def test_recipe_nutrition_characterization(client: AsyncClient):
    """Characterization labels are included in nutrition response."""
    # Create high-protein food
    food_resp = await client.post(
        "/api/v1/food", json={"name": "Whey Protein"}
    )
    food_id = food_resp.json()["id"]
    await client.post(
        f"/api/v1/food/{food_id}/nutrition",
        json={
            "serving_size": 30,
            "serving_unit": "g",
            "calories": 120,
            "protein_g": 25,
            "carbohydrates_g": 3,
            "fat_g": 1,
            "added_sugar_g": 0,
            "source_type": "label",
        },
    )

    recipe_resp = await client.post(
        "/api/v1/recipes",
        json={
            "title": "Protein Shake",
            "base_servings": 1,
            "ingredients": [
                {"name": "Whey Protein", "amount": 30, "unit": "g", "food_entry_id": food_id},
            ],
        },
    )
    recipe_id = recipe_resp.json()["id"]

    resp = await client.get(f"/api/v1/recipes/{recipe_id}/nutrition")
    data = resp.json()

    assert "Protein-rich" in data["characterization"]
