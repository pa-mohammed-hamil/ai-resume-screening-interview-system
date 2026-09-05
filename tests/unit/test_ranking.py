# Project scaffold file
```python
import pytest

from ai.ranking.candidate_ranker import CandidateRanker
from ai.ranking.ranking_features import RankingFeatures
from ai.ranking.ranking_explainer import RankingExplainer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def candidates():
    return [
        {
            "id": 1,
            "name": "Alice",
            "match_score": 92,
            "skills_score": 95,
            "experience_score": 90,
            "education_score": 88,
            "ats_score": 94,
        },
        {
            "id": 2,
            "name": "Bob",
            "match_score": 75,
            "skills_score": 78,
            "experience_score": 72,
            "education_score": 80,
            "ats_score": 76,
        },
        {
            "id": 3,
            "name": "Charlie",
            "match_score": 85,
            "skills_score": 88,
            "experience_score": 84,
            "education_score": 82,
            "ats_score": 86,
        },
    ]


@pytest.fixture
def job():
    return {
        "id": 101,
        "title": "Python Backend Developer",
        "required_skills": [
            "Python",
            "FastAPI",
            "SQL",
            "Docker",
        ],
    }


# ---------------------------------------------------------------------------
# Ranking Features
# ---------------------------------------------------------------------------

def test_ranking_features_returns_features():
    features = RankingFeatures()

    candidate = {
        "match_score": 90,
        "skills_score": 95,
        "experience_score": 85,
        "education_score": 80,
        "ats_score": 92,
    }

    result = features.extract(candidate)

    assert result is not None


def test_ranking_features_contains_expected_values():
    features = RankingFeatures()

    candidate = {
        "match_score": 90,
        "skills_score": 95,
        "experience_score": 85,
        "education_score": 80,
        "ats_score": 92,
    }

    result = features.extract(candidate)

    assert result is not None

    if isinstance(result, dict):
        assert "match_score" in result or "matching_score" in result
        assert "skills_score" in result or "skill_score" in result


def test_ranking_features_handles_missing_values():
    features = RankingFeatures()

    candidate = {
        "match_score": 80,
    }

    result = features.extract(candidate)

    assert result is not None


# ---------------------------------------------------------------------------
# Candidate Ranker
# ---------------------------------------------------------------------------

def test_candidate_ranker_returns_ranked_candidates(candidates, job):
    ranker = CandidateRanker()

    result = ranker.rank(
        candidates=candidates,
        job=job,
    )

    assert result is not None
    assert isinstance(result, list)
    assert len(result) == len(candidates)


def test_candidate_ranker_orders_candidates_by_score(candidates, job):
    ranker = CandidateRanker()

    result = ranker.rank(
        candidates=candidates,
        job=job,
    )

    assert result is not None

    scores = []

    for candidate in result:
        if isinstance(candidate, dict):
            score = (
                candidate.get("ranking_score")
                or candidate.get("rank_score")
                or candidate.get("score")
            )

            if score is not None:
                scores.append(score)

    if len(scores) >= 2:
        assert scores == sorted(scores, reverse=True)


def test_highest_scoring_candidate_is_ranked_first(candidates, job):
    ranker = CandidateRanker()

    result = ranker.rank(
        candidates=candidates,
        job=job,
    )

    assert result

    first = result[0]

    if isinstance(first, dict):
        assert (
            first.get("id") == 1
            or first.get("name") == "Alice"
            or first.get("ranking_score", 0) >= 90
        )


def test_candidate_ranker_assigns_rank(candidates, job):
    ranker = CandidateRanker()

    result = ranker.rank(
        candidates=candidates,
        job=job,
    )

    assert result

    ranks = []

    for candidate in result:
        if isinstance(candidate, dict) and "rank" in candidate:
            ranks.append(candidate["rank"])

    if ranks:
        assert ranks == list(range(1, len(ranks) + 1))


# ---------------------------------------------------------------------------
# Ranking Score
# ---------------------------------------------------------------------------

def test_ranking_score_is_valid(candidates, job):
    ranker = CandidateRanker()

    result = ranker.rank(
        candidates=candidates,
        job=job,
    )

    assert result

    for candidate in result:
        if isinstance(candidate, dict):
            score = (
                candidate.get("ranking_score")
                or candidate.get("rank_score")
                or candidate.get("score")
            )

            if score is not None:
                assert isinstance(score, (int, float))
                assert 0 <= score <= 100


def test_strong_candidate_scores_higher_than_weak_candidate(job):
    ranker = CandidateRanker()

    candidates = [
        {
            "id": 1,
            "name": "Strong Candidate",
            "match_score": 95,
            "skills_score": 95,
            "experience_score": 90,
            "education_score": 90,
            "ats_score": 95,
        },
        {
            "id": 2,
            "name": "Weak Candidate",
            "match_score": 40,
            "skills_score": 35,
            "experience_score": 45,
            "education_score": 50,
            "ats_score": 42,
        },
    ]

    result = ranker.rank(
        candidates=candidates,
        job=job,
    )

    assert result
    assert result[0]["id"] == 1


# ---------------------------------------------------------------------------
# Ranking Explainer
# ---------------------------------------------------------------------------

def test_ranking_explainer_returns_explanation():
    explainer = RankingExplainer()

    candidate = {
        "name": "Alice",
        "match_score": 92,
        "skills_score": 95,
        "experience_score": 90,
        "education_score": 88,
        "ats_score": 94,
    }

    result = explainer.explain(candidate)

    assert result is not None


def test_ranking_explainer_identifies_strengths():
    explainer = RankingExplainer()

    candidate = {
        "name": "Alice",
        "match_score": 95,
        "skills_score": 98,
        "experience_score": 94,
        "education_score": 80,
        "ats_score": 96,
    }

    result = explainer.explain(candidate)

    assert result is not None

    if isinstance(result, dict):
        assert (
            "strengths" in result
            or "reasons" in result
            or "explanation" in result
        )


def test_ranking_explainer_handles_weak_candidate():
    explainer = RankingExplainer()

    candidate = {
        "name": "Bob",
        "match_score": 35,
        "skills_score": 30,
        "experience_score": 40,
        "education_score": 45,
        "ats_score": 38,
    }

    result = explainer.explain(candidate)

    assert result is not None


# ---------------------------------------------------------------------------
# Empty / Edge Cases
# ---------------------------------------------------------------------------

def test_ranker_handles_empty_candidates(job):
    ranker = CandidateRanker()

    result = ranker.rank(
        candidates=[],
        job=job,
    )

    assert result == []


def test_ranker_handles_single_candidate(job):
    ranker = CandidateRanker()

    candidate = {
        "id": 1,
        "name": "Alice",
        "match_score": 90,
        "skills_score": 90,
        "experience_score": 90,
        "education_score": 90,
        "ats_score": 90,
    }

    result = ranker.rank(
        candidates=[candidate],
        job=job,
    )

    assert result
    assert len(result) == 1


def test_ranker_handles_missing_scores(job):
    ranker = CandidateRanker()

    candidates = [
        {
            "id": 1,
            "name": "Alice",
        },
        {
            "id": 2,
            "name": "Bob",
            "match_score": 80,
        },
    ]

    result = ranker.rank(
        candidates=candidates,
        job=job,
    )

    assert result is not None
    assert len(result) == 2


def test_ranker_does_not_modify_original_candidates(candidates, job):
    original = [candidate.copy() for candidate in candidates]

    ranker = CandidateRanker()

    ranker.rank(
        candidates=candidates,
        job=job,
    )

    assert candidates == original


# ---------------------------------------------------------------------------
# Ties
# ---------------------------------------------------------------------------

def test_ranker_handles_equal_scores(job):
    ranker = CandidateRanker()

    candidates = [
        {
            "id": 1,
            "name": "Alice",
            "match_score": 80,
            "skills_score": 80,
            "experience_score": 80,
            "education_score": 80,
            "ats_score": 80,
        },
        {
            "id": 2,
            "name": "Bob",
            "match_score": 80,
            "skills_score": 80,
            "experience_score": 80,
            "education_score": 80,
            "ats_score": 80,
        },
    ]

    result = ranker.rank(
        candidates=candidates,
        job=job,
    )

    assert result is not None
    assert len(result) == 2


# ---------------------------------------------------------------------------
# Ranking Stability
# ---------------------------------------------------------------------------

def test_ranking_is_deterministic(candidates, job):
    ranker = CandidateRanker()

    result_one = ranker.rank(
        candidates=candidates,
        job=job,
    )

    result_two = ranker.rank(
        candidates=candidates,
        job=job,
    )

    assert result_one == result_two
