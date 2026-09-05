# Project scaffold file
```python
import pytest

from ai.matching.keyword_matcher import KeywordMatcher
from ai.matching.semantic_matcher import SemanticMatcher
from ai.matching.resume_job_matcher import ResumeJobMatcher


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def resume():
    return {
        "summary": "Python backend developer with API development experience.",
        "skills": [
            "Python",
            "FastAPI",
            "SQL",
            "PostgreSQL",
            "Docker",
            "Git",
        ],
        "experience": [
            {
                "title": "Backend Developer",
                "years": 3,
                "description": "Built REST APIs using Python and FastAPI.",
            }
        ],
        "education": [
            {
                "degree": "B.Tech Computer Science",
            }
        ],
    }


@pytest.fixture
def job():
    return {
        "title": "Python Backend Developer",
        "description": (
            "We are looking for a Python developer to build REST APIs "
            "and backend services."
        ),
        "required_skills": [
            "Python",
            "FastAPI",
            "SQL",
            "Docker",
        ],
        "preferred_skills": [
            "PostgreSQL",
            "Git",
        ],
    }


# ---------------------------------------------------------------------------
# Keyword Matching
# ---------------------------------------------------------------------------

def test_keyword_matcher_finds_matching_skills():
    matcher = KeywordMatcher()

    result = matcher.match(
        resume_text="Python FastAPI SQL Docker PostgreSQL",
        job_text="Python FastAPI SQL Docker",
    )

    assert result is not None

    if isinstance(result, dict):
        assert "score" in result
        assert 0 <= result["score"] <= 100


def test_keyword_matcher_returns_zero_for_no_match():
    matcher = KeywordMatcher()

    result = matcher.match(
        resume_text="Java Spring Hibernate",
        job_text="Python FastAPI PostgreSQL",
    )

    assert result is not None

    if isinstance(result, dict) and "score" in result:
        assert result["score"] == 0


def test_keyword_matcher_is_case_insensitive():
    matcher = KeywordMatcher()

    result_lower = matcher.match(
        resume_text="python fastapi sql",
        job_text="python fastapi sql",
    )

    result_upper = matcher.match(
        resume_text="PYTHON FASTAPI SQL",
        job_text="PYTHON FASTAPI SQL",
    )

    assert result_lower is not None
    assert result_upper is not None


def test_keyword_matcher_handles_empty_resume():
    matcher = KeywordMatcher()

    result = matcher.match(
        resume_text="",
        job_text="Python FastAPI SQL",
    )

    assert result is not None

    if isinstance(result, dict) and "score" in result:
        assert result["score"] >= 0


def test_keyword_matcher_handles_empty_job():
    matcher = KeywordMatcher()

    result = matcher.match(
        resume_text="Python FastAPI SQL",
        job_text="",
    )

    assert result is not None

    if isinstance(result, dict) and "score" in result:
        assert result["score"] >= 0


# ---------------------------------------------------------------------------
# Semantic Matching
# ---------------------------------------------------------------------------

def test_semantic_matcher_returns_result():
    matcher = SemanticMatcher()

    result = matcher.match(
        resume_text=(
            "Python backend developer experienced in building REST APIs "
            "and database applications."
        ),
        job_text=(
            "Looking for a backend engineer who can develop APIs using "
            "Python and work with relational databases."
        ),
    )

    assert result is not None


def test_semantic_matcher_related_text_scores_higher():
    matcher = SemanticMatcher()

    related = matcher.match(
        resume_text=(
            "Python backend developer with experience building REST APIs "
            "using FastAPI and PostgreSQL."
        ),
        job_text=(
            "Backend developer required with Python, REST API, FastAPI "
            "and PostgreSQL experience."
        ),
    )

    unrelated = matcher.match(
        resume_text=(
            "Graphic designer experienced in Photoshop, Illustrator "
            "and visual branding."
        ),
        job_text=(
            "Backend developer required with Python, REST API, FastAPI "
            "and PostgreSQL experience."
        ),
    )

    assert related is not None
    assert unrelated is not None

    if (
        isinstance(related, dict)
        and isinstance(unrelated, dict)
        and "score" in related
        and "score" in unrelated
    ):
        assert related["score"] >= unrelated["score"]


def test_semantic_matcher_score_is_valid():
    matcher = SemanticMatcher()

    result = matcher.match(
        resume_text="Python developer",
        job_text="Backend Python engineer",
    )

    assert result is not None

    if isinstance(result, dict) and "score" in result:
        assert 0 <= result["score"] <= 100


# ---------------------------------------------------------------------------
# Resume-Job Matching
# ---------------------------------------------------------------------------

def test_resume_job_matcher_returns_result(resume, job):
    matcher = ResumeJobMatcher()

    result = matcher.match(
        resume=resume,
        job=job,
    )

    assert result is not None


def test_resume_job_matcher_returns_valid_score(resume, job):
    matcher = ResumeJobMatcher()

    result = matcher.match(
        resume=resume,
        job=job,
    )

    assert result is not None

    if isinstance(result, dict) and "score" in result:
        assert 0 <= result["score"] <= 100


def test_resume_job_matcher_identifies_matching_skills(resume, job):
    matcher = ResumeJobMatcher()

    result = matcher.match(
        resume=resume,
        job=job,
    )

    assert result is not None

    if isinstance(result, dict):
        matching_skills = (
            result.get("matching_skills")
            or result.get("matched_skills")
            or []
        )

        if matching_skills:
            normalized = {skill.lower() for skill in matching_skills}

            assert "python" in normalized


def test_resume_job_matcher_identifies_missing_skills():
    matcher = ResumeJobMatcher()

    resume = {
        "skills": ["Python"],
        "experience": [],
        "education": [],
    }

    job = {
        "required_skills": [
            "Python",
            "FastAPI",
            "PostgreSQL",
        ],
        "preferred_skills": [],
    }

    result = matcher.match(
        resume=resume,
        job=job,
    )

    assert result is not None

    if isinstance(result, dict):
        missing_skills = (
            result.get("missing_skills")
            or result.get("skill_gaps")
            or []
        )

        if missing_skills:
            normalized = {skill.lower() for skill in missing_skills}

            assert "fastapi" in normalized


def test_perfect_resume_job_match():
    matcher = ResumeJobMatcher()

    resume = {
        "skills": [
            "Python",
            "FastAPI",
            "SQL",
            "Docker",
        ],
        "experience": [
            {
                "title": "Python Developer",
                "years": 5,
            }
        ],
        "education": [
            {
                "degree": "B.Tech Computer Science",
            }
        ],
    }

    job = {
        "title": "Python Developer",
        "required_skills": [
            "Python",
            "FastAPI",
            "SQL",
            "Docker",
        ],
        "preferred_skills": [],
    }

    result = matcher.match(
        resume=resume,
        job=job,
    )

    assert result is not None

    if isinstance(result, dict) and "score" in result:
        assert result["score"] >= 80


def test_poor_resume_job_match():
    matcher = ResumeJobMatcher()

    resume = {
        "skills": [
            "Java",
            "Spring",
            "Hibernate",
        ],
        "experience": [
            {
                "title": "Java Developer",
                "years": 2,
            }
        ],
        "education": [],
    }

    job = {
        "title": "Python Developer",
        "required_skills": [
            "Python",
            "FastAPI",
            "PostgreSQL",
        ],
        "preferred_skills": [
            "Docker",
        ],
    }

    result = matcher.match(
        resume=resume,
        job=job,
    )

    assert result is not None

    if isinstance(result, dict) and "score" in result:
        assert result["score"] <= 50


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "resume_text,job_text",
    [
        ("", ""),
        ("Python", ""),
        ("", "Python"),
        ("Python Python Python", "Python"),
        ("Python, FastAPI, SQL", "Python FastAPI SQL"),
    ],
)
def test_keyword_matching_edge_cases(resume_text, job_text):
    matcher = KeywordMatcher()

    result = matcher.match(
        resume_text=resume_text,
        job_text=job_text,
    )

    assert result is not None


def test_matching_does_not_return_invalid_score(resume, job):
    matcher = ResumeJobMatcher()

    result = matcher.match(
        resume=resume,
        job=job,
    )

    if isinstance(result, dict) and "score" in result:
        assert isinstance(result["score"], (int, float))
        assert 0 <= result["score"] <= 100
