# Project scaffold file
"""
Resume Information Extraction Orchestrator
===========================================

Location:
    ai/information_extraction/extractor.py

Purpose:
    Coordinate all resume information extraction modules.

Pipeline:

    Resume Text
        |
        +--> Contact Extractor
        +--> Entity Extractor
        +--> Education Extractor
        +--> Experience Extractor
        |
        v
    Structured Resume Information
        |
        +--> Skill Intelligence
        +--> Resume Scoring
        +--> Resume/Job Matching
        +--> Candidate Ranking
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Sequence


# ============================================================================
# Utility Functions
# ============================================================================


def normalize_text(value: Any) -> str:
    """Convert input into normalized text."""

    if value is None:
        return ""

    text = str(value)

    text = text.replace("\u00a0", " ")

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


def clean_list(
    values: Any,
) -> list[str]:
    """Normalize and deduplicate a list of values."""

    if values is None:
        return []

    if isinstance(values, str):
        values = [values]

    if not isinstance(values, Sequence):
        return []

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


def get_value(
    data: Any,
    keys: Sequence[str],
    default: Any = None,
) -> Any:
    """Get a value from either a mapping or an object."""

    if isinstance(data, Mapping):

        for key in keys:

            if key in data:
                return data[key]

        return default

    for key in keys:

        if hasattr(data, key):
            return getattr(
                data,
                key,
            )

    return default


def extract_text(
    resume: Any,
) -> str:
    """
    Extract resume text from common input formats.

    Supports:
        - str
        - dict
        - parsed resume objects
    """

    if isinstance(resume, str):
        return normalize_text(resume)

    value = get_value(
        resume,
        (
            "cleaned_text",
            "text",
            "raw_text",
            "content",
            "extracted_text",
        ),
    )

    return normalize_text(value)


# ============================================================================
# Result Models
# ============================================================================


@dataclass
class ContactInformation:
    """Candidate contact information."""

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EducationInformation:
    """Candidate education information."""

    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    grade: str | None = None
    raw_text: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExperienceInformation:
    """Candidate professional experience."""

    company: str | None = None
    title: str | None = None
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    achievements: list[str] = field(
        default_factory=list
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResumeExtractionResult:
    """Complete structured resume extraction."""

    contact: ContactInformation = field(
        default_factory=ContactInformation
    )

    entities: dict[str, list[str]] = field(
        default_factory=dict
    )

    education: list[EducationInformation] = field(
        default_factory=list
    )

    experience: list[ExperienceInformation] = field(
        default_factory=list
    )

    skills: list[str] = field(
        default_factory=list
    )

    sections: dict[str, str] = field(
        default_factory=dict
    )

    summary: str | None = None

    certifications: list[str] = field(
        default_factory=list
    )

    projects: list[str] = field(
        default_factory=list
    )

    languages: list[str] = field(
        default_factory=list
    )

    extraction_metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "contact": self.contact.to_dict(),
            "entities": self.entities,
            "education": [
                item.to_dict()
                for item in self.education
            ],
            "experience": [
                item.to_dict()
                for item in self.experience
            ],
            "skills": self.skills,
            "sections": self.sections,
            "summary": self.summary,
            "certifications": self.certifications,
            "projects": self.projects,
            "languages": self.languages,
            "extraction_metadata": self.extraction_metadata,
        }


# ============================================================================
# Dynamic Import Helpers
# ============================================================================


def _load_contact_extractor():
    """Load contact extractor lazily."""

    try:
        from .contact_extractor import ContactExtractor

        return ContactExtractor
    except ImportError:
        return None


def _load_entity_extractor():
    """Load entity extractor lazily."""

    try:
        from .entity_extractor import EntityExtractor

        return EntityExtractor
    except ImportError:
        return None


def _load_education_extractor():
    """Load education extractor lazily."""

    try:
        from .education_extractor import EducationExtractor

        return EducationExtractor
    except ImportError:
        return None


def _load_experience_extractor():
    """Load experience extractor lazily."""

    try:
        from .experience_extractor import ExperienceExtractor

        return ExperienceExtractor
    except ImportError:
        return None


# ============================================================================
# Generic Extraction Helpers
# ============================================================================


SECTION_HEADERS = {
    "summary": {
        "summary",
        "professional summary",
        "profile",
        "objective",
        "career objective",
        "about me",
    },
    "skills": {
        "skills",
        "technical skills",
        "core skills",
        "key skills",
        "skills & technologies",
        "technical expertise",
    },
    "experience": {
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
    },
    "education": {
        "education",
        "academic background",
        "educational background",
        "academic qualifications",
    },
    "certifications": {
        "certifications",
        "certificates",
        "licenses & certifications",
    },
    "projects": {
        "projects",
        "personal projects",
        "academic projects",
        "key projects",
    },
    "languages": {
        "languages",
        "language skills",
    },
}


def canonical_section(
    header: str,
) -> str | None:
    """Convert a section heading into canonical name."""

    normalized = normalize_text(
        header
    ).lower()

    normalized = re.sub(
        r"[:\-]+$",
        "",
        normalized,
    )

    for canonical, aliases in SECTION_HEADERS.items():

        if normalized in aliases:
            return canonical

    return None


def extract_sections(
    text: str,
) -> dict[str, str]:
    """
    Extract common resume sections.

    This is a fallback section parser and is intentionally
    tolerant of different resume layouts.
    """

    lines = text.splitlines()

    sections: dict[str, list[str]] = {}

    current: str | None = None

    for line in lines:

        cleaned = normalize_text(line)

        if not cleaned:
            continue

        section = canonical_section(
            cleaned
        )

        if section:

            current = section

            sections.setdefault(
                section,
                [],
            )

            continue

        if current:

            sections[
                current
            ].append(cleaned)

    return {
        name: "\n".join(values).strip()
        for name, values in sections.items()
        if values
    }


def extract_summary(
    sections: Mapping[str, str],
) -> str | None:
    """Extract resume summary."""

    summary = sections.get(
        "summary"
    )

    if not summary:
        return None

    return normalize_text(summary)


def extract_certifications(
    sections: Mapping[str, str],
) -> list[str]:
    """Fallback certification extraction."""

    text = sections.get(
        "certifications",
        "",
    )

    if not text:
        return []

    lines = [
        normalize_text(line)
        for line in text.splitlines()
        if normalize_text(line)
    ]

    if len(lines) == 1:
        parts = re.split(
            r"[,;|]",
            lines[0],
        )

        return clean_list(parts)

    return clean_list(lines)


def extract_projects(
    sections: Mapping[str, str],
) -> list[str]:
    """Fallback project extraction."""

    text = sections.get(
        "projects",
        "",
    )

    if not text:
        return []

    lines = [
        normalize_text(line)
        for line in text.splitlines()
        if normalize_text(line)
    ]

    return clean_list(lines)


def extract_languages(
    sections: Mapping[str, str],
) -> list[str]:
    """Fallback language extraction."""

    text = sections.get(
        "languages",
        "",
    )

    if not text:
        return []

    return clean_list(
        re.split(
            r"[,;|\n]",
            text,
        )
    )


# ============================================================================
# Skills Fallback
# ============================================================================


COMMON_SKILLS = (
    "python",
    "java",
    "javascript",
    "typescript",
    "c",
    "c++",
    "c#",
    "go",
    "rust",
    "sql",
    "html",
    "css",
    "react",
    "angular",
    "vue",
    "node.js",
    "nodejs",
    "django",
    "flask",
    "fastapi",
    "spring",
    "spring boot",
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
    "gitlab",
    "machine learning",
    "deep learning",
    "nlp",
    "natural language processing",
    "generative ai",
    "genai",
    "llm",
    "openai",
    "langchain",
    "pytorch",
    "tensorflow",
    "scikit-learn",
    "pandas",
    "numpy",
    "spark",
    "hadoop",
    "tableau",
    "power bi",
    "excel",
)


def fallback_extract_skills(
    text: str,
) -> list[str]:
    """Extract common skills when SkillExtractor is unavailable."""

    normalized = text.lower()

    found: list[str] = []

    for skill in COMMON_SKILLS:

        pattern = (
            r"(?<!\w)"
            + re.escape(skill.lower())
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            normalized,
        ):
            found.append(skill)

    return clean_list(found)


# ============================================================================
# Output Normalization
# ============================================================================


def normalize_contact(
    value: Any,
) -> ContactInformation:
    """Normalize contact extractor output."""

    if isinstance(
        value,
        ContactInformation,
    ):
        return value

    if value is None:
        return ContactInformation()

    return ContactInformation(
        name=normalize_text(
            get_value(
                value,
                ("name", "full_name"),
            )
        )
        or None,
        email=normalize_text(
            get_value(
                value,
                ("email", "email_address"),
            )
        )
        or None,
        phone=normalize_text(
            get_value(
                value,
                ("phone", "phone_number"),
            )
        )
        or None,
        location=normalize_text(
            get_value(
                value,
                ("location", "address", "city"),
            )
        )
        or None,
        linkedin=normalize_text(
            get_value(
                value,
                ("linkedin", "linkedin_url"),
            )
        )
        or None,
        github=normalize_text(
            get_value(
                value,
                ("github", "github_url"),
            )
        )
        or None,
        portfolio=normalize_text(
            get_value(
                value,
                (
                    "portfolio",
                    "portfolio_url",
                    "website",
                ),
            )
        )
        or None,
    )


def normalize_education(
    value: Any,
) -> list[EducationInformation]:
    """Normalize education extractor output."""

    if value is None:
        return []

    if not isinstance(
        value,
        Sequence,
    ) or isinstance(
        value,
        (str, bytes),
    ):
        value = [value]

    result: list[
        EducationInformation
    ] = []

    for item in value:

        if isinstance(
            item,
            EducationInformation,
        ):
            result.append(item)
            continue

        result.append(
            EducationInformation(
                institution=normalize_text(
                    get_value(
                        item,
                        (
                            "institution",
                            "university",
                            "college",
                            "school",
                        ),
                    )
                )
                or None,
                degree=normalize_text(
                    get_value(
                        item,
                        ("degree",),
                    )
                )
                or None,
                field_of_study=normalize_text(
                    get_value(
                        item,
                        (
                            "field_of_study",
                            "field",
                            "major",
                        ),
                    )
                )
                or None,
                start_date=normalize_text(
                    get_value(
                        item,
                        (
                            "start_date",
                            "from_date",
                        ),
                    )
                )
                or None,
                end_date=normalize_text(
                    get_value(
                        item,
                        (
                            "end_date",
                            "graduation_date",
                            "to_date",
                        ),
                    )
                )
                or None,
                grade=normalize_text(
                    get_value(
                        item,
                        (
                            "grade",
                            "gpa",
                            "percentage",
                        ),
                    )
                )
                or None,
                raw_text=normalize_text(
                    get_value(
                        item,
                        ("raw_text", "text"),
                    )
                )
                or None,
            )
        )

    return result


def normalize_experience(
    value: Any,
) -> list[ExperienceInformation]:
    """Normalize experience extractor output."""

    if value is None:
        return []

    if not isinstance(
        value,
        Sequence,
    ) or isinstance(
        value,
        (str, bytes),
    ):
        value = [value]

    result: list[
        ExperienceInformation
    ] = []

    for item in value:

        if isinstance(
            item,
            ExperienceInformation,
        ):
            result.append(item)
            continue

        achievements = get_value(
            item,
            (
                "achievements",
                "highlights",
                "accomplishments",
            ),
            [],
        )

        result.append(
            ExperienceInformation(
                company=normalize_text(
                    get_value(
                        item,
                        (
                            "company",
                            "organization",
                            "employer",
                        ),
                    )
                )
                or None,
                title=normalize_text(
                    get_value(
                        item,
                        (
                            "title",
                            "job_title",
                            "position",
                            "role",
                        ),
                    )
                )
                or None,
                location=normalize_text(
                    get_value(
                        item,
                        ("location",),
                    )
                )
                or None,
                start_date=normalize_text(
                    get_value(
                        item,
                        (
                            "start_date",
                            "from_date",
                        ),
                    )
                )
                or None,
                end_date=normalize_text(
                    get_value(
                        item,
                        (
                            "end_date",
                            "to_date",
                        ),
                    )
                )
                or None,
                description=normalize_text(
                    get_value(
                        item,
                        (
                            "description",
                            "summary",
                            "details",
                        ),
                    )
                )
                or None,
                achievements=clean_list(
                    achievements
                ),
            )
        )

    return result


# ============================================================================
# Main Extractor
# ============================================================================


class InformationExtractor:
    """
    Main resume information extraction orchestrator.

    It delegates specialized extraction to:

        ContactExtractor
        EntityExtractor
        EducationExtractor
        ExperienceExtractor

    and provides fallback extraction when a specialized
    extractor is unavailable.
    """

    def __init__(
        self,
        *,
        contact_extractor: Any = None,
        entity_extractor: Any = None,
        education_extractor: Any = None,
        experience_extractor: Any = None,
        skill_extractor: Any = None,
    ) -> None:

        self.contact_extractor = (
            contact_extractor
        )

        self.entity_extractor = (
            entity_extractor
        )

        self.education_extractor = (
            education_extractor
        )

        self.experience_extractor = (
            experience_extractor
        )

        self.skill_extractor = (
            skill_extractor
        )

        self._initialize_default_extractors()

    def _initialize_default_extractors(
        self,
    ) -> None:
        """Initialize available specialized extractors."""

        if self.contact_extractor is None:

            extractor_cls = (
                _load_contact_extractor()
            )

            if extractor_cls:

                try:
                    self.contact_extractor = (
                        extractor_cls()
                    )
                except Exception:
                    self.contact_extractor = None

        if self.entity_extractor is None:

            extractor_cls = (
                _load_entity_extractor()
            )

            if extractor_cls:

                try:
                    self.entity_extractor = (
                        extractor_cls()
                    )
                except Exception:
                    self.entity_extractor = None

        if self.education_extractor is None:

            extractor_cls = (
                _load_education_extractor()
            )

            if extractor_cls:

                try:
                    self.education_extractor = (
                        extractor_cls()
                    )
                except Exception:
                    self.education_extractor = None

        if self.experience_extractor is None:

            extractor_cls = (
                _load_experience_extractor()
            )

            if extractor_cls:

                try:
                    self.experience_extractor = (
                        extractor_cls()
                    )
                except Exception:
                    self.experience_extractor = None

    # ------------------------------------------------------------------
    # Generic invocation
    # ------------------------------------------------------------------

    @staticmethod
    def _invoke(
        extractor: Any,
        text: str,
    ) -> Any:
        """Invoke an extractor using common method names."""

        if extractor is None:
            return None

        methods = (
            "extract",
            "parse",
            "process",
            "run",
        )

        for method_name in methods:

            method = getattr(
                extractor,
                method_name,
                None,
            )

            if callable(method):

                try:
                    return method(text)
                except TypeError:
                    try:
                        return method(
                            text=text
                        )
                    except Exception:
                        continue
                except Exception:
                    continue

        if callable(extractor):

            try:
                return extractor(text)
            except Exception:
                return None

        return None

    # ------------------------------------------------------------------
    # Specialized extraction
    # ------------------------------------------------------------------

    def extract_contact(
        self,
        text: str,
    ) -> ContactInformation:
        """Extract contact information."""

        result = self._invoke(
            self.contact_extractor,
            text,
        )

        if result is not None:
            return normalize_contact(
                result
            )

        return ContactInformation()

    def extract_entities(
        self,
        text: str,
    ) -> dict[str, list[str]]:
        """Extract named entities."""

        result = self._invoke(
            self.entity_extractor,
            text,
        )

        if result is None:
            return {}

        if isinstance(
            result,
            Mapping,
        ):

            normalized: dict[
                str,
                list[str],
            ] = {}

            for key, values in result.items():

                if isinstance(
                    values,
                    (str, bytes),
                ):
                    values = [values]

                normalized[
                    str(key)
                ] = clean_list(
                    values
                    if isinstance(
                        values,
                        Sequence,
                    )
                    else [values]
                )

            return normalized

        return {}

    def extract_education(
        self,
        text: str,
    ) -> list[EducationInformation]:
        """Extract education history."""

        result = self._invoke(
            self.education_extractor,
            text,
        )

        return normalize_education(
            result
        )

    def extract_experience(
        self,
        text: str,
    ) -> list[ExperienceInformation]:
        """Extract professional experience."""

        result = self._invoke(
            self.experience_extractor,
            text,
        )

        return normalize_experience(
            result
        )

    def extract_skills(
        self,
        text: str,
    ) -> list[str]:
        """Extract skills."""

        result = self._invoke(
            self.skill_extractor,
            text,
        )

        if result is not None:

            if isinstance(
                result,
                Mapping,
            ):

                for key in (
                    "skills",
                    "technical_skills",
                    "extracted_skills",
                ):

                    if key in result:
                        return clean_list(
                            result[key]
                        )

            if isinstance(
                result,
                Sequence,
            ) and not isinstance(
                result,
                (str, bytes),
            ):
                return clean_list(
                    result
                )

        return fallback_extract_skills(
            text
        )

    # ------------------------------------------------------------------
    # Main pipeline
    # ------------------------------------------------------------------

    def extract(
        self,
        resume: Any,
    ) -> ResumeExtractionResult:
        """
        Extract all available information from a resume.
        """

        text = extract_text(
            resume
        )

        if not text:

            return ResumeExtractionResult(
                extraction_metadata={
                    "success": False,
                    "error": "No resume text provided.",
                    "text_length": 0,
                }
            )

        sections = extract_sections(
            text
        )

        contact = self.extract_contact(
            text
        )

        entities = self.extract_entities(
            text
        )

        education = self.extract_education(
            text
        )

        experience = self.extract_experience(
            text
        )

        skills = self.extract_skills(
            text
        )

        summary = extract_summary(
            sections
        )

        certifications = (
            extract_certifications(
                sections
            )
        )

        projects = extract_projects(
            sections
        )

        languages = extract_languages(
            sections
        )

        # Add useful fallback entities.
        if contact.name:
            entities.setdefault(
                "PERSON",
                [],
            )

            if contact.name not in entities[
                "PERSON"
            ]:
                entities[
                    "PERSON"
                ].insert(
                    0,
                    contact.name,
                )

        return ResumeExtractionResult(
            contact=contact,
            entities=entities,
            education=education,
            experience=experience,
            skills=skills,
            sections=sections,
            summary=summary,
            certifications=certifications,
            projects=projects,
            languages=languages,
            extraction_metadata={
                "success": True,
                "text_length": len(text),
                "word_count": len(
                    text.split()
                ),
                "section_count": len(
                    sections
                ),
                "education_count": len(
                    education
                ),
                "experience_count": len(
                    experience
                ),
                "skill_count": len(
                    skills
                ),
                "certification_count": len(
                    certifications
                ),
                "project_count": len(
                    projects
                ),
                "language_count": len(
                    languages
                ),
                "extractors": {
                    "contact": (
                        self.contact_extractor
                        is not None
                    ),
                    "entity": (
                        self.entity_extractor
                        is not None
                    ),
                    "education": (
                        self.education_extractor
                        is not None
                    ),
                    "experience": (
                        self.experience_extractor
                        is not None
                    ),
                    "skills": (
                        self.skill_extractor
                        is not None
                    ),
                },
            },
        )

    def extract_dict(
        self,
        resume: Any,
    ) -> dict[str, Any]:
        """Return extraction result as a dictionary."""

        return self.extract(
            resume
        ).to_dict()


# ============================================================================
# Alternative Class Name
# ============================================================================


ResumeInformationExtractor = (
    InformationExtractor
)


# ============================================================================
# Convenience Functions
# ============================================================================


_default_extractor: InformationExtractor | None = None


def get_default_extractor() -> InformationExtractor:
    """Return a shared extractor instance."""

    global _default_extractor

    if _default_extractor is None:
        _default_extractor = (
            InformationExtractor()
        )

    return _default_extractor


def extract_resume_information(
    resume: Any,
) -> ResumeExtractionResult:
    """Extract structured information from a resume."""

    return get_default_extractor().extract(
        resume
    )


def extract_resume_dict(
    resume: Any,
) -> dict[str, Any]:
    """Extract structured resume information as a dictionary."""

    return get_default_extractor().extract_dict(
        resume
    )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "ContactInformation",
    "EducationInformation",
    "ExperienceInformation",
    "ResumeExtractionResult",
    "InformationExtractor",
    "ResumeInformationExtractor",
    "normalize_text",
    "clean_list",
    "extract_text",
    "extract_sections",
    "extract_summary",
    "extract_certifications",
    "extract_projects",
    "extract_languages",
    "fallback_extract_skills",
    "get_default_extractor",
    "extract_resume_information",
    "extract_resume_dict",
]