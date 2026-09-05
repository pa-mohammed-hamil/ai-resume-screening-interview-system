# Project scaffold file
```python
"""
Integration tests for the Interview API.

Target modules:
    backend/app/api/interviews.py
    backend/app/services/interview_service.py
    backend/app/models/interview.py
    backend/app/schemas/interview.py
    interview_engine/

Expected endpoints:
    GET    /api/interviews
    POST   /api/interviews
    GET    /api/interviews/{interview_id}
    PATCH  /api/interviews/{interview_id}
    DELETE /api/interviews/{interview_id}

    POST   /api/interviews/{interview_id}/start
    GET    /api/interviews/{interview_id}/questions
    POST   /api/interviews/{interview_id}/answers
    POST   /api/interviews/{interview_id}/complete
    GET    /api/interviews/{interview_id}/report

Run:
    pytest tests/integration/test_interview_api.py -v
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

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
    return (
        f"interview-test-{uuid.uuid4().hex[:10]}"
        "@example.com"
    )


def create_test_user() -> str:
    """Create a recruiter account and return its JWT."""

    email = unique_email()
    password = "StrongPassword123!"

    register_response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Interview API Tester",
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

    return login_response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}"
    }


def candidate_payload():
    return {
        "name": "Interview Candidate",
        "email": unique_email(),
        "phone": "+1 555 111 2222",
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


def create_candidate(token: str) -> dict:
    response = client.post(
        "/api/candidates",
        json=candidate_payload(),
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 201)

    return response.json()


def create_job(token: str) -> dict:
    """
    Create a minimal job for interview relationship tests.

    If the actual jobs API uses different field names, adjust this helper
    without changing the interview assertions.
    """

    payload = {
        "title": "Backend Developer",
        "description": (
            "Backend developer responsible for APIs, "
            "databases, testing, and cloud services."
        ),
        "requirements": [
            "Python",
            "FastAPI",
            "PostgreSQL",
        ],
        "experience_required": 3,
    }

    response = client.post(
        "/api/jobs",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 201)

    return response.json()


def interview_payload(
    candidate_id,
    job_id=None,
):
    payload = {
        "candidate_id": candidate_id,
        "type": "technical",
        "difficulty": "medium",
        "duration_minutes": 30,
    }

    if job_id is not None:
        payload["job_id"] = job_id

    return payload


def create_interview(
    token: str,
    candidate_id=None,
    job_id=None,
) -> dict:
    if candidate_id is None:
        candidate = create_candidate(token)
        candidate_id = candidate["id"]

    response = client.post(
        "/api/interviews",
        json=interview_payload(
            candidate_id=candidate_id,
            job_id=job_id,
        ),
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 201)

    return response.json()


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def token():
    return create_test_user()


@pytest.fixture
def candidate(token):
    return create_candidate(token)


@pytest.fixture
def job(token):
    return create_job(token)


@pytest.fixture
def interview(token, candidate):
    return create_interview(
        token,
        candidate_id=candidate["id"],
    )


# ============================================================================
# Interview creation
# ============================================================================

def test_create_interview(
    token,
    candidate,
):
    response = client.post(
        "/api/interviews",
        json=interview_payload(
            candidate_id=candidate["id"],
        ),
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert "id" in data
    assert data["candidate_id"] == candidate["id"]


def test_create_interview_with_job(
    token,
    candidate,
    job,
):
    response = client.post(
        "/api/interviews",
        json=interview_payload(
            candidate_id=candidate["id"],
            job_id=job["id"],
        ),
        headers=auth_headers(token),
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert data["candidate_id"] == candidate["id"]

    if "job_id" in data:
        assert data["job_id"] == job["id"]


def test_create_interview_requires_authentication(
    candidate,
):
    response = client.post(
        "/api/interviews",
        json=interview_payload(
            candidate_id=candidate["id"],
        ),
    )

    assert response.status_code == 401


def test_create_interview_requires_candidate_id(
    token,
):
    payload = interview_payload(
        candidate_id=str(uuid.uuid4())
    )

    del payload["candidate_id"]

    response = client.post(
        "/api/interviews",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_create_interview_rejects_unknown_candidate(
    token,
):
    response = client.post(
        "/api/interviews",
        json=interview_payload(
            candidate_id=str(uuid.uuid4()),
        ),
        headers=auth_headers(token),
    )

    assert response.status_code in (
        404,
        422,
    )


# ============================================================================
# Interview retrieval
# ============================================================================

def test_get_interview(
    token,
    interview,
):
    interview_id = interview["id"]

    response = client.get(
        f"/api/interviews/{interview_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == interview_id


def test_get_nonexistent_interview(token):
    interview_id = str(uuid.uuid4())

    response = client.get(
        f"/api/interviews/{interview_id}",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        404,
        422,
    )


def test_get_interview_requires_authentication(
    interview,
):
    response = client.get(
        f"/api/interviews/{interview['id']}"
    )

    assert response.status_code == 401


# ============================================================================
# Interview listing
# ============================================================================

def test_list_interviews(token):
    response = client.get(
        "/api/interviews",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    if isinstance(data, list):
        interviews = data
    else:
        interviews = data.get(
            "items",
            data.get("interviews", []),
        )

    assert isinstance(interviews, list)


def test_created_interview_appears_in_list(
    token,
    interview,
):
    response = client.get(
        "/api/interviews",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    interviews = (
        data
        if isinstance(data, list)
        else data.get(
            "items",
            data.get("interviews", []),
        )
    )

    ids = {
        item.get("id")
        for item in interviews
    }

    assert interview["id"] in ids


def test_list_interviews_requires_authentication():
    response = client.get(
        "/api/interviews"
    )

    assert response.status_code == 401


# ============================================================================
# Interview setup
# ============================================================================

def test_interview_setup_fields_are_valid(
    interview,
):
    if "type" in interview:
        assert interview["type"] in (
            "technical",
            "behavioral",
            "mixed",
            "screening",
        )

    if "difficulty" in interview:
        assert interview["difficulty"] in (
            "easy",
            "medium",
            "hard",
        )

    if "duration_minutes" in interview:
        assert interview["duration_minutes"] > 0


def test_update_interview_setup(
    token,
    interview,
):
    interview_id = interview["id"]

    response = client.patch(
        f"/api/interviews/{interview_id}",
        json={
            "difficulty": "hard",
            "duration_minutes": 45,
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    if "difficulty" in data:
        assert data["difficulty"] == "hard"

    if "duration_minutes" in data:
        assert data["duration_minutes"] == 45


# ============================================================================
# Start interview
# ============================================================================

def test_start_interview(
    token,
    interview,
):
    interview_id = interview["id"]

    response = client.post(
        f"/api/interviews/{interview_id}/start",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        201,
    )

    data = response.json()

    if "status" in data:
        assert data["status"] in (
            "started",
            "in_progress",
            "active",
        )


def test_start_interview_returns_session_information(
    token,
    interview,
):
    response = client.post(
        f"/api/interviews/{interview['id']}/start",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        201,
    )

    data = response.json()

    # At least one useful session identifier or question payload
    # should normally be returned.
    assert any(
        key in data
        for key in (
            "session_id",
            "question",
            "questions",
            "id",
            "status",
        )
    )


def test_start_nonexistent_interview(token):
    response = client.post(
        f"/api/interviews/{uuid.uuid4()}/start",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        404,
        422,
    )


def test_start_interview_requires_authentication(
    interview,
):
    response = client.post(
        f"/api/interviews/{interview['id']}/start"
    )

    assert response.status_code == 401


# ============================================================================
# Question generation
# ============================================================================

def test_get_interview_questions(
    token,
    interview,
):
    response = client.get(
        f"/api/interviews/{interview['id']}/questions",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        404,
    )

    if response.status_code == 404:
        pytest.skip(
            "Interview questions endpoint is not implemented."
        )

    data = response.json()

    questions = (
        data
        if isinstance(data, list)
        else data.get(
            "questions",
            data.get("items", []),
        )
    )

    assert isinstance(questions, list)


def test_interview_questions_have_content(
    token,
    interview,
):
    response = client.get(
        f"/api/interviews/{interview['id']}/questions",
        headers=auth_headers(token),
    )

    if response.status_code == 404:
        pytest.skip(
            "Interview questions endpoint is not implemented."
        )

    assert response.status_code == 200

    data = response.json()

    questions = (
        data
        if isinstance(data, list)
        else data.get(
            "questions",
            data.get("items", []),
        )
    )

    for question in questions:
        if isinstance(question, str):
            assert question.strip()
        else:
            assert any(
                key in question
                for key in (
                    "question",
                    "text",
                    "content",
                )
            )


# ============================================================================
# Answer submission
# ============================================================================

def test_submit_interview_answer(
    token,
    interview,
):
    interview_id = interview["id"]

    start_response = client.post(
        f"/api/interviews/{interview_id}/start",
        headers=auth_headers(token),
    )

    if start_response.status_code not in (
        200,
        201,
    ):
        pytest.skip(
            "Interview start endpoint is unavailable."
        )

    start_data = start_response.json()

    question_id = (
        start_data.get("question_id")
        or start_data.get("current_question_id")
    )

    if not question_id:
        questions_response = client.get(
            f"/api/interviews/{interview_id}/questions",
            headers=auth_headers(token),
        )

        if questions_response.status_code != 200:
            pytest.skip(
                "No interview question is available."
            )

        questions = questions_response.json()

        if isinstance(questions, dict):
            questions = questions.get(
                "questions",
                questions.get("items", []),
            )

        if not questions:
            pytest.skip(
                "Interview has no generated questions."
            )

        first_question = questions[0]

        if isinstance(first_question, dict):
            question_id = (
                first_question.get("id")
                or first_question.get("question_id")
            )

    if not question_id:
        pytest.skip(
            "Interview API does not expose a question identifier."
        )

    response = client.post(
        f"/api/interviews/{interview_id}/answers",
        json={
            "question_id": question_id,
            "answer": (
                "I would first understand the requirements, "
                "design the API, implement validation and "
                "tests, and then monitor the deployment."
            ),
        },
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        201,
        202,
    )


def test_submit_empty_answer_is_rejected(
    token,
    interview,
):
    response = client.post(
        f"/api/interviews/{interview['id']}/answers",
        json={
            "question_id": str(uuid.uuid4()),
            "answer": "",
        },
        headers=auth_headers(token),
    )

    assert response.status_code in (
        400,
        404,
        422,
    )


def test_submit_answer_requires_authentication(
    interview,
):
    response = client.post(
        f"/api/interviews/{interview['id']}/answers",
        json={
            "question_id": str(uuid.uuid4()),
            "answer": "Test answer",
        },
    )

    assert response.status_code == 401


# ============================================================================
# Interview completion
# ============================================================================

def test_complete_interview(
    token,
    interview,
):
    interview_id = interview["id"]

    start_response = client.post(
        f"/api/interviews/{interview_id}/start",
        headers=auth_headers(token),
    )

    # Some implementations allow completion directly from scheduled state;
    # others require a started session.
    if start_response.status_code not in (
        200,
        201,
    ):
        pytest.skip(
            "Interview could not be started."
        )

    response = client.post(
        f"/api/interviews/{interview_id}/complete",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        201,
        202,
    )

    data = response.json()

    if "status" in data:
        assert data["status"] in (
            "completed",
            "complete",
            "finished",
        )


def test_complete_nonexistent_interview(token):
    response = client.post(
        f"/api/interviews/{uuid.uuid4()}/complete",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        404,
        422,
    )


def test_complete_requires_authentication(
    interview,
):
    response = client.post(
        f"/api/interviews/{interview['id']}/complete"
    )

    assert response.status_code == 401


# ============================================================================
# Interview report
# ============================================================================

def test_get_interview_report(
    token,
    interview,
):
    interview_id = interview["id"]

    response = client.get(
        f"/api/interviews/{interview_id}/report",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        404,
        409,
    )

    if response.status_code != 200:
        pytest.skip(
            "Interview report is not available before completion."
        )

    data = response.json()

    assert isinstance(data, dict)


def test_completed_interview_has_report(
    token,
    interview,
):
    interview_id = interview["id"]

    start_response = client.post(
        f"/api/interviews/{interview_id}/start",
        headers=auth_headers(token),
    )

    if start_response.status_code not in (
        200,
        201,
    ):
        pytest.skip(
            "Interview start endpoint is unavailable."
        )

    complete_response = client.post(
        f"/api/interviews/{interview_id}/complete",
        headers=auth_headers(token),
    )

    if complete_response.status_code not in (
        200,
        201,
        202,
    ):
        pytest.skip(
            "Interview cannot be completed without answers."
        )

    report_response = client.get(
        f"/api/interviews/{interview_id}/report",
        headers=auth_headers(token),
    )

    assert report_response.status_code in (
        200,
        202,
    )


# ============================================================================
# Evaluation / scorecard
# ============================================================================

def test_interview_report_scores_are_valid(
    token,
    interview,
):
    response = client.get(
        f"/api/interviews/{interview['id']}/report",
        headers=auth_headers(token),
    )

    if response.status_code != 200:
        pytest.skip(
            "Interview report is not currently available."
        )

    data = response.json()

    possible_score_fields = (
        "score",
        "overall_score",
        "technical_score",
        "communication_score",
        "confidence_score",
    )

    for field in possible_score_fields:
        if field not in data:
            continue

        value = data[field]

        if value is None:
            continue

        assert isinstance(
            value,
            (int, float),
        )

        assert 0 <= value <= 100


# ============================================================================
# Delete
# ============================================================================

def test_delete_interview(
    token,
    interview,
):
    interview_id = interview["id"]

    response = client.delete(
        f"/api/interviews/{interview_id}",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        204,
    )

    get_response = client.get(
        f"/api/interviews/{interview_id}",
        headers=auth_headers(token),
    )

    assert get_response.status_code == 404


def test_delete_nonexistent_interview(token):
    response = client.delete(
        f"/api/interviews/{uuid.uuid4()}",
        headers=auth_headers(token),
    )

    assert response.status_code in (
        404,
        422,
    )


# ============================================================================
# Validation
# ============================================================================

@pytest.mark.parametrize(
    "interview_type",
    [
        "technical",
        "behavioral",
        "mixed",
        "screening",
    ],
)
def test_supported_interview_types(
    token,
    candidate,
    interview_type,
):
    payload = interview_payload(
        candidate_id=candidate["id"]
    )

    payload["type"] = interview_type

    response = client.post(
        "/api/interviews",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code in (
        200,
        201,
    )


def test_invalid_interview_type_is_rejected(
    token,
    candidate,
):
    payload = interview_payload(
        candidate_id=candidate["id"]
    )

    payload["type"] = "invalid-interview-type"

    response = client.post(
        "/api/interviews",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code in (
        400,
        422,
    )


def test_negative_duration_is_rejected(
    token,
    candidate,
):
    payload = interview_payload(
        candidate_id=candidate["id"]
    )

    payload["duration_minutes"] = -10

    response = client.post(
        "/api/interviews",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_zero_duration_is_rejected(
    token,
    candidate,
):
    payload = interview_payload(
        candidate_id=candidate["id"]
    )

    payload["duration_minutes"] = 0

    response = client.post(
        "/api/interviews",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code == 422


# ============================================================================
# Authorization / isolation
# ============================================================================

def test_second_user_cannot_access_private_interview(
    token,
    interview,
):
    second_token = create_test_user()

    response = client.get(
        f"/api/interviews/{interview['id']}",
        headers=auth_headers(second_token),
    )

    assert response.status_code in (
        403,
        404,
    )


def test_second_user_cannot_modify_private_interview(
    token,
    interview,
):
    second_token = create_test_user()

    response = client.patch(
        f"/api/interviews/{interview['id']}",
        json={
            "difficulty": "hard"
        },
        headers=auth_headers(second_token),
    )

    assert response.status_code in (
        403,
        404,
    )


# ============================================================================
# Interview state machine
# ============================================================================

def test_interview_cannot_be_completed_twice(
    token,
    interview,
):
    interview_id = interview["id"]

    start_response = client.post(
        f"/api/interviews/{interview_id}/start",
        headers=auth_headers(token),
    )

    if start_response.status_code not in (
        200,
        201,
    ):
        pytest.skip(
            "Interview cannot be started."
        )

    first_complete = client.post(
        f"/api/interviews/{interview_id}/complete",
        headers=auth_headers(token),
    )

    if first_complete.status_code not in (
        200,
        201,
        202,
    ):
        pytest.skip(
            "Interview requires answers before completion."
        )

    second_complete = client.post(
        f"/api/interviews/{interview_id}/complete",
        headers=auth_headers(token),
    )

    assert second_complete.status_code in (
        400,
        409,
        422,
    )


def test_interview_state_is_consistent_after_start(
    token,
    interview,
):
    interview_id = interview["id"]

    response = client.post(
        f"/api/interviews/{interview_id}/start",
        headers=auth_headers(token),
    )

    if response.status_code not in (
        200,
        201,
    ):
        pytest.skip(
            "Interview start endpoint is unavailable."
        )

    get_response = client.get(
        f"/api/interviews/{interview_id}",
        headers=auth_headers(token),
    )

    assert get_response.status_code == 200

    data = get_response.json()

    if "status" in data:
        assert data["status"] in (
            "started",
            "in_progress",
            "active",
        )


# ============================================================================
# Response contract
# ============================================================================

def test_interview_response_contains_core_fields(
    interview,
):
    assert "id" in interview
    assert "candidate_id" in interview


def test_interview_id_is_not_empty(
    interview,
):
    assert interview["id"] is not None
    assert str(interview["id"]).strip() != ""


def test_interview_candidate_relationship_is_valid(
    interview,
):
    assert interview["candidate_id"] is not None


# ============================================================================
# Date/time behavior
# ============================================================================

def test_interview_timestamps_are_serializable(
    interview,
):
    for field in (
        "created_at",
        "updated_at",
        "started_at",
        "completed_at",
    ):
        if field not in interview:
            continue

        value = interview[field]

        if value is None:
            continue

        assert isinstance(value, str)

        # Accept ISO-8601 timestamps.
        datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
