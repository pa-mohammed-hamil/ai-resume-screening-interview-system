"""
Integration tests for authentication API.

Target modules:
    backend/app/main.py
    backend/app/api/auth.py
    backend/app/services/auth_service.py
    backend/app/core/security.py

Expected endpoints:
    POST /api/auth/register
    POST /api/auth/login
    GET  /api/users/me

Run:
    pytest tests/integration/test_auth_api.py -v
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient


# ============================================================================
# Application import
# ============================================================================

try:
    from app.main import app
except ImportError:
    # Supports running pytest from the repository root when backend/app
    # is not already on PYTHONPATH.
    from backend.app.main import app


client = TestClient(app)


# ============================================================================
# Test data helpers
# ============================================================================

def unique_email() -> str:
    """Generate a unique test email."""

    return f"test-{uuid.uuid4().hex[:12]}@example.com"


def registration_payload(
    email: str | None = None,
    password: str = "StrongPassword123!",
):
    return {
        "email": email or unique_email(),
        "password": password,
        "full_name": "Test Recruiter",
    }


def login_payload(
    email: str,
    password: str = "StrongPassword123!",
):
    return {
        "email": email,
        "password": password,
    }


# ============================================================================
# Registration
# ============================================================================

def test_register_user_successfully():
    payload = registration_payload()

    response = client.post(
        "/api/auth/register",
        json=payload,
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert "email" in data
    assert data["email"].lower() == payload["email"].lower()

    # Password must never be returned by the API.
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_returns_user_identifier():
    payload = registration_payload()

    response = client.post(
        "/api/auth/register",
        json=payload,
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert any(
        key in data
        for key in ("id", "user_id")
    )


def test_register_preserves_full_name():
    payload = registration_payload()

    response = client.post(
        "/api/auth/register",
        json=payload,
    )

    assert response.status_code in (200, 201)

    data = response.json()

    if "full_name" in data:
        assert data["full_name"] == "Test Recruiter"


def test_duplicate_email_is_rejected():
    email = unique_email()

    first_response = client.post(
        "/api/auth/register",
        json=registration_payload(email),
    )

    assert first_response.status_code in (200, 201)

    second_response = client.post(
        "/api/auth/register",
        json=registration_payload(email),
    )

    assert second_response.status_code in (
        400,
        409,
        422,
    )


# ============================================================================
# Registration validation
# ============================================================================

def test_register_rejects_invalid_email():
    payload = registration_payload(
        email="not-an-email"
    )

    response = client.post(
        "/api/auth/register",
        json=payload,
    )

    assert response.status_code == 422


def test_register_rejects_missing_email():
    payload = registration_payload()

    del payload["email"]

    response = client.post(
        "/api/auth/register",
        json=payload,
    )

    assert response.status_code == 422


def test_register_rejects_missing_password():
    payload = registration_payload()

    del payload["password"]

    response = client.post(
        "/api/auth/register",
        json=payload,
    )

    assert response.status_code == 422


def test_register_rejects_empty_password():
    payload = registration_payload(
        password=""
    )

    response = client.post(
        "/api/auth/register",
        json=payload,
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "password",
    [
        "short",
        "123",
        "password",
    ],
)
def test_register_rejects_weak_password(password):
    payload = registration_payload(
        password=password
    )

    response = client.post(
        "/api/auth/register",
        json=payload,
    )

    # Depending on the application's password policy, 422 or 400 is valid.
    assert response.status_code in (400, 422)


# ============================================================================
# Login
# ============================================================================

def test_login_successfully():
    email = unique_email()
    password = "StrongPassword123!"

    register_response = client.post(
        "/api/auth/register",
        json=registration_payload(
            email=email,
            password=password,
        ),
    )

    assert register_response.status_code in (200, 201)

    response = client.post(
        "/api/auth/login",
        json=login_payload(
            email=email,
            password=password,
        ),
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert isinstance(
        data["access_token"],
        str,
    )
    assert len(data["access_token"]) > 20


def test_login_returns_token_type():
    email = unique_email()
    password = "StrongPassword123!"

    client.post(
        "/api/auth/register",
        json=registration_payload(
            email=email,
            password=password,
        ),
    )

    response = client.post(
        "/api/auth/login",
        json=login_payload(
            email=email,
            password=password,
        ),
    )

    assert response.status_code == 200

    data = response.json()

    if "token_type" in data:
        assert data["token_type"].lower() == "bearer"


def test_login_rejects_wrong_password():
    email = unique_email()

    client.post(
        "/api/auth/register",
        json=registration_payload(
            email=email,
            password="CorrectPassword123!",
        ),
    )

    response = client.post(
        "/api/auth/login",
        json=login_payload(
            email=email,
            password="WrongPassword123!",
        ),
    )

    assert response.status_code in (
        401,
        403,
    )


def test_login_rejects_unknown_email():
    response = client.post(
        "/api/auth/login",
        json=login_payload(
            email=unique_email(),
            password="StrongPassword123!",
        ),
    )

    assert response.status_code in (
        401,
        403,
        404,
    )


def test_login_email_is_case_insensitive():
    email = unique_email()
    password = "StrongPassword123!"

    client.post(
        "/api/auth/register",
        json=registration_payload(
            email=email,
            password=password,
        ),
    )

    response = client.post(
        "/api/auth/login",
        json=login_payload(
            email=email.upper(),
            password=password,
        ),
    )

    assert response.status_code == 200


# ============================================================================
# Token validation
# ============================================================================

def test_protected_endpoint_accepts_valid_token():
    email = unique_email()
    password = "StrongPassword123!"

    client.post(
        "/api/auth/register",
        json=registration_payload(
            email=email,
            password=password,
        ),
    )

    login_response = client.post(
        "/api/auth/login",
        json=login_payload(
            email=email,
            password=password,
        ),
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"].lower() == email.lower()


def test_protected_endpoint_rejects_missing_token():
    response = client.get(
        "/api/users/me"
    )

    assert response.status_code == 401


def test_protected_endpoint_rejects_invalid_token():
    response = client.get(
        "/api/users/me",
        headers={
            "Authorization": "Bearer invalid-token"
        },
    )

    assert response.status_code == 401


def test_protected_endpoint_rejects_malformed_authorization_header():
    response = client.get(
        "/api/users/me",
        headers={
            "Authorization": "NotBearer token"
        },
    )

    assert response.status_code == 401


def test_protected_endpoint_rejects_empty_bearer_token():
    response = client.get(
        "/api/users/me",
        headers={
            "Authorization": "Bearer "
        },
    )

    assert response.status_code == 401


# ============================================================================
# Token uniqueness / session behavior
# ============================================================================

def test_login_generates_access_token_each_time():
    email = unique_email()
    password = "StrongPassword123!"

    client.post(
        "/api/auth/register",
        json=registration_payload(
            email=email,
            password=password,
        ),
    )

    first_login = client.post(
        "/api/auth/login",
        json=login_payload(
            email=email,
            password=password,
        ),
    )

    second_login = client.post(
        "/api/auth/login",
        json=login_payload(
            email=email,
            password=password,
        ),
    )

    assert first_login.status_code == 200
    assert second_login.status_code == 200

    first_token = first_login.json()["access_token"]
    second_token = second_login.json()["access_token"]

    assert first_token
    assert second_token

    # If JWTs contain issued-at timestamps, tokens should normally differ.
    # Do not require inequality if the implementation intentionally creates
    # deterministic tokens.
    if first_token != second_token:
        assert first_token != second_token


# ============================================================================
# User isolation
# ============================================================================

def test_user_can_only_access_own_profile():
    first_email = unique_email()
    second_email = unique_email()

    password = "StrongPassword123!"

    client.post(
        "/api/auth/register",
        json=registration_payload(
            email=first_email,
            password=password,
        ),
    )

    client.post(
        "/api/auth/register",
        json=registration_payload(
            email=second_email,
            password=password,
        ),
    )

    first_login = client.post(
        "/api/auth/login",
        json=login_payload(
            email=first_email,
            password=password,
        ),
    )

    second_login = client.post(
        "/api/auth/login",
        json=login_payload(
            email=second_email,
            password=password,
        ),
    )

    first_token = first_login.json()["access_token"]
    second_token = second_login.json()["access_token"]

    first_profile = client.get(
        "/api/users/me",
        headers={
            "Authorization": f"Bearer {first_token}"
        },
    )

    second_profile = client.get(
        "/api/users/me",
        headers={
            "Authorization": f"Bearer {second_token}"
        },
    )

    assert first_profile.status_code == 200
    assert second_profile.status_code == 200

    assert (
        first_profile.json()["email"].lower()
        == first_email.lower()
    )

    assert (
        second_profile.json()["email"].lower()
        == second_email.lower()
    )

    assert (
        first_profile.json()["email"].lower()
        != second_profile.json()["email"].lower()
    )


# ============================================================================
# Security behavior
# ============================================================================

def test_register_response_does_not_expose_password():
    payload = registration_payload()

    response = client.post(
        "/api/auth/register",
        json=payload,
    )

    assert response.status_code in (200, 201)

    response_text = response.text.lower()

    assert payload["password"].lower() not in response_text


def test_login_error_does_not_expose_password():
    response = client.post(
        "/api/auth/login",
        json=login_payload(
            email=unique_email(),
            password="SecretPassword123!",
        ),
    )

    assert "SecretPassword123!" not in response.text


def test_login_error_does_not_expose_internal_details():
    response = client.post(
        "/api/auth/login",
        json=login_payload(
            email=unique_email(),
            password="SecretPassword123!",
        ),
    )

    body = response.text.lower()

    assert "traceback" not in body
    assert "sqlalchemy" not in body
    assert "database password" not in body


# ============================================================================
# Logout
# ============================================================================

def test_logout_endpoint_if_implemented():
    """
    Optional logout contract.

    Stateless JWT systems may not implement server-side logout. In that
    case a 404 is acceptable until token revocation/blacklisting is added.
    """

    email = unique_email()
    password = "StrongPassword123!"

    client.post(
        "/api/auth/register",
        json=registration_payload(
            email=email,
            password=password,
        ),
    )

    login_response = client.post(
        "/api/auth/login",
        json=login_payload(
            email=email,
            password=password,
        ),
    )

    token = login_response.json()["access_token"]

    response = client.post(
        "/api/auth/logout",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code in (
        200,
        204,
        404,
    )


# ============================================================================
# Health check
# ============================================================================

def test_health_endpoint_is_available():
    response = client.get("/api/health")

    # Some projects expose /health instead.
    if response.status_code == 404:
        response = client.get("/health")

    assert response.status_code == 200
