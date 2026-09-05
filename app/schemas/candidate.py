# backend/app/schemas/candidate.py

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ======================================================================
# Base Candidate Schema
# ======================================================================

class CandidateBase(BaseModel):
    """Common candidate fields."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
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

    email: str = Field(
        ...,
        max_length=255,
    )

    phone: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    location: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    current_title: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    current_company: Optional[str] = Field(
        default=None,
        max_length=255,
    )


# ======================================================================
# Create Candidate
# ======================================================================

class CandidateCreate(CandidateBase):
    """Schema used to create a candidate."""

    resume_id: Optional[int] = None

    source: Optional[str] = Field(
        default="manual",
        max_length=100,
    )

    notes: Optional[str] = None

    tags: Optional[list[Any]] = None


# ======================================================================
# Update Candidate
# ======================================================================

class CandidateUpdate(BaseModel):
    """Schema used to update a candidate profile."""

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

    email: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    phone: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    location: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    current_title: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    current_company: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    notes: Optional[str] = None

    tags: Optional[list[Any]] = None


# ======================================================================
# Candidate Status Update
# ======================================================================

class CandidateStatusUpdate(BaseModel):
    """Schema used to update candidate hiring status."""

    status: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    notes: Optional[str] = None


# ======================================================================
# Candidate Skill
# ======================================================================

class CandidateSkill(BaseModel):
    """Individual candidate skill."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=150,
    )

    category: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    proficiency: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    years_of_experience: Optional[float] = Field(
        default=None,
        ge=0,
    )

    confidence: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
    )


# ======================================================================
# Candidate Experience
# ======================================================================

class CandidateExperience(BaseModel):
    """Candidate work experience."""

    job_title: Optional[str] = None

    company: Optional[str] = None

    location: Optional[str] = None

    start_date: Optional[datetime] = None

    end_date: Optional[datetime] = None

    is_current: bool = False

    description: Optional[str] = None

    skills: list[Any] = Field(
        default_factory=list,
    )


# ======================================================================
# Candidate Education
# ======================================================================

class CandidateEducation(BaseModel):
    """Candidate education record."""

    degree: Optional[str] = None

    field_of_study: Optional[str] = None

    institution: Optional[str] = None

    location: Optional[str] = None

    start_date: Optional[datetime] = None

    end_date: Optional[datetime] = None

    grade: Optional[str] = None


# ======================================================================
# Candidate Match Request
# ======================================================================

class CandidateMatchRequest(BaseModel):
    """Request for matching a candidate against a job."""

    candidate_id: int

    job_id: int

    include_explanation: bool = True


# ======================================================================
# Candidate Match Response
# ======================================================================

class CandidateMatchResponse(BaseModel):
    """AI-generated candidate-job matching result."""

    candidate_id: int

    job_id: int

    overall_match_score: float = Field(
        ...,
        ge=0,
        le=100,
    )

    semantic_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    skill_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    experience_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    education_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    keyword_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    matched_skills: list[Any] = Field(
        default_factory=list,
    )

    missing_skills: list[Any] = Field(
        default_factory=list,
    )

    matching_keywords: list[Any] = Field(
        default_factory=list,
    )

    missing_keywords: list[Any] = Field(
        default_factory=list,
    )

    explanation: Optional[str] = None

    recommendations: list[Any] = Field(
        default_factory=list,
    )


# ======================================================================
# Candidate Ranking Item
# ======================================================================

class CandidateRankingItem(BaseModel):
    """Candidate item returned by ranking API."""

    candidate_id: int

    rank: int

    candidate_name: str

    email: Optional[str] = None

    overall_score: float = Field(
        ...,
        ge=0,
        le=100,
    )

    skill_score: Optional[float] = None

    experience_score: Optional[float] = None

    education_score: Optional[float] = None

    semantic_score: Optional[float] = None

    matched_skills: list[Any] = Field(
        default_factory=list,
    )

    missing_skills: list[Any] = Field(
        default_factory=list,
    )

    recommendation: Optional[str] = None


# ======================================================================
# Candidate Ranking Response
# ======================================================================

