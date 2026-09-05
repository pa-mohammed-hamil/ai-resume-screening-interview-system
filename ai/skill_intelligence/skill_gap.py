"""
Skill Gap Analysis
------------------
Analyzes the difference between candidate skills and job requirements.

Location:
    ai/skill_intelligence/skill_gap.py

Responsibilities:
    - Normalize candidate and required skills
    - Find matched skills
    - Find missing skills
    - Identify related skills
    - Calculate coverage percentages
    - Weight skills by importance
    - Separate required and preferred gaps
    - Generate recruiter-friendly recommendations

Dependencies:
    ai.skill_intelligence.skill_taxonomy
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from .skill_taxonomy import (
    SkillCategory,
    are_related,
    canonicalize_skills,
    get_skill,
    get_skill_category,
    get_skill_importance,
)


# ============================================================================
# Data Models
# ============================================================================


@dataclass
class SkillGap:
    """Represents one missing or partially satisfied skill."""

    skill: str
    category: str
    importance: int
    required: bool = True

    related_candidate_skills: list[str] = field(
        default_factory=list
    )

    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill": self.skill,
            "category": self.category,
            "importance": self.importance,
            "required": self.required,
            "related_candidate_skills": (
                self.related_candidate_skills
            ),
            "reason": self.reason,
        }


@dataclass
class SkillGapReport:
    """Complete candidate skill-gap report."""

    candidate_skills: list[str]

    required_skills: list[str]

    preferred_skills: list[str]

    matched_required: list[str]

    matched_preferred: list[str]

    missing_required: list[SkillGap]

    missing_preferred: list[SkillGap]

    related_matches: dict[str, list[str]]

    required_coverage: float

    preferred_coverage: float

    overall_coverage: float

    weighted_score: float

    critical_gaps: list[str]

    recommendations: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_skills": self.candidate_skills,
            "required_skills": self.required_skills,
            "preferred_skills": self.preferred_skills,
            "matched_required": self.matched_required,
            "matched_preferred": self.matched_preferred,
            "missing_required": [
                gap.to_dict()
                for gap in self.missing_required
            ],
            "missing_preferred": [
                gap.to_dict()
                for gap in self.missing_preferred
            ],
            "related_matches": self.related_matches,
            "required_coverage": self.required_coverage,
            "preferred_coverage": self.preferred_coverage,
            "overall_coverage": self.overall_coverage,
            "weighted_score": self.weighted_score,
            "critical_gaps": self.critical_gaps,
            "recommendations": self.recommendations,
        }


# ============================================================================
# Utility Functions
# ============================================================================


def _unique(items: Iterable[str]) -> list[str]:
    """Return unique strings while preserving order."""

    result: list[str] = []
    seen: set[str] = set()

    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)

    return result


def _safe_percentage(
    numerator: float,
    denominator: float,
) -> float:
    """Calculate percentage safely."""

    if denominator <= 0:
        return 100.0

    return round(
        (numerator / denominator) * 100,
        2,
    )


def _normalize_skill_list(
    skills: Iterable[str] | None,
) -> list[str]:
    """Canonicalize and deduplicate a skill list."""

    if not skills:
        return []

    return canonicalize_skills(
        skills
    )


# ============================================================================
# Basic Matching
# ============================================================================


def get_matched_skills(
    candidate_skills: Iterable[str],
    required_skills: Iterable[str],
) -> list[str]:
    """
    Return required skills directly matched by candidate.

    Aliases are resolved through the taxonomy.
    """

    candidate = set(
        _normalize_skill_list(
            candidate_skills
        )
    )

    required = _normalize_skill_list(
        required_skills
    )

    return [
        skill
        for skill in required
        if skill in candidate
    ]


def get_missing_skills(
    candidate_skills: Iterable[str],
    required_skills: Iterable[str],
) -> list[str]:
    """Return required skills not directly present."""

    candidate = set(
        _normalize_skill_list(
            candidate_skills
        )
    )

    required = _normalize_skill_list(
        required_skills
    )

    return [
        skill
        for skill in required
        if skill not in candidate
    ]


# ============================================================================
# Related Skill Analysis
# ============================================================================


def find_related_candidate_skills(
    candidate_skills: Iterable[str],
    missing_skill: str,
) -> list[str]:
    """
    Find candidate skills that are related to a missing skill.

    Example:

        Candidate:
            ["Python"]

        Missing:
            "FastAPI"

        Result:
            ["python"]
    """

    candidate = _normalize_skill_list(
        candidate_skills
    )

    missing = get_skill(
        missing_skill
    )

    if missing is None:
        return []

    related: list[str] = []

    for candidate_skill in candidate:

        if are_related(
            candidate_skill,
            missing.name,
        ):
            related.append(
                candidate_skill
            )

    return related


def build_related_matches(
    candidate_skills: Iterable[str],
    missing_skills: Iterable[str],
) -> dict[str, list[str]]:
    """Build mapping of missing skill -> related candidate skills."""

    result: dict[str, list[str]] = {}

    for skill in missing_skills:

        related = (
            find_related_candidate_skills(
                candidate_skills,
                skill,
            )
        )

        if related:
            result[skill] = related

    return result


# ============================================================================
# Skill Coverage
# ============================================================================


def calculate_coverage(
    candidate_skills: Iterable[str],
    required_skills: Iterable[str],
) -> float:
    """
    Calculate direct skill coverage.

    Returns:
        Percentage between 0 and 100.
    """

    candidate = set(
        _normalize_skill_list(
            candidate_skills
        )
    )

    required = _normalize_skill_list(
        required_skills
    )

    if not required:
        return 100.0

    matched = sum(
        skill in candidate
        for skill in required
    )

    return _safe_percentage(
        matched,
        len(required),
    )


def calculate_weighted_coverage(
    candidate_skills: Iterable[str],
    required_skills: Iterable[str],
) -> float:
    """
    Calculate importance-weighted coverage.

    Higher importance skills contribute more
    to the final score.
    """

    candidate = set(
        _normalize_skill_list(
            candidate_skills
        )
    )

    required = _normalize_skill_list(
        required_skills
    )

    if not required:
        return 100.0

    total_weight = 0.0
    achieved_weight = 0.0

    for skill in required:

        importance = get_skill_importance(
            skill
        )

        total_weight += importance

        if skill in candidate:
            achieved_weight += importance

    return _safe_percentage(
        achieved_weight,
        total_weight,
    )


# ============================================================================
# Gap Construction
# ============================================================================


def _build_gap(
    skill: str,
    candidate_skills: Iterable[str],
    required: bool,
) -> SkillGap:
    """Create a SkillGap object."""

    definition = get_skill(skill)

    if definition is None:
        return SkillGap(
            skill=skill,
            category=SkillCategory.OTHER.value,
            importance=1,
            required=required,
            reason="Skill is not present in the candidate profile.",
        )

    related = find_related_candidate_skills(
        candidate_skills,
        skill,
    )

    if related:
        reason = (
            "Candidate has related skills "
            "but not the requested skill."
        )
    else:
        reason = (
            "Candidate does not list this skill."
        )

    return SkillGap(
        skill=definition.name,
        category=definition.category.value,
        importance=definition.importance,
        required=required,
        related_candidate_skills=related,
        reason=reason,
    )


def build_skill_gaps(
    candidate_skills: Iterable[str],
    required_skills: Iterable[str],
    preferred: bool = False,
) -> list[SkillGap]:
    """Build detailed gap objects."""

    missing = get_missing_skills(
        candidate_skills,
        required_skills,
    )

    return [
        _build_gap(
            skill,
            candidate_skills,
            required=not preferred,
        )
        for skill in missing
    ]


# ============================================================================
# Critical Gap Detection
# ============================================================================


def get_critical_gaps(
    gaps: Iterable[SkillGap],
    minimum_importance: int = 5,
) -> list[str]:
    """
    Return high-importance missing skills.

    By default, only importance-5 skills are returned.
    """

    return [
        gap.skill
        for gap in gaps
        if gap.importance >= minimum_importance
        and gap.required
    ]


# ============================================================================
# Recommendations
# ============================================================================


def generate_recommendations(
    missing_required: Iterable[SkillGap],
    missing_preferred: Iterable[SkillGap],
    related_matches: dict[str, list[str]] | None = None,
) -> list[str]:
    """
    Generate actionable recommendations from skill gaps.
    """

    recommendations: list[str] = []

    required_gaps = list(
        missing_required
    )

    preferred_gaps = list(
        missing_preferred
    )

    related_matches = (
        related_matches or {}
    )

    # ----------------------------------------------------------------------
    # Required skills
    # ----------------------------------------------------------------------

    critical = [
        gap
        for gap in required_gaps
        if gap.importance >= 5
    ]

    for gap in critical:
        if gap.skill in related_matches:
            related = ", ".join(
                related_matches[gap.skill]
            )

            recommendations.append(
                f"Develop {gap.skill}; "
                f"the candidate already has related "
                f"skills: {related}."
            )
        else:
            recommendations.append(
                f"Add practical experience with "
                f"{gap.skill}."
            )

    # ----------------------------------------------------------------------
    # Medium-priority skills
    # ----------------------------------------------------------------------

    medium = [
        gap
        for gap in required_gaps
        if gap.importance in (3, 4)
    ]

    if medium:
        skills = ", ".join(
            gap.skill
            for gap in medium[:5]
        )

        recommendations.append(
            f"Consider strengthening these "
            f"required skills: {skills}."
        )

    # ----------------------------------------------------------------------
    # Preferred skills
    # ----------------------------------------------------------------------

    if preferred_gaps:
        skills = ", ".join(
            gap.skill
            for gap in preferred_gaps[:5]
        )

        recommendations.append(
            f"Preferred skills that could "
            f"improve the candidate's profile: "
            f"{skills}."
        )

    # ----------------------------------------------------------------------
    # No gaps
    # ----------------------------------------------------------------------

    if not recommendations:
        recommendations.append(
            "Candidate has strong coverage of "
            "the listed job skills."
        )

    return _unique(
        recommendations
    )


# ============================================================================
# Overall Score
# ============================================================================


def calculate_overall_score(
    required_coverage: float,
    preferred_coverage: float,
    required_weight: float = 0.80,
    preferred_weight: float = 0.20,
) -> float:
    """
    Calculate overall skill-fit score.

    Default:
        Required skills  = 80%
        Preferred skills = 20%
    """

    total_weight = (
        required_weight
        + preferred_weight
    )

    if total_weight <= 0:
        return 0.0

    score = (
        required_coverage
        * required_weight
        + preferred_coverage
        * preferred_weight
    ) / total_weight

    return round(
        score,
        2,
    )


# ============================================================================
# Main Analysis
# ============================================================================


def analyze_skill_gap(
    candidate_skills: Iterable[str],
    required_skills: Iterable[str],
    preferred_skills: Iterable[str] | None = None,
) -> SkillGapReport:
    """
    Perform complete skill-gap analysis.

    Args:
        candidate_skills:
            Skills extracted from candidate resume.

        required_skills:
            Mandatory skills extracted from JD.

        preferred_skills:
            Optional/preferred skills extracted from JD.

    Returns:
        SkillGapReport
    """

    preferred_skills = (
        preferred_skills or []
    )

    candidate = _normalize_skill_list(
        candidate_skills
    )

    required = _normalize_skill_list(
        required_skills
    )

    preferred = _normalize_skill_list(
        preferred_skills
    )

    # ----------------------------------------------------------------------
    # Direct matching
    # ----------------------------------------------------------------------

    matched_required = (
        get_matched_skills(
            candidate,
            required,
        )
    )

    matched_preferred = (
        get_matched_skills(
            candidate,
            preferred,
        )
    )

    # ----------------------------------------------------------------------
    # Missing skills
    # ----------------------------------------------------------------------

    missing_required = build_skill_gaps(
        candidate,
        required,
        preferred=False,
    )

    missing_preferred = build_skill_gaps(
        candidate,
        preferred,
        preferred=True,
    )

    # ----------------------------------------------------------------------
    # Related skills
    # ----------------------------------------------------------------------

    all_missing = [
        gap.skill
        for gap in (
            missing_required
            + missing_preferred
        )
    ]

    related_matches = (
        build_related_matches(
            candidate,
            all_missing,
        )
    )

    # ----------------------------------------------------------------------
    # Coverage
    # ----------------------------------------------------------------------

    required_coverage = (
        calculate_coverage(
            candidate,
            required,
        )
    )

    preferred_coverage = (
        calculate_coverage(
            candidate,
            preferred,
        )
    )

    weighted_score = (
        calculate_weighted_coverage(
            candidate,
            required,
        )
    )

    # ----------------------------------------------------------------------
    # Overall
    # ----------------------------------------------------------------------

    overall_coverage = (
        calculate_overall_score(
            required_coverage,
            preferred_coverage,
        )
    )

    # ----------------------------------------------------------------------
    # Critical gaps
    # ----------------------------------------------------------------------

    critical_gaps = (
        get_critical_gaps(
            missing_required
        )
    )

    # ----------------------------------------------------------------------
    # Recommendations
    # ----------------------------------------------------------------------

    recommendations = (
        generate_recommendations(
            missing_required,
            missing_preferred,
            related_matches,
        )
    )

    return SkillGapReport(
        candidate_skills=candidate,
        required_skills=required,
        preferred_skills=preferred,
        matched_required=matched_required,
        matched_preferred=matched_preferred,
        missing_required=missing_required,
        missing_preferred=missing_preferred,
        related_matches=related_matches,
        required_coverage=required_coverage,
        preferred_coverage=preferred_coverage,
        overall_coverage=overall_coverage,
        weighted_score=weighted_score,
        critical_gaps=critical_gaps,
        recommendations=recommendations,
    )


# ============================================================================
# Convenience APIs
# ============================================================================


def get_skill_gap_summary(
    candidate_skills: Iterable[str],
    required_skills: Iterable[str],
    preferred_skills: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Return a lightweight summary."""

    report = analyze_skill_gap(
        candidate_skills=candidate_skills,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
    )

    return {
        "required_coverage": (
            report.required_coverage
        ),
        "preferred_coverage": (
            report.preferred_coverage
        ),
        "overall_coverage": (
            report.overall_coverage
        ),
        "weighted_score": (
            report.weighted_score
        ),
        "matched_required": (
            report.matched_required
        ),
        "missing_required": [
            gap.skill
            for gap in report.missing_required
        ],
        "critical_gaps": (
            report.critical_gaps
        ),
    }


