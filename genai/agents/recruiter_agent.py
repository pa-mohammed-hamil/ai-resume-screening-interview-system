# Project scaffold file
"""
genai/agents/recruiter_agent.py

AI Recruiter Agent
------------------
Responsible for assisting recruiters with:
- Candidate screening
- Candidate ranking explanations
- Resume/job matching insights
- Interview summaries
- Skill-gap analysis
- Hiring recommendations
- Recruiter questions using available context

The agent is intentionally kept independent from FastAPI routes and
database implementation. The service/API layer should provide the
candidate/job/interview context.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from genai.llm.client import LLMClient
from genai.llm.model_config import ModelConfig
from genai.llm.prompts import RECRUITER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


@dataclass
class RecruiterContext:
    """Context supplied to the recruiter agent."""

    job: Optional[Dict[str, Any]] = None
    candidates: List[Dict[str, Any]] = field(default_factory=list)
    selected_candidate: Optional[Dict[str, Any]] = None
    interview: Optional[Dict[str, Any]] = None
    resume: Optional[Dict[str, Any]] = None
    additional_context: Optional[str] = None


@dataclass
class RecruiterResponse:
    """Standard response returned by the recruiter agent."""

    answer: str
    action: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RecruiterAgent:
    """
    AI agent for recruiter assistance.

    Example:

        agent = RecruiterAgent()

        response = await agent.ask(
            "Who are the strongest candidates for this Python role?",
            context=RecruiterContext(
                job=job_data,
                candidates=candidate_data,
            ),
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

    async def ask(
        self,
        query: str,
        context: Optional[RecruiterContext] = None,
    ) -> RecruiterResponse:
        """
        Answer a recruiter question using the supplied context.
        """

        if not query or not query.strip():
            raise ValueError("Recruiter query cannot be empty.")

        context = context or RecruiterContext()

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
            logger.exception("Recruiter agent failed: %s", exc)

            return RecruiterResponse(
                answer=(
                    "I couldn't process the recruiter request right now. "
                    "Please try again."
                ),
                warnings=["Recruiter AI service temporarily unavailable."],
                metadata={"error": str(exc)},
            )

    async def screen_candidates(
        self,
        job: Dict[str, Any],
        candidates: List[Dict[str, Any]],
    ) -> RecruiterResponse:
        """
        Screen a group of candidates against a job description.
        """

        context = RecruiterContext(
            job=job,
            candidates=candidates,
        )

        query = (
            "Screen these candidates against the job requirements. "
            "Identify the strongest candidates, explain the evidence, "
            "highlight skill gaps, and identify candidates who require "
            "manual review. Do not make decisions using protected "
            "characteristics."
        )

        return await self.ask(
            query=query,
            context=context,
        )

    async def rank_candidates(
        self,
        job: Dict[str, Any],
        candidates: List[Dict[str, Any]],
    ) -> RecruiterResponse:
        """
        Generate an explainable ranking analysis.

        This should complement, not replace, the deterministic ranking
        system in ai/ranking/.
        """

        context = RecruiterContext(
            job=job,
            candidates=candidates,
        )

        query = (
            "Analyze the candidates for this role and provide an "
            "explainable ranking based only on job-relevant evidence. "
            "For each candidate, explain strengths, weaknesses, "
            "missing requirements, and confidence in the assessment."
        )

        return await self.ask(
            query=query,
            context=context,
        )

    async def compare_candidates(
        self,
        job: Dict[str, Any],
        candidates: List[Dict[str, Any]],
    ) -> RecruiterResponse:
        """
        Compare candidates side-by-side.
        """

        if len(candidates) < 2:
            raise ValueError(
                "At least two candidates are required for comparison."
            )

        context = RecruiterContext(
            job=job,
            candidates=candidates,
        )

        query = (
            "Compare these candidates for the given role. "
            "Create a concise recruiter-friendly comparison covering "
            "skills, experience, education, job requirements, gaps, "
            "and interview evidence when available."
        )

        return await self.ask(
            query=query,
            context=context,
        )

    async def analyze_candidate(
        self,
        candidate: Dict[str, Any],
        job: Optional[Dict[str, Any]] = None,
        interview: Optional[Dict[str, Any]] = None,
        resume: Optional[Dict[str, Any]] = None,
    ) -> RecruiterResponse:
        """
        Generate a detailed candidate analysis.
        """

        context = RecruiterContext(
            job=job,
            candidates=[candidate],
            selected_candidate=candidate,
            interview=interview,
            resume=resume,
        )

        query = (
            "Provide a detailed recruiter analysis of this candidate. "
            "Summarize relevant qualifications, strengths, concerns, "
            "skill gaps, job fit, interview performance if available, "
            "and suggested next steps."
        )

        return await self.ask(
            query=query,
            context=context,
        )

    async def summarize_interview(
        self,
        candidate: Dict[str, Any],
        interview: Dict[str, Any],
    ) -> RecruiterResponse:
        """
        Summarize interview performance for recruiter review.
        """

        context = RecruiterContext(
            candidates=[candidate],
            selected_candidate=candidate,
            interview=interview,
        )

        query = (
            "Summarize this candidate's interview for a recruiter. "
            "Include technical performance, communication, confidence, "
            "strengths, weaknesses, unanswered concerns, and recommended "
            "follow-up questions."
        )

        return await self.ask(
            query=query,
            context=context,
        )

    async def identify_skill_gaps(
        self,
        job: Dict[str, Any],
        candidate: Dict[str, Any],
    ) -> RecruiterResponse:
        """
        Identify missing or weak job-relevant skills.
        """

        context = RecruiterContext(
            job=job,
            candidates=[candidate],
            selected_candidate=candidate,
        )

        query = (
            "Identify the candidate's skill gaps relative to this job. "
            "Separate critical missing requirements from skills that "
            "could reasonably be learned after hiring."
        )

        return await self.ask(
            query=query,
            context=context,
        )

    async def generate_interview_questions(
        self,
        job: Dict[str, Any],
        candidate: Dict[str, Any],
        count: int = 5,
    ) -> RecruiterResponse:
        """
        Generate targeted interview questions.
        """

        count = max(1, min(count, 20))

        context = RecruiterContext(
            job=job,
            candidates=[candidate],
            selected_candidate=candidate,
        )

        query = (
            f"Generate {count} targeted interview questions for this "
            "candidate and job. Focus on validating important skills, "
            "experience claims, and job requirements. Include a short "
            "reason why each question matters."
        )

        return await self.ask(
            query=query,
            context=context,
        )

    async def hiring_recommendation(
        self,
        job: Dict[str, Any],
        candidate: Dict[str, Any],
        interview: Optional[Dict[str, Any]] = None,
    ) -> RecruiterResponse:
        """
        Produce a structured hiring recommendation.

        The recommendation is advisory and should not be treated as an
        automated employment decision.
        """

        context = RecruiterContext(
            job=job,
            candidates=[candidate],
            selected_candidate=candidate,
            interview=interview,
        )

        query = (
            "Provide an evidence-based hiring recommendation for this "
            "candidate. Use only job-related qualifications and available "
            "interview evidence. Clearly separate evidence from inference. "
            "Return one of: Strong Consideration, Consider, or Needs Review. "
            "Explain the recommendation and list any concerns requiring "
            "human verification."
        )

        response = await self.ask(
            query=query,
            context=context,
        )

        response.warnings.append(
            "AI recommendations are advisory and require human recruiter review."
        )

        return response

    async def _generate(self, prompt: str) -> Any:
        """
        Call the configured LLM client.

        Supports clients exposing either `generate()` or `complete()`.
        """

        if hasattr(self.llm, "generate"):
            return await self.llm.generate(
                prompt=prompt,
                system_prompt=RECRUITER_SYSTEM_PROMPT,
            )

        if hasattr(self.llm, "complete"):
            return await self.llm.complete(
                prompt=prompt,
                system_prompt=RECRUITER_SYSTEM_PROMPT,
            )

        raise AttributeError(
            "LLMClient must implement generate() or complete()."
        )

    def _build_prompt(
        self,
        query: str,
        context: RecruiterContext,
    ) -> str:
        """Build a safe, structured recruiter prompt."""

        context_payload = {
            "job": context.job,
            "candidates": context.candidates,
            "selected_candidate": context.selected_candidate,
            "interview": context.interview,
            "resume": context.resume,
            "additional_context": context.additional_context,
        }

        serialized_context = json.dumps(
            context_payload,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

        return f"""
RECRUITER REQUEST
=================
{query}

RECRUITMENT CONTEXT
===================
{serialized_context}

INSTRUCTIONS
============
1. Use only the supplied information.
2. Prioritize job-related qualifications.
3. Do not infer protected characteristics.
4. Do not use name, gender, age, race, religion, nationality,
   disability, marital status, or other protected characteristics
   as selection criteria.
5. Clearly distinguish facts from interpretation.
6. Explain recommendations using evidence.
7. Identify missing information instead of inventing it.
8. Flag cases that require human review.
9. Do not make a final employment decision on behalf of the recruiter.
10. Keep the response concise but useful.

Return JSON with this structure:

{{
    "answer": "main recruiter-facing response",
    "action": "recommended next action or null",
    "recommendations": [
        "recommendation 1"
    ],
    "evidence": [
        "supporting evidence 1"
    ],
    "warnings": [
        "warning or missing information"
    ]
}}
""".strip()

    def _parse_response(
        self,
        result: Any,
        query: str,
    ) -> RecruiterResponse:
        """Normalize different LLM response formats."""

        text = self._extract_text(result)

        if not text:
            return RecruiterResponse(
                answer="The AI model returned an empty response.",
                warnings=["Empty model response."],
            )

        parsed = self._try_parse_json(text)

        if isinstance(parsed, dict):
            return RecruiterResponse(
                answer=str(
                    parsed.get(
                        "answer",
                        "No answer was generated.",
                    )
                ),
                action=parsed.get("action"),
                recommendations=self._as_string_list(
                    parsed.get("recommendations", [])
                ),
                evidence=self._as_string_list(
                    parsed.get("evidence", [])
                ),
                warnings=self._as_string_list(
                    parsed.get("warnings", [])
                ),
                metadata={
                    "query": query,
                    "structured_response": True,
                },
            )

        return RecruiterResponse(
            answer=text,
            metadata={
                "query": query,
                "structured_response": False,
            },
        )

    @staticmethod
    def _extract_text(result: Any) -> str:
        """Extract text from common LLM response formats."""

        if result is None:
            return ""

        if isinstance(result, str):
            return result.strip()

        if isinstance(result, dict):
            for key in ("text", "content", "response", "output"):
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
    def _try_parse_json(text: str) -> Optional[Dict[str, Any]]:
        """Safely parse JSON returned by an LLM."""

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
    def _as_string_list(value: Any) -> List[str]:
        """Convert an arbitrary value to a list of strings."""

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