# tests/unit/services/test_unit_conversion.py

import pytest

from meal_planner.services.unit_conversion import (
    cups_to_ml,
    grams_to_ounces,
    ml_to_cups,
    ml_to_tablespoons,
    ml_to_teaspoons,
    ounces_to_grams,
    tablespoons_to_ml,
    teaspoons_to_ml,
    GRAMS_PER_OUNCE,
    ML_PER_CUP,
    ML_PER_TBSP,
    ML_PER_TSP,
)


class TestGramOunceConversion:
    """Test gram/ounce bidirectional conversions."""

    def test_grams_to_ounces_standard(self) -> None:
        """Test standard 100g → ounce conversion."""
        result = grams_to_ounces(100)
        assert round(result, 2) == round(100 / GRAMS_PER_OUNCE, 2)

    def test_ounces_to_grams_standard(self) -> None:
        """Test standard ounce → gram conversion."""
        result = ounces_to_grams(1)
        assert abs(result - GRAMS_PER_OUNCE) < 0.0001

    def test_gram_ounce_roundtrip(self) -> None:
        """Test that gram → ounce → gram is identity."""
        original = 250.0
        converted = ounces_to_grams(grams_to_ounces(original))
        assert abs(converted - original) < 0.001

    def test_zero_grams(self) -> None:
        """Test edge case: zero grams."""
        assert grams_to_ounces(0) == 0.0

    def test_large_values(self) -> None:
        """Test large gram values (e.g., 1kg)."""
        result = grams_to_ounces(1000)
        expected = 1000 / GRAMS_PER_OUNCE
        assert abs(result - expected) < 0.01


class TestVolumeConversion:
    """Test volume conversions (ml, cups, tsp, tbsp)."""

    def test_cups_to_ml_standard(self) -> None:
        """Test 1 cup → ml conversion."""
        result = cups_to_ml(1)
        assert result == ML_PER_CUP

    def test_ml_to_cups_standard(self) -> None:
        """Test ml → cups conversion."""
        result = ml_to_cups(ML_PER_CUP)
        assert result == 1.0

    def test_ml_cups_roundtrip(self) -> None:
        """Test ml → cups → ml is identity."""
        original = 480.0
        converted = cups_to_ml(ml_to_cups(original))
        assert abs(converted - original) < 0.001

    def test_ml_to_teaspoons_standard(self) -> None:
        """Test ml → teaspoons conversion."""
        result = ml_to_teaspoons(ML_PER_TSP)
        assert abs(result - 1.0) < 0.0001

    def test_teaspoons_to_ml_standard(self) -> None:
        """Test teaspoons → ml conversion."""
        result = teaspoons_to_ml(1)
        assert abs(result - ML_PER_TSP) < 0.0001

    def test_ml_to_tablespoons_standard(self) -> None:
        """Test ml → tablespoons conversion."""
        result = ml_to_tablespoons(ML_PER_TBSP)
        assert abs(result - 1.0) < 0.0001

    def test_tablespoons_to_ml_standard(self) -> None:
        """Test tablespoons → ml conversion."""
        result = tablespoons_to_ml(1)
        assert abs(result - ML_PER_TBSP) < 0.0001

    def test_fractional_cups(self) -> None:
        """Test fractional cup conversions (common in recipes)."""
        # 0.5 cup = 120 ml
        result = cups_to_ml(0.5)
        assert abs(result - 120.0) < 0.1

    def test_zero_volume(self) -> None:
        """Test edge case: zero volume."""
        assert ml_to_cups(0) == 0.0
        assert cups_to_ml(0) == 0.0
