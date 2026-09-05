# Project scaffold file
```python
"""
tests/unit/test_auth.py

Unit tests for authentication and security functionality.

Covers:
    - Password hashing
    - Password verification
    - JWT creation
    - JWT decoding
    - Invalid/expired tokens
    - Authentication service behavior
    - User credential validation

Run:
    pytest tests/unit/test_auth.py -v
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest


# ============================================================================
# Imports
# ============================================================================

try:
    from app.core.security import (
        create_access_token,
        decode_access_token,
        get_password_hash,
        verify_password,
    )
except ImportError:
    from backend.app.core.security import (
        create_access_token,
        decode_access_token,
        get_password_hash,
        verify_password,
    )


# ============================================================================
# Password hashing
# ============================================================================

def test_password_hash_is_not_plaintext():
    password = "StrongPassword123!"

    hashed = get_password_hash(password)

    assert hashed != password


def test_password_hash_is_not_empty():
    hashed = get_password_hash(
        "StrongPassword123!"
    )

    assert hashed
    assert len(hashed) > 20


def test_password_verification_succeeds():
    password = "StrongPassword123!"

    hashed = get_password_hash(password)

    assert verify_password(
        password,
        hashed,
    ) is True


def test_password_verification_fails_for_wrong_password():
    password = "StrongPassword123!"
    wrong_password = "WrongPassword123!"

    hashed = get_password_hash(password)

    assert verify_password(
        wrong_password,
        hashed,
    ) is False


def test_password_hashes_are_different_for_same_password():
    password = "StrongPassword123!"

    first_hash = get_password_hash(password)
    second_hash = get_password_hash(password)

    assert first_hash != second_hash


def test_both_hashes_verify_same_password():
    password = "StrongPassword123!"

    first_hash = get_password_hash(password)
    second_hash = get_password_hash(password)

    assert verify_password(
        password,
        first_hash,
    )

    assert verify_password(
        password,
        second_hash,
    )


@pytest.mark.parametrize(
    "password",
    [
        "password",
        "Password123",
        "VeryStrongPassword!2026",
        "pässwörd",
        "密码Password123!",
        "a" * 32,
    ],
)
def test_password_hashing_supports_valid_passwords(
    password,
):
    hashed = get_password_hash(password)

    assert hashed != password

    assert verify_password(
        password,
        hashed,
    )


def test_wrong_hash_does_not_verify():
    password = "StrongPassword123!"

    assert verify_password(
        password,
        "invalid-hash",
    ) is False


# ============================================================================
# JWT creation
# ============================================================================

def test_create_access_token():
    subject = str(uuid.uuid4())

    token = create_access_token(
        data={
            "sub": subject
        }
    )

    assert token
    assert isinstance(token, str)


def test_access_token_is_not_empty():
    token = create_access_token(
        data={
            "sub": "user-123"
        }
    )

    assert token.strip() != ""


def test_access_token_contains_expected_claim():
    subject = "user-123"

    token = create_access_token(
        data={
            "sub": subject
        }
    )

    payload = decode_access_token(token)

    assert payload["sub"] == subject


def test_access_token_supports_multiple_claims():
    payload = {
        "sub": "user-123",
        "role": "recruiter",
        "email": "recruiter@example.com",
    }

    token = create_access_token(
        data=payload
    )

    decoded = decode_access_token(token)

    assert decoded["sub"] == "user-123"
    assert decoded["role"] == "recruiter"
    assert decoded["email"] == (
        "recruiter@example.com"
    )


# ============================================================================
# JWT decoding
# ============================================================================

def test_decode_access_token():
    subject = "user-123"

    token = create_access_token(
        data={
            "sub": subject
        }
    )

    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == subject


def test_decode_invalid_token_raises_error():
    with pytest.raises(Exception):
        decode_access_token(
            "this-is-not-a-valid-jwt"
        )


def test_decode_empty_token_raises_error():
    with pytest.raises(Exception):
        decode_access_token("")


def test_decode_modified_token_fails():
    token = create_access_token(
        data={
            "sub": "user-123"
        }
    )

    parts = token.split(".")

    assert len(parts) == 3

    # Modify the signature portion.
    parts[-1] = "invalid-signature"

    modified_token = ".".join(parts)

    with pytest.raises(Exception):
        decode_access_token(modified_token)


# ============================================================================
# JWT expiration
# ============================================================================

def test_expired_token_is_rejected():
    expired_time = (
        datetime.now(timezone.utc)
        - timedelta(minutes=5)
    )

    token = create_access_token(
        data={
            "sub": "user-123",
            "exp": expired_time,
        }
    )

    with pytest.raises(Exception):
        decode_access_token(token)


def test_future_token_is_accepted():
    expiration = (
        datetime.now(timezone.utc)
        + timedelta(minutes=30)
    )

    token = create_access_token(
        data={
            "sub": "user-123",
            "exp": expiration,
        }
    )

    payload = decode_access_token(token)

    assert payload["sub"] == "user-123"


# ============================================================================
# JWT subject validation
# ============================================================================

def test_token_supports_string_subject():
    token = create_access_token(
        data={
            "sub": "abc123"
        }
    )

    payload = decode_access_token(token)

    assert payload["sub"] == "abc123"


def test_token_supports_uuid_subject():
    user_id = str(uuid.uuid4())

    token = create_access_token(
        data={
            "sub": user_id
        }
    )

    payload = decode_access_token(token)

    assert payload["sub"] == user_id


# ============================================================================
# Authentication service
# ============================================================================

try:
    from app.services.auth_service import AuthService
except ImportError:
    try:
        from backend.app.services.auth_service import AuthService
    except ImportError:
        AuthService = None


@pytest.mark.skipif(
    AuthService is None,
    reason="AuthService is not available.",
)
def test_auth_service_can_be_imported():
    assert AuthService is not None


# ============================================================================
# Authentication utility behavior
# ============================================================================

def test_hashing_same_password_remains_verifiable():
    password = (
        "CorrectHorseBatteryStaple!"
    )

    hashed = get_password_hash(password)

    for _ in range(3):
        assert verify_password(
            password,
            hashed,
        )


def test_password_case_sensitivity():
    password = "Password123!"

    hashed = get_password_hash(password)

    assert verify_password(
        "Password123!",
        hashed,
    )

    assert not verify_password(
        "password123!",
        hashed,
    )


def test_password_whitespace_is_significant():
    password = "Password123!"

    hashed = get_password_hash(password)

    assert verify_password(
        password,
        hashed,
    )

    assert not verify_password(
        f" {password}",
        hashed,
    )

    assert not verify_password(
        f"{password} ",
        hashed,
    )


# ============================================================================
# Security regression tests
# ============================================================================

def test_plaintext_password_is_never_equal_to_hash():
    passwords = [
        "password",
        "Password123!",
        "admin123",
        "VerySecurePassword!2026",
    ]

    for password in passwords:
        hashed = get_password_hash(password)

        assert hashed != password


def test_invalid_password_cannot_become_valid():
    password = "CorrectPassword123!"

    hashed = get_password_hash(password)

    invalid_passwords = [
        "correctpassword123!",
        "CorrectPassword123",
        "CorrectPassword124!",
        "",
        " ",
    ]

    for invalid_password in invalid_passwords:
        assert not verify_password(
            invalid_password,
            hashed,
        )


def test_token_contains_three_jwt_sections():
    token = create_access_token(
        data={
            "sub": "user-123"
        }
    )

    assert len(token.split(".")) == 3


# ============================================================================
# Token uniqueness
# ============================================================================

def test_tokens_for_different_users_are_different():
    first_token = create_access_token(
        data={
            "sub": "user-1"
        }
    )

    second_token = create_access_token(
        data={
            "sub": "user-2"
        }
    )

    assert first_token != second_token


def test_token_payload_is_preserved():
    user_id = str(uuid.uuid4())

    token = create_access_token(
        data={
            "sub": user_id,
            "role": "recruiter",
            "permissions": [
                "resume:read",
                "resume:write",
            ],
        }
    )

    payload = decode_access_token(token)

    assert payload["sub"] == user_id
    assert payload["role"] == "recruiter"
    assert payload["permissions"] == [
        "resume:read",
        "resume:write",
    ]


# ============================================================================
# Optional authentication dependency tests
# ============================================================================

try:
    from app.core.dependencies import get_current_user
except ImportError:
    try:
        from backend.app.core.dependencies import (
            get_current_user,
        )
    except ImportError:
        get_current_user = None


@pytest.mark.skipif(
    get_current_user is None,
    reason="Authentication dependency is not available.",
)
def test_current_user_dependency_can_be_imported():
    assert callable(get_current_user)


# ============================================================================
# Edge cases
# ============================================================================

def test_empty_subject_token_behavior():
    """
    Depending on the application's JWT validation rules, an empty subject
    may either be accepted by the low-level token utility or rejected by
    the authentication dependency.

    This test therefore verifies only that token creation/decoding does
    not silently corrupt the supplied value.
    """

    token = create_access_token(
        data={
            "sub": ""
        }
    )

    payload = decode_access_token(token)

    assert payload["sub"] == ""


def test_unicode_subject():
    subject = "用户-123"

    token = create_access_token(
        data={
            "sub": subject
        }
    )

    payload = decode_access_token(token)

    assert payload["sub"] == subject


def test_long_subject():
    subject = "user-" + ("x" * 500)

    token = create_access_token(
        data={
            "sub": subject
        }
    )

    payload = decode_access_token(token)

    assert payload["sub"] == subject
