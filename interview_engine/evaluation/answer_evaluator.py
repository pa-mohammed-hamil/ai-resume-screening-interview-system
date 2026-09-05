# Project scaffold file
"""
Answer Evaluator

Main orchestration layer for AI interview answer evaluation.

Responsibilities:
- Validate interview answers
- Evaluate answer relevance
- Evaluate completeness
- Evaluate technical quality
- Evaluate communication quality
- Incorporate observable voice metrics when available
- Generate strengths and improvement suggestions
- Produce a structured scorecard

This evaluator should be used as the high-level entry point.
Specialized evaluators remain responsible for their own dimensions:

    technical_evaluator.py
    communication_evaluator.py
    confidence_evaluator.py
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------


class AnswerEvaluationError(Exception):
    """Base exception for answer evaluation errors."""


class EmptyAnswerError(AnswerEvaluationError):
    """Raised when the candidate answer is empty."""


class InvalidEvaluationError(AnswerEvaluationError):
    """Raised when evaluation input is invalid."""


# ----------------------------------------------------------------------
# Data Models
# ----------------------------------------------------------------------


@dataclass
class DimensionScore:
    """Score for an individual evaluation dimension."""

    name: str
    score: float
    weight: float
    feedback: str = ""
    strengths: List[str] = field(
        default_factory=list
    )
    improvements: List[str] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        self.score = max(
            0.0,
            min(100.0, float(self.score)),
        )

        self.weight = max(
            0.0,
            float(self.weight),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "score": round(self.score, 2),
            "weight": round(self.weight, 4),
            "feedback": self.feedback,
            "strengths": self.strengths,
            "improvements": self.improvements,
        }


@dataclass
class AnswerEvaluation:
    """Complete evaluation result for one interview answer."""

    question: str
    answer: str

    overall_score: float

    dimensions: List[DimensionScore] = field(
        default_factory=list
    )

    strengths: List[str] = field(
        default_factory=list
    )

    improvements: List[str] = field(
        default_factory=list
    )

    missing_topics: List[str] = field(
        default_factory=list
    )

    recommendation: str = ""

    follow_up_needed: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question": self.question,
            "answer": self.answer,
            "overall_score": round(
                self.overall_score,
                2,
            ),
            "dimensions": [
                dimension.to_dict()
                for dimension in self.dimensions
            ],
            "strengths": self.strengths,
            "improvements": self.improvements,
            "missing_topics": self.missing_topics,
            "recommendation": self.recommendation,
            "follow_up_needed": self.follow_up_needed,
            "metadata": self.metadata,
        }


# ----------------------------------------------------------------------
# Answer Evaluator
# ----------------------------------------------------------------------


class AnswerEvaluator:
    """
    High-level interview answer evaluator.

    The evaluator is designed to work even when the specialized
    evaluator modules are unavailable. In that case it uses deterministic
    baseline heuristics.

    Specialized evaluators can be injected through the constructor.

    Example:

        evaluator = AnswerEvaluator()

        result = evaluator.evaluate(
            question="What is polymorphism in Python?",
            answer=(
                "Polymorphism allows different objects to respond "
                "to the same interface or method."
            ),
        )

        print(result.overall_score)
    """

    DEFAULT_WEIGHTS = {
        "technical": 0.35,
        "communication": 0.25,
        "relevance": 0.20,
        "completeness": 0.20,
    }

    def __init__(
        self,
        technical_evaluator: Optional[Any] = None,
        communication_evaluator: Optional[Any] = None,
        confidence_evaluator: Optional[Any] = None,
        weights: Optional[Dict[str, float]] = None,
    ) -> None:

        self.technical_evaluator = (
            technical_evaluator
        )

        self.communication_evaluator = (
            communication_evaluator
        )

        self.confidence_evaluator = (
            confidence_evaluator
        )

        self.weights = (
            weights
            or self.DEFAULT_WEIGHTS.copy()
        )

        self._validate_weights()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(
        self,
        question: str,
        answer: str,
        expected_topics: Optional[
            Sequence[str]
        ] = None,
        difficulty: Optional[str] = None,
        question_type: Optional[str] = None,
        voice_metrics: Optional[
            Dict[str, Any]
        ] = None,
    ) -> AnswerEvaluation:
        """
        Evaluate a candidate's answer.

        Args:
            question:
                Interview question.

            answer:
                Candidate's transcript.

            expected_topics:
                Topics that should ideally appear in the answer.

            difficulty:
                Question difficulty such as easy, medium, or hard.

            question_type:
                technical, behavioral, situational, general, etc.

            voice_metrics:
                Optional observable speech metrics from voice_analyzer.py.

        Returns:
            AnswerEvaluation
        """

        question = self._validate_question(
            question
        )

        answer = self._validate_answer(
            answer
        )

        expected_topics = (
            list(expected_topics)
            if expected_topics
            else []
        )

        logger.info(
            "Evaluating interview answer."
        )

        relevance = self._evaluate_relevance(
            question,
            answer,
        )

        completeness = self._evaluate_completeness(
            answer,
            expected_topics,
        )

        technical = self._evaluate_technical(
            question=question,
            answer=answer,
            expected_topics=expected_topics,
            difficulty=difficulty,
            question_type=question_type,
        )

        communication = (
            self._evaluate_communication(
                answer
            )
        )

        dimensions = [
            technical,
            communication,
            relevance,
            completeness,
        ]

        overall_score = self._calculate_overall_score(
            dimensions
        )

        missing_topics = (
            self._find_missing_topics(
                answer,
                expected_topics,
            )
        )

        strengths = self._collect_strengths(
            dimensions
        )

        improvements = (
            self._collect_improvements(
                dimensions
            )
        )

        recommendation = (
            self._generate_recommendation(
                overall_score
            )
        )

        follow_up_needed = (
            self.should_ask_follow_up(
                overall_score=overall_score,
                missing_topics=missing_topics,
                answer=answer,
            )
        )

        # Voice metrics are supporting signals only.
        voice_summary = (
            self._summarize_voice_metrics(
                voice_metrics
            )
        )

        return AnswerEvaluation(
            question=question,
            answer=answer,
            overall_score=overall_score,
            dimensions=dimensions,
            strengths=strengths,
            improvements=improvements,
            missing_topics=missing_topics,
            recommendation=recommendation,
            follow_up_needed=follow_up_needed,
            metadata={
                "difficulty": difficulty,
                "question_type": question_type,
                "expected_topics": expected_topics,
                "voice_metrics": voice_summary,
            },
        )

    # ------------------------------------------------------------------
    # Relevance
    # ------------------------------------------------------------------

    def _evaluate_relevance(
        self,
        question: str,
        answer: str,
    ) -> DimensionScore:
        """
        Estimate how directly the answer addresses the question.

        This deterministic implementation uses keyword overlap and
        answer-length signals. A production system can replace this
        with an LLM/embedding-based evaluator.
        """

        question_terms = self._important_words(
            question
        )

        answer_terms = self._important_words(
            answer
        )

        if not question_terms:
            score = 70.0
        else:
            overlap = (
                len(
                    question_terms
                    & answer_terms
                )
                / len(question_terms)
            )

            score = min(
                100.0,
                45.0 + overlap * 55.0,
            )

        strengths: List[str] = []
        improvements: List[str] = []

        if score >= 80:
            strengths.append(
                "The answer addresses the main topic directly."
            )

        elif score < 60:
            improvements.append(
                "Keep the answer more directly focused on the question."
            )

        feedback = (
            "The response is reasonably focused."
            if score >= 70
            else
            "The response could be more directly connected "
            "to the question."
        )

        return DimensionScore(
            name="relevance",
            score=score,
            weight=self.weights["relevance"],
            feedback=feedback,
            strengths=strengths,
            improvements=improvements,
        )

    # ------------------------------------------------------------------
    # Completeness
    # ------------------------------------------------------------------

    def _evaluate_completeness(
        self,
        answer: str,
        expected_topics: Sequence[str],
    ) -> DimensionScore:
        """Evaluate coverage of expected topics."""

        if not expected_topics:
            word_count = self._word_count(
                answer
            )

            if word_count >= 80:
                score = 90.0
            elif word_count >= 50:
                score = 82.0
            elif word_count >= 25:
                score = 72.0
            elif word_count >= 10:
                score = 60.0
            else:
                score = 40.0

        else:
            answer_lower = answer.lower()

            matched = 0

            for topic in expected_topics:
                topic_lower = topic.lower()

                if (
                    topic_lower in answer_lower
                    or self._topic_token_overlap(
                        topic_lower,
                        answer_lower,
                    )
                ):
                    matched += 1

            score = (
                matched
                / len(expected_topics)
                * 100.0
            )

        strengths: List[str] = []
        improvements: List[str] = []

        if score >= 80:
            strengths.append(
                "The answer provides good topic coverage."
            )

        elif score < 60:
            improvements.append(
                "Cover more of the key points expected in the answer."
            )

        return DimensionScore(
            name="completeness",
            score=score,
            weight=self.weights["completeness"],
            feedback=(
                "Good coverage of the expected content."
                if score >= 80
                else
                "Some important content appears to be missing."
            ),
            strengths=strengths,
            improvements=improvements,
        )

    # ------------------------------------------------------------------
    # Technical Evaluation
    # ------------------------------------------------------------------

    def _evaluate_technical(
        self,
        question: str,
        answer: str,
        expected_topics: Sequence[str],
        difficulty: Optional[str],
        question_type: Optional[str],
    ) -> DimensionScore:
        """
        Evaluate technical quality.

        Uses the specialized technical evaluator when supplied.
        Otherwise falls back to deterministic heuristics.
        """

        if self.technical_evaluator is not None:
            result = self._call_specialized_evaluator(
                self.technical_evaluator,
                question=question,
                answer=answer,
                expected_topics=expected_topics,
                difficulty=difficulty,
                question_type=question_type,
            )

            if result is not None:
                return self._normalize_dimension_result(
                    result,
                    name="technical",
                    weight=self.weights["technical"],
                )

        score = self._baseline_technical_score(
            answer,
            expected_topics,
        )

        strengths: List[str] = []
        improvements: List[str] = []

        if self._contains_examples(answer):
            score += 8
            strengths.append(
                "The answer includes a practical example."
            )

        if self._contains_explanation(answer):
            score += 5
            strengths.append(
                "The answer includes explanatory reasoning."
            )

        if score >= 80:
            feedback = (
                "The response demonstrates good technical understanding."
            )

        elif score >= 60:
            feedback = (
                "The response demonstrates partial technical understanding."
            )

            improvements.append(
                "Add more precise technical details or examples."
            )

        else:
            feedback = (
                "The response needs stronger technical explanation."
            )

            improvements.append(
                "Explain the underlying concept more clearly."
            )

        return DimensionScore(
            name="technical",
            score=min(100.0, score),
            weight=self.weights["technical"],
            feedback=feedback,
            strengths=strengths,
            improvements=improvements,
        )

    # ------------------------------------------------------------------
    # Communication Evaluation
    # ------------------------------------------------------------------

    def _evaluate_communication(
        self,
        answer: str,
    ) -> DimensionScore:
        """Evaluate clarity and structure of written transcript."""

        if self.communication_evaluator is not None:
            result = self._call_specialized_evaluator(
                self.communication_evaluator,
                answer=answer,
            )

            if result is not None:
                return self._normalize_dimension_result(
                    result,
                    name="communication",
                    weight=self.weights["communication"],
                )

        words = self._word_count(answer)

        sentences = self._sentence_count(
            answer
        )

        score = 60.0

        if words >= 15:
            score += 10

        if words >= 40:
            score += 8

        if sentences >= 2:
            score += 5

        if sentences >= 4:
            score += 5

        if self._contains_structure_markers(
            answer
        ):
            score += 7

        if self._has_excessive_repetition(
            answer
        ):
            score -= 15

        if self._has_fragmented_text(
            answer
        ):
            score -= 10

        score = max(
            0.0,
            min(100.0, score),
        )

        strengths: List[str] = []
        improvements: List[str] = []

        if score >= 80:
            strengths.append(
                "The answer is reasonably clear and structured."
            )
        else:
            improvements.append(
                "Use a clearer structure when explaining your answer."
            )

        return DimensionScore(
            name="communication",
            score=score,
            weight=self.weights["communication"],
            feedback=(
                "The response is clear and reasonably structured."
                if score >= 80
                else
                "The response could be clearer and better structured."
            ),
            strengths=strengths,
            improvements=improvements,
        )

    # ------------------------------------------------------------------
    # Overall Score
    # ------------------------------------------------------------------

    @staticmethod
    def _calculate_overall_score(
        dimensions: Sequence[DimensionScore],
    ) -> float:
        """Calculate weighted overall score."""

        total_weight = sum(
            dimension.weight
            for dimension in dimensions
        )

        if total_weight <= 0:
            return 0.0

        score = sum(
            dimension.score
            * dimension.weight
            for dimension in dimensions
        )

        return round(
            score / total_weight,
            2,
        )

    # ------------------------------------------------------------------
    # Follow-up Logic
    # ------------------------------------------------------------------

    def should_ask_follow_up(
        self,
        overall_score: float,
        missing_topics: Sequence[str],
        answer: str,
    ) -> bool:
        """
        Determine whether a follow-up question may be useful.

        The adaptive interview engine can use this signal together with
        difficulty and interview state.
        """

        if not answer.strip():
            return True

        if overall_score < 55:
            return True

        if len(missing_topics) >= 2:
            return True

        return False

    # ------------------------------------------------------------------
    # Recommendation
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_recommendation(
        score: float,
    ) -> str:
        """Generate a high-level recommendation."""

        if score >= 90:
            return "excellent"

        if score >= 80:
            return "strong"

        if score >= 70:
            return "good"

        if score >= 60:
            return "needs_improvement"

        return "weak"

    # ------------------------------------------------------------------
    # Missing Topics
    # ------------------------------------------------------------------

    def _find_missing_topics(
        self,
        answer: str,
        expected_topics: Sequence[str],
    ) -> List[str]:
        """Find expected topics absent from the answer."""

        answer_lower = answer.lower()

        missing: List[str] = []

        for topic in expected_topics:
            topic_lower = topic.lower()

            if (
                topic_lower not in answer_lower
                and not self._topic_token_overlap(
                    topic_lower,
                    answer_lower,
                )
            ):
                missing.append(topic)

        return missing

    # ------------------------------------------------------------------
    # Voice Metrics
    # ------------------------------------------------------------------

    def _summarize_voice_metrics(
        self,
        voice_metrics: Optional[
            Dict[str, Any]
        ],
    ) -> Dict[str, Any]:
        """
        Keep only observable speech metrics useful for interview
        feedback.

        Voice metrics are not used as direct evidence of personality,
        intelligence, confidence, or hiring suitability.
        """

        if not voice_metrics:
            return {}

        allowed = {
            "duration_seconds",
            "speech_duration_seconds",
            "silence_duration_seconds",
            "pause_count",
            "long_pause_count",
            "average_pause_seconds",
            "longest_pause_seconds",
            "words_per_minute",
            "estimated_speech_ratio",
            "rms_db",
            "peak_db",
            "warnings",
        }

        return {
            key: value
            for key, value in voice_metrics.items()
            if key in allowed
        }

    # ------------------------------------------------------------------
    # Strengths / Improvements
    # ------------------------------------------------------------------

    @staticmethod
    def _collect_strengths(
        dimensions: Sequence[DimensionScore],
    ) -> List[str]:
        """Collect unique strengths."""

        strengths: List[str] = []

        for dimension in dimensions:
            for strength in dimension.strengths:
                if strength not in strengths:
                    strengths.append(strength)

        return strengths[:8]

    @staticmethod
    def _collect_improvements(
        dimensions: Sequence[DimensionScore],
    ) -> List[str]:
        """Collect unique improvement suggestions."""

        improvements: List[str] = []

        for dimension in dimensions:
            for improvement in dimension.improvements:
                if improvement not in improvements:
                    improvements.append(
                        improvement
                    )

        return improvements[:8]

    # ------------------------------------------------------------------
    # Specialized Evaluator Support
    # ------------------------------------------------------------------

    @staticmethod
    def _call_specialized_evaluator(
        evaluator: Any,
        **kwargs: Any,
    ) -> Optional[Any]:
        """Call a specialized evaluator safely."""

        try:
            if hasattr(evaluator, "evaluate"):
                return evaluator.evaluate(
                    **kwargs
                )

            if callable(evaluator):
                return evaluator(
                    **kwargs
                )

        except Exception as exc:
            logger.warning(
                "Specialized evaluator failed: %s",
                exc,
            )

        return None

    @staticmethod
    def _normalize_dimension_result(
        result: Any,
        name: str,
        weight: float,
    ) -> DimensionScore:
        """Normalize specialized evaluator output."""

        if isinstance(
            result,
            DimensionScore,
        ):
            result.name = name
            result.weight = weight
            return result

        if isinstance(result, dict):
            return DimensionScore(
                name=name,
                score=float(
                    result.get(
                        "score",
                        0,
                    )
                ),
                weight=weight,
                feedback=str(
                    result.get(
                        "feedback",
                        "",
                    )
                ),
                strengths=list(
                    result.get(
                        "strengths",
                        [],
                    )
                ),
                improvements=list(
                    result.get(
                        "improvements",
                        [],
                    )
                ),
            )

        if isinstance(result, (int, float)):
            return DimensionScore(
                name=name,
                score=float(result),
                weight=weight,
            )

        raise InvalidEvaluationError(
            f"Unsupported evaluator result type: "
            f"{type(result).__name__}"
        )

    # ------------------------------------------------------------------
    # Baseline Technical Heuristics
    # ------------------------------------------------------------------

    def _baseline_technical_score(
        self,
        answer: str,
        expected_topics: Sequence[str],
    ) -> float:
        """Calculate a deterministic baseline technical score."""

        words = self._word_count(
            answer
        )

        score = 45.0

        if words >= 20:
            score += 10

        if words >= 50:
            score += 10

        if words >= 100:
            score += 5

        if expected_topics:
            matched = 0

            answer_lower = answer.lower()

            for topic in expected_topics:
                if (
                    topic.lower() in answer_lower
                    or self._topic_token_overlap(
                        topic.lower(),
                        answer_lower,
                    )
                ):
                    matched += 1

            score += (
                matched
                / len(expected_topics)
                * 30
            )

        return min(
            100.0,
            score,
        )

    # ------------------------------------------------------------------
    # Text Analysis Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_question(
        question: str,
    ) -> str:
        """Validate interview question."""

        if question is None:
            raise InvalidEvaluationError(
                "Question cannot be None."
            )

        question = str(
            question
        ).strip()

        if not question:
            raise InvalidEvaluationError(
                "Question cannot be empty."
            )

        return question

    @staticmethod
    def _validate_answer(
        answer: str,
    ) -> str:
        """Validate candidate answer."""

        if answer is None:
            raise EmptyAnswerError(
                "Candidate answer cannot be None."
            )

        answer = str(
            answer
        ).strip()

        if not answer:
            raise EmptyAnswerError(
                "Candidate answer cannot be empty."
            )

        return answer

    @staticmethod
    def _word_count(
        text: str,
    ) -> int:
        """Count words."""

        return len(
            re.findall(
                r"\b[\w'-]+\b",
                text,
            )
        )

    @staticmethod
    def _sentence_count(
        text: str,
    ) -> int:
        """Estimate sentence count."""

        sentences = re.split(
            r"[.!?]+",
            text,
        )

        return len(
            [
                sentence
                for sentence in sentences
                if sentence.strip()
            ]
        )

    @staticmethod
    def _important_words(
        text: str,
    ) -> set[str]:
        """Extract simple content words."""

        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "is",
            "are",
            "was",
            "were",
            "to",
            "of",
            "in",
            "on",
            "for",
            "with",
            "what",
            "why",
            "how",
            "when",
            "where",
            "which",
            "do",
            "does",
            "did",
            "can",
            "could",
            "would",
            "should",
            "you",
            "your",
            "i",
            "we",
            "they",
        }

        words = re.findall(
            r"\b[a-zA-Z][a-zA-Z0-9_-]+\b",
            text.lower(),
        )

        return {
            word
            for word in words
            if word not in stop_words
            and len(word) > 2
        }

    @staticmethod
    def _topic_token_overlap(
        topic: str,
        answer: str,
    ) -> bool:
        """Check whether enough topic tokens occur in answer."""

        topic_tokens = {
            token
            for token in re.findall(
                r"\b[a-zA-Z0-9+#.-]+\b",
                topic.lower(),
            )
            if len(token) > 2
        }

        answer_tokens = set(
            re.findall(
                r"\b[a-zA-Z0-9+#.-]+\b",
                answer.lower(),
            )
        )

        if not topic_tokens:
            return False

        overlap = (
            len(
                topic_tokens
                & answer_tokens
            )
            / len(topic_tokens)
        )

        return overlap >= 0.5

    @staticmethod
    def _contains_examples(
        text: str,
    ) -> bool:
        """Detect common example indicators."""

        markers = (
            "for example",
            "for instance",
            "such as",
            "e.g.",
            "in practice",
            "example",
        )

        text_lower = text.lower()

        return any(
            marker in text_lower
            for marker in markers
        )

    @staticmethod
    def _contains_explanation(
        text: str,
    ) -> bool:
        """Detect basic explanation markers."""

        markers = (
            "because",
            "therefore",
            "this means",
            "which means",
            "the reason",
            "so that",
            "as a result",
        )

        text_lower = text.lower()

        return any(
            marker in text_lower
            for marker in markers
        )

    @staticmethod
    def _contains_structure_markers(
        text: str,
    ) -> bool:
        """Detect words indicating structured explanations."""

        markers = (
            "first",
            "second",
            "third",
            "finally",
            "however",
            "therefore",
            "for example",
            "in summary",
            "overall",
        )

        text_lower = text.lower()

        return any(
            marker in text_lower
            for marker in markers
        )

    @staticmethod
    def _has_excessive_repetition(
        text: str,
    ) -> bool:
        """Detect repeated words as a rough transcript-quality signal."""

        words = re.findall(
            r"\b[a-zA-Z]+\b",
            text.lower(),
        )

        if len(words) < 10:
            return False

        counts: Dict[str, int] = {}

        for word in words:
            counts[word] = (
                counts.get(word, 0) + 1
            )

        repeated = sum(
            1
            for count in counts.values()
            if count >= 5
        )

        return repeated >= 2

    @staticmethod
    def _has_fragmented_text(
        text: str,
    ) -> bool:
        """Detect very fragmented transcript text."""

        words = re.findall(
            r"\b[\w'-]+\b",
            text,
        )

        if len(words) < 10:
            return False

        sentences = re.split(
            r"[.!?]+",
            text,
        )

        non_empty = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

        if not non_empty:
            return False

        short_sentences = sum(
            1
            for sentence in non_empty
            if len(sentence.split()) <= 2
        )

        return (
            short_sentences
            / len(non_empty)
            > 0.6
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_weights(self) -> None:
        """Validate evaluation weights."""

        required = {
            "technical",
            "communication",
            "relevance",
            "completeness",
        }

        missing = (
            required
            - set(self.weights.keys())
        )

        if missing:
            raise InvalidEvaluationError(
                f"Missing evaluation weights: "
                f"{', '.join(sorted(missing))}"
            )

        if any(
            weight < 0
            for weight in self.weights.values()
        ):
            raise InvalidEvaluationError(
                "Evaluation weights cannot be negative."
            )

        if sum(self.weights.values()) <= 0:
            raise InvalidEvaluationError(
                "At least one evaluation weight must be greater than zero."
            )


# ----------------------------------------------------------------------
# Convenience Function
# ----------------------------------------------------------------------


def evaluate_answer(
    question: str,
    answer: str,
    expected_topics: Optional[
        Sequence[str]
    ] = None,
    difficulty: Optional[str] = None,
    question_type: Optional[str] = None,
    voice_metrics: Optional[
        Dict[str, Any]
    ] = None,
) -> AnswerEvaluation:
    """
    Convenience function for evaluating one answer.
    """

    evaluator = AnswerEvaluator()

    return evaluator.evaluate(
        question=question,
        answer=answer,
        expected_topics=expected_topics,
        difficulty=difficulty,
        question_type=question_type,
        voice_metrics=voice_metrics,
    )


__all__ = [
    "AnswerEvaluator",
    "AnswerEvaluation",
    "DimensionScore",
    "AnswerEvaluationError",
    "EmptyAnswerError",
    "InvalidEvaluationError",
    "evaluate_answer",
]