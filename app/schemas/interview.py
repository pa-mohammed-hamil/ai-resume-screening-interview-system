# backend/app/schemas/interview.py

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ======================================================================
# Base Interview Schema
# ======================================================================

class InterviewBase(BaseModel):
    """Common interview configuration fields."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    title: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    interview_type: str = Field(
        default="technical",
        max_length=50,
    )

    mode: str = Field(
        default="text",
        max_length=50,
    )

    difficulty: str = Field(
        default="medium",
        max_length=50,
    )

    duration_minutes: int = Field(
        default=30,
        ge=5,
        le=180,
    )

    total_questions: int = Field(
        default=10,
        ge=1,
        le=100,
    )

    focus_areas: Optional[list[Any]] = None


# ======================================================================
# Create Interview
# ======================================================================

class InterviewCreate(InterviewBase):
    """Schema used to create an interview."""

    candidate_id: int

    job_id: Optional[int] = None

    scheduled_at: Optional[datetime] = None

    interview_config: Optional[dict[str, Any]] = None


# ======================================================================
# Update Interview
# ======================================================================

class InterviewUpdate(BaseModel):
    """Schema used to update interview configuration."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    title: Optional[str] = Field(
        default=None,
        max_length=255,
    )

    interview_type: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    mode: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    difficulty: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    duration_minutes: Optional[int] = Field(
        default=None,
        ge=5,
        le=180,
    )

    total_questions: Optional[int] = Field(
        default=None,
        ge=1,
        le=100,
    )

    focus_areas: Optional[list[Any]] = None

    interview_config: Optional[dict[str, Any]] = None

    scheduled_at: Optional[datetime] = None


# ======================================================================
# Interview Status Update
# ======================================================================

class InterviewStatusUpdate(BaseModel):
    """Schema used to update interview status."""

    status: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )


# ======================================================================
# Interview Question
# ======================================================================

class InterviewQuestion(BaseModel):
    """AI-generated interview question."""

    id: Optional[str] = None

    question: str = Field(
        ...,
        min_length=1,
    )

    question_type: str = Field(
        default="technical",
        max_length=50,
    )

    difficulty: str = Field(
        default="medium",
        max_length=50,
    )

    category: Optional[str] = None

    skill: Optional[str] = None

    expected_topics: list[Any] = Field(
        default_factory=list,
    )

    evaluation_criteria: list[Any] = Field(
        default_factory=list,
    )

    time_limit_seconds: Optional[int] = Field(
        default=None,
        ge=10,
    )


# ======================================================================
# Generate Questions Request
# ======================================================================

class QuestionGenerationRequest(BaseModel):
    """Request for AI interview question generation."""

    candidate_id: int

    job_id: Optional[int] = None

    interview_type: str = "technical"

    difficulty: str = "medium"

    number_of_questions: int = Field(
        default=10,
        ge=1,
        le=100,
    )

    focus_areas: list[Any] = Field(
        default_factory=list,
    )

    include_behavioral: bool = True

    include_followups: bool = True


# ======================================================================
# Generate Questions Response
# ======================================================================

class QuestionGenerationResponse(BaseModel):
    """Response containing generated interview questions."""

    interview_id: Optional[int] = None

    questions: list[InterviewQuestion] = Field(
        default_factory=list,
    )

    total_questions: int


# ======================================================================
# Start Interview
# ======================================================================

class InterviewStartRequest(BaseModel):
    """Request used to start an interview."""

    interview_id: int


class InterviewStartResponse(BaseModel):
    """Response returned when an interview starts."""

    interview_id: int

    status: str

    started_at: datetime

    current_question: int

    question: Optional[InterviewQuestion] = None


# ======================================================================
# Submit Answer
# ======================================================================

class AnswerSubmitRequest(BaseModel):
    """Candidate's answer to an interview question."""

    interview_id: int

    question_id: str

    answer: str = Field(
        ...,
        min_length=1,
    )

    response_time_seconds: Optional[float] = Field(
        default=None,
        ge=0,
    )


# ======================================================================
# Answer Response
# ======================================================================

class AnswerResponse(BaseModel):
    """Stored candidate answer."""

    question_id: str

    answer: str

    response_time_seconds: Optional[float] = None

    submitted_at: datetime

    score: Optional[float] = None

    feedback: Optional[str] = None


# ======================================================================
# Adaptive Interview
# ======================================================================

class AdaptiveDecisionRequest(BaseModel):
    """Request for deciding the next adaptive interview question."""

    interview_id: int

    previous_question_id: Optional[str] = None

    previous_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    previous_difficulty: Optional[str] = None


class AdaptiveDecisionResponse(BaseModel):
    """AI adaptive-interview decision."""

    next_question: Optional[InterviewQuestion] = None

    next_difficulty: str

    reason: Optional[str] = None

    should_end: bool = False


# ======================================================================
# Voice Interview
# ======================================================================

class VoiceInterviewStartRequest(BaseModel):
    """Request to start a voice interview."""

    interview_id: int


class VoiceAnswerResponse(BaseModel):
    """Processed voice answer."""

    question_id: str

    transcript: str

    audio_duration_seconds: Optional[float] = None

    speech_rate: Optional[float] = None

    confidence_level: Optional[float] = None

    filler_word_count: Optional[int] = None

    submitted_at: datetime


