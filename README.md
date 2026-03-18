# Meal Planner

A local-first recipe home and nutrition-aware meal planning companion.

---

## Quick Start

### Development Setup
```bash
# Install dependencies
uv sync

# Apply database migrations
uv run alembic -c alembic.ini upgrade head

# Run tests
uv run pytest tests/ -v

# Start development server
uv run uvicorn meal_planner.main:app --reload
```

### API Docs

After starting the server:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Quick API Test

```bash
# Create a recipe
curl -X POST http://localhost:8000/api/v1/recipes \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Recipe", "base_servings": 2, "ingredients": [{"name": "Flour", "amount": 1.0, "unit": "cup"}]}'

# Get recipe (use the id from the response above)
curl http://localhost:8000/api/v1/recipes/{id}

# List all recipes
curl http://localhost:8000/api/v1/recipes
```

See [VALIDATION.md](VALIDATION.md) for the full API testing reference with curl examples for all endpoints.

---

## Project Status

- ✅ **Phase 1–3**: Recipe management with full CRUD, scaling, duplication, search, and notes
- ⏭️ **Phase 4**: Nutrition data integration (User Story 2)
- 📋 **Testing**: 100 automated tests (89% coverage) — 63 unit + 7 integration + 30 API endpoint tests

See [specs/](specs/) for detailed requirements and [tests/TEST_REPORT.md](tests/TEST_REPORT.md) for test coverage.