def get_top_skill_gaps(
    candidate_skills: Iterable[str],
    required_skills: Iterable[str],
    limit: int = 5,
) -> list[SkillGap]:
    """Return highest-priority missing skills."""

    gaps = build_skill_gaps(
        candidate_skills,
        required_skills,
    )

    gaps.sort(
        key=lambda gap: (
            gap.importance,
            gap.skill,
        ),
        reverse=True,
    )

    return gaps[:limit]


def has_critical_skill_gap(
    candidate_skills: Iterable[str],
    required_skills: Iterable[str],
) -> bool:
    """Check whether candidate is missing any critical skill."""

    gaps = build_skill_gaps(
        candidate_skills,
        required_skills,
    )

    return any(
        gap.importance >= 5
        for gap in gaps
    )


# ============================================================================
# Category-level Analysis
# ============================================================================


def category_skill_gap(
    candidate_skills: Iterable[str],
    required_skills: Iterable[str],
) -> dict[str, dict[str, Any]]:
    """
    Calculate skill coverage by category.

    Example:

        {
            "programming_language": {
                "required": 2,
                "matched": 2,
                "missing": 0,
                "coverage": 100.0
            }
        }
    """

    candidate = set(
        _normalize_skill_list(
            candidate_skills
        )
    )

    required = _normalize_skill_list(
        required_skills
    )

    categories: dict[
        str,
        list[str],
    ] = {}

    for skill in required:

        category = get_skill_category(
            skill
        )

        category_name = (
            category.value
            if category
            else SkillCategory.OTHER.value
        )

        categories.setdefault(
            category_name,
            [],
        ).append(skill)

    result: dict[
        str,
        dict[str, Any],
    ] = {}

    for category, skills in categories.items():

        matched = [
            skill
            for skill in skills
            if skill in candidate
        ]

        missing = [
            skill
            for skill in skills
            if skill not in candidate
        ]

        result[category] = {
            "required": len(skills),
            "matched": len(matched),
            "missing": len(missing),
            "matched_skills": matched,
            "missing_skills": missing,
            "coverage": _safe_percentage(
                len(matched),
                len(skills),
            ),
        }

    return result


