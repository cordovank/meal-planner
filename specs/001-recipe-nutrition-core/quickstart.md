# Quickstart: Meal Planner Development

**Context**: Local development setup for Phase 1 MVP

## Prerequisites

- Python 3.12
- UV package manager
- Git

## Setup

1. **Clone and enter directory**:
   ```bash
   git clone https://github.com/your-org/meal-planner.git
   cd meal-planner
   git checkout 001-recipe-nutrition-core
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Initialize database**:
   ```bash
   uv run alembic upgrade head
   ```

5. **Start development server**:
   ```bash
   uv run uvicorn meal_planner.main:app --reload
   ```

6. **Access application**:
   - Web UI: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs
   - ReDoc: http://localhost:8000/api/redoc

## Development Workflow

### Code Changes
- Use `uv run` for all Python commands
- Run tests: `uv run pytest`
- Format code: `uv run ruff format`
- Lint: `uv run ruff check`
- Type check: `uv run mypy`

### Database Changes
- Create migration: `uv run alembic revision --autogenerate -m "description"`
- Apply migrations: `uv run alembic upgrade head`

### Testing
- Unit tests: `uv run pytest tests/unit/`
- Integration tests: `uv run pytest tests/integration/`
- Coverage: `uv run pytest --cov=meal_planner`

## Key Files

- `src/meal_planner/main.py`: FastAPI application
- `src/meal_planner/config.py`: Settings and configuration
- `src/meal_planner/api/`: API routes and schemas
- `src/meal_planner/services/`: Business logic
- `src/meal_planner/repository/`: Data access layer
- `alembic/`: Database migrations

## First Development Steps

1. **Create a recipe** via API or UI
2. **Add nutrition data** to ingredients
3. **Set up a profile** with targets
4. **Log a meal** and see progress
5. **Plan a weekly menu**

## Troubleshooting

- **Import errors**: Ensure you're in the correct directory and have activated the environment
- **Database issues**: Check `.env` DATABASE_URL and run migrations
- **Port conflicts**: Change port with `--port 8001`
- **Permission errors**: Check file permissions on SQLite database

## Architecture Notes

- **Dependency direction**: API → Services → Repository → DB
- **Pydantic contracts**: All I/O uses schemas from `api/schemas/`
- **Async everywhere**: SQLite with aiosqlite for async operations
- **UUID PKs**: All entities use UUID primary keys
- **Soft deletes**: `deleted_at` field on all entities