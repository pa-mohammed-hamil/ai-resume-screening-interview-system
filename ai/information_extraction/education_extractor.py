# Project scaffold file
"""
Education Information Extractor
================================

Location:
    ai/information_extraction/education_extractor.py

Purpose:
    Extract structured education information from resume text.

Extracted fields:
    - institution
    - degree
    - field_of_study
    - start_date
    - end_date
    - grade / GPA / percentage
    - raw_text

Examples supported:
    B.Tech in Computer Science, ABC University, 2024
    Bachelor of Technology - Computer Science
    University of Delhi | B.Sc. Mathematics | 2020 - 2023
    MBA, Harvard Business School, 2022
    M.Tech in Artificial Intelligence (2023)
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Sequence


# ============================================================================
# Degree Vocabulary
# ============================================================================

DEGREE_PATTERNS: dict[str, str] = {
    "ph.d": r"\b(?:ph\.?d\.?|doctor(?:ate)?\s+of\s+philosophy)\b",
    "m.phil": r"\b(?:m\.?\s*phil|master\s+of\s+philosophy)\b",
    "m.tech": r"\b(?:m\.?\s*tech|master\s+of\s+technology)\b",
    "m.e": r"\b(?:m\.?\s*e\.?|master\s+of\s+engineering)\b",
    "m.sc": r"\b(?:m\.?\s*sc\.?|master\s+of\s+science)\b",
    "mca": r"\b(?:m\.?\s*c\.?\s*a\.?|master\s+of\s+computer\s+applications)\b",
    "mba": r"\b(?:m\.?\s*b\.?\s*a\.?|master\s+of\s+business\s+administration)\b",
    "m.com": r"\b(?:m\.?\s*com\.?|master\s+of\s+commerce)\b",
    "ma": r"\b(?:m\.?\s*a\.?|master\s+of\s+arts)\b",
    "llm": r"\b(?:ll\.?m\.?|master\s+of\s+law)\b",
    "b.tech": r"\b(?:b\.?\s*tech\.?|bachelor\s+of\s+technology)\b",
    "b.e": r"\b(?:b\.?\s*e\.?|bachelor\s+of\s+engineering)\b",
    "b.sc": r"\b(?:b\.?\s*sc\.?|bachelor\s+of\s+science)\b",
    "bca": r"\b(?:b\.?\s*c\.?\s*a\.?|bachelor\s+of\s+computer\s+applications)\b",
    "bba": r"\b(?:b\.?\s*b\.?\s*a\.?|bachelor\s+of\s+business\s+administration)\b",
    "b.com": r"\b(?:b\.?\s*com\.?|bachelor\s+of\s+commerce)\b",
    "ba": r"\b(?:b\.?\s*a\.?|bachelor\s+of\s+arts)\b",
    "llb": r"\b(?:ll\.?b\.?|bachelor\s+of\s+law)\b",
    "associate": r"\bassociate(?:'s)?\s+degree\b",
    "diploma": r"\bdiploma\b",
    "higher secondary": r"\bhigher\s+secondary\b",
    "secondary": r"\bsecondary\s+(?:school|education)\b",
}


# ============================================================================
# Field of Study Vocabulary
# ============================================================================

FIELD_TERMS = {
    "computer science",
    "computer engineering",
    "information technology",
    "information science",
    "software engineering",
    "artificial intelligence",
    "machine learning",
    "data science",
    "data analytics",
    "cyber security",
    "cybersecurity",
    "electronics",
    "electronics and communication",
    "electrical engineering",
    "mechanical engineering",
    "civil engineering",
    "chemical engineering",
    "biotechnology",
    "bioinformatics",
    "mathematics",
    "physics",
    "chemistry",
    "biology",
    "statistics",
    "economics",
    "commerce",
    "accounting",
    "finance",
    "business administration",
    "management",
    "marketing",
    "human resources",
    "psychology",
    "sociology",
    "law",
    "medicine",
    "pharmacy",
    "architecture",
}


# ============================================================================
# Education Section Headers
# ============================================================================

EDUCATION_HEADERS = {
    "education",
    "educational background",
    "academic background",
    "academic qualifications",
    "education qualifications",
    "qualifications",
    "academic history",
    "educational qualifications",
}


# ============================================================================
# Date Patterns
# ============================================================================

MONTH_PATTERN = (
    r"(?:"
    r"jan(?:uary)?|"
    r"feb(?:ruary)?|"
    r"mar(?:ch)?|"
    r"apr(?:il)?|"
    r"may|"
    r"jun(?:e)?|"
    r"jul(?:y)?|"
    r"aug(?:ust)?|"
    r"sep(?:t(?:ember)?)?|"
    r"oct(?:ober)?|"
    r"nov(?:ember)?|"
    r"dec(?:ember)?"
    r")"
)

DATE_PATTERN = re.compile(
    rf"""
    (?:
        {MONTH_PATTERN}\s+\d{{4}}
        |
        \d{{1,2}}\s+{MONTH_PATTERN}\s+\d{{4}}
        |
        \d{{4}}[/-]\d{{1,2}}
        |
        \d{{1,2}}[/-]\d{{4}}
        |
        \d{{4}}
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)


