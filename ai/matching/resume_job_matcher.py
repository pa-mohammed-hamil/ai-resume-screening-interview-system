# Project scaffold file
"""
Resume ↔ Job Matcher
=====================

Location:
    ai/matching/resume_job_matcher.py

Purpose:
    Match a candidate resume against a job description using:
        - Skill matching
        - Keyword matching
        - Semantic similarity
        - Skill-gap analysis
        - Experience matching
        - Education matching

The matcher is designed to be:
    - Explainable
    - Deterministic where possible
    - Easy to integrate with candidate ranking
    - Easy to replace with ML/embedding models later
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

from ..skill_intelligence.skill_gap import (
    analyze_skill_gap,
    calculate_weighted_coverage,
)

try:
    from .keyword_matcher import KeywordMatcher
except ImportError:
    KeywordMatcher = None

try:
    from .semantic_matcher import SemanticMatcher
except ImportError:
    SemanticMatcher = None


# ============================================================================
# Constants
# ============================================================================

DEFAULT_SKILL_WEIGHT = 0.40
DEFAULT_KEYWORD_WEIGHT = 0.20
DEFAULT_SEMANTIC_WEIGHT = 0.25
DEFAULT_EXPERIENCE_WEIGHT = 0.10
DEFAULT_EDUCATION_WEIGHT = 0.05

MIN_SCORE = 0.0
MAX_SCORE = 100.0


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class MatchWeights:
    """Weights used to calculate the final match score."""

    skill: float = DEFAULT_SKILL_WEIGHT
    keyword: float = DEFAULT_KEYWORD_WEIGHT
    semantic: float = DEFAULT_SEMANTIC_WEIGHT
    experience: float = DEFAULT_EXPERIENCE_WEIGHT
    education: float = DEFAULT_EDUCATION_WEIGHT

    def validate(self) -> None:
        """Validate that weights form a valid distribution."""

        weights = [
            self.skill,
            self.keyword,
            self.semantic,
            self.experience,
            self.education,
        ]

        if any(weight < 0 for weight in weights):
            raise ValueError(
                "Match weights cannot be negative."
            )

        total = sum(weights)

        if total <= 0:
            raise ValueError(
                "At least one match weight must be greater than zero."
            )

    def normalized(self) -> "MatchWeights":
        """Return normalized weights summing to 1."""

        self.validate()

        total = (
            self.skill
            + self.keyword
            + self.semantic
            + self.experience
            + self.education
        )

        return MatchWeights(
            skill=self.skill / total,
            keyword=self.keyword / total,
            semantic=self.semantic / total,
            experience=self.experience / total,
            education=self.education / total,
        )


@dataclass
class MatchBreakdown:
    """Individual components of a resume-job match."""

    skill_score: float = 0.0
    keyword_score: float = 0.0
    semantic_score: float = 0.0
    experience_score: float = 0.0
    education_score: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "skill_score": self.skill_score,
            "keyword_score": self.keyword_score,
            "semantic_score": self.semantic_score,
            "experience_score": self.experience_score,
            "education_score": self.education_score,
        }


@dataclass
class MatchResult:
    """Complete resume-job matching result."""

    match_score: float

    match_level: str

    breakdown: MatchBreakdown

    matched_skills: list[str] = field(
        default_factory=list
    )

    missing_required_skills: list[str] = field(
        default_factory=list
    )

    missing_preferred_skills: list[str] = field(
        default_factory=list
    )

    matched_keywords: list[str] = field(
        default_factory=list
    )

    missing_keywords: list[str] = field(
        default_factory=list
    )

    related_skills: dict[str, list[str]] = field(
        default_factory=dict
    )

    critical_skill_gaps: list[str] = field(
        default_factory=list
    )

    strengths: list[str] = field(
        default_factory=list
    )

    weaknesses: list[str] = field(
        default_factory=list
    )

    recommendations: list[str] = field(
        default_factory=list
    )

    confidence: float = 0.0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "match_score": self.match_score,
            "match_level": self.match_level,
            "breakdown": self.breakdown.to_dict(),
            "matched_skills": self.matched_skills,
            "missing_required_skills": (
                self.missing_required_skills
            ),
            "missing_preferred_skills": (
                self.missing_preferred_skills
            ),
            "matched_keywords": self.matched_keywords,
            "missing_keywords": self.missing_keywords,
            "related_skills": self.related_skills,
            "critical_skill_gaps": (
                self.critical_skill_gaps
            ),
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "recommendations": self.recommendations,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


# ============================================================================
# General Utilities
# ============================================================================


def _clean_text(value: Any) -> str:
    """Convert a value into normalized text."""

    if value is None:
        return ""

    return " ".join(
        str(value).lower().split()
    )


def _normalize_items(
    items: Iterable[str] | None,
) -> list[str]:
    """Normalize a collection of strings."""

    if not items:
        return []

    result: list[str] = []

    for item in items:
        value = _clean_text(item)

        if value and value not in result:
            result.append(value)

    return result


def _clamp_score(score: float) -> float:
    """Keep score within 0-100."""

    return round(
        max(
            MIN_SCORE,
            min(MAX_SCORE, float(score)),
        ),
        2,
    )


def _safe_ratio(
    numerator: float,
    denominator: float,
) -> float:
    """Calculate a ratio safely."""

    if denominator <= 0:
        return 1.0

    return numerator / denominator


# ============================================================================
# Keyword Matching
# ============================================================================


def basic_keyword_match(
    resume_text: str,
    job_text: str,
    keywords: Iterable[str] | None = None,
) -> tuple[list[str], list[str], float]:
    """
    Perform simple keyword matching.

    If keywords are provided, those are used as the required
    keyword set. Otherwise an empty keyword result is returned.
    """

    resume = _clean_text(resume_text)

    keyword_list = _normalize_items(
        keywords
    )

    if not keyword_list:
        return [], [], 100.0

    matched: list[str] = []
    missing: list[str] = []

    for keyword in keyword_list:

        if keyword in resume:
            matched.append(keyword)
        else:
            missing.append(keyword)

    score = (
        _safe_ratio(
            len(matched),
            len(keyword_list),
        )
        * 100
    )

    return (
        matched,
        missing,
        _clamp_score(score),
    )


def _run_keyword_matcher(
    resume_text: str,
    job_text: str,
    keywords: Iterable[str] | None,
) -> tuple[list[str], list[str], float]:
    """Use the project's KeywordMatcher when available."""

    if KeywordMatcher is None:
        return basic_keyword_match(
            resume_text,
            job_text,
            keywords,
        )

    try:
        matcher = KeywordMatcher()

        # Support common matcher APIs.
        if hasattr(matcher, "match"):
            result = matcher.match(
                resume_text,
                job_text,
                keywords=keywords,
            )

        elif hasattr(matcher, "calculate_score"):
            score = matcher.calculate_score(
                resume_text,
                job_text,
            )

            return [], [], _clamp_score(
                float(score)
            )

        else:
            return basic_keyword_match(
                resume_text,
                job_text,
                keywords,
            )

        if isinstance(result, Mapping):

            matched = _normalize_items(
                result.get("matched_keywords", [])
            )

            missing = _normalize_items(
                result.get("missing_keywords", [])
            )

            score = result.get(
                "score",
                result.get(
                    "keyword_score",
                    0,
                ),
            )

            return (
                matched,
                missing,
                _clamp_score(
                    float(score)
                ),
            )

    except Exception:
        # Matching should not break the complete pipeline
        # because of an optional matcher implementation.
        pass

    return basic_keyword_match(
        resume_text,
        job_text,
        keywords,
    )


