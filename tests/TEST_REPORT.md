# Test Report: Meal Planner MVP

**Status**: ✅ PASSING
**Last Updated**: 2026-03-18
**Test Framework**: pytest 9.0.2, asyncio (auto mode)

---

## Summary

All Phase 1–4 tests passing. **141 tests** across 13 test modules validate core infrastructure, recipe functionality, food library, nutrition calculations, API endpoints, error handling, and schema validation.

| Phase | Module | Tests | Status | Coverage |
|-------|--------|-------|--------|----------|
| 2     | `services/unit_conversion.py` | 14 | ✅ PASS | Gram/oz, ml/cup/tsp/tbsp conversions |
| 2     | `services/nutrition_calculator.py` | 24 | ✅ PASS | Aggregation, confidence, characterization, per-serving |
| 2     | `infra/search/fuzzy.py` | 10 | ✅ PASS | Exact/partial matching, scoring, limits |
| 2     | `repository/sqlalchemy/session.py` | 6 | ✅ PASS | Engine/sessionmaker singletons, config |
| 3     | `services/recipe_service.py` (integration) | 7 | ✅ PASS | CRUD, scaling, duplication, search |
| 3     | `api/v1/recipes.py` (HTTP endpoints) | 25 | ✅ PASS | Full-stack API tests via httpx |
| 3     | `api/middleware.py` (error handling) | 5 | ✅ PASS | Error envelopes, validation rejection |
| 3     | `services/recipe_service.py` (unit) | 12 | ✅ PASS | Service branch coverage with mocks |
| 3     | `api/schemas/recipe.py` | 6 | ✅ PASS | Pydantic validation rules |
| 4     | `api/v1/food.py` (HTTP endpoints) | 18 | ✅ PASS | Food CRUD, nutrition, recipe nutrition breakdown |
| 4     | `services/food_service.py` (unit) | 10 | ✅ PASS | Food service branch coverage with mocks |
| 4     | `api/schemas/food.py` | 7 | ✅ PASS | Food/nutrition schema validation |

---

## Test Suites

### T009: Unit Conversion (14 tests)

**File**: `tests/unit/services/test_unit_conversion.py`

**Purpose**: Validate bidirectional conversions for recipe scaling and ingredient measurements.

**Tests**:
- ✅ `test_grams_to_ounces_standard` — 100g → oz
- ✅ `test_ounces_to_grams_standard` — 1 oz → g (with tolerance)
- ✅ `test_gram_ounce_roundtrip` — g → oz → g identity
- ✅ `test_zero_grams` — Edge case: zero
- ✅ `test_large_values` — 1kg conversion
- ✅ `test_cups_to_ml_standard` — 1 cup = 240ml
- ✅ `test_ml_to_cups_standard` — 240ml = 1 cup
- ✅ `test_ml_cups_roundtrip` — ml → cup → ml identity
- ✅ `test_ml_to_teaspoons_standard` — ml → tsp
- ✅ `test_teaspoons_to_ml_standard` — tsp → ml
- ✅ `test_ml_to_tablespoons_standard` — ml → tbsp
- ✅ `test_tablespoons_to_ml_standard` — tbsp → ml
- ✅ `test_fractional_cups` — 0.5 cup = 120ml (common recipe case)
- ✅ `test_zero_volume` — Edge case: zero volume

**Key Validations**:
- All conversions maintain ±0.01 tolerance
- Roundtrip conversions are identity-preserving
- Edge cases (zero, large values) handled safely

---

### T011: Nutrition Calculator (15 tests)

**File**: `tests/unit/services/test_nutrition_calculator.py`

**Purpose**: Validate nutrition aggregation, confidence scoring, and meal characterization per cooking context requirements.

**Test Groups**:

#### Aggregation (4 tests)
- ✅ `test_aggregate_single_record` — Single item totals
- ✅ `test_aggregate_multiple_records` — Multi-item sum
- ✅ `test_aggregate_empty_list` — Empty returns zeros
- ✅ `test_aggregate_precision` — Floating-point precision maintained

#### Confidence Levels (3 tests)
- ✅ `test_confidence_high_for_usda` — USDA → HIGH
- ✅ `test_confidence_medium_for_third_party` — 3rd-party → MEDIUM
- ✅ `test_confidence_low_for_user_entered` — User → LOW

#### Characterization (8 tests)
- ✅ `test_characterize_high_protein` — ≥20g protein labeled
- ✅ `test_characterize_low_protein` — <20g not labeled
- ✅ `test_characterize_high_calories` — >700 kcal labeled
- ✅ `test_characterize_low_calories` — ≤700 kcal not labeled
- ✅ `test_characterize_high_sugar` — >15g added sugar labeled
- ✅ `test_characterize_low_sugar` — ≤15g not labeled
- ✅ `test_characterize_multiple_labels` — Multi-nutrient meals get multiple labels
- ✅ `test_characterize_empty_totals` — Zero totals = no labels

