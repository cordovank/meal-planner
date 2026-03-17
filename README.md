# Meal Planner

A local-first recipe home and nutrition-aware meal planning companion.

---

## Quick Start

### Development Setup
```bash
# Install dependencies
uv sync

# Run tests
uv run python -m pytest tests/ -v

# Start development server
uv run uvicorn meal_planner.main:app --reload
```

### Manual Validation (Phase 3 Complete)

After starting the server, test core functionality:

1. **Recipe Creation**: Visit `http://localhost:8000/recipes` → "Add Recipe" → Fill form → Save
2. **Recipe Scaling**: View recipe → "Scale Recipe" → Change servings → Verify ingredient amounts scale
3. **Recipe Search**: Create multiple recipes → Use search box → Verify filtering works
4. **API Testing**: Use curl or browser dev tools to test `/api/v1/recipes` endpoints

See [VALIDATION.md](VALIDATION.md) for detailed commands and automated checks.

---

## Project Status

- ✅ **Phase 1–3**: Recipe management with full CRUD, scaling, and search
- ⏭️ **Phase 4**: Nutrition integration and meal planning
- 📋 **Testing**: 52 automated tests covering critical paths (45 unit + 7 integration)

See [specs/](specs/) for detailed requirements and [tests/TEST_REPORT.md](tests/TEST_REPORT.md) for test coverage.
