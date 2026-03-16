# ./src/meal_planner/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Meal Planner"
    debug: bool = False
    secret_key: str = "change-me"

    # Database
    database_url: str = "sqlite+aiosqlite:///./src/meal_planner.db"

    # Nutrition defaults (OQ-02 from Technical Plan)
    calorie_tolerance_default: int = 100       # ±kcal
    protein_tolerance_default: float = 15.0    # ±g
    carb_tolerance_default: float = 20.0       # ±g
    fat_tolerance_default: float = 10.0        # ±g
    added_sugar_tolerance_default: float = 3.0 # ±g
    added_sugar_daily_default: float = 25.0    # WHO guideline (OQ-06)


settings = Settings()