# ============================================================================
# Semantic Matching
# ============================================================================


def _token_similarity(
    text_a: str,
    text_b: str,
) -> float:
    """
    Lightweight fallback semantic similarity.

    This is intentionally simple and deterministic.
    A production system can replace it with embeddings.
    """

    tokens_a = set(
        _clean_text(text_a).split()
    )

    tokens_b = set(
        _clean_text(text_b).split()
    )

    if not tokens_a or not tokens_b:
        return 0.0

    intersection = (
        tokens_a & tokens_b
    )

    union = (
        tokens_a | tokens_b
    )

    return (
        len(intersection)
        / len(union)
        * 100
    )


def _run_semantic_matcher(
    resume_text: str,
    job_text: str,
) -> float:
    """Run semantic matcher with a safe fallback."""

    if SemanticMatcher is not None:

        try:
            matcher = SemanticMatcher()

            if hasattr(
                matcher,
                "similarity",
            ):
                score = matcher.similarity(
                    resume_text,
                    job_text,
                )

                return _clamp_score(
                    float(score)
                )

            if hasattr(
                matcher,
                "match",
            ):
                result = matcher.match(
                    resume_text,
                    job_text,
                )

                if isinstance(
                    result,
                    Mapping,
                ):
                    score = result.get(
                        "score",
                        result.get(
                            "semantic_score",
                            0,
                        ),
                    )

                    return _clamp_score(
                        float(score)
                    )

                if isinstance(
                    result,
                    (int, float),
                ):
                    return _clamp_score(
                        float(result)
                    )

        except Exception:
            pass

    return _clamp_score(
        _token_similarity(
            resume_text,
            job_text,
        )
    )


