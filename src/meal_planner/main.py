# ./src/meal_planner/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from meal_planner.config import settings
from meal_planner.api.middleware import register_api_middleware

templates = Jinja2Templates(directory="src/meal_planner/web/templates")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    app.mount("/static", StaticFiles(directory="src/meal_planner/web/static"), name="static")
    register_api_middleware(app)

    # Register API routers
    from meal_planner.api.v1 import recipes_router
    app.include_router(recipes_router)

    return app


app = create_app()