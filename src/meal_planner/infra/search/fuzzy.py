# ./src/meal_planner/infra/search/fuzzy.py

from __future__ import annotations

from typing import Iterable, List, Tuple

from rapidfuzz import process, fuzz


def best_matches(
    query: str,
    choices: Iterable[str],
    limit: int = 10,
    score_cutoff: int = 50,
    scorer: callable = fuzz.WRatio,
) -> List[Tuple[str, float]]:
    """Return the best fuzzy matches for a query from a list of choices.

    Args:
        query: The search query.
        choices: Iterable of strings to search.
        limit: Maximum number of results to return.
        score_cutoff: Minimum score to include results.
        scorer: RapidFuzz scorer function.

    Returns:
        List of (choice, score) sorted descending by score.
    """

    results = process.extract(
        query,
        choices,
        scorer=scorer,
        limit=limit,
        score_cutoff=score_cutoff,
    )

    # Each result is (choice, score, index)
    return [(choice, score) for choice, score, _ in results]
