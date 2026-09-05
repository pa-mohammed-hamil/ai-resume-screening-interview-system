# Project scaffold file
"""
Job Description Scorer
======================

Location:
    ai/jd_analysis/jd_scorer.py

Purpose:
    Score and analyze the quality, completeness, and structure of a
    Job Description (JD).

Pipeline:

    JD
     |
     +--> Requirements
     |
     +--> Responsibilities
     |
     +--> Skills
     |
     +--> Experience
     |
     +--> Education
     |
     +--> Seniority
     |
     v
    JD Score
     |
     +--> Resume/Job Matcher
     +--> Candidate Ranking
     +--> Analytics
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Mapping, Sequence


# ============================================================================
# Constants
# ============================================================================

MAX_SCORE = 100.0
MIN_SCORE = 0.0

WEIGHT_REQUIREMENTS = 0.20
WEIGHT_RESPONSIBILITIES = 0.20
WEIGHT_SKILLS = 0.20
WEIGHT_EXPERIENCE = 0.15
WEIGHT_EDUCATION = 0.10
WEIGHT_SENIORITY = 0.05
WEIGHT_CLARITY = 0.10

SECTION_ALIASES = {
    "requirements": {
        "requirements",
        "required qualifications",
        "minimum qualifications",
        "qualifications",
        "must have",
        "required skills",
    },
    "responsibilities": {
        "responsibilities",
        "responsibility",
        "roles and responsibilities",
        "role and responsibilities",
        "key responsibilities",
        "job responsibilities",
        "what you'll do",
        "what you will do",
        "what you’ll do",
        "duties",
        "key duties",
    },
    "skills": {
        "skills",
        "technical skills",
        "required skills",
        "preferred skills",
        "technologies",
        "technical requirements",
    },
    "experience": {
        "experience",
        "work experience",
        "professional experience",
        "years of experience",
    },
    "education": {
        "education",
        "educational qualifications",
        "academic qualifications",
        "degree",
        "degrees",
    },
    "benefits": {
        "benefits",
        "perks",
        "what we offer",
        "employee benefits",
    },
    "about": {
        "about us",
        "about the company",
        "company overview",
        "about the role",
    },
}


# ============================================================================
# Utility Functions
# ============================================================================


def normalize_text(text: Any) -> str:
    """Normalize arbitrary input into clean text."""

    if text is None:
        return ""

    value = str(text)

    value = value.replace(
        "\u00a0",
        " ",
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


def clamp(
    value: float,
    minimum: float = MIN_SCORE,
    maximum: float = MAX_SCORE,
) -> float:
    """Clamp a numeric value into a range."""

    return max(
        minimum,
        min(
            maximum,
            float(value),
        ),
    )


def safe_ratio(
    numerator: float,
    denominator: float,
) -> float:
    """Calculate a safe ratio."""

    if denominator <= 0:
        return 0.0

    return numerator / denominator


def unique_strings(
    values: Iterable[Any],
) -> list[str]:
    """Deduplicate strings while preserving order."""

    result: list[str] = []

    seen: set[str] = set()

    for value in values:

        value = normalize_text(value)

        if not value:
            continue

        key = value.lower()

        if key in seen:
            continue

        seen.add(key)
        result.append(value)

    return result


def contains_any(
    text: str,
    keywords: Iterable[str],
) -> bool:
    """Return True when text contains at least one keyword."""

    normalized = normalize_text(text).lower()

    return any(
        keyword.lower() in normalized
        for keyword in keywords
    )


def count_keywords(
    text: str,
    keywords: Iterable[str],
) -> int:
    """Count unique keywords present in text."""

    normalized = normalize_text(text).lower()

    return sum(
        1
        for keyword in keywords
        if keyword.lower() in normalized
    )


# ============================================================================
# JD Extraction Helpers
# ============================================================================


def extract_raw_text(jd: Any) -> str:
    """
    Extract text from:
        - string
        - dictionary
        - parsed JD object
    """

    if isinstance(jd, str):
        return jd

    if isinstance(jd, Mapping):

        for key in (
            "cleaned_text",
            "text",
            "raw_text",
            "content",
            "description",
        ):

            value = jd.get(key)

            if value:
                return normalize_text(value)

        return ""

    for attribute in (
        "cleaned_text",
        "text",
        "raw_text",
        "content",
        "description",
    ):

        value = getattr(
            jd,
            attribute,
            None,
        )

        if value:
            return normalize_text(value)

    return ""


def extract_sections(
    jd: Any,
) -> dict[str, Any]:
    """
    Extract sections from a parsed JD.
    """

    if isinstance(jd, Mapping):

        sections = jd.get(
            "sections",
            {},
        )

        if isinstance(
            sections,
            Mapping,
        ):
            return dict(sections)

    sections = getattr(
        jd,
        "sections",
        None,
    )

    if isinstance(
        sections,
        Mapping,
    ):
        return dict(sections)

    return {}


def canonical_section_name(
    name: Any,
) -> str:
    """Convert arbitrary section names into canonical names."""

    normalized = normalize_text(
        name
    ).lower()

    normalized = normalized.rstrip(":")

    for canonical, aliases in SECTION_ALIASES.items():

        if normalized in aliases:
            return canonical

    return normalized


def detect_sections_from_text(
    text: str,
) -> dict[str, str]:
    """
    Detect common JD sections from plain text.

    This is intentionally heuristic and lightweight.
    """

    lines = text.splitlines()

    detected: dict[str, list[str]] = {}

    current_section: str | None = None

    for line in lines:

        line = normalize_text(line)

        if not line:
            continue

        section = canonical_section_name(line)

        if section in SECTION_ALIASES:

            current_section = section

            detected.setdefault(
                section,
                [],
            )

            continue

        if current_section is not None:

            detected[
                current_section
            ].append(line)

    return {
        key: "\n".join(value)
        for key, value in detected.items()
    }


# ============================================================================
# Metric Functions
# ============================================================================


def score_requirements(
    jd: Any,
) -> float:
    """
    Score requirement completeness.

    Factors:
        - Required section
        - Number of requirement statements
        - Explicit required markers
        - Specificity
    """

    text = extract_raw_text(jd)

    sections = extract_sections(jd)

    requirement_text = ""

    for name, value in sections.items():

        if canonical_section_name(name) == "requirements":
            requirement_text += (
                "\n" + normalize_text(value)
            )

    if not requirement_text:

        detected = detect_sections_from_text(
            text
        )

        requirement_text = detected.get(
            "requirements",
            "",
        )

    if not requirement_text:

        requirement_text = text

    score = 0.0

    # Section exists.
    if requirement_text:
        score += 30.0

    # Requirement count.
    lines = [
        line
        for line in requirement_text.splitlines()
        if normalize_text(line)
    ]

    if len(lines) >= 5:
        score += 25.0
    elif len(lines) >= 3:
        score += 20.0
    elif len(lines) >= 1:
        score += 10.0

    required_markers = (
        "must",
        "required",
        "mandatory",
        "essential",
        "minimum",
    )

    marker_count = count_keywords(
        requirement_text,
        required_markers,
    )

    score += min(
        marker_count * 5.0,
        20.0,
    )

    # Specificity.
    specificity_keywords = (
        "years",
        "degree",
        "experience",
        "python",
        "java",
        "sql",
        "aws",
        "azure",
        "gcp",
        "bachelor",
        "master",
        "certification",
    )

    specificity_count = count_keywords(
        requirement_text,
        specificity_keywords,
    )

    score += min(
        specificity_count * 2.5,
        25.0,
    )

    return round(
        clamp(score),
        2,
    )


def score_responsibilities(
    jd: Any,
) -> float:
    """
    Score responsibility completeness and clarity.
    """

    text = extract_raw_text(jd)

    sections = extract_sections(jd)

    responsibility_text = ""

    for name, value in sections.items():

        if (
            canonical_section_name(name)
            == "responsibilities"
        ):
            responsibility_text += (
                "\n" + normalize_text(value)
            )

    if not responsibility_text:

        detected = detect_sections_from_text(
            text
        )

        responsibility_text = detected.get(
            "responsibilities",
            "",
        )

    if not responsibility_text:
        responsibility_text = text

    score = 0.0

    if responsibility_text:
        score += 25.0

    lines = [
        line
        for line in responsibility_text.splitlines()
        if normalize_text(line)
    ]

    if len(lines) >= 7:
        score += 30.0
    elif len(lines) >= 5:
        score += 25.0
    elif len(lines) >= 3:
        score += 18.0
    elif len(lines) >= 1:
        score += 10.0

    action_verbs = (
        "develop",
        "build",
        "design",
        "implement",
        "maintain",
        "test",
        "deploy",
        "monitor",
        "analyze",
        "manage",
        "lead",
        "collaborate",
        "optimize",
        "support",
        "create",
        "deliver",
    )

    action_count = count_keywords(
        responsibility_text,
        action_verbs,
    )

    score += min(
        action_count * 3.0,
        30.0,
    )

    # Reasonable responsibility detail.
    words = responsibility_text.split()

    if len(words) >= 100:
        score += 15.0
    elif len(words) >= 50:
        score += 10.0
    elif len(words) >= 20:
        score += 5.0

    return round(
        clamp(score),
        2,
    )


def score_skills(
    jd: Any,
) -> float:
    """
    Score technical/functional skill specificity.
    """

    text = extract_raw_text(jd)

    common_skills = (
        "python",
        "java",
        "javascript",
        "typescript",
        "c++",
        "c#",
        "go",
        "rust",
        "sql",
        "react",
        "angular",
        "vue",
        "node.js",
        "django",
        "flask",
        "fastapi",
        "spring",
        "postgresql",
        "mysql",
        "mongodb",
        "redis",
        "aws",
        "azure",
        "gcp",
        "docker",
        "kubernetes",
        "terraform",
        "jenkins",
        "git",
        "github",
        "machine learning",
        "deep learning",
        "nlp",
        "llm",
        "generative ai",
        "pytorch",
        "tensorflow",
        "scikit-learn",
        "pandas",
        "numpy",
        "spark",
        "tableau",
        "power bi",
        "excel",
    )

    found = count_keywords(
        text,
        common_skills,
    )

    score = 20.0

    if found >= 10:
        score += 65.0
    elif found >= 7:
        score += 55.0
    elif found >= 5:
        score += 45.0
    elif found >= 3:
        score += 35.0
    elif found >= 1:
        score += 20.0

    # Generic skill section.
    detected = detect_sections_from_text(
        text
    )

    if detected.get("skills"):
        score += 15.0

    return round(
        clamp(score),
        2,
    )


def score_experience(
    jd: Any,
) -> float:
    """
    Score experience requirement specificity.
    """

    text = extract_raw_text(jd).lower()

    score = 0.0

    # Explicit years.
    years = re.findall(
        r"\b(\d+)\+?\s*(?:years?|yrs?)\b",
        text,
    )

    if years:
        score += 50.0

        if any(
            int(year) >= 3
            for year in years
        ):
            score += 15.0
    else:
        if "experience" in text:
            score += 25.0

    # Relevant experience wording.
    experience_terms = (
        "professional experience",
        "industry experience",
        "relevant experience",
        "hands-on experience",
        "production experience",
        "software development experience",
    )

    score += min(
        count_keywords(
            text,
            experience_terms,
        )
        * 7.0,
        35.0,
    )

    return round(
        clamp(score),
        2,
    )


def score_education(
    jd: Any,
) -> float:
    """
    Score education requirement clarity.
    """

    text = extract_raw_text(jd).lower()

    education_terms = (
        "bachelor",
        "bachelors",
        "bachelor's",
        "master",
        "master's",
        "phd",
        "doctorate",
        "degree",
        "computer science",
        "engineering",
        "information technology",
        "related field",
    )

    count = count_keywords(
        text,
        education_terms,
    )

    score = min(
        count * 12.0,
        75.0,
    )

    detected = detect_sections_from_text(
        text
    )

    if detected.get("education"):
        score += 25.0

    return round(
        clamp(score),
        2,
    )


def score_seniority(
    jd: Any,
) -> float:
    """
    Score how clearly the JD communicates seniority.
    """

    text = extract_raw_text(jd).lower()

    seniority_terms = (
        "intern",
        "internship",
        "junior",
        "entry level",
        "entry-level",
        "associate",
        "mid-level",
        "mid level",
        "senior",
        "lead",
        "staff",
        "principal",
        "architect",
        "manager",
        "director",
    )

    found = count_keywords(
        text,
        seniority_terms,
    )

    score = 0.0

    if found >= 1:
        score += 70.0

    if found >= 2:
        score += 20.0

    if re.search(
        r"\b\d+\+?\s*(?:years?|yrs?)\b",
        text,
    ):
        score += 10.0

    return round(
        clamp(score),
        2,
    )


def score_clarity(
    jd: Any,
) -> float:
    """
    Score overall readability and structural clarity.
    """

    text = extract_raw_text(jd)

    if not text:
        return 0.0

    score = 30.0

    words = text.split()

    word_count = len(words)

    # Reasonable length.
    if 100 <= word_count <= 1500:
        score += 20.0
    elif 50 <= word_count <= 2500:
        score += 10.0

    # Section structure.
    detected = detect_sections_from_text(
        text
    )

    useful_sections = sum(
        1
        for section in (
            "requirements",
            "responsibilities",
            "skills",
            "experience",
            "education",
        )
        if detected.get(section)
    )

    score += min(
        useful_sections * 7.0,
        35.0,
    )

    # Bullet formatting.
    bullet_lines = sum(
        1
        for line in text.splitlines()
        if re.match(
            r"^\s*[-*•▪◦]",
            line,
        )
    )

    score += min(
        bullet_lines * 1.5,
        15.0,
    )

    return round(
        clamp(score),
        2,
    )


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class JDScoreBreakdown:
    """Individual JD quality scores."""

    requirements: float = 0.0
    responsibilities: float = 0.0
    skills: float = 0.0
    experience: float = 0.0
    education: float = 0.0
    seniority: float = 0.0
    clarity: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass
class JDScore:
    """
    Complete JD scoring result.
    """

    overall_score: float

    grade: str

    quality_level: str

    breakdown: JDScoreBreakdown

    weighted_scores: dict[str, float] = field(
        default_factory=dict
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

    metrics: dict[str, Any] = field(
        default_factory=dict
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "grade": self.grade,
            "quality_level": self.quality_level,
            "breakdown": self.breakdown.to_dict(),
            "weighted_scores": self.weighted_scores,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "recommendations": self.recommendations,
            "metrics": self.metrics,
            "metadata": self.metadata,
        }


# ============================================================================
# Grade
# ============================================================================


def score_to_grade(
    score: float,
) -> str:
    """Convert score to letter grade."""

    score = clamp(score)

    if score >= 90:
        return "A"

    if score >= 80:
        return "B"

    if score >= 70:
        return "C"

    if score >= 60:
        return "D"

    return "F"


def score_to_quality(
    score: float,
) -> str:
    """Convert score to quality label."""

    score = clamp(score)

    if score >= 90:
        return "excellent"

    if score >= 80:
        return "good"

    if score >= 70:
        return "fair"

    if score >= 60:
        return "needs_improvement"

    return "poor"


# ============================================================================
# Main Scorer
# ============================================================================


class JDScorer:
    """
    Main Job Description scorer.

    Example:

        scorer = JDScorer()

        result = scorer.score(jd_text)

        print(result.overall_score)
        print(result.grade)
        print(result.recommendations)
    """

    def __init__(
        self,
        *,
        weights: Mapping[str, float] | None = None,
    ) -> None:

        default_weights = {
            "requirements": WEIGHT_REQUIREMENTS,
            "responsibilities": WEIGHT_RESPONSIBILITIES,
            "skills": WEIGHT_SKILLS,
            "experience": WEIGHT_EXPERIENCE,
            "education": WEIGHT_EDUCATION,
            "seniority": WEIGHT_SENIORITY,
            "clarity": WEIGHT_CLARITY,
        }

        if weights:
            default_weights.update(
                {
                    key: float(value)
                    for key, value
                    in weights.items()
                }
            )

        total = sum(
            default_weights.values()
        )

        if total <= 0:
            raise ValueError(
                "JD scoring weights must sum to a positive value."
            )

        # Normalize weights.
        self.weights = {
            key: value / total
            for key, value
            in default_weights.items()
        }

    def calculate_breakdown(
        self,
        jd: Any,
    ) -> JDScoreBreakdown:
        """Calculate all individual JD metrics."""

        return JDScoreBreakdown(
            requirements=score_requirements(jd),
            responsibilities=score_responsibilities(jd),
            skills=score_skills(jd),
            experience=score_experience(jd),
            education=score_education(jd),
            seniority=score_seniority(jd),
            clarity=score_clarity(jd),
        )

    def calculate_overall(
        self,
        breakdown: JDScoreBreakdown,
    ) -> tuple[
        float,
        dict[str, float],
    ]:
        """Calculate weighted overall score."""

        values = breakdown.to_dict()

        weighted_scores: dict[
            str,
            float,
        ] = {}

        for name, value in values.items():

            weighted_scores[name] = round(
                value
                * self.weights.get(
                    name,
                    0.0,
                ),
                2,
            )

        overall = sum(
            weighted_scores.values()
        )

        return (
            round(
                clamp(overall),
                2,
            ),
            weighted_scores,
        )

    def identify_strengths(
        self,
        breakdown: JDScoreBreakdown,
    ) -> list[str]:
        """Identify strong JD dimensions."""

        strengths: list[str] = []

        checks = {
            "requirements": (
                breakdown.requirements,
                "Clear and detailed requirements.",
            ),
            "responsibilities": (
                breakdown.responsibilities,
                "Responsibilities are clearly defined.",
            ),
            "skills": (
                breakdown.skills,
                "Technical and functional skills are specific.",
            ),
            "experience": (
                breakdown.experience,
                "Experience expectations are reasonably clear.",
            ),
            "education": (
                breakdown.education,
                "Education requirements are clearly specified.",
            ),
            "seniority": (
                breakdown.seniority,
                "Seniority level is clearly communicated.",
            ),
            "clarity": (
                breakdown.clarity,
                "The job description has good structure and clarity.",
            ),
        }

        for _, (
            score,
            message,
        ) in checks.items():

            if score >= 80:
                strengths.append(
                    message
                )

        return strengths

    def identify_weaknesses(
        self,
        breakdown: JDScoreBreakdown,
    ) -> list[str]:
        """Identify weak JD dimensions."""

        weaknesses: list[str] = []

        checks = {
            "requirements": (
                breakdown.requirements,
                "Requirements are incomplete or too generic.",
            ),
            "responsibilities": (
                breakdown.responsibilities,
                "Responsibilities need more detail.",
            ),
            "skills": (
                breakdown.skills,
                "Skills and technologies are not specific enough.",
            ),
            "experience": (
                breakdown.experience,
                "Experience requirements are unclear.",
            ),
            "education": (
                breakdown.education,
                "Education requirements are unclear or missing.",
            ),
            "seniority": (
                breakdown.seniority,
                "Seniority level is not clearly specified.",
            ),
            "clarity": (
                breakdown.clarity,
                "JD structure and readability could be improved.",
            ),
        }

        for _, (
            score,
            message,
        ) in checks.items():

            if score < 60:
                weaknesses.append(
                    message
                )

        return weaknesses

    def generate_recommendations(
        self,
        breakdown: JDScoreBreakdown,
    ) -> list[str]:
        """Generate actionable JD improvement recommendations."""

        recommendations: list[str] = []

        if breakdown.requirements < 70:
            recommendations.append(
                "Add specific mandatory qualifications, "
                "skills, certifications, and domain requirements."
            )

        if breakdown.responsibilities < 70:
            recommendations.append(
                "Describe the main responsibilities using "
                "specific action-oriented bullet points."
            )

        if breakdown.skills < 70:
            recommendations.append(
                "Specify the key technologies, frameworks, "
                "tools, and domain skills required."
            )

        if breakdown.experience < 70:
            recommendations.append(
                "State the expected years and type of relevant "
                "professional experience."
            )

        if breakdown.education < 60:
            recommendations.append(
                "Clarify the required degree or educational "
                "background and acceptable related fields."
            )

        if breakdown.seniority < 60:
            recommendations.append(
                "Explicitly state the role's seniority level."
            )

        if breakdown.clarity < 70:
            recommendations.append(
                "Improve section organization and use concise "
                "bullets for requirements and responsibilities."
            )

        return recommendations

    def calculate_metrics(
        self,
        jd: Any,
        breakdown: JDScoreBreakdown,
    ) -> dict[str, Any]:
        """Calculate additional JD metrics."""

        text = extract_raw_text(jd)

        words = text.split()

        lines = [
            line
            for line in text.splitlines()
            if normalize_text(line)
        ]

        detected_sections = (
            detect_sections_from_text(
                text
            )
        )

        section_count = sum(
            bool(value)
            for value in detected_sections.values()
        )

        bullet_count = sum(
            bool(
                re.match(
                    r"^\s*[-*•▪◦]",
                    line,
                )
            )
            for line in lines
        )

        required_markers = (
            "must",
            "required",
            "mandatory",
            "essential",
        )

        preferred_markers = (
            "preferred",
            "nice to have",
            "bonus",
            "plus",
        )

        required_count = count_keywords(
            text,
            required_markers,
        )

        preferred_count = count_keywords(
            text,
            preferred_markers,
        )

        return {
            "character_count": len(text),
            "word_count": len(words),
            "line_count": len(lines),
            "section_count": section_count,
            "bullet_count": bullet_count,
            "required_marker_count": required_count,
            "preferred_marker_count": preferred_count,
            "requirements_score": (
                breakdown.requirements
            ),
            "responsibilities_score": (
                breakdown.responsibilities
            ),
            "skills_score": breakdown.skills,
            "experience_score": (
                breakdown.experience
            ),
            "education_score": (
                breakdown.education
            ),
            "seniority_score": (
                breakdown.seniority
            ),
            "clarity_score": breakdown.clarity,
        }

    def score(
        self,
        jd: Any,
    ) -> JDScore:
        """
        Score a complete Job Description.
        """

        text = extract_raw_text(jd)

        if not text:
            breakdown = JDScoreBreakdown()

            return JDScore(
                overall_score=0.0,
                grade="F",
                quality_level="poor",
                breakdown=breakdown,
                weighted_scores={},
                strengths=[],
                weaknesses=[
                    "Job description is empty."
                ],
                recommendations=[
                    "Provide a complete job description."
                ],
                metrics={
                    "character_count": 0,
                    "word_count": 0,
                },
                metadata={
                    "empty": True,
                },
            )

        breakdown = self.calculate_breakdown(
            jd
        )

        overall_score, weighted_scores = (
            self.calculate_overall(
                breakdown
            )
        )

        strengths = self.identify_strengths(
            breakdown
        )

        weaknesses = self.identify_weaknesses(
            breakdown
        )

        recommendations = (
            self.generate_recommendations(
                breakdown
            )
        )

        metrics = self.calculate_metrics(
            jd,
            breakdown,
        )

        return JDScore(
            overall_score=overall_score,
            grade=score_to_grade(
                overall_score
            ),
            quality_level=score_to_quality(
                overall_score
            ),
            breakdown=breakdown,
            weighted_scores=weighted_scores,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            metrics=metrics,
            metadata={
                "empty": False,
                "scoring_version": "1.0",
                "weights": self.weights,
            },
        )

    def score_dict(
        self,
        jd: Any,
    ) -> dict[str, Any]:
        """Return a JSON-compatible result."""

        return self.score(
            jd
        ).to_dict()


# ============================================================================
# Convenience API
# ============================================================================


_default_scorer: JDScorer | None = None


def get_default_scorer() -> JDScorer:
    """Return shared default scorer."""

    global _default_scorer

    if _default_scorer is None:
        _default_scorer = JDScorer()

    return _default_scorer


def score_jd(
    jd: Any,
) -> JDScore:
    """Score a Job Description."""

    return get_default_scorer().score(
        jd
    )


def score_jd_dict(
    jd: Any,
) -> dict[str, Any]:
    """Score a Job Description and return a dictionary."""

    return get_default_scorer().score_dict(
        jd
    )


def calculate_jd_score(
    jd: Any,
) -> float:
    """Return only the overall JD score."""

    return score_jd(
        jd
    ).overall_score


def calculate_jd_grade(
    jd: Any,
) -> str:
    """Return only the JD grade."""

    return score_jd(
        jd
    ).grade


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "JDScoreBreakdown",
    "JDScore",
    "JDScorer",
    "normalize_text",
    "clamp",
    "safe_ratio",
    "unique_strings",
    "extract_raw_text",
    "extract_sections",
    "canonical_section_name",
    "detect_sections_from_text",
    "score_requirements",
    "score_responsibilities",
    "score_skills",
    "score_experience",
    "score_education",
    "score_seniority",
    "score_clarity",
    "score_to_grade",
    "score_to_quality",
    "get_default_scorer",
    "score_jd",
    "score_jd_dict",
    "calculate_jd_score",
    "calculate_jd_grade",
]