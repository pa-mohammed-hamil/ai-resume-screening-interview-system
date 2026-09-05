# backend/app/schemas/copilot.py

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ======================================================================
# Copilot Message
# ======================================================================

class CopilotMessage(BaseModel):
    """Single message in a Copilot conversation."""

    role: str = Field(
        ...,
        min_length=1,
        max_length=30,
    )

    content: str = Field(
        ...,
        min_length=1,
    )

    timestamp: Optional[datetime] = None

    metadata: Optional[dict[str, Any]] = None


# ======================================================================
# Copilot Context
# ======================================================================

class CopilotContext(BaseModel):
    """Context supplied to the AI recruiter Copilot."""

    user_id: Optional[int] = None

    job_id: Optional[int] = None

    candidate_id: Optional[int] = None

    resume_id: Optional[int] = None

    interview_id: Optional[int] = None

    page: Optional[str] = None

    selected_ids: list[int] = Field(
        default_factory=list,
    )

    filters: dict[str, Any] = Field(
        default_factory=dict,
    )

    additional_context: dict[str, Any] = Field(
        default_factory=dict,
    )


# ======================================================================
# Copilot Chat Request
# ======================================================================

class CopilotChatRequest(BaseModel):
    """Request sent to Recruiter Copilot."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )

    conversation_id: Optional[str] = None

    context: Optional[CopilotContext] = None

    history: list[CopilotMessage] = Field(
        default_factory=list,
    )

    stream: bool = False


# ======================================================================
# Copilot Action
# ======================================================================

class CopilotAction(BaseModel):
    """Action proposed or executed by Copilot."""

    action_id: Optional[str] = None

    action_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    description: Optional[str] = None

    parameters: dict[str, Any] = Field(
        default_factory=dict,
    )

    requires_confirmation: bool = False

    status: str = "pending"


# ======================================================================
# Copilot Action Request
# ======================================================================

class CopilotActionRequest(BaseModel):
    """Request to execute a Copilot action."""

    action_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    parameters: dict[str, Any] = Field(
        default_factory=dict,
    )

    confirmed: bool = False

    context: Optional[CopilotContext] = None


# ======================================================================
# Copilot Action Result
# ======================================================================

class CopilotActionResult(BaseModel):
    """Result returned after executing an AI action."""

    action_id: Optional[str] = None

    action_type: str

    success: bool

    message: Optional[str] = None

    data: Optional[dict[str, Any]] = None

    error: Optional[str] = None

    executed_at: datetime


# ======================================================================
# Copilot Recommendation
# ======================================================================

class CopilotRecommendation(BaseModel):
    """AI-generated recruiter recommendation."""

    recommendation_id: Optional[str] = None

    title: str

    description: str

    category: str = "general"

    priority: str = "medium"

    confidence: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
    )

    candidate_id: Optional[int] = None

    job_id: Optional[int] = None

    interview_id: Optional[int] = None

    suggested_action: Optional[CopilotAction] = None


# ======================================================================
# Candidate Recommendation
# ======================================================================

class CandidateRecommendation(BaseModel):
    """Recommendation for a specific candidate."""

    candidate_id: int

    candidate_name: Optional[str] = None

    score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    recommendation: str

    reasons: list[str] = Field(
        default_factory=list,
    )

    strengths: list[str] = Field(
        default_factory=list,
    )

    concerns: list[str] = Field(
        default_factory=list,
    )

    next_action: Optional[str] = None


# ======================================================================
# Job Recommendation
# ======================================================================

class JobRecommendation(BaseModel):
    """Recommendation related to a job posting."""

    job_id: int

    job_title: Optional[str] = None

    recommendation: str

    reasons: list[str] = Field(
        default_factory=list,
    )

    suggested_changes: list[str] = Field(
        default_factory=list,
    )

    priority: str = "medium"


# ======================================================================
# Hiring Recommendation
# ======================================================================

class HiringRecommendation(BaseModel):
    """AI hiring recommendation."""

    candidate_id: int

    job_id: Optional[int] = None

    recommendation: str

    confidence: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
    )

    overall_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    evidence: list[str] = Field(
        default_factory=list,
    )

    risks: list[str] = Field(
        default_factory=list,
    )

    recommended_next_step: Optional[str] = None


# ======================================================================
# Copilot Response
# ======================================================================

class CopilotResponse(BaseModel):
    """Complete Recruiter Copilot response."""

    success: bool = True

    conversation_id: Optional[str] = None

    message: str

    response_type: str = "text"

    actions: list[CopilotAction] = Field(
        default_factory=list,
    )

    recommendations: list[CopilotRecommendation] = Field(
        default_factory=list,
    )

    action_results: list[CopilotActionResult] = Field(
        default_factory=list,
    )

    sources: list[dict[str, Any]] = Field(
        default_factory=list,
    )

    context_used: Optional[CopilotContext] = None

    generated_at: datetime


# ======================================================================
# Copilot Conversation
# ======================================================================

class CopilotConversation(BaseModel):
    """Stored Copilot conversation."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    conversation_id: str

    user_id: int

    title: Optional[str] = None

    messages: list[CopilotMessage] = Field(
        default_factory=list,
    )

    context: Optional[CopilotContext] = None

    created_at: datetime

    updated_at: datetime


