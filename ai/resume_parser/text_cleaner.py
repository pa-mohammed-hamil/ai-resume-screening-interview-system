# Project scaffold file
"""
Resume Text Cleaner
-------------------
Cleans and normalizes text extracted from resumes.

Responsibilities:
- Normalize whitespace
- Remove control characters
- Normalize Unicode
- Fix common PDF extraction artifacts
- Preserve useful resume structure
- Remove excessive blank lines
- Normalize bullets
- Normalize email/URL spacing
- Provide reusable cleaning utilities

Used by:
    ai/resume_parser/parser.py
"""

from __future__ import annotations

import re
import unicodedata


# ---------------------------------------------------------------------------
# Regular expressions
# ---------------------------------------------------------------------------

CONTROL_CHARS_RE = re.compile(
    r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]"
)

MULTIPLE_SPACES_RE = re.compile(
    r"[ \t]+"
)

MULTIPLE_NEWLINES_RE = re.compile(
    r"\n{3,}"
)

SPACE_BEFORE_PUNCTUATION_RE = re.compile(
    r"\s+([,.;:!?])"
)

SPACE_AFTER_PUNCTUATION_RE = re.compile(
    r"([,.;:!?])([^\s\n])"
)

BULLET_RE = re.compile(
    r"^[\s]*[•●▪◦‣⁃∙◉○➢➤➜➔►▸◆◇■□]"
)

EMAIL_SPACING_RE = re.compile(
    r"\s*@\s*"
)

URL_SPACING_RE = re.compile(
    r"\s*(https?://)\s*"
)

PHONE_SPACING_RE = re.compile(
    r"(?<=\d)[ \t]+(?=\d)"
)

HYPHEN_LINE_BREAK_RE = re.compile(
    r"(\w)-\n(\w)"
)

LINE_BREAK_RE = re.compile(
    r"(?<!\n)\n(?!\n)"
)


# ---------------------------------------------------------------------------
# Unicode normalization
# ---------------------------------------------------------------------------

def normalize_unicode(text: str) -> str:
    """
    Normalize Unicode characters.

    Converts visually equivalent Unicode sequences into
    a consistent representation.
    """

    if not text:
        return ""

    text = unicodedata.normalize(
        "NFKC",
        text,
    )

    # Common typographic characters.
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u00a0": " ",
        "\u200b": "",
        "\u200c": "",
        "\u200d": "",
        "\ufeff": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


# ---------------------------------------------------------------------------
# Control character removal
# ---------------------------------------------------------------------------

def remove_control_characters(text: str) -> str:
    """Remove invisible/control characters."""

    if not text:
        return ""

    return CONTROL_CHARS_RE.sub("", text)


# ---------------------------------------------------------------------------
# PDF line-break cleanup
# ---------------------------------------------------------------------------

def fix_hyphenated_line_breaks(text: str) -> str:
    """
    Join words split across lines by a hyphen.

    Example:
        "develop-\nment" -> "development"

    This is useful for PDF extraction.
    """

    if not text:
        return ""

    return HYPHEN_LINE_BREAK_RE.sub(
        r"\1\2",
        text,
    )


def normalize_line_breaks(text: str) -> str:
    """Normalize Windows/Mac line endings."""

    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    return text


# ---------------------------------------------------------------------------
# Whitespace cleanup
# ---------------------------------------------------------------------------

def normalize_spaces(text: str) -> str:
    """Collapse repeated spaces and tabs."""

    if not text:
        return ""

    lines = []

    for line in text.split("\n"):
        line = MULTIPLE_SPACES_RE.sub(
            " ",
            line,
        )

        lines.append(
            line.strip()
        )

    return "\n".join(lines)


def remove_excessive_newlines(text: str) -> str:
    """Limit consecutive blank lines."""

    if not text:
        return ""

    text = MULTIPLE_NEWLINES_RE.sub(
        "\n\n",
        text,
    )

    return text.strip()


# ---------------------------------------------------------------------------
# Bullet normalization
# ---------------------------------------------------------------------------

