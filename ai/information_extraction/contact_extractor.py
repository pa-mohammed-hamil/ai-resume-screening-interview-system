# Project scaffold file
"""
Contact Information Extractor
=============================

Location:
    ai/information_extraction/contact_extractor.py

Purpose:
    Extract structured contact information from resume text.

Supported fields:
    - name
    - email
    - phone
    - location
    - linkedin
    - github
    - portfolio
    - website
    - other_urls

The extractor is intentionally dependency-light and uses regular
expressions plus simple heuristics. It can be used independently
or through information_extraction/extractor.py.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable


# ============================================================================
# Regular Expressions
# ============================================================================

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+\-]+@"
    r"[A-Za-z0-9.\-]+\.[A-Za-z]{2,63}\b",
    re.IGNORECASE,
)


PHONE_PATTERN = re.compile(
    r"""
    (?<!\d)
    (?:
        (?:\+|00)\s?\d{1,3}[\s.\-]?
    )?
    (?:
        \(?\d{2,5}\)?[\s.\-]?
    )?
    \d{3,5}
    [\s.\-]?
    \d{3,5}
    (?!\d)
    """,
    re.VERBOSE,
)


URL_PATTERN = re.compile(
    r"""
    (?:
        https?://
        |
        http://
        |
        www\.
    )
    [^\s<>()\[\]{}]+
    """,
    re.IGNORECASE | re.VERBOSE,
)


LINKEDIN_PATTERN = re.compile(
    r"""
    (?:
        https?://
        |
        www\.
    )?
    linkedin\.com/
    [^\s<>()\[\]{}]+
    """,
    re.IGNORECASE | re.VERBOSE,
)


GITHUB_PATTERN = re.compile(
    r"""
    (?:
        https?://
        |
        www\.
    )?
    github\.com/
    [^\s<>()\[\]{}]+
    """,
    re.IGNORECASE | re.VERBOSE,
)


# ============================================================================
# Location Patterns
# ============================================================================

LOCATION_LABEL_PATTERN = re.compile(
    r"""
    (?:
        location
        |
        address
        |
        based\s+in
        |
        based\s+at
        |
        residence
        |
        city
    )
    \s*[:\-]?\s*
    ([A-Za-z][A-Za-z0-9 ,.\-]{2,100})
    """,
    re.IGNORECASE | re.VERBOSE,
)


# ============================================================================
# Name Patterns
# ============================================================================

NAME_LABEL_PATTERN = re.compile(
    r"""
    (?:
        name
        |
        candidate
        |
        full\s+name
    )
    \s*[:\-]\s*
    ([A-Za-z][A-Za-z .'\-]{2,80})
    """,
    re.IGNORECASE | re.VERBOSE,
)


# ============================================================================
# Data Model
# ============================================================================


@dataclass
class ContactInformation:
    """Structured contact information extracted from a resume."""

    name: str | None = None

    email: str | None = None

    phone: str | None = None

    location: str | None = None

    linkedin: str | None = None

    github: str | None = None

    portfolio: str | None = None

    website: str | None = None

    other_urls: list[str] = field(
        default_factory=list
    )

    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ContactExtractionResult:
    """Complete contact extraction result."""

    contact: ContactInformation

    raw_header: str = ""

    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "contact": self.contact.to_dict(),
            "raw_header": self.raw_header,
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


def clean_url(url: str | None) -> str | None:
    """Remove punctuation accidentally captured after a URL."""

    if not url:
        return None

    url = normalize_text(url)

    url = url.rstrip(
        ".,;:!?)]}>\"'"
    )

    if not url:
        return None

    if not re.match(
        r"^https?://",
        url,
        re.IGNORECASE,
    ):
        url = "https://" + url

    return url


def normalize_email(
    email: str | None,
) -> str | None:
    """Normalize email address."""

    if not email:
        return None

    email = normalize_text(
        email
    ).lower()

    return email.strip(
        ".,;:<>[](){}\"'"
    )


def normalize_phone(
    phone: str | None,
) -> str | None:
    """
    Normalize a phone number while preserving an optional
    international '+' prefix.
    """

    if not phone:
        return None

    phone = normalize_text(
        phone
    )

    phone = phone.strip(
        ".,;:"
    )

    # Keep digits and a possible leading +.
    has_plus = phone.startswith(
        "+"
    )

    digits = re.sub(
        r"\D",
        "",
        phone,
    )

    if not digits:
        return None

    if has_plus:
        return "+" + digits

    return digits


def clean_name(
    name: str | None,
) -> str | None:
    """Clean a candidate name."""

    if not name:
        return None

    name = normalize_text(
        name
    )

    name = name.strip(
        ".,;:|/-"
    )

    name = re.sub(
        r"\s+",
        " ",
        name,
    )

    return name or None


def unique_values(
    values: Iterable[str],
) -> list[str]:
    """Deduplicate strings while preserving order."""

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
        result.append(value)

    return result


# ============================================================================
# Contact Extractor
# ============================================================================


class ContactExtractor:
    """
    Extract contact information from resume text.

    Usage:

        extractor = ContactExtractor()

        contact = extractor.extract(text)

    Returns:

        {
            "name": "...",
            "email": "...",
            "phone": "...",
            "location": "...",
            "linkedin": "...",
            "github": "...",
            "portfolio": "...",
            "website": "...",
            "other_urls": [...],
            "confidence": 0.95
        }
    """

    def __init__(
        self,
        *,
        max_header_lines: int = 15,
    ) -> None:

        self.max_header_lines = max(
            1,
            max_header_lines,
        )

    # ------------------------------------------------------------------
    # Email
    # ------------------------------------------------------------------

    def extract_emails(
        self,
        text: str,
    ) -> list[str]:
        """Extract all email addresses."""

        emails = [
            normalize_email(
                match.group(0)
            )
            for match in EMAIL_PATTERN.finditer(
                text
            )
        ]

        return unique_values(
            email
            for email in emails
            if email
        )

    # ------------------------------------------------------------------
    # Phone
    # ------------------------------------------------------------------

    def extract_phones(
        self,
        text: str,
    ) -> list[str]:
        """Extract phone numbers."""

        phones: list[str] = []

        for match in PHONE_PATTERN.finditer(
            text
        ):

            raw = match.group(0)

            # Avoid treating years as phone numbers.
            digits = re.sub(
                r"\D",
                "",
                raw,
            )

            if len(digits) < 7:
                continue

            if len(digits) == 4 and (
                digits.startswith(
                    ("19", "20")
                )
            ):
                continue

            normalized = normalize_phone(
                raw
            )

            if normalized:
                phones.append(
                    normalized
                )

        return unique_values(
            phones
        )

    # ------------------------------------------------------------------
    # URLs
    # ------------------------------------------------------------------

    def extract_urls(
        self,
        text: str,
    ) -> list[str]:
        """Extract URLs."""

        urls = [
            clean_url(
                match.group(0)
            )
            for match in URL_PATTERN.finditer(
                text
            )
        ]

        return unique_values(
            url
            for url in urls
            if url
        )

    # ------------------------------------------------------------------
    # LinkedIn
    # ------------------------------------------------------------------

    def extract_linkedin(
        self,
        text: str,
    ) -> str | None:
        """Extract the first LinkedIn profile URL."""

        match = LINKEDIN_PATTERN.search(
            text
        )

        if not match:
            return None

        return clean_url(
            match.group(0)
        )

    # ------------------------------------------------------------------
    # GitHub
    # ------------------------------------------------------------------

    def extract_github(
        self,
        text: str,
    ) -> str | None:
        """Extract the first GitHub profile URL."""

        match = GITHUB_PATTERN.search(
            text
        )

        if not match:
            return None

        return clean_url(
            match.group(0)
        )

    # ------------------------------------------------------------------
    # Name
    # ------------------------------------------------------------------

    def extract_name(
        self,
        text: str,
    ) -> str | None:
        """
        Extract a likely candidate name.

        Strategy:
            1. Explicit "Name:" field.
            2. First meaningful header line.
            3. Capitalized 2-5 word line.
        """

        # --------------------------------------------------------------
        # Explicit name label
        # --------------------------------------------------------------

        match = NAME_LABEL_PATTERN.search(
            text
        )

        if match:

            name = clean_name(
                match.group(1)
            )

            if self.is_valid_name(
                name
            ):
                return name

        # --------------------------------------------------------------
        # Inspect first few lines
        # --------------------------------------------------------------

        lines = [
            normalize_text(line)
            for line in text.splitlines()
            if normalize_text(line)
        ]

        lines = lines[
            : self.max_header_lines
        ]

        for line in lines:

            if self.is_likely_name(
                line
            ):
                return clean_name(
                    line
                )

        return None

    def is_valid_name(
        self,
        name: str | None,
    ) -> bool:
        """Validate a possible name."""

        if not name:
            return False

        words = name.split()

        if not 2 <= len(words) <= 5:
            return False

        if any(
            not re.fullmatch(
                r"[A-Za-z][A-Za-z.'\-]*",
                word,
            )
            for word in words
        ):
            return False

        return True

    def is_likely_name(
        self,
        line: str,
    ) -> bool:
        """Determine whether a line looks like a person's name."""

        line = normalize_text(
            line
        )

        if not line:
            return False

        # Don't interpret contact details as names.
        if "@" in line:
            return False

        if re.search(
            r"https?://|www\.",
            line,
            re.IGNORECASE,
        ):
            return False

        if re.search(
            r"\d",
            line,
        ):
            return False

        # Avoid section headings.
        section_words = {
            "resume",
            "curriculum vitae",
            "cv",
            "profile",
            "summary",
            "objective",
            "experience",
            "education",
            "skills",
            "projects",
            "certifications",
            "achievements",
            "contact",
            "references",
        }

        if line.lower() in section_words:
            return False

        words = line.split()

        if not 2 <= len(words) <= 5:
            return False

        valid_words = 0

        for word in words:

            cleaned = word.strip(
                ".,;:()[]{}"
            )

            if re.fullmatch(
                r"[A-Za-z][A-Za-z.'\-]*",
                cleaned,
            ):
                valid_words += 1

        if valid_words != len(words):
            return False

        # Names are normally title-cased or uppercase.
        title_like = all(
            word[0].isupper()
            for word in words
            if word
        )

        uppercase_like = line.isupper()

        return (
            title_like
            or uppercase_like
        )

    # ------------------------------------------------------------------
    # Location
    # ------------------------------------------------------------------

    def extract_location(
        self,
        text: str,
    ) -> str | None:
        """Extract explicitly labeled location/address."""

        match = LOCATION_LABEL_PATTERN.search(
            text
        )

        if match:

            value = normalize_text(
                match.group(1)
            )

            # Stop accidental capture at common separators.
            value = re.split(
                r"\s*(?:\||;)\s*",
                value,
            )[0]

            return value.strip(
                ".,;:"
            ) or None

        # Look at header lines for location-like information.
        lines = [
            normalize_text(line)
            for line in text.splitlines()
            if normalize_text(line)
        ]

        for line in lines[
            : self.max_header_lines
        ]:

            lower = line.lower()

            if any(
                marker in lower
                for marker in (
                    "india",
                    "usa",
                    "united states",
                    "uk",
                    "united kingdom",
                    "canada",
                    "australia",
                    "kerala",
                    "karnataka",
                    "maharashtra",
                    "california",
                    "texas",
                    "new york",
                )
            ):

                if (
                    "@" not in line
                    and not re.search(
                        r"https?://|www\.",
                        line,
                        re.IGNORECASE,
                    )
                    and not re.search(
                        r"\d{7,}",
                        line,
                    )
                ):
                    return line

        return None

    # ------------------------------------------------------------------
    # Portfolio
    # ------------------------------------------------------------------

    def extract_portfolio(
        self,
        urls: Iterable[str],
    ) -> str | None:
        """
        Identify a likely personal portfolio.

        Domains such as:
            vercel.app
            netlify.app
            github.io
            personal domains
        are treated as portfolio candidates.
        """

        portfolio_domains = (
            "vercel.app",
            "netlify.app",
            "github.io",
            "gitlab.io",
            "pages.dev",
            "web.app",
        )

        for url in urls:

            lower = url.lower()

            if any(
                domain in lower
                for domain in portfolio_domains
            ):
                return url

        return None

    # ------------------------------------------------------------------
    # Website
    # ------------------------------------------------------------------

    def extract_website(
        self,
        urls: Iterable[str],
        *,
        linkedin: str | None = None,
        github: str | None = None,
        portfolio: str | None = None,
    ) -> str | None:
        """Find a general website URL."""

        excluded = {
            value.lower()
            for value in (
                linkedin,
                github,
                portfolio,
            )
            if value
        }

        for url in urls:

            if url.lower() in excluded:
                continue

            return url

        return None

    # ------------------------------------------------------------------
    # Other URLs
    # ------------------------------------------------------------------

    def extract_other_urls(
        self,
        urls: Iterable[str],
        *,
        linkedin: str | None = None,
        github: str | None = None,
        portfolio: str | None = None,
        website: str | None = None,
    ) -> list[str]:
        """Return URLs not categorized elsewhere."""

        excluded = {
            value.lower()
            for value in (
                linkedin,
                github,
                portfolio,
                website,
            )
            if value
        }

        return [
            url
            for url in urls
            if url.lower()
            not in excluded
        ]

    # ------------------------------------------------------------------
    # Header extraction
    # ------------------------------------------------------------------

    def extract_header(
        self,
        text: str,
    ) -> str:
        """Extract the likely resume header."""

        lines = [
            normalize_text(line)
            for line in text.splitlines()
            if normalize_text(line)
        ]

        return "\n".join(
            lines[
                : self.max_header_lines
            ]
        )

    # ------------------------------------------------------------------
    # Confidence
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_confidence(
        *,
        name: str | None,
        email: str | None,
        phone: str | None,
        location: str | None,
        linkedin: str | None,
        github: str | None,
        portfolio: str | None,
        website: str | None,
    ) -> float:
        """Calculate confidence based on extracted fields."""

        score = 0.0

        if name:
            score += 0.25

        if email:
            score += 0.25

        if phone:
            score += 0.20

        if location:
            score += 0.10

        if linkedin:
            score += 0.07

        if github:
            score += 0.06

        if portfolio:
            score += 0.04

        if website:
            score += 0.03

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
    ) -> ContactExtractionResult:
        """Extract complete contact information."""

        text = normalize_text(
            text
        )

        if not text:

            contact = ContactInformation()

            return ContactExtractionResult(
                contact=contact,
                raw_header="",
                confidence=0.0,
            )

        emails = self.extract_emails(
            text
        )

        phones = self.extract_phones(
            text
        )

        urls = self.extract_urls(
            text
        )

        name = self.extract_name(
            text
        )

        location = self.extract_location(
            text
        )

        linkedin = (
            self.extract_linkedin(
                text
            )
        )

        github = (
            self.extract_github(
                text
            )
        )

        portfolio = (
            self.extract_portfolio(
                urls
            )
        )

        website = (
            self.extract_website(
                urls,
                linkedin=linkedin,
                github=github,
                portfolio=portfolio,
            )
        )

        other_urls = (
            self.extract_other_urls(
                urls,
                linkedin=linkedin,
                github=github,
                portfolio=portfolio,
                website=website,
            )
        )

        contact = ContactInformation(
            name=name,
            email=emails[0]
            if emails
            else None,
            phone=phones[0]
            if phones
            else None,
            location=location,
            linkedin=linkedin,
            github=github,
            portfolio=portfolio,
            website=website,
            other_urls=other_urls,
        )

        confidence = (
            self.calculate_confidence(
                name=name,
                email=contact.email,
                phone=contact.phone,
                location=location,
                linkedin=linkedin,
                github=github,
                portfolio=portfolio,
                website=website,
            )
        )

        contact.confidence = (
            confidence
        )

        return ContactExtractionResult(
            contact=contact,
            raw_header=self.extract_header(
                text
            ),
            confidence=confidence,
        )

    def extract(
        self,
        text: str,
    ) -> dict[str, Any]:
        """Main public API."""

        return self.extract_result(
            text
        ).contact.to_dict()

    def extract_object(
        self,
        text: str,
    ) -> ContactInformation:
        """Return ContactInformation object."""

        return self.extract_result(
            text
        ).contact


# ============================================================================
# Alternative Class Name
# ============================================================================


ResumeContactExtractor = ContactExtractor


# ============================================================================
# Convenience Functions
# ============================================================================


_default_extractor: ContactExtractor | None = None


def get_default_extractor() -> ContactExtractor:
    """Return shared contact extractor."""

    global _default_extractor

    if _default_extractor is None:
        _default_extractor = (
            ContactExtractor()
        )

    return _default_extractor


def extract_contact(
    text: str,
) -> dict[str, Any]:
    """Extract contact information."""

    return get_default_extractor().extract(
        text
    )


def extract_contact_result(
    text: str,
) -> ContactExtractionResult:
    """Return complete extraction result."""

    return get_default_extractor().extract_result(
        text
    )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "ContactInformation",
    "ContactExtractionResult",
    "ContactExtractor",
    "ResumeContactExtractor",
    "extract_contact",
    "extract_contact_result",
    "get_default_extractor",
]