# ======================================================================
# Voice Analysis
# ======================================================================

class VoiceAnalysis(BaseModel):
    """AI analysis of candidate speech."""

    speech_rate: Optional[float] = None

    confidence_level: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    clarity_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    fluency_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    filler_word_count: Optional[int] = Field(
        default=None,
        ge=0,
    )

    pronunciation_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    observations: list[Any] = Field(
        default_factory=list,
    )


# ======================================================================
# Question Evaluation
# ======================================================================

class QuestionEvaluation(BaseModel):
    """AI evaluation of an individual answer."""

    question_id: str

    score: float = Field(
        ...,
        ge=0,
        le=100,
    )

    correctness_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    relevance_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    depth_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    communication_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    strengths: list[Any] = Field(
        default_factory=list,
    )

    weaknesses: list[Any] = Field(
        default_factory=list,
    )

    feedback: Optional[str] = None


# ======================================================================
# Interview Evaluation
# ======================================================================

class InterviewEvaluationResponse(BaseModel):
    """Complete AI evaluation of an interview."""

    interview_id: int

    overall_score: float = Field(
        ...,
        ge=0,
        le=100,
    )

    technical_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    communication_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    confidence_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    problem_solving_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    behavioral_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    question_evaluations: list[QuestionEvaluation] = Field(
        default_factory=list,
    )

    strengths: list[Any] = Field(
        default_factory=list,
    )

    weaknesses: list[Any] = Field(
        default_factory=list,
    )

    recommendations: list[Any] = Field(
        default_factory=list,
    )

    hiring_recommendation: Optional[str] = None

    evaluated_at: datetime


# ======================================================================
# Interview Scorecard
# ======================================================================

class InterviewScorecard(BaseModel):
    """Recruiter-friendly interview scorecard."""

    interview_id: int

    candidate_id: int

    candidate_name: Optional[str] = None

    overall_score: Optional[float] = None

    technical_score: Optional[float] = None

    communication_score: Optional[float] = None

    confidence_score: Optional[float] = None

    problem_solving_score: Optional[float] = None

    behavioral_score: Optional[float] = None

    recommendation: Optional[str] = None

    strengths: list[Any] = Field(
        default_factory=list,
    )

    weaknesses: list[Any] = Field(
        default_factory=list,
    )

    recommendations: list[Any] = Field(
        default_factory=list,
    )


# ======================================================================
# Interview Report
# ======================================================================

class InterviewReportResponse(BaseModel):
    """Complete interview report."""

    interview_id: int

    candidate_id: int

    job_id: Optional[int] = None

    scorecard: Optional[InterviewScorecard] = None

    transcript: Optional[str] = None

    voice_analysis: Optional[VoiceAnalysis] = None

    evaluation: Optional[InterviewEvaluationResponse] = None

    report_data: Optional[dict[str, Any]] = None

    report_file_path: Optional[str] = None

    generated_at: datetime


# ======================================================================
# Interview Response
# ======================================================================

class InterviewResponse(InterviewBase):
    """Complete interview API response."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    user_id: int

    candidate_id: int

    job_id: Optional[int] = None

    questions: Optional[list[Any]] = None

    interview_config: Optional[dict[str, Any]] = None

    answers: Optional[list[Any]] = None

    answered_questions: int

    current_question: int

    overall_score: Optional[float] = None

    technical_score: Optional[float] = None

    communication_score: Optional[float] = None

    confidence_score: Optional[float] = None

    problem_solving_score: Optional[float] = None

    behavioral_score: Optional[float] = None

    evaluation: Optional[dict[str, Any]] = None

    strengths: Optional[list[Any]] = None

    weaknesses: Optional[list[Any]] = None

    recommendations: Optional[list[Any]] = None

    question_scores: Optional[list[Any]] = None

    audio_file_path: Optional[str] = None

    transcript: Optional[str] = None

    voice_analysis: Optional[dict[str, Any]] = None

    report_data: Optional[dict[str, Any]] = None

    report_file_path: Optional[str] = None

    hiring_recommendation: Optional[str] = None

    recruiter_feedback: Optional[str] = None

    status: str

    is_completed: bool

    is_evaluated: bool

    scheduled_at: Optional[datetime] = None

    started_at: Optional[datetime] = None

    completed_at: Optional[datetime] = None

    evaluated_at: Optional[datetime] = None

    created_at: datetime

    updated_at: datetime


# ======================================================================
# Interview List Item
# ======================================================================

class InterviewListItem(BaseModel):
    """Lightweight interview representation."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    candidate_id: int

    job_id: Optional[int] = None

    title: Optional[str] = None

    interview_type: str

    mode: str

    difficulty: str

    status: str

    overall_score: Optional[float] = None

    hiring_recommendation: Optional[str] = None

    scheduled_at: Optional[datetime] = None

    completed_at: Optional[datetime] = None

    created_at: datetime


# ======================================================================
# Interview List Response
# ======================================================================

class InterviewListResponse(BaseModel):
    """Paginated interview list."""

    items: list[InterviewListItem] = Field(
        default_factory=list,
    )

    total: int

    page: int

    page_size: int

    total_pages: int