# ============================================================================
# Resume Optimization Helpers
# ============================================================================


def get_resume_optimization_gaps(
    candidate_skills: Iterable[str],
    required_skills: Iterable[str],
) -> list[dict[str, Any]]:
    """
    Return missing skills in a format suitable for
    resume optimizer services.
    """

    gaps = build_skill_gaps(
        candidate_skills,
        required_skills,
    )

    result: list[dict[str, Any]] = []

    for gap in gaps:

        result.append(
            {
                "skill": gap.skill,
                "category": gap.category,
                "importance": gap.importance,
                "priority": (
                    "high"
                    if gap.importance >= 5
                    else "medium"
                    if gap.importance >= 3
                    else "low"
                ),
                "has_related_skill": bool(
                    gap.related_candidate_skills
                ),
                "related_skills": (
                    gap.related_candidate_skills
                ),
                "suggestion": (
                    f"Consider adding evidence of "
                    f"{gap.skill} if the candidate "
                    f"actually has this experience."
                ),
            }
        )

    return result


# ============================================================================
# Serialization
# ============================================================================


def report_to_dict(
    report: SkillGapReport,
) -> dict[str, Any]:
    """Convert report to JSON-compatible dictionary."""

    return report.to_dict()


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "SkillGap",
    "SkillGapReport",
    "get_matched_skills",
    "get_missing_skills",
    "find_related_candidate_skills",
    "build_related_matches",
    "calculate_coverage",
    "calculate_weighted_coverage",
    "build_skill_gaps",
    "get_critical_gaps",
    "generate_recommendations",
    "calculate_overall_score",
    "analyze_skill_gap",
    "get_skill_gap_summary",
    "get_top_skill_gaps",
    "has_critical_skill_gap",
    "category_skill_gap",
    "get_resume_optimization_gaps",
    "report_to_dict",
]

