# Validation & Commands Reference

**Date**: 2026-03-18
**Status**: ✅ Phase 1–4 Validated

---

## Quick Reference

### Run All Tests
```bash
uv run pytest tests/ -v
```

### Run Application (Development)
```bash
uv run uvicorn meal_planner.main:app --reload
```

### Database Migrations

#### Check Current State
```bash
uv run alembic -c alembic.ini current
```

#### Apply Latest Migration
```bash
uv run alembic -c alembic.ini upgrade head
```

#### Create New Migration (after model changes)
```bash
uv run alembic -c alembic.ini revision --autogenerate -m "Description of changes"
```

#### Downgrade (revert last migration)
```bash
uv run alembic -c alembic.ini downgrade -1
```

#### View Migration History
```bash
uv run alembic -c alembic.ini history
```

---

## Phase 1–3 Validation Log

### Phase 3: Recipe Management (User Story 1)

#### Automated Validation Commands

**Python Compilation Check**:
```bash
uv run python -m py_compile src/meal_planner/repository/sqlalchemy/models/recipe.py src/meal_planner/repository/sqlalchemy/repositories/recipe_repository.py src/meal_planner/services/recipe_service.py src/meal_planner/api/schemas/recipe.py src/meal_planner/api/v1/recipes.py
```
*Result*: ✅ All files compile successfully

**FastAPI App Initialization**:
```bash
uv run python -c "from meal_planner.main import app; print('✓ FastAPI app initialized successfully'); print('Available routes:', len([route.path for route in app.routes]))"
```
*Result*: ✅ App starts with 17 routes

**Database Schema Validation**:
```bash
sqlite3 src/meal_planner.db ".schema recipe"
```
*Result*: ✅ Recipe tables created with correct schema

**Migration Status**:
```bash
sqlite3 src/meal_planner.db "SELECT * FROM alembic_version;"
```
*Result*: ✅ Migration 0002 applied successfully

**Full Test Suite**:
```bash
uv run pytest tests/ --tb=short
```
*Result*: ✅ All 141 tests pass in ~0.8s

**Coverage Report**:
```bash
uv run pytest tests/ --cov=meal_planner --cov-report=term-missing
```
*Result*: ✅ 83% overall coverage

---

## API Testing Reference

Start the dev server first:
```bash
uv run uvicorn meal_planner.main:app --reload
```

Base URL: `http://localhost:8000`

### Recipe CRUD

#### Create a Recipe (POST /api/v1/recipes)

**Minimal (title only)**:
```bash
curl -X POST http://localhost:8000/api/v1/recipes \
  -H "Content-Type: application/json" \
  -d '{"title": "Quick Oatmeal"}'
```
Expected: `201 Created`
```json
{"id": "<uuid>", "title": "Quick Oatmeal", "state": "draft", "created_at": "..."}
```

**With ingredients**:
```bash
curl -X POST http://localhost:8000/api/v1/recipes \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Pancakes",
    "description": "Fluffy weekend pancakes",
    "base_servings": 4,
    "ingredients": [
      {"name": "Flour", "amount": 2.0, "unit": "cups"},
      {"name": "Eggs", "amount": 3, "unit": "pieces"},
      {"name": "Milk", "amount": 1.5, "unit": "cups"},
      {"name": "Salt", "to_taste": true}
    ]
  }'
```
Expected: `201 Created`
```json
{"id": "<uuid>", "title": "Pancakes", "state": "draft", "created_at": "..."}
```

**With all fields**:
```bash
curl -X POST http://localhost:8000/api/v1/recipes \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Chicken Stir Fry",
    "description": "Quick weeknight dinner",
    "state": "finalized",
    "base_servings": 4,
    "prep_time_minutes": 15,
    "cook_time_minutes": 20,
    "ingredients": [
      {"name": "Chicken Breast", "amount": 500, "unit": "g", "notes": "boneless, skinless"},
      {"name": "Soy Sauce", "amount": 3, "unit": "tbsp"},
      {"name": "Garlic", "amount": 4, "unit": "cloves", "optional": true}
    ]
  }'
```
Expected: `201 Created`

#### Get a Recipe (GET /api/v1/recipes/{id})