**Key Validations**:
- Confidence levels map to source_type enum correctly
- Characterization labels use domain thresholds (protein ≥20g, calories >700, sugar >15g)
- Supports non-punitive language per constitution (labels are constructive)

---

### T010: Fuzzy Search (10 tests)

**File**: `tests/unit/services/test_fuzzy_search.py`

**Purpose**: Validate ingredient search works with typo tolerance and scoring.

**Tests**:
- ✅ `test_exact_match_returns_high_score` — "apple" → "apple" (100.0)
- ✅ `test_partial_match_returns_results` — "chicken" finds chicken variants
- ✅ `test_limit_respects_max_results` — limit=3 returns ≤3 results
- ✅ `test_score_cutoff_filters_poor_matches` — High cutoff eliminates low-quality matches
- ✅ `test_empty_choices` — No crash on empty list
- ✅ `test_consistent_matching` — Queries are deterministic
- ✅ `test_typo_tolerance` — "tomat" finds "tomato"
- ✅ `test_common_ingredient_search` — Multi-word ingredient matching
- ✅ `test_multiple_word_matching` — "extra virgin olive" finds variants
- ✅ `test_score_ordering` — Results in descending score order

**Key Validations**:
- RapidFuzz `WRatio` scorer integrated correctly
- Typo tolerance works (>50% threshold by default)
- Results sorted by score descending

---

### T008: SQLAlchemy Async Session (6 tests)

**File**: `tests/unit/repository/test_session.py`

**Purpose**: Validate async database connectivity and session factory configuration.

**Tests**:
- ✅ `test_get_engine_singleton` — Engine instance reused
- ✅ `test_get_engine_creates_async_engine` — Async SQLite engine created
- ✅ `test_get_sessionmaker_singleton` — SessionMaker instance reused
- ✅ `test_get_sessionmaker_configuration` — AsyncSession class, expire_on_commit=False, autoflush=False, future=True
- ✅ `test_engine_url_configuration` — URL uses aiosqlite driver
- ✅ `test_sessionmaker_bound_to_engine` — SessionMaker bound to engine

**Key Validations**:
- Both engine and sessionmaker are singletons (cached)
- Async settings configured per SQLAlchemy 2.0 best practices
- Database URL uses **sqlite+aiosqlite** (not pysqlite)
- Ready for FastAPI dependency injection

---

### Recipe Service Integration (7 tests)

**File**: `tests/integration/test_recipe_service.py`

**Purpose**: Validate recipe CRUD operations, scaling, duplication, and search functionality end-to-end with database.

**Tests**:
- ✅ `test_create_recipe` — Create recipe with ingredients
- ✅ `test_get_recipe` — Retrieve recipe by ID
- ✅ `test_update_recipe` — Update recipe details and ingredients
- ✅ `test_delete_recipe` — Soft delete recipe
- ✅ `test_scale_recipe` — Scale ingredients for different servings
- ✅ `test_duplicate_recipe` — Duplicate recipe with new name
- ✅ `test_list_recipes` — List and search recipes

**Key Validations**:
- Full CRUD cycle works with async database operations
- Ingredient scaling maintains proportions
- Duplication creates independent copies
- Search works across recipe names
- Soft deletes hide recipes from queries

---

### HTTP API Endpoint Tests (25 tests)

**File**: `tests/api/test_recipe_endpoints.py`

**Purpose**: Full-stack HTTP integration tests using httpx AsyncClient. These tests exercise the complete request lifecycle: HTTP request → FastAPI routing → dependency injection → service → repository → database → response serialization. This suite would have caught the session ROLLBACK bug discovered during manual validation.

**Test Groups**:

#### Recipe CRUD (10 tests)
- ✅ `test_create_recipe_returns_201` — POST returns 201 with id/title/state/created_at
- ✅ `test_create_then_get_persists` — POST then GET verifies cross-request persistence
- ✅ `test_create_with_ingredients_then_get_has_ingredients` — Ingredients appear on detail view
- ✅ `test_create_minimal_recipe` — Only title required; defaults applied
- ✅ `test_get_nonexistent_returns_404` — Random UUID returns 404
- ✅ `test_update_recipe` — PUT updates fields correctly
- ✅ `test_update_nonexistent_returns_404` — PUT on missing recipe returns 404
- ✅ `test_delete_returns_204` — DELETE returns 204 with empty body
- ✅ `test_delete_then_get_returns_404` — Soft-deleted recipe hidden from GET
- ✅ `test_delete_nonexistent_returns_404` — DELETE on missing recipe returns 404

