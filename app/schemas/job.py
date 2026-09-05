# backend/app/schemas/job.py

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ======================================================================
# Base Job Schema
# ======================================================================

class JobBase(BaseModel):
    """Common job fields."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    company_name: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    department: Optional[str] = Field(
        default=None,
        max_length=150,
    )

    location: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    employment_type: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    work_mode: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    experience_level: Optional[str] = Field(
        default=None,
        max_length=100,
    )


# ======================================================================
# Create Job
# ======================================================================

class JobCreate(JobBase):
    """Schema used to create a new job."""

    description: str = Field(
        ...,
        min_length=10,
    )

    requirements: Optional[list[Any]] = None

    responsibilities: Optional[list[Any]] = None

    qualifications: Optional[list[Any]] = None

    preferred_qualifications: Optional[list[Any]] = None

    benefits: Optional[list[Any]] = None

    required_skills: Optional[list[Any]] = None

    preferred_skills: Optional[list[Any]] = None

    technical_skills: Optional[list[Any]] = None

    soft_skills: Optional[list[Any]] = None

    salary_min: Optional[float] = Field(
        default=None,
        ge=0,
    )

    salary_max: Optional[float] = Field(
        default=None,
        ge=0,
    )

    salary_currency: Optional[str] = Field(
        default="USD",
        max_length=10,
    )

    application_url: Optional[str] = None

    application_deadline: Optional[datetime] = None

    openings: int = Field(
        default=1,
        ge=1,
    )


# ======================================================================
# Update Job
# ======================================================================

class JobUpdate(BaseModel):
    """Schema used to update an existing job."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    company_name: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    department: Optional[str] = Field(
        default=None,
        max_length=150,
    )

    location: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    employment_type: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    work_mode: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    experience_level: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    description: Optional[str] = Field(
        default=None,
        min_length=10,
    )

    requirements: Optional[list[Any]] = None

    responsibilities: Optional[list[Any]] = None

    qualifications: Optional[list[Any]] = None

    preferred_qualifications: Optional[list[Any]] = None

    benefits: Optional[list[Any]] = None

    required_skills: Optional[list[Any]] = None

    preferred_skills: Optional[list[Any]] = None

    technical_skills: Optional[list[Any]] = None

    soft_skills: Optional[list[Any]] = None

    salary_min: Optional[float] = Field(
        default=None,
        ge=0,
    )

    salary_max: Optional[float] = Field(
        default=None,
        ge=0,
    )

    salary_currency: Optional[str] = Field(
        default=None,
        max_length=10,
    )

    application_url: Optional[str] = None

    application_deadline: Optional[datetime] = None

    openings: Optional[int] = Field(
        default=None,
        ge=1,
    )


# ======================================================================
# Job Status Update
# ======================================================================

class JobStatusUpdate(BaseModel):
    """Schema used to change job status."""

    status: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    is_active: Optional[bool] = None


# ======================================================================
# Job Scoring Configuration
# ======================================================================

class JobScoringConfig(BaseModel):
    """Scoring weights used during candidate matching."""

    skill_weight: float = Field(
        default=0.40,
        ge=0,
        le=1,
    )

    experience_weight: float = Field(
        default=0.25,
        ge=0,
        le=1,
    )

    education_weight: float = Field(
        default=0.15,
        ge=0,
        le=1,
    )

    keyword_weight: float = Field(
        default=0.20,
        ge=0,
        le=1,
    )


# ======================================================================
# Job Analysis
# ======================================================================

class JobAnalysisResponse(BaseModel):
    """AI-generated job description analysis."""

    job_id: int

    jd_analysis: Optional[dict[str, Any]] = None

    requirements: list[Any] = Field(
        default_factory=list,
    )

    responsibilities: list[Any] = Field(
        default_factory=list,
    )

    required_skills: list[Any] = Field(
        default_factory=list,
    )

    preferred_skills: list[Any] = Field(
        default_factory=list,
    )

    technical_skills: list[Any] = Field(
        default_factory=list,
    )

    soft_skills: list[Any] = Field(
        default_factory=list,
    )

    keywords: list[Any] = Field(
        default_factory=list,
    )

    must_have_keywords: list[Any] = Field(
        default_factory=list,
    )

    nice_to_have_keywords: list[Any] = Field(
        default_factory=list,
    )


# ======================================================================
# Job Response
# ======================================================================

class JobResponse(JobBase):
    """Complete job API response."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    user_id: int

    description: str

    requirements: Optional[list[Any]] = None

    responsibilities: Optional[list[Any]] = None

    qualifications: Optional[list[Any]] = None

    preferred_qualifications: Optional[list[Any]] = None

    benefits: Optional[list[Any]] = None

    required_skills: Optional[list[Any]] = None

    preferred_skills: Optional[list[Any]] = None

    technical_skills: Optional[list[Any]] = None

    soft_skills: Optional[list[Any]] = None

    salary_min: Optional[float] = None

    salary_max: Optional[float] = None

    salary_currency: Optional[str] = None

    jd_analysis: Optional[dict[str, Any]] = None

    keywords: Optional[list[Any]] = None

    must_have_keywords: Optional[list[Any]] = None

    nice_to_have_keywords: Optional[list[Any]] = None

    skill_weight: float

    experience_weight: float

    education_weight: float

    keyword_weight: float

    status: str

    is_active: bool

    is_analyzed: bool

    application_url: Optional[str] = None

    application_deadline: Optional[datetime] = None

    openings: int

    created_at: datetime

    updated_at: datetime

    published_at: Optional[datetime] = None

    analyzed_at: Optional[datetime] = None


# ======================================================================
# Job List Item
# ======================================================================

class JobListItem(BaseModel):
    """Lightweight job representation for dashboard/list pages."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    title: str

    company_name: Optional[str] = None

    location: Optional[str] = None

    employment_type: Optional[str] = None

    work_mode: Optional[str] = None

    experience_level: Optional[str] = None

    status: str

    is_active: bool

    is_analyzed: bool

    openings: int

    created_at: datetime

    published_at: Optional[datetime] = None


# ======================================================================
# Job List Response
# ======================================================================

class JobListResponse(BaseModel):
    """Paginated job list response."""

    items: list[JobListItem]

    total: int

    page: int

    page_size: int

    total_pages: int


# ======================================================================
# Job Summary
# ======================================================================

class JobSummary(BaseModel):
    """Compact job information used by matching/ranking APIs."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    title: str

    company_name: Optional[str] = None

    required_skills: list[Any] = Field(
        default_factory=list,
    )

    preferred_skills: list[Any] = Field(
        default_factory=list,
    )

    experience_level: Optional[str] = None

    location: Optional[str] = None

    status: str