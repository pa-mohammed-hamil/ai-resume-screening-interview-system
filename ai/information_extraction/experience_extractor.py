# Project scaffold file
"""
Resume Entity Extractor
=======================

Location:
    ai/information_extraction/entity_extractor.py

Purpose:
    Extract named entities and resume-specific entities from
    raw resume text.

Supported entities:
    - PERSON
    - ORGANIZATION
    - LOCATION
    - DATE
    - EMAIL
    - PHONE
    - URL
    - LINKEDIN
    - GITHUB
    - JOB_TITLE
    - DEGREE
    - SKILL
    - TECHNOLOGY
    - CERTIFICATION

The extractor is designed to work without requiring a heavy NLP
model. If spaCy is installed and a compatible model is available,
it can optionally use spaCy for general named-entity extraction.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence


# ============================================================================
# Regular Expressions
# ============================================================================

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@"
    r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    re.IGNORECASE,
)

PHONE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:\+?\d{1,3}[\s.-]?)?"
    r"(?:\(?\d{2,5}\)?[\s.-]?)?"
    r"\d{3,5}[\s.-]?\d{3,5}"
    r"(?!\d)"
)

URL_PATTERN = re.compile(
    r"\b(?:https?://|www\.)"
    r"[^\s<>()]+",
    re.IGNORECASE,
)

LINKEDIN_PATTERN = re.compile(
    r"(?:https?://)?"
    r"(?:www\.)?"
    r"linkedin\.com/[^\s<>()]+",
    re.IGNORECASE,
)

GITHUB_PATTERN = re.compile(
    r"(?:https?://)?"
    r"(?:www\.)?"
    r"github\.com/[^\s<>()]+",
    re.IGNORECASE,
)

DATE_PATTERN = re.compile(
    r"\b(?:"
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
    r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
    r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    r"\s+\d{4}"
    r"|"
    r"\d{1,2}[/-]\d{4}"
    r"|"
    r"\d{4}[/-]\d{1,2}"
    r"|"
    r"\d{4}"
    r")\b",
    re.IGNORECASE,
)


# ============================================================================
# Entity Vocabulary
# ============================================================================

SKILL_TERMS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "c",
    "c++",
    "c#",
    "go",
    "rust",
    "php",
    "ruby",
    "kotlin",
    "swift",
    "sql",
    "html",
    "css",
    "react",
    "react.js",
    "angular",
    "vue",
    "node.js",
    "nodejs",
    "express",
    "django",
    "flask",
    "fastapi",
    "spring",
    "spring boot",
    "postgresql",
    "mysql",
    "mongodb",
    "redis",
    "oracle",
    "sqlite",
    "aws",
    "azure",
    "gcp",
    "google cloud",
    "docker",
    "kubernetes",
    "terraform",
    "jenkins",
    "git",
    "github",
    "gitlab",
    "linux",
    "machine learning",
    "deep learning",
    "nlp",
    "natural language processing",
    "computer vision",
    "generative ai",
    "genai",
    "llm",
    "large language models",
    "openai",
    "langchain",
    "langgraph",
    "pytorch",
    "tensorflow",
    "scikit-learn",
    "sklearn",
    "pandas",
    "numpy",
    "spark",
    "hadoop",
    "tableau",
    "power bi",
    "excel",
    "rest api",
    "graphql",
    "microservices",
    "api",
    "rest",
}


TECHNOLOGY_TERMS = {
    "python",
    "java",
    "javascript",
    "typescript",
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
    "oracle",
    "sqlite",
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
    "linux",
    "pytorch",
    "tensorflow",
    "scikit-learn",
    "pandas",
    "numpy",
    "spark",
    "hadoop",
    "tableau",
    "power bi",
    "langchain",
    "langgraph",
    "openai",
}


DEGREE_TERMS = {
    "b.tech",
    "btech",
    "b.e",
    "be",
    "b.sc",
    "bsc",
    "bca",
    "bba",
    "m.tech",
    "mtech",
    "m.e",
    "me",
    "m.sc",
    "msc",
    "mca",
    "mba",
    "phd",
    "ph.d",
    "doctor of philosophy",
    "master of science",
    "master of technology",
    "master of business administration",
    "bachelor of technology",
    "bachelor of engineering",
    "bachelor of science",
    "bachelor of computer applications",
}


JOB_TITLE_TERMS = {
    "software engineer",
    "software developer",
    "backend developer",
    "backend engineer",
    "frontend developer",
    "frontend engineer",
    "full stack developer",
    "full stack engineer",
    "python developer",
    "java developer",
    "data scientist",
    "data analyst",
    "machine learning engineer",
    "ml engineer",
    "ai engineer",
    "ai developer",
    "generative ai engineer",
    "genai developer",
    "devops engineer",
    "cloud engineer",
    "data engineer",
    "database administrator",
    "product manager",
    "project manager",
    "business analyst",
    "qa engineer",
    "test engineer",
    "technical lead",
    "team lead",
    "engineering manager",
    "software architect",
    "solution architect",
    "intern",
    "developer",
    "engineer",
}


CERTIFICATION_TERMS = {
    "aws certified",
    "azure certification",
    "google cloud certification",
    "pmp",
    "scrum master",
    "cissp",
    "comptia",
    "oracle certified",
    "certified kubernetes administrator",
    "cka",
    "tensorflow developer",
}


# ============================================================================
# Data Models
# ============================================================================


@dataclass
class Entity:
    """Represents a single extracted entity."""

    text: str
    label: str
    start: int | None = None
    end: int | None = None
    confidence: float = 1.0
    source: str = "regex"

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "label": self.label,
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence,
            "source": self.source,
        }


@dataclass
class EntityExtractionResult:
    """Structured entity extraction result."""

    entities: list[Entity] = field(
        default_factory=list
    )

    grouped: dict[str, list[str]] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "entities": [
                entity.to_dict()
                for entity in self.entities
            ],
            "grouped": self.grouped,
        }


# ============================================================================
# Utility Functions
# ============================================================================


def normalize_text(value: Any) -> str:
    """Normalize whitespace and common Unicode spaces."""

    if value is None:
        return ""

    text = str(value)

    text = text.replace(
        "\u00a0",
        " ",
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    return text.strip()


def normalize_entity(value: str) -> str:
    """Normalize an entity value."""

    value = normalize_text(value)

    value = value.strip(
        ".,;:|()[]{}<>\"'"
    )

    return value.strip()


def unique_strings(
    values: Iterable[str],
) -> list[str]:
    """Deduplicate strings while preserving order."""

    result: list[str] = []
    seen: set[str] = set()

    for value in values:

        value = normalize_entity(value)

        if not value:
            continue

        key = value.lower()

        if key in seen:
            continue

        seen.add(key)
        result.append(value)

    return result


# ============================================================================
# Entity Extractor
# ============================================================================


class EntityExtractor:
    """
    Extract entities from resume text.

    Usage:

        extractor = EntityExtractor()

        result = extractor.extract(text)

    Result:

        {
            "PERSON": [...],
            "EMAIL": [...],
            "PHONE": [...],
            "SKILL": [...],
            "TECHNOLOGY": [...],
            ...
        }
    """

    def __init__(
        self,
        *,
        use_spacy: bool = True,
        spacy_model: str = "en_core_web_sm",
        custom_skills: Iterable[str] | None = None,
        custom_job_titles: Iterable[str] | None = None,
    ) -> None:

        self.use_spacy = use_spacy
        self.spacy_model = spacy_model

        self.skills = set(
            SKILL_TERMS
        )

        self.technologies = set(
            TECHNOLOGY_TERMS
        )

        self.degrees = set(
            DEGREE_TERMS
        )

        self.job_titles = set(
            JOB_TITLE_TERMS
        )

        self.certifications = set(
            CERTIFICATION_TERMS
        )

        if custom_skills:
            self.skills.update(
                str(item).lower()
                for item in custom_skills
            )

        if custom_job_titles:
            self.job_titles.update(
                str(item).lower()
                for item in custom_job_titles
            )

        self.nlp = None

        if self.use_spacy:
            self._load_spacy()

    # ------------------------------------------------------------------
    # spaCy
    # ------------------------------------------------------------------

    def _load_spacy(self) -> None:
        """Load spaCy model if available."""

        try:
            import spacy

            self.nlp = spacy.load(
                self.spacy_model
            )

        except (
            ImportError,
            OSError,
            Exception,
        ):
            self.nlp = None

    # ------------------------------------------------------------------
    # Regex extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _regex_entities(
        text: str,
        pattern: re.Pattern[str],
        label: str,
        confidence: float = 0.98,
    ) -> list[Entity]:
        """Extract entities using a regular expression."""

        result: list[Entity] = []

        for match in pattern.finditer(text):

            value = normalize_entity(
                match.group(0)
            )

            if not value:
                continue

            result.append(
                Entity(
                    text=value,
                    label=label,
                    start=match.start(),
                    end=match.end(),
                    confidence=confidence,
                    source="regex",
                )
            )

        return result

    def extract_contact_entities(
        self,
        text: str,
    ) -> list[Entity]:
        """Extract email, phone, URL and social links."""

        entities: list[Entity] = []

        entities.extend(
            self._regex_entities(
                text,
                EMAIL_PATTERN,
                "EMAIL",
                0.99,
            )
        )

        entities.extend(
            self._regex_entities(
                text,
                PHONE_PATTERN,
                "PHONE",
                0.90,
            )
        )

        entities.extend(
            self._regex_entities(
                text,
                LINKEDIN_PATTERN,
                "LINKEDIN",
                0.99,
            )
        )

        entities.extend(
            self._regex_entities(
                text,
                GITHUB_PATTERN,
                "GITHUB",
                0.99,
            )
        )

        entities.extend(
            self._regex_entities(
                text,
                URL_PATTERN,
                "URL",
                0.97,
            )
        )

        return entities

    # ------------------------------------------------------------------
    # Vocabulary matching
    # ------------------------------------------------------------------

    def _find_terms(
        self,
        text: str,
        terms: Iterable[str],
        label: str,
        confidence: float = 0.95,
    ) -> list[Entity]:
        """Find known vocabulary terms in text."""

        entities: list[Entity] = []

        sorted_terms = sorted(
            set(terms),
            key=len,
            reverse=True,
        )

        for term in sorted_terms:

            term = normalize_text(term)

            if not term:
                continue

            pattern = re.compile(
                r"(?<!\w)"
                + re.escape(term)
                + r"(?!\w)",
                re.IGNORECASE,
            )

            for match in pattern.finditer(
                text
            ):

                value = normalize_entity(
                    match.group(0)
                )

                if not value:
                    continue

                entities.append(
                    Entity(
                        text=value,
                        label=label,
                        start=match.start(),
                        end=match.end(),
                        confidence=confidence,
                        source="vocabulary",
                    )
                )

        return entities

    def extract_skills(
        self,
        text: str,
    ) -> list[Entity]:
        """Extract known technical and professional skills."""

        return self._find_terms(
            text,
            self.skills,
            "SKILL",
            0.96,
        )

    def extract_technologies(
        self,
        text: str,
    ) -> list[Entity]:
        """Extract technology names."""

        return self._find_terms(
            text,
            self.technologies,
            "TECHNOLOGY",
            0.97,
        )

    def extract_degrees(
        self,
        text: str,
    ) -> list[Entity]:
        """Extract academic degree terms."""

        return self._find_terms(
            text,
            self.degrees,
            "DEGREE",
            0.94,
        )

    def extract_job_titles(
        self,
        text: str,
    ) -> list[Entity]:
        """Extract common job titles."""

        return self._find_terms(
            text,
            self.job_titles,
            "JOB_TITLE",
            0.91,
        )

    def extract_certifications(
        self,
        text: str,
    ) -> list[Entity]:
        """Extract known certifications."""

        return self._find_terms(
            text,
            self.certifications,
            "CERTIFICATION",
            0.93,
        )

    def extract_dates(
        self,
        text: str,
    ) -> list[Entity]:
        """Extract dates and years."""

        return self._regex_entities(
            text,
            DATE_PATTERN,
            "DATE",
            0.94,
        )

    # ------------------------------------------------------------------
    # spaCy entities
    # ------------------------------------------------------------------

    def extract_spacy_entities(
        self,
        text: str,
    ) -> list[Entity]:
        """Extract general named entities using spaCy."""

        if self.nlp is None:
            return []

        try:
            document = self.nlp(
                text
            )

        except Exception:
            return []

        result: list[Entity] = []

        allowed_labels = {
            "PERSON",
            "ORG",
            "GPE",
            "LOC",
            "FAC",
            "DATE",
            "NORP",
            "EVENT",
            "PRODUCT",
        }

        label_mapping = {
            "ORG": "ORGANIZATION",
            "GPE": "LOCATION",
            "LOC": "LOCATION",
            "FAC": "LOCATION",
            "DATE": "DATE",
            "PERSON": "PERSON",
            "NORP": "GROUP",
            "EVENT": "EVENT",
            "PRODUCT": "PRODUCT",
        }

        for entity in document.ents:

            if entity.label_ not in allowed_labels:
                continue

            value = normalize_entity(
                entity.text
            )

            if not value:
                continue

            result.append(
                Entity(
                    text=value,
                    label=label_mapping.get(
                        entity.label_,
                        entity.label_,
                    ),
                    start=entity.start_char,
                    end=entity.end_char,
                    confidence=0.80,
                    source="spacy",
                )
            )

        return result

    # ------------------------------------------------------------------
    # Person name
    # ------------------------------------------------------------------

    def extract_person_name(
        self,
        text: str,
    ) -> list[Entity]:
        """
        Extract likely candidate name.

        First checks spaCy PERSON entities. If unavailable,
        examines the beginning of the resume.
        """

        entities: list[Entity] = []

        if self.nlp is not None:

            try:
                document = self.nlp(
                    text[:3000]
                )

                for entity in document.ents:

                    if entity.label_ != "PERSON":
                        continue

                    value = normalize_entity(
                        entity.text
                    )

                    if not value:
                        continue

                    entities.append(
                        Entity(
                            text=value,
                            label="PERSON",
                            start=entity.start_char,
                            end=entity.end_char,
                            confidence=0.88,
                            source="spacy",
                        )
                    )

            except Exception:
                pass

        if entities:
            return entities[:3]

        lines = [
            normalize_text(line)
            for line in text.splitlines()
            if normalize_text(line)
        ]

        for index, line in enumerate(
            lines[:8]
        ):

            if (
                "@" in line
                or "http" in line.lower()
                or re.search(
                    r"\d{4,}",
                    line,
                )
            ):
                continue

            words = line.split()

            if not 2 <= len(words) <= 5:
                continue

            if all(
                re.fullmatch(
                    r"[A-Za-z][A-Za-z.'-]*",
                    word,
                )
                for word in words
            ):

                return [
                    Entity(
                        text=line,
                        label="PERSON",
                        confidence=0.65,
                        source="heuristic",
                    )
                ]

        return []

    # ------------------------------------------------------------------
    # Deduplication
    # ------------------------------------------------------------------

    @staticmethod
    def _deduplicate_entities(
        entities: Iterable[Entity],
    ) -> list[Entity]:
        """Remove duplicate entities."""

        result: list[Entity] = []

        seen: set[
            tuple[str, str]
        ] = set()

        for entity in entities:

            key = (
                entity.label,
                entity.text.lower(),
            )

            if key in seen:
                continue

            seen.add(key)
            result.append(entity)

        return result

    # ------------------------------------------------------------------
    # Grouping
    # ------------------------------------------------------------------

    @staticmethod
    def group_entities(
        entities: Iterable[Entity],
    ) -> dict[str, list[str]]:
        """Group extracted entities by label."""

        grouped: dict[
            str,
            list[str],
        ] = {}

        for entity in entities:

            grouped.setdefault(
                entity.label,
                [],
            )

            grouped[
                entity.label
            ].append(
                entity.text
            )

        for label in grouped:

            grouped[label] = (
                unique_strings(
                    grouped[label]
                )
            )

        return grouped

    # ------------------------------------------------------------------
    # Main extraction
    # ------------------------------------------------------------------

    def extract_result(
        self,
        text: str,
    ) -> EntityExtractionResult:
        """
        Extract all supported entities.

        Returns an EntityExtractionResult.
        """

        text = normalize_text(
            text
        )

        if not text:
            return EntityExtractionResult()

        entities: list[Entity] = []

        # Contact information.
        entities.extend(
            self.extract_contact_entities(
                text
            )
        )

        # Dates.
        entities.extend(
            self.extract_dates(
                text
            )
        )

        # Vocabulary.
        entities.extend(
            self.extract_skills(
                text
            )
        )

        entities.extend(
            self.extract_technologies(
                text
            )
        )

        entities.extend(
            self.extract_degrees(
                text
            )
        )

        entities.extend(
            self.extract_job_titles(
                text
            )
        )

        entities.extend(
            self.extract_certifications(
                text
            )
        )

        # General NLP entities.
        entities.extend(
            self.extract_spacy_entities(
                text
            )
        )

        # Candidate name.
        entities.extend(
            self.extract_person_name(
                text
            )
        )

        entities = (
            self._deduplicate_entities(
                entities
            )
        )

        grouped = self.group_entities(
            entities
        )

        return EntityExtractionResult(
            entities=entities,
            grouped=grouped,
        )

    def extract(
        self,
        text: str,
    ) -> dict[str, list[str]]:
        """
        Main public API.

        Returns:

            {
                "PERSON": [...],
                "ORGANIZATION": [...],
                "LOCATION": [...],
                "EMAIL": [...],
                "PHONE": [...],
                "SKILL": [...],
                ...
            }
        """

        return self.extract_result(
            text
        ).grouped


# ============================================================================
# Alternative Class Name
# ============================================================================


ResumeEntityExtractor = EntityExtractor


# ============================================================================
# Convenience Function
# ============================================================================


_default_extractor: EntityExtractor | None = None


def get_default_extractor() -> EntityExtractor:
    """Return a shared EntityExtractor."""

    global _default_extractor

    if _default_extractor is None:
        _default_extractor = (
            EntityExtractor()
        )

    return _default_extractor


def extract_entities(
    text: str,
) -> dict[str, list[str]]:
    """Extract entities from resume text."""

    return get_default_extractor().extract(
        text
    )


def extract_entity_result(
    text: str,
) -> EntityExtractionResult:
    """Return the complete entity extraction result."""

    return get_default_extractor().extract_result(
        text
    )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "Entity",
    "EntityExtractionResult",
    "EntityExtractor",
    "ResumeEntityExtractor",
    "extract_entities",
    "extract_entity_result",
    "get_default_extractor",
]