```bash
curl http://localhost:8000/api/v1/recipes/{recipe_id}
```
Expected: `200 OK`
```json
{
  "id": "<uuid>",
  "title": "Pancakes",
  "description": "Fluffy weekend pancakes",
  "state": "draft",
  "base_servings": 4,
  "prep_time_minutes": null,
  "cook_time_minutes": null,
  "ingredients": [
    {"id": "<uuid>", "name": "Flour", "amount": "2.000", "unit": "cups", "to_taste": false, "optional": false, "notes": null, "sort_order": 0},
    {"id": "<uuid>", "name": "Eggs", "amount": "3.000", "unit": "pieces", "to_taste": false, "optional": false, "notes": null, "sort_order": 1}
  ],
  "notes": [],
  "created_at": "...",
  "updated_at": "...",
  "deleted_at": null
}
```

**Not found**:
```bash
curl http://localhost:8000/api/v1/recipes/00000000-0000-0000-0000-000000000000
```
Expected: `404 Not Found`
```json
{"error": {"type": "http", "message": "Recipe not found"}}
```

#### List Recipes (GET /api/v1/recipes)

**List all**:
```bash
curl http://localhost:8000/api/v1/recipes
```
Expected: `200 OK`
```json
{"items": [...], "total": 5, "has_more": false}
```

**Filter by state**:
```bash
curl "http://localhost:8000/api/v1/recipes?state=draft"
```

**Paginate**:
```bash
curl "http://localhost:8000/api/v1/recipes?limit=2&offset=0"
```

**Search by title/description**:
```bash
curl "http://localhost:8000/api/v1/recipes?q=pancake"
```

#### Update a Recipe (PUT /api/v1/recipes/{id})

All fields are optional (partial update):
```bash
curl -X PUT http://localhost:8000/api/v1/recipes/{recipe_id} \
  -H "Content-Type: application/json" \
  -d '{"title": "Buttermilk Pancakes", "base_servings": 6}'
```
Expected: `200 OK` — returns full updated recipe detail

#### Delete a Recipe (DELETE /api/v1/recipes/{id})

Soft delete (sets `deleted_at`, hides from queries):
```bash
curl -X DELETE http://localhost:8000/api/v1/recipes/{recipe_id}
```
Expected: `204 No Content` (empty body)

After deletion, GET returns 404:
```bash
curl http://localhost:8000/api/v1/recipes/{recipe_id}
# → 404 Not Found
```

---

### Recipe Scaling

#### Scale a Recipe (POST /api/v1/recipes/{id}/scale)

```bash
curl -X POST http://localhost:8000/api/v1/recipes/{recipe_id}/scale \
  -H "Content-Type: application/json" \
  -d '{"new_servings": 8}'
```
Expected: `200 OK`
```json
{
  "factor": 2.0,
  "servings": 8,
  "ingredients": [
    {"id": "<uuid>", "name": "Flour", "amount": "4.000", "unit": "cups", "to_taste": false, "optional": false},
    {"id": "<uuid>", "name": "Eggs", "amount": "6.000", "unit": "pieces", "to_taste": false, "optional": false}
  ]
}
```

**Validation error** (new_servings must be > 0):
```bash
curl -X POST http://localhost:8000/api/v1/recipes/{recipe_id}/scale \
  -H "Content-Type: application/json" \
  -d '{"new_servings": 0}'
```
Expected: `422 Unprocessable Entity`
```json
{"error": {"type": "validation", "message": "Request validation failed", "details": [...]}}
```

---

### Recipe Duplication

#### Duplicate a Recipe (POST /api/v1/recipes/{id}/duplicate)

```bash
curl -X POST http://localhost:8000/api/v1/recipes/{recipe_id}/duplicate \
  -H "Content-Type: application/json" \
  -d '{"title": "Whole Wheat Pancakes", "version_label": "healthier"}'
```
Expected: `201 Created`
```json
{
  "id": "<new-uuid>",
  "title": "Whole Wheat Pancakes",
  "state": "draft",
  "parent_recipe_id": "<original-uuid>",
  "version_label": "healthier",
  "created_at": "..."
}
```

---

### Ingredient Management

#### Add an Ingredient (POST /api/v1/recipes/{id}/ingredients)

```bash
curl -X POST http://localhost:8000/api/v1/recipes/{recipe_id}/ingredients \
  -H "Content-Type: application/json" \
  -d '{"name": "Vanilla Extract", "amount": 1.0, "unit": "tsp"}'
```
Expected: `201 Created`
```json
{"id": "<uuid>", "name": "Vanilla Extract", "amount": "1.000", "unit": "tsp"}
```

#### Update an Ingredient (PUT /api/v1/recipes/ingredients/{ingredient_id})