# ============================================================================
# Experience Matching
# ============================================================================


def calculate_experience_score(
    candidate_years: float | int | None,
    required_years: float | int | None,
) -> float:
    """
    Calculate experience compatibility.

    Rules:
        candidate >= required -> 100
        candidate == 0         -> 0
        otherwise proportional
    """

    if required_years is None:
        return 100.0

    try:
        candidate = max(
            0.0,
            float(
                candidate_years or 0
            ),
        )

        required = max(
            0.0,
            float(required_years),
        )

    except (
        TypeError,
        ValueError,
    ):
        return 100.0

    if required == 0:
        return 100.0

    if candidate >= required:
        return 100.0

    return _clamp_score(
        (candidate / required)
        * 100
    )


# ============================================================================
# Education Matching
# ============================================================================


def calculate_education_score(
    candidate_education: str | None,
    required_education: str | None,
) -> float:
    """
    Calculate education compatibility.

    Uses simple normalized text matching as a safe baseline.
    """

    required = _clean_text(
        required_education
    )

    candidate = _clean_text(
        candidate_education
    )

    if not required:
        return 100.0

    if not candidate:
        return 0.0

    if required in candidate:
        return 100.0

    candidate_tokens = set(
        candidate.split()
    )

    required_tokens = set(
        required.split()
    )

    if not required_tokens:
        return 100.0

    overlap = (
        candidate_tokens
        & required_tokens
    )

    return _clamp_score(
        (
            len(overlap)
            / len(required_tokens)
        )
        * 100
    )


# ============================================================================
# Skill Matching
# ============================================================================


def calculate_skill_score(
    candidate_skills: Iterable[str],
    required_skills: Iterable[str],
) -> float:
    """
    Calculate weighted skill score.

    Uses skill importance from the skill taxonomy.
    """

    return _clamp_score(
        calculate_weighted_coverage(
            candidate_skills,
            required_skills,
        )
    )


