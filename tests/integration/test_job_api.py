"""
tests/integration/test_job_api.py

Integration tests for the Job API.

Covers:
    - Authentication
    - Job creation
    - Job retrieval
    - Job listing
    - Job updating
    - Job deletion
    - Job filtering/search
    - Job description analysis
    - Validation
    - Authorization / ownership
    - Pagination

Expected API prefix:
    /api/jobs

Run:
    pytest tests/integration/test_job_api.py -v
"""

from __future__ import annotations

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
    return f"job-test-{uuid.uuid4().hex[:10]}@example.com"


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
            "full_name": "Job API Tester",
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


def job_payload(
    title: str = "Backend Developer",
):
    return {
        "title": title,
        "description": (
            "We are looking for a backend developer "
            "to build scalable APIs and services."
        ),
        "requirements": [
            "Python",
            "FastAPI",
            "PostgreSQL",
            "REST APIs",
        ],
        "responsibilities": [
            "Design backend APIs",
            "Write automated tests",
            "Review code",
            "Maintain production services",
        ],
        "experience_required": 3,
        "location": "Remote",
        "employment_type": "full-time",
    }


def create_job(token: str) -> dict:
    response = client.post(
        "/api/jobs",
        json=job_payload(),
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 201)

    return response.json()


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def token():
    return create_user()


@pytest.fixture
def job(token):
    return create_job(token)


# ============================================================================
# Authentication
# ============================================================================

def test_list_jobs_requires_authentication():
    response = client.get("/api/jobs")

    assert response.status_code == 401


def test_create_job_requires_authentication():
    response = client.post(
        "/api/jobs",
        json=job_payload(),
    )

    assert response.status_code == 401


def test_get_job_requires_authentication():
    token = create_user()
    created_job = create_job(token)

    response = client.get(
        f"/api/jobs/{created_job['id']}"
    )

    assert response.status_code == 401


def test_update_job_requires_authentication():
    token = create_user()
    created_job = create_job(token)

    response = client.patch(
        f"/api/jobs/{created_job['id']}",
        json={
            "title": "Updated Developer"
        },
    )

    assert response.status_code == 401


def test_delete_job_requires_authentication():
    token = create_user()
    created_job = create_job(token)

    response = client.delete(
        f"/api/jobs/{created_job['id']}"
    )

    assert response.status_code == 401


# ============================================================================
# Job creation
# ============================================================================