class CandidateRankingResponse(BaseModel):
    """Complete candidate ranking response."""

    job_id: int

    items: list[CandidateRankingItem] = Field(
        default_factory=list,
    )

    total_candidates: int

    ranking_method: str = "hybrid"

    generated_at: datetime


# ======================================================================
# Skill Gap Response
# ======================================================================

class CandidateSkillGapResponse(BaseModel):
    """Candidate skill-gap analysis."""

    candidate_id: int

    job_id: Optional[int] = None

    matched_skills: list[Any] = Field(
        default_factory=list,
    )

    missing_skills: list[Any] = Field(
        default_factory=list,
    )

    partially_matched_skills: list[Any] = Field(
        default_factory=list,
    )

    skill_coverage: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    recommendations: list[Any] = Field(
        default_factory=list,
    )


# ======================================================================
# Candidate Comparison Request
# ======================================================================

class CandidateCompareRequest(BaseModel):
    """Request for comparing multiple candidates."""

    candidate_ids: list[int] = Field(
        ...,
        min_length=2,
        max_length=10,
    )

    job_id: Optional[int] = None


# ======================================================================
# Candidate Comparison Item
# ======================================================================

class CandidateComparisonItem(BaseModel):
    """Candidate comparison result."""

    candidate_id: int

    candidate_name: str

    overall_score: Optional[float] = None

    skill_score: Optional[float] = None

    experience_score: Optional[float] = None

    education_score: Optional[float] = None

    interview_score: Optional[float] = None

    ats_score: Optional[float] = None

    matched_skills: list[Any] = Field(
        default_factory=list,
    )

    missing_skills: list[Any] = Field(
        default_factory=list,
    )

    strengths: list[Any] = Field(
        default_factory=list,
    )

    weaknesses: list[Any] = Field(
        default_factory=list,
    )


# ======================================================================
# Candidate Comparison Response
# ======================================================================

class CandidateComparisonResponse(BaseModel):
    """Response for candidate comparison."""

    job_id: Optional[int] = None

    candidates: list[CandidateComparisonItem] = Field(
        default_factory=list,
    )

    comparison_summary: Optional[str] = None

    recommended_candidate_id: Optional[int] = None

    generated_at: datetime


# ======================================================================
# Candidate Response
# ======================================================================

class CandidateResponse(CandidateBase):
    """Complete candidate API response."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    user_id: int

    resume_id: Optional[int] = None

    source: Optional[str] = None

    status: str

    notes: Optional[str] = None

    tags: Optional[list[Any]] = None

    skills: Optional[list[Any]] = None

    experience: Optional[list[Any]] = None

    education: Optional[list[Any]] = None

    certifications: Optional[list[Any]] = None

    projects: Optional[list[Any]] = None

    total_experience_years: Optional[float] = None

    current_salary: Optional[float] = None

    expected_salary: Optional[float] = None

    notice_period_days: Optional[int] = None

    overall_score: Optional[float] = None

    ats_score: Optional[float] = None

    match_score: Optional[float] = None

    interview_score: Optional[float] = None

    created_at: datetime

    updated_at: datetime


# ======================================================================
# Candidate List Item
# ======================================================================

class CandidateListItem(BaseModel):
    """Lightweight candidate representation."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    first_name: str

    last_name: str

    email: str

    current_title: Optional[str] = None

    current_company: Optional[str] = None

    location: Optional[str] = None

    status: str

    overall_score: Optional[float] = None

    ats_score: Optional[float] = None

    match_score: Optional[float] = None

    interview_score: Optional[float] = None

    created_at: datetime


# ======================================================================
# Candidate List Response
# ======================================================================

class CandidateListResponse(BaseModel):
    """Paginated candidate list."""

    items: list[CandidateListItem]

    total: int

    page: int

    page_size: int

    total_pages: int


# ======================================================================
# Candidate Summary
# ======================================================================

class CandidateSummary(BaseModel):
    """Compact candidate representation for other APIs."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    first_name: str

    last_name: str

    email: str

    current_title: Optional[str] = None

    status: str

    overall_score: Optional[float] = None

    match_score: Optional[float] = None