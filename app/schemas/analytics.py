# backend/app/schemas/analytics.py

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ======================================================================
# Date Range
# ======================================================================

class AnalyticsDateRange(BaseModel):
    """Date range used for analytics queries."""

    start_date: date

    end_date: date


# ======================================================================
# Analytics Filter
# ======================================================================

class AnalyticsFilter(BaseModel):
    """Common analytics filters."""

    start_date: Optional[date] = None

    end_date: Optional[date] = None

    job_id: Optional[int] = None

    candidate_id: Optional[int] = None

    department: Optional[str] = None

    location: Optional[str] = None

    status: Optional[str] = None


# ======================================================================
# KPI Metric
# ======================================================================

class KPIMetric(BaseModel):
    """Single dashboard KPI."""

    value: float

    previous_value: Optional[float] = None

    change: Optional[float] = None

    change_percentage: Optional[float] = None

    trend: Optional[str] = None

    label: Optional[str] = None


# ======================================================================
# Dashboard Overview
# ======================================================================

class DashboardOverview(BaseModel):
    """Main recruiter dashboard metrics."""

    total_resumes: int = 0

    total_candidates: int = 0

    total_jobs: int = 0

    active_jobs: int = 0

    total_interviews: int = 0

    completed_interviews: int = 0

    shortlisted_candidates: int = 0

    hired_candidates: int = 0

    rejected_candidates: int = 0

    average_ats_score: Optional[float] = None

    average_match_score: Optional[float] = None

    average_interview_score: Optional[float] = None

    hiring_rate: Optional[float] = None

    interview_completion_rate: Optional[float] = None


# ======================================================================
# Dashboard KPI Response
# ======================================================================

class DashboardKPIResponse(BaseModel):
    """Dashboard KPI cards."""

    resumes: KPIMetric

    candidates: KPIMetric

    jobs: KPIMetric

    interviews: KPIMetric

    hires: KPIMetric

    average_score: KPIMetric


# ======================================================================
# Time Series Data
# ======================================================================

class TimeSeriesPoint(BaseModel):
    """Single time-series data point."""

    date: date

    value: float

    label: Optional[str] = None


class TimeSeriesResponse(BaseModel):
    """Time-series chart data."""

    metric: str

    period: str

    data: list[TimeSeriesPoint] = Field(
        default_factory=list,
    )


# ======================================================================
# Recruitment Funnel
# ======================================================================

class FunnelStage(BaseModel):
    """Single recruitment funnel stage."""

    stage: str

    count: int

    percentage: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    conversion_rate: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )


class RecruitmentFunnelResponse(BaseModel):
    """Recruitment pipeline funnel."""

    stages: list[FunnelStage] = Field(
        default_factory=list,
    )

    total_candidates: int = 0

    overall_conversion_rate: Optional[float] = None


# ======================================================================
# Resume Analytics
# ======================================================================

class ResumeAnalytics(BaseModel):
    """Resume processing and ATS analytics."""

    total_resumes: int = 0

    analyzed_resumes: int = 0

    pending_resumes: int = 0

    failed_resumes: int = 0

    average_ats_score: Optional[float] = None

    average_skill_score: Optional[float] = None

    average_experience_score: Optional[float] = None

    average_education_score: Optional[float] = None

    top_skills: list[Any] = Field(
        default_factory=list,
    )

    missing_skills: list[Any] = Field(
        default_factory=list,
    )


# ======================================================================
# ATS Score Distribution
# ======================================================================

class ScoreDistributionBucket(BaseModel):
    """Score distribution bucket."""

    range_start: float

    range_end: float

    count: int


class ATSScoreDistributionResponse(BaseModel):
    """ATS score distribution."""

    average_score: Optional[float] = None

    median_score: Optional[float] = None

    minimum_score: Optional[float] = None

    maximum_score: Optional[float] = None

    distribution: list[ScoreDistributionBucket] = Field(
        default_factory=list,
    )


# ======================================================================
# Candidate Analytics
# ======================================================================

class CandidateAnalytics(BaseModel):
    """Candidate-related analytics."""

    total_candidates: int = 0

    new_candidates: int = 0

    shortlisted_candidates: int = 0

    interview_candidates: int = 0

    hired_candidates: int = 0

    rejected_candidates: int = 0

    average_match_score: Optional[float] = None

    average_candidate_score: Optional[float] = None

    top_candidates: list[Any] = Field(
        default_factory=list,
    )

    candidates_by_status: dict[str, int] = Field(
        default_factory=dict,
    )


# ======================================================================
# Candidate Ranking Analytics
# ======================================================================

class RankingAnalytics(BaseModel):
    """Candidate ranking statistics."""

    total_ranked_candidates: int = 0

    average_rank_score: Optional[float] = None

    top_score: Optional[float] = None

    lowest_score: Optional[float] = None

    average_skill_match: Optional[float] = None

    average_experience_match: Optional[float] = None

    average_semantic_match: Optional[float] = None


