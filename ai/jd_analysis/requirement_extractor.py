# Project scaffold file
"""
Job Description Requirement Extractor
======================================

Location:
    ai/jd_analysis/requirement_extractor.py

Purpose:
    Extract structured hiring requirements from a Job Description.

Extracts:
    - Required requirements
    - Preferred requirements
    - Technical skills
    - Soft skills
    - Education requirements
    - Experience requirements
    - Certifications
    - Years of experience
    - Tools / technologies
    - Requirement priority

Designed to work with:
    ai/jd_analysis/jd_parser.py
    ai/jd_analysis/responsibility_extractor.py
    ai/jd_analysis/jd_scorer.py
    ai/skill_intelligence/skill_normalizer.py
    ai/matching/resume_job_matcher.py
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Mapping, Sequence


# ============================================================================
# Constants
# ============================================================================

REQUIRED = "required"
PREFERRED = "preferred"
GENERAL = "general"

TECHNICAL = "technical"
SOFT = "soft"
EDUCATION = "education"
EXPERIENCE = "experience"
CERTIFICATION = "certification"
OTHER = "other"


REQUIRED_MARKERS = (
    "required",
    "must have",
    "must-have",
    "mandatory",
    "essential",
    "minimum",
    "need to have",
    "should have",
    "you have",
    "we require",
    "required qualification",
    "required qualifications",
    "required skill",
    "required skills",
)

PREFERRED_MARKERS = (
    "preferred",
    "nice to have",
    "nice-to-have",
    "bonus",
    "desired",
    "plus",
    "would be a plus",
    "preferred qualification",
    "preferred qualifications",
    "preferred skill",
    "preferred skills",
)

TECHNICAL_KEYWORDS = {
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
    "gitlab ci",
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
}

SOFT_SKILLS = {
    "communication",
    "leadership",
    "teamwork",
    "collaboration",
    "problem solving",
    "problem-solving",
    "critical thinking",
    "analytical thinking",
    "time management",
    "adaptability",
    "adaptable",
    "creativity",
    "creativity",
    "attention to detail",
    "decision making",
    "decision-making",
    "mentoring",
    "negotiation",
    "presentation",
    "interpersonal skills",
    "organization",
    "organizational skills",
    "self motivated",
    "self-motivated",
}

EDUCATION_PATTERNS = [
    r"\bbachelor(?:'s)?\b",
    r"\bmaster(?:'s)?\b",
    r"\bph\.?d\.?\b",
    r"\bdoctorate\b",
    r"\bdegree\b",
    r"\bundergraduate\b",
    r"\bgraduate degree\b",
    r"\bb\.?tech\b",
    r"\bm\.?tech\b",
    r"\bb\.?e\.?\b",
    r"\bm\.?e\.?\b",
    r"\bmca\b",
    r"\bbca\b",
    r"\bmba\b",
    r"\bcomputer science\b",
    r"\binformation technology\b",
    r"\bengineering\b",
]

CERTIFICATION_PATTERNS = [
    r"\bcertification\b",
    r"\bcertified\b",
    r"\baws certified\b",
    r"\bazure certified\b",
    r"\bgcp certified\b",
    r"\bcka\b",
    r"\bckad\b",
    r"\bpmp\b",
    r"\bscrum master\b",
    r"\bcomptia\b",
    r"\bsecurity\+\b",
    r"\bnetwork\+\b",
    r"\bcia\b",
    r"\bcpa\b",
]

EXPERIENCE_PATTERN = re.compile(
    r"(?P<min>\d+(?:\.\d+)?)"
    r"\s*(?:\+|plus)?"
    r"\s*(?:-|to)?\s*"
    r"(?P<max>\d+(?:\.\d+)?)?"
    r"\s*(?:years?|yrs?)"
    r"(?:\s+of)?\s+"
    r"(?:professional\s+)?experience",
    re.IGNORECASE,
)

EXPERIENCE_GENERAL_PATTERN = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\b",
    re.IGNORECASE,
)


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class Requirement:
    """
    Represents one extracted requirement.
    """

    text: str

    category: str

    priority: str = GENERAL

    normalized: str = ""

    skill: str | None = None

    years_min: float | None = None

    years_max: float | None = None

    source_section: str | None = None

    confidence: float = 0.0

    evidence: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RequirementExtraction:
    """
    Complete structured requirement extraction result.
    """

    required: list[Requirement] = field(
        default_factory=list
    )

    preferred: list[Requirement] = field(
        default_factory=list
    )

    general: list[Requirement] = field(
        default_factory=list
    )

    technical_skills: list[str] = field(
        default_factory=list
    )

    soft_skills: list[str] = field(
        default_factory=list
    )

    education_requirements: list[str] = field(
        default_factory=list
    )

    experience_requirements: list[str] = field(
        default_factory=list
    )

    certifications: list[str] = field(
        default_factory=list
    )

    years_of_experience: list[dict[str, Any]] = field(
        default_factory=list
    )

    all_requirements: list[Requirement] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "required": [
                item.to_dict()
                for item in self.required
            ],
            "preferred": [
                item.to_dict()
                for item in self.preferred
            ],
            "general": [
                item.to_dict()
                for item in self.general
            ],
            "technical_skills": self.technical_skills,
            "soft_skills": self.soft_skills,
            "education_requirements": (
                self.education_requirements
            ),
            "experience_requirements": (
                self.experience_requirements
            ),
            "certifications": self.certifications,
            "years_of_experience": (
                self.years_of_experience
            ),
            "all_requirements": [
                item.to_dict()
                for item in self.all_requirements
            ],
            "metadata": self.metadata,
        }


# ============================================================================
# Text Utilities
# ============================================================================


def normalize_text(
    text: Any,
) -> str:
    """
    Normalize arbitrary text.
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