def normalize_bullets(
    text: str,
    bullet_style: str = "-",
) -> str:
    """
    Normalize common bullet characters.

    Args:
        text: Input resume text.
        bullet_style: Replacement bullet, usually "-".
    """

    if not text:
        return ""

    lines = []

    for line in text.split("\n"):
        if BULLET_RE.match(line):
            line = BULLET_RE.sub(
                "",
                line,
            ).strip()

            if line:
                line = f"{bullet_style} {line}"

        lines.append(line)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Punctuation cleanup
# ---------------------------------------------------------------------------

def normalize_punctuation(text: str) -> str:
    """Fix common spacing issues around punctuation."""

    if not text:
        return ""

    text = SPACE_BEFORE_PUNCTUATION_RE.sub(
        r"\1",
        text,
    )

    text = SPACE_AFTER_PUNCTUATION_RE.sub(
        r"\1 \2",
        text,
    )

    return text


# ---------------------------------------------------------------------------
# Email cleanup
# ---------------------------------------------------------------------------

def normalize_emails(text: str) -> str:
    """
    Remove spaces accidentally inserted around @.

    Example:
        john @ gmail.com -> john@gmail.com
    """

    if not text:
        return ""

    return EMAIL_SPACING_RE.sub(
        "@",
        text,
    )


# ---------------------------------------------------------------------------
# URL cleanup
# ---------------------------------------------------------------------------

def normalize_urls(text: str) -> str:
    """Normalize spacing around HTTP/HTTPS URLs."""

    if not text:
        return ""

    return URL_SPACING_RE.sub(
        r"\1",
        text,
    )


# ---------------------------------------------------------------------------
# Phone cleanup
# ---------------------------------------------------------------------------

def normalize_phone_spacing(text: str) -> str:
    """
    Normalize excessive spaces inside phone numbers.

    Keeps normal phone formatting intact.
    """

    if not text:
        return ""

    # Only collapse repeated spaces between digits.
    return PHONE_SPACING_RE.sub(
        " ",
        text,
    )


# ---------------------------------------------------------------------------
# Empty-line handling
# ---------------------------------------------------------------------------

def remove_empty_lines(text: str) -> str:
    """Remove unnecessary empty lines while preserving sections."""

    if not text:
        return ""

    lines = []

    previous_empty = False

    for line in text.split("\n"):
        line = line.strip()

        if not line:
            if previous_empty:
                continue

            previous_empty = True
            lines.append("")
            continue

        previous_empty = False
        lines.append(line)

    return "\n".join(lines).strip()


# ---------------------------------------------------------------------------
# Section cleanup
# ---------------------------------------------------------------------------

def normalize_section_headers(text: str) -> str:
    """
    Normalize common resume section headers.

    This does not force capitalization because the original
    formatting may be useful for downstream extraction.
    """

    if not text:
        return ""

    replacements = {
        "professional experience": "Experience",
        "work experience": "Experience",
        "employment history": "Experience",
        "professional summary": "Summary",
        "career summary": "Summary",
        "career objective": "Objective",
        "professional objective": "Objective",
        "academic background": "Education",
        "educational background": "Education",
        "technical skills": "Skills",
        "core competencies": "Skills",
        "areas of expertise": "Skills",
        "projects": "Projects",
        "personal projects": "Projects",
        "certifications": "Certifications",
        "certificates": "Certifications",
        "achievements": "Achievements",
        "awards": "Awards",
        "publications": "Publications",
        "languages": "Languages",
        "interests": "Interests",
        "hobbies": "Hobbies",
        "references": "References",
    }

    lines = []

    for line in text.split("\n"):
        normalized = line.strip().lower()

        if normalized in replacements:
            lines.append(
                replacements[normalized]
            )
        else:
            lines.append(line)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Duplicate line removal
# ---------------------------------------------------------------------------

def remove_duplicate_consecutive_lines(
    text: str,
) -> str:
    """
    Remove identical consecutive lines.

    Useful for PDFs where headers/footers may be repeated.
    """

    if not text:
        return ""

    result = []
    previous = None

    for line in text.split("\n"):
        normalized = line.strip().lower()

        if normalized and normalized == previous:
            continue

        result.append(line)

        if normalized:
            previous = normalized
        else:
            previous = None

    return "\n".join(result)


