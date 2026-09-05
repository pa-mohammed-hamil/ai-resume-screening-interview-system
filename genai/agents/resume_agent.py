# Project scaffold file
"""
genai/agents/resume_agent.py

AI Resume Agent
---------------
Responsible for:
- Resume analysis
- Resume summarization
- Skill identification
- Job/resume matching
- Skill-gap analysis
- ATS optimization
- Resume improvement suggestions
- Resume section rewriting
- Recruiter/candidate explanations

The agent does not directly access the database.
The backend service layer should provide the required context.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from genai.llm.client import LLMClient
from genai.llm.model_config import ModelConfig
from genai.llm.prompts import RESUME_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


@dataclass
class ResumeContext:
    """Context supplied to the resume agent."""

    resume: Optional[Dict[str, Any]] = None
    job: Optional[Dict[str, Any]] = None
    extracted_skills: List[str] = field(default_factory=list)
    matching_result: Optional[Dict[str, Any]] = None
    ats_score: Optional[float] = None
    skill_gaps: List[str] = field(default_factory=list)
    additional_context: Optional[str] = None


@dataclass
class ResumeResponse:
    """Standard response returned by the resume agent."""

    answer: str
    suggestions: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResumeAgent:
    """
    AI agent for resume analysis and optimization.

    Example:

        agent = ResumeAgent()

        response = await agent.analyze(
            ResumeContext(
                resume=resume_data,
                job=job_data,
            )
        )
    """

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        model_config: Optional[ModelConfig] = None,
    ) -> None:
        self.model_config = model_config or ModelConfig()

        self.llm = llm_client or LLMClient(
            model_config=self.model_config
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def analyze(
        self,
        context: ResumeContext,
    ) -> ResumeResponse:
        """
        Perform a complete resume analysis.
        """

        query = (
            "Analyze this resume comprehensively. "
            "Identify strengths, weaknesses, relevant skills, "
            "missing information, ATS issues, and practical "
            "improvements."
        )

        return await self.ask(
            query=query,
            context=context,
        )

    async def ask(
        self,
        query: str,
        context: Optional[ResumeContext] = None,
    ) -> ResumeResponse:
        """
        Answer a resume-related request using supplied context.
        """

        if not query or not query.strip():
            raise ValueError("Resume query cannot be empty.")

        context = context or ResumeContext()

        prompt = self._build_prompt(
            query=query.strip(),
            context=context,
        )

        try:
            result = await self._generate(prompt)

            return self._parse_response(
                result=result,
                query=query,
            )

        except Exception as exc:
            logger.exception(
                "Resume agent failed: %s",
                exc,
            )

            return ResumeResponse(
                answer=(
                    "I couldn't analyze the resume right now. "
                    "Please try again."
                ),
                warnings=[
                    "Resume AI service temporarily unavailable."
                ],
                metadata={
                    "error": str(exc),
                },
            )

    async def summarize(
        self,
        resume: Dict[str, Any],
    ) -> ResumeResponse:
        """
        Generate a concise professional resume summary.
        """

        context = ResumeContext(
            resume=resume,
        )

        query = (
            "Create a concise professional summary of this resume. "
            "Highlight the candidate's experience, strongest skills, "
            "technical areas, education, and notable achievements."
        )

        return await self.ask(
            query=query,
            context=context,
        )

    async def extract_skills(
        self,
        resume: Dict[str, Any],
    ) -> ResumeResponse:
        """
        Identify technical and professional skills.

        Note:
        Deterministic skill extraction should still be performed by:
            ai/skill_intelligence/skill_extractor.py
        This method provides an LLM-based interpretation.
        """

        context = ResumeContext(
            resume=resume,
        )

        query = (
            "Identify all relevant skills in this resume. "
            "Separate technical skills, programming languages, "
            "frameworks, databases, cloud technologies, tools, "
            "soft skills, and domain knowledge. "
            "Do not invent skills that are not supported by the resume."
        )

        return await self.ask(
            query=query,
            context=context,
        )

    async def match_job(
        self,
        resume: Dict[str, Any],
        job: Dict[str, Any],
    ) -> ResumeResponse:
        """
        Analyze resume fit against a job description.
        """

        context = ResumeContext(
            resume=resume,
            job=job,
        )

        query = (
            "Compare this resume against the job description. "
            "Identify matching qualifications, missing requirements, "
            "relevant experience, transferable skills, and potential "
            "concerns. Explain the match using evidence from both "
            "documents."
        )

        return await self.ask(
            query=query,
            context=context,
        )

    async def identify_skill_gaps(
        self,
        resume: Dict[str, Any],
        job: Dict[str, Any],
    ) -> ResumeResponse:
        """
        Identify job-specific skill gaps.
        """

        context = ResumeContext(
            resume=resume,
            job=job,
        )

        query = (
            "Identify the candidate's skill gaps relative to this job. "
            "Classify gaps into critical requirements, preferred skills, "
            "and skills that can reasonably be learned."
        )

        return await self.ask(
            query=query,
            context=context,
        )

    async def optimize_ats(
        self,
        resume: Dict[str, Any],
        job: Optional[Dict[str, Any]] = None,
    ) -> ResumeResponse:
        """
        Generate ATS optimization recommendations.
        """

        context = ResumeContext(
            resume=resume,
            job=job,
        )

        query = (
            "Review this resume for ATS compatibility. "
            "Identify missing job-relevant keywords, unclear sections, "
            "weak formatting signals, vague statements, and areas that "
            "could be improved for machine-readable screening."
        )

        return await self.ask(
            query=query,
            context=context,
        )

    async def improve_content(
        self,
        resume: Dict[str, Any],
        job: Optional[Dict[str, Any]] = None,
    ) -> ResumeResponse:
        """
        Suggest improvements to resume content.
        """

        context = ResumeContext(
            resume=resume,
            job=job,
        )

        query = (
            "Improve the content of this resume while preserving "
            "the candidate's factual information. "
            "Make experience descriptions clearer, more concise, "
            "achievement-oriented, and relevant to the target job."
        )

        return await self.ask(
            query=query,
            context=context,
        )

    async def optimize_keywords(
        self,
        resume: Dict[str, Any],
        job: Dict[str, Any],
    ) -> ResumeResponse:
        """
        Find useful job-relevant keywords.
        """

        context = ResumeContext(
            resume=resume,
            job=job,
        )

        query = (
            "Identify important keywords and phrases from this job "
            "description that are relevant to the candidate. "
            "Explain where each keyword could naturally be incorporated "
            "into the resume. Never recommend keyword stuffing."
        )

        return await self.ask(
            query=query,
            context=context,
        )

    async def rewrite_section(
        self,
        section_name: str,
        section_content: str,
        job: Optional[Dict[str, Any]] = None,
    ) -> ResumeResponse:
        """
        Rewrite one resume section.
        """

        if not section_name.strip():
            raise ValueError(
                "Resume section name cannot be empty."
            )

        if not section_content.strip():
            raise ValueError(
                "Resume section content cannot be empty."
            )

        context = ResumeContext(
            job=job,
        )

        query = f"""
