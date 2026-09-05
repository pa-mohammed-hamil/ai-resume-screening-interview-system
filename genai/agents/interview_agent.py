"""
genai/agents/interview_agent.py

AI Interview Agent
------------------
Responsible for:
- Interview preparation
- Interview question generation
- Answer analysis
- Follow-up question generation
- Technical/behavioral evaluation assistance
- Interview summaries
- Candidate feedback
- Interview report explanations

The authoritative interview scoring and adaptive logic should remain
inside interview_engine/. This agent provides LLM-powered reasoning,
conversation, explanations, and assistance.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from genai.llm.client import LLMClient
from genai.llm.model_config import ModelConfig
from genai.llm.prompts import INTERVIEW_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


@dataclass
class InterviewContext:
    """Context supplied to the interview agent."""

    candidate: Optional[Dict[str, Any]] = None
    resume: Optional[Dict[str, Any]] = None
    job: Optional[Dict[str, Any]] = None
    interview: Optional[Dict[str, Any]] = None

    current_question: Optional[Dict[str, Any]] = None
    candidate_answer: Optional[str] = None

    previous_questions: List[Dict[str, Any]] = field(
        default_factory=list
    )

    previous_answers: List[Dict[str, Any]] = field(
        default_factory=list
    )

    evaluation: Optional[Dict[str, Any]] = None
    additional_context: Optional[str] = None


@dataclass
class InterviewResponse:
    """Standard response returned by the interview agent."""

    answer: str

    questions: List[Dict[str, Any]] = field(
        default_factory=list
    )

    strengths: List[str] = field(
        default_factory=list
    )

    weaknesses: List[str] = field(
        default_factory=list
    )

    recommendations: List[str] = field(
        default_factory=list
    )

    follow_up_questions: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


class InterviewAgent:
    """
    LLM-powered interview assistant.

    Example:

        agent = InterviewAgent()

        response = await agent.generate_questions(
            context=InterviewContext(
                candidate=candidate,
                resume=resume,
                job=job,
            ),
            count=5,
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

    # ================================================================
    # GENERAL INTERVIEW ASSISTANCE
    # ================================================================

    async def ask(
        self,
        query: str,
        context: Optional[InterviewContext] = None,
    ) -> InterviewResponse:
        """
        Answer an interview-related request.
        """

        if not query or not query.strip():
            raise ValueError(
                "Interview query cannot be empty."
            )

        context = context or InterviewContext()

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
                "Interview agent failed: %s",
                exc,
            )

            return InterviewResponse(
                answer=(
                    "I couldn't process the interview request "
                    "right now. Please try again."
                ),
                warnings=[
                    "Interview AI service temporarily unavailable."
                ],
                metadata={
                    "error": str(exc)
                },
            )

    # ================================================================
    # QUESTION GENERATION
    # ================================================================

    async def generate_questions(
        self,
        context: InterviewContext,
        count: int = 5,
        question_type: str = "mixed",
        difficulty: str = "medium",
    ) -> InterviewResponse:
        """
        Generate interview questions.

        question_type:
            technical
            behavioral
            situational
            mixed

        difficulty:
            easy
            medium
            hard
        """

        count = max(1, min(count, 20))

        allowed_types = {
            "technical",
            "behavioral",
            "situational",
            "mixed",
        }

        allowed_difficulties = {
            "easy",
            "medium",
            "hard",
        }

        if question_type not in allowed_types:
            raise ValueError(
                f"Invalid question type: {question_type}"
            )

        if difficulty not in allowed_difficulties:
            raise ValueError(
                f"Invalid difficulty: {difficulty}"
            )

        query = f"""
Generate {count} interview questions.

Question type:
{question_type}

Difficulty:
{difficulty}

Requirements:
- Questions must be relevant to the target job.
- Use the candidate's resume when useful.
- Avoid questions unrelated to job requirements.
- Do not repeat previous questions.
- Include a reason for asking each question.
- Include what a strong answer should demonstrate.
""".strip()

        response = await self.ask(
            query=query,
            context=context,
        )

        return response

    async def generate_technical_questions(
        self,
        job: Dict[str, Any],
        resume: Optional[Dict[str, Any]] = None,
        count: int = 5,
        difficulty: str = "medium",
    ) -> InterviewResponse:
        """
        Generate technical interview questions.
        """

        context = InterviewContext(
            job=job,
            resume=resume,
        )

        return await self.generate_questions(
            context=context,
            count=count,
            question_type="technical",
            difficulty=difficulty,
        )

    async def generate_behavioral_questions(
        self,
        job: Dict[str, Any],
        resume: Optional[Dict[str, Any]] = None,
        count: int = 5,
    ) -> InterviewResponse:
        """
        Generate behavioral interview questions.
        """

        context = InterviewContext(
            job=job,
            resume=resume,
        )

        return await self.generate_questions(
            context=context,
            count=count,
            question_type="behavioral",
            difficulty="medium",
        )

    # ================================================================
    # FOLLOW-UP QUESTIONS
    # ================================================================

    async def generate_follow_up(
        self,
        context: InterviewContext,
        count: int = 2,
    ) -> InterviewResponse:
        """
        Generate follow-up questions based on the candidate's answer.
        """

        if not context.candidate_answer:
            raise ValueError(
                "Candidate answer is required."
            )

        count = max(1, min(count, 10))

        query = f"""
Analyze the candidate's current answer and generate {count}
useful follow-up questions.

The follow-up questions should:
- investigate unclear claims;
- test depth of understanding;
- explore practical experience;
- clarify important omissions;
- remain relevant to the job;
- avoid unnecessarily repeating the original question.

Current question:
{context.current_question}

Candidate answer:
{context.candidate_answer}
""".strip()

        return await self.ask(
            query=query,
            context=context,
        )

    # ================================================================
    # ANSWER EVALUATION
    # ================================================================

    async def evaluate_answer(
        self,
        context: InterviewContext,
    ) -> InterviewResponse:
        """
        Analyze a candidate answer.

        This is an LLM-assisted evaluation. The authoritative scoring
        should be performed by interview_engine/evaluation/.
        """

        if not context.candidate_answer:
            raise ValueError(
                "Candidate answer is required."
            )

        query = """
Evaluate the candidate's answer against the interview question.

Analyze:

1. Technical correctness
2. Understanding of the topic
3. Relevance
4. Completeness
5. Problem-solving ability
6. Communication quality
7. Evidence/examples
8. Possible inaccuracies
9. Areas requiring follow-up

Do not invent facts about the candidate.
Do not infer protected characteristics.
""".strip()

        return await self.ask(
            query=query,
            context=context,
        )

    async def evaluate_technical_answer(
        self,
        question: Dict[str, Any],
        answer: str,
        job: Optional[Dict[str, Any]] = None,
    ) -> InterviewResponse:
        """
        Evaluate a technical interview answer.
        """

        if not answer.strip():
            raise ValueError(
                "Answer cannot be empty."
            )

        context = InterviewContext(
            job=job,
            current_question=question,
            candidate_answer=answer,
        )

        query = """
Evaluate this technical interview answer.

Focus on:
- correctness;
- technical depth;
- reasoning;
- understanding;
- edge cases;
- practical implementation knowledge;
- mistakes;
- missing concepts.

Provide constructive feedback.
""".strip()

        return await self.ask(
            query=query,
            context=context,
        )

    async def evaluate_behavioral_answer(
        self,
        question: Dict[str, Any],
        answer: str,
        job: Optional[Dict[str, Any]] = None,
    ) -> InterviewResponse:
        """
        Evaluate a behavioral interview answer.
        """

        if not answer.strip():
            raise ValueError(
                "Answer cannot be empty."
            )

        context = InterviewContext(
            job=job,
            current_question=question,
            candidate_answer=answer,
        )

        query = """
Evaluate this behavioral interview answer.

Analyze:
- clarity;
- relevance;
- ownership;
- communication;
- problem-solving;
- decision-making;
- use of concrete examples;
- outcome;
- reflection and learning.

Use evidence from the answer only.
""".strip()

        return await self.ask(
            query=query,
            context=context,
        )

    # ================================================================
    # INTERVIEW PREPARATION
    # ================================================================

    async def prepare_candidate(
        self,
        resume: Dict[str, Any],
        job: Dict[str, Any],
    ) -> InterviewResponse:
        """
        Prepare a candidate for an interview.
        """

        context = InterviewContext(
            resume=resume,
            job=job,
        )

        query = """
Prepare the candidate for this interview.

Provide:
- likely technical topics;
- likely behavioral topics;
- important resume areas to prepare;
- likely questions;
- potential weak areas;
- recommended preparation topics;
- practical interview tips.
""".strip()

        return await self.ask(
            query=query,
            context=context,
        )

    async def identify_interview_risks(
        self,
        context: InterviewContext,
    ) -> InterviewResponse:
        """
        Identify areas that deserve additional interview validation.
        """

        query = """
Identify job-relevant areas that require additional validation
during the interview.

Look for:
- unclear resume claims;
- missing evidence;
- skill gaps;
- unusually broad claims;
- experience that should be verified;
- important job requirements not demonstrated.

Do not make unsupported accusations.
""".strip()

        return await self.ask(
            query=query,
            context=context,
        )

    # ================================================================
    # ADAPTIVE INTERVIEW
    # ================================================================

    async def recommend_next_question(
        self,
        context: InterviewContext,
        current_difficulty: str = "medium",
    ) -> InterviewResponse:
        """
        Recommend the next question based on interview context.

        The actual difficulty controller should remain in:
            interview_engine/adaptive/difficulty_controller.py
        """

        query = f"""
Recommend the next interview question.

Current difficulty:
{current_difficulty}

Consider:
- previous questions;
- previous answers;
- current performance;
- unanswered job requirements;
- areas needing clarification.

Return:
- recommended question;
- question type;
- suggested difficulty;
- reason for selecting it.
""".strip()

        return await self.ask(
            query=query,
            context=context,
        )

    # ================================================================
    # INTERVIEW SUMMARY
    # ================================================================

    async def summarize_interview(
        self,
        context: InterviewContext,
    ) -> InterviewResponse:
        """
        Generate an interview summary.
        """

        query = """
Create a recruiter-friendly summary of the interview.

Include:
- overall performance;
- technical strengths;
- technical weaknesses;
- communication strengths;
- communication weaknesses;
- important evidence;
- unresolved concerns;
- recommended follow-up areas.

Do not make claims that are unsupported by the interview data.
""".strip()

        return await self.ask(
            query=query,
            context=context,
        )

    # ================================================================
    # FEEDBACK
    # ================================================================

    async def generate_candidate_feedback(
        self,
        context: InterviewContext,
    ) -> InterviewResponse:
        """
        Generate constructive feedback for the candidate.
        """

        query = """
Generate constructive candidate feedback.

Include:
- what the candidate did well;
- what could be improved;
- technical preparation recommendations;
- communication recommendations;
- suggested practice areas.

Use supportive and professional language.
Do not reveal confidential recruiter information.
""".strip()

        return await self.ask(
            query=query,
            context=context,
        )

    # ================================================================
    # REPORT EXPLANATION
    # ================================================================

    async def explain_interview_score(
        self,
        context: InterviewContext,
        score: float,
    ) -> InterviewResponse:
        """
        Explain an existing interview score.

        The score must be calculated by interview_engine.
        """

        query = f"""
Explain the supplied interview score.

Score:
{score}

Explain:
- what the score represents;
- strongest contributing areas;
- weaker areas;
- evidence supporting the assessment;
- practical improvement recommendations.

Do not recalculate or alter the supplied score.
""".strip()

        return await self.ask(
            query=query,
            context=context,
        )

    # ================================================================
    # LLM GENERATION
    # ================================================================

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
                system_prompt=INTERVIEW_SYSTEM_PROMPT,
            )

        if hasattr(self.llm, "complete"):
            return await self.llm.complete(
                prompt=prompt,
                system_prompt=INTERVIEW_SYSTEM_PROMPT,
            )

        raise AttributeError(
            "LLMClient must implement generate() or complete()."
        )

    # ================================================================
    # PROMPT BUILDING
    # ================================================================

    def _build_prompt(
        self,
        query: str,
        context: InterviewContext,
    ) -> str:
        """
        Build structured LLM prompt.
        """

        context_payload = {
            "candidate": context.candidate,
            "resume": context.resume,
            "job": context.job,
            "interview": context.interview,
            "current_question": context.current_question,
            "candidate_answer": context.candidate_answer,
            "previous_questions": context.previous_questions,
            "previous_answers": context.previous_answers,
            "evaluation": context.evaluation,
            "additional_context": context.additional_context,
        }

        serialized_context = json.dumps(
            context_payload,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

        return f"""
INTERVIEW AI REQUEST
====================

{query}

INTERVIEW CONTEXT
=================

{serialized_context}

RULES
=====

1. Use only the supplied information.
2. Never fabricate candidate information.
3. Never invent technical skills or experience.
4. Focus on job-relevant interview evidence.
5. Do not infer protected characteristics.
6. Clearly separate facts from interpretation.
7. Identify uncertainty where information is missing.
8. Do not make a final hiring decision.
9. Provide constructive and actionable feedback.
10. Avoid unnecessarily repetitive questions.
11. Questions must be relevant to the target role.
12. Respect candidate privacy.

Return JSON:

{{
    "answer": "main response",

    "questions": [
        {{
            "question": "question text",
            "type": "technical|behavioral|situational",
            "difficulty": "easy|medium|hard",
            "reason": "why this question is useful",
            "expected_signals": [
                "signal 1"
            ]
        }}
    ],

    "strengths": [
        "strength 1"
    ],

    "weaknesses": [
        "weakness 1"
    ],

    "recommendations": [
        "recommendation 1"
    ],

    "follow_up_questions": [
        "follow-up question 1"
    ],

    "warnings": [
        "warning 1"
    ]
}}
""".strip()

    # ================================================================
    # RESPONSE PARSING
    # ================================================================

    def _parse_response(
        self,
        result: Any,
        query: str,
    ) -> InterviewResponse:
        """
        Convert LLM output to InterviewResponse.
        """

        text = self._extract_text(result)

        if not text:
            return InterviewResponse(
                answer="The AI model returned an empty response.",
                warnings=[
                    "Empty model response."
                ],
            )

        parsed = self._try_parse_json(text)

        if isinstance(parsed, dict):
            return InterviewResponse(
                answer=str(
                    parsed.get(
                        "answer",
                        "No answer was generated.",
                    )
                ),

                questions=self._as_dict_list(
                    parsed.get("questions", [])
                ),

                strengths=self._as_string_list(
                    parsed.get("strengths", [])
                ),

                weaknesses=self._as_string_list(
                    parsed.get("weaknesses", [])
                ),

                recommendations=self._as_string_list(
                    parsed.get("recommendations", [])
                ),

                follow_up_questions=self._as_string_list(
                    parsed.get("follow_up_questions", [])
                ),

                warnings=self._as_string_list(
                    parsed.get("warnings", [])
                ),

                metadata={
                    "query": query,
                    "structured_response": True,
                },
            )

        return InterviewResponse(
            answer=text,
            metadata={
                "query": query,
                "structured_response": False,
            },
        )

    # ================================================================
    # RESPONSE HELPERS
    # ================================================================

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
        Safely parse JSON from an LLM response.
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
        Convert arbitrary values into strings.
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
        Convert arbitrary values into a list of dictionaries.
        """

        if not isinstance(value, list):
            return []

        return [
            item
            for item in value
            if isinstance(item, dict)
        ]