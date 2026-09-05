# Project scaffold file
```python
"""
Fairness evaluation tests for the AI resume screening system.

These tests are intentionally written around observable scoring/ranking
behavior rather than protected attributes.

Run:
    pytest tests/evaluation/test_fairness.py -v
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def demographic_parity_difference(
    group_a_scores: list[float],
    group_b_scores: list[float],
    threshold: float = 70.0,
) -> float:
    """Difference in selection rates between two groups."""

    if not group_a_scores or not group_b_scores:
        raise ValueError("Both groups must contain candidates.")

    rate_a = sum(score >= threshold for score in group_a_scores) / len(
        group_a_scores
    )
    rate_b = sum(score >= threshold for score in group_b_scores) / len(
        group_b_scores
    )

    return abs(rate_a - rate_b)


def selection_rate(
    scores: list[float],
    threshold: float = 70.0,
) -> float:
    """Return the proportion of candidates above the selection threshold."""

    if not scores:
        return 0.0

    return sum(score >= threshold for score in scores) / len(scores)


def average_score_difference(
    group_a_scores: list[float],
    group_b_scores: list[float],
) -> float:
    """Difference between average scores of two groups."""

    if not group_a_scores or not group_b_scores:
        raise ValueError("Both groups must contain candidates.")

    return abs(
        sum(group_a_scores) / len(group_a_scores)
        - sum(group_b_scores) / len(group_b_scores)
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def balanced_candidate_scores():
    """
    Synthetic evaluation data.

    Protected attributes are represented only for evaluation purposes.
    They must NOT be used as ranking features.
    """

    return {
        "group_a": [92, 88, 84, 81, 76, 72, 68, 61],
        "group_b": [91, 87, 85, 80, 77, 73, 67, 60],
    }


@pytest.fixture
def biased_candidate_scores():
    """Synthetic data representing an intentionally biased model."""

    return {
        "group_a": [95, 92, 90, 88, 85, 82, 79, 75],
        "group_b": [65, 62, 60, 58, 55, 52, 49, 45],
    }


# ---------------------------------------------------------------------------
# Selection-rate tests
# ---------------------------------------------------------------------------

def test_selection_rate_is_calculated_correctly():
    scores = [90, 80, 70, 60, 50]

    rate = selection_rate(scores, threshold=70)

    assert rate == pytest.approx(0.6)


def test_demographic_parity_difference_is_low_for_balanced_model(
    balanced_candidate_scores,
):
    difference = demographic_parity_difference(
        balanced_candidate_scores["group_a"],
        balanced_candidate_scores["group_b"],
        threshold=70,
    )

    # Both groups have approximately the same selection rate.
    assert difference <= 0.20


def test_biased_model_is_detected(biased_candidate_scores):
    difference = demographic_parity_difference(
        biased_candidate_scores["group_a"],
        biased_candidate_scores["group_b"],
        threshold=70,
    )

    assert difference > 0.20


# ---------------------------------------------------------------------------
# Score-distribution tests
# ---------------------------------------------------------------------------

def test_average_score_difference_is_small_for_balanced_model(
    balanced_candidate_scores,
):
    difference = average_score_difference(
        balanced_candidate_scores["group_a"],
        balanced_candidate_scores["group_b"],
    )

    assert difference <= 5.0


def test_large_average_score_difference_is_detected(
    biased_candidate_scores,
):
    difference = average_score_difference(
        biased_candidate_scores["group_a"],
        biased_candidate_scores["group_b"],
    )

    assert difference > 5.0


# ---------------------------------------------------------------------------
# Ranking fairness
# ---------------------------------------------------------------------------

def rank_candidates(candidates):
    """Rank candidates by model score only."""

    return sorted(
        candidates,
        key=lambda candidate: candidate["score"],
        reverse=True,
    )


def test_ranking_does_not_depend_on_protected_attribute():
    candidates = [
        {
            "id": "candidate-1",
            "score": 91,
            "protected_attribute": "A",
        },
        {
            "id": "candidate-2",
            "score": 88,
            "protected_attribute": "B",
        },
        {
            "id": "candidate-3",
            "score": 84,
            "protected_attribute": "A",
        },
        {
            "id": "candidate-4",
            "score": 80,
            "protected_attribute": "B",
        },
    ]

    ranked = rank_candidates(candidates)

    assert [candidate["id"] for candidate in ranked] == [
        "candidate-1",
        "candidate-2",
        "candidate-3",
        "candidate-4",
    ]


def test_same_score_produces_same_rank_regardless_of_group():
    candidates_a = [
        {"id": "a", "score": 85, "protected_attribute": "A"},
        {"id": "b", "score": 85, "protected_attribute": "B"},
    ]

    candidates_b = [
        {"id": "a", "score": 85, "protected_attribute": "B"},
        {"id": "b", "score": 85, "protected_attribute": "A"},
    ]

    ranking_a = rank_candidates(candidates_a)
    ranking_b = rank_candidates(candidates_b)

    assert [
        candidate["score"] for candidate in ranking_a
    ] == [
        candidate["score"] for candidate in ranking_b
    ]


# ---------------------------------------------------------------------------
# Protected-attribute leakage tests
# ---------------------------------------------------------------------------

def test_protected_attributes_are_not_used_by_ranker():
    """
    Verify that changing the protected attribute alone does not change
    the candidate's score.
    """

    candidate = {
        "skills": ["Python", "FastAPI", "PostgreSQL"],
        "experience_years": 5,
        "education": "Bachelor",
    }

    candidate_group_a = {
        **candidate,
        "protected_attribute": "A",
    }

    candidate_group_b = {
        **candidate,
        "protected_attribute": "B",
    }

    # Replace this with the real CandidateRanker in the application.
    def mock_score(candidate_data):
        return (
            len(candidate_data["skills"]) * 20
            + candidate_data["experience_years"] * 5
        )

    score_a = mock_score(candidate_group_a)
    score_b = mock_score(candidate_group_b)

    assert score_a == score_b


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def test_empty_group_raises_error():
    with pytest.raises(ValueError):
        demographic_parity_difference(
            [],
            [80, 75, 70],
        )


def test_empty_score_group_returns_zero_selection_rate():
    assert selection_rate([]) == 0.0


# ---------------------------------------------------------------------------
# Fairness threshold
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "threshold",
    [60, 70, 80, 90],
)
def test_selection_rate_is_between_zero_and_one(
    balanced_candidate_scores,
    threshold,
):
    for scores in balanced_candidate_scores.values():
        rate = selection_rate(scores, threshold)

        assert 0.0 <= rate <= 1.0
