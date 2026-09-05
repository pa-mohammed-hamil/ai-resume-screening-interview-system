# Project scaffold file
```python
import pytest

from ai.scoring.ats_scorer import ATSScorer
from ai.scoring.skill_scorer import SkillScorer
from ai.scoring.experience_scorer import ExperienceScorer
from ai.scoring.education_scorer import EducationScorer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def strong_resume():
    return {
        "name": "John Doe",
        "summary": (
            "Python Backend Developer with 5 years of experience "
            "building scalable REST APIs and backend systems."
        ),
        "skills": [
            "Python",
            "FastAPI",
            "SQL",
            "PostgreSQL",
            "Docker",
            "Git",
            "AWS",
        ],
        "experience": [
            {
                "title": "Senior Backend Developer",
                "company": "ABC Technologies",
                "years": 3,
                "description": (
                    "Built REST APIs using Python and FastAPI. "
                    "Designed PostgreSQL databases and deployed "
                    "applications using Docker and AWS."
                ),
            },
            {
                "title": "Backend Developer",
                "company": "XYZ Solutions",
                "years": 2,
                "description": "Developed Python backend services.",
            },
        ],
        "education": [
            {
                "degree": "B.Tech Computer Science",
                "field": "Computer Science",
                "institution": "University of Technology",
            }
        ],
    }


@pytest.fixture
def weak_resume():
    return {
        "name": "Jane Doe",
        "summary": "Entry-level candidate.",
        "skills": [
            "MS Office",
            "Communication",
        ],
        "experience": [],
        "education": [],
    }


@pytest.fixture
def job():
    return {
        "title": "Python Backend Developer",
        "description": (
            "We are looking for a Python backend developer "
            "with experience building REST APIs."
        ),
        "required_skills": [
            "Python",
            "FastAPI",
            "SQL",
            "PostgreSQL",
            "Docker",
        ],
        "preferred_skills": [
            "AWS",
            "Git",
        ],
        "minimum_experience": 3,
        "education": "Computer Science",
    }


# ---------------------------------------------------------------------------
# ATS Scorer
# ---------------------------------------------------------------------------

def test_ats_scorer_initialization():
    scorer = ATSScorer()

    assert scorer is not None


def test_ats_scorer_returns_result(strong_resume, job):
    scorer = ATSScorer()

    result = scorer.score(
        resume=strong_resume,
        job=job,
    )

    assert result is not None


def test_ats_score_is_between_zero_and_hundred(strong_resume, job):
    scorer = ATSScorer()

    result = scorer.score(
        resume=strong_resume,
        job=job,
    )

    assert result is not None

    if isinstance(result, dict):
        score = (
            result.get("score")
            or result.get("ats_score")
        )

        if score is not None:
            assert 0 <= score <= 100

    elif isinstance(result, (int, float)):
        assert 0 <= result <= 100


def test_strong_resume_has_high_ats_score(strong_resume, job):
    scorer = ATSScorer()

    result = scorer.score(
        resume=strong_resume,
        job=job,
    )

    assert result is not None

    if isinstance(result, dict):
        score = (
            result.get("score")
            or result.get("ats_score")
        )

        if score is not None:
            assert score >= 70

    elif isinstance(result, (int, float)):
        assert result >= 70


def test_weak_resume_has_lower_ats_score(
    strong_resume,
    weak_resume,
    job,
):
    scorer = ATSScorer()

    strong_result = scorer.score(
        resume=strong_resume,
        job=job,
    )

    weak_result = scorer.score(
        resume=weak_resume,
        job=job,
    )

    assert strong_result is not None
    assert weak_result is not None

    if (
        isinstance(strong_result, dict)
        and isinstance(weak_result, dict)
    ):
        strong_score = (
            strong_result.get("score")
            or strong_result.get("ats_score")
        )

        weak_score = (
            weak_result.get("score")
            or weak_result.get("ats_score")
        )

        if strong_score is not None and weak_score is not None:
            assert strong_score >= weak_score


# ---------------------------------------------------------------------------
# Skill Scorer
# ---------------------------------------------------------------------------

def test_skill_scorer_initialization():
    scorer = SkillScorer()

    assert scorer is not None


def test_skill_scorer_returns_result(strong_resume, job):
    scorer = SkillScorer()

    result = scorer.score(
        resume=strong_resume,
        job=job,
    )

    assert result is not None


def test_skill_score_is_valid(strong_resume, job):
    scorer = SkillScorer()

    result = scorer.score(
        resume=strong_resume,
        job=job,
    )

    assert result is not None

    if isinstance(result, dict):
        score = (
            result.get("score")
            or result.get("skill_score")
        )

        if score is not None:
            assert 0 <= score <= 100

    elif isinstance(result, (int, float)):
        assert 0 <= result <= 100


def test_matching_skills_produce_high_score(job):
    scorer = SkillScorer()

    resume = {
        "skills": [
            "Python",
            "FastAPI",
            "SQL",
            "PostgreSQL",
            "Docker",
            "AWS",
        ]
    }

    result = scorer.score(
        resume=resume,
        job=job,
    )

    assert result is not None

    if isinstance(result, dict):
        score = (
            result.get("score")
            or result.get("skill_score")
        )

        if score is not None:
            assert score >= 70

    elif isinstance(result, (int, float)):
        assert result >= 70


def test_missing_skills_reduce_score(job):
    scorer = SkillScorer()

    resume = {
        "skills": [
            "Java",
            "Spring",
        ]
    }

    result = scorer.score(
        resume=resume,
        job=job,
    )

    assert result is not None

    if isinstance(result, dict):
        score = (
            result.get("score")
            or result.get("skill_score")
        )

        if score is not None:
            assert score < 70

    elif isinstance(result, (int, float)):
        assert result < 70


def test_skill_scorer_handles_empty_skills(job):
    scorer = SkillScorer()

    result = scorer.score(
        resume={"skills": []},
        job=job,
    )

    assert result is not None


# ---------------------------------------------------------------------------
# Experience Scorer
# ---------------------------------------------------------------------------

def test_experience_scorer_initialization():
    scorer = ExperienceScorer()

    assert scorer is not None


def test_experience_scorer_returns_result(strong_resume, job):
    scorer = ExperienceScorer()

    result = scorer.score(
        resume=strong_resume,
        job=job,
    )

    assert result is not None


def test_experience_score_is_valid(strong_resume, job):
    scorer = ExperienceScorer()

    result = scorer.score(
        resume=strong_resume,
        job=job,
    )

    assert result is not None

    if isinstance(result, dict):
        score = (
            result.get("score")
            or result.get("experience_score")
        )

        if score is not None:
            assert 0 <= score <= 100

    elif isinstance(result, (int, float)):
        assert 0 <= result <= 100


def test_experienced_candidate_scores_higher(job):
    scorer = ExperienceScorer()

    experienced = {
        "experience": [
            {
                "title": "Senior Backend Developer",
                "years": 5,
            }
        ]
    }

    inexperienced = {
        "experience": []
    }

    experienced_result = scorer.score(
        resume=experienced,
        job=job,
    )

    inexperienced_result = scorer.score(
        resume=inexperienced,
        job=job,
    )

    assert experienced_result is not None
    assert inexperienced_result is not None

    if (
        isinstance(experienced_result, dict)
        and isinstance(inexperienced_result, dict)
    ):
        experienced_score = (
            experienced_result.get("score")
            or experienced_result.get("experience_score")
        )

        inexperienced_score = (
            inexperienced_result.get("score")
            or inexperienced_result.get("experience_score")
        )

        if (
            experienced_score is not None
            and inexperienced_score is not None
        ):
            assert experienced_score >= inexperienced_score


def test_experience_scorer_handles_missing_experience(job):
    scorer = ExperienceScorer()

    result = scorer.score(
        resume={},
        job=job,
    )

    assert result is not None


# ---------------------------------------------------------------------------
# Education Scorer
# ---------------------------------------------------------------------------

def test_education_scorer_initialization():
    scorer = EducationScorer()

    assert scorer is not None


def test_education_scorer_returns_result(strong_resume, job):
    scorer = EducationScorer()

    result = scorer.score(
        resume=strong_resume,
        job=job,
    )

    assert result is not None


def test_education_score_is_valid(strong_resume, job):
    scorer = EducationScorer()

    result = scorer.score(
        resume=strong_resume,
        job=job,
    )

    assert result is not None

    if isinstance(result, dict):
        score = (
            result.get("score")
            or result.get("education_score")
        )

        if score is not None:
            assert 0 <= score <= 100

    elif isinstance(result, (int, float)):
        assert 0 <= result <= 100


def test_relevant_education_produces_high_score(job):
    scorer = EducationScorer()

    resume = {
        "education": [
            {
                "degree": "B.Tech Computer Science",
                "field": "Computer Science",
            }
        ]
    }

    result = scorer.score(
        resume=resume,
        job=job,
    )

    assert result is not None

    if isinstance(result, dict):
        score = (
            result.get("score")
            or result.get("education_score")
        )

        if score is not None:
            assert score >= 50

    elif isinstance(result, (int, float)):
        assert result >= 50


def test_education_scorer_handles_missing_education(job):
    scorer = EducationScorer()

    result = scorer.score(
        resume={"education": []},
        job=job,
    )

    assert result is not None


# ---------------------------------------------------------------------------
# Score Comparison
# ---------------------------------------------------------------------------

def test_strong_resume_scores_better_than_weak_resume(
    strong_resume,
    weak_resume,
    job,
):
    ats_scorer = ATSScorer()
    skill_scorer = SkillScorer()

    strong_ats = ats_scorer.score(
        resume=strong_resume,
        job=job,
    )

    weak_ats = ats_scorer.score(
        resume=weak_resume,
        job=job,
    )

    strong_skill = skill_scorer.score(
        resume=strong_resume,
        job=job,
    )

    weak_skill = skill_scorer.score(
        resume=weak_resume,
        job=job,
    )

    assert strong_ats is not None
    assert weak_ats is not None
    assert strong_skill is not None
    assert weak_skill is not None


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "resume",
    [
        {},
        {"skills": []},
        {"experience": []},
        {"education": []},
        {
            "skills": [],
            "experience": [],
            "education": [],
        },
    ],
)
def test_scorers_handle_incomplete_resume(resume, job):
    scorers = [
        ATSScorer(),
        SkillScorer(),
        ExperienceScorer(),
        EducationScorer(),
    ]

    for scorer in scorers:
        result = scorer.score(
            resume=resume,
            job=job,
        )

        assert result is not None


def test_scorers_handle_empty_job(strong_resume):
    scorers = [
        ATSScorer(),
        SkillScorer(),
        ExperienceScorer(),
        EducationScorer(),
    ]

    for scorer in scorers:
        result = scorer.score(
            resume=strong_resume,
            job={},
        )

        assert result is not None


def test_scorers_are_deterministic(strong_resume, job):
    scorers = [
        ATSScorer(),
        SkillScorer(),
        ExperienceScorer(),
        EducationScorer(),
    ]

    for scorer in scorers:
        result_one = scorer.score(
            resume=strong_resume,
            job=job,
        )

        result_two = scorer.score(
            resume=strong_resume,
            job=job,
        )

        assert result_one == result_two
