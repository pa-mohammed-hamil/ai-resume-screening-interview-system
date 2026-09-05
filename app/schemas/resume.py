# backend/app/schemas/resume.py

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ======================================================================
# Base Resume Schema
# ======================================================================

class ResumeBase(BaseModel):
    """Common resume fields."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    title: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    candidate_name: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    candidate_email: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    candidate_phone: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    location: Optional[str] = Field(
        default=None,
        max_length=255,
    )


# ======================================================================
# Resume Upload
# ======================================================================

class ResumeUploadResponse(BaseModel):
    """Response returned after resume upload."""

    id: int

    filename: str

    original_filename: Optional[str] = None

    file_type: Optional[str] = None

    file_size: Optional[int] = None

    status: str

    is_analyzed: bool

    created_at: datetime


# ======================================================================
# Resume Update
# ======================================================================

class ResumeUpdate(BaseModel):
    """Schema used to update resume metadata."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    title: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    candidate_name: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    candidate_email: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    candidate_phone: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    location: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    is_primary: Optional[bool] = None


# ======================================================================
# Resume Analysis
# ======================================================================

class ResumeAnalysis(BaseModel):
    """AI-generated resume analysis."""

    summary: Optional[str] = None

    skills: list[Any] = Field(
        default_factory=list,
    )

    education: list[Any] = Field(
        default_factory=list,
    )

    experience: list[Any] = Field(
        default_factory=list,
    )

    certifications: list[Any] = Field(
        default_factory=list,
    )

    projects: list[Any] = Field(
        default_factory=list,
    )

    languages: list[Any] = Field(
        default_factory=list,
    )


# ======================================================================
# Resume Score
# ======================================================================

class ResumeScoreResponse(BaseModel):
    """ATS and resume quality scores."""

    ats_score: Optional[float] = None

    skill_score: Optional[float] = None

    experience_score: Optional[float] = None

    education_score: Optional[float] = None

    overall_score: Optional[float] = None


# ======================================================================
# Skill Gap
# ======================================================================

class SkillGapResponse(BaseModel):
    """Resume skill-gap analysis."""

    matched_skills: list[Any] = Field(
        default_factory=list,
    )

    missing_skills: list[Any] = Field(
        default_factory=list,
    )

    recommendations: list[Any] = Field(
        default_factory=list,
    )


# ======================================================================
# Complete Resume Response
# ======================================================================

class ResumeResponse(ResumeBase):
    """Complete resume API response."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    user_id: int

    filename: str

    original_filename: Optional[str] = None

    file_path: str

    file_type: Optional[str] = None

    file_size: Optional[int] = None

    summary: Optional[str] = None

    raw_text: Optional[str] = None

    skills: Optional[list[Any]] = None

    education: Optional[list[Any]] = None

    experience: Optional[list[Any]] = None

    certifications: Optional[list[Any]] = None

    projects: Optional[list[Any]] = None

    languages: Optional[list[Any]] = None

    ats_score: Optional[float] = None

    skill_score: Optional[float] = None

    experience_score: Optional[float] = None

    education_score: Optional[float] = None

    overall_score: Optional[float] = None

    analysis: Optional[dict[str, Any]] = None

    missing_skills: Optional[list[Any]] = None

    matched_skills: Optional[list[Any]] = None

    recommendations: Optional[list[Any]] = None

    status: str

    processing_error: Optional[str] = None

    is_analyzed: bool

    version: int

    is_primary: bool

    created_at: datetime

    updated_at: datetime

    analyzed_at: Optional[datetime] = None


# ======================================================================
# Resume List Item
# ======================================================================

class ResumeListItem(BaseModel):
    """Lightweight resume representation for list pages."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    filename: str

    candidate_name: Optional[str] = None

    candidate_email: Optional[str] = None

    status: str

    is_analyzed: bool

    ats_score: Optional[float] = None

    overall_score: Optional[float] = None

    created_at: datetime


# ======================================================================
# Resume List Response
# ======================================================================

class ResumeListResponse(BaseModel):
    """Paginated resume list."""

    items: list[ResumeListItem]

    total: int

    page: int

    page_size: int

    total_pages: int


# ======================================================================
# Resume Analysis Response
# ======================================================================

class ResumeAnalysisResponse(BaseModel):
    """Response returned after AI resume analysis."""

    resume_id: int

    status: str

    is_analyzed: bool

    analysis: Optional[dict[str, Any]] = None

    ats_score: Optional[float] = None

    skill_score: Optional[float] = None

    experience_score: Optional[float] = None

    education_score: Optional[float] = None

    overall_score: Optional[float] = None

    matched_skills: list[Any] = Field(
        default_factory=list,
    )

    missing_skills: list[Any] = Field(
        default_factory=list,
    )

    recommendations: list[Any] = Field(
        default_factory=list,
    )

    analyzed_at: Optional[datetime] = None


# ======================================================================
# Resume Status Response
# ======================================================================

class ResumeStatusResponse(BaseModel):
    """Resume processing status."""

    resume_id: int

    status: str

    is_analyzed: bool

    processing_error: Optional[str] = None

    analyzed_at: Optional[datetime] = None