```bash
curl -X PUT http://localhost:8000/api/v1/recipes/ingredients/{ingredient_id} \
  -H "Content-Type: application/json" \
  -d '{"name": "Pure Vanilla Extract", "amount": 2.0, "unit": "tsp"}'
```
Expected: `200 OK`
```json
{"id": "<uuid>", "name": "Pure Vanilla Extract", "amount": "2.000", "unit": "tsp"}
```

#### Remove an Ingredient (DELETE /api/v1/recipes/ingredients/{ingredient_id})

```bash
curl -X DELETE http://localhost:8000/api/v1/recipes/ingredients/{ingredient_id}
```
Expected: `204 No Content`

---

### Note Management

#### Add a Note (POST /api/v1/recipes/{id}/notes)

```bash
curl -X POST http://localhost:8000/api/v1/recipes/{recipe_id}/notes \
  -H "Content-Type: application/json" \
  -d '{"text": "Too salty last time - reduce salt by half"}'
```
Expected: `201 Created`
```json
{"id": "<uuid>", "text": "Too salty last time - reduce salt by half", "created_at": "..."}
```

#### Remove a Note (DELETE /api/v1/recipes/notes/{note_id})

```bash
curl -X DELETE http://localhost:8000/api/v1/recipes/notes/{note_id}
```
Expected: `204 No Content`

---

### Food Library (Phase 4)

#### Create a Food Entry (POST /api/v1/food)

```bash
curl -X POST http://localhost:8000/api/v1/food \
  -H "Content-Type: application/json" \
  -d '{"name": "Chicken Breast", "category": "protein", "is_custom": true}'
```
Expected: `201 Created`
```json
{"id": "<uuid>", "name": "Chicken Breast", "source_type": "user_created", "is_custom": true, "created_at": "..."}
```

#### Add Nutrition to a Food Entry (POST /api/v1/food/{id}/nutrition)

```bash
curl -X POST http://localhost:8000/api/v1/food/{food_id}/nutrition \
  -H "Content-Type: application/json" \
  -d '{
    "serving_size": 100,
    "serving_unit": "g",
    "calories": 165,
    "protein_g": 31,
    "carbohydrates_g": 0,
    "fat_g": 3.6,
    "added_sugar_g": 0,
    "source_type": "user_confirmed",
    "fiber_g": 0,
    "sodium_mg": 74
  }'
```
Expected: `201 Created`

#### Get Food Entry with Nutrition (GET /api/v1/food/{id})

```bash
curl http://localhost:8000/api/v1/food/{food_id}
```
Expected: `200 OK` — includes `nutrition_records` array

#### List/Search Food Entries (GET /api/v1/food)

```bash
curl "http://localhost:8000/api/v1/food?q=chicken"
```

---

### Recipe Nutrition (Phase 4)

#### Get Recipe Nutrition Breakdown (GET /api/v1/recipes/{id}/nutrition)

Requires ingredients to be linked to food entries via `food_entry_id`.

**Create a recipe with linked ingredient:**
```bash
curl -X POST http://localhost:8000/api/v1/recipes \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Grilled Chicken",
    "base_servings": 2,
    "ingredients": [
      {"name": "Chicken Breast", "amount": 200, "unit": "g", "food_entry_id": "<food_entry_uuid>"}
    ]
  }'
```

**Get nutrition breakdown:**
```bash
curl http://localhost:8000/api/v1/recipes/{recipe_id}/nutrition
```
Expected: `200 OK`
```json
{
  "total": {"calories": 330, "protein_g": 62, "carbohydrates_g": 0, "fat_g": 7.2, "added_sugar_g": 0, ...},
  "per_serving": {"calories": 165, "protein_g": 31, ...},
  "by_ingredient": [
    {"ingredient_name": "Chicken Breast", "amount": 200, "unit": "g", "nutrition": {...}, "confidence": "low"}
  ],
  "confidence_overall": "complete",
  "characterization": ["Protein-rich"],
  "missing_data": []
}
```

**Unlinked ingredients show in missing_data:**
```json
{
  "missing_data": ["Olive Oil - no nutrition linked"],
  "confidence_overall": "incomplete"
}
```

---

### Error Response Format

All errors use a consistent envelope:

**HTTP errors (404, etc.)**:
```json
{"error": {"type": "http", "message": "Recipe not found"}}
```

**Validation errors (422)**:
```json
{
  "error": {
    "type": "validation",
    "message": "Request validation failed",
    "details": [
      {"type": "missing", "loc": ["body", "title"], "msg": "Field required", "input": {}}
    ]
  }
}
```

---

## Phase 1–2 Validation Log

### ✅ Initial Alembic Setup (T001)

**Command**:
```bash
uv run alembic -c alembic.ini upgrade head
```

