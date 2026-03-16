# ./src/meal_planner/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from meal_planner.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    app.mount("/static", StaticFiles(directory="src/meal_planner/web/static"), name="static")

    # Register API routers (uncomment as you build them)
    # from meal_planner.api.v1 import recipes, nutrition, profiles
    # app.include_router(recipes.router, prefix="/api/v1")

    return app


app = create_app()