Rewrite the following resume section:

SECTION:
{section_name}

ORIGINAL CONTENT:
{section_content}

Requirements:
- Preserve factual information.
- Do not invent employers, projects, skills, dates, metrics,
  certifications, or achievements.
- Use concise professional language.
- Prefer measurable achievements when metrics already exist.
- Optimize for clarity and job relevance.
""".strip()

        return await self.ask(
            query=query,
            context=context,
        )

    async def generate_bullet_points(
        self,
        experience: str,
        job: Optional[Dict[str, Any]] = None,
        count: int = 5,
    ) -> ResumeResponse:
        """
        Generate stronger experience bullet points.
        """

        count = max(1, min(count, 10))

        context = ResumeContext(
            job=job,
        )

        query = f"""
Convert the following experience into {count} strong resume
bullet points:

{experience}

Rules:
- Preserve the original facts.
- Do not fabricate metrics.
- Do not invent technologies.
- Use action-oriented language.
- Emphasize impact when supported by the source.
""".strip()

        return await self.ask(
            query=query,
            context=context,
        )

    async def explain_score(
        self,
        resume: Dict[str, Any],
        score: float,
        job: Optional[Dict[str, Any]] = None,
        score_breakdown: Optional[Dict[str, Any]] = None,
    ) -> ResumeResponse:
        """
        Explain an existing ATS/matching score.

        The agent does not calculate the authoritative score.
        The scoring modules under ai/scoring/ should do that.
        """

        context = ResumeContext(
            resume=resume,
            job=job,
            ats_score=score,
            matching_result=score_breakdown,
        )

        query = (
            "Explain this resume score to a user in simple language. "
            "Describe what contributed positively, what reduced the "
            "score, and what practical changes could improve it. "
            "Do not change or recalculate the supplied score."
        )

        return await self.ask(
            query=query,
            context=context,
        )

    # ------------------------------------------------------------------
    # LLM
    # ------------------------------------------------------------------

    async def _generate(
        self,
        prompt: str,
    ) -> Any:
        """
        Call the configured LLM client.

        Supports clients exposing either generate() or complete().
        """

        if hasattr(self.llm, "generate"):
            return await self.llm.generate(
                prompt=prompt,
                system_prompt=RESUME_SYSTEM_PROMPT,
            )

        if hasattr(self.llm, "complete"):
            return await self.llm.complete(
                prompt=prompt,
                system_prompt=RESUME_SYSTEM_PROMPT,
            )

        raise AttributeError(
            "LLMClient must implement generate() or complete()."
        )

    # ------------------------------------------------------------------
    # Prompt
    # ------------------------------------------------------------------

    def _build_prompt(
        self,
        query: str,
        context: ResumeContext,
    ) -> str:
        """
        Build a structured prompt for the LLM.
        """

        context_payload = {
            "resume": context.resume,
            "job": context.job,
            "extracted_skills": context.extracted_skills,
            "matching_result": context.matching_result,
            "ats_score": context.ats_score,
            "skill_gaps": context.skill_gaps,
            "additional_context": context.additional_context,
        }

        serialized_context = json.dumps(
            context_payload,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

        return f"""
