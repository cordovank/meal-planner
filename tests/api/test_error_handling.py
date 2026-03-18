"""Tests for error response envelope format (middleware) and input validation."""

from __future__ import annotations

import uuid

from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Error Envelope Format (middleware.py handlers)
# ---------------------------------------------------------------------------


async def test_http_error_envelope(client: AsyncClient):
    """404 errors return the standardized error envelope."""
    fake_id = str(uuid.uuid4())
    resp = await client.get(f"/api/v1/recipes/{fake_id}")

    assert resp.status_code == 404
    data = resp.json()
    assert data == {
        "error": {
            "type": "http",
            "message": "Recipe not found",
        }
    }


async def test_validation_error_envelope_missing_field(client: AsyncClient):
    """POST with missing required field returns validation error envelope."""
    resp = await client.post("/api/v1/recipes", json={})

    assert resp.status_code == 422
    data = resp.json()
    assert data["error"]["type"] == "validation"
    assert data["error"]["message"] == "Request validation failed"
    assert isinstance(data["error"]["details"], list)
    assert len(data["error"]["details"]) > 0


async def test_validation_error_wrong_types(client: AsyncClient):
    """POST with wrong field types returns 422 with details."""
    resp = await client.post(
        "/api/v1/recipes",
        json={"title": "Valid", "base_servings": "not_a_number"},
    )

    assert resp.status_code == 422
    data = resp.json()
    assert data["error"]["type"] == "validation"


async def test_scale_rejects_zero_servings(client: AsyncClient, sample_recipe: dict):
    """Scaling with new_servings=0 is rejected by the gt=0 constraint."""
    recipe_id = sample_recipe["id"]

    resp = await client.post(
        f"/api/v1/recipes/{recipe_id}/scale",
        json={"new_servings": 0},
    )

    assert resp.status_code == 422
    data = resp.json()
    assert data["error"]["type"] == "validation"


async def test_scale_rejects_negative_servings(client: AsyncClient, sample_recipe: dict):
    """Scaling with negative new_servings is rejected."""
    recipe_id = sample_recipe["id"]

    resp = await client.post(
        f"/api/v1/recipes/{recipe_id}/scale",
        json={"new_servings": -1},
    )

    assert resp.status_code == 422
    data = resp.json()
    assert data["error"]["type"] == "validation"