def analyze_skills(
    candidate_skills: Iterable[str],
    required_skills: Iterable[str],
    preferred_skills: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Perform detailed skill analysis."""

    report = analyze_skill_gap(
        candidate_skills=candidate_skills,
        required_skills=required_skills,
        preferred_skills=preferred_skills or [],
    )

    return report.to_dict()


# ============================================================================
# Strength / Weakness Detection
# ============================================================================


def _build_strengths(
    skill_score: float,
    keyword_score: float,
    semantic_score: float,
    experience_score: float,
    education_score: float,
    matched_skills: Sequence[str],
) -> list[str]:
    """Generate positive match explanations."""

    strengths: list[str] = []

    if skill_score >= 80:
        strengths.append(
            "Strong coverage of required skills."
        )
    elif skill_score >= 60:
        strengths.append(
            "Good coverage of required skills."
        )

    if keyword_score >= 80:
        strengths.append(
            "Strong keyword alignment with the job."
        )

    if semantic_score >= 80:
        strengths.append(
            "Resume content is highly relevant to the job."
        )

    if experience_score >= 90:
        strengths.append(
            "Experience level meets or exceeds the requirement."
        )

    if education_score >= 90:
        strengths.append(
            "Education background aligns with the job requirement."
        )

    if matched_skills:
        strengths.append(
            f"{len(matched_skills)} required skills matched."
        )

    return strengths


def _build_weaknesses(
    skill_score: float,
    keyword_score: float,
    semantic_score: float,
    experience_score: float,
    education_score: float,
    missing_required_skills: Sequence[str],
) -> list[str]:
    """Generate negative match explanations."""

    weaknesses: list[str] = []

    if skill_score < 60:
        weaknesses.append(
            "Significant required-skill gaps were detected."
        )
    elif skill_score < 80:
        weaknesses.append(
            "Some required skills are missing."
        )

    if keyword_score < 60:
        weaknesses.append(
            "Resume has limited keyword alignment with the job."
        )

    if semantic_score < 60:
        weaknesses.append(
            "Resume content has limited semantic relevance to the job."
        )

    if experience_score < 60:
        weaknesses.append(
            "Candidate experience is below the stated requirement."
        )

    if education_score < 60:
        weaknesses.append(
            "Education background has limited alignment."
        )

    if missing_required_skills:
        weaknesses.append(
            f"{len(missing_required_skills)} required skills are missing."
        )

    return weaknesses


# ============================================================================
# Match Level
# ============================================================================


def get_match_level(
    score: float,
) -> str:
    """Convert numeric score to a human-readable level."""

    score = _clamp_score(score)

    if score >= 90:
        return "excellent"

    if score >= 80:
        return "strong"

    if score >= 70:
        return "good"

    if score >= 60:
        return "moderate"

    if score >= 40:
        return "weak"

    return "poor"


# ============================================================================
# Confidence
# ============================================================================


def calculate_confidence(
    *,
    resume_text_available: bool,
    job_text_available: bool,
    candidate_skills_available: bool,
    required_skills_available: bool,
) -> float:
    """
    Estimate confidence in the match result.

    This is NOT a probability of candidate quality.
    It indicates how complete the available matching inputs are.
    """

    signals = [
        resume_text_available,
        job_text_available,
        candidate_skills_available,
        required_skills_available,
    ]

    available = sum(
        bool(signal)
        for signal in signals
    )

    return _clamp_score(
        (
            available
            / len(signals)
        )
        * 100
    )


# ============================================================================
# Recommendations
# ============================================================================


def _generate_recommendations(
    missing_required_skills: Sequence[str],
    missing_preferred_skills: Sequence[str],
    related_skills: Mapping[str, Sequence[str]],
    experience_score: float,
    keyword_score: float,
) -> list[str]:
    """Generate actionable recommendations."""

    recommendations: list[str] = []

    for skill in missing_required_skills[:5]:

        related = related_skills.get(
            skill,
            [],
        )

        if related:
            recommendations.append(
                f"Strengthen {skill} using related "
                f"experience: {', '.join(related)}."
            )
        else:
            recommendations.append(
                f"Build demonstrable experience with {skill} "
                "if genuinely applicable."
            )

    if missing_preferred_skills:
        recommendations.append(
            "Consider highlighting preferred skills: "
            + ", ".join(
                missing_preferred_skills[:5]
            )
            + "."
        )

    if experience_score < 70:
        recommendations.append(
            "Highlight projects, internships, or "
            "relevant practical experience that demonstrate "
            "job-related capabilities."
        )

    if keyword_score < 70:
        recommendations.append(
            "Improve resume terminology to accurately "
            "reflect skills and responsibilities already "
            "supported by the candidate's experience."
        )

    return list(
        dict.fromkeys(
            recommendations
        )
    )


# ============================================================================
# Main Matcher
# ============================================================================


class ResumeJobMatcher:
    """
    Main resume-job matching service.

    Example:

        matcher = ResumeJobMatcher()

        result = matcher.match(
            resume_text=resume_text,
            job_text=job_text,
            candidate_skills=[
                "Python",
                "FastAPI",
                "PostgreSQL",
            ],
            required_skills=[
                "Python",
                "FastAPI",
                "Docker",
                "AWS",
            ],
            preferred_skills=[
                "Kubernetes",
            ],
            candidate_years=2,
            required_years=2,
            candidate_education="B.Tech Computer Science",
            required_education="Computer Science",
        )
    """

    def __init__(
        self,
        weights: MatchWeights | None = None,
    ) -> None:

        self.weights = (
            weights
            or MatchWeights()
        ).normalized()

    # ----------------------------------------------------------------------
    # Match
    # ----------------------------------------------------------------------

    def match(
        self,
        *,
        resume_text: str = "",
        job_text: str = "",
        candidate_skills: Iterable[str] | None = None,
        required_skills: Iterable[str] | None = None,
        preferred_skills: Iterable[str] | None = None,
        keywords: Iterable[str] | None = None,
        candidate_years: float | int | None = None,
        required_years: float | int | None = None,
        candidate_education: str | None = None,
        required_education: str | None = None,
    ) -> MatchResult:
        """Calculate a complete resume-job match."""

        candidate_skills = (
            _normalize_items(
                candidate_skills
            )
        )

        required_skills = (
            _normalize_items(
                required_skills
            )
        )

        preferred_skills = (
            _normalize_items(
                preferred_skills
            )
        )

        # --------------------------------------------------------------
        # Skill analysis
        # --------------------------------------------------------------

        skill_report = analyze_skill_gap(
            candidate_skills=candidate_skills,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
        )

        skill_score = _clamp_score(
            skill_report.weighted_score
        )

        # --------------------------------------------------------------
        # Keyword analysis
        # --------------------------------------------------------------

        (
            matched_keywords,
            missing_keywords,
            keyword_score,
        ) = _run_keyword_matcher(
            resume_text,
            job_text,
            keywords,
        )

        # --------------------------------------------------------------
        # Semantic analysis
        # --------------------------------------------------------------

        semantic_score = _run_semantic_matcher(
            resume_text,
            job_text,
        )

        # --------------------------------------------------------------
        # Experience
        # --------------------------------------------------------------

        experience_score = (
            calculate_experience_score(
                candidate_years,
                required_years,
            )
        )

        # --------------------------------------------------------------
        # Education
        # --------------------------------------------------------------

        education_score = (
            calculate_education_score(
                candidate_education,
                required_education,
            )
        )

        # --------------------------------------------------------------
        # Weighted final score
        # --------------------------------------------------------------

        final_score = (
            skill_score
            * self.weights.skill
            + keyword_score
            * self.weights.keyword
            + semantic_score
            * self.weights.semantic
            + experience_score
            * self.weights.experience
            + education_score
            * self.weights.education
        )

        final_score = _clamp_score(
            final_score
        )

        # --------------------------------------------------------------
        # Match level
        # --------------------------------------------------------------

        match_level = get_match_level(
            final_score
        )

        # --------------------------------------------------------------
        # Strengths
        # --------------------------------------------------------------

        strengths = _build_strengths(
            skill_score,
            keyword_score,
            semantic_score,
            experience_score,
            education_score,
            skill_report.matched_required,
        )

        # --------------------------------------------------------------
        # Weaknesses
        # --------------------------------------------------------------

        weaknesses = _build_weaknesses(
            skill_score,
            keyword_score,
            semantic_score,
            experience_score,
            education_score,
            [
                gap.skill
                for gap
                in skill_report.missing_required
            ],
        )

        # --------------------------------------------------------------
        # Recommendations
        # --------------------------------------------------------------

        recommendations = (
            _generate_recommendations(
                missing_required_skills=[
                    gap.skill
                    for gap
                    in skill_report.missing_required
                ],
                missing_preferred_skills=[
                    gap.skill
                    for gap
                    in skill_report.missing_preferred
                ],
                related_skills=(
                    skill_report.related_matches
                ),
                experience_score=experience_score,
                keyword_score=keyword_score,
            )
        )

        # --------------------------------------------------------------
        # Confidence
        # --------------------------------------------------------------

        confidence = calculate_confidence(
            resume_text_available=bool(
                resume_text.strip()
            ),
            job_text_available=bool(
                job_text.strip()
            ),
            candidate_skills_available=bool(
                candidate_skills
            ),
            required_skills_available=bool(
                required_skills
            ),
        )

        # --------------------------------------------------------------
        # Result
        # --------------------------------------------------------------

        return MatchResult(
            match_score=final_score,
            match_level=match_level,
            breakdown=MatchBreakdown(
                skill_score=skill_score,
                keyword_score=keyword_score,
                semantic_score=semantic_score,
                experience_score=experience_score,
                education_score=education_score,
            ),
            matched_skills=(
                skill_report.matched_required
            ),
            missing_required_skills=[
                gap.skill
                for gap
                in skill_report.missing_required
            ],
            missing_preferred_skills=[
                gap.skill
                for gap
                in skill_report.missing_preferred
            ],
            matched_keywords=matched_keywords,
            missing_keywords=missing_keywords,
            related_skills=(
                skill_report.related_matches
            ),
            critical_skill_gaps=(
                skill_report.critical_gaps
            ),
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            confidence=confidence,
            metadata={
                "required_skill_count": len(
                    required_skills
                ),
                "candidate_skill_count": len(
                    candidate_skills
                ),
                "preferred_skill_count": len(
                    preferred_skills
                ),
                "weights": {
                    "skill": self.weights.skill,
                    "keyword": self.weights.keyword,
                    "semantic": self.weights.semantic,
                    "experience": self.weights.experience,
                    "education": self.weights.education,
                },
            },
        )


# ============================================================================
# Functional API
# ============================================================================


def match_resume_to_job(
    *,
    resume_text: str = "",
    job_text: str = "",
    candidate_skills: Iterable[str] | None = None,
    required_skills: Iterable[str] | None = None,
    preferred_skills: Iterable[str] | None = None,
    keywords: Iterable[str] | None = None,
    candidate_years: float | int | None = None,
    required_years: float | int | None = None,
    candidate_education: str | None = None,
    required_education: str | None = None,
    weights: MatchWeights | None = None,
) -> MatchResult:
    """
    Convenience function for resume-job matching.
    """

    matcher = ResumeJobMatcher(
        weights=weights
    )

    return matcher.match(
        resume_text=resume_text,
        job_text=job_text,
        candidate_skills=candidate_skills,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        keywords=keywords,
        candidate_years=candidate_years,
        required_years=required_years,
        candidate_education=candidate_education,
        required_education=required_education,
    )


# ============================================================================
# Ranking Helper
# ============================================================================


def calculate_match_score(
    candidate_skills: Iterable[str],
    required_skills: Iterable[str],
    preferred_skills: Iterable[str] | None = None,
) -> float:
    """
    Lightweight matching function for candidate ranking.

    Useful when the ranking pipeline only needs a skill-fit score.
    """

    report = analyze_skill_gap(
        candidate_skills=candidate_skills,
        required_skills=required_skills,
        preferred_skills=preferred_skills or [],
    )

    return _clamp_score(
        report.overall_coverage
    )


def compare_candidates(
    candidates: Sequence[Mapping[str, Any]],
    required_skills: Iterable[str],
    preferred_skills: Iterable[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Score and sort multiple candidates by skill match.

    Expected candidate format:

        {
            "id": 1,
            "name": "Candidate",
            "skills": ["Python", "FastAPI"]
        }
    """

    results: list[dict[str, Any]] = []

    for candidate in candidates:

        skills = candidate.get(
            "skills",
            [],
        )

        score = calculate_match_score(
            candidate_skills=skills,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
        )

        results.append(
            {
                **dict(candidate),
                "match_score": score,
                "match_level": get_match_level(
                    score
                ),
            }
        )

    results.sort(
        key=lambda item: item[
            "match_score"
        ],
        reverse=True,
    )

    return results


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "MatchWeights",
    "MatchBreakdown",
    "MatchResult",
    "ResumeJobMatcher",
    "match_resume_to_job",
    "calculate_match_score",
    "compare_candidates",
    "calculate_experience_score",
    "calculate_education_score",
    "calculate_skill_score",
    "analyze_skills",
    "get_match_level",
]