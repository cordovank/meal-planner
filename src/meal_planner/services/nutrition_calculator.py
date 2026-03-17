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
        return labels
