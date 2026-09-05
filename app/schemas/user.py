# backend/app/schemas/user.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ======================================================================
# Base User Schema
# ======================================================================

class UserBase(BaseModel):
    """Common user fields."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    email: EmailStr

    first_name: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    last_name: Optional[str] = Field(
        default=None,
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
# Create User
# ======================================================================

class UserCreate(UserBase):
    """Schema used to create a user."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )

    role: str = Field(
        default="recruiter",
        max_length=50,
    )


# ======================================================================
# Update User
# ======================================================================

class UserUpdate(BaseModel):
    """Schema used to update a user's profile."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    first_name: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    last_name: Optional[str] = Field(
        default=None,
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

    avatar_url: Optional[str] = None


# ======================================================================
# Admin User Update
# ======================================================================

class AdminUserUpdate(UserUpdate):
    """Schema for administrator-level user updates."""

    role: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    is_active: Optional[bool] = None

    is_verified: Optional[bool] = None

    is_admin: Optional[bool] = None


# ======================================================================
# User Response
# ======================================================================

class UserResponse(UserBase):
    """Public API representation of a user."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    avatar_url: Optional[str] = None

    role: str

    is_active: bool

    is_verified: bool

    is_admin: bool

    last_login_at: Optional[datetime] = None

    created_at: datetime

    updated_at: datetime


# ======================================================================
# User Summary
# ======================================================================

class UserSummary(BaseModel):
    """Lightweight user representation."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    email: EmailStr

    first_name: Optional[str] = None

    last_name: Optional[str] = None

    role: str

    is_active: bool


# ======================================================================
# Profile Response
# ======================================================================

class UserProfileResponse(UserResponse):
    """Detailed profile response."""

    full_name: Optional[str] = None

    avatar_url: Optional[str] = None


# ======================================================================
# User List Response
# ======================================================================

class UserListResponse(BaseModel):
    """Paginated user list response."""

    items: list[UserResponse]

    total: int

    page: int

    page_size: int

    total_pages: int


# ======================================================================
# User Status Update
# ======================================================================

class UserStatusUpdate(BaseModel):
    """Schema for changing account status."""

    is_active: bool


# ======================================================================
# User Role Update
# ======================================================================

class UserRoleUpdate(BaseModel):
    """Schema for changing a user's role."""

    role: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )