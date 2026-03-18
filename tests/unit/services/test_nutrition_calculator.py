# tests/unit/services/test_nutrition_calculator.py

from dataclasses import dataclass

import pytest

from meal_planner.services.nutrition_calculator import (
    ConfidenceLevel,
    NutritionCalculator,
    NutritionRecord,
    NutritionSourceType,
    NutritionTotals,
)


@dataclass
class MockNutritionRecord:
    """Mock NutritionRecord for testing."""

    calories: float = 100.0
    protein_g: float = 10.0
    carbs_g: float = 50.0
    fat_g: float = 5.0
    added_sugar_g: float = 2.0
    source_type: NutritionSourceType = NutritionSourceType.USDA


class TestNutritionAggregation:
    """Test nutrition aggregation across multiple records."""

    def test_aggregate_single_record(self) -> None:
        """Test aggregating a single record."""
        record = MockNutritionRecord()
        result = NutritionCalculator.aggregate([record])

        assert result.calories == 100.0
        assert result.protein_g == 10.0
        assert result.carbs_g == 50.0
        assert result.fat_g == 5.0
        assert result.added_sugar_g == 2.0

    def test_aggregate_multiple_records(self) -> None:
        """Test aggregating multiple records."""
        records = [
            MockNutritionRecord(calories=100, protein_g=10),
            MockNutritionRecord(calories=200, protein_g=20),
            MockNutritionRecord(calories=150, protein_g=15),
        ]
        result = NutritionCalculator.aggregate(records)

        assert result.calories == 450.0
        assert result.protein_g == 45.0

    def test_aggregate_empty_list(self) -> None:
        """Test aggregating an empty list returns zeros."""
        result = NutritionCalculator.aggregate([])

        assert result.calories == 0.0
        assert result.protein_g == 0.0
        assert result.carbs_g == 0.0
        assert result.fat_g == 0.0
        assert result.added_sugar_g == 0.0

    def test_aggregate_precision(self) -> None:
        """Test that aggregation maintains floating-point precision."""
        records = [
            MockNutritionRecord(calories=100.5),
            MockNutritionRecord(calories=200.3),
        ]
        result = NutritionCalculator.aggregate(records)

        assert abs(result.calories - 300.8) < 0.0001


class TestConfidenceLevel:
    """Test confidence level derivation from source types."""

    def test_confidence_high_for_usda(self) -> None:
        """Test USDA source yields HIGH confidence."""
        record = MockNutritionRecord(source_type=NutritionSourceType.USDA)
        result = NutritionCalculator.confidence_for_record(record)

        assert result == ConfidenceLevel.HIGH

    def test_confidence_medium_for_third_party(self) -> None:
        """Test third-party source yields MEDIUM confidence."""
        record = MockNutritionRecord(source_type=NutritionSourceType.THIRD_PARTY)
        result = NutritionCalculator.confidence_for_record(record)

        assert result == ConfidenceLevel.MEDIUM

    def test_confidence_low_for_user_entered(self) -> None:
        """Test user-entered source yields LOW confidence."""
        record = MockNutritionRecord(source_type=NutritionSourceType.USER_ENTERED)
        result = NutritionCalculator.confidence_for_record(record)

        assert result == ConfidenceLevel.LOW


class TestCharacterization:
    """Test meal characterization label generation."""

    def test_characterize_high_protein(self) -> None:
        """Test that high protein meals get labeled."""
        totals = NutritionTotals(protein_g=30.0)
        labels = NutritionCalculator.characterize_totals(totals)

        assert "Protein-rich" in labels

    def test_characterize_low_protein(self) -> None:
        """Test that low protein meals don't get protein label."""
        totals = NutritionTotals(protein_g=5.0)
        labels = NutritionCalculator.characterize_totals(totals)

        assert "Protein-rich" not in labels

    def test_characterize_high_calories(self) -> None:
        """Test that high-calorie meals get labeled."""
        totals = NutritionTotals(calories=800.0)
        labels = NutritionCalculator.characterize_totals(totals)

        assert "High calories" in labels

    def test_characterize_low_calories(self) -> None:
        """Test that low-calorie meals don't get high-calorie label."""
        totals = NutritionTotals(calories=400.0)
        labels = NutritionCalculator.characterize_totals(totals)

        assert "High calories" not in labels

    def test_characterize_high_sugar(self) -> None:
        """Test that high added-sugar meals get labeled."""
        totals = NutritionTotals(added_sugar_g=20.0)
        labels = NutritionCalculator.characterize_totals(totals)

        assert "High added sugar" in labels

    def test_characterize_low_sugar(self) -> None:
        """Test that low added-sugar meals don't get sugar label."""
        totals = NutritionTotals(added_sugar_g=5.0)
        labels = NutritionCalculator.characterize_totals(totals)

        assert "High added sugar" not in labels

    def test_characterize_multiple_labels(self) -> None:
        """Test meal with multiple high-level nutrients gets multiple labels."""
        totals = NutritionTotals(protein_g=30.0, calories=900.0, added_sugar_g=20.0, carbs_g=100.0)
        labels = NutritionCalculator.characterize_totals(totals)

        assert "Protein-rich" in labels
        assert "High calories" in labels
        assert "High added sugar" in labels

    def test_characterize_empty_totals(self) -> None:
        """Test that zero totals yield no labels."""
        totals = NutritionTotals()
        labels = NutritionCalculator.characterize_totals(totals)

        assert len(labels) == 0

    def test_characterize_high_fiber(self) -> None:
        """Test high fiber label when fiber >= 5g."""
        totals = NutritionTotals(fiber_g=6.0, calories=300, carbs_g=40)
        labels = NutritionCalculator.characterize_totals(totals)
        assert "High fiber" in labels

    def test_characterize_low_carb(self) -> None:
        """Test low carb label when carb calories < 25% of total."""
        totals = NutritionTotals(calories=400, carbs_g=20, protein_g=50, fat_g=20)
        labels = NutritionCalculator.characterize_totals(totals)
        assert "Low carb" in labels


class TestOverallConfidence:
    """Tests for overall_confidence method."""

    def test_empty_returns_incomplete(self) -> None:
        assert NutritionCalculator.overall_confidence([]) == "incomplete"

    def test_single_level_returns_complete(self) -> None:
        assert NutritionCalculator.overall_confidence([ConfidenceLevel.HIGH]) == "complete"

    def test_same_levels_returns_complete(self) -> None:
        levels = [ConfidenceLevel.HIGH, ConfidenceLevel.HIGH]
        assert NutritionCalculator.overall_confidence(levels) == "complete"

    def test_mixed_levels_returns_mixed(self) -> None:
        levels = [ConfidenceLevel.HIGH, ConfidenceLevel.LOW]
        assert NutritionCalculator.overall_confidence(levels) == "mixed"


class TestPerServing:
    """Tests for per_serving method."""

    def test_divides_correctly(self) -> None:
        totals = NutritionTotals(calories=400, protein_g=40, carbs_g=60, fat_g=20)
        per = NutritionCalculator.per_serving(totals, 4)
        assert per.calories == 100
        assert per.protein_g == 10

    def test_zero_servings_returns_totals(self) -> None:
        totals = NutritionTotals(calories=400)
        per = NutritionCalculator.per_serving(totals, 0)
        assert per.calories == 400

    def test_single_serving_returns_same(self) -> None:
        totals = NutritionTotals(calories=250, protein_g=25)
        per = NutritionCalculator.per_serving(totals, 1)
        assert per.calories == 250
        assert per.protein_g == 25
