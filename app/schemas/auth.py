# backend/app/schemas/auth.py

from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ======================================================================
# Registration
# ======================================================================

class RegisterRequest(BaseModel):
    """Schema used when creating a new user account."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    phone: Optional[str] = Field(
        default=None,
        max_length=30,
    )

    company_name: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    job_title: Optional[str] = Field(
        default=None,
        max_length=150,
    )


# ======================================================================
# Login
# ======================================================================

class LoginRequest(BaseModel):
    """Schema used for user login."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr

    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
    )


# ======================================================================
# Token
# ======================================================================

class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str

    refresh_token: Optional[str] = None

    token_type: str = "bearer"

    expires_in: Optional[int] = None


# ======================================================================
# Refresh Token
# ======================================================================

class RefreshTokenRequest(BaseModel):
    """Schema used to refresh an access token."""

    refresh_token: str = Field(
        ...,
        min_length=1,
    )


# ======================================================================
# Forgot Password
# ======================================================================

class ForgotPasswordRequest(BaseModel):
    """Schema used to request a password reset."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr


# ======================================================================
# Reset Password
# ======================================================================

class ResetPasswordRequest(BaseModel):
    """Schema used to reset a user's password."""

    token: str = Field(
        ...,
        min_length=1,
    )

    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )


# ======================================================================
# Change Password
# ======================================================================

class ChangePasswordRequest(BaseModel):
    """Schema used by authenticated users to change their password."""

    current_password: str = Field(
        ...,
        min_length=1,
        max_length=128,
    )

    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )


# ======================================================================
# Email Verification
# ======================================================================

class VerifyEmailRequest(BaseModel):
    """Schema used to verify a user's email address."""

    token: str = Field(
        ...,
        min_length=1,
    )


# ======================================================================
# Resend Verification
# ======================================================================

class ResendVerificationRequest(BaseModel):
    """Schema used to resend an email verification link."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr


# ======================================================================
# Authenticated User
# ======================================================================

class AuthUserResponse(BaseModel):
    """Minimal authenticated-user response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool


# ======================================================================
# Login Response
# ======================================================================

class LoginResponse(BaseModel):
    """Complete response returned after successful login."""

    access_token: str

    refresh_token: Optional[str] = None

    token_type: str = "bearer"

    expires_in: Optional[int] = None

    user: AuthUserResponse


# ======================================================================
# Generic Authentication Response
# ======================================================================

class AuthMessageResponse(BaseModel):
    """Generic response for authentication operations."""

    message: str

    success: bool = True