# Project scaffold file
```python
"""
Resume extraction accuracy evaluation tests.

Target modules:
    ai/resume_parser/parser.py
    ai/resume_parser/pdf_parser.py
    ai/resume_parser/docx_parser.py
    ai/resume_parser/text_cleaner.py
    ai/information_extraction/extractor.py
    ai/information_extraction/entity_extractor.py
    ai/information_extraction/education_extractor.py
    ai/information_extraction/experience_extractor.py
    ai/information_extraction/contact_extractor.py
    ai/skill_intelligence/skill_extractor.py
    ai/skill_intelligence/skill_normalizer.py

Run:
    pytest tests/evaluation/test_resume_accuracy.py -v
"""

from __future__ import annotations

import re
from typing import Any

import pytest


# ============================================================================
# Synthetic evaluation dataset
# ============================================================================

@pytest.fixture
def resume_dataset():
    """
    Ground-truth resume extraction examples.

    These examples are intentionally synthetic and contain no real
    candidate information.

    In production, expected_results should be created from human-reviewed
    annotations rather than generated from the parser itself.
    """

    return [
        {
            "id": "resume-001",
            "text": """
            JOHN DOE
            john.doe@example.com
            +1 555 123 4567
            linkedin.com/in/johndoe

            PROFESSIONAL SUMMARY
            Backend Developer with 5 years of experience building APIs.

            EXPERIENCE
            Senior Backend Developer
            ABC Technologies
            2021 - Present

            Backend Developer
            XYZ Software
            2019 - 2021

            EDUCATION
            Bachelor of Technology in Computer Science
            University of Example
            2015 - 2019

            SKILLS
            Python, FastAPI, PostgreSQL, Docker, AWS, Redis
            """,
            "expected": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1 555 123 4567",
                "skills": [
                    "Python",
                    "FastAPI",
                    "PostgreSQL",
                    "Docker",
                    "AWS",
                    "Redis",
                ],
                "education": [
                    "Bachelor of Technology",
                    "Computer Science",
                ],
                "experience_years_min": 4,
            },
        },
        {
            "id": "resume-002",
            "text": """
            JANE SMITH

            Contact:
            jane.smith@example.com
            +91 98765 43210

            SUMMARY
            Frontend Engineer specializing in modern web applications.

            EXPERIENCE
            Frontend Engineer
            Web Company
            2022 - Present

            Junior Developer
            Design Company
            2020 - 2022

            EDUCATION
            Bachelor of Science in Computer Science
            Example University

            SKILLS
            JavaScript, React, TypeScript, HTML, CSS
            """,
            "expected": {
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "phone": "+91 98765 43210",
                "skills": [
                    "JavaScript",
                    "React",
                    "TypeScript",
                    "HTML",
                    "CSS",
                ],
                "education": [
                    "Bachelor of Science",
                    "Computer Science",
                ],
                "experience_years_min": 4,
            },
        },
    ]


# ============================================================================
# Reference extraction helpers
# ============================================================================

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)


PHONE_PATTERN = re.compile(
    r"""
    (?:
        \+\d{1,3}[\s.-]?
    )?
    (?:\(?\d{2,4}\)?[\s.-]?)?
    \d{3,4}[\s.-]?\d{3,4}
    """,
    re.VERBOSE,
)


def extract_email(text: str) -> str | None:
    """Reference email extractor."""

    match = EMAIL_PATTERN.search(text)

    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    """Reference phone extractor."""

    match = PHONE_PATTERN.search(text)

    if not match:
        return None

    return " ".join(match.group(0).split())


def extract_name(text: str) -> str | None:
    """
    Reference name extractor.

    Assumes the first non-empty line is the candidate's name.
    """

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if "@" in line:
            continue

        if any(char.isdigit() for char in line):
            continue

        if len(line.split()) >= 2:
            return line.title()

    return None


def normalize_skill(skill: str) -> str:
    """Normalize skill names for comparison."""

    return (
        skill.lower()
        .strip()
        .replace("-", " ")
        .replace("_", " ")
    )


def extract_skills(
    text: str,
    taxonomy: list[str],
) -> list[str]:
    """
    Reference taxonomy-based skill extractor.

    The real implementation should use:
        ai.skill_intelligence.skill_extractor.SkillExtractor
    """

    normalized_text = normalize_skill(text)

    found = []

    for skill in taxonomy:
        if normalize_skill(skill) in normalized_text:
            found.append(skill)

    return found


def skill_recall(
    extracted: list[str],
    expected: list[str],
) -> float:
    """Calculate skill extraction recall."""

    if not expected:
        return 1.0

    extracted_set = {
        normalize_skill(skill)
        for skill in extracted
    }

    expected_set = {
        normalize_skill(skill)
        for skill in expected
    }

    return len(
        extracted_set.intersection(expected_set)
    ) / len(expected_set)


def skill_precision(
    extracted: list[str],
    expected: list[str],
) -> float:
    """Calculate skill extraction precision."""

    if not extracted:
        return 1.0 if not expected else 0.0

    extracted_set = {
        normalize_skill(skill)
        for skill in extracted
    }

    expected_set = {
        normalize_skill(skill)
        for skill in expected
    }

    return len(
        extracted_set.intersection(expected_set)
    ) / len(extracted_set)


def exact_match(
    predicted: Any,
    expected: Any,
) -> bool:
    """Safe exact comparison."""

    if isinstance(predicted, str):
        return predicted.strip().lower() == (
            str(expected).strip().lower()
        )

    return predicted == expected


# ============================================================================
# Contact extraction
# ============================================================================

def test_email_extraction_accuracy(resume_dataset):
    correct = 0

    for item in resume_dataset:
        predicted = extract_email(item["text"])
        expected = item["expected"]["email"]

        if exact_match(predicted, expected):
            correct += 1

    accuracy = correct / len(resume_dataset)

    assert accuracy >= 0.95


def test_email_format_validation():
    valid_emails = [
        "john@example.com",
        "jane.smith@example.co.uk",
        "developer+resume@example.org",
    ]

    for email in valid_emails:
        assert EMAIL_PATTERN.fullmatch(email)


def test_invalid_email_is_not_extracted():
    text = """
    Candidate
    john.example.com
    """

    assert extract_email(text) is None


def test_phone_extraction_accuracy(resume_dataset):
    correct = 0

    for item in resume_dataset:
        predicted = extract_phone(item["text"])
        expected = item["expected"]["phone"]

        if predicted == expected:
            correct += 1

    accuracy = correct / len(resume_dataset)

    assert accuracy >= 0.95


# ============================================================================
# Name extraction
# ============================================================================

def test_name_extraction_accuracy(resume_dataset):
    correct = 0

    for item in resume_dataset:
        predicted = extract_name(item["text"])
        expected = item["expected"]["name"]

        if exact_match(predicted, expected):
            correct += 1

    accuracy = correct / len(resume_dataset)

    assert accuracy >= 0.95


def test_name_extraction_ignores_contact_lines():
    text = """
    Alice Johnson
    alice.johnson@example.com
    +1 555 111 2222
    """

    assert extract_name(text) == "Alice Johnson"


# ============================================================================
# Skill extraction
# ============================================================================

@pytest.fixture
def skill_taxonomy():
    return [
        "Python",
        "FastAPI",
        "PostgreSQL",
        "Docker",
        "AWS",
        "Redis",
        "JavaScript",
        "React",
        "TypeScript",
        "HTML",
        "CSS",
        "Java",
        "Spring Boot",
        "MySQL",
        "Kubernetes",
        "Git",
    ]


def test_skill_extraction_recall(
    resume_dataset,
    skill_taxonomy,
):
    recalls = []

    for item in resume_dataset:
        extracted = extract_skills(
            item["text"],
            skill_taxonomy,
        )

        expected = item["expected"]["skills"]

        recalls.append(
            skill_recall(
                extracted,
                expected,
            )
        )

    average_recall = sum(recalls) / len(recalls)

    assert average_recall >= 0.90


def test_skill_extraction_precision(
    resume_dataset,
    skill_taxonomy,
):
    precisions = []

    for item in resume_dataset:
        extracted = extract_skills(
            item["text"],
            skill_taxonomy,
        )

        expected = item["expected"]["skills"]

        precisions.append(
            skill_precision(
                extracted,
                expected,
            )
        )

    average_precision = (
        sum(precisions) / len(precisions)
    )

    assert average_precision >= 0.90


def test_skill_normalization_is_case_insensitive():
    skills = [
        "Python",
        "PYTHON",
        "python",
        " Python ",
    ]

    normalized = {
        normalize_skill(skill)
        for skill in skills
    }

    assert normalized == {"python"}


def test_skill_normalization_handles_separators():
    assert normalize_skill("machine-learning") == (
        "machine learning"
    )

    assert normalize_skill("machine_learning") == (
        "machine learning"
    )


def test_missing_skill_is_not_reported(
    skill_taxonomy,
):
    text = """
    Candidate
    Skills:
    Python, FastAPI, PostgreSQL
    """

    extracted = extract_skills(
        text,
        skill_taxonomy,
    )

    assert "Python" in extracted
    assert "FastAPI" in extracted
    assert "PostgreSQL" in extracted
    assert "React" not in extracted


# ============================================================================
# Education extraction
# ============================================================================

def extract_education(text: str) -> list[str]:
    """Simple reference education extractor."""

    education_terms = [
        "Bachelor of Technology",
        "Bachelor of Science",
        "Bachelor of Engineering",
        "Master of Science",
        "Master of Technology",
        "Master of Engineering",
        "Computer Science",
    ]

    return [
        term
        for term in education_terms
        if term.lower() in text.lower()
    ]


def test_education_extraction_accuracy(resume_dataset):
    correct = 0

    for item in resume_dataset:
        predicted = extract_education(item["text"])
        expected = item["expected"]["education"]

        expected_set = {
            normalize_skill(value)
            for value in expected
        }

        predicted_set = {
            normalize_skill(value)
            for value in predicted
        }

        if expected_set.issubset(predicted_set):
            correct += 1

    accuracy = correct / len(resume_dataset)

    assert accuracy >= 0.90


def test_education_extraction_does_not_invent_degree():
    text = """
    Candidate
    EXPERIENCE
    Software Developer

    SKILLS
    Python, Java
    """

    extracted = extract_education(text)

    assert extracted == []


# ============================================================================
# Experience extraction
# ============================================================================

def extract_experience_years(text: str) -> float:
    """
    Lightweight reference experience estimator.

    The production implementation should calculate experience from
    normalized employment intervals and handle overlapping positions.
    """

    ranges = re.findall(
        r"(20\d{2})\s*-\s*(Present|20\d{2})",
        text,
        flags=re.IGNORECASE,
    )

    if not ranges:
        return 0.0

    current_year = 2026
    total = 0

    for start, end in ranges:
        start_year = int(start)

        if end.lower() == "present":
            end_year = current_year
        else:
            end_year = int(end)

        if end_year >= start_year:
            total += end_year - start_year

    return float(total)


def test_experience_extraction_meets_minimum(
    resume_dataset,
):
    for item in resume_dataset:
        years = extract_experience_years(
            item["text"]
        )

        expected_min = item["expected"]["experience_years_min"]

        assert years >= expected_min


def test_present_employment_is_handled():
    text = """
    EXPERIENCE

    Software Engineer
    Example Corp
    2022 - Present
    """

    years = extract_experience_years(text)

    assert years >= 4


def test_historical_employment_range_is_handled():
    text = """
    EXPERIENCE

    Software Engineer
    Example Corp
    2018 - 2021
    """

    years = extract_experience_years(text)

    assert years == pytest.approx(3.0)


def test_missing_experience_returns_zero():
    text = """
    Candidate

    SKILLS
    Python, FastAPI
    """

    assert extract_experience_years(text) == 0.0


# ============================================================================
# Text cleaning
# ============================================================================

def clean_text(text: str) -> str:
    """Reference text cleaner."""

    text = text.replace("\r\n", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def test_text_cleaner_removes_excess_whitespace():
    text = "John    Doe\n\n\n\nPython"

    cleaned = clean_text(text)

    assert "    " not in cleaned
    assert "\n\n\n" not in cleaned


def test_text_cleaner_preserves_meaningful_content():
    text = """
    John Doe

    Python Developer

    Skills:
    Python, FastAPI
    """

    cleaned = clean_text(text)

    assert "John Doe" in cleaned
    assert "Python Developer" in cleaned
    assert "FastAPI" in cleaned


# ============================================================================
# Full extraction evaluation
# ============================================================================

def test_resume_extraction_has_high_field_accuracy(
    resume_dataset,
    skill_taxonomy,
):
    """
    Evaluate core structured fields across the synthetic dataset.
    """

    total = 0
    correct = 0

    for item in resume_dataset:
        text = item["text"]
        expected = item["expected"]

        # Name
        total += 1
        if exact_match(
            extract_name(text),
            expected["name"],
        ):
            correct += 1

        # Email
        total += 1
        if exact_match(
            extract_email(text),
            expected["email"],
        ):
            correct += 1

        # Phone
        total += 1
        if extract_phone(text) == expected["phone"]:
            correct += 1

        # Skills
        extracted_skills = extract_skills(
            text,
            skill_taxonomy,
        )

        total += 1
        if skill_recall(
            extracted_skills,
            expected["skills"],
        ) >= 0.90:
            correct += 1

        # Education
        extracted_education = extract_education(text)

        expected_education = {
            normalize_skill(value)
            for value in expected["education"]
        }

        predicted_education = {
            normalize_skill(value)
            for value in extracted_education
        }

        total += 1
        if expected_education.issubset(
            predicted_education
        ):
            correct += 1

    accuracy = correct / total

    assert accuracy >= 0.90


# ============================================================================
# Parser robustness
# ============================================================================

def test_parser_handles_empty_resume():
    text = ""

    assert extract_email(text) is None
    assert extract_phone(text) is None
    assert extract_skills(text, ["Python"]) == []
    assert extract_education(text) == []
    assert extract_experience_years(text) == 0.0


def test_parser_handles_whitespace_only_resume():
    text = "   \n\n\t   "

    assert extract_email(text) is None
    assert extract_phone(text) is None
    assert extract_skills(text, ["Python"]) == []


def test_parser_handles_unicode_text():
    text = """
    José García
    jose@example.com

    Skills:
    Python, React
    """

    assert extract_email(text) == "jose@example.com"

    skills = extract_skills(
        text,
        ["Python", "React"],
    )

    assert "Python" in skills
    assert "React" in skills


# ============================================================================
# False-positive tests
# ============================================================================

def test_email_is_not_taken_from_non_email_text():
    text = """
    Contact me through the company website.
    """

    assert extract_email(text) is None


def test_unrelated_numbers_are_not_treated_as_phone():
    text = """
    Graduation year: 2020
    GPA: 8.5
    """

    # The exact behavior can be tightened further in the production
    # phone extractor.
    phone = extract_phone(text)

    assert phone is None


def test_skill_extractor_does_not_match_empty_skill():
    text = "Python Developer"

    assert "" not in extract_skills(
        text,
        ["", "Python"],
    )


# ============================================================================
# Production integration contract
# ============================================================================

def test_resume_extractor_output_contract():
    """
    Integration contract for the production ResumeExtractor.

    Expected output shape:

        {
            "name": str | None,
            "email": str | None,
            "phone": str | None,
            "skills": list[str],
            "education": list[dict],
            "experience": list[dict],
        }

    Once ai/information_extraction/extractor.py is implemented, replace
    the reference extraction calls above with the real extractor.
    """

    text = """
    JOHN DOE

    john.doe@example.com

    SKILLS
    Python, FastAPI, PostgreSQL
    """

    result = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(
            text,
            [
                "Python",
                "FastAPI",
                "PostgreSQL",
            ],
        ),
        "education": extract_education(text),
        "experience": [],
    }

    assert isinstance(result, dict)

    assert "name" in result
    assert "email" in result
    assert "phone" in result
    assert "skills" in result
    assert "education" in result
    assert "experience" in result

    assert isinstance(result["skills"], list)
    assert isinstance(result["education"], list)
    assert isinstance(result["experience"], list)
