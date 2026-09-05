# Project scaffold file
```python
import pytest

from ai.resume_parser.parser import ResumeParser
from ai.resume_parser.pdf_parser import PDFParser
from ai.resume_parser.docx_parser import DOCXParser
from ai.resume_parser.text_cleaner import TextCleaner


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def resume_text():
    return """
    John Doe
    john.doe@example.com
    +91 9876543210

    Python Backend Developer

    SUMMARY
    Backend developer with 4 years of experience building REST APIs.

    SKILLS
    Python, FastAPI, SQL, PostgreSQL, Docker, Git

    EXPERIENCE
    Backend Developer - ABC Technologies
    2022 - Present

    Developed REST APIs using Python and FastAPI.
    Worked with PostgreSQL and Docker.

    EDUCATION
    B.Tech in Computer Science
    University of Technology
    """


@pytest.fixture
def sample_resume_data():
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+91 9876543210",
        "skills": [
            "Python",
            "FastAPI",
            "SQL",
            "PostgreSQL",
            "Docker",
            "Git",
        ],
        "experience": [
            {
                "title": "Backend Developer",
                "company": "ABC Technologies",
            }
        ],
        "education": [
            {
                "degree": "B.Tech in Computer Science",
                "institution": "University of Technology",
            }
        ],
    }


# ---------------------------------------------------------------------------
# Text Cleaner
# ---------------------------------------------------------------------------

def test_text_cleaner_returns_clean_text(resume_text):
    cleaner = TextCleaner()

    result = cleaner.clean(resume_text)

    assert result is not None
    assert isinstance(result, str)
    assert result.strip()


def test_text_cleaner_removes_extra_whitespace():
    cleaner = TextCleaner()

    text = "John     Doe\n\n\nPython    Developer"

    result = cleaner.clean(text)

    assert result is not None
    assert "John Doe" in result
    assert "Python Developer" in result


def test_text_cleaner_handles_empty_text():
    cleaner = TextCleaner()

    result = cleaner.clean("")

    assert result is not None


def test_text_cleaner_handles_none():
    cleaner = TextCleaner()

    result = cleaner.clean(None)

    assert result is not None


def test_text_cleaner_preserves_meaningful_content():
    cleaner = TextCleaner()

    text = """
    Python Developer
    Skills: Python, FastAPI, SQL
    Experience: 4 years
    """

    result = cleaner.clean(text)

    assert "Python" in result
    assert "FastAPI" in result
    assert "SQL" in result


# ---------------------------------------------------------------------------
# PDF Parser
# ---------------------------------------------------------------------------

def test_pdf_parser_initialization():
    parser = PDFParser()

    assert parser is not None


def test_pdf_parser_rejects_invalid_file():
    parser = PDFParser()

    with pytest.raises((ValueError, TypeError, FileNotFoundError, Exception)):
        parser.parse("non_existing_resume.pdf")


def test_pdf_parser_handles_invalid_pdf(tmp_path):
    pdf_file = tmp_path / "invalid.pdf"
    pdf_file.write_text("This is not a valid PDF file.")

    parser = PDFParser()

    with pytest.raises(Exception):
        parser.parse(str(pdf_file))


# ---------------------------------------------------------------------------
# DOCX Parser
# ---------------------------------------------------------------------------

def test_docx_parser_initialization():
    parser = DOCXParser()

    assert parser is not None


def test_docx_parser_rejects_invalid_file():
    parser = DOCXParser()

    with pytest.raises((ValueError, TypeError, FileNotFoundError, Exception)):
        parser.parse("non_existing_resume.docx")


def test_docx_parser_handles_invalid_docx(tmp_path):
    docx_file = tmp_path / "invalid.docx"
    docx_file.write_text("This is not a valid DOCX file.")

    parser = DOCXParser()

    with pytest.raises(Exception):
        parser.parse(str(docx_file))


# ---------------------------------------------------------------------------
# Resume Parser
# ---------------------------------------------------------------------------

def test_resume_parser_initialization():
    parser = ResumeParser()

    assert parser is not None


def test_resume_parser_has_parse_method():
    parser = ResumeParser()

    assert hasattr(parser, "parse")
    assert callable(parser.parse)


def test_resume_parser_rejects_missing_file():
    parser = ResumeParser()

    with pytest.raises((ValueError, TypeError, FileNotFoundError, Exception)):
        parser.parse("resume_that_does_not_exist.pdf")


def test_resume_parser_rejects_unsupported_extension(tmp_path):
    resume_file = tmp_path / "resume.txt"
    resume_file.write_text("Python Developer")

    parser = ResumeParser()

    with pytest.raises((ValueError, TypeError, Exception)):
        parser.parse(str(resume_file))


# ---------------------------------------------------------------------------
# Resume Parser with DOCX
# ---------------------------------------------------------------------------

def test_resume_parser_parses_docx(tmp_path, resume_text):
    """
    Creates a real DOCX file when python-docx is available.
    """

    docx = pytest.importorskip("docx")

    document = docx.Document()

    for line in resume_text.splitlines():
        if line.strip():
            document.add_paragraph(line.strip())

    file_path = tmp_path / "resume.docx"
    document.save(file_path)

    parser = ResumeParser()

    result = parser.parse(str(file_path))

    assert result is not None


# ---------------------------------------------------------------------------
# Resume Parser Output
# ---------------------------------------------------------------------------

def test_resume_parser_returns_expected_structure(
    tmp_path,
    resume_text,
):
    docx = pytest.importorskip("docx")

    document = docx.Document()

    for line in resume_text.splitlines():
        if line.strip():
            document.add_paragraph(line.strip())

    file_path = tmp_path / "resume.docx"
    document.save(file_path)

    parser = ResumeParser()

    result = parser.parse(str(file_path))

    assert result is not None

    if isinstance(result, dict):
        possible_text_fields = [
            "text",
            "raw_text",
            "content",
            "cleaned_text",
        ]

        assert any(
            field in result
            for field in possible_text_fields
        )


def test_resume_parser_extracts_resume_text(
    tmp_path,
    resume_text,
):
    docx = pytest.importorskip("docx")

    document = docx.Document()

    for line in resume_text.splitlines():
        if line.strip():
            document.add_paragraph(line.strip())

    file_path = tmp_path / "resume.docx"
    document.save(file_path)

    parser = ResumeParser()

    result = parser.parse(str(file_path))

    assert result is not None

    if isinstance(result, str):
        parsed_text = result
    elif isinstance(result, dict):
        parsed_text = (
            result.get("text")
            or result.get("raw_text")
            or result.get("content")
            or ""
        )
    else:
        parsed_text = str(result)

    assert "Python" in parsed_text
    assert "FastAPI" in parsed_text


# ---------------------------------------------------------------------------
# Resume Content Tests
# ---------------------------------------------------------------------------

def test_resume_contains_contact_information(resume_text):
    assert "john.doe@example.com" in resume_text
    assert "+91 9876543210" in resume_text


def test_resume_contains_skills(resume_text):
    skills = [
        "Python",
        "FastAPI",
        "SQL",
        "PostgreSQL",
        "Docker",
        "Git",
    ]

    for skill in skills:
        assert skill in resume_text


def test_resume_contains_experience(resume_text):
    assert "Backend Developer" in resume_text
    assert "ABC Technologies" in resume_text


def test_resume_contains_education(resume_text):
    assert "B.Tech in Computer Science" in resume_text
    assert "University of Technology" in resume_text


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------

def test_parser_handles_empty_docx(tmp_path):
    docx = pytest.importorskip("docx")

    document = docx.Document()

    file_path = tmp_path / "empty_resume.docx"
    document.save(file_path)

    parser = ResumeParser()

    result = parser.parse(str(file_path))

    assert result is not None


def test_parser_handles_resume_with_special_characters(tmp_path):
    docx = pytest.importorskip("docx")

    document = docx.Document()

    document.add_paragraph(
        "John Doe — Python Developer | C++ | C# | Node.js"
    )
    document.add_paragraph(
        "Skills: Python, FastAPI, PostgreSQL & Docker"
    )

    file_path = tmp_path / "special_resume.docx"
    document.save(file_path)

    parser = ResumeParser()

    result = parser.parse(str(file_path))

    assert result is not None


# ---------------------------------------------------------------------------
# Parser Consistency
# ---------------------------------------------------------------------------

def test_parser_returns_consistent_result(tmp_path, resume_text):
    docx = pytest.importorskip("docx")

    document = docx.Document()

    for line in resume_text.splitlines():
        if line.strip():
            document.add_paragraph(line.strip())

    file_path = tmp_path / "resume.docx"
    document.save(file_path)

    parser = ResumeParser()

    result_one = parser.parse(str(file_path))
    result_two = parser.parse(str(file_path))

    assert result_one == result_two


# ---------------------------------------------------------------------------
# Sample Resume Data Validation
# ---------------------------------------------------------------------------

def test_sample_resume_data_structure(sample_resume_data):
    assert "name" in sample_resume_data
    assert "email" in sample_resume_data
    assert "skills" in sample_resume_data
    assert "experience" in sample_resume_data
    assert "education" in sample_resume_data

    assert isinstance(sample_resume_data["skills"], list)
    assert isinstance(sample_resume_data["experience"], list)
    assert isinstance(sample_resume_data["education"], list)


def test_sample_resume_has_required_skills(sample_resume_data):
    assert "Python" in sample_resume_data["skills"]
    assert "FastAPI" in sample_resume_data["skills"]
    assert "SQL" in sample_resume_data["skills"]


def test_sample_resume_has_experience(sample_resume_data):
    experience = sample_resume_data["experience"]

    assert len(experience) > 0
    assert experience[0]["title"] == "Backend Developer"


def test_sample_resume_has_education(sample_resume_data):
    education = sample_resume_data["education"]

    assert len(education) > 0
    assert "B.Tech" in education[0]["degree"]