def test_create_job(token):
    payload = job_payload()

    response = client.post(
        "/api/jobs",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert "id" in data
    assert data["title"] == payload["title"]


def test_create_job_returns_core_fields(token):
    response = client.post(
        "/api/jobs",
        json=job_payload(),
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert "id" in data
    assert "title" in data


def test_create_job_preserves_description(token):
    payload = job_payload()

    response = client.post(
        "/api/jobs",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert data["description"] == payload["description"]


def test_create_job_preserves_requirements(token):
    payload = job_payload()

    response = client.post(
        "/api/jobs",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert "requirements" in data

    returned = {
        str(item).lower()
        for item in data["requirements"]
    }

    expected = {
        str(item).lower()
        for item in payload["requirements"]
    }

    assert expected.issubset(returned)


def test_create_job_preserves_responsibilities(token):
    payload = job_payload()

    response = client.post(
        "/api/jobs",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 201)

    data = response.json()

    if "responsibilities" not in data:
        pytest.skip(
            "Job response does not expose responsibilities."
        )

    returned = {
        str(item).lower()
        for item in data["responsibilities"]
    }

    expected = {
        str(item).lower()
        for item in payload["responsibilities"]
    }

    assert expected.issubset(returned)


# ============================================================================
# Job retrieval
# ============================================================================

def test_get_job(
    token,
    job,
):
    response = client.get(
        f"/api/jobs/{job['id']}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == job["id"]
    assert data["title"] == job["title"]


def test_get_unknown_job(token):
    job_id = str(uuid.uuid4())

    response = client.get(
        f"/api/jobs/{job_id}",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        404,
        422,
    )


def test_job_id_is_not_empty(job):
    assert job["id"] is not None
    assert str(job["id"]).strip() != ""


# ============================================================================
# Job listing
# ============================================================================

def test_list_jobs(token):
    response = client.get(
        "/api/jobs",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    if isinstance(data, list):
        jobs = data
    else:
        jobs = data.get(
            "items",
            data.get(
                "jobs",
                [],
            ),
        )

    assert isinstance(jobs, list)


def test_created_job_appears_in_list(
    token,
    job,
):
    response = client.get(
        "/api/jobs",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    if isinstance(data, list):
        jobs = data
    else:
        jobs = data.get(
            "items",
            data.get(
                "jobs",
                [],
            ),
        )

    job_ids = {
        item.get("id")
        for item in jobs
    }

    assert job["id"] in job_ids


# ============================================================================
# Job search
# ============================================================================

def test_search_jobs_by_title(token):
    unique_title = (
        f"Python Engineer "
        f"{uuid.uuid4().hex[:6]}"
    )

    response = client.post(
        "/api/jobs",
        json=job_payload(
            title=unique_title
        ),
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 201)

    search_response = client.get(
        "/api/jobs",
        params={
            "search": unique_title
        },
        headers=auth_headers(token),
    )

    assert search_response.status_code == 200

    data = search_response.json()

    if isinstance(data, list):
        jobs = data
    else:
        jobs = data.get(
            "items",
            data.get(
                "jobs",
                [],
            ),
        )

    assert any(
        item.get("title") == unique_title
        for item in jobs
    )


def test_filter_jobs_by_location(token):
    response = client.get(
        "/api/jobs",
        params={
            "location": "Remote"
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200


def test_filter_jobs_by_employment_type(token):
    response = client.get(
        "/api/jobs",
        params={
            "employment_type": "full-time"
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200


def test_filter_jobs_by_experience(token):
    response = client.get(
        "/api/jobs",
        params={
            "min_experience": 3
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200


# ============================================================================
# Pagination
# ============================================================================

def test_job_pagination(token):
    response = client.get(
        "/api/jobs",
        params={
            "page": 1,
            "page_size": 10,
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    if isinstance(data, dict):
        jobs = data.get(
            "items",
            data.get(
                "jobs",
                [],
            ),
        )

        assert isinstance(jobs, list)

        if "page" in data:
            assert data["page"] == 1

        if "page_size" in data:
            assert data["page_size"] <= 10


def test_job_page_size_validation(token):
    response = client.get(
        "/api/jobs",
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
# Job update
# ============================================================================

def test_update_job(
    token,
    job,
):
    response = client.patch(
        f"/api/jobs/{job['id']}",
        json={
            "title": "Senior Backend Developer",
            "experience_required": 5,
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == job["id"]

    if "title" in data:
        assert (
            data["title"]
            == "Senior Backend Developer"
        )

    if "experience_required" in data:
        assert data["experience_required"] == 5


def test_update_unknown_job(token):
    response = client.patch(
        f"/api/jobs/{uuid.uuid4()}",
        json={
            "title": "Updated Job"
        },
        headers=auth_headers(token),
    )

    assert response.status_code in (
        404,
        422,
    )


def test_partial_job_update(
    token,
    job,
):
    original_description = job.get("description")

    response = client.patch(
        f"/api/jobs/{job['id']}",
        json={
            "title": "Partially Updated Job"
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Partially Updated Job"

    if original_description is not None:
        assert data["description"] == original_description


# ============================================================================
# Job deletion
# ============================================================================

def test_delete_job(
    token,
    job,
):
    response = client.delete(
        f"/api/jobs/{job['id']}",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        204,
    )

    get_response = client.get(
        f"/api/jobs/{job['id']}",
        headers=auth_headers(token),
    )

    assert get_response.status_code == 404


def test_delete_unknown_job(token):
    response = client.delete(
        f"/api/jobs/{uuid.uuid4()}",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        404,
        422,
    )


# ============================================================================
# Job description analysis
# ============================================================================

def test_job_description_analysis(
    token,
    job,
):
    """
    Tests the JD-analysis endpoint if it is exposed through the Job API.

    Common implementation:
        POST /api/jobs/{job_id}/analyze

    If JD analysis is handled asynchronously or through another endpoint,
    this test can be adapted accordingly.
    """

    response = client.post(
        f"/api/jobs/{job['id']}/analyze",
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
            "Job description analysis endpoint is not implemented."
        )

    data = response.json()

    assert isinstance(data, dict)


def test_job_analysis_contains_requirements(
    token,
    job,
):
    response = client.post(
        f"/api/jobs/{job['id']}/analyze",
        headers=auth_headers(token),
    )

    if response.status_code == 404:
        pytest.skip(
            "Job description analysis endpoint is not implemented."
        )

    if response.status_code not in (
        200,
        201,
        202,
    ):
        pytest.skip(
            "JD analysis is not currently available."
        )

    data = response.json()

    # At least one structured analysis field should normally exist.
    assert any(
        key in data
        for key in (
            "requirements",
            "skills",
            "responsibilities",
            "keywords",
            "analysis",
        )
    )


# ============================================================================
# Validation
# ============================================================================

def test_create_job_requires_title(token):
    payload = job_payload()

    del payload["title"]

    response = client.post(
        "/api/jobs",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_create_job_rejects_empty_title(token):
    payload = job_payload()

    payload["title"] = ""

    response = client.post(
        "/api/jobs",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code in (
        400,
        422,
    )


def test_create_job_requires_description(token):
    payload = job_payload()

    del payload["description"]

    response = client.post(
        "/api/jobs",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_create_job_rejects_negative_experience(
    token,
):
    payload = job_payload()

    payload["experience_required"] = -1

    response = client.post(
        "/api/jobs",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_create_job_rejects_invalid_payload(token):
    response = client.post(
        "/api/jobs",
        json={
            "invalid": "payload"
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 422


# ============================================================================
# Authorization / ownership
# ============================================================================

def test_second_user_cannot_access_private_job(
    token,
    job,
):
    second_token = create_user()

    response = client.get(
        f"/api/jobs/{job['id']}",
        headers=auth_headers(second_token),
    )

    assert response.status_code in (
        403,
        404,
    )


def test_second_user_cannot_update_private_job(
    token,
    job,
):
    second_token = create_user()

    response = client.patch(
        f"/api/jobs/{job['id']}",
        json={
            "title": "Unauthorized Update"
        },
        headers=auth_headers(second_token),
    )

    assert response.status_code in (
        403,
        404,
    )


def test_second_user_cannot_delete_private_job(
    token,
    job,
):
    second_token = create_user()

    response = client.delete(
        f"/api/jobs/{job['id']}",
        headers=auth_headers(second_token),
    )

    assert response.status_code in (
        403,
        404,
    )


# ============================================================================
# Job response contract
# ============================================================================

def test_job_response_has_required_fields(job):
    required_fields = {
        "id",
        "title",
    }

    assert required_fields.issubset(
        job.keys()
    )


def test_job_title_is_not_empty(job):
    assert job["title"] is not None
    assert str(job["title"]).strip() != ""


def test_job_description_is_not_empty(job):
    if "description" not in job:
        pytest.skip(
            "Job response does not expose description."
        )

    assert job["description"] is not None
    assert str(job["description"]).strip() != ""


# ============================================================================
# Duplicate / consistency behavior
# ============================================================================

def test_create_multiple_jobs(
    token,
):
    first = create_job(token)

    second_response = client.post(
        "/api/jobs",
        json=job_payload(
            title="Another Backend Developer"
        ),
        headers=auth_headers(token),
    )

    assert second_response.status_code in (
        200,
        201,
    )

    second = second_response.json()

    assert first["id"] != second["id"]


def test_job_update_persists(
    token,
    job,
):
    new_title = "Persistent Updated Job"

    update_response = client.patch(
        f"/api/jobs/{job['id']}",
        json={
            "title": new_title
        },
        headers=auth_headers(token),
    )

    assert update_response.status_code == 200

    get_response = client.get(
        f"/api/jobs/{job['id']}",
        headers=auth_headers(token),
    )

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["title"] == new_title