def normalize_requirement(
    text: str,
) -> str:
    """
    Normalize requirement text.
    """

    text = normalize_text(
        text
    )

    text = re.sub(
        r"^[\-\*\•▪◦‣➢]+\s*",
        "",
        text,
    )

    text = re.sub(
        r"^\d+[\.\)]\s*",
        "",
        text,
    )

    return text.strip()


def canonical_text(
    text: str,
) -> str:
    """
    Canonical representation used for deduplication.
    """

    text = normalize_text(
        text
    ).lower()

    text = re.sub(
        r"[^a-z0-9+#.\-/ ]+",
        "",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================================
# Priority Detection
# ============================================================================


def detect_priority(
    text: str,
    source_section: str | None = None,
) -> str:
    """
    Detect requirement priority.
    """

    normalized = normalize_text(
        text
    ).lower()

    section = normalize_text(
        source_section or ""
    ).lower()

    if section in {
        "requirements",
        "required",
        "required qualifications",
        "required skills",
    }:
        return REQUIRED

    if section in {
        "preferred",
        "preferred qualifications",
        "preferred skills",
    }:
        return PREFERRED

    if any(
        marker in normalized
        for marker in REQUIRED_MARKERS
    ):
        return REQUIRED

    if any(
        marker in normalized
        for marker in PREFERRED_MARKERS
    ):
        return PREFERRED

    return GENERAL


# ============================================================================
# Category Detection
# ============================================================================


def contains_any(
    text: str,
    values: Iterable[str],
) -> bool:
    """
    Check whether normalized text contains any value.
    """

    normalized = normalize_text(
        text
    ).lower()

    return any(
        value.lower()
        in normalized
        for value in values
    )


def detect_category(
    text: str,
) -> str:
    """
    Detect requirement category.
    """

    normalized = normalize_text(
        text
    ).lower()

    # Education first because degree names may appear
    # inside broader requirements.
    if any(
        re.search(
            pattern,
            normalized,
            re.IGNORECASE,
        )
        for pattern in EDUCATION_PATTERNS
    ):
        return EDUCATION

    if any(
        re.search(
            pattern,
            normalized,
            re.IGNORECASE,
        )
        for pattern in CERTIFICATION_PATTERNS
    ):
        return CERTIFICATION

    if EXPERIENCE_PATTERN.search(
        normalized
    ):
        return EXPERIENCE

    if EXPERIENCE_GENERAL_PATTERN.search(
        normalized
    ):
        return EXPERIENCE

    if contains_any(
        normalized,
        SOFT_SKILLS,
    ):
        return SOFT

    if contains_any(
        normalized,
        TECHNICAL_KEYWORDS,
    ):
        return TECHNICAL

    return OTHER


# ============================================================================
# Skill Extraction
# ============================================================================


def _skill_pattern(
    skill: str,
) -> str:
    """
    Build a safe regex pattern for a skill.
    """

    escaped = re.escape(
        skill.lower()
    )

    return rf"(?<!\w){escaped}(?!\w)"


def extract_technical_skills(
    text: str,
) -> list[str]:
    """
    Extract known technical skills from requirement text.
    """

    normalized = normalize_text(
        text
    ).lower()

    found: list[str] = []

    # Longest first prevents partial matches from
    # dominating shorter terms.
    skills = sorted(
        TECHNICAL_KEYWORDS,
        key=len,
        reverse=True,
    )

    for skill in skills:

        pattern = _skill_pattern(
            skill
        )

        if re.search(
            pattern,
            normalized,
            re.IGNORECASE,
        ):

            if skill not in found:
                found.append(
                    skill
                )

    return found


def extract_soft_skills(
    text: str,
) -> list[str]:
    """
    Extract known soft skills.
    """

    normalized = normalize_text(
        text
    ).lower()

    found: list[str] = []

    skills = sorted(
        SOFT_SKILLS,
        key=len,
        reverse=True,
    )

    for skill in skills:

        if re.search(
            _skill_pattern(skill),
            normalized,
            re.IGNORECASE,
        ):
            if skill not in found:
                found.append(
                    skill
                )

    return found


# ============================================================================
# Experience Extraction
# ============================================================================


def extract_experience_years(
    text: str,
) -> list[dict[str, Any]]:
    """
    Extract years of experience.

    Examples:
        3 years experience
        3+ years experience
        2-5 years experience
        4 years of Python experience
    """

    normalized = normalize_text(
        text
    )

    results: list[dict[str, Any]] = []

    for match in EXPERIENCE_PATTERN.finditer(
        normalized
    ):

        min_years = float(
            match.group("min")
        )

        max_group = match.group(
            "max"
        )

        max_years = (
            float(max_group)
            if max_group
            else None
        )

        results.append(
            {
                "min_years": min_years,
                "max_years": max_years,
                "text": match.group(0),
            }
        )

    # Fallback for "5+ years".
    if not results:

        for match in EXPERIENCE_GENERAL_PATTERN.finditer(
            normalized
        ):

            min_years = float(
                match.group(1)
            )

            results.append(
                {
                    "min_years": min_years,
                    "max_years": None,
                    "text": match.group(0),
                }
            )

    return results


# ============================================================================
# Education Extraction
# ============================================================================


def extract_education(
    text: str,
) -> list[str]:
    """
    Extract education-related requirements.
    """

    normalized = normalize_text(
        text
    )

    results: list[str] = []

    education_patterns = [
        r"(?:bachelor(?:'s)?|b\.?tech|b\.?e\.?|bca)"
        r"(?:\s+(?:degree|in|of)\s+[^,.;]+)?",

        r"(?:master(?:'s)?|m\.?tech|m\.?e\.?|mca|mba)"
        r"(?:\s+(?:degree|in|of)\s+[^,.;]+)?",

        r"(?:ph\.?d\.?|doctorate)"
        r"(?:\s+(?:degree|in|of)\s+[^,.;]+)?",

        r"(?:degree)\s+in\s+[^,.;]+",

        r"(?:computer science|information technology)"
        r"(?:\s+degree)?",
    ]

    for pattern in education_patterns:

        matches = re.findall(
            pattern,
            normalized,
            re.IGNORECASE,
        )

        for match in matches:

            if isinstance(
                match,
                tuple,
            ):
                value = next(
                    (
                        item
                        for item in match
                        if item
                    ),
                    "",
                )
            else:
                value = match

            value = normalize_text(
                value
            )

            if (
                value
                and value.lower()
                not in {
                    item.lower()
                    for item in results
                }
            ):
                results.append(
                    value
                )

    return results


# ============================================================================
# Certification Extraction
# ============================================================================


def extract_certifications(
    text: str,
) -> list[str]:
    """
    Extract certification requirements.
    """

    normalized = normalize_text(
        text
    )

    results: list[str] = []

    patterns = [
        r"\bAWS Certified [A-Za-z0-9 \-]+",
        r"\bAzure Certified [A-Za-z0-9 \-]+",
        r"\bGoogle Cloud Certified [A-Za-z0-9 \-]+",
        r"\bCertified Kubernetes Administrator\b",
        r"\bCKA\b",
        r"\bCKAD\b",
        r"\bPMP\b",
        r"\bCertified Scrum Master\b",
        r"\bCompTIA [A-Za-z0-9\+\-]+",
        r"\bSecurity\+\b",
        r"\bNetwork\+\b",
        r"\bCISSP\b",
        r"\bCPA\b",
        r"\bcertification\b",
    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            normalized,
            re.IGNORECASE,
        )

        for match in matches:

            value = normalize_text(
                match
            )

            if (
                value
                and value.lower()
                not in {
                    item.lower()
                    for item in results
                }
            ):
                results.append(
                    value
                )

    return results


# ============================================================================
# Requirement Evidence
# ============================================================================


def calculate_confidence(
    text: str,
    category: str,
    priority: str,
) -> float:
    """
    Calculate extraction confidence.

    This is a heuristic confidence score, not a probability.
    """

    score = 0.55

    normalized = normalize_text(
        text
    ).lower()

    if category == TECHNICAL:
        score += 0.15

    elif category == EDUCATION:
        score += 0.12

    elif category == EXPERIENCE:
        score += 0.15

    elif category == CERTIFICATION:
        score += 0.12

    elif category == SOFT:
        score += 0.08

    if priority == REQUIRED:
        score += 0.10

    elif priority == PREFERRED:
        score += 0.05

    if len(normalized) > 20:
        score += 0.03

    if any(
        marker in normalized
        for marker in REQUIRED_MARKERS
    ):
        score += 0.04

    if any(
        marker in normalized
        for marker in PREFERRED_MARKERS
    ):
        score += 0.02

    return round(
        min(score, 0.99),
        2,
    )


def build_requirement(
    text: str,
    *,
    source_section: str | None = None,
    priority: str | None = None,
) -> Requirement:
    """
    Convert a raw requirement into a structured Requirement.
    """

    normalized = normalize_requirement(
        text
    )

    resolved_priority = (
        priority
        or detect_priority(
            normalized,
            source_section,
        )
    )

    category = detect_category(
        normalized
    )

    skills = extract_technical_skills(
        normalized
    )

    skill = (
        skills[0]
        if len(skills) == 1
        else None
    )

    years = extract_experience_years(
        normalized
    )

    years_min = None
    years_max = None

    if years:

        years_min = years[0][
            "min_years"
        ]

        years_max = years[0][
            "max_years"
        ]

    confidence = calculate_confidence(
        normalized,
        category,
        resolved_priority,
    )

    evidence: list[str] = []

    if skills:
        evidence.extend(
            skills
        )

    if years:
        evidence.append(
            years[0]["text"]
        )

    return Requirement(
        text=normalized,
        category=category,
        priority=resolved_priority,
        normalized=canonical_text(
            normalized
        ),
        skill=skill,
        years_min=years_min,
        years_max=years_max,
        source_section=source_section,
        confidence=confidence,
        evidence=evidence,
        metadata={
            "technical_skills": skills,
            "soft_skills": extract_soft_skills(
                normalized
            ),
            "education": extract_education(
                normalized
            ),
            "certifications": extract_certifications(
                normalized
            ),
        },
    )


# ============================================================================
# Deduplication
# ============================================================================


def deduplicate_requirements(
    requirements: Sequence[Requirement],
) -> list[Requirement]:
    """
    Deduplicate requirements while retaining the highest-confidence
    representation.
    """

    grouped: dict[str, Requirement] = {}

    for requirement in requirements:

        key = requirement.normalized

        if not key:
            continue

        existing = grouped.get(
            key
        )

        if existing is None:
            grouped[key] = requirement
            continue

        # Prefer higher confidence.
        if (
            requirement.confidence
            > existing.confidence
        ):
            grouped[key] = requirement

    return list(
        grouped.values()
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
    Support either:

        JobDescription object

    or:

        dictionary returned by JobDescription.to_dict()
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

    cleaned_text = getattr(
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
        str(cleaned_text),
        sections,
    )


# ============================================================================
# Main Extractor
# ============================================================================


class RequirementExtractor:
    """
    Main Job Description requirement extractor.

    Example:

        extractor = RequirementExtractor()

        result = extractor.extract(jd_text)

        print(result["technical_skills"])
        print(result["required"])
        print(result["preferred"])
    """

    def __init__(
        self,
        *,
        include_general: bool = True,
        min_confidence: float = 0.0,
    ) -> None:

        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError(
                "min_confidence must be between 0 and 1."
            )

        self.include_general = (
            include_general
        )

        self.min_confidence = (
            min_confidence
        )

    def _collect_source_items(
        self,
        text: str,
        sections: Mapping[str, Any] | None,
    ) -> list[
        tuple[str, str | None]
    ]:
        """
        Collect candidate requirement lines.

        Uses structured JD sections when available.
        Otherwise splits raw text into lines.
        """

        items: list[
            tuple[str, str | None]
        ] = []

        if sections:

            target_sections = {
                "requirements",
                "qualifications",
                "skills",
                "experience",
                "education",
                "preferred",
            }

            for section_name, section in sections.items():

                normalized_section = (
                    str(section_name)
                    .lower()
                )

                if normalized_section not in target_sections:
                    continue

                # JDSection object.
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
                        []
                    )

                if section_items:

                    for item in section_items:

                        items.append(
                            (
                                str(item),
                                normalized_section,
                            )
                        )

                    continue

                # Fallback to section content.
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

                    for line in str(
                        content
                    ).splitlines():

                        if normalize_text(line):
                            items.append(
                                (
                                    line,
                                    normalized_section,
                                )
                            )

        if items:
            return items

        # Raw-text fallback.
        for line in text.splitlines():

            line = normalize_requirement(
                line
            )

            if not line:
                continue

            # Ignore obvious headings.
            if (
                len(line.split())
                <= 6
                and line.endswith(":")
            ):
                continue

            items.append(
                (
                    line,
                    None,
                )
            )

        return items

    def extract(
        self,
        jd: Any,
    ) -> RequirementExtraction:
        """
        Extract structured requirements.
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
            return RequirementExtraction(
                metadata={
                    "empty": True,
                    "requirement_count": 0,
                }
            )

        source_items = (
            self._collect_source_items(
                text,
                sections,
            )
        )

        requirements: list[
            Requirement
        ] = []

        for raw_item, section in source_items:

            requirement = build_requirement(
                raw_item,
                source_section=section,
            )

            if (
                requirement.confidence
                < self.min_confidence
            ):
                continue

            # General requirements can be disabled.
            if (
                requirement.category
                == OTHER
                and not self.include_general
            ):
                continue

            requirements.append(
                requirement
            )

        requirements = (
            deduplicate_requirements(
                requirements
            )
        )

        # --------------------------------------------------------------
        # Priority groups
        # --------------------------------------------------------------

        required = [
            item
            for item in requirements
            if item.priority == REQUIRED
        ]

        preferred = [
            item
            for item in requirements
            if item.priority == PREFERRED
        ]

        general = [
            item
            for item in requirements
            if item.priority == GENERAL
        ]

        # --------------------------------------------------------------
        # Skills
        # --------------------------------------------------------------

        technical_skills: list[str] = []

        soft_skills: list[str] = []

        education: list[str] = []

        experience: list[str] = []

        certifications: list[str] = []

        years_of_experience: list[
            dict[str, Any]
        ] = []

        for requirement in requirements:

            technical_skills.extend(
                requirement.metadata.get(
                    "technical_skills",
                    [],
                )
            )

            soft_skills.extend(
                requirement.metadata.get(
                    "soft_skills",
                    [],
                )
            )

            education.extend(
                requirement.metadata.get(
                    "education",
                    [],
                )
            )

            certifications.extend(
                requirement.metadata.get(
                    "certifications",
                    [],
                )
            )

            if (
                requirement.category
                == EXPERIENCE
            ):

                experience.append(
                    requirement.text
                )

                if (
                    requirement.years_min
                    is not None
                ):
                    years_of_experience.append(
                        {
                            "min_years": (
                                requirement.years_min
                            ),
                            "max_years": (
                                requirement.years_max
                            ),
                            "requirement": (
                                requirement.text
                            ),
                        }
                    )

        # --------------------------------------------------------------
        # Deduplicate lists
        # --------------------------------------------------------------

        technical_skills = (
            self._unique_strings(
                technical_skills
            )
        )

        soft_skills = (
            self._unique_strings(
                soft_skills
            )
        )

        education = (
            self._unique_strings(
                education
            )
        )

        experience = (
            self._unique_strings(
                experience
            )
        )

        certifications = (
            self._unique_strings(
                certifications
            )
        )

        # --------------------------------------------------------------
        # Metadata
        # --------------------------------------------------------------

        metadata = {
            "empty": False,
            "requirement_count": len(
                requirements
            ),
            "required_count": len(
                required
            ),
            "preferred_count": len(
                preferred
            ),
            "general_count": len(
                general
            ),
            "technical_skill_count": len(
                technical_skills
            ),
            "soft_skill_count": len(
                soft_skills
            ),
            "education_count": len(
                education
            ),
            "experience_count": len(
                experience
            ),
            "certification_count": len(
                certifications
            ),
            "source": (
                "parsed_sections"
                if sections
                else "raw_text"
            ),
        }

        return RequirementExtraction(
            required=required,
            preferred=preferred,
            general=general,
            technical_skills=technical_skills,
            soft_skills=soft_skills,
            education_requirements=education,
            experience_requirements=experience,
            certifications=certifications,
            years_of_experience=(
                years_of_experience
            ),
            all_requirements=requirements,
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
        Return JSON-compatible result.
        """

        return self.extract(
            jd
        ).to_dict()


# ============================================================================
# Functional API
# ============================================================================


_default_extractor: RequirementExtractor | None = None


def get_default_extractor() -> RequirementExtractor:
    """
    Return lazily-created default extractor.
    """

    global _default_extractor

    if _default_extractor is None:
        _default_extractor = (
            RequirementExtractor()
        )

    return _default_extractor


def extract_requirements(
    jd: Any,
) -> RequirementExtraction:
    """
    Functional extraction API.
    """

    return get_default_extractor().extract(
        jd
    )


def extract_requirements_dict(
    jd: Any,
) -> dict[str, Any]:
    """
    Functional dictionary API.
    """

    return get_default_extractor().extract_dict(
        jd
    )


def extract_required_skills(
    jd: Any,
) -> list[str]:
    """
    Return technical skills appearing in
    required requirements.
    """

    result = extract_requirements(
        jd
    )

    skills: list[str] = []

    for requirement in result.required:

        skills.extend(
            requirement.metadata.get(
                "technical_skills",
                [],
            )
        )

    return list(
        dict.fromkeys(
            skills
        )
    )


def extract_preferred_skills(
    jd: Any,
) -> list[str]:
    """
    Return technical skills appearing in
    preferred requirements.
    """

    result = extract_requirements(
        jd
    )

    skills: list[str] = []

    for requirement in result.preferred:

        skills.extend(
            requirement.metadata.get(
                "technical_skills",
                [],
            )
        )

    return list(
        dict.fromkeys(
            skills
        )
    )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "REQUIRED",
    "PREFERRED",
    "GENERAL",
    "TECHNICAL",
    "SOFT",
    "EDUCATION",
    "EXPERIENCE",
    "CERTIFICATION",
    "OTHER",
    "Requirement",
    "RequirementExtraction",
    "RequirementExtractor",
    "normalize_text",
    "normalize_requirement",
    "canonical_text",
    "detect_priority",
    "detect_category",
    "extract_technical_skills",
    "extract_soft_skills",
    "extract_experience_years",
    "extract_education",
    "extract_certifications",
    "calculate_confidence",
    "build_requirement",
    "deduplicate_requirements",
    "get_default_extractor",
    "extract_requirements",
    "extract_requirements_dict",
    "extract_required_skills",
    "extract_preferred_skills",
]