RESUME AI REQUEST
=================
{query}

RESUME/JOB CONTEXT
==================
{serialized_context}

INSTRUCTIONS
============
1. Use only the supplied information.
2. Never fabricate resume facts.
3. Never invent employers, degrees, certifications, skills,
   job titles, dates, projects, achievements, or metrics.
4. Preserve factual accuracy when rewriting content.
5. Separate facts from suggestions.
6. Focus on job-relevant qualifications.
7. Avoid protected characteristics and unrelated personal information.
8. Do not recommend keyword stuffing.
9. Identify uncertainty when information is incomplete.
10. Keep recommendations practical and actionable.

Return JSON using this structure:

{{
    "answer": "main response",
    "suggestions": [
        "suggestion 1",
        "suggestion 2"
    ],
    "strengths": [
        "strength 1"
    ],
    "weaknesses": [
        "weakness 1"
    ],
    "missing_skills": [
        "skill 1"
    ],
    "keywords": [
        "keyword 1"
    ],
    "warnings": [
        "warning 1"
    ]
}}
""".strip()

    # ------------------------------------------------------------------
    # Response parsing
    # ------------------------------------------------------------------

    def _parse_response(
        self,
        result: Any,
        query: str,
    ) -> ResumeResponse:
        """
        Normalize LLM output into ResumeResponse.
        """

        text = self._extract_text(result)

        if not text:
            return ResumeResponse(
                answer="The AI model returned an empty response.",
                warnings=["Empty model response."],
            )

        parsed = self._try_parse_json(text)

        if isinstance(parsed, dict):
            return ResumeResponse(
                answer=str(
                    parsed.get(
                        "answer",
                        "No answer was generated.",
                    )
                ),
                suggestions=self._as_string_list(
                    parsed.get("suggestions", [])
                ),
                strengths=self._as_string_list(
                    parsed.get("strengths", [])
                ),
                weaknesses=self._as_string_list(
                    parsed.get("weaknesses", [])
                ),
                missing_skills=self._as_string_list(
                    parsed.get("missing_skills", [])
                ),
                keywords=self._as_string_list(
                    parsed.get("keywords", [])
                ),
                warnings=self._as_string_list(
                    parsed.get("warnings", [])
                ),
                metadata={
                    "query": query,
                    "structured_response": True,
                },
            )

        return ResumeResponse(
            answer=text,
            metadata={
                "query": query,
                "structured_response": False,
            },
        )

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

            choices = result.get("choices")

            if isinstance(choices, list) and choices:
                first = choices[0]

                if isinstance(first, dict):
                    message = first.get("message")

                    if isinstance(message, dict):
                        content = message.get("content")

                        if isinstance(content, str):
                            return content.strip()

                    content = first.get("text")

                    if isinstance(content, str):
                        return content.strip()

        return str(result).strip()

    @staticmethod
    def _try_parse_json(
        text: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Safely parse JSON returned by an LLM.
        """

        cleaned = text.strip()

        if cleaned.startswith("```"):
            lines = cleaned.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            cleaned = "\n".join(lines).strip()

        try:
            parsed = json.loads(cleaned)

            if isinstance(parsed, dict):
                return parsed

        except json.JSONDecodeError:
            pass

        return None

    @staticmethod
    def _as_string_list(
        value: Any,
    ) -> List[str]:
        """
        Convert arbitrary values to a list of strings.
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