#### List & Search (5 tests)
- ✅ `test_list_empty` — Empty DB returns `{items: [], total: 0, has_more: false}`
- ✅ `test_list_returns_created` — Created recipes appear in list
- ✅ `test_list_state_filter` — `?state=finalized` filters correctly
- ✅ `test_list_pagination` — `?limit=2&offset=0` paginates with `has_more`
- ✅ `test_search_recipes` — `?q=Chocolate` matches title search

#### Scale & Duplicate (4 tests)
- ✅ `test_scale_recipe` — Doubled servings double ingredient amounts
- ✅ `test_scale_nonexistent_returns_404` — Scale missing recipe returns 404
- ✅ `test_duplicate_recipe` — Returns 201 with new ID and parent link
- ✅ `test_duplicate_nonexistent_returns_404` — Duplicate missing recipe returns 404

#### Ingredient Sub-resource (4 tests)
- ✅ `test_add_ingredient` — POST ingredient returns 201
- ✅ `test_add_ingredient_missing_recipe_returns_404` — Missing recipe returns 404
- ✅ `test_update_ingredient` — PUT updates ingredient fields
- ✅ `test_remove_ingredient` — DELETE ingredient returns 204

#### Note Sub-resource (2 tests)
- ✅ `test_add_note` — POST note returns 201 with text and created_at
- ✅ `test_remove_note` — DELETE note returns 204

**Key Validations**:
- Cross-request data persistence (the commit bug catcher)
- All 12 API endpoints exercised with success and error paths
- Response status codes match API contract (201, 204, 404)
- Soft delete hides recipes from subsequent GETs
- Pagination and search work correctly at the HTTP level

---

### Error Handling & Middleware (5 tests)

**File**: `tests/api/test_error_handling.py`

**Purpose**: Validate the standardized error response envelope format produced by middleware exception handlers.

**Tests**:
- ✅ `test_http_error_envelope` — 404 returns `{"error": {"type": "http", "message": "..."}}`
- ✅ `test_validation_error_envelope_missing_field` — Missing required field returns 422 with details
- ✅ `test_validation_error_wrong_types` — Wrong field types return 422
- ✅ `test_scale_rejects_zero_servings` — `new_servings: 0` rejected (gt=0 constraint)
- ✅ `test_scale_rejects_negative_servings` — `new_servings: -1` rejected

**Key Validations**:
- HTTP errors wrapped in `{"error": {"type": "http", "message": "..."}}` envelope
- Validation errors wrapped in `{"error": {"type": "validation", "message": "...", "details": [...]}}` envelope
- Pydantic field constraints (`gt=0`) enforced at the API level

---

### Recipe Service Unit Tests (12 tests)

**File**: `tests/unit/services/test_recipe_service_unit.py`

**Purpose**: Mock-based unit tests for RecipeService methods not covered by integration tests. Fills branch coverage gaps.

**Tests**:
- ✅ `test_update_ingredient_applies_fields` — All field updates applied correctly
- ✅ `test_update_ingredient_not_found` — Returns None
- ✅ `test_remove_ingredient_not_found` — Returns False
- ✅ `test_remove_ingredient_success` — Returns True, calls repo
- ✅ `test_add_note_recipe_not_found` — Returns None
- ✅ `test_add_note_success` — Creates note with correct text and UUID
- ✅ `test_remove_note_not_found` — Returns False
- ✅ `test_remove_note_success` — Returns True, calls repo
- ✅ `test_get_recipe_with_relations_not_found` — Returns None
- ✅ `test_scale_base_servings_zero` — Returns `{factor: 1.0, ingredients: []}`
- ✅ `test_scale_ingredient_amount_none` — To-taste ingredient stays None
- ✅ `test_duplicate_not_found` — Returns None

**Key Validations**:
- All "not found" branches return correct sentinel values (None/False)
- Ingredient update applies all optional fields correctly
- Scale edge cases: zero servings, None amounts handled safely

---

### Schema Validation Tests (6 tests)

**File**: `tests/unit/schemas/test_recipe_schemas.py`

**Purpose**: Validate Pydantic schema constraints directly.

**Tests**:
- ✅ `test_create_defaults` — `RecipeCreateSchema(title="X")` defaults: state=draft, base_servings=1
- ✅ `test_create_requires_title` — Missing title raises ValidationError
- ✅ `test_scale_rejects_zero` — `new_servings=0` raises ValidationError
- ✅ `test_scale_rejects_negative` — `new_servings=-1` raises ValidationError
- ✅ `test_update_all_optional` — All fields optional for partial updates
- ✅ `test_ingredient_create_defaults` — Boolean defaults: to_taste=False, optional=False

---

## Running Tests

### All Tests
```bash
uv run pytest tests/ -v
```

### By Layer
```bash
# API endpoint tests (HTTP-level)
uv run pytest tests/api/ -v

# Unit tests
uv run pytest tests/unit/ -v

# Integration tests (service-layer)
uv run pytest tests/integration/ -v
```

