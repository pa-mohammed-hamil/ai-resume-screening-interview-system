# Project scaffold file
"""
genai/copilot/context.py

Recruiter Copilot Context Management
====================================

Centralized context layer for the Recruiter Copilot.

Responsibilities:

- Store recruiter/user context
- Store job context
- Store candidate context
- Store resume context
- Store interview context
- Store analytics context
- Store conversation history
- Store RAG results
- Build compact LLM-ready context
- Prevent unnecessary/private data exposure
- Merge context from multiple sources

Architecture:

    API
     │
     ▼
    CopilotService
     │
     ▼
    ContextManager
     │
     ├── User
     ├── Organization
     ├── Job
     ├── Candidate
     ├── Resume
     ├── Interview
     ├── Analytics
     ├── Conversation
     └── RAG
            │
            ▼
        RecruiterCopilot
            │
            ▼
            LLM
"""

from __future__ import annotations

import copy
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


# ============================================================================
# CONSTANTS
# ============================================================================

DEFAULT_MAX_HISTORY = 20
DEFAULT_MAX_RAG_RESULTS = 10
DEFAULT_MAX_SEARCH_RESULTS = 20

SENSITIVE_FIELDS = {
    "password",
    "password_hash",
    "hashed_password",
    "token",
    "access_token",
    "refresh_token",
    "secret",
    "api_key",
    "private_key",
    "credit_card",
    "ssn",
}

PROTECTED_FIELDS = {
    "age",
    "date_of_birth",
    "gender",
    "sex",
    "race",
    "ethnicity",
    "religion",
    "marital_status",
    "disability",
    "medical_history",
    "health_information",
}


# ============================================================================
# CONTEXT DATA CLASSES
# ============================================================================


@dataclass
class UserContext:
    """
    Recruiter/user information.
    """

    user_id: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = None
    organization_id: Optional[str] = None
    permissions: List[str] = field(
        default_factory=list
    )


@dataclass
class OrganizationContext:
    """
    Organization-level information.
    """

    organization_id: Optional[str] = None
    name: Optional[str] = None
    industry: Optional[str] = None
    settings: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class JobContext:
    """
    Current job information.
    """

    job_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: List[str] = field(
        default_factory=list
    )
    responsibilities: List[str] = field(
        default_factory=list
    )
    skills: List[str] = field(
        default_factory=list
    )
    experience_required: Optional[str] = None
    education_required: Optional[str] = None
    location: Optional[str] = None
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class CandidateContext:
    """
    Current candidate information.
    """

    candidate_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = field(
        default_factory=list
    )
    experience: List[Dict[str, Any]] = field(
        default_factory=list
    )
    education: List[Dict[str, Any]] = field(
        default_factory=list
    )
    scores: Dict[str, Any] = field(
        default_factory=dict
    )
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ResumeContext:
    """
    Resume information.
    """

    resume_id: Optional[str] = None
    candidate_id: Optional[str] = None
    filename: Optional[str] = None
    raw_text: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = field(
        default_factory=list
    )
    experience: List[Dict[str, Any]] = field(
        default_factory=list
    )
    education: List[Dict[str, Any]] = field(
        default_factory=list
    )
    projects: List[Dict[str, Any]] = field(
        default_factory=list
    )
    certifications: List[str] = field(
        default_factory=list
    )
    ats_score: Optional[float] = None
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class InterviewContext:
    """
    Interview information.
    """

    interview_id: Optional[str] = None
    candidate_id: Optional[str] = None
    job_id: Optional[str] = None
    status: Optional[str] = None
    interview_type: Optional[str] = None
    questions: List[Dict[str, Any]] = field(
        default_factory=list
    )
    answers: List[Dict[str, Any]] = field(
        default_factory=list
    )
    scores: Dict[str, Any] = field(
        default_factory=dict
    )
    feedback: List[str] = field(
        default_factory=list
    )
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class AnalyticsContext:
    """
    Recruitment analytics.
    """

    metrics: Dict[str, Any] = field(
        default_factory=dict
    )

    trends: List[Dict[str, Any]] = field(
        default_factory=list
    )

    funnel: Dict[str, Any] = field(
        default_factory=dict
    )

    time_to_hire: Optional[float] = None

    additional_metrics: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class RAGContext:
    """
    Retrieved knowledge/documents.
    """

    query: Optional[str] = None

    documents: List[Dict[str, Any]] = field(
        default_factory=list
    )

    sources: List[str] = field(
        default_factory=list
    )

    relevance_scores: List[float] = field(
        default_factory=list
    )


