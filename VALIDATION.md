# Validation & Commands Reference

**Date**: 2026-03-16  
**Status**: ✅ Phase 1–2 Validated  

---

## Quick Reference

### Run All Tests
```bash
./.venv/bin/python -m pytest tests/unit/ -v
```

### Run Application (Development)
```bash
./.venv/bin/python -m uvicorn meal_planner.main:app --reload
```

### Database Migrations

#### Check Current State
```bash
./.venv/bin/python -m alembic -c alembic.ini current
```

#### Apply Latest Migration
```bash
./.venv/bin/python -m alembic -c alembic.ini upgrade head
```

#### Create New Migration (after model changes)
```bash
./.venv/bin/python -m alembic -c alembic.ini revision --autogenerate -m "Description of changes"
```

#### Downgrade (revert last migration)
```bash
./.venv/bin/python -m alembic -c alembic.ini downgrade -1
```

#### View Migration History
```bash
./.venv/bin/python -m alembic -c alembic.ini history
```

---

## Phase 1–2 Validation Log

### ✅ Initial Alembic Setup (T001)

**Command**:
```bash
./.venv/bin/python -m alembic -c alembic.ini upgrade head
```

**Result**: ✅ SUCCESS  
**Output**:
```
2026-03-16 22:35:23,691 INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
2026-03-16 22:35:23,691 INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
2026-03-16 22:35:23,694 INFO  [alembic.runtime.migration] Running upgrade  -> 0001_initial, Initial revision
```

**Verification**:
- ✅ Migration file created: `src/meal_planner/repository/migrations/versions/0001_initial.py`
- ✅ `alembic.ini` properly configured with section headers and logging
- ✅ `env.py` updated to use `Base.metadata` from models and sync driver for migrations
- ✅ SQLite database created at `src/meal_planner.db`

---

### ✅ Pydantic Schemas (T002)

**Module**: `src/meal_planner/api/schemas/common.py`

**Validation**:
```bash
./.venv/bin/python -c "from meal_planner.api.schemas.common import BaseSchema, UUIDSchema, TimestampedSchema; print('Schemas OK')"
```

**Result**: ✅ Schemas imported successfully

---

### ✅ Error Handling Middleware (T003)

**Module**: `src/meal_planner/api/middleware.py`

**Validation**:
```bash
./.venv/bin/python -c "from meal_planner.api.middleware import register_api_middleware, http_exception_handler; print('Middleware OK')"
```

**Result**: ✅ Middleware handlers ready for FastAPI attachment

---

### ✅ Template Structure (T004)

**Paths Created**:
- ✅ `src/meal_planner/web/templates/base.html`
- ✅ `src/meal_planner/web/templates/recipes/README.md`

**Validation**:
```bash
ls -la src/meal_planner/web/templates/
```

**Result**: ✅ Jinja2 template directories ready

---

### ✅ Static Files (T005)

**Paths Created**:
- ✅ `src/meal_planner/web/static/css/main.css`
- ✅ `src/meal_planner/web/static/js/main.js`

**Validation**:
```bash
ls -la src/meal_planner/web/static/
```

**Result**: ✅ Static file serving ready

---

### ✅ Base Entity Models (T006)

**Module**: `src/meal_planner/repository/sqlalchemy/models/base.py`

**Validation**:
```bash
./.venv/bin/python -c "from meal_planner.repository.sqlalchemy.models import Base; print(f'Base metadata tables: {Base.metadata.tables}')"
```

**Result**: ✅ Base class with UUID PKs and audit fields (created_at, updated_at, deleted_at)

---

### ✅ Repository Protocols (T007)

**Module**: `src/meal_planner/services/interfaces.py`

**Validation**:
```bash
./.venv/bin/python -c "from meal_planner.services.interfaces import RepositoryProtocol, SearchRepositoryProtocol; print('Protocols OK')"
```

**Result**: ✅ Protocols defined and importable

---

### ✅ SQLAlchemy Session Management (T008)

**Module**: `src/meal_planner/repository/sqlalchemy/session.py`

**Test Command**:
```bash
./.venv/bin/python -m pytest tests/unit/repository/test_session.py -v
```

**Result**: ✅ 6/6 tests passing
- ✅ Engine singleton verified
- ✅ SessionMaker singleton verified
- ✅ Async configuration correct (expire_on_commit=False, autoflush=False)

---

### ✅ Unit Conversion Utilities (T009)

**Module**: `src/meal_planner/services/unit_conversion.py`

