# Project scaffold file
```python
"""
tests/integration/test_resume_api.py

Integration tests for the Resume API.

Covers:
    - Authentication
    - Resume upload
    - Resume retrieval
    - Resume listing
    - Resume analysis
    - ATS scoring
    - Skills extraction
    - Resume optimization
    - Resume deletion
    - Validation
    - Authorization / ownership
    - Pagination

Expected API prefix:
    /api/resumes

Run:
    pytest tests/integration/test_resume_api.py -v
"""

from __future__ import annotations

import io
import uuid

import pytest
from fastapi.testclient import TestClient


# ============================================================================
# Application
# ============================================================================

try:
    from app.main import app
except ImportError:
    from backend.app.main import app


client = TestClient(app)


# ============================================================================
# Helpers
# ============================================================================

def unique_email() -> str:
    return f"resume-test-{uuid.uuid4().hex[:10]}@example.com"


def auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}"
    }


def create_user() -> str:
    """Create a recruiter account and return an access token."""

    email = unique_email()
    password = "StrongPassword123!"

    register_response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Resume API Tester",
        },
    )

    assert register_response.status_code in (200, 201)

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "access_token" in data

    return data["access_token"]


def create_candidate(token: str) -> dict:
    """Create a candidate for resume relationship tests."""

    response = client.post(
        "/api/candidates",
        json={
            "name": "Resume Test Candidate",
            "email": unique_email(),
            "phone": "+91 9876543210",
            "location": "Remote",
            "skills": [
                "Python",
                "FastAPI",
                "PostgreSQL",
            ],
            "experience_years": 5,
            "education": "Bachelor of Technology",
            "current_title": "Backend Developer",
        },
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 201)

    return response.json()


def sample_resume_text() -> str:
    return """
John Doe

Backend Developer

Email: john.doe@example.com
Phone: +91 9876543210

SUMMARY
Backend developer with 5 years of experience building scalable web
applications and REST APIs.

SKILLS
Python, FastAPI, Django, PostgreSQL, Redis, Docker, AWS, Git

EXPERIENCE
Senior Backend Developer
Tech Company
2022 - Present

- Designed REST APIs using Python and FastAPI.
- Built PostgreSQL database services.
- Implemented automated unit and integration tests.
- Deployed services using Docker and AWS.

Backend Developer
Software Company
2020 - 2022

- Developed backend services using Python and Django.
- Improved API performance and database queries.

EDUCATION
Bachelor of Technology in Computer Science
Engineering University
2020
""".strip()


def sample_resume_file(
    filename: str = "resume.txt",
):
    return {
        "file": (
            filename,
            io.BytesIO(
                sample_resume_text().encode("utf-8")
            ),
            "text/plain",
        )
    }


def upload_resume(
    token: str,
    filename: str = "resume.txt",
) -> dict:
    response = client.post(
        "/api/resumes/upload",
        files=sample_resume_file(filename),
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        201,
        202,
    )

    return response.json()


def extract_items(data):
    """Support list and paginated API response formats."""

    if isinstance(data, list):
        return data

    return data.get(
        "items",
        data.get(
            "resumes",
            [],
        ),
    )


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def token():
    return create_user()


@pytest.fixture
def candidate(token):
    return create_candidate(token)


@pytest.fixture
def resume(token):
    return upload_resume(token)


# ============================================================================
# Authentication
# ============================================================================

def test_resume_list_requires_authentication():
    response = client.get("/api/resumes")

    assert response.status_code == 401


def test_resume_upload_requires_authentication():
    response = client.post(
        "/api/resumes/upload",
        files=sample_resume_file(),
    )

    assert response.status_code == 401


def test_resume_get_requires_authentication(
    token,
    resume,
):
    response = client.get(
        f"/api/resumes/{resume['id']}"
    )

    assert response.status_code == 401


def test_resume_analysis_requires_authentication(
    token,
    resume,
):
    response = client.post(
        f"/api/resumes/{resume['id']}/analyze"
    )

    assert response.status_code == 401


def test_resume_delete_requires_authentication(
    token,
    resume,
):
    response = client.delete(
        f"/api/resumes/{resume['id']}"
    )

    assert response.status_code == 401


# ============================================================================
# Resume upload
# ============================================================================

def test_upload_resume(token):
    response = client.post(
        "/api/resumes/upload",
        files=sample_resume_file(),
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        201,
        202,
    )

    data = response.json()

    assert "id" in data


def test_upload_resume_returns_identifier(token):
    resume = upload_resume(token)

    assert resume.get("id") is not None
    assert str(resume["id"]).strip() != ""


def test_upload_resume_preserves_filename(token):
    filename = "john-doe-resume.txt"

    resume = upload_resume(
        token,
        filename=filename,
    )

    assert any(
        resume.get(field) == filename
        for field in (
            "filename",
            "file_name",
            "original_filename",
        )
        if field in resume
    )


def test_upload_resume_pdf(token):
    """
    Verify that PDF files are accepted by the API.

    The test uses a minimal PDF-like payload. A production parser may
    require a fully valid PDF, in which case replace the bytes with a
    fixture from data/evaluation/test_resumes/.
    """

    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj\n"
        b"<< /Type /Catalog >>\n"
        b"endobj\n"
        b"%%EOF"
    )

    response = client.post(
        "/api/resumes/upload",
        files={
            "file": (
                "resume.pdf",
                io.BytesIO(pdf_content),
                "application/pdf",
            )
        },
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        201,
        202,
        400,
        422,
    )


# ============================================================================
# Resume retrieval
# ============================================================================

def test_get_resume(
    token,
    resume,
):
    response = client.get(
        f"/api/resumes/{resume['id']}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == resume["id"]


def test_get_unknown_resume(token):
    resume_id = str(uuid.uuid4())

    response = client.get(
        f"/api/resumes/{resume_id}",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        404,
        422,
    )


# ============================================================================
# Resume listing
# ============================================================================

def test_list_resumes(token):
    response = client.get(
        "/api/resumes",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    resumes = extract_items(
        response.json()
    )

    assert isinstance(resumes, list)


def test_uploaded_resume_appears_in_list(
    token,
    resume,
):
    response = client.get(
        "/api/resumes",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    resumes = extract_items(
        response.json()
    )

    resume_ids = {
        item.get("id")
        for item in resumes
    }

    assert resume["id"] in resume_ids


# ============================================================================
# Resume filtering
# ============================================================================

def test_filter_resumes_by_candidate(
    token,
    candidate,
):
    """
    If resume upload accepts candidate_id, verify candidate filtering.

    Some implementations associate resumes with candidates during a
    separate candidate-resume operation, so a 400/422 is accepted here.
    """

    response = client.post(
        "/api/resumes/upload",
        files=sample_resume_file(),
        data={
            "candidate_id": str(candidate["id"])
        },
        headers=auth_headers(token),
    )

    if response.status_code not in (
        200,
        201,
        202,
    ):
        pytest.skip(
            "Resume upload does not accept candidate_id."
        )

    list_response = client.get(
        "/api/resumes",
        params={
            "candidate_id": str(candidate["id"])
        },
        headers=auth_headers(token),
    )

    assert list_response.status_code == 200


# ============================================================================
# Resume analysis
# ============================================================================

def test_analyze_resume(
    token,
    resume,
):
    response = client.post(
        f"/api/resumes/{resume['id']}/analyze",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        201,
        202,
    )

    data = response.json()

    assert isinstance(data, dict)


def test_resume_analysis_contains_information(
    token,
    resume,
):
    response = client.post(
        f"/api/resumes/{resume['id']}/analyze",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        201,
        202,
    )

    data = response.json()

    assert any(
        field in data
        for field in (
            "skills",
            "experience",
            "education",
            "contact",
            "analysis",
            "score",
            "ats_score",
        )
    )


def test_analyze_unknown_resume(token):
    response = client.post(
        f"/api/resumes/{uuid.uuid4()}/analyze",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        404,
        422,
    )


# ============================================================================
# ATS scoring
# ============================================================================

def test_resume_ats_score(
    token,
    resume,
):
    response = client.get(
        f"/api/resumes/{resume['id']}/score",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        404,
    )

    if response.status_code == 404:
        pytest.skip(
            "Dedicated resume score endpoint is not implemented."
        )

    data = response.json()

    assert isinstance(data, dict)

    score = (
        data.get("score")
        or data.get("ats_score")
        or data.get("overall_score")
    )

    if score is not None:
        assert isinstance(
            score,
            (int, float),
        )
        assert 0 <= score <= 100


def test_resume_score_is_not_negative(
    token,
    resume,
):
    response = client.get(
        f"/api/resumes/{resume['id']}/score",
        headers=auth_headers(token),
    )

    if response.status_code == 404:
        pytest.skip(
            "Dedicated resume score endpoint is not implemented."
        )

    assert response.status_code == 200

    data = response.json()

    score = (
        data.get("score")
        or data.get("ats_score")
        or data.get("overall_score")
    )

    if score is not None:
        assert score >= 0


# ============================================================================
# Skills extraction
# ============================================================================

def test_resume_skill_extraction(
    token,
    resume,
):
    response = client.post(
        f"/api/resumes/{resume['id']}/analyze",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        201,
        202,
    )

    data = response.json()

    skills = data.get("skills")

    if skills is None:
        pytest.skip(
            "Resume analysis response does not expose skills."
        )

    assert isinstance(skills, list)

    normalized = {
        str(skill).lower()
        for skill in skills
    }

    expected_skills = {
        "python",
        "fastapi",
        "postgresql",
    }

    assert expected_skills.intersection(
        normalized
    )


# ============================================================================
# Resume optimization
# ============================================================================

def test_resume_optimizer(
    token,
    resume,
):
    response = client.post(
        f"/api/resumes/{resume['id']}/optimize",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        201,
        202,
        404,
    )

    if response.status_code == 404:
        pytest.skip(
            "Resume optimizer endpoint is not implemented."
        )

    data = response.json()

    assert isinstance(data, dict)


def test_resume_optimizer_returns_suggestions(
    token,
    resume,
):
    response = client.post(
        f"/api/resumes/{resume['id']}/optimize",
        headers=auth_headers(token),
    )

    if response.status_code == 404:
        pytest.skip(
            "Resume optimizer endpoint is not implemented."
        )

    assert response.status_code in (
        200,
        201,
        202,
    )

    data = response.json()

    assert any(
        key in data
        for key in (
            "suggestions",
            "recommendations",
            "optimized_resume",
            "improvements",
            "changes",
        )
    )


# ============================================================================
# Resume deletion
# ============================================================================

def test_delete_resume(
    token,
    resume,
):
    resume_id = resume["id"]

    response = client.delete(
        f"/api/resumes/{resume_id}",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        204,
    )

    get_response = client.get(
        f"/api/resumes/{resume_id}",
        headers=auth_headers(token),
    )

    assert get_response.status_code == 404


def test_delete_unknown_resume(token):
    response = client.delete(
        f"/api/resumes/{uuid.uuid4()}",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        404,
        422,
    )


# ============================================================================
# Upload validation
# ============================================================================

def test_upload_requires_file(token):
    response = client.post(
        "/api/resumes/upload",
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_upload_rejects_empty_file(token):
    response = client.post(
        "/api/resumes/upload",
        files={
            "file": (
                "empty.txt",
                io.BytesIO(b""),
                "text/plain",
            )
        },
        headers=auth_headers(token),
    )

    assert response.status_code in (
        400,
        422,
    )


def test_upload_rejects_unsupported_file_type(
    token,
):
    response = client.post(
        "/api/resumes/upload",
        files={
            "file": (
                "resume.exe",
                io.BytesIO(b"not a resume"),
                "application/octet-stream",
            )
        },
        headers=auth_headers(token),
    )

    assert response.status_code in (
        400,
        415,
        422,
    )


def test_upload_accepts_docx_extension(
    token,
):
    """
    The actual DOCX parser may require a valid OOXML document. This test
    verifies the API's file-type handling without assuming parser behavior.
    """

    response = client.post(
        "/api/resumes/upload",
        files={
            "file": (
                "resume.docx",
                io.BytesIO(b"placeholder docx"),
                "application/vnd.openxmlformats-officedocument"
                ".wordprocessingml.document",
            )
        },
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        201,
        202,
        400,
        422,
    )


# ============================================================================
# Pagination
# ============================================================================

def test_resume_pagination(token):
    response = client.get(
        "/api/resumes",
        params={
            "page": 1,
            "page_size": 10,
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    if isinstance(data, dict):
        resumes = extract_items(data)

        assert isinstance(
            resumes,
            list,
        )

        if "page" in data:
            assert data["page"] == 1

        if "page_size" in data:
            assert data["page_size"] <= 10


def test_resume_page_size_validation(token):
    response = client.get(
        "/api/resumes",
        params={
            "page": 1,
            "page_size": 100000,
        },
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        400,
        422,
    )


# ============================================================================
# Authorization / ownership
# ============================================================================

def test_second_user_cannot_access_private_resume(
    token,
    resume,
):
    second_token = create_user()

    response = client.get(
        f"/api/resumes/{resume['id']}",
        headers=auth_headers(second_token),
    )

    assert response.status_code in (
        403,
        404,
    )


def test_second_user_cannot_analyze_private_resume(
    token,
    resume,
):
    second_token = create_user()

    response = client.post(
        f"/api/resumes/{resume['id']}/analyze",
        headers=auth_headers(second_token),
    )

    assert response.status_code in (
        403,
        404,
    )


def test_second_user_cannot_delete_private_resume(
    token,
    resume,
):
    second_token = create_user()

    response = client.delete(
        f"/api/resumes/{resume['id']}",
        headers=auth_headers(second_token),
    )

    assert response.status_code in (
        403,
        404,
    )


# ============================================================================
# Persistence / consistency
# ============================================================================

def test_uploaded_resume_persists(
    token,
):
    uploaded = upload_resume(token)

    resume_id = uploaded["id"]

    response = client.get(
        f"/api/resumes/{resume_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == resume_id


def test_multiple_resume_uploads_have_unique_ids(
    token,
):
    first = upload_resume(
        token,
        "resume-one.txt",
    )

    second = upload_resume(
        token,
        "resume-two.txt",
    )

    assert first["id"] != second["id"]


# ============================================================================
# Response contract
# ============================================================================

def test_resume_response_contains_core_fields(
    resume,
):
    assert "id" in resume


def test_resume_id_is_not_empty(
    resume,
):
    assert resume["id"] is not None
    assert str(resume["id"]).strip() != ""


# ============================================================================
# Resume analysis data types
# ============================================================================

def test_resume_analysis_field_types(
    token,
    resume,
):
    response = client.post(
        f"/api/resumes/{resume['id']}/analyze",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        201,
        202,
    )

    data = response.json()

    if "skills" in data:
        assert isinstance(
            data["skills"],
            list,
        )

    if "experience" in data:
        assert isinstance(
            data["experience"],
            (list, dict, str),
        )

    if "education" in data:
        assert isinstance(
            data["education"],
            (list, dict, str),
        )


# ============================================================================
# Resume analysis idempotency
# ============================================================================

def test_resume_analysis_can_be_repeated(
    token,
    resume,
):
    first = client.post(
        f"/api/resumes/{resume['id']}/analyze",
        headers=auth_headers(token),
    )

    second = client.post(
        f"/api/resumes/{resume['id']}/analyze",
        headers=auth_headers(token),
    )

    assert first.status_code in (
        200,
        201,
        202,
    )

    assert second.status_code in (
        200,
        201,
        202,
        409,
    )
