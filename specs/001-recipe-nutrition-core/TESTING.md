# Testing Strategy & Validation

**Date**: 2026-03-18

---

## Phase 1–3 Testing (Complete for Recipe Core)

**Status**: ✅ COMPLETE
**Test Report**: [tests/TEST_REPORT.md](../../tests/TEST_REPORT.md)

**Test Suites** (100 tests, all passing):

| Layer | Module | Tests | Status |
|-------|--------|-------|--------|
| Unit | `services/unit_conversion.py` | 14 | ✅ PASS |
| Unit | `services/nutrition_calculator.py` | 15 | ✅ PASS |
| Unit | `infra/search/fuzzy.py` | 10 | ✅ PASS |
| Unit | `repository/sqlalchemy/session.py` | 6 | ✅ PASS |
| Unit | `services/recipe_service.py` (mock-based) | 12 | ✅ PASS |
| Unit | `api/schemas/recipe.py` | 6 | ✅ PASS |
| API | `api/v1/recipes.py` (HTTP endpoints) | 25 | ✅ PASS |
| API | `api/middleware.py` (error handling) | 5 | ✅ PASS |
| Integration | `services/recipe_service.py` (with DB) | 7 | ✅ PASS |

**Run Tests**:
```bash
uv run pytest tests/ -v
```

---

## Phase 3 Test Coverage by Layer

### API Endpoint Tests (30 tests)

**Files**: `tests/api/test_recipe_endpoints.py`, `tests/api/test_error_handling.py`
**Fixtures**: `tests/api/conftest.py` (in-memory SQLite, httpx AsyncClient)

**Purpose**: Full-stack HTTP tests exercising the complete request lifecycle. These tests use `httpx.AsyncClient` with FastAPI's `ASGITransport` and an in-memory SQLite database (via dependency override) for isolated, fast testing.

**Coverage**:
- ✅ **All 12 API endpoints** tested with success and error paths
- ✅ **Cross-request persistence** (POST then GET — catches session commit bugs)
- ✅ **Error envelope format** validated for both HTTP and validation errors
- ✅ **Pydantic field constraints** (e.g., `new_servings > 0`) enforced at API level
- ✅ **Pagination, search, state filtering** verified at HTTP level
- ✅ **Soft delete behavior** (DELETE then GET returns 404)

### Service Layer Unit Tests (12 tests)

**File**: `tests/unit/services/test_recipe_service_unit.py`

**Purpose**: Mock-based unit tests filling branch coverage gaps in `RecipeService`. Uses `unittest.mock.AsyncMock` for the repository.

**Coverage**:
- ✅ All "not found" branches (update_ingredient, remove_ingredient, add_note, remove_note, duplicate_recipe, get_recipe_with_relations)
- ✅ Scale edge cases (base_servings=0, ingredient.amount=None)
- ✅ Field update application in update_ingredient

### Schema Validation Tests (6 tests)

**File**: `tests/unit/schemas/test_recipe_schemas.py`

**Coverage**:
- ✅ Default values applied correctly
- ✅ Required field enforcement
- ✅ Field constraints (gt=0)
- ✅ Partial update semantics (all fields optional)

### Service Layer Integration Tests (7 tests)

**File**: `tests/integration/test_recipe_service.py`

**Purpose**: Direct service-layer tests with real async database operations.

**Coverage**:
- ✅ **CRUD Operations**: Create, read, update, delete recipes with ingredients
- ✅ **Scaling**: Linear ingredient scaling for different serving sizes
- ✅ **Duplication**: Independent recipe copies with new names
- ✅ **Search**: Recipe listing and name-based filtering
- ✅ **Soft Deletes**: Recipes hidden after deletion

---

## Bugs Found by Tests

1. **Session ROLLBACK bug**: `get_session()` never committed. POST created data but ROLLBACK on session close meant GET returned 404. Fixed by adding commit/rollback to `get_session()`. Caught by `test_create_then_get_persists`.

2. **Scale endpoint lazy-load bug**: `scale_recipe()` accessed `recipe.ingredients` (lazy ORM relationship) in async context, causing `MissingGreenlet` error. Fixed by passing pre-loaded ingredients explicitly. Caught by `test_scale_recipe`.

---

## Testing Pattern

```
Layer          │ Test Type        │ Tools            │ Purpose
───────────────┼──────────────────┼──────────────────┼──────────────────────
API endpoints  │ HTTP integration │ httpx + FastAPI  │ Contract validation
Middleware     │ HTTP integration │ httpx + FastAPI  │ Error envelope format
Schemas        │ Unit             │ Pydantic direct  │ Input constraints
Service        │ Unit (mocks)     │ AsyncMock        │ Branch coverage
Service        │ Integration      │ Real DB session  │ E2E business logic
Repository     │ (via service)    │ Real DB session  │ Query correctness
Infrastructure │ Unit             │ Direct calls     │ Config/singleton
```

---

## Test Location Convention

```
tests/
├── api/                              # HTTP-level tests (httpx AsyncClient)
│   ├── conftest.py                   # In-memory DB fixtures, client
│   ├── test_recipe_endpoints.py      # 25 endpoint tests
│   └── test_error_handling.py        # 5 error/validation tests
├── unit/
│   ├── services/                     # Business logic tests
│   │   ├── test_unit_conversion.py
│   │   ├── test_nutrition_calculator.py
│   │   ├── test_fuzzy_search.py
│   │   └── test_recipe_service_unit.py
│   ├── schemas/                      # Pydantic validation tests
│   │   └── test_recipe_schemas.py
│   └── repository/                   # Data access config tests
│       └── test_session.py
├── integration/                      # Service + real DB tests
│   └── test_recipe_service.py
└── TEST_REPORT.md
```

---

## Validation Commands

```bash
# All tests
uv run pytest tests/ -v

# By layer
uv run pytest tests/api/ -v          # API endpoint tests
uv run pytest tests/unit/ -v         # Unit tests
uv run pytest tests/integration/ -v  # Integration tests

# Coverage report
uv run pytest tests/ --cov=meal_planner --cov-report=term-missing
```

---

## Architecture-Specific Notes

Per copilot-instructions.md:
- **All nutrition calculation logic**: Unit tested (✅ T011)
- **All constraint/verifier logic**: Unit tested with boundary cases
- **All API endpoints**: Integration tested via httpx AsyncClient (✅)
- **No untested verifier logic ships**

---

## Implementation Validation

See **[VALIDATION.md](../../VALIDATION.md)** for:
- ✅ Alembic migration run & output
- ✅ Python syntax validation
- ✅ Dependency verification
- ✅ Database state verification
- ✅ API curl testing reference with sample payloads