**Test Command**:
```bash
./.venv/bin/python -m pytest tests/unit/services/test_unit_conversion.py -v
```

**Result**: ✅ 14/14 tests passing
- ✅ Gram/ounce bidirectional conversions
- ✅ ML/cup/teaspoon/tablespoon conversions
- ✅ Edge cases (zero, large values)
- ✅ Roundtrip precision maintained

---

### ✅ Fuzzy Search (T010)

**Module**: `src/meal_planner/infra/search/fuzzy.py`

**Test Command**:
```bash
./.venv/bin/python -m pytest tests/unit/services/test_fuzzy_search.py -v
```

**Result**: ✅ 10/10 tests passing
- ✅ Exact match scoring (100.0)
- ✅ Partial match detection
- ✅ Typo tolerance
- ✅ Multi-word ingredient matching
- ✅ Score ordering (descending)

---

### ✅ Nutrition Calculator (T011)

**Module**: `src/meal_planner/services/nutrition_calculator.py`

**Test Command**:
```bash
./.venv/bin/python -m pytest tests/unit/services/test_nutrition_calculator.py -v
```

**Result**: ✅ 15/15 tests passing
- ✅ Nutrition aggregation (single, multiple, empty)
- ✅ Confidence levels (HIGH→USDA, MEDIUM→3rd-party, LOW→user)
- ✅ Meal characterization (protein, calories, sugar labels)
- ✅ Precision on floating-point values

---

## Compilation & Import Validation

### Check All Python Files for Syntax

```bash
find src/meal_planner -name "*.py" -exec python -m py_compile {} +
```

**Result**: ✅ All files compile without syntax errors

---

### Verify Main Application Loads

```bash
./.venv/bin/python -c "from meal_planner.main import app; print(f'App title: {app.title}')"
```

**Result**: ✅ FastAPI app initializes successfully
```
App title: Meal Planner
```

---

## Environment & Dependencies

### Python Version
```bash
python --version
# Python 3.12.7
```

### Key Dependencies Installed
```bash
./.venv/bin/pip list | grep -E "(fastapi|sqlalchemy|alembic|pydantic|pytest|rapidfuzz)"
```

**Result**: ✅ All required packages present
- fastapi>=0.115
- sqlalchemy>=2.0
- alembic>=1.13
- pydantic>=2.7
- pytest>=8.2
- rapidfuzz>=3.9

---

## Database State

### Check SQLite Database Created
```bash
ls -lah src/meal_planner.db
```

**Result**: ✅ Database file exists and migration has been applied

---

## Test Coverage Summary

```bash
./.venv/bin/python -m pytest tests/unit/ -v --tb=no | grep -E "(passed|failed|error)"
```

**Result**: ✅ Phase 1–2 testing complete
```
45 passed in 0.34s
```

---

## Ready for Phase 3

**Status**: ✅ READY  

All Phase 1–2 foundations validated:
- ✅ Alembic migrations working
- ✅ Base models defined
- ✅ Service layer infrastructure complete
- ✅ Async session management tested
- ✅ Critical business logic (nutrition, search, conversions) tested

**Next Command** (when starting Phase 3 recipes):
```bash
./.venv/bin/python -m pytest tests/unit/ -v && echo "✅ Ready for Phase 3"
```

---

## Troubleshooting

### Migration Issues

**Problem**: `migrationError: Can't locate revision identified by ''`

**Solution**: Check `alembic.ini` has proper `[alembic]` section with `script_location`.

**Validate**:
```bash
head -20 alembic.ini
```

### Session Errors

**Problem**: `greenlet not installed`

**Solution**: The migration uses sync driver (`sqlite+pysqlite`), not async (`sqlite+aiosqlite`).

**Verify**:
```bash
./.venv/bin/python -c "from meal_planner.repository.sqlalchemy.session import get_engine; print(get_engine().url)"
# Should show: sqlite+aiosqlite:///./src/meal_planner.db
```

### Test Failures

**Problem**: Tests fail with import errors

**Solution**: Ensure pytest can find `meal_planner` package.

**Validate**:
```bash
./.venv/bin/python -m pytest --co -q tests/unit/ | head -5
```

Should list all discovered tests.

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
./.venv/bin/python -m alembic -c alembic.ini upgrade head
```

### Format Code
```bash
./.venv/bin/ruff format src/ tests/
./.venv/bin/ruff check src/ tests/ --fix
```

### Type Check
```bash
./.venv/bin/mypy src/meal_planner --ignore-missing-imports
```
