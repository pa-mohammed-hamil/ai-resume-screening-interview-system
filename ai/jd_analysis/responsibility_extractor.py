# Project scaffold file
"""
Job Description Responsibility Extractor
=========================================

Location:
    ai/jd_analysis/responsibility_extractor.py

Purpose:
    Extract structured responsibilities from a Job Description.

Features:
    - Responsibility extraction
    - Action verb extraction
    - Responsibility categorization
    - Technology/skill detection
    - Seniority signal detection
    - Priority detection
    - Confidence scoring
    - Deduplication
    - Parsed-JD and raw-text compatibility

Works with:
    ai/jd_analysis/jd_parser.py
    ai/jd_analysis/requirement_extractor.py
    ai/jd_analysis/jd_scorer.py
    ai/matching/resume_job_matcher.py
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Mapping, Sequence


# ============================================================================
# Constants
# ============================================================================

CATEGORY_DEVELOPMENT = "development"
CATEGORY_DESIGN = "design"
CATEGORY_MAINTENANCE = "maintenance"
CATEGORY_TESTING = "testing"
CATEGORY_DEPLOYMENT = "deployment"
CATEGORY_DATA = "data"
CATEGORY_ANALYSIS = "analysis"
CATEGORY_LEADERSHIP = "leadership"
CATEGORY_COLLABORATION = "collaboration"
CATEGORY_DOCUMENTATION = "documentation"
CATEGORY_CUSTOMER = "customer"
CATEGORY_SECURITY = "security"
CATEGORY_PROJECT = "project_management"
CATEGORY_OTHER = "other"


RESPONSIBILITY_SECTIONS = {
    "responsibilities",
    "responsibility",
    "roles and responsibilities",
    "role and responsibilities",
    "what you'll do",
    "what you will do",
    "what you’ll do",
    "what you will be doing",
    "job responsibilities",
    "duties",
    "key duties",
    "key responsibilities",
    "your responsibilities",
    "day to day",
    "day-to-day",
}


ACTION_VERBS = {
    "develop",
    "developing",
    "design",
    "designing",
    "build",
    "building",
    "create",
    "creating",
    "implement",
    "implementing",
    "maintain",
    "maintaining",
    "support",
    "supporting",
    "test",
    "testing",
    "deploy",
    "deploying",
    "monitor",
    "monitoring",
    "analyze",
    "analyzing",
    "analyse",
    "analysing",
    "evaluate",
    "evaluating",
    "optimize",
    "optimizing",
    "optimise",
    "optimising",
    "manage",
    "managing",
    "lead",
    "leading",
    "mentor",
    "mentoring",
    "collaborate",
    "collaborating",
    "coordinate",
    "coordinating",
    "communicate",
    "communicating",
    "document",
    "documenting",
    "automate",
    "automating",
    "integrate",
    "integrating",
    "architect",
    "architecting",
    "research",
    "researching",
    "improve",
    "improving",
    "troubleshoot",
    "troubleshooting",
    "debug",
    "debugging",
    "review",
    "reviewing",
    "own",
    "owning",
    "drive",
    "driving",
    "deliver",
    "delivering",
    "plan",
    "planning",
    "report",
    "reporting",
    "secure",
    "securing",
    "scale",
    "scaling",
    "deploy",
    "deploying",
}


TECHNOLOGY_KEYWORDS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "go",
    "golang",
    "rust",
    "ruby",
    "php",
    "scala",
    "kotlin",
    "swift",
    "sql",
    "nosql",
    "html",
    "css",
    "react",
    "react.js",
    "angular",
    "vue",
    "node.js",
    "nodejs",
    "django",
    "flask",
    "fastapi",
    "spring",
    "spring boot",
    "express",
    "postgresql",
    "postgres",
    "mysql",
    "mongodb",
    "redis",
    "oracle",
    "sqlite",
    "elasticsearch",
    "aws",
    "azure",
    "gcp",
    "google cloud",
    "docker",
    "kubernetes",
    "k8s",
    "terraform",
    "jenkins",
    "github actions",
    "gitlab",
    "git",
    "github",
    "ci/cd",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "natural language processing",
    "nlp",
    "computer vision",
    "generative ai",
    "genai",
    "llm",
    "large language model",
    "langchain",
    "pytorch",
    "tensorflow",
    "scikit-learn",
    "pandas",
    "numpy",
    "spark",
    "hadoop",
    "airflow",
    "power bi",
    "tableau",
    "excel",
    "rest api",
    "restful api",
    "graphql",
    "microservices",
    "api",
}


CATEGORY_KEYWORDS = {
    CATEGORY_DEVELOPMENT: {
        "develop",
        "developing",
        "build",
        "building",
        "code",
        "coding",
        "implement",
        "implementing",
        "program",
        "programming",
        "software",
        "application",
        "feature",
        "backend",
        "frontend",
        "full-stack",
        "full stack",
    },
    CATEGORY_DESIGN: {
        "design",
        "designing",
        "architect",
        "architecture",
        "architecting",
        "system design",
        "solution design",
        "technical design",
    },
    CATEGORY_MAINTENANCE: {
        "maintain",
        "maintaining",
        "maintenance",
        "support",
        "supporting",
        "troubleshoot",
        "troubleshooting",
        "debug",
        "debugging",
        "fix",
        "incident",
    },
    CATEGORY_TESTING: {
        "test",
        "testing",
        "qa",
        "quality assurance",
        "unit test",
        "integration test",
        "automation test",
        "regression",
    },
    CATEGORY_DEPLOYMENT: {
        "deploy",
        "deploying",
        "deployment",
        "release",
        "releasing",
        "ci/cd",
        "pipeline",
        "devops",
        "infrastructure",
        "production",
    },
    CATEGORY_DATA: {
        "data",
        "database",
        "sql",
        "etl",
        "pipeline",
        "analytics",
        "machine learning",
        "model",
        "modeling",
        "reporting",
        "dataset",
        "data warehouse",
        "data lake",
    },
    CATEGORY_ANALYSIS: {
        "analyze",
        "analyzing",
        "analyse",
        "analysing",
        "analysis",
        "evaluate",
        "evaluating",
        "research",
        "researching",
        "investigate",
        "investigating",
        "metrics",
        "insights",
    },
    CATEGORY_LEADERSHIP: {
        "lead",
        "leading",
        "mentor",
        "mentoring",
        "manage",
        "managing",
        "manager",
        "strategy",
        "strategic",
        "ownership",
        "own",
        "owning",
        "drive",
        "driving",
    },
    CATEGORY_COLLABORATION: {
        "collaborate",
        "collaborating",
        "coordinate",
        "coordinating",
        "cross-functional",
        "team",
        "stakeholder",
        "partner",
        "communication",
    },
    CATEGORY_DOCUMENTATION: {
        "document",
        "documenting",
        "documentation",
        "write",
        "writing",
        "technical documentation",
        "reports",
        "reporting",
    },
    CATEGORY_CUSTOMER: {
        "customer",
        "client",
        "user",
        "users",
        "customer-facing",
        "client-facing",
        "support customers",
    },
    CATEGORY_SECURITY: {
        "security",
        "secure",
        "securing",
        "authentication",
        "authorization",
        "encryption",
        "vulnerability",
        "compliance",
        "privacy",
        "access control",
    },
    CATEGORY_PROJECT: {
        "project",
        "project management",
        "planning",
        "schedule",
        "roadmap",
        "milestone",
        "delivery",
        "deliver",
    },
}


SENIORITY_SIGNALS = {
    "intern": "intern",
    "internship": "intern",
    "junior": "junior",
    "entry level": "entry",
    "entry-level": "entry",
    "associate": "associate",
    "mid-level": "mid",
    "mid level": "mid",
    "senior": "senior",
    "lead": "lead",
    "staff": "staff",
    "principal": "principal",
    "architect": "architect",
    "manager": "manager",
    "director": "director",
    "head of": "head",
}


REQUIRED_MARKERS = (
    "must",
    "required",
    "mandatory",
    "essential",
    "need to",
    "needs to",
    "responsible for",
    "responsibility",
)


PREFERRED_MARKERS = (
    "preferred",
    "nice to have",
    "nice-to-have",
    "bonus",
    "plus",
    "desired",
)


# ============================================================================
# Utility Functions
# ============================================================================


def normalize_text(
    text: Any,
) -> str:
    """
    Normalize arbitrary input text.
    """

    if text is None:
        return ""

    text = str(text)

    text = text.replace(
        "\u00a0",
        " ",
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def canonical_text(
    text: str,
) -> str:
    """
    Create canonical text for comparison/deduplication.
    """

    value = normalize_text(
        text
    ).lower()

    value = re.sub(
        r"[^a-z0-9+#./\- ]+",
        "",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


def contains_keyword(
    text: str,
    keyword: str,
) -> bool:
    """
    Safely detect a keyword in text.
    """

    text = normalize_text(
        text
    ).lower()

    keyword = normalize_text(
        keyword
    ).lower()

    if not keyword:
        return False

    if " " in keyword or "/" in keyword or "." in keyword:
        return keyword in text

    return bool(
        re.search(
            rf"(?<!\w){re.escape(keyword)}(?!\w)",
            text,
            re.IGNORECASE,
        )
    )


def contains_any(
    text: str,
    keywords: Iterable[str],
) -> bool:
    """
    Check whether text contains at least one keyword.
    """

    return any(
        contains_keyword(
            text,
            keyword,
        )
        for keyword in keywords
    )


# ============================================================================
# Action Verb Extraction
# ============================================================================


def extract_action_verbs(
    text: str,
) -> list[str]:
    """
    Extract common responsibility/action verbs.
    """

    normalized = normalize_text(
        text
    )

    found: list[str] = []

    for verb in sorted(
        ACTION_VERBS,
        key=len,
        reverse=True,
    ):

        if contains_keyword(
            normalized,
            verb,
        ):
            found.append(
                verb
            )

    return found


# ============================================================================
# Technology Extraction
# ============================================================================


def extract_technologies(
    text: str,
) -> list[str]:
    """
    Extract technologies/tools mentioned in a responsibility.
    """

    normalized = normalize_text(
        text
    )

    found: list[str] = []

    for technology in sorted(
        TECHNOLOGY_KEYWORDS,
        key=len,
        reverse=True,
    ):

        if contains_keyword(
            normalized,
            technology,
        ):

            if technology not in found:
                found.append(
                    technology
                )

    return found


# ============================================================================
# Category Detection
# ============================================================================


def detect_category(
    text: str,
) -> str:
    """
    Detect the primary responsibility category.
    """

    normalized = normalize_text(
        text
    ).lower()

    scores: dict[str, int] = {}

    for category, keywords in CATEGORY_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            if contains_keyword(
                normalized,
                keyword,
            ):
                score += 1

        if score:
            scores[category] = score

    if not scores:
        return CATEGORY_OTHER

    return max(
        scores,
        key=scores.get,
    )


def detect_all_categories(
    text: str,
) -> list[str]:
    """
    Return all matching responsibility categories.
    """

    normalized = normalize_text(
        text
    ).lower()

    categories: list[str] = []

    for category, keywords in CATEGORY_KEYWORDS.items():

        if contains_any(
            normalized,
            keywords,
        ):
            categories.append(
                category
            )

    if not categories:
        categories.append(
            CATEGORY_OTHER
        )

    return categories


# ============================================================================
# Priority
# ============================================================================


def detect_priority(
    text: str,
    source_section: str | None = None,
) -> str:
    """
    Detect responsibility priority.
    """

    normalized = normalize_text(
        text
    ).lower()

    section = normalize_text(
        source_section or ""
    ).lower()

    if any(
        marker in section
        for marker in {
            "required",
            "responsibilities",
            "key responsibilities",
            "job responsibilities",
        }
    ):
        return "required"

    if any(
        marker in normalized
        for marker in REQUIRED_MARKERS
    ):
        return "required"

    if any(
        marker in normalized
        for marker in PREFERRED_MARKERS
    ):
        return "preferred"

    return "general"


# ============================================================================
# Seniority Detection
# ============================================================================


def detect_seniority_signals(
    text: str,
) -> list[str]:
    """
    Detect seniority/leadership signals.
    """

    normalized = normalize_text(
        text
    ).lower()

    found: list[str] = []

    for signal, normalized_value in SENIORITY_SIGNALS.items():

        if signal in normalized:
            if normalized_value not in found:
                found.append(
                    normalized_value
                )

    return found


# ============================================================================
# Confidence
# ============================================================================


def calculate_confidence(
    text: str,
    category: str,
    action_verbs: Sequence[str],
    technologies: Sequence[str],
    source_section: str | None,
) -> float:
    """
    Calculate heuristic extraction confidence.

    This is not a statistical probability.
    """

    score = 0.50

    if action_verbs:
        score += 0.18

    if technologies:
        score += 0.08

    if category != CATEGORY_OTHER:
        score += 0.10

    if source_section:
        score += 0.08

    if len(
        normalize_text(text).split()
    ) >= 6:
        score += 0.03

    if len(
        normalize_text(text).split()
    ) >= 12:
        score += 0.02

    return round(
        min(score, 0.99),
        2,
    )


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class Responsibility:
    """
    Structured job responsibility.
    """

    text: str

    category: str

    categories: list[str] = field(
        default_factory=list
    )

    priority: str = "general"

    action_verbs: list[str] = field(
        default_factory=list
    )

    technologies: list[str] = field(
        default_factory=list
    )

    seniority_signals: list[str] = field(
        default_factory=list
    )

    source_section: str | None = None

    confidence: float = 0.0

    normalized: str = ""

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResponsibilityExtraction:
    """
    Complete responsibility extraction result.
    """

    responsibilities: list[Responsibility] = field(
        default_factory=list
    )

    by_category: dict[str, list[Responsibility]] = field(
        default_factory=dict
    )

    action_verbs: list[str] = field(
        default_factory=list
    )

    technologies: list[str] = field(
        default_factory=list
    )

    seniority_signals: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "responsibilities": [
                item.to_dict()
                for item in self.responsibilities
            ],
            "by_category": {
                category: [
                    item.to_dict()
                    for item in items
                ]
                for category, items
                in self.by_category.items()
            },
            "action_verbs": self.action_verbs,
            "technologies": self.technologies,
            "seniority_signals": (
                self.seniority_signals
            ),
            "metadata": self.metadata,
        }


# ============================================================================
# Responsibility Construction
# ============================================================================


def build_responsibility(
    text: str,
    *,
    source_section: str | None = None,
    priority: str | None = None,
) -> Responsibility:
    """
    Build a structured Responsibility object.
    """

    normalized = normalize_text(
        text
    )

    normalized = re.sub(
        r"^[\-\*\•▪◦‣➢]+\s*",
        "",
        normalized,
    )

    normalized = re.sub(
        r"^\d+[\.\)]\s*",
        "",
        normalized,
    )

    action_verbs = (
        extract_action_verbs(
            normalized
        )
    )

    technologies = (
        extract_technologies(
            normalized
        )
    )

    categories = (
        detect_all_categories(
            normalized
        )
    )

    category = (
        categories[0]
        if categories
        else CATEGORY_OTHER
    )

    resolved_priority = (
        priority
        or detect_priority(
            normalized,
            source_section,
        )
    )

    seniority_signals = (
        detect_seniority_signals(
            normalized
        )
    )

    confidence = calculate_confidence(
        normalized,
        category,
        action_verbs,
        technologies,
        source_section,
    )

    return Responsibility(
        text=normalized,
        category=category,
        categories=categories,
        priority=resolved_priority,
        action_verbs=action_verbs,
        technologies=technologies,
        seniority_signals=seniority_signals,
        source_section=source_section,
        confidence=confidence,
        normalized=canonical_text(
            normalized
        ),
        metadata={
            "has_action_verb": bool(
                action_verbs
            ),
            "has_technology": bool(
                technologies
            ),
            "has_seniority_signal": bool(
                seniority_signals
            ),
        },
    )


# ============================================================================
# Deduplication
# ============================================================================


def deduplicate_responsibilities(
    responsibilities: Sequence[Responsibility],
) -> list[Responsibility]:
    """
    Remove duplicate responsibilities.
    """

    unique: dict[
        str,
        Responsibility,
    ] = {}

    for responsibility in responsibilities:

        key = responsibility.normalized

        if not key:
            continue

        existing = unique.get(
            key
        )

        if existing is None:
            unique[key] = responsibility
            continue

        if (
            responsibility.confidence
            > existing.confidence
        ):
            unique[key] = responsibility

    return list(
        unique.values()
    )


# ============================================================================
# Parsed JD Compatibility
# ============================================================================


def _extract_from_parsed_jd(
    parsed_jd: Any,
) -> tuple[
    str,
    Mapping[str, Any] | None,
]:
    """
    Accept either raw JD text, a dictionary, or a parsed JD object.
    """

    if isinstance(
        parsed_jd,
        str,
    ):
        return parsed_jd, None

    if isinstance(
        parsed_jd,
        Mapping,
    ):

        text = str(
            parsed_jd.get(
                "cleaned_text",
                parsed_jd.get(
                    "raw_text",
                    "",
                ),
            )
        )

        sections = parsed_jd.get(
            "sections"
        )

        return (
            text,
            sections
            if isinstance(
                sections,
                Mapping,
            )
            else None,
        )

    text = getattr(
        parsed_jd,
        "cleaned_text",
        "",
    )

    sections = getattr(
        parsed_jd,
        "sections",
        None,
    )

    return (
        str(text),
        sections,
    )


# ============================================================================
# Candidate Line Extraction
# ============================================================================


def _is_heading(
    line: str,
) -> bool:
    """
    Detect likely section heading.
    """

    normalized = normalize_text(
        line
    )

    if not normalized:
        return True

    if normalized.endswith(":"):
        return True

    if len(normalized.split()) <= 5:

        lower = normalized.lower()

        if lower in RESPONSIBILITY_SECTIONS:
            return True

        if lower in {
            "requirements",
            "qualifications",
            "skills",
            "education",
            "experience",
            "preferred qualifications",
            "about the role",
            "about us",
            "benefits",
        }:
            return True

    return False


def _split_responsibility_text(
    text: str,
) -> list[str]:
    """
    Split responsibility text into candidate items.
    """

    if not text:
        return []

    # First use line boundaries.
    lines = text.splitlines()

    result: list[str] = []

    for line in lines:

        line = normalize_text(
            line
        )

        if not line:
            continue

        line = re.sub(
            r"^[\-\*\•▪◦‣➢]+\s*",
            "",
            line,
        )

        line = re.sub(
            r"^\d+[\.\)]\s*",
            "",
            line,
        )

        if not line:
            continue

        result.append(
            line
        )

    # If there are no line boundaries, split semicolon-style
    # responsibility lists.
    if len(result) <= 1:

        text = normalize_text(
            text
        )

        chunks = re.split(
            r";\s+",
            text,
        )

        if len(chunks) > 1:
            result = [
                normalize_text(
                    chunk
                )
                for chunk in chunks
                if normalize_text(
                    chunk
                )
            ]

    return result


# ============================================================================
# Main Extractor
# ============================================================================


class ResponsibilityExtractor:
    """
    Main responsibility extraction engine.

    Example:

        extractor = ResponsibilityExtractor()

        result = extractor.extract(jd_text)

        for responsibility in result.responsibilities:
            print(responsibility.text)
    """

    def __init__(
        self,
        *,
        min_confidence: float = 0.0,
        include_general: bool = True,
    ) -> None:

        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError(
                "min_confidence must be between 0 and 1."
            )

        self.min_confidence = (
            min_confidence
        )

        self.include_general = (
            include_general
        )

    def _collect_items(
        self,
        text: str,
        sections: Mapping[str, Any] | None,
    ) -> list[
        tuple[str, str | None]
    ]:
        """
        Collect likely responsibility items from
        parsed sections or raw text.
        """

        items: list[
            tuple[str, str | None]
        ] = []

        # --------------------------------------------------------------
        # Structured sections
        # --------------------------------------------------------------

        if sections:

            for section_name, section in sections.items():

                normalized_name = (
                    normalize_text(
                        section_name
                    ).lower()
                )

                if normalized_name not in RESPONSIBILITY_SECTIONS:
                    continue

                section_items = getattr(
                    section,
                    "items",
                    None,
                )

                if section_items is None and isinstance(
                    section,
                    Mapping,
                ):
                    section_items = section.get(
                        "items",
                        [],
                    )

                if section_items:

                    for item in section_items:

                        item_text = normalize_text(
                            item
                        )

                        if item_text:
                            items.append(
                                (
                                    item_text,
                                    normalized_name,
                                )
                            )

                    continue

                content = getattr(
                    section,
                    "content",
                    None,
                )

                if content is None and isinstance(
                    section,
                    Mapping,
                ):
                    content = section.get(
                        "content",
                        "",
                    )

                if content:

                    for item in _split_responsibility_text(
                        str(content)
                    ):

                        items.append(
                            (
                                item,
                                normalized_name,
                            )
                        )

        if items:
            return items

        # --------------------------------------------------------------
        # Raw text fallback
        # --------------------------------------------------------------

        lines = text.splitlines()

        in_responsibility_section = False

        current_section: str | None = None

        for line in lines:

            cleaned = normalize_text(
                line
            )

            if not cleaned:
                continue

            lower = cleaned.lower().rstrip(":")

            # Start responsibility section.
            if lower in RESPONSIBILITY_SECTIONS:

                in_responsibility_section = True
                current_section = lower
                continue

            # Detect common new sections.
            if (
                in_responsibility_section
                and lower in {
                    "requirements",
                    "qualifications",
                    "skills",
                    "education",
                    "experience",
                    "preferred qualifications",
                    "benefits",
                    "about us",
                    "about the company",
                    "what we offer",
                }
            ):

                in_responsibility_section = False
                current_section = None
                continue

            if not in_responsibility_section:
                continue

            if _is_heading(
                cleaned
            ):
                continue

            items.append(
                (
                    cleaned,
                    current_section,
                )
            )

        # --------------------------------------------------------------
        # If no explicit section exists, use lines that look
        # strongly like responsibilities.
        # --------------------------------------------------------------

        if not items:

            for line in lines:

                cleaned = normalize_text(
                    line
                )

                if not cleaned:
                    continue

                verbs = extract_action_verbs(
                    cleaned
                )

                if verbs:
                    items.append(
                        (
                            cleaned,
                            None,
                        )
                    )

        return items

    def extract(
        self,
        jd: Any,
    ) -> ResponsibilityExtraction:
        """
        Extract responsibilities from a JD.
        """

        text, sections = (
            _extract_from_parsed_jd(
                jd
            )
        )

        text = normalize_text(
            text
        )

        if not text:
            return ResponsibilityExtraction(
                metadata={
                    "empty": True,
                    "responsibility_count": 0,
                }
            )

        raw_items = self._collect_items(
            text,
            sections,
        )

        responsibilities: list[
            Responsibility
        ] = []

        for raw_text, section in raw_items:

            responsibility = build_responsibility(
                raw_text,
                source_section=section,
            )

            if (
                responsibility.confidence
                < self.min_confidence
            ):
                continue

            if (
                responsibility.category
                == CATEGORY_OTHER
                and not self.include_general
            ):
                continue

            responsibilities.append(
                responsibility
            )

        responsibilities = (
            deduplicate_responsibilities(
                responsibilities
            )
        )

        # --------------------------------------------------------------
        # Aggregate information
        # --------------------------------------------------------------

        action_verbs: list[str] = []

        technologies: list[str] = []

        seniority_signals: list[str] = []

        for responsibility in responsibilities:

            action_verbs.extend(
                responsibility.action_verbs
            )

            technologies.extend(
                responsibility.technologies
            )

            seniority_signals.extend(
                responsibility.seniority_signals
            )

        action_verbs = (
            self._unique_strings(
                action_verbs
            )
        )

        technologies = (
            self._unique_strings(
                technologies
            )
        )

        seniority_signals = (
            self._unique_strings(
                seniority_signals
            )
        )

        # --------------------------------------------------------------
        # Group by category
        # --------------------------------------------------------------

        by_category: dict[
            str,
            list[Responsibility],
        ] = {}

        for responsibility in responsibilities:

            for category in (
                responsibility.categories
            ):

                by_category.setdefault(
                    category,
                    [],
                ).append(
                    responsibility
                )

        # --------------------------------------------------------------
        # Metadata
        # --------------------------------------------------------------

        required_count = sum(
            1
            for item in responsibilities
            if item.priority == "required"
        )

        preferred_count = sum(
            1
            for item in responsibilities
            if item.priority == "preferred"
        )

        technology_responsibility_count = sum(
            1
            for item in responsibilities
            if item.technologies
        )

        action_based_count = sum(
            1
            for item in responsibilities
            if item.action_verbs
        )

        metadata = {
            "empty": False,
            "responsibility_count": len(
                responsibilities
            ),
            "required_count": required_count,
            "preferred_count": preferred_count,
            "general_count": (
                len(responsibilities)
                - required_count
                - preferred_count
            ),
            "category_count": len(
                by_category
            ),
            "action_based_count": (
                action_based_count
            ),
            "technology_responsibility_count": (
                technology_responsibility_count
            ),
            "action_coverage": round(
                action_based_count
                / len(responsibilities),
                3,
            )
            if responsibilities
            else 0.0,
            "source": (
                "parsed_sections"
                if sections
                else "raw_text"
            ),
        }

        return ResponsibilityExtraction(
            responsibilities=responsibilities,
            by_category=by_category,
            action_verbs=action_verbs,
            technologies=technologies,
            seniority_signals=seniority_signals,
            metadata=metadata,
        )

    @staticmethod
    def _unique_strings(
        values: Iterable[str],
    ) -> list[str]:
        """
        Deduplicate strings while preserving order.
        """

        result: list[str] = []

        seen: set[str] = set()

        for value in values:

            value = normalize_text(
                value
            )

            if not value:
                continue

            key = value.lower()

            if key in seen:
                continue

            seen.add(key)

            result.append(
                value
            )

        return result

    def extract_dict(
        self,
        jd: Any,
    ) -> dict[str, Any]:
        """
        Return JSON-compatible extraction.
        """

        return self.extract(
            jd
        ).to_dict()


# ============================================================================
# Functional API
# ============================================================================


_default_extractor: ResponsibilityExtractor | None = None


def get_default_extractor() -> ResponsibilityExtractor:
    """
    Get the shared default extractor.
    """

    global _default_extractor

    if _default_extractor is None:
        _default_extractor = (
            ResponsibilityExtractor()
        )

    return _default_extractor


def extract_responsibilities(
    jd: Any,
) -> ResponsibilityExtraction:
    """
    Extract responsibilities from a JD.
    """

    return get_default_extractor().extract(
        jd
    )


def extract_responsibilities_dict(
    jd: Any,
) -> dict[str, Any]:
    """
    Extract responsibilities as a dictionary.
    """

    return get_default_extractor().extract_dict(
        jd
    )


def extract_action_verbs_from_jd(
    jd: Any,
) -> list[str]:
    """
    Extract all action verbs from JD responsibilities.
    """

    result = extract_responsibilities(
        jd
    )

    return result.action_verbs


def extract_responsibility_technologies(
    jd: Any,
) -> list[str]:
    """
    Extract technologies mentioned in responsibilities.
    """

    result = extract_responsibilities(
        jd
    )

    return result.technologies


def extract_seniority_signals(
    jd: Any,
) -> list[str]:
    """
    Extract seniority signals from responsibilities.
    """

    result = extract_responsibilities(
        jd
    )

    return result.seniority_signals


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "CATEGORY_DEVELOPMENT",
    "CATEGORY_DESIGN",
    "CATEGORY_MAINTENANCE",
    "CATEGORY_TESTING",
    "CATEGORY_DEPLOYMENT",
    "CATEGORY_DATA",
    "CATEGORY_ANALYSIS",
    "CATEGORY_LEADERSHIP",
    "CATEGORY_COLLABORATION",
    "CATEGORY_DOCUMENTATION",
    "CATEGORY_CUSTOMER",
    "CATEGORY_SECURITY",
    "CATEGORY_PROJECT",
    "CATEGORY_OTHER",
    "Responsibility",
    "ResponsibilityExtraction",
    "ResponsibilityExtractor",
    "normalize_text",
    "canonical_text",
    "extract_action_verbs",
    "extract_technologies",
    "detect_category",
    "detect_all_categories",
    "detect_priority",
    "detect_seniority_signals",
    "calculate_confidence",
    "build_responsibility",
    "deduplicate_responsibilities",
    "get_default_extractor",
    "extract_responsibilities",
    "extract_responsibilities_dict",
    "extract_action_verbs_from_jd",
    "extract_responsibility_technologies",
    "extract_seniority_signals",
]