DATE_RANGE_PATTERN = re.compile(
    rf"""
    (
        (?:{MONTH_PATTERN}\s+)?\d{{4}}
    )
    \s*
    (?:
        -
        |
        –
        |
        —
        |
        to
        |
        -
    )
    \s*
    (
        (?:{MONTH_PATTERN}\s+)?\d{{4}}
        |
        present
        |
        current
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)


# ============================================================================
# Grade / GPA Patterns
# ============================================================================

GPA_PATTERN = re.compile(
    r"""
    (?:
        GPA
        |
        CGPA
        |
        C\.G\.P\.A
    )
    \s*[:\-]?\s*
    (
        \d+(?:\.\d+)?
        (?:\s*/\s*\d+(?:\.\d+)?)?
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)


PERCENTAGE_PATTERN = re.compile(
    r"""
    (?:
        percentage
        |
        percent
        |
        score
        |
        marks
    )
    \s*[:\-]?\s*
    (
        \d+(?:\.\d+)?
        \s*%
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)


GRADE_PATTERN = re.compile(
    r"""
    \b
    grade
    \s*[:\-]?\s*
    (
        [A-F][+-]?
        |
        distinction
        |
        first\s+class
        |
        second\s+class
    )
    \b
    """,
    re.IGNORECASE | re.VERBOSE,
)


# ============================================================================
# Data Model
# ============================================================================


@dataclass
class Education:
    """Represents one education record."""

    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None

    start_date: str | None = None
    end_date: str | None = None

    grade: str | None = None
    gpa: str | None = None
    percentage: str | None = None

    location: str | None = None
    raw_text: str | None = None

    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EducationExtractionResult:
    """Complete education extraction result."""

    education: list[Education] = field(
        default_factory=list
    )

    education_section: str = ""

    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "education": [
                item.to_dict()
                for item in self.education
            ],
            "education_section": self.education_section,
            "confidence": self.confidence,
        }


# ============================================================================
# Utility Functions
# ============================================================================


def normalize_text(value: Any) -> str:
    """Normalize whitespace."""

    if value is None:
        return ""

    text = str(value)

    text = text.replace(
        "\u00a0",
        " ",
    )

    text = text.replace(
        "\t",
        " ",
    )

    text = re.sub(
        r"[ ]+",
        " ",
        text,
    )

    return text.strip()


def clean_value(value: str | None) -> str | None:
    """Clean an extracted value."""

    if not value:
        return None

    value = normalize_text(value)

    value = value.strip(
        " ,;:|-–—|"
    )

    if not value:
        return None

    return value


def unique_list(
    values: Iterable[str],
) -> list[str]:
    """Deduplicate values."""

    result: list[str] = []
    seen: set[str] = set()

    for value in values:

        value = clean_value(value)

        if not value:
            continue

        key = value.lower()

        if key in seen:
            continue

        seen.add(key)
        result.append(value)

    return result


# ============================================================================
# Education Extractor
# ============================================================================


class EducationExtractor:
    """
    Extract education information from resume text.

    Main API:

        extractor = EducationExtractor()

        result = extractor.extract(text)

    Returns a list of dictionaries containing:

        institution
        degree
        field_of_study
        start_date
        end_date
        grade
        gpa
        percentage
        location
        raw_text
        confidence
    """

    def __init__(
        self,
        *,
        education_headers: Iterable[str] | None = None,
        field_terms: Iterable[str] | None = None,
    ) -> None:

        self.education_headers = {
            item.lower().strip()
            for item in (
                education_headers
                or EDUCATION_HEADERS
            )
        }

        self.field_terms = {
            item.lower().strip()
            for item in (
                field_terms
                or FIELD_TERMS
            }

        }

    # ------------------------------------------------------------------
    # Section extraction
    # ------------------------------------------------------------------

    def extract_education_section(
        self,
        text: str,
    ) -> str:
        """
        Extract the education section from a resume.

        Stops when another major resume section starts.
        """

        lines = text.splitlines()

        inside = False
        collected: list[str] = []

        stop_headers = {
            "experience",
            "work experience",
            "professional experience",
            "employment",
            "employment history",
            "skills",
            "technical skills",
            "projects",
            "certifications",
            "certificates",
            "achievements",
            "awards",
            "publications",
            "languages",
            "interests",
            "references",
        }

        for line in lines:

            cleaned = normalize_text(
                line
            )

            if not cleaned:
                continue

            header = cleaned.lower()

            if header.rstrip(":") in self.education_headers:

                inside = True
                continue

            if inside and (
                header.rstrip(":")
                in stop_headers
            ):
                break

            if inside:
                collected.append(
                    cleaned
                )

        return "\n".join(
            collected
        ).strip()

    # ------------------------------------------------------------------
    # Degree extraction
    # ------------------------------------------------------------------

    def extract_degree(
        self,
        text: str,
    ) -> str | None:
        """Extract the most likely degree."""

        matches: list[
            tuple[int, int, str]
        ] = []

        for canonical, pattern in DEGREE_PATTERNS.items():

            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:

                matches.append(
                    (
                        match.start(),
                        match.end(),
                        match.group(0),
                    )
                )

        if not matches:
            return None

        matches.sort(
            key=lambda item: item[0]
        )

        return clean_value(
            matches[0][2]
        )

    # ------------------------------------------------------------------
    # Field extraction
    # ------------------------------------------------------------------

    def extract_field_of_study(
        self,
        text: str,
    ) -> str | None:
        """Extract field of study."""

        normalized = text.lower()

        # Explicit field/major notation.
        explicit_patterns = [
            r"(?:major|field|specialization|specialisation)"
            r"\s*(?:in|of)?\s*[:\-]?\s*"
            r"([A-Za-z][A-Za-z &/\-]{2,80})",

            r"(?:b\.?tech|btech|m\.?tech|mtech|"
            r"b\.?e|be|m\.?e|me|b\.?sc|bsc|"
            r"m\.?sc|msc|bca|mca|mba)"
            r"\s+(?:in|of)\s+"
            r"([A-Za-z][A-Za-z &/\-]{2,80})",
        ]

        for pattern in explicit_patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:

                value = clean_value(
                    match.group(1)
                )

                if value:
                    return value

        # Vocabulary-based extraction.
        candidates: list[str] = []

        for field_name in self.field_terms:

            pattern = (
                r"(?<!\w)"
                + re.escape(field_name)
                + r"(?!\w)"
            )

            match = re.search(
                pattern,
                normalized,
            )

            if match:
                candidates.append(
                    match.group(0)
                )

        if candidates:

            candidates.sort(
                key=len,
                reverse=True,
            )

            return clean_value(
                candidates[0]
            )

        return None

    # ------------------------------------------------------------------
    # Date extraction
    # ------------------------------------------------------------------

    def extract_dates(
        self,
        text: str,
    ) -> tuple[
        str | None,
        str | None,
    ]:
        """Extract start and end dates."""

        range_match = DATE_RANGE_PATTERN.search(
            text
        )

        if range_match:

            return (
                clean_value(
                    range_match.group(1)
                ),
                clean_value(
                    range_match.group(2)
                ),
            )

        dates = [
            clean_value(
                match.group(0)
            )
            for match in DATE_PATTERN.finditer(
                text
            )
        ]

        dates = [
            date
            for date in dates
            if date
        ]

        if len(dates) >= 2:
            return dates[0], dates[1]

        if len(dates) == 1:
            return None, dates[0]

        return None, None

    # ------------------------------------------------------------------
    # Grade extraction
    # ------------------------------------------------------------------

    def extract_grade(
        self,
        text: str,
    ) -> tuple[
        str | None,
        str | None,
        str | None,
    ]:
        """Extract grade, GPA, and percentage."""

        gpa = None
        percentage = None
        grade = None

        gpa_match = GPA_PATTERN.search(
            text
        )

        if gpa_match:
            gpa = clean_value(
                gpa_match.group(1)
            )

        percentage_match = (
            PERCENTAGE_PATTERN.search(
                text
            )
        )

        if percentage_match:
            percentage = clean_value(
                percentage_match.group(1)
            )

        grade_match = GRADE_PATTERN.search(
            text
        )

        if grade_match:
            grade = clean_value(
                grade_match.group(1)
            )

        return (
            grade,
            gpa,
            percentage,
        )

    # ------------------------------------------------------------------
    # Institution extraction
    # ------------------------------------------------------------------

    def extract_institution(
        self,
        text: str,
    ) -> str | None:
        """Extract likely institution name."""

        lines = [
            normalize_text(line)
            for line in text.splitlines()
            if normalize_text(line)
        ]

        institution_keywords = (
            "university",
            "college",
            "institute",
            "school",
            "academy",
            "technology",
            "polytechnic",
        )

        candidates: list[str] = []

        for line in lines:

            lower = line.lower()

            if any(
                keyword in lower
                for keyword in institution_keywords
            ):
                candidates.append(
                    line
                )

        if candidates:

            # Prefer lines containing university/college.
            candidates.sort(
                key=lambda value: (
                    "university" not in value.lower(),
                    "college" not in value.lower(),
                    -len(value),
                )
            )

            return clean_value(
                candidates[0]
            )

        # Common format:
        #
        # B.Tech in Computer Science,
        # ABC University,
        # 2024
        #
        for line in lines:

            if re.search(
                r"\b(university|college|institute)\b",
                line,
                re.IGNORECASE,
            ):
                return clean_value(
                    line
                )

        return None

    # ------------------------------------------------------------------
    # Location extraction
    # ------------------------------------------------------------------

    def extract_location(
        self,
        text: str,
    ) -> str | None:
        """Extract an institution location when explicitly labeled."""

        patterns = [
            r"(?:location|located\s+in)"
            r"\s*[:\-]\s*"
            r"([A-Za-z][A-Za-z ,.-]{2,80})",

            r"(?:campus)"
            r"\s*[:\-]\s*"
            r"([A-Za-z][A-Za-z ,.-]{2,80})",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:

                return clean_value(
                    match.group(1)
                )

        return None

    # ------------------------------------------------------------------
    # Single record
    # ------------------------------------------------------------------

    def parse_entry(
        self,
        text: str,
    ) -> Education:
        """Parse one education entry."""

        text = normalize_text(
            text
        )

        degree = self.extract_degree(
            text
        )

        field_of_study = (
            self.extract_field_of_study(
                text
            )
        )

        start_date, end_date = (
            self.extract_dates(
                text
            )
        )

        grade, gpa, percentage = (
            self.extract_grade(
                text
            )
        )

        institution = (
            self.extract_institution(
                text
            )
        )

        location = (
            self.extract_location(
                text
            )
        )

        confidence = self.calculate_confidence(
            institution=institution,
            degree=degree,
            field_of_study=field_of_study,
            dates=(start_date, end_date),
            grade=grade,
            gpa=gpa,
            percentage=percentage,
        )

        return Education(
            institution=institution,
            degree=degree,
            field_of_study=field_of_study,
            start_date=start_date,
            end_date=end_date,
            grade=grade,
            gpa=gpa,
            percentage=percentage,
            location=location,
            raw_text=text,
            confidence=confidence,
        )

    # ------------------------------------------------------------------
    # Entry splitting
    # ------------------------------------------------------------------

    def split_entries(
        self,
        section: str,
    ) -> list[str]:
        """
        Split education section into individual entries.

        Handles:
            blank lines
            bullet points
            year-based entries
            repeated degree patterns
        """

        if not section:
            return []

        lines = [
            normalize_text(line)
            for line in section.splitlines()
            if normalize_text(line)
        ]

        if not lines:
            return []

        entries: list[str] = []
        current: list[str] = []

        degree_regex = re.compile(
            "|".join(
                DEGREE_PATTERNS.values()
            ),
            re.IGNORECASE,
        )

        for line in lines:

            is_degree_line = bool(
                degree_regex.search(
                    line
                )
            )

            has_year = bool(
                re.search(
                    r"\b(?:19|20)\d{2}\b",
                    line,
                )
            )

            # A new degree usually indicates a new record.
            if (
                current
                and is_degree_line
                and (
                    degree_regex.search(
                        " ".join(current)
                    )
                    or has_year
                )
            ):
                entries.append(
                    " ".join(current)
                )

                current = []

            current.append(
                line
            )

        if current:
            entries.append(
                " ".join(current)
            )

        # If no meaningful splitting happened,
        # try blank-line based splitting.
        if len(entries) == 1:

            blocks = re.split(
                r"\n\s*\n",
                section,
            )

            blocks = [
                normalize_text(block)
                for block in blocks
                if normalize_text(block)
            ]

            if len(blocks) > 1:
                entries = blocks

        return unique_list(
            entries
        )

    # ------------------------------------------------------------------
    # Structured line parsing
    # ------------------------------------------------------------------

    def parse_structured_entry(
        self,
        text: str,
    ) -> Education:
        """
        Parse entries formatted with separators.

        Example:

            ABC University | B.Tech |
            Computer Science | 2020 - 2024
        """

        parts = [
            clean_value(part)
            for part in re.split(
                r"\s*[|•]\s*",
                text,
            )
        ]

        parts = [
            part
            for part in parts
            if part
        ]

        if len(parts) < 2:
            return self.parse_entry(
                text
            )

        degree_index = None

        for index, part in enumerate(
            parts
        ):

            if self.extract_degree(
                part
            ):
                degree_index = index
                break

        institution = None
        degree = None
        field = None

        if degree_index is not None:

            degree = self.extract_degree(
                parts[degree_index]
            )

            field = self.extract_field_of_study(
                parts[degree_index]
            )

            before = parts[
                :degree_index
            ]

            if before:
                institution = before[-1]

            after = parts[
                degree_index + 1:
            ]

            if after:

                for item in after:

                    if self.extract_field_of_study(
                        item
                    ):
                        field = (
                            self.extract_field_of_study(
                                item
                            )
                        )

                        break

        else:
            institution = parts[0]

        start_date, end_date = (
            self.extract_dates(
                text
            )
        )

        grade, gpa, percentage = (
            self.extract_grade(
                text
            )
        )

        confidence = self.calculate_confidence(
            institution=institution,
            degree=degree,
            field_of_study=field,
            dates=(start_date, end_date),
            grade=grade,
            gpa=gpa,
            percentage=percentage,
        )

        return Education(
            institution=institution,
            degree=degree,
            field_of_study=field,
            start_date=start_date,
            end_date=end_date,
            grade=grade,
            gpa=gpa,
            percentage=percentage,
            location=self.extract_location(
                text
            ),
            raw_text=text,
            confidence=confidence,
        )

    # ------------------------------------------------------------------
    # Confidence
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_confidence(
        *,
        institution: str | None,
        degree: str | None,
        field_of_study: str | None,
        dates: tuple[
            str | None,
            str | None,
        ],
        grade: str | None,
        gpa: str | None,
        percentage: str | None,
    ) -> float:
        """Calculate extraction confidence."""

        score = 0.0

        if institution:
            score += 0.30

        if degree:
            score += 0.30

        if field_of_study:
            score += 0.15

        if dates[0] or dates[1]:
            score += 0.10

        if grade or gpa or percentage:
            score += 0.10

        if institution and degree:
            score += 0.05

        return round(
            min(score, 1.0),
            2,
        )

    # ------------------------------------------------------------------
    # Main extraction
    # ------------------------------------------------------------------

    def extract_result(
        self,
        text: str,
    ) -> EducationExtractionResult:
        """Extract all education records."""

        text = normalize_text(
            text
        )

        if not text:
            return EducationExtractionResult()

        section = (
            self.extract_education_section(
                text
            )
        )

        # If no explicit education section exists,
        # scan the complete text.
        if not section:

            education_keywords = (
                "b.tech",
                "btech",
                "bachelor",
                "m.tech",
                "mtech",
                "master",
                "mba",
                "mca",
                "bca",
                "university",
                "college",
                "institute",
            )

            lines = [
                normalize_text(line)
                for line in text.splitlines()
                if normalize_text(line)
            ]

            candidates = [
                line
                for line in lines
                if any(
                    keyword in line.lower()
                    for keyword in education_keywords
                )
            ]

            section = "\n".join(
                candidates
            )

        entries = self.split_entries(
            section
        )

        education_records: list[
            Education
        ] = []

        for entry in entries:

            if "|" in entry or "•" in entry:

                record = (
                    self.parse_structured_entry(
                        entry
                    )
                )

            else:

                record = self.parse_entry(
                    entry
                )

            # Ignore entries that contain
            # no education-related information.
            if not any(
                (
                    record.institution,
                    record.degree,
                    record.field_of_study,
                )
            ):
                continue

            education_records.append(
                record
            )

        confidence = 0.0

        if education_records:

            confidence = round(
                sum(
                    item.confidence
                    for item in education_records
                )
                / len(education_records),
                2,
            )

        return EducationExtractionResult(
            education=education_records,
            education_section=section,
            confidence=confidence,
        )

    def extract(
        self,
        text: str,
    ) -> list[dict[str, Any]]:
        """
        Main API used by extractor.py.

        Returns a list of dictionaries.
        """

        result = self.extract_result(
            text
        )

        return [
            item.to_dict()
            for item in result.education
        ]

    def extract_objects(
        self,
        text: str,
    ) -> list[Education]:
        """Return Education objects instead of dictionaries."""

        return self.extract_result(
            text
        ).education


# ============================================================================
# Alternative Class Name
# ============================================================================


ResumeEducationExtractor = EducationExtractor


# ============================================================================
# Convenience Functions
# ============================================================================


_default_extractor: EducationExtractor | None = None


def get_default_extractor() -> EducationExtractor:
    """Return shared education extractor."""

    global _default_extractor

    if _default_extractor is None:
        _default_extractor = (
            EducationExtractor()
        )

    return _default_extractor


def extract_education(
    text: str,
) -> list[dict[str, Any]]:
    """Extract education information."""

    return get_default_extractor().extract(
        text
    )


def extract_education_result(
    text: str,
) -> EducationExtractionResult:
    """Return complete education extraction result."""

    return get_default_extractor().extract_result(
        text
    )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "Education",
    "EducationExtractionResult",
    "EducationExtractor",
    "ResumeEducationExtractor",
    "extract_education",
    "extract_education_result",
    "get_default_extractor",
]