# ---------------------------------------------------------------------------
# Main cleaner
# ---------------------------------------------------------------------------

def clean_text(
    text: str,
    *,
    normalize_bullet_points: bool = True,
    normalize_headers: bool = True,
    remove_duplicates: bool = True,
) -> str:
    """
    Perform complete resume text cleaning.

    Args:
        text:
            Raw extracted resume text.

        normalize_bullet_points:
            Normalize bullet characters.

        normalize_headers:
            Normalize common resume section names.

        remove_duplicates:
            Remove repeated consecutive lines.

    Returns:
        Cleaned resume text.
    """

    if not text:
        return ""

    # 1. Unicode normalization
    text = normalize_unicode(text)

    # 2. Remove control characters
    text = remove_control_characters(text)

    # 3. Normalize line endings
    text = normalize_line_breaks(text)

    # 4. Join words broken by PDF line wrapping
    text = fix_hyphenated_line_breaks(text)

    # 5. Normalize emails and URLs
    text = normalize_emails(text)
    text = normalize_urls(text)

    # 6. Normalize whitespace
    text = normalize_spaces(text)

    # 7. Normalize punctuation
    text = normalize_punctuation(text)

    # 8. Normalize bullets
    if normalize_bullet_points:
        text = normalize_bullets(text)

    # 9. Normalize section headers
    if normalize_headers:
        text = normalize_section_headers(text)

    # 10. Remove repeated consecutive lines
    if remove_duplicates:
        text = remove_duplicate_consecutive_lines(text)

    # 11. Remove excessive blank lines
    text = remove_excessive_newlines(text)

    # 12. Final cleanup
    text = remove_empty_lines(text)

    return text.strip()


# ---------------------------------------------------------------------------
# Specialized cleaning functions
# ---------------------------------------------------------------------------

def clean_for_nlp(text: str) -> str:
    """
    Prepare text for NLP/ML processing.

    Preserves words and useful punctuation while removing
    formatting noise.
    """

    text = clean_text(text)

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    return text.strip()


def clean_for_embedding(text: str) -> str:
    """
    Prepare resume text for embedding models/RAG.

    Keeps semantic information while reducing formatting noise.
    """

    text = clean_text(
        text,
        normalize_bullet_points=True,
        normalize_headers=True,
        remove_duplicates=True,
    )

    # Convert bullets to normal sentences.
    text = re.sub(
        r"^\-\s+",
        "",
        text,
        flags=re.MULTILINE,
    )

    # Remove excessive blank lines.
    text = re.sub(
        r"\n{2,}",
        "\n",
        text,
    )

    return text.strip()


def clean_for_display(text: str) -> str:
    """
    Prepare cleaned text for frontend display.
    """

    return clean_text(
        text,
        normalize_bullet_points=True,
        normalize_headers=False,
        remove_duplicates=True,
    )


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def get_text_statistics(
    text: str,
) -> dict[str, int]:
    """Return useful statistics about cleaned resume text."""

    if not text:
        return {
            "characters": 0,
            "words": 0,
            "lines": 0,
            "paragraphs": 0,
            "sentences": 0,
        }

    lines = [
        line
        for line in text.split("\n")
        if line.strip()
    ]

    paragraphs = [
        paragraph
        for paragraph in re.split(
            r"\n\s*\n",
            text,
        )
        if paragraph.strip()
    ]

    sentences = [
        sentence
        for sentence in re.split(
            r"[.!?]+",
            text,
        )
        if sentence.strip()
    ]

    return {
        "characters": len(text),
        "words": len(text.split()),
        "lines": len(lines),
        "paragraphs": len(paragraphs),
        "sentences": len(sentences),
    }


# ---------------------------------------------------------------------------
# Convenience alias
# ---------------------------------------------------------------------------

def normalize_resume_text(text: str) -> str:
    """Alias for clean_text()."""

    return clean_text(text)