# ======================================================================
# Job Analytics
# ======================================================================

class JobAnalytics(BaseModel):
    """Job performance analytics."""

    total_jobs: int = 0

    active_jobs: int = 0

    closed_jobs: int = 0

    draft_jobs: int = 0

    total_openings: int = 0

    filled_openings: int = 0

    average_applicants_per_job: Optional[float] = None

    average_time_to_hire_days: Optional[float] = None

    top_jobs: list[Any] = Field(
        default_factory=list,
    )


# ======================================================================
# Job Performance
# ======================================================================

class JobPerformance(BaseModel):
    """Performance metrics for a specific job."""

    job_id: int

    job_title: str

    applicants: int = 0

    shortlisted: int = 0

    interviewed: int = 0

    hired: int = 0

    rejected: int = 0

    average_match_score: Optional[float] = None

    average_ats_score: Optional[float] = None

    average_interview_score: Optional[float] = None

    hiring_rate: Optional[float] = None


# ======================================================================
# Interview Analytics
# ======================================================================

class InterviewAnalytics(BaseModel):
    """Interview performance analytics."""

    total_interviews: int = 0

    scheduled_interviews: int = 0

    in_progress_interviews: int = 0

    completed_interviews: int = 0

    cancelled_interviews: int = 0

    evaluated_interviews: int = 0

    average_score: Optional[float] = None

    average_technical_score: Optional[float] = None

    average_communication_score: Optional[float] = None

    average_confidence_score: Optional[float] = None

    average_problem_solving_score: Optional[float] = None

    average_behavioral_score: Optional[float] = None

    completion_rate: Optional[float] = None


# ======================================================================
# Interview Score Distribution
# ======================================================================

class InterviewScoreDistributionResponse(BaseModel):
    """Interview score distribution."""

    average_score: Optional[float] = None

    distribution: list[ScoreDistributionBucket] = Field(
        default_factory=list,
    )


# ======================================================================
# Skill Analytics
# ======================================================================

class SkillAnalyticsItem(BaseModel):
    """Analytics for an individual skill."""

    skill: str

    demand_count: int = 0

    candidate_count: int = 0

    matched_count: int = 0

    missing_count: int = 0

    demand_percentage: Optional[float] = None

    coverage_percentage: Optional[float] = None


class SkillAnalyticsResponse(BaseModel):
    """Skill demand and candidate skill coverage."""

    total_skills: int = 0

    top_skills: list[SkillAnalyticsItem] = Field(
        default_factory=list,
    )

    skill_gaps: list[SkillAnalyticsItem] = Field(
        default_factory=list,
    )


# ======================================================================
# Hiring Analytics
# ======================================================================

class HiringAnalytics(BaseModel):
    """Hiring performance analytics."""

    total_hires: int = 0

    hiring_rate: Optional[float] = None

    average_time_to_hire_days: Optional[float] = None

    average_hired_candidate_score: Optional[float] = None

    average_hired_interview_score: Optional[float] = None

    hires_by_month: list[TimeSeriesPoint] = Field(
        default_factory=list,
    )

    hires_by_job: list[Any] = Field(
        default_factory=list,
    )


# ======================================================================
# Source Analytics
# ======================================================================

class CandidateSourceAnalytics(BaseModel):
    """Candidate source performance."""

    source: str

    candidate_count: int = 0

    shortlisted_count: int = 0

    interviewed_count: int = 0

    hired_count: int = 0

    conversion_rate: Optional[float] = None

    hiring_rate: Optional[float] = None


class CandidateSourceAnalyticsResponse(BaseModel):
    """Candidate source analytics."""

    sources: list[CandidateSourceAnalytics] = Field(
        default_factory=list,
    )


# ======================================================================
# Department Analytics
# ======================================================================

class DepartmentAnalytics(BaseModel):
    """Hiring analytics by department."""

    department: str

    jobs: int = 0

    candidates: int = 0

    interviews: int = 0

    hires: int = 0

    hiring_rate: Optional[float] = None


class DepartmentAnalyticsResponse(BaseModel):
    """Department-level analytics."""

    departments: list[DepartmentAnalytics] = Field(
        default_factory=list,
    )


# ======================================================================
# Analytics Summary
# ======================================================================

class AnalyticsSummary(BaseModel):
    """Complete analytics summary."""

    date_range: Optional[AnalyticsDateRange] = None

    overview: DashboardOverview

    resumes: Optional[ResumeAnalytics] = None

    candidates: Optional[CandidateAnalytics] = None

    jobs: Optional[JobAnalytics] = None

    interviews: Optional[InterviewAnalytics] = None

    hiring: Optional[HiringAnalytics] = None

    funnel: Optional[RecruitmentFunnelResponse] = None

    skills: Optional[SkillAnalyticsResponse] = None


# ======================================================================
# Analytics Response
# ======================================================================

class AnalyticsResponse(BaseModel):
    """Generic analytics API response."""

    success: bool = True

    generated_at: datetime

    data: AnalyticsSummary