@dataclass
class ConversationMessage:
    """
    Single conversation message.
    """

    role: str
    content: str
    timestamp: Optional[str] = None
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class CopilotContext:
    """
    Complete context supplied to the Recruiter Copilot.
    """

    user: Optional[UserContext] = None

    organization: Optional[OrganizationContext] = None

    job: Optional[JobContext] = None

    candidate: Optional[CandidateContext] = None

    resume: Optional[ResumeContext] = None

    interview: Optional[InterviewContext] = None

    analytics: Optional[AnalyticsContext] = None

    rag: Optional[RAGContext] = None

    conversation: List[ConversationMessage] = field(
        default_factory=list
    )

    search_results: List[Dict[str, Any]] = field(
        default_factory=list
    )

    additional_context: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )


# ============================================================================
# CONTEXT BUILDER
# ============================================================================


class ContextBuilder:
    """
    Builder used to construct CopilotContext incrementally.
    """

    def __init__(self) -> None:

        self.context = CopilotContext()

    # ------------------------------------------------------------------------
    # USER
    # ------------------------------------------------------------------------

    def set_user(
        self,
        user: Optional[Dict[str, Any]],
    ) -> "ContextBuilder":

        if user is None:
            self.context.user = None
            return self

        clean_user = sanitize_data(
            user,
            remove_protected=False,
        )

        self.context.user = UserContext(
            user_id=_get(clean_user, "user_id", "id"),
            name=_get(clean_user, "name", "full_name"),
            role=clean_user.get("role"),
            organization_id=_get(
                clean_user,
                "organization_id",
                "org_id",
            ),
            permissions=clean_user.get(
                "permissions",
                [],
            ),
        )

        return self

    # ------------------------------------------------------------------------
    # ORGANIZATION
    # ------------------------------------------------------------------------

    def set_organization(
        self,
        organization: Optional[Dict[str, Any]],
    ) -> "ContextBuilder":

        if organization is None:
            self.context.organization = None
            return self

        data = sanitize_data(
            organization
        )

        self.context.organization = (
            OrganizationContext(
                organization_id=_get(
                    data,
                    "organization_id",
                    "id",
                ),
                name=data.get("name"),
                industry=data.get("industry"),
                settings=data.get(
                    "settings",
                    {},
                ),
            )
        )

        return self

    # ------------------------------------------------------------------------
    # JOB
    # ------------------------------------------------------------------------

    def set_job(
        self,
        job: Optional[Dict[str, Any]],
    ) -> "ContextBuilder":

        if job is None:
            self.context.job = None
            return self

        data = sanitize_data(
            job
        )

        self.context.job = JobContext(
            job_id=_get(
                data,
                "job_id",
                "id",
            ),
            title=data.get("title"),
            description=data.get(
                "description"
            ),
            requirements=_as_list(
                data.get("requirements")
            ),
            responsibilities=_as_list(
                data.get("responsibilities")
            ),
            skills=_as_list(
                data.get("skills")
            ),
            experience_required=data.get(
                "experience_required"
            ),
            education_required=data.get(
                "education_required"
            ),
            location=data.get("location"),
            metadata=data.get(
                "metadata",
                {},
            ),
        )

        return self

    # ------------------------------------------------------------------------
    # CANDIDATE
    # ------------------------------------------------------------------------

    def set_candidate(
        self,
        candidate: Optional[Dict[str, Any]],
    ) -> "ContextBuilder":

        if candidate is None:
            self.context.candidate = None
            return self

        data = sanitize_data(
            candidate
        )

        self.context.candidate = (
            CandidateContext(
                candidate_id=_get(
                    data,
                    "candidate_id",
                    "id",
                ),
                name=_get(
                    data,
                    "name",
                    "full_name",
                ),
                email=data.get("email"),
                headline=data.get(
                    "headline"
                ),
                summary=data.get(
                    "summary"
                ),
                skills=_as_list(
                    data.get("skills")
                ),
                experience=_as_dict_list(
                    data.get("experience")
                ),
                education=_as_dict_list(
                    data.get("education")
                ),
                scores=data.get(
                    "scores",
                    {},
                ),
                metadata=data.get(
                    "metadata",
                    {},
                ),
            )
        )

        return self

    # ------------------------------------------------------------------------
    # RESUME
    # ------------------------------------------------------------------------

    def set_resume(
        self,
        resume: Optional[Dict[str, Any]],
    ) -> "ContextBuilder":

        if resume is None:
            self.context.resume = None
            return self

        data = sanitize_data(
            resume
        )

        self.context.resume = ResumeContext(
            resume_id=_get(
                data,
                "resume_id",
                "id",
            ),
            candidate_id=data.get(
                "candidate_id"
            ),
            filename=data.get(
                "filename"
            ),
            raw_text=data.get(
                "raw_text"
            ),
            summary=data.get(
                "summary"
            ),
            skills=_as_list(
                data.get("skills")
            ),
            experience=_as_dict_list(
                data.get("experience")
            ),
            education=_as_dict_list(
                data.get("education")
            ),
            projects=_as_dict_list(
                data.get("projects")
            ),
            certifications=_as_list(
                data.get("certifications")
            ),
            ats_score=data.get(
                "ats_score"
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )

        return self

    # ------------------------------------------------------------------------
    # INTERVIEW
    # ------------------------------------------------------------------------

    def set_interview(
        self,
        interview: Optional[Dict[str, Any]],
    ) -> "ContextBuilder":

        if interview is None:
            self.context.interview = None
            return self

        data = sanitize_data(
            interview
        )

        self.context.interview = (
            InterviewContext(
                interview_id=_get(
                    data,
                    "interview_id",
                    "id",
                ),
                candidate_id=data.get(
                    "candidate_id"
                ),
                job_id=data.get(
                    "job_id"
                ),
                status=data.get(
                    "status"
                ),
                interview_type=data.get(
                    "interview_type"
                ),
                questions=_as_dict_list(
                    data.get("questions")
                ),
                answers=_as_dict_list(
                    data.get("answers")
                ),
                scores=data.get(
                    "scores",
                    {},
                ),
                feedback=_as_list(
                    data.get("feedback")
                ),
                metadata=data.get(
                    "metadata",
                    {},
                ),
            )
        )

        return self

    # ------------------------------------------------------------------------
    # ANALYTICS
    # ------------------------------------------------------------------------

    def set_analytics(
        self,
        analytics: Optional[Dict[str, Any]],
    ) -> "ContextBuilder":

        if analytics is None:
            self.context.analytics = None
            return self

        data = sanitize_data(
            analytics
        )

        self.context.analytics = (
            AnalyticsContext(
                metrics=data.get(
                    "metrics",
                    {},
                ),
                trends=_as_dict_list(
                    data.get("trends")
                ),
                funnel=data.get(
                    "funnel",
                    {},
                ),
                time_to_hire=data.get(
                    "time_to_hire"
                ),
                additional_metrics=data.get(
                    "additional_metrics",
                    {},
                ),
            )
        )

        return self

    # ------------------------------------------------------------------------
    # RAG
    # ------------------------------------------------------------------------

    def set_rag(
        self,
        rag: Optional[Dict[str, Any]],
    ) -> "ContextBuilder":

        if rag is None:
            self.context.rag = None
            return self

        data = sanitize_data(
            rag
        )

        documents = _as_dict_list(
            data.get("documents")
        )

        self.context.rag = RAGContext(
            query=data.get("query"),
            documents=documents[
                :DEFAULT_MAX_RAG_RESULTS
            ],
            sources=_as_list(
                data.get("sources")
            ),
            relevance_scores=_as_float_list(
                data.get("relevance_scores")
            ),
        )

        return self

    # ------------------------------------------------------------------------
    # SEARCH RESULTS
    # ------------------------------------------------------------------------

    def set_search_results(
        self,
        results: Optional[
            List[Dict[str, Any]]
        ],
    ) -> "ContextBuilder":

        if not results:
            self.context.search_results = []
            return self

        clean_results = [
            sanitize_data(item)
            for item in results
            if isinstance(item, dict)
        ]

        self.context.search_results = (
            clean_results[
                :DEFAULT_MAX_SEARCH_RESULTS
            ]
        )

        return self

    # ------------------------------------------------------------------------
    # CONVERSATION
    # ------------------------------------------------------------------------

    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> "ContextBuilder":

        if not content or not content.strip():
            return self

        if role not in {
            "system",
            "user",
            "assistant",
            "tool",
        }:
            raise ValueError(
                f"Invalid conversation role: {role}"
            )

        self.context.conversation.append(
            ConversationMessage(
                role=role,
                content=content.strip(),
                timestamp=datetime.utcnow().isoformat(),
                metadata=metadata or {},
            )
        )

        self.context.conversation = (
            self.context.conversation[
                -DEFAULT_MAX_HISTORY:
            ]
        )

        return self

    # ------------------------------------------------------------------------
    # ADDITIONAL CONTEXT
    # ------------------------------------------------------------------------

    def add_context(
        self,
        key: str,
        value: Any,
    ) -> "ContextBuilder":

        if not key:
            raise ValueError(
                "Context key cannot be empty."
            )

        self.context.additional_context[
            key
        ] = sanitize_data(value)

        return self

    # ------------------------------------------------------------------------
    # BUILD
    # ------------------------------------------------------------------------

    def build(self) -> CopilotContext:

        return copy.deepcopy(
            self.context
        )


# ============================================================================
# CONTEXT MANAGER
# ============================================================================


class ContextManager:
    """
    Manages context lifecycle for the Recruiter Copilot.
    """

    def __init__(
        self,
        max_history: int = DEFAULT_MAX_HISTORY,
        max_rag_results: int = DEFAULT_MAX_RAG_RESULTS,
    ) -> None:

        self.max_history = max(
            1,
            max_history,
        )

        self.max_rag_results = max(
            1,
            max_rag_results,
        )

    # ------------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------------

    def create(
        self,
        *,
        user: Optional[Dict[str, Any]] = None,
        organization: Optional[
            Dict[str, Any]
        ] = None,
        job: Optional[Dict[str, Any]] = None,
        candidate: Optional[
            Dict[str, Any]
        ] = None,
        resume: Optional[
            Dict[str, Any]
        ] = None,
        interview: Optional[
            Dict[str, Any]
        ] = None,
        analytics: Optional[
            Dict[str, Any]
        ] = None,
        rag: Optional[
            Dict[str, Any]
        ] = None,
        search_results: Optional[
            List[Dict[str, Any]]
        ] = None,
        conversation: Optional[
            List[Dict[str, Any]]
        ] = None,
        additional_context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> CopilotContext:
        """
        Create a complete copilot context.
        """

        builder = ContextBuilder()

        builder.set_user(user)
        builder.set_organization(
            organization
        )
        builder.set_job(job)
        builder.set_candidate(candidate)
        builder.set_resume(resume)
        builder.set_interview(interview)
        builder.set_analytics(analytics)
        builder.set_rag(rag)
        builder.set_search_results(
            search_results
        )

        if conversation:

            for message in conversation:

                if not isinstance(
                    message,
                    dict,
                ):
                    continue

                builder.add_message(
                    role=message.get(
                        "role",
                        "user",
                    ),
                    content=message.get(
                        "content",
                        "",
                    ),
                    metadata=message.get(
                        "metadata",
                        {},
                    ),
                )

        if additional_context:

            for key, value in (
                additional_context.items()
            ):

                builder.add_context(
                    key,
                    value,
                )

        return builder.build()

    # ------------------------------------------------------------------------
    # MERGE
    # ------------------------------------------------------------------------

    def merge(
        self,
        base: CopilotContext,
        update: CopilotContext,
    ) -> CopilotContext:
        """
        Merge two contexts.

        Values from update take precedence when present.
        """

        result = copy.deepcopy(
            base
        )

        if update.user is not None:
            result.user = update.user

        if update.organization is not None:
            result.organization = (
                update.organization
            )

        if update.job is not None:
            result.job = update.job

        if update.candidate is not None:
            result.candidate = (
                update.candidate
            )

        if update.resume is not None:
            result.resume = update.resume

        if update.interview is not None:
            result.interview = (
                update.interview
            )

        if update.analytics is not None:
            result.analytics = (
                update.analytics
            )

        if update.rag is not None:
            result.rag = update.rag

        if update.search_results:

            result.search_results = (
                update.search_results
            )

        if update.conversation:

            result.conversation = (
                result.conversation
                + update.conversation
            )

            result.conversation = (
                result.conversation[
                    -self.max_history:
                ]
            )

        result.additional_context.update(
            update.additional_context
        )

        return result

    # ------------------------------------------------------------------------
    # ADD USER MESSAGE
    # ------------------------------------------------------------------------

    def add_user_message(
        self,
        context: CopilotContext,
        message: str,
    ) -> CopilotContext:
        """
        Add a recruiter message to context.
        """

        context = copy.deepcopy(
            context
        )

        context.conversation.append(
            ConversationMessage(
                role="user",
                content=message.strip(),
                timestamp=datetime.utcnow().isoformat(),
            )
        )

        context.conversation = (
            context.conversation[
                -self.max_history:
            ]
        )

        return context

    # ------------------------------------------------------------------------
    # ADD ASSISTANT MESSAGE
    # ------------------------------------------------------------------------

    def add_assistant_message(
        self,
        context: CopilotContext,
        message: str,
    ) -> CopilotContext:
        """
        Add an assistant response.
        """

        context = copy.deepcopy(
            context
        )

        context.conversation.append(
            ConversationMessage(
                role="assistant",
                content=message.strip(),
                timestamp=datetime.utcnow().isoformat(),
            )
        )

        context.conversation = (
            context.conversation[
                -self.max_history:
            ]
        )

        return context

    # ------------------------------------------------------------------------
    # ADD RAG
    # ------------------------------------------------------------------------

    def add_rag_results(
        self,
        context: CopilotContext,
        documents: List[Dict[str, Any]],
        query: Optional[str] = None,
    ) -> CopilotContext:
        """
        Add retrieved RAG documents.
        """

        context = copy.deepcopy(
            context
        )

        clean_documents = [
            sanitize_data(document)
            for document in documents
            if isinstance(document, dict)
        ]

        context.rag = RAGContext(
            query=query,
            documents=clean_documents[
                :self.max_rag_results
            ],
            sources=[
                str(
                    document.get(
                        "source",
                        "",
                    )
                )
                for document in clean_documents[
                    :self.max_rag_results
                ]
                if document.get("source")
            ],
            relevance_scores=[
                float(
                    document.get(
                        "score",
                        0,
                    )
                )
                for document in clean_documents[
                    :self.max_rag_results
                ]
                if isinstance(
                    document.get("score"),
                    (int, float),
                )
            ],
        )

        return context

    # ------------------------------------------------------------------------
    # TO DICT
    # ------------------------------------------------------------------------

    def to_dict(
        self,
        context: CopilotContext,
    ) -> Dict[str, Any]:
        """
        Convert context into a serializable dictionary.
        """

        data = asdict(
            context
        )

        return sanitize_data(
            data
        )

    # ------------------------------------------------------------------------
    # TO LLM CONTEXT
    # ------------------------------------------------------------------------

    def to_llm_context(
        self,
        context: CopilotContext,
    ) -> Dict[str, Any]:
        """
        Return only the information needed by the LLM.

        This intentionally avoids exposing unnecessary system data.
        """

        output: Dict[str, Any] = {}

        if context.user:

            output["user"] = {
                "name": context.user.name,
                "role": context.user.role,
                "organization_id": (
                    context.user.organization_id
                ),
            }

        if context.organization:

            output["organization"] = {
                "name": context.organization.name,
                "industry": context.organization.industry,
            }

        if context.job:

            output["job"] = {
                "job_id": context.job.job_id,
                "title": context.job.title,
                "description": context.job.description,
                "requirements": (
                    context.job.requirements
                ),
                "responsibilities": (
                    context.job.responsibilities
                ),
                "skills": context.job.skills,
                "experience_required": (
                    context.job.experience_required
                ),
                "education_required": (
                    context.job.education_required
                ),
                "location": context.job.location,
            }

        if context.candidate:

            output["candidate"] = {
                "candidate_id": (
                    context.candidate.candidate_id
                ),
                "name": context.candidate.name,
                "headline": (
                    context.candidate.headline
                ),
                "summary": (
                    context.candidate.summary
                ),
                "skills": context.candidate.skills,
                "experience": (
                    context.candidate.experience
                ),
                "education": (
                    context.candidate.education
                ),
                "scores": (
                    context.candidate.scores
                ),
            }

        if context.resume:

            output["resume"] = {
                "resume_id": (
                    context.resume.resume_id
                ),
                "summary": context.resume.summary,
                "skills": context.resume.skills,
                "experience": (
                    context.resume.experience
                ),
                "education": (
                    context.resume.education
                ),
                "projects": (
                    context.resume.projects
                ),
                "certifications": (
                    context.resume.certifications
                ),
                "ats_score": (
                    context.resume.ats_score
                ),
            }

        if context.interview:

            output["interview"] = {
                "interview_id": (
                    context.interview.interview_id
                ),
                "status": (
                    context.interview.status
                ),
                "interview_type": (
                    context.interview.interview_type
                ),
                "questions": (
                    context.interview.questions
                ),
                "answers": (
                    context.interview.answers
                ),
                "scores": (
                    context.interview.scores
                ),
                "feedback": (
                    context.interview.feedback
                ),
            }

        if context.analytics:

            output["analytics"] = {
                "metrics": (
                    context.analytics.metrics
                ),
                "trends": (
                    context.analytics.trends
                ),
                "funnel": (
                    context.analytics.funnel
                ),
                "time_to_hire": (
                    context.analytics.time_to_hire
                ),
                "additional_metrics": (
                    context.analytics.additional_metrics
                ),
            }

        if context.rag:

            output["knowledge"] = {
                "query": context.rag.query,
                "documents": (
                    context.rag.documents
                ),
                "sources": (
                    context.rag.sources
                ),
                "relevance_scores": (
                    context.rag.relevance_scores
                ),
            }

        if context.search_results:

            output["search_results"] = (
                context.search_results[
                    :DEFAULT_MAX_SEARCH_RESULTS
                ]
            )

        if context.conversation:

            output["conversation"] = [
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in context.conversation[
                    -self.max_history:
                ]
            ]

        if context.additional_context:

            output["additional_context"] = (
                context.additional_context
            )

        return sanitize_data(
            output
        )


# ============================================================================
# SANITIZATION
# ============================================================================


def sanitize_data(
    data: Any,
    *,
    remove_protected: bool = True,
) -> Any:
    """
    Recursively remove sensitive fields.

    Protected employment characteristics are removed by default
    so they cannot accidentally become inputs to hiring decisions.
    """

    if isinstance(data, dict):

        result = {}

        for key, value in data.items():

            normalized_key = str(
                key
            ).lower().replace(
                "-",
                "_",
            ).replace(
                " ",
                "_",
            )

            if normalized_key in SENSITIVE_FIELDS:
                continue

            if (
                remove_protected
                and normalized_key in PROTECTED_FIELDS
            ):
                continue

            result[key] = sanitize_data(
                value,
                remove_protected=remove_protected,
            )

        return result

    if isinstance(data, list):

        return [
            sanitize_data(
                item,
                remove_protected=remove_protected,
            )
            for item in data
        ]

    if isinstance(data, tuple):

        return tuple(
            sanitize_data(
                item,
                remove_protected=remove_protected,
            )
            for item in data
        )

    return data


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _get(
    data: Dict[str, Any],
    *keys: str,
) -> Optional[Any]:
    """
    Get the first available value from multiple keys.
    """

    for key in keys:

        value = data.get(key)

        if value is not None:
            return value

    return None


def _as_list(
    value: Any,
) -> List[Any]:
    """
    Convert a value to a list.
    """

    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    if isinstance(value, set):
        return list(value)

    return [value]


def _as_dict_list(
    value: Any,
) -> List[Dict[str, Any]]:
    """
    Convert a value to a list of dictionaries.
    """

    if not isinstance(value, list):
        return []

    return [
        item
        for item in value
        if isinstance(item, dict)
    ]


def _as_float_list(
    value: Any,
) -> List[float]:
    """
    Convert numeric values to floats.
    """

    if not isinstance(value, list):
        return []

    result = []

    for item in value:

        try:
            result.append(
                float(item)
            )
        except (
            TypeError,
            ValueError,
        ):
            continue

    return result


# ============================================================================
# DEFAULT MANAGER
# ============================================================================


default_context_manager = ContextManager()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


def create_context(
    **kwargs: Any,
) -> CopilotContext:
    """
    Convenience wrapper around ContextManager.create().
    """

    return default_context_manager.create(
        **kwargs
    )


def context_to_llm(
    context: CopilotContext,
) -> Dict[str, Any]:
    """
    Convert CopilotContext into an LLM-safe dictionary.
    """

    return default_context_manager.to_llm_context(
        context
    )


def add_user_message(
    context: CopilotContext,
    message: str,
) -> CopilotContext:
    """
    Add a recruiter message to context.
    """

    return default_context_manager.add_user_message(
        context,
        message,
    )


def add_assistant_message(
    context: CopilotContext,
    message: str,
) -> CopilotContext:
    """
    Add an assistant message to context.
    """

    return default_context_manager.add_assistant_message(
        context,
        message,
    )


def add_rag_results(
    context: CopilotContext,
    documents: List[Dict[str, Any]],
    query: Optional[str] = None,
) -> CopilotContext:
    """
    Add RAG retrieval results to context.
    """

    return default_context_manager.add_rag_results(
        context,
        documents,
        query,
    )