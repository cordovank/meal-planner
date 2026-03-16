# API Contracts: Recipe Management

**Context**: REST API endpoints for recipe CRUD, scaling, and search

## Endpoints

### GET /api/v1/recipes
List recipes with filtering and search.

**Query Parameters**:
- `q`: String (full-text search)
- `state`: Enum (draft, incomplete, pending_review, finalized)
- `macro_profile`: Enum (high_protein, low_carb, high_fiber, balanced)
- `meal_type`: Enum (breakfast, lunch, dinner, snack)
- `limit`: Integer (default 20, max 100)
- `offset`: Integer (default 0)

**Response**: 200 OK
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "string",
      "state": "finalized",
      "base_servings": 4,
      "nutrition_per_serving": {
        "calories": 450,
        "protein_g": 25,
        "carbohydrates_g": 45,
        "fat_g": 20,
        "added_sugar_g": 5
      },
      "confidence": "mixed",
      "tags": ["dinner", "high_protein"],
      "created_at": "2026-03-16T10:00:00Z"
    }
  ],
  "total": 42,
  "has_more": true
}
```

### POST /api/v1/recipes
Create a new recipe.

**Request Body**:
```json
{
  "title": "string",
  "description": "string?",
  "state": "draft",
  "base_servings": 4,
  "ingredients": [
    {
      "name": "Chicken Breast",
      "amount": 500,
      "unit": "g",
      "notes": "boneless"
    }
  ],
  "instructions": ["Step 1", "Step 2"],
  "tags": ["dinner"]
}
```

**Response**: 201 Created
```json
{
  "id": "uuid",
  "title": "string",
  "state": "draft",
  "created_at": "2026-03-16T10:00:00Z"
}
```

### GET /api/v1/recipes/{id}
Get recipe details with nutrition.

**Response**: 200 OK
```json
{
  "id": "uuid",
  "title": "Chicken Stir Fry",
  "description": "Quick weeknight dinner",
  "state": "finalized",
  "base_servings": 4,
  "prep_time_minutes": 15,
  "cook_time_minutes": 20,
  "ingredients": [
    {
      "id": "uuid",
      "name": "Chicken Breast",
      "amount": 500,
      "unit": "g",
      "food_entry_id": "uuid",
      "nutrition_contribution": {
        "calories": 825,
        "protein_g": 165
      },
      "confidence": "user_confirmed"
    }
  ],
  "instructions": [
    {"step": 1, "text": "Cut chicken into strips"},
    {"step": 2, "text": "Heat oil in wok"}
  ],
  "nutrition_total": {
    "calories": 1200,
    "protein_g": 80,
    "carbohydrates_g": 100,
    "fat_g": 45,
    "added_sugar_g": 10
  },
  "nutrition_per_serving": {...},
  "characterization": ["high_protein", "balanced"],
  "tags": ["dinner", "quick"],
  "notes": [
    {
      "text": "Too salty last time - reduce soy sauce",
      "created_at": "2026-03-15T18:00:00Z"
    }
  ],
  "created_at": "2026-03-10T10:00:00Z",
  "updated_at": "2026-03-15T18:00:00Z"
}
```

### PUT /api/v1/recipes/{id}
Update recipe.

**Request Body**: Same as POST, plus version fields for duplication.

**Response**: 200 OK (updated recipe)

### DELETE /api/v1/recipes/{id}
Soft delete recipe.

**Response**: 204 No Content

### POST /api/v1/recipes/{id}/scale
Scale recipe to new serving count.

**Request Body**:
```json
{
  "new_servings": 6
}
```

**Response**: 200 OK (scaled recipe with updated amounts)

### POST /api/v1/recipes/{id}/duplicate
Duplicate recipe, optionally as version.

**Request Body**:
```json
{
  "title": "Low-Sodium Chicken Stir Fry",
  "version_label": "low_sodium"
}
```

**Response**: 201 Created (new recipe)

### GET /api/v1/recipes/{id}/nutrition
Get detailed nutrition breakdown.

**Response**: 200 OK
```json
{
  "total": {...},
  "per_serving": {...},
  "by_ingredient": [
    {
      "ingredient_name": "Chicken Breast",
      "amount": 500,
      "unit": "g",
      "nutrition": {...},
      "confidence": "user_confirmed"
    }
  ],
  "confidence_overall": "mixed",
  "missing_data": ["Rice - no nutrition linked"]
}
```