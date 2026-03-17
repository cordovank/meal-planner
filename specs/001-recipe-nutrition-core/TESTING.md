# Testing Strategy & Validation

**Date**: 2026-03-17  

---

## Phase 1–3 Testing (Complete for Recipe Core)

**Status**: ✅ COMPLETE  
**Test Report**: [tests/TEST_REPORT.md](../../tests/TEST_REPORT.md)

**Test Suites Created** (52 tests, all passing):

| Task | Module | Tests | Status |
|------|--------|-------|--------|
| T009 | `services/unit_conversion.py` | 14 | ✅ PASS |
| T011 | `services/nutrition_calculator.py` | 15 | ✅ PASS |
| T010 | `infra/search/fuzzy.py` | 10 | ✅ PASS |
| T008 | `repository/sqlalchemy/session.py` | 6 | ✅ PASS |
| T024 | `services/recipe_service.py` | 7 | ✅ PASS |

**Run Tests**:
```bash
./.venv/bin/python -m pytest tests/ -v
```

---

## Phase 3 Recipe Service Integration Tests

**File**: `tests/integration/test_recipe_service.py`  
**Purpose**: Validate high-ROI recipe operations end-to-end with database persistence.

**Test Coverage**:
- ✅ **CRUD Operations**: Create, read, update, delete recipes with ingredients
- ✅ **Scaling**: Linear ingredient scaling for different serving sizes
- ✅ **Duplication**: Independent recipe copies with new names
- ✅ **Search**: Recipe listing and name-based filtering
- ✅ **Soft Deletes**: Recipes hidden after deletion (per domain rules)

**Key Validations**:
- Async database operations work correctly
- Pydantic schemas enforce data integrity
- Business logic (scaling proportions) maintained
- Repository protocol interfaces used properly
- Service layer coordinates multiple repository calls

**Run Recipe Tests**:
```bash
./.venv/bin/python -m pytest tests/integration/test_recipe_service.py -v
```

---

## Phase 3+ Testing (Per User Story)

**Integration Tests**: Added after each user story (APIs, templates, end-to-end flows)

**Pattern**:
- T0XX model creation → Unit test model validation
- T0XX repository implementation → Unit test repository methods
- T0XX service layer → Unit test business logic
- T0XX API endpoints → Integration test via TestClient
- T0XX templates → Manual test or Jinja2 render test

**Test Location Convention**:
```
tests/
├── unit/
│   ├── services/          # Business logic tests
│   ├── repository/        # Data access tests
│   └── [domain]/          # Entity/enum tests if needed
├── integration/
│   ├── api/               # Endpoint tests (Phase 3+)
│   └── end_to_end/        # Full workflow tests (Phase 5+)
└── TEST_REPORT.md         # Master report (updated per phase)
```

**Validation Commands** (see [VALIDATION.md](../../VALIDATION.md)):
```bash
# All tests
./.venv/bin/python -m pytest tests/ -v

# Specific module
./.venv/bin/python -m pytest tests/unit/services/test_nutrition_calculator.py -v

# Coverage report
./.venv/bin/python -m pytest tests/ --cov=meal_planner --cov-report=html
```

---

## Architecture-Specific Notes

Per copilot-instructions.md:
- **All nutrition calculation logic**: Unit tested (✅ T011)
- **All constraint/verifier logic**: Unit tested with boundary cases
- **All API endpoints**: Integration tested via TestClient (Phase 3+)
- **No untested verifier logic ships**

---

## Implementation Validation

See **[VALIDATION.md](../../VALIDATION.md)** for:
- ✅ Alembic migration run & output
- ✅ Python syntax validation
- ✅ Dependency verification
- ✅ Database state verification
- ✅ Quick reference commands
