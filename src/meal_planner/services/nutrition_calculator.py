# ./src/meal_planner/services/nutrition_calculator.py

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Protocol


class NutritionSourceType(str, Enum):
    """Sources for nutrition values used for confidence scoring."""

    USER_ENTERED = "user_entered"
    USDA = "usda"
    THIRD_PARTY = "third_party"


class NutritionRecord(Protocol):
    """Protocol for objects that can provide nutrition values."""

    @property
    def calories(self) -> float:
        ...

    @property
    def protein_g(self) -> float:
        ...

    @property
    def carbs_g(self) -> float:
        ...

    @property
    def fat_g(self) -> float:
        ...

    @property
    def added_sugar_g(self) -> float:
        ...

    @property
    def source_type(self) -> NutritionSourceType:
        ...


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class NutritionTotals:
    calories: float = 0.0
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    added_sugar_g: float = 0.0
    fiber_g: float = 0.0
    total_sugar_g: float = 0.0
    sodium_mg: float = 0.0
    saturated_fat_g: float = 0.0


class NutritionCalculator:
    """Foundation for nutrition calculation logic."""

    @staticmethod
    def aggregate(records: Iterable[NutritionRecord]) -> NutritionTotals:
        """Aggregate nutrition values across records."""

        totals = NutritionTotals()
        for record in records:
            totals = NutritionTotals(
                calories=totals.calories + record.calories,
                protein_g=totals.protein_g + record.protein_g,
                carbs_g=totals.carbs_g + record.carbs_g,
                fat_g=totals.fat_g + record.fat_g,
                added_sugar_g=totals.added_sugar_g + record.added_sugar_g,
                fiber_g=totals.fiber_g + getattr(record, "fiber_g", 0) or 0,
                total_sugar_g=totals.total_sugar_g + getattr(record, "total_sugar_g", 0) or 0,
                sodium_mg=totals.sodium_mg + getattr(record, "sodium_mg", 0) or 0,
                saturated_fat_g=totals.saturated_fat_g + getattr(record, "saturated_fat_g", 0) or 0,
            )
        return totals

    @staticmethod
    def confidence_for_record(record: NutritionRecord) -> ConfidenceLevel:
        """Derive a confidence level from the source type."""

        if record.source_type == NutritionSourceType.USER_ENTERED:
            return ConfidenceLevel.LOW
        if record.source_type == NutritionSourceType.THIRD_PARTY:
            return ConfidenceLevel.MEDIUM
        if record.source_type == NutritionSourceType.USDA:
            return ConfidenceLevel.HIGH
        return ConfidenceLevel.MEDIUM

    @staticmethod
    def characterize_totals(totals: NutritionTotals) -> list[str]:
        """Return lightweight characterization labels for a nutrition total."""

        labels: list[str] = []
        if totals.protein_g >= 20:
            labels.append("Protein-rich")
        if totals.calories > 700:
            labels.append("High calories")
        if totals.added_sugar_g > 15:
            labels.append("High added sugar")
        if totals.fiber_g >= 5:
            labels.append("High fiber")
        if totals.calories > 0 and totals.carbs_g * 4 / totals.calories < 0.25:
            labels.append("Low carb")
        return labels

    @staticmethod
    def overall_confidence(confidence_levels: list[ConfidenceLevel]) -> str:
        """Determine overall confidence from a list of per-ingredient levels.

        Returns 'complete', 'mixed', or 'incomplete'.
        """
        if not confidence_levels:
            return "incomplete"
        unique = set(confidence_levels)
        if len(unique) == 1:
            return "complete"
        return "mixed"

    @staticmethod
    def per_serving(totals: NutritionTotals, servings: int) -> NutritionTotals:
        """Divide totals by number of servings."""
        if servings <= 0:
            return totals
        return NutritionTotals(
            calories=round(totals.calories / servings, 2),
            protein_g=round(totals.protein_g / servings, 2),
            carbs_g=round(totals.carbs_g / servings, 2),
            fat_g=round(totals.fat_g / servings, 2),
            added_sugar_g=round(totals.added_sugar_g / servings, 2),
            fiber_g=round(totals.fiber_g / servings, 2),
            total_sugar_g=round(totals.total_sugar_g / servings, 2),
            sodium_mg=round(totals.sodium_mg / servings, 2),
            saturated_fat_g=round(totals.saturated_fat_g / servings, 2),
        )