### By Module
```bash
# Unit conversions
uv run pytest tests/unit/services/test_unit_conversion.py -v

# Nutrition calculator
uv run pytest tests/unit/services/test_nutrition_calculator.py -v

# Fuzzy search
uv run pytest tests/unit/services/test_fuzzy_search.py -v

# Session/DB
uv run pytest tests/unit/repository/test_session.py -v

# Recipe service (mock-based unit)
uv run pytest tests/unit/services/test_recipe_service_unit.py -v

# Schema validation
uv run pytest tests/unit/schemas/test_recipe_schemas.py -v

# Recipe service integration
uv run pytest tests/integration/test_recipe_service.py -v

# API endpoints
uv run pytest tests/api/test_recipe_endpoints.py -v

# Error handling
uv run pytest tests/api/test_error_handling.py -v

# Food endpoints (Phase 4)
uv run pytest tests/api/test_food_endpoints.py -v

# Food service unit tests (Phase 4)
uv run pytest tests/unit/services/test_food_service_unit.py -v

# Food schema validation (Phase 4)
uv run pytest tests/unit/schemas/test_food_schemas.py -v
```

### Coverage Report
```bash
uv run pytest tests/ --cov=meal_planner --cov-report=term-missing
```

---

## Bugs Found by Test Suite

### 1. Session ROLLBACK Bug (Fixed)
**Found by**: Manual validation (POST then GET returned 404)
**Root cause**: `get_session()` in `session.py` never called `commit()`. Data was flushed but rolled back when the session closed.
**Fix**: Added `await session.commit()` on success, `await session.rollback()` on exception in `get_session()`.
**Preventing test**: `test_create_then_get_persists` in `test_recipe_endpoints.py`.

### 2. Scale Endpoint Lazy-Load Bug (Fixed)
**Found by**: `test_scale_recipe` in `test_recipe_endpoints.py`
**Root cause**: The scale endpoint fetched `relations` (with pre-loaded ingredients) but passed the ORM `recipe` object to `scale_recipe()`, which accessed `recipe.ingredients` (a lazy-loaded relationship). This triggered sync I/O in an async context.
**Fix**: `scale_recipe()` now accepts an explicit `ingredients` parameter; endpoint passes `relations["ingredients"]`.

---

## Coverage Summary (2026-03-18)

| Module | Coverage |
|--------|----------|
| `api/middleware.py` | 100% |
| `api/schemas/recipe.py` | 100% |
| `api/schemas/food.py` | 100% |
| `api/schemas/common.py` | 100% |
| `config.py` | 100% |
| `main.py` | 100% |
| `infra/search/fuzzy.py` | 100% |
| `services/unit_conversion.py` | 100% |
| `services/nutrition_calculator.py` | 99% |
| `models/food.py` | 96% |
| `models/recipe.py` | 94% |
| `services/recipe_service.py` | 94% |
| `repositories/recipe_repository.py` | 92% |
| `api/v1/food.py` | 66% |
| `services/food_service.py` | 64% |
| `repositories/food_repository.py` | 66% |
| **Overall** | **83%** |

---

## Test Metrics (2026-03-18)

| Metric | Value |
|--------|-------|
| **Total Tests** | 141 |
| **Passing** | 141 (100%) |
| **Failing** | 0 |
| **Skipped** | 0 |
| **Errors** | 0 |
| **Execution Time** | ~0.8s |
| **Modules Covered** | 13 test files across 3 layers |

---

## Test Organization

```
tests/
├── api/
│   ├── conftest.py                        # In-memory DB fixtures, httpx client
│   ├── test_recipe_endpoints.py           # 25 HTTP-level API tests
│   ├── test_food_endpoints.py             # 18 food + nutrition API tests
│   └── test_error_handling.py             # 5 middleware/validation tests
├── unit/
│   ├── services/
│   │   ├── test_unit_conversion.py        # T009 (14 tests)
│   │   ├── test_nutrition_calculator.py   # T011 (24 tests)
│   │   ├── test_fuzzy_search.py           # T010 (10 tests)
│   │   ├── test_recipe_service_unit.py    # 12 mock-based service tests
│   │   └── test_food_service_unit.py      # 10 food service mock tests
│   ├── schemas/
│   │   ├── test_recipe_schemas.py         # 6 Pydantic validation tests
│   │   └── test_food_schemas.py           # 7 food schema validation tests
│   └── repository/
│       └── test_session.py                # T008 (6 tests)
├── integration/
│   └── test_recipe_service.py             # 7 service-layer integration tests
└── TEST_REPORT.md
```

**Convention**: Test file names follow `test_<module>.py`, matching source module names in `src/meal_planner/`.
