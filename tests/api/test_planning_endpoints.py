"""HTTP-level integration tests for planning API endpoints."""

from __future__ import annotations

import uuid
from datetime import date, timedelta

from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_recipe(client: AsyncClient, title: str = "Test Recipe") -> dict:
    """Create a recipe and return its JSON response."""
    resp = await client.post(
        "/api/v1/recipes",
        json={"title": title, "base_servings": 4},
    )
    assert resp.status_code == 201
    return resp.json()


def _monday() -> str:
    """Return this week's Monday as YYYY-MM-DD."""
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    return monday.isoformat()


# ---------------------------------------------------------------------------
# Weekly Plan
# ---------------------------------------------------------------------------


async def test_get_empty_week_plan(client: AsyncClient):
    """GET week plan returns 7 empty days."""
    resp = await client.get(f"/api/v1/plan/{_monday()}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["week_start"] == _monday()
    assert len(data["days"]) == 7


async def test_get_week_plan_invalid_date(client: AsyncClient):
    """GET week plan with bad date returns 400."""
    resp = await client.get("/api/v1/plan/not-a-date")
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Add / Remove Meals
# ---------------------------------------------------------------------------


async def test_add_meal_to_plan(client: AsyncClient):
    """POST adds a meal to a specific date."""
    recipe = await _create_recipe(client)
    today = date.today().isoformat()

    resp = await client.post(
        f"/api/v1/plan/{today}/meals",
        json={
            "meal_slot": "dinner",
            "recipe_id": recipe["id"],
            "servings": 2,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["recipe_id"] == recipe["id"]
    assert data["meal_slot"] == "dinner"
    assert data["servings"] == 2.0


async def test_add_meal_invalid_slot(client: AsyncClient):
    """POST with invalid meal slot returns 422."""
    recipe = await _create_recipe(client)
    today = date.today().isoformat()

    resp = await client.post(
        f"/api/v1/plan/{today}/meals",
        json={
            "meal_slot": "brunch",
            "recipe_id": recipe["id"],
        },
    )
    assert resp.status_code == 422


async def test_add_meal_nonexistent_recipe(client: AsyncClient):
    """POST with nonexistent recipe returns 404."""
    today = date.today().isoformat()

    resp = await client.post(
        f"/api/v1/plan/{today}/meals",
        json={
            "meal_slot": "lunch",
            "recipe_id": str(uuid.uuid4()),
        },
    )
    assert resp.status_code == 404


async def test_remove_meal_from_plan(client: AsyncClient):
    """DELETE removes a meal from the plan."""
    recipe = await _create_recipe(client)
    today = date.today().isoformat()

    add_resp = await client.post(
        f"/api/v1/plan/{today}/meals",
        json={"meal_slot": "lunch", "recipe_id": recipe["id"]},
    )
    entry_id = add_resp.json()["id"]

    resp = await client.delete(f"/api/v1/plan/{today}/meals/{entry_id}")
    assert resp.status_code == 204


async def test_remove_nonexistent_meal(client: AsyncClient):
    """DELETE nonexistent meal returns 404."""
    today = date.today().isoformat()
    resp = await client.delete(f"/api/v1/plan/{today}/meals/{uuid.uuid4()}")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Rescheduling
# ---------------------------------------------------------------------------


async def test_reschedule_meal(client: AsyncClient):
    """POST reschedule changes the date and slot."""
    recipe = await _create_recipe(client)
    today = date.today()
    tomorrow = (today + timedelta(days=1)).isoformat()
    today_str = today.isoformat()

    add_resp = await client.post(
        f"/api/v1/plan/{today_str}/meals",
        json={"meal_slot": "breakfast", "recipe_id": recipe["id"]},
    )
    entry_id = add_resp.json()["id"]

    resp = await client.post(
        f"/api/v1/plan/{today_str}/reschedule",
        json={
            "meal_id": entry_id,
            "new_date": tomorrow,
            "new_slot": "dinner",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["date"] == tomorrow
    assert data["meal_slot"] == "dinner"


async def test_reschedule_nonexistent_meal(client: AsyncClient):
    """POST reschedule nonexistent meal returns 404."""
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    resp = await client.post(
        f"/api/v1/plan/{today}/reschedule",
        json={
            "meal_id": str(uuid.uuid4()),
            "new_date": tomorrow,
        },
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Batch Management
# ---------------------------------------------------------------------------


async def test_create_batch(client: AsyncClient):
    """POST creates a leftover batch."""
    recipe = await _create_recipe(client)

    resp = await client.post(
        "/api/v1/plan/batch",
        json={
            "recipe_id": recipe["id"],
            "prepared_servings": 6,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["initial_servings"] == 6
    assert data["servings_remaining"] == 6
    assert data["recipe_id"] == recipe["id"]


async def test_create_batch_nonexistent_recipe(client: AsyncClient):
    """POST batch with nonexistent recipe returns 404."""
    resp = await client.post(
        "/api/v1/plan/batch",
        json={
            "recipe_id": str(uuid.uuid4()),
            "prepared_servings": 4,
        },
    )
    assert resp.status_code == 404


async def test_consume_batch(client: AsyncClient):
    """POST consume decrements batch servings."""
    recipe = await _create_recipe(client)

    batch_resp = await client.post(
        "/api/v1/plan/batch",
        json={"recipe_id": recipe["id"], "prepared_servings": 4},
    )
    batch_id = batch_resp.json()["batch_id"]

    resp = await client.post(
        f"/api/v1/plan/batch/{batch_id}/consume",
        json={"servings_consumed": 2},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["servings_remaining"] == 2


async def test_consume_batch_insufficient(client: AsyncClient):
    """POST consume with more than remaining returns 404."""
    recipe = await _create_recipe(client)

    batch_resp = await client.post(
        "/api/v1/plan/batch",
        json={"recipe_id": recipe["id"], "prepared_servings": 2},
    )
    batch_id = batch_resp.json()["batch_id"]

    resp = await client.post(
        f"/api/v1/plan/batch/{batch_id}/consume",
        json={"servings_consumed": 5},
    )
    assert resp.status_code == 404


async def test_consume_nonexistent_batch(client: AsyncClient):
    """POST consume nonexistent batch returns 404."""
    resp = await client.post(
        f"/api/v1/plan/batch/{uuid.uuid4()}/consume",
        json={"servings_consumed": 1},
    )
    assert resp.status_code == 404


async def test_list_active_batches(client: AsyncClient):
    """GET active batches lists created batches."""
    recipe = await _create_recipe(client)

    await client.post(
        "/api/v1/plan/batch",
        json={"recipe_id": recipe["id"], "prepared_servings": 3},
    )

    resp = await client.get("/api/v1/plan/batch/active")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


# ---------------------------------------------------------------------------
# Batch from Meal Entry
# ---------------------------------------------------------------------------


async def test_create_batch_from_meal_entry(client: AsyncClient):
    """POST batch on a meal entry creates a batch and links it."""
    recipe = await _create_recipe(client)
    today = date.today().isoformat()

    add_resp = await client.post(
        f"/api/v1/plan/{today}/meals",
        json={"meal_slot": "dinner", "recipe_id": recipe["id"], "servings": 1},
    )
    entry_id = add_resp.json()["id"]

    resp = await client.post(
        f"/api/v1/plan/{today}/meals/{entry_id}/batch",
        json={"prepared_servings": 8},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["initial_servings"] == 8
    assert data["servings_remaining"] == 8


async def test_create_batch_from_nonexistent_entry(client: AsyncClient):
    """POST batch on nonexistent entry returns 404."""
    today = date.today().isoformat()
    resp = await client.post(
        f"/api/v1/plan/{today}/meals/{uuid.uuid4()}/batch",
        json={"prepared_servings": 4},
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Meal from Batch
# ---------------------------------------------------------------------------


async def test_add_meal_from_batch(client: AsyncClient):
    """POST from-batch creates a meal and decrements the batch."""
    recipe = await _create_recipe(client)
    today = date.today().isoformat()

    batch_resp = await client.post(
        "/api/v1/plan/batch",
        json={"recipe_id": recipe["id"], "prepared_servings": 4},
    )
    batch_id = batch_resp.json()["batch_id"]

    resp = await client.post(
        f"/api/v1/plan/{today}/meals/from-batch",
        json={
            "batch_id": batch_id,
            "meal_slot": "lunch",
            "servings_consumed": 1,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["batch_id"] == batch_id
    assert data["recipe_id"] == recipe["id"]


async def test_add_meal_from_nonexistent_batch(client: AsyncClient):
    """POST from-batch with nonexistent batch returns 404."""
    today = date.today().isoformat()
    resp = await client.post(
        f"/api/v1/plan/{today}/meals/from-batch",
        json={
            "batch_id": str(uuid.uuid4()),
            "meal_slot": "dinner",
            "servings_consumed": 1,
        },
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Suggestions
# ---------------------------------------------------------------------------


async def test_get_suggestions(client: AsyncClient):
    """GET suggestions returns recent and leftovers."""
    resp = await client.get("/api/v1/plan/suggestions")
    assert resp.status_code == 200
    data = resp.json()
    assert "recent" in data
    assert "leftovers" in data


# ---------------------------------------------------------------------------
# Weekly Plan with Meals
# ---------------------------------------------------------------------------


async def test_week_plan_includes_added_meal(client: AsyncClient):
    """After adding a meal, the weekly plan includes it."""
    recipe = await _create_recipe(client, title="Weekly Test Recipe")
    monday = _monday()

    await client.post(
        f"/api/v1/plan/{monday}/meals",
        json={"meal_slot": "dinner", "recipe_id": recipe["id"], "servings": 2},
    )

    resp = await client.get(f"/api/v1/plan/{monday}")
    assert resp.status_code == 200
    plan = resp.json()

    # Find Monday's entry
    monday_day = plan["days"][0]
    assert len(monday_day["meals"]) >= 1
    found = any(m["title"] == "Weekly Test Recipe" for m in monday_day["meals"])
    assert found, "Added meal should appear in the weekly plan"
