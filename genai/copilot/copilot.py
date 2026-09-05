# Project scaffold file
"""
genai/copilot/copilot.py

Recruiter Copilot
=================

Central AI assistant for recruiters.

Responsibilities:

- Understand recruiter requests
- Use recruiter/candidate/job context
- Answer recruitment questions
- Delegate specialized tasks to AI agents
- Generate recruiter recommendations
- Prepare interview questions
- Explain resume and candidate information
- Assist with jobs and hiring workflows
- Use RAG context when available
- Suggest actions without performing unauthorized actions

Architecture:

    Frontend
        ↓
    backend/app/api/copilot.py
        ↓
    backend/app/services/copilot_service.py
        ↓
    genai/copilot/copilot.py
        ↓
    ┌───────────────┬────────────────┬─────────────────┐
    │ Recruiter     │ Resume         │ Interview       │
    │ Agent         │ Agent          │ Agent           │
    └───────────────┴────────────────┴─────────────────┘
        ↓
    LLM / RAG
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from genai.llm.client import LLMClient
from genai.llm.model_config import ModelConfig
from genai.llm.prompts import COPILOT_SYSTEM_PROMPT

from genai.agents.recruiter_agent import RecruiterAgent
from genai.agents.resume_agent import ResumeAgent
from genai.agents.interview_agent import InterviewAgent
from genai.agents.analytics_agent import AnalyticsAgent


logger = logging.getLogger(__name__)


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class CopilotContext:
    """
    Context available to the recruiter copilot.
    """

    user: Optional[Dict[str, Any]] = None

    organization: Optional[Dict[str, Any]] = None

    job: Optional[Dict[str, Any]] = None

    candidate: Optional[Dict[str, Any]] = None

    resume: Optional[Dict[str, Any]] = None

    interview: Optional[Dict[str, Any]] = None

    analytics: Optional[Dict[str, Any]] = None

    search_results: List[Dict[str, Any]] = field(
        default_factory=list
    )

    rag_context: List[Dict[str, Any]] = field(
        default_factory=list
    )

    conversation_history: List[Dict[str, Any]] = field(
        default_factory=list
    )

    additional_context: Optional[str] = None


@dataclass
class CopilotResponse:
    """
    Standardized response from the recruiter copilot.
    """

    answer: str

    intent: str = "general"

    suggestions: List[str] = field(
        default_factory=list
    )

    actions: List[Dict[str, Any]] = field(
        default_factory=list
    )

    insights: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================================
# RECRUITER COPILOT
# ============================================================================


class RecruiterCopilot:
    """
    Central AI assistant for recruiter workflows.

    Example:

        copilot = RecruiterCopilot()

        response = await copilot.ask(
            "Which candidates should I interview?",
            context=context,
        )
    """

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        model_config: Optional[ModelConfig] = None,
        recruiter_agent: Optional[RecruiterAgent] = None,
        resume_agent: Optional[ResumeAgent] = None,
        interview_agent: Optional[InterviewAgent] = None,
        analytics_agent: Optional[AnalyticsAgent] = None,
    ) -> None:

        self.model_config = model_config or ModelConfig()

        self.llm = llm_client or LLMClient(
            model_config=self.model_config
        )

        self.recruiter_agent = (
            recruiter_agent or RecruiterAgent(
                llm_client=self.llm,
                model_config=self.model_config,
            )
        )

        self.resume_agent = (
            resume_agent or ResumeAgent(
                llm_client=self.llm,
                model_config=self.model_config,
            )
        )

        self.interview_agent = (
            interview_agent or InterviewAgent(
                llm_client=self.llm,
                model_config=self.model_config,
            )
        )

        self.analytics_agent = (
            analytics_agent or AnalyticsAgent(
                llm_client=self.llm,
                model_config=self.model_config,
            )
        )

    # ========================================================================
    # MAIN ASK
    # ========================================================================

    async def ask(
        self,
        message: str,
        context: Optional[CopilotContext] = None,
    ) -> CopilotResponse:
        """
        Main entry point for recruiter requests.
        """

        if not message or not message.strip():
            raise ValueError(
                "Copilot message cannot be empty."
            )

        context = context or CopilotContext()

        intent = self._detect_intent(
            message
        )

        try:

            return await self._route_request(
                message=message.strip(),
                intent=intent,
                context=context,
            )

        except Exception as exc:

            logger.exception(
                "Recruiter copilot failed: %s",
                exc,
            )

            return CopilotResponse(
                answer=(
                    "I couldn't process that request right now. "
                    "Please try again."
                ),
                intent=intent,
                warnings=[
                    "Copilot service is temporarily unavailable."
                ],
                metadata={
                    "error": str(exc),
                },
            )

    # ========================================================================
    # REQUEST ROUTING
    # ========================================================================

    async def _route_request(
        self,
        message: str,
        intent: str,
        context: CopilotContext,
    ) -> CopilotResponse:
        """
        Route recruiter requests to the appropriate specialist agent.
        """

        if intent == "resume":
            return await self._handle_resume(
                message,
                context,
            )

        if intent == "interview":
            return await self._handle_interview(
                message,
                context,
            )

        if intent == "analytics":
            return await self._handle_analytics(
                message,
                context,
            )

        if intent == "candidate":
            return await self._handle_candidate(
                message,
                context,
            )

        if intent == "job":
            return await self._handle_job(
                message,
                context,
            )

        if intent == "recommendation":
            return await self._handle_recommendation(
                message,
                context,
            )

        return await self._handle_general(
            message,
            context,
        )

    # ========================================================================
    # RESUME REQUEST
    # ========================================================================

    async def _handle_resume(
        self,
        message: str,
        context: CopilotContext,
    ) -> CopilotResponse:
        """
        Handle resume-related requests.
        """

        result = await self.resume_agent.ask(
            query=message,
            context=self._resume_context(context),
        )

        return CopilotResponse(
            answer=result.answer,
            intent="resume",
            suggestions=result.recommendations,
            insights=result.strengths,
            warnings=result.warnings,
            metadata={
                "agent": "resume_agent",
            },
        )

    # ========================================================================
    # INTERVIEW REQUEST
    # ========================================================================

    async def _handle_interview(
        self,
        message: str,
        context: CopilotContext,
    ) -> CopilotResponse:
        """
        Handle interview-related requests.
        """

        from genai.agents.interview_agent import InterviewContext

        interview_context = InterviewContext(
            candidate=context.candidate,
            resume=context.resume,
            job=context.job,
            interview=context.interview,
        )

        result = await self.interview_agent.ask(
            query=message,
            context=interview_context,
        )

        return CopilotResponse(
            answer=result.answer,
            intent="interview",
            suggestions=result.recommendations,
            insights=result.strengths,
            actions=[
                {
                    "type": "interview_questions",
                    "questions": result.questions,
                }
            ]
            if result.questions
            else [],
            warnings=result.warnings,
            metadata={
                "agent": "interview_agent",
            },
        )

    # ========================================================================
    # ANALYTICS REQUEST
    # ========================================================================

    async def _handle_analytics(
        self,
        message: str,
        context: CopilotContext,
    ) -> CopilotResponse:
        """
        Handle analytics requests.
        """

        from genai.agents.analytics_agent import AnalyticsContext

        analytics_context = AnalyticsContext(
            organization=context.organization,
            jobs=context.search_results,
            candidates=(
                [context.candidate]
                if context.candidate
                else []
            ),
            interviews=(
                [context.interview]
                if context.interview
                else []
            ),
            metrics=context.analytics or {},
            rag_context if False else {},
        )

        # Remove accidental unsupported field construction by creating
        # a clean analytics context.
        analytics_context = AnalyticsContext(
            organization=context.organization,
            jobs=context.search_results,
            candidates=(
                [context.candidate]
                if context.candidate
                else []
            ),
            interviews=(
                [context.interview]
                if context.interview
                else []
            ),
            metrics=context.analytics or {},
            additional_context=context.additional_context,
        )

        result = await self.analytics_agent.ask(
            query=message,
            context=analytics_context,
        )

        return CopilotResponse(
            answer=result.answer,
            intent="analytics",
            suggestions=result.recommendations,
            insights=result.insights,
            warnings=result.warnings,
            metadata={
                "agent": "analytics_agent",
            },
        )

    # ========================================================================
    # CANDIDATE REQUEST
    # ========================================================================

    async def _handle_candidate(
        self,
        message: str,
        context: CopilotContext,
    ) -> CopilotResponse:
        """
        Handle candidate-related requests.
        """

        result = await self.recruiter_agent.ask(
            query=message,
            context=self._recruiter_context(context),
        )

        return CopilotResponse(
            answer=result.answer,
            intent="candidate",
            suggestions=result.recommendations,
            insights=result.insights,
            actions=result.actions,
            warnings=result.warnings,
            metadata={
                "agent": "recruiter_agent",
            },
        )

    # ========================================================================
    # JOB REQUEST
    # ========================================================================

    async def _handle_job(
        self,
        message: str,
        context: CopilotContext,
    ) -> CopilotResponse:
        """
        Handle job-related requests.
        """

        result = await self.recruiter_agent.ask(
            query=message,
            context=self._recruiter_context(context),
        )

        return CopilotResponse(
            answer=result.answer,
            intent="job",
            suggestions=result.recommendations,
            insights=result.insights,
            actions=result.actions,
            warnings=result.warnings,
            metadata={
                "agent": "recruiter_agent",
            },
        )

    # ========================================================================
    # RECOMMENDATION REQUEST
    # ========================================================================

    async def _handle_recommendation(
        self,
        message: str,
        context: CopilotContext,
    ) -> CopilotResponse:
        """
        Generate recruiter recommendations.
        """

        result = await self.recruiter_agent.ask(
            query=message,
            context=self._recruiter_context(context),
        )

        return CopilotResponse(
            answer=result.answer,
            intent="recommendation",
            suggestions=result.recommendations,
            insights=result.insights,
            actions=result.actions,
            warnings=result.warnings,
            metadata={
                "agent": "recruiter_agent",
            },
        )

    # ========================================================================
    # GENERAL REQUEST
    # ========================================================================

    async def _handle_general(
        self,
        message: str,
        context: CopilotContext,
    ) -> CopilotResponse:
        """
        Handle general recruiter questions directly with the LLM.
        """

        prompt = self._build_prompt(
            message=message,
            context=context,
        )

        result = await self._generate(
            prompt
        )

        return self._parse_response(
            result=result,
            intent="general",
        )

    # ========================================================================
    # INTENT DETECTION
    # ========================================================================

    def _detect_intent(
        self,
        message: str,
    ) -> str:
        """
        Lightweight deterministic intent detection.

        This avoids making a separate LLM call for every request.
        """

        text = message.lower()

        resume_keywords = [
            "resume",
            "cv",
            "ats",
            "skill",
            "experience",
            "education",
            "resume score",
        ]

        interview_keywords = [
            "interview",
            "question",
            "technical question",
            "behavioral",
            "follow-up",
            "interview score",
        ]

        analytics_keywords = [
            "analytics",
            "dashboard",
            "metric",
            "statistics",
            "funnel",
            "conversion",
            "time to hire",
            "trend",
            "report",
        ]

        candidate_keywords = [
            "candidate",
            "applicant",
            "shortlist",
            "shortlisted",
            "rank",
            "ranking",
            "compare candidates",
        ]

        job_keywords = [
            "job",
            "job description",
            "jd",
            "vacancy",
            "position",
            "role",
            "hiring",
        ]

        recommendation_keywords = [
            "recommend",
            "recommendation",
            "suggest",
            "what should",
            "what do you recommend",
            "next step",
        ]

        if any(
            keyword in text
            for keyword in interview_keywords
        ):
            return "interview"

        if any(
            keyword in text
            for keyword in analytics_keywords
        ):
            return "analytics"

        if any(
            keyword in text
            for keyword in candidate_keywords
        ):
            return "candidate"

        if any(
            keyword in text
            for keyword in resume_keywords
        ):
            return "resume"

        if any(
            keyword in text
            for keyword in job_keywords
        ):
            return "job"

        if any(
            keyword in text
            for keyword in recommendation_keywords
        ):
            return "recommendation"

        return "general"

    # ========================================================================
    # CONTEXT CONVERTERS
    # ========================================================================

    @staticmethod
    def _resume_context(
        context: CopilotContext,
    ) -> Any:
        """
        Convert CopilotContext into ResumeAgent-compatible context.
        """

        from genai.agents.resume_agent import ResumeContext

        return ResumeContext(
            candidate=context.candidate,
            resume=context.resume,
            job=context.job,
            additional_context=context.additional_context,
        )

    @staticmethod
    def _recruiter_context(
        context: CopilotContext,
    ) -> Any:
        """
        Convert CopilotContext into RecruiterAgent-compatible context.
        """

        try:

            from genai.agents.recruiter_agent import RecruiterContext

            return RecruiterContext(
                user=context.user,
                organization=context.organization,
                job=context.job,
                candidate=context.candidate,
                resume=context.resume,
                interview=context.interview,
                analytics=context.analytics,
                search_results=context.search_results,
                additional_context=context.additional_context,
            )

        except ImportError:

            return context

    # ========================================================================
    # LLM GENERATION
    # ========================================================================

    async def _generate(
        self,
        prompt: str,
    ) -> Any:
        """
        Call the configured LLM client.
        """

        if hasattr(self.llm, "generate"):

            return await self.llm.generate(
                prompt=prompt,
                system_prompt=COPILOT_SYSTEM_PROMPT,
            )

        if hasattr(self.llm, "complete"):

            return await self.llm.complete(
                prompt=prompt,
                system_prompt=COPILOT_SYSTEM_PROMPT,
            )

        raise AttributeError(
            "LLMClient must implement generate() or complete()."
        )

    # ========================================================================
    # PROMPT BUILDING
    # ========================================================================

    def _build_prompt(
        self,
        message: str,
        context: CopilotContext,
    ) -> str:
        """
        Build the recruiter copilot prompt.
        """

        payload = {
            "user": context.user,
            "organization": context.organization,
            "job": context.job,
            "candidate": context.candidate,
            "resume": context.resume,
            "interview": context.interview,
            "analytics": context.analytics,
            "search_results": context.search_results,
            "rag_context": context.rag_context,
            "conversation_history": context.conversation_history,
            "additional_context": context.additional_context,
        }

        serialized_context = json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

        return f"""