**Result**: ✅ SUCCESS

**Verification**:
- ✅ Migration file created: `src/meal_planner/repository/migrations/versions/0001_initial.py`
- ✅ `alembic.ini` properly configured
- ✅ `env.py` updated to use `Base.metadata` from models and sync driver for migrations
- ✅ SQLite database created at `src/meal_planner.db`

---

### ✅ Pydantic Schemas (T002)

**Module**: `src/meal_planner/api/schemas/common.py`

**Validation**:
```bash
uv run python -c "from meal_planner.api.schemas.common import BaseSchema, UUIDSchema, TimestampedSchema; print('Schemas OK')"
```

**Result**: ✅ Schemas imported successfully

---

### ✅ Error Handling Middleware (T003)

**Module**: `src/meal_planner/api/middleware.py`

**Validation**:
```bash
uv run python -c "from meal_planner.api.middleware import register_api_middleware, http_exception_handler; print('Middleware OK')"
```

**Result**: ✅ Middleware handlers ready for FastAPI attachment

---

### ✅ Template Structure (T004)

**Paths Created**:
- ✅ `src/meal_planner/web/templates/base.html`
- ✅ `src/meal_planner/web/templates/recipes/`

**Result**: ✅ Jinja2 template directories ready

---

### ✅ Static Files (T005)

**Paths Created**:
- ✅ `src/meal_planner/web/static/css/main.css`
- ✅ `src/meal_planner/web/static/js/main.js`

**Result**: ✅ Static file serving ready

---

### ✅ Base Entity Models (T006)

**Module**: `src/meal_planner/repository/sqlalchemy/models/base.py`

**Result**: ✅ Base class with UUID PKs and audit fields (created_at, updated_at, deleted_at)

---

### ✅ Repository Protocols (T007)

**Module**: `src/meal_planner/services/interfaces.py`

**Result**: ✅ Protocols defined and importable

---

### ✅ SQLAlchemy Session Management (T008)

**Module**: `src/meal_planner/repository/sqlalchemy/session.py`

**Test Command**:
```bash
uv run pytest tests/unit/repository/test_session.py -v
```

**Result**: ✅ 6/6 tests passing

---

### ✅ Unit Conversion Utilities (T009)

**Test Command**:
```bash
uv run pytest tests/unit/services/test_unit_conversion.py -v
```

**Result**: ✅ 14/14 tests passing

---

### ✅ Fuzzy Search (T010)

**Test Command**:
```bash
uv run pytest tests/unit/services/test_fuzzy_search.py -v
```

**Result**: ✅ 10/10 tests passing

---

### ✅ Nutrition Calculator (T011)

**Test Command**:
```bash
uv run pytest tests/unit/services/test_nutrition_calculator.py -v
```

**Result**: ✅ 15/15 tests passing

---

## Environment & Dependencies

### Python Version
```bash
python --version
# Python 3.12.7
```

### Key Dependencies
- fastapi>=0.115
- sqlalchemy>=2.0
- alembic>=1.13
- pydantic>=2.7
- pytest>=8.2
- pytest-asyncio>=0.23
- httpx>=0.27
- rapidfuzz>=3.9

---

## Database State

### Check SQLite Database
```bash
ls -lah src/meal_planner.db
```

### Database Integrity
```bash
sqlite3 src/meal_planner.db "SELECT COUNT(*) FROM recipe WHERE deleted_at IS NULL;"
sqlite3 src/meal_planner.db "SELECT title, base_servings FROM recipe LIMIT 5;"
```

---

## Maintenance Commands

### Clear Test Cache
```bash
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type d -name .pytest_cache -exec rm -rf {} +
```

### Reset Database (lose all data)
```bash
rm src/meal_planner.db
uv run alembic -c alembic.ini upgrade head
```

### Format Code
```bash
uv run ruff format src/ tests/
uv run ruff check src/ tests/ --fix
```

### Type Check
```bash
uv run mypy src/meal_planner --ignore-missing-imports
```

---

## Troubleshooting

### Migration Issues

**Problem**: `migrationError: Can't locate revision identified by ''`

**Solution**: Check `alembic.ini` has proper `[alembic]` section with `script_location`.

### Session Errors

**Problem**: `greenlet not installed`

**Solution**: The migration uses sync driver (`sqlite+pysqlite`), not async (`sqlite+aiosqlite`).

### Test Failures

**Problem**: Tests fail with import errors

**Solution**: Ensure pytest can find `meal_planner` package.

```bash
uv run pytest --co -q tests/ | head -5
```

Should list all discovered tests.
