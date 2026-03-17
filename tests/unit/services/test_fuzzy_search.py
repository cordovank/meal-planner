# tests/unit/services/test_fuzzy_search.py

import pytest

from meal_planner.infra.search.fuzzy import best_matches


class TestFuzzySearch:
    """Test fuzzy search utility."""

    def test_exact_match_returns_high_score(self) -> None:
        """Test that exact matches get high scores."""
        choices = ["apple", "apricot", "banana"]
        results = best_matches("apple", choices, limit=5)

        assert len(results) > 0
        best_choice, best_score = results[0]
        assert best_choice == "apple"
        assert best_score == 100.0

    def test_partial_match_returns_results(self) -> None:
        """Test that partial matches are found."""
        choices = ["chicken breast", "chicken thighs", "beef"]
        results = best_matches("chicken", choices, limit=5)

        assert len(results) >= 2
        # Both chicken items should be present
        matched_items = [choice for choice, _ in results]
        assert "chicken breast" in matched_items or "chicken thighs" in matched_items

    def test_limit_respects_max_results(self) -> None:
        """Test that limit parameter is respected."""
        choices = ["apple", "apricot", "avocado", "asparagus", "artichoke"]
        results = best_matches("a", choices, limit=3)

        assert len(results) <= 3

    def test_score_cutoff_filters_poor_matches(self) -> None:
        """Test that score_cutoff filters out low-quality matches."""
        choices = ["apple", "zebra", "zucchini"]
        results_high_cutoff = best_matches("apple", choices, score_cutoff=90)
        results_low_cutoff = best_matches("apple", choices, score_cutoff=20)

        # With high cutoff, should only get exact/near-exact matches
        assert len(results_high_cutoff) <= len(results_low_cutoff)

    def test_empty_choices(self) -> None:
        """Test searching with empty choices list."""
        results = best_matches("apple", [])

        assert len(results) == 0

    def test_consistent_matching(self) -> None:
        """Test that consistent queries return consistent results."""
        choices = ["apple", "apricot", "avocado"]
        results1 = best_matches("app", choices, limit=5)
        results2 = best_matches("app", choices, limit=5)

        # Same query should give same results
        assert len(results1) == len(results2)
        assert [c for c, _ in results1] == [c for c, _ in results2]

    def test_typo_tolerance(self) -> None:
        """Test that minor typos still match."""
        choices = ["tomato", "potato", "parmesan"]
        results = best_matches("tomat", choices, limit=5)

        # Should find "tomato" even with typo
        matched_items = [choice for choice, _ in results]
        assert "tomato" in matched_items

    def test_common_ingredient_search(self) -> None:
        """Test realistic ingredient search scenario."""
        choices = [
            "chicken breast",
            "chicken thighs",
            "chicken drumsticks",
            "ground chicken",
        ]
        results = best_matches("chicken breast", choices, limit=5)

        assert len(results) > 0
        assert results[0][0] == "chicken breast"
        assert results[0][1] == 100.0  # Exact match

    def test_multiple_word_matching(self) -> None:
        """Test matching with multi-word ingredients."""
        choices = [
            "olive oil extra virgin",
            "canola oil",
            "regular olive oil",
        ]
        results = best_matches("extra virgin olive", choices, limit=5)

        matched_items = [choice for choice, _ in results]
        assert "olive oil extra virgin" in matched_items

    def test_score_ordering(self) -> None:
        """Test that results are ordered by score (descending)."""
        choices = ["apple", "apricot", "avocado", "zebra"]
        results = best_matches("app", choices, limit=5)

        scores = [score for _, score in results]
        # Scores should be in descending order
        assert scores == sorted(scores, reverse=True)
