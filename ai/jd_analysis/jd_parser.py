# Project scaffold file
"""
Job Description Parser
======================

Location:
    ai/jd_analysis/jd_parser.py

Purpose:
    Parse raw job descriptions into structured sections.

Responsibilities:
    - Clean and normalize JD text
    - Detect common JD sections
    - Extract title/company/location when available
    - Separate requirements, responsibilities, qualifications,
      skills, benefits, etc.
    - Preserve original text
    - Provide JSON-friendly output

This module focuses on parsing/segmentation.
Actual requirement extraction and scoring should be handled by:

    requirement_extractor.py
    responsibility_extractor.py
    jd_scorer.py
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Mapping, Sequence


# ============================================================================
# Constants
# ============================================================================

DEFAULT_SECTION = "general"

SECTION_ALIASES: dict[str, set[str]] = {
    "summary": {
        "summary",
        "job summary",
        "position summary",
        "role summary",
        "about the role",
        "about this role",
        "role overview",
        "job overview",
        "position overview",
        "overview",
    },
    "responsibilities": {
        "responsibilities",
        "responsibility",
        "key responsibilities",
        "primary responsibilities",
        "main responsibilities",
        "what you'll do",
        "what you will do",
        "what you'll be doing",
        "duties",
        "job duties",
        "roles and responsibilities",
    },
    "requirements": {
        "requirements",
        "requirement",
        "job requirements",
        "position requirements",
        "role requirements",
        "required qualifications",
        "required skills",
        "must have",
        "must-have",
        "essential qualifications",
        "essential skills",
    },
    "qualifications": {
        "qualifications",
        "qualification",
        "basic qualifications",
        "preferred qualifications",
        "desired qualifications",
        "candidate qualifications",
    },
    "skills": {
        "skills",
        "technical skills",
        "required skills",
        "core skills",
        "key skills",
        "technologies",
        "technology",
        "tech stack",
    },
    "experience": {
        "experience",
        "required experience",
        "professional experience",
        "work experience",
        "years of experience",
    },
    "education": {
        "education",
        "educational requirements",
        "educational qualifications",
        "academic qualifications",
        "degree requirements",
    },
    "preferred": {
        "preferred",
        "preferred skills",
        "preferred experience",
        "nice to have",
        "nice-to-have",
        "bonus qualifications",
        "additional qualifications",
        "desired skills",
    },
    "benefits": {
        "benefits",
        "employee benefits",
        "perks",
        "what we offer",
        "why join us",
        "compensation and benefits",
    },
    "company": {
        "about us",
        "about the company",
        "company",
        "company overview",
        "who we are",
    },
    "location": {
        "location",
        "job location",
        "work location",
        "office location",
    },
    "salary": {
        "salary",
        "compensation",
        "pay",
        "salary range",
        "compensation range",
    },
    "application": {
        "application",
        "how to apply",
        "apply",
        "application process",
    },
}


COMMON_TITLE_PATTERNS = [
    re.compile(
        r"^(?:job\s+title|position|role|title)\s*[:\-]\s*(.+)$",
        re.IGNORECASE,
    ),
]

COMMON_COMPANY_PATTERNS = [
    re.compile(
        r"^(?:company|employer|organization)\s*[:\-]\s*(.+)$",
        re.IGNORECASE,
    ),
]

COMMON_LOCATION_PATTERNS = [
    re.compile(
        r"^(?:location|job\s+location|work\s+location)\s*[:\-]\s*(.+)$",
        re.IGNORECASE,
    ),
]


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class JDSection:
    """Represents one parsed Job Description section."""

    name: str

    title: str

    content: str

    lines: list[str] = field(
        default_factory=list
    )

    items: list[str] = field(
        default_factory=list
    )

    start_line: int = 0

    end_line: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class JobDescription:
    """Structured representation of a Job Description."""

    raw_text: str

    cleaned_text: str

    title: str | None = None

    company: str | None = None

    location: str | None = None

    sections: dict[str, JDSection] = field(
        default_factory=dict
    )

    requirements: list[str] = field(
        default_factory=list
    )

    responsibilities: list[str] = field(
        default_factory=list
    )

    skills: list[str] = field(
        default_factory=list
    )

    qualifications: list[str] = field(
        default_factory=list
    )

    education: list[str] = field(
        default_factory=list
    )

    experience: list[str] = field(
        default_factory=list
    )

    preferred: list[str] = field(
        default_factory=list
    )

    benefits: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw_text": self.raw_text,
            "cleaned_text": self.cleaned_text,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "sections": {
                name: section.to_dict()
                for name, section in self.sections.items()
            },
            "requirements": self.requirements,
            "responsibilities": self.responsibilities,
            "skills": self.skills,
            "qualifications": self.qualifications,
            "education": self.education,
            "experience": self.experience,
            "preferred": self.preferred,
            "benefits": self.benefits,
            "metadata": self.metadata,
        }


# ============================================================================
# Text Cleaning
# ============================================================================


def normalize_line(
    line: str,
) -> str:
    """Normalize a single line."""

    line = line.replace(
        "\u00a0",
        " ",
    )

    line = line.replace(
        "\r",
        "",
    )

    line = re.sub(
        r"[ \t]+",
        " ",
        line,
    )

    return line.strip()


def clean_text(
    text: Any,
) -> str:
    """
    Clean and normalize complete JD text.
    """

    if text is None:
        return ""

    text = str(text)

    text = text.replace(
        "\r\n",
        "\n",
    )

    text = text.replace(
        "\r",
        "\n",
    )

    lines = [
        normalize_line(line)
        for line in text.split("\n")
    ]

    cleaned_lines: list[str] = []

    previous_blank = False

    for line in lines:

        if not line:

            if not previous_blank:
                cleaned_lines.append("")

            previous_blank = True
            continue

        cleaned_lines.append(line)

        previous_blank = False

    return "\n".join(
        cleaned_lines
    ).strip()


def split_lines(
    text: str,
) -> list[str]:
    """Return normalized non-empty lines."""

    return [
        normalize_line(line)
        for line in clean_text(text).splitlines()
        if normalize_line(line)
    ]


# ============================================================================
# Header Detection
# ============================================================================


def normalize_heading(
    heading: str,
) -> str:
    """
    Normalize section heading for comparison.
    """

    heading = normalize_line(
        heading
    )

    heading = heading.strip(
        " :-\t"
    )

    heading = re.sub(
        r"^[\d\.\)\-\:]+\s*",
        "",
        heading,
    )

    heading = heading.lower()

    return heading.strip()


def detect_section_name(
    heading: str,
) -> str | None:
    """
    Detect canonical section name.

    Examples:
        "Key Responsibilities" → responsibilities
        "Required Qualifications" → requirements
        "Nice to Have" → preferred
    """

    normalized = normalize_heading(
        heading
    )

    if not normalized:
        return None

    for canonical, aliases in SECTION_ALIASES.items():

        if normalized in aliases:
            return canonical

    return None


def looks_like_heading(
    line: str,
) -> bool:
    """
    Determine whether a line is likely to be a section heading.
    """

    line = normalize_line(
        line
    )

    if not line:
        return False

    if detect_section_name(line):
        return True

    # Colon-based labels.
    if re.match(
        r"^[A-Za-z][A-Za-z\s/&\-]{1,50}:$",
        line,
    ):
        return True

    # Short title-like lines.
    words = line.split()

    if len(words) <= 6:

        if line.endswith(":"):
            return True

        # Avoid treating long sentences as headings.
        if not re.search(
            r"[.!?]$",
            line,
        ):
            if line.isupper():
                return True

    return False


# ============================================================================
# Bullet Handling
# ============================================================================


BULLET_PATTERN = re.compile(
    r"^\s*(?:"
    r"[-*•▪◦‣➢]"
    r"|\d+[.)]"
    r"|[a-zA-Z][.)]"
    r")\s+"
)


def is_bullet(
    line: str,
) -> bool:
    """Return True when line looks like a bullet."""

    return bool(
        BULLET_PATTERN.match(
            line
        )
    )


def clean_bullet(
    line: str,
) -> str:
    """Remove bullet marker."""

    line = normalize_line(
        line
    )

    return BULLET_PATTERN.sub(
        "",
        line,
        count=1,
    ).strip()


def extract_items(
    lines: Sequence[str],
) -> list[str]:
    """
    Convert section lines into logical list items.

    Bullet lines become individual items.
    Non-bullet lines are preserved as paragraphs.
    """

    items: list[str] = []

    current: str | None = None

    for line in lines:

        line = normalize_line(
            line
        )

        if not line:
            continue

        if is_bullet(line):

            if current:
                items.append(
                    current.strip()
                )

            current = clean_bullet(
                line
            )

        else:

            if current:
                current += " " + line
            else:
                current = line

    if current:
        items.append(
            current.strip()
        )

    return items


# ============================================================================
# Header Metadata Extraction
# ============================================================================


def _extract_by_patterns(
    lines: Sequence[str],
    patterns: Sequence[re.Pattern[str]],
) -> str | None:

    for line in lines:

        for pattern in patterns:

            match = pattern.match(
                line
            )

            if match:

                value = match.group(
                    1
                ).strip()

                if value:
                    return value

    return None


def infer_title(
    lines: Sequence[str],
) -> str | None:
    """
    Infer job title.

    Priority:
        1. Explicit "Job Title:"
        2. First line if title-like
    """

    explicit = _extract_by_patterns(
        lines,
        COMMON_TITLE_PATTERNS,
    )

    if explicit:
        return explicit

    for line in lines[:10]:

        if detect_section_name(line):
            continue

        if is_bullet(line):
            continue

        if len(line) > 100:
            continue

        # Skip obvious metadata lines.
        if re.match(
            r"^(company|location|salary|employment type)\s*:",
            line,
            re.IGNORECASE,
        ):
            continue

        # A short first line is often the job title.
        if len(line.split()) <= 10:
            return line

    return None


def infer_company(
    lines: Sequence[str],
) -> str | None:
    """Extract company name when explicitly provided."""

    return _extract_by_patterns(
        lines,
        COMMON_COMPANY_PATTERNS,
    )


def infer_location(
    lines: Sequence[str],
) -> str | None:
    """Extract location when explicitly provided."""

    return _extract_by_patterns(
        lines,
        COMMON_LOCATION_PATTERNS,
    )


# ============================================================================
# Section Parsing
# ============================================================================


def parse_sections(
    text: str,
) -> dict[str, JDSection]:
    """
    Parse text into named sections.

    Unknown content before the first recognized heading is
    stored as "general".
    """

    lines = split_lines(
        text
    )

    sections: dict[str, JDSection] = {}

    current_name = DEFAULT_SECTION
    current_title = "General"
    current_lines: list[str] = []
    current_start = 0

    def flush_section(
        end_line: int,
    ) -> None:

        nonlocal current_lines

        if not current_lines:
            return

        content = "\n".join(
            current_lines
        ).strip()

        if not content:
            current_lines = []
            return

        items = extract_items(
            current_lines
        )

        section = JDSection(
            name=current_name,
            title=current_title,
            content=content,
            lines=list(
                current_lines
            ),
            items=items,
            start_line=current_start,
            end_line=end_line,
        )

        # Handle duplicate headings by merging.
        if current_name in sections:

            existing = sections[
                current_name
            ]

            existing.content = (
                existing.content
                + "\n"
                + section.content
            ).strip()

            existing.lines.extend(
                section.lines
            )

            existing.items.extend(
                section.items
            )

            existing.end_line = (
                section.end_line
            )

        else:
            sections[
                current_name
            ] = section

        current_lines = []

    for index, line in enumerate(
        lines
    ):

        section_name = (
            detect_section_name(
                line
            )
        )

        if section_name:

            flush_section(
                index - 1
            )

            current_name = (
                section_name
            )

            current_title = line

            current_start = index

            continue

        # If heading is unknown but clearly looks like
        # a heading, preserve it as a custom section.
        if (
            looks_like_heading(line)
            and not current_lines
        ):

            custom_name = normalize_heading(
                line
            )

            if custom_name:
                flush_section(
                    index - 1
                )

                current_name = (
                    custom_name
                )

                current_title = line

                current_start = index

                continue

        current_lines.append(
            line
        )

    flush_section(
        len(lines) - 1
    )

    return sections


# ============================================================================
# Section Item Extraction
# ============================================================================


def _get_section_items(
    sections: Mapping[str, JDSection],
    names: Iterable[str],
) -> list[str]:

    result: list[str] = []

    for name in names:

        section = sections.get(
            name
        )

        if not section:
            continue

        for item in section.items:

            item = item.strip()

            if (
                item
                and item not in result
            ):
                result.append(
                    item
                )

    return result


# ============================================================================
# Skill Extraction
# ============================================================================


TECHNICAL_SKILL_PATTERNS = [
    r"\bpython\b",
    r"\bjava\b",
    r"\bc\+\+\b",
    r"\bc#\b",
    r"\bjavascript\b",
    r"\btypescript\b",
    r"\breact(?:\.js|js)?\b",
    r"\bangular\b",
    r"\bvue(?:\.js|js)?\b",
    r"\bnode(?:\.js|js)?\b",
    r"\bfastapi\b",
    r"\bdjango\b",
    r"\bflask\b",
    r"\bspring\s+boot\b",
    r"\bpostgres(?:ql)?\b",
    r"\bmysql\b",
    r"\bmongodb\b",
    r"\bredis\b",
    r"\bsql\b",
    r"\baws\b",
    r"\bazure\b",
    r"\bgcp\b",
    r"\bdocker\b",
    r"\bkubernetes\b",
    r"\bk8s\b",
    r"\bterraform\b",
    r"\bjenkins\b",
    r"\bgit\b",
    r"\bgithub\b",
    r"\bmachine\s+learning\b",
    r"\bdeep\s+learning\b",
    r"\bnatural\s+language\s+processing\b",
    r"\bnlp\b",
    r"\bartificial\s+intelligence\b",
    r"\bgenerative\s+ai\b",
    r"\bllm\b",
    r"\blarge\s+language\s+models?\b",
    r"\bpower\s+bi\b",
    r"\btableau\b",
    r"\bexcel\b",
]


def extract_technical_skills(
    text: str,
) -> list[str]:
    """
    Lightweight technical skill extraction.

    The dedicated skill_intelligence module should perform
    authoritative normalization/taxonomy handling.
    """

    normalized = normalize_text(
        text
    )

    skills: list[str] = []

    for pattern in TECHNICAL_SKILL_PATTERNS:

        matches = re.findall(
            pattern,
            normalized,
            flags=re.IGNORECASE,
        )

        if not matches:
            continue

        for match in matches:

            if isinstance(
                match,
                tuple,
            ):
                skill = next(
                    (
                        value
                        for value in match
                        if value
                    ),
                    "",
                )
            else:
                skill = match

            skill = normalize_line(
                skill
            )

            if skill and skill not in skills:
                skills.append(
                    skill
                )

    return skills


# ============================================================================
# Requirement Classification
# ============================================================================


REQUIRED_MARKERS = (
    "required",
    "must have",
    "must-have",
    "essential",
    "mandatory",
    "minimum",
    "need to have",
)

PREFERRED_MARKERS = (
    "preferred",
    "nice to have",
    "nice-to-have",
    "bonus",
    "desired",
    "plus",
)


def classify_requirement(
    text: str,
) -> str:
    """
    Classify a requirement as:

        required
        preferred
        general
    """

    normalized = normalize_text(
        text
    )

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


def split_requirements(
    items: Iterable[str],
) -> tuple[list[str], list[str], list[str]]:
    """
    Split requirement items into required,
    preferred, and general groups.
    """

    required: list[str] = []
    preferred: list[str] = []
    general: list[str] = []

    for item in items:

        category = classify_requirement(
            item
        )

        if category == "required":
            required.append(item)

        elif category == "preferred":
            preferred.append(item)

        else:
            general.append(item)

    return (
        required,
        preferred,
        general,
    )


# ============================================================================
# Main Parser
# ============================================================================


class JDParser:
    """
    Main Job Description parser.

    Example:

        parser = JDParser()

        result = parser.parse(jd_text)

        print(result.title)
        print(result.requirements)
        print(result.responsibilities)
    """

    def __init__(
        self,
        *,
        extract_skills: bool = True,
        infer_metadata: bool = True,
    ) -> None:

        self.extract_skills_enabled = (
            extract_skills
        )

        self.infer_metadata_enabled = (
            infer_metadata
        )

    def parse(
        self,
        text: str,
    ) -> JobDescription:
        """
        Parse a complete Job Description.
        """

        raw_text = (
            str(text)
            if text is not None
            else ""
        )

        cleaned = clean_text(
            raw_text
        )

        lines = split_lines(
            cleaned
        )

        if not cleaned:

            return JobDescription(
                raw_text=raw_text,
                cleaned_text="",
                metadata={
                    "line_count": 0,
                    "word_count": 0,
                    "empty": True,
                },
            )

        sections = parse_sections(
            cleaned
        )

        # --------------------------------------------------------------
        # Metadata
        # --------------------------------------------------------------

        title = None
        company = None
        location = None

        if self.infer_metadata_enabled:

            title = infer_title(
                lines
            )

            company = infer_company(
                lines
            )

            location = infer_location(
                lines
            )

        # --------------------------------------------------------------
        # Standard section extraction
        # --------------------------------------------------------------

        requirements = _get_section_items(
            sections,
            [
                "requirements",
                "qualifications",
            ],
        )

        responsibilities = _get_section_items(
            sections,
            [
                "responsibilities",
            ],
        )

        qualifications = _get_section_items(
            sections,
            [
                "qualifications",
            ],
        )

        education = _get_section_items(
            sections,
            [
                "education",
            ],
        )

        experience = _get_section_items(
            sections,
            [
                "experience",
            ],
        )

        preferred = _get_section_items(
            sections,
            [
                "preferred",
            ],
        )

        benefits = _get_section_items(
            sections,
            [
                "benefits",
            ],
        )

        # --------------------------------------------------------------
        # Skills
        # --------------------------------------------------------------

        skills = _get_section_items(
            sections,
            [
                "skills",
            ],
        )

        if self.extract_skills_enabled:

            extracted_skills = (
                extract_technical_skills(
                    cleaned
                )
            )

            for skill in extracted_skills:

                if skill not in skills:
                    skills.append(
                        skill
                    )

        # --------------------------------------------------------------
        # Requirement classification
        # --------------------------------------------------------------

        (
            classified_required,
            classified_preferred,
            _,
        ) = split_requirements(
            requirements
        )

        for item in classified_preferred:

            if item not in preferred:
                preferred.append(
                    item
                )

        # --------------------------------------------------------------
        # Metadata
        # --------------------------------------------------------------

        metadata = {
            "line_count": len(lines),
            "word_count": len(
                cleaned.split()
            ),
            "character_count": len(
                cleaned
            ),
            "section_count": len(
                sections
            ),
            "has_requirements": bool(
                requirements
            ),
            "has_responsibilities": bool(
                responsibilities
            ),
            "has_skills": bool(
                skills
            ),
            "has_education": bool(
                education
            ),
            "has_experience": bool(
                experience
            ),
            "has_preferred": bool(
                preferred
            ),
            "required_item_count": len(
                classified_required
            ),
            "preferred_item_count": len(
                preferred
            ),
        }

        return JobDescription(
            raw_text=raw_text,
            cleaned_text=cleaned,
            title=title,
            company=company,
            location=location,
            sections=sections,
            requirements=requirements,
            responsibilities=responsibilities,
            skills=skills,
            qualifications=qualifications,
            education=education,
            experience=experience,
            preferred=preferred,
            benefits=benefits,
            metadata=metadata,
        )

    def parse_dict(
        self,
        text: str,
    ) -> dict[str, Any]:
        """
        Parse JD and return a JSON-friendly dictionary.
        """

        return self.parse(
            text
        ).to_dict()


# ============================================================================
# Functional API
# ============================================================================


_default_parser: JDParser | None = None


def get_default_parser() -> JDParser:
    """Return lazily-created default parser."""

    global _default_parser

    if _default_parser is None:
        _default_parser = JDParser()

    return _default_parser


def parse_job_description(
    text: str,
) -> JobDescription:
    """
    Functional API.
    """

    return get_default_parser().parse(
        text
    )


def parse_job_description_dict(
    text: str,
) -> dict[str, Any]:
    """
    Functional API returning dictionary.
    """

    return get_default_parser().parse_dict(
        text
    )


# ============================================================================
# Convenience Functions
# ============================================================================


def get_requirements(
    text: str,
) -> list[str]:
    """Extract requirements from a JD."""

    return parse_job_description(
        text
    ).requirements


def get_responsibilities(
    text: str,
) -> list[str]:
    """Extract responsibilities from a JD."""

    return parse_job_description(
        text
    ).responsibilities


def get_skills(
    text: str,
) -> list[str]:
    """Extract technical skills from a JD."""

    return parse_job_description(
        text
    ).skills


def get_job_title(
    text: str,
) -> str | None:
    """Extract job title."""

    return parse_job_description(
        text
    ).title


def get_job_location(
    text: str,
) -> str | None:
    """Extract job location."""

    return parse_job_description(
        text
    ).location


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "JDSection",
    "JobDescription",
    "JDParser",
    "SECTION_ALIASES",
    "clean_text",
    "normalize_line",
    "normalize_heading",
    "detect_section_name",
    "looks_like_heading",
    "is_bullet",
    "clean_bullet",
    "extract_items",
    "parse_sections",
    "extract_technical_skills",
    "classify_requirement",
    "split_requirements",
    "get_default_parser",
    "parse_job_description",
    "parse_job_description_dict",
    "get_requirements",
    "get_responsibilities",
    "get_skills",
    "get_job_title",
    "get_job_location",
]