RECRUITER COPILOT REQUEST
=========================

Recruiter message:

{message}


CONTEXT
=======

{serialized_context}


INSTRUCTIONS
============

1. Answer the recruiter's request directly.
2. Use only information supplied in the context.
3. Never fabricate candidate information.
4. Never invent metrics.
5. Never infer protected characteristics.
6. Focus on job-related evidence.
7. Clearly identify uncertainty.
8. Provide actionable recommendations where appropriate.
9. Do not make final hiring decisions.
10. Do not claim an action was completed unless it actually was.
11. Do not expose confidential system information.
12. Respect candidate privacy.
13. Prefer concise recruiter-friendly responses.


RETURN JSON
===========

{{
    "answer": "main response",

    "intent": "general",

    "suggestions": [
        "suggestion 1"
    ],

    "actions": [
        {{
            "type": "action_type",
            "label": "action label",
            "parameters": {{}}
        }}
    ],

    "insights": [
        "insight 1"
    ],

    "warnings": [
        "warning 1"
    ]
}}
""".strip()

    # ========================================================================
    # RESPONSE PARSING
    # ========================================================================

    def _parse_response(
        self,
        result: Any,
        intent: str,
    ) -> CopilotResponse:
        """
        Convert an LLM result to CopilotResponse.
        """

        text = self._extract_text(
            result
        )

        if not text:

            return CopilotResponse(
                answer="No response was generated.",
                intent=intent,
                warnings=[
                    "Empty model response."
                ],
            )

        parsed = self._try_parse_json(
            text
        )

        if isinstance(parsed, dict):

            return CopilotResponse(
                answer=str(
                    parsed.get(
                        "answer",
                        text,
                    )
                ),
                intent=str(
                    parsed.get(
                        "intent",
                        intent,
                    )
                ),
                suggestions=self._as_string_list(
                    parsed.get(
                        "suggestions",
                        [],
                    )
                ),
                actions=self._as_dict_list(
                    parsed.get(
                        "actions",
                        [],
                    )
                ),
                insights=self._as_string_list(
                    parsed.get(
                        "insights",
                        [],
                    )
                ),
                warnings=self._as_string_list(
                    parsed.get(
                        "warnings",
                        [],
                    )
                ),
                metadata={
                    "structured_response": True,
                },
            )

        return CopilotResponse(
            answer=text,
            intent=intent,
            metadata={
                "structured_response": False,
            },
        )

    # ========================================================================
    # TEXT EXTRACTION
    # ========================================================================

    @staticmethod
    def _extract_text(
        result: Any,
    ) -> str:
        """
        Extract text from common LLM response formats.
        """

        if result is None:
            return ""

        if isinstance(result, str):
            return result.strip()

        if isinstance(result, dict):

            for key in (
                "text",
                "content",
                "response",
                "output",
            ):

                value = result.get(key)

                if isinstance(value, str):
                    return value.strip()

            choices = result.get(
                "choices"
            )

            if isinstance(choices, list) and choices:

                first = choices[0]

                if isinstance(first, dict):

                    message = first.get(
                        "message"
                    )

                    if isinstance(message, dict):

                        content = message.get(
                            "content"
                        )

                        if isinstance(content, str):
                            return content.strip()

                    content = first.get(
                        "text"
                    )

                    if isinstance(content, str):
                        return content.strip()

        return str(result).strip()

    # ========================================================================
    # JSON PARSING
    # ========================================================================

    @staticmethod
    def _try_parse_json(
        text: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Parse JSON returned by the LLM.
        """

        cleaned = text.strip()

        if cleaned.startswith("```"):

            lines = cleaned.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            cleaned = "\n".join(
                lines
            ).strip()

        try:

            parsed = json.loads(
                cleaned
            )

            if isinstance(parsed, dict):
                return parsed

        except json.JSONDecodeError:

            pass

        return None

    # ========================================================================
    # TYPE HELPERS
    # ========================================================================

    @staticmethod
    def _as_string_list(
        value: Any,
    ) -> List[str]:
        """
        Convert arbitrary values to strings.
        """

        if value is None:
            return []

        if isinstance(value, str):
            return [value]

        if isinstance(value, list):

            return [
                str(item)
                for item in value
                if item is not None
            ]

        return [str(value)]

    @staticmethod
    def _as_dict_list(
        value: Any,
    ) -> List[Dict[str, Any]]:
        """
        Convert arbitrary values to dictionaries.
        """

        if not isinstance(value, list):
            return []

        return [
            item
            for item in value
            if isinstance(item, dict)
        ]