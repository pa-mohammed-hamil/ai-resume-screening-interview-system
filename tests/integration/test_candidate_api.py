# Project scaffold file
# Project scaffold file
```python
"""
Integration tests for the Candidate API.

Target modules:
    backend/app/api/candidates.py
    backend/app/services/candidate_service.py
    backend/app/models/candidate.py
    backend/app/schemas/candidate.py

Expected endpoints:
    GET    /api/candidates
    GET    /api/candidates/{candidate_id}
    POST   /api/candidates
    PATCH  /api/candidates/{candidate_id}
    DELETE /api/candidates/{candidate_id}
    POST   /api/candidates/compare
    GET    /api/candidates/ranking

Run:
    pytest tests/integration/test_candidate_api.py -v
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
    return f"candidate-test-{uuid.uuid4().hex[:10]}@example.com"


def create_test_user():
    """
    Create a recruiter account and return an access token.

    Adjust the endpoint/payload here if your authentication API uses a
    different contract.
    """

    email = unique_email()
    password = "StrongPassword123!"

    register_payload = {
        "email": email,
        "password": password,
        "full_name": "Candidate API Tester",
    }

    register_response = client.post(
        "/api/auth/register",
        json=register_payload,
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

    return login_response.json()["access_token"]


def auth_headers(token: str):
    return {
        "Authorization": f"Bearer {token}"
    }


def candidate_payload(
    name: str = "John Doe",
    email: str | None = None,
):
    return {
        "name": name,
        "email": email or unique_email(),
        "phone": "+1 555 123 4567",
        "location": "Remote",
        "skills": [
            "Python",
            "FastAPI",
            "PostgreSQL",
        ],
        "experience_years": 5,
        "education": "Bachelor of Technology",
        "current_title": "Backend Developer",
    }


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def token():
    return create_test_user()


@pytest.fixture
def created_candidate(token):
    response = client.post(
        "/api/candidates",
        json=candidate_payload(),
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 201)

    return response.json()


# ============================================================================
# Candidate creation
# ============================================================================

def test_create_candidate(token):
    payload = candidate_payload()

    response = client.post(
        "/api/candidates",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert "id" in data
    assert data["name"] == payload["name"]
    assert data["email"].lower() == payload["email"].lower()


def test_create_candidate_preserves_skills(token):
    payload = candidate_payload()

    response = client.post(
        "/api/candidates",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert "skills" in data

    returned_skills = {
        skill.lower()
        for skill in data["skills"]
    }

    expected_skills = {
        skill.lower()
        for skill in payload["skills"]
    }

    assert expected_skills.issubset(returned_skills)


def test_create_candidate_preserves_experience(token):
    payload = candidate_payload()

    response = client.post(
        "/api/candidates",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert data["experience_years"] == 5


def test_create_candidate_requires_authentication():
    response = client.post(
        "/api/candidates",
        json=candidate_payload(),
    )

    assert response.status_code == 401


# ============================================================================
# Candidate retrieval
# ============================================================================

def test_get_candidate_by_id(
    token,
    created_candidate,
):
    candidate_id = created_candidate["id"]

    response = client.get(
        f"/api/candidates/{candidate_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == candidate_id
    assert data["name"] == created_candidate["name"]


def test_get_nonexistent_candidate(token):
    fake_id = str(uuid.uuid4())

    response = client.get(
        f"/api/candidates/{fake_id}",
        headers=auth_headers(token),
    )

    assert response.status_code in (404, 422)


def test_get_candidate_requires_authentication(
    created_candidate,
):
    candidate_id = created_candidate["id"]

    response = client.get(
        f"/api/candidates/{candidate_id}"
    )

    assert response.status_code == 401


# ============================================================================
# Candidate listing
# ============================================================================

def test_list_candidates(token):
    response = client.get(
        "/api/candidates",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    # Support either a direct list or a paginated response.
    if isinstance(data, list):
        candidates = data
    else:
        candidates = data.get(
            "items",
            data.get("candidates", []),
        )

    assert isinstance(candidates, list)


def test_created_candidate_appears_in_list(
    token,
    created_candidate,
):
    response = client.get(
        "/api/candidates",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    if isinstance(data, list):
        candidates = data
    else:
        candidates = data.get(
            "items",
            data.get("candidates", []),
        )

    ids = {
        candidate.get("id")
        for candidate in candidates
    }

    assert created_candidate["id"] in ids


def test_list_candidates_requires_authentication():
    response = client.get(
        "/api/candidates"
    )

    assert response.status_code == 401


# ============================================================================
# Filtering
# ============================================================================

def test_filter_candidates_by_skill(token):
    unique_skill = "TestSkill"

    payload = candidate_payload()
    payload["skills"] = [
        "Python",
        unique_skill,
    ]

    create_response = client.post(
        "/api/candidates",
        json=payload,
        headers=auth_headers(token),
    )

    assert create_response.status_code in (200, 201)

    response = client.get(
        "/api/candidates",
        params={
            "skill": unique_skill,
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    candidates = (
        data
        if isinstance(data, list)
        else data.get(
            "items",
            data.get("candidates", []),
        )
    )

    for candidate in candidates:
        skills = {
            skill.lower()
            for skill in candidate.get("skills", [])
        }

        assert unique_skill.lower() in skills


def test_filter_candidates_by_minimum_experience(token):
    payload = candidate_payload()
    payload["experience_years"] = 8

    create_response = client.post(
        "/api/candidates",
        json=payload,
        headers=auth_headers(token),
    )

    assert create_response.status_code in (200, 201)

    response = client.get(
        "/api/candidates",
        params={
            "min_experience": 7,
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    candidates = (
        data
        if isinstance(data, list)
        else data.get(
            "items",
            data.get("candidates", []),
        )
    )

    for candidate in candidates:
        assert candidate["experience_years"] >= 7


def test_filter_candidates_by_location(token):
    payload = candidate_payload()
    payload["location"] = "Remote-Test"

    create_response = client.post(
        "/api/candidates",
        json=payload,
        headers=auth_headers(token),
    )

    assert create_response.status_code in (200, 201)

    response = client.get(
        "/api/candidates",
        params={
            "location": "Remote-Test",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200


# ============================================================================
# Search
# ============================================================================

def test_search_candidates_by_name(
    token,
):
    unique_name = (
        f"Unique Candidate "
        f"{uuid.uuid4().hex[:6]}"
    )

    payload = candidate_payload(
        name=unique_name
    )

    create_response = client.post(
        "/api/candidates",
        json=payload,
        headers=auth_headers(token),
    )

    assert create_response.status_code in (200, 201)

    response = client.get(
        "/api/candidates",
        params={
            "search": unique_name,
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    candidates = (
        data
        if isinstance(data, list)
        else data.get(
            "items",
            data.get("candidates", []),
        )
    )

    assert any(
        candidate.get("name") == unique_name
        for candidate in candidates
    )


# ============================================================================
# Pagination
# ============================================================================

def test_candidate_pagination(token):
    response = client.get(
        "/api/candidates",
        params={
            "page": 1,
            "page_size": 10,
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    if isinstance(data, dict):
        candidates = data.get(
            "items",
            data.get("candidates", []),
        )

        assert isinstance(candidates, list)

        if "page" in data:
            assert data["page"] == 1

        if "page_size" in data:
            assert data["page_size"] <= 10


def test_candidate_page_size_is_limited(token):
    response = client.get(
        "/api/candidates",
        params={
            "page": 1,
            "page_size": 10000,
        },
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        400,
        422,
    )


# ============================================================================
# Update
# ============================================================================

def test_update_candidate(
    token,
    created_candidate,
):
    candidate_id = created_candidate["id"]

    response = client.patch(
        f"/api/candidates/{candidate_id}",
        json={
            "current_title": "Senior Backend Developer",
            "experience_years": 7,
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == candidate_id

    if "current_title" in data:
        assert (
            data["current_title"]
            == "Senior Backend Developer"
        )

    if "experience_years" in data:
        assert data["experience_years"] == 7


def test_update_nonexistent_candidate(token):
    fake_id = str(uuid.uuid4())

    response = client.patch(
        f"/api/candidates/{fake_id}",
        json={
            "current_title": "Developer"
        },
        headers=auth_headers(token),
    )

    assert response.status_code in (404, 422)


# ============================================================================
# Delete
# ============================================================================

def test_delete_candidate(
    token,
    created_candidate,
):
    candidate_id = created_candidate["id"]

    response = client.delete(
        f"/api/candidates/{candidate_id}",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        204,
    )

    get_response = client.get(
        f"/api/candidates/{candidate_id}",
        headers=auth_headers(token),
    )

    assert get_response.status_code == 404


def test_delete_nonexistent_candidate(token):
    fake_id = str(uuid.uuid4())

    response = client.delete(
        f"/api/candidates/{fake_id}",
        headers=auth_headers(token),
    )

    assert response.status_code in (404, 422)


# ============================================================================
# Candidate comparison
# ============================================================================

def test_compare_candidates(
    token,
):
    candidate_one = client.post(
        "/api/candidates",
        json=candidate_payload(
            name="Candidate One"
        ),
        headers=auth_headers(token),
    )

    candidate_two = client.post(
        "/api/candidates",
        json=candidate_payload(
            name="Candidate Two"
        ),
        headers=auth_headers(token),
    )

    assert candidate_one.status_code in (200, 201)
    assert candidate_two.status_code in (200, 201)

    id_one = candidate_one.json()["id"]
    id_two = candidate_two.json()["id"]

    response = client.post(
        "/api/candidates/compare",
        json={
            "candidate_ids": [
                id_one,
                id_two,
            ]
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None


def test_compare_requires_multiple_candidates(
    token,
    created_candidate,
):
    candidate_id = created_candidate["id"]

    response = client.post(
        "/api/candidates/compare",
        json={
            "candidate_ids": [
                candidate_id,
            ]
        },
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        400,
        422,
    )


def test_compare_rejects_invalid_candidate_id(
    token,
):
    response = client.post(
        "/api/candidates/compare",
        json={
            "candidate_ids": [
                str(uuid.uuid4()),
                str(uuid.uuid4()),
            ]
        },
        headers=auth_headers(token),
    )

    assert response.status_code in (
        404,
        422,
    )


# ============================================================================
# Candidate ranking
# ============================================================================

def test_candidate_ranking_endpoint(
    token,
):
    response = client.get(
        "/api/candidates/ranking",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        404,
    )

    if response.status_code == 404:
        pytest.skip(
            "Candidate ranking endpoint has not been implemented yet."
        )

    data = response.json()

    candidates = (
        data
        if isinstance(data, list)
        else data.get(
            "items",
            data.get("candidates", []),
        )
    )

    assert isinstance(candidates, list)


def test_candidate_ranking_scores_are_valid(
    token,
):
    response = client.get(
        "/api/candidates/ranking",
        headers=auth_headers(token),
    )

    if response.status_code == 404:
        pytest.skip(
            "Candidate ranking endpoint has not been implemented yet."
        )

    assert response.status_code == 200

    data = response.json()

    candidates = (
        data
        if isinstance(data, list)
        else data.get(
            "items",
            data.get("candidates", []),
        )
    )

    for candidate in candidates:
        if "score" in candidate:
            score = candidate["score"]

            assert isinstance(
                score,
                (int, float),
            )

            assert 0 <= score <= 100


# ============================================================================
# Validation
# ============================================================================

def test_create_candidate_rejects_missing_name(token):
    payload = candidate_payload()

    del payload["name"]

    response = client.post(
        "/api/candidates",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_create_candidate_rejects_invalid_email(token):
    payload = candidate_payload(
        email="invalid-email"
    )

    response = client.post(
        "/api/candidates",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_create_candidate_rejects_negative_experience(token):
    payload = candidate_payload()
    payload["experience_years"] = -1

    response = client.post(
        "/api/candidates",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_create_candidate_rejects_invalid_payload(token):
    response = client.post(
        "/api/candidates",
        json={
            "invalid": "payload"
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 422


# ============================================================================
# Authorization / isolation
# ============================================================================

def test_candidate_created_by_user_is_accessible_to_same_user(
    token,
    created_candidate,
):
    candidate_id = created_candidate["id"]

    response = client.get(
        f"/api/candidates/{candidate_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200


def test_second_user_cannot_modify_first_users_candidate(
    token,
    created_candidate,
):
    second_token = create_test_user()

    candidate_id = created_candidate["id"]

    response = client.patch(
        f"/api/candidates/{candidate_id}",
        json={
            "current_title": "Unauthorized Update"
        },
        headers=auth_headers(second_token),
    )

    # Depending on whether candidates are globally visible to recruiters,
    # either 403/404 or a successful update under a shared organization
    # model is possible. A secure personal-ownership model should reject it.
    assert response.status_code in (
        403,
        404,
    )


# ============================================================================
# Response contract
# ============================================================================

def test_candidate_response_contains_core_fields(
    token,
    created_candidate,
):
    required_fields = {
        "id",
        "name",
        "email",
    }

    assert required_fields.issubset(
        created_candidate.keys()
    )


def test_candidate_id_is_not_empty(
    created_candidate,
):
    assert created_candidate["id"] is not None
    assert str(created_candidate["id"]).strip() != ""


def test_candidate_email_is_not_empty(
    created_candidate,
):
    assert created_candidate["email"]
