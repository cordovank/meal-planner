# ./src/meal_planner/services/unit_conversion.py

from __future__ import annotations

# Common unit conversions. These are intentionally simple and deterministic for Phase 1.

GRAMS_PER_OUNCE = 28.349523125
ML_PER_CUP = 240.0
ML_PER_TSP = 4.92892159375
ML_PER_TBSP = 14.78676478125


def grams_to_ounces(grams: float) -> float:
    """Convert grams to ounces."""

    return grams / GRAMS_PER_OUNCE


def ounces_to_grams(ounces: float) -> float:
    """Convert ounces to grams."""

    return ounces * GRAMS_PER_OUNCE


def ml_to_cups(ml: float) -> float:
    """Convert milliliters to cups."""

    return ml / ML_PER_CUP


def cups_to_ml(cups: float) -> float:
    """Convert cups to milliliters."""

    return cups * ML_PER_CUP


def ml_to_teaspoons(ml: float) -> float:
    """Convert milliliters to teaspoons."""

    return ml / ML_PER_TSP


def teaspoons_to_ml(tsp: float) -> float:
    """Convert teaspoons to milliliters."""

    return tsp * ML_PER_TSP


def ml_to_tablespoons(ml: float) -> float:
    """Convert milliliters to tablespoons."""

    return ml / ML_PER_TBSP


def tablespoons_to_ml(tbsp: float) -> float:
    """Convert tablespoons to milliliters."""

    return tbsp * ML_PER_TBSP