# ======================================================================
# Copilot Conversation List
# ======================================================================

class CopilotConversationItem(BaseModel):
    """Lightweight conversation representation."""

    conversation_id: str

    title: Optional[str] = None

    message_count: int = 0

    created_at: datetime

    updated_at: datetime


class CopilotConversationListResponse(BaseModel):
    """Paginated Copilot conversation list."""

    items: list[CopilotConversationItem] = Field(
        default_factory=list,
    )

    total: int

    page: int

    page_size: int

    total_pages: int


# ======================================================================
# Copilot Query
# ======================================================================

class CopilotQueryRequest(BaseModel):
    """Structured recruiter query."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )

    query_type: Optional[str] = None

    context: Optional[CopilotContext] = None

    limit: int = Field(
        default=10,
        ge=1,
        le=100,
    )


# ======================================================================
# Copilot Query Result
# ======================================================================

class CopilotQueryResult(BaseModel):
    """Structured result from a recruiter query."""

    query: str

    query_type: Optional[str] = None

    answer: str

    results: list[Any] = Field(
        default_factory=list,
    )

    total_results: int = 0

    generated_at: datetime


# ======================================================================
# Copilot Search
# ======================================================================

class CopilotSearchRequest(BaseModel):
    """Natural-language search request."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    entity_type: Optional[str] = None

    filters: dict[str, Any] = Field(
        default_factory=dict,
    )

    limit: int = Field(
        default=20,
        ge=1,
        le=100,
    )


class CopilotSearchResult(BaseModel):
    """Search result returned to Copilot."""

    entity_type: str

    entity_id: int

    title: Optional[str] = None

    score: Optional[float] = None

    data: dict[str, Any] = Field(
        default_factory=dict,
    )


class CopilotSearchResponse(BaseModel):
    """Natural-language search response."""

    query: str

    results: list[CopilotSearchResult] = Field(
        default_factory=list,
    )

    total: int


# ======================================================================
# Copilot Analytics Query
# ======================================================================

class CopilotAnalyticsRequest(BaseModel):
    """Request analytics through natural language."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    start_date: Optional[datetime] = None

    end_date: Optional[datetime] = None

    job_id: Optional[int] = None

    department: Optional[str] = None


class CopilotAnalyticsResponse(BaseModel):
    """AI-generated analytics answer."""

    question: str

    answer: str

    metrics: dict[str, Any] = Field(
        default_factory=dict,
    )

    insights: list[str] = Field(
        default_factory=list,
    )

    recommendations: list[CopilotRecommendation] = Field(
        default_factory=list,
    )

    generated_at: datetime


# ======================================================================
# Copilot Feedback
# ======================================================================

class CopilotFeedbackRequest(BaseModel):
    """Recruiter feedback on a Copilot response."""

    conversation_id: Optional[str] = None

    message_id: Optional[str] = None

    rating: int = Field(
        ...,
        ge=1,
        le=5,
    )

    feedback: Optional[str] = Field(
        default=None,
        max_length=5000,
    )


class CopilotFeedbackResponse(BaseModel):
    """Feedback submission response."""

    success: bool = True

    message: str = "Feedback recorded successfully."