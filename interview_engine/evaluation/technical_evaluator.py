# Project scaffold file
"""
Technical Interview Answer Evaluator.

Evaluates the technical quality of an interview answer using:
- Expected-topic coverage
- Technical terminology
- Explanation depth
- Examples
- Reasoning indicators
- Code/implementation discussion
- Difficulty-aware scoring

The evaluator produces explainable scores and feedback.

This module does not make hiring decisions. It only evaluates the
technical content of an individual answer.
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


class TechnicalEvaluationError(Exception):
    """Base exception for technical evaluation errors."""


class EmptyTechnicalAnswerError(
    TechnicalEvaluationError
):
    """Raised when a technical answer is empty."""


class InvalidTechnicalInputError(
    TechnicalEvaluationError
):
    """Raised when technical evaluation input is invalid."""


# ----------------------------------------------------------------------
# Data Models
# ----------------------------------------------------------------------


@dataclass
class TechnicalDimension:
    """Individual technical scoring dimension."""

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
class TechnicalEvaluation:
    """Complete technical evaluation result."""

    question: str
    answer: str
    score: float

    dimensions: List[TechnicalDimension] = field(
        default_factory=list
    )

    covered_topics: List[str] = field(
        default_factory=list
    )

    missing_topics: List[str] = field(
        default_factory=list
    )

    strengths: List[str] = field(
        default_factory=list
    )

    improvements: List[str] = field(
        default_factory=list
    )

    technical_level: str = "unknown"

    recommendation: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question": self.question,
            "answer": self.answer,
            "score": round(self.score, 2),
            "dimensions": [
                dimension.to_dict()
                for dimension in self.dimensions
            ],
            "covered_topics": self.covered_topics,
            "missing_topics": self.missing_topics,
            "strengths": self.strengths,
            "improvements": self.improvements,
            "technical_level": self.technical_level,
            "recommendation": self.recommendation,
            "metadata": self.metadata,
        }


# ----------------------------------------------------------------------
# Technical Evaluator
# ----------------------------------------------------------------------


class TechnicalEvaluator:
    """
    Evaluate the technical quality of an interview answer.

    Default scoring dimensions:

        topic_coverage       30%
        correctness          30%
        explanation          20%
        reasoning            10%
        practical_application 10%

    Example:

        evaluator = TechnicalEvaluator()

        result = evaluator.evaluate(
            question="What is polymorphism?",
            answer=(
                "Polymorphism allows different classes to provide "
                "different implementations of the same interface."
            ),
            expected_topics=[
                "same interface",
                "different implementation",
                "method",
            ],
            difficulty="medium",
        )

        print(result.score)
    """

    DEFAULT_WEIGHTS = {
        "topic_coverage": 0.30,
        "correctness": 0.30,
        "explanation": 0.20,
        "reasoning": 0.10,
        "practical_application": 0.10,
    }

    DIFFICULTY_MULTIPLIERS = {
        "easy": 0.90,
        "beginner": 0.90,
        "medium": 1.00,
        "intermediate": 1.00,
        "hard": 1.08,
        "advanced": 1.08,
    }

    def __init__(
        self,
        weights: Optional[
            Dict[str, float]
        ] = None,
    ) -> None:

        self.weights = (
            weights
            or self.DEFAULT_WEIGHTS.copy()
        )

        self._validate_weights()

    # ------------------------------------------------------------------
    # Main Evaluation
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
        reference_answer: Optional[str] = None,
        technical_keywords: Optional[
            Sequence[str]
        ] = None,
    ) -> TechnicalEvaluation:
        """
        Evaluate a technical interview answer.

        Args:
            question:
                Interview question.

            answer:
                Candidate's answer.

            expected_topics:
                Important concepts expected in the answer.

            difficulty:
                easy, medium, hard, etc.

            question_type:
                technical, coding, system_design, database, etc.

            reference_answer:
                Optional model/reference answer.

            technical_keywords:
                Optional technical terminology expected.

        Returns:
            TechnicalEvaluation
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

        technical_keywords = (
            list(technical_keywords)
            if technical_keywords
            else []
        )

        covered_topics, missing_topics = (
            self._analyze_topic_coverage(
                answer,
                expected_topics,
            )
        )

        topic_dimension = (
            self._score_topic_coverage(
                covered_topics,
                expected_topics,
            )
        )

        correctness_dimension = (
            self._score_correctness(
                answer=answer,
                reference_answer=reference_answer,
                expected_topics=expected_topics,
            )
        )

        explanation_dimension = (
            self._score_explanation(
                answer
            )
        )

        reasoning_dimension = (
            self._score_reasoning(
                answer
            )
        )

        practical_dimension = (
            self._score_practical_application(
                answer,
                question_type=question_type,
            )
        )

        dimensions = [
            topic_dimension,
            correctness_dimension,
            explanation_dimension,
            reasoning_dimension,
            practical_dimension,
        ]

        score = self._calculate_weighted_score(
            dimensions
        )

        score = self._apply_difficulty_context(
            score,
            difficulty,
        )

        strengths = self._collect_strengths(
            dimensions
        )

        improvements = (
            self._collect_improvements(
                dimensions
            )
        )

        improvements.extend(
            self._topic_improvements(
                missing_topics
            )
        )

        improvements = self._unique(
            improvements
        )[:8]

        technical_level = (
            self._determine_technical_level(
                score
            )
        )

        recommendation = (
            self._generate_recommendation(
                score
            )
        )

        return TechnicalEvaluation(
            question=question,
            answer=answer,
            score=score,
            dimensions=dimensions,
            covered_topics=covered_topics,
            missing_topics=missing_topics,
            strengths=self._unique(
                strengths
            )[:8],
            improvements=improvements,
            technical_level=technical_level,
            recommendation=recommendation,
            metadata={
                "difficulty": difficulty,
                "question_type": question_type,
                "technical_keywords": (
                    technical_keywords
                ),
                "reference_answer_used": (
                    reference_answer
                    is not None
                ),
            },
        )

    # ------------------------------------------------------------------
    # Topic Coverage
    # ------------------------------------------------------------------

    def _analyze_topic_coverage(
        self,
        answer: str,
        expected_topics: Sequence[str],
    ) -> tuple[
        List[str],
        List[str],
    ]:
        """Determine which expected concepts are covered."""

        if not expected_topics:
            return [], []

        answer_lower = answer.lower()

        covered: List[str] = []
        missing: List[str] = []

        for topic in expected_topics:
            topic = str(topic).strip()

            if not topic:
                continue

            if self._topic_present(
                topic,
                answer_lower,
            ):
                covered.append(topic)
            else:
                missing.append(topic)

        return covered, missing

    def _topic_present(
        self,
        topic: str,
        answer_lower: str,
    ) -> bool:
        """Check whether a topic is present."""

        topic_lower = topic.lower().strip()

        if topic_lower in answer_lower:
            return True

        topic_tokens = self._content_tokens(
            topic_lower
        )

        answer_tokens = self._content_tokens(
            answer_lower
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

        return overlap >= 0.50

    def _score_topic_coverage(
        self,
        covered_topics: Sequence[str],
        expected_topics: Sequence[str],
    ) -> TechnicalDimension:
        """Score expected concept coverage."""

        if not expected_topics:
            score = 70.0

        else:
            score = (
                len(covered_topics)
                / len(expected_topics)
                * 100.0
            )

        strengths: List[str] = []
        improvements: List[str] = []

        if score >= 80:
            strengths.append(
                "Most of the expected technical concepts were covered."
            )

        elif score < 60:
            improvements.append(
                "Address more of the core technical concepts."
            )

        return TechnicalDimension(
            name="topic_coverage",
            score=score,
            weight=self.weights[
                "topic_coverage"
            ],
            feedback=(
                "Strong coverage of expected topics."
                if score >= 80
                else
                "Some expected technical topics were not addressed."
            ),
            strengths=strengths,
            improvements=improvements,
        )

    # ------------------------------------------------------------------
    # Correctness
    # ------------------------------------------------------------------

    def _score_correctness(
        self,
        answer: str,
        reference_answer: Optional[str],
        expected_topics: Sequence[str],
    ) -> TechnicalDimension:
        """
        Estimate technical correctness.

        If a reference answer is provided, semantic comparison can be
        added here later. The current implementation uses consistency
        and technical-explanation indicators rather than pretending
        deterministic keyword matching proves correctness.
        """

        score = 55.0

        words = self._word_count(
            answer
        )

        if words >= 20:
            score += 10

        if words >= 50:
            score += 8

        if self._contains_definition(
            answer
        ):
            score += 7

        if self._contains_reasoning(
            answer
        ):
            score += 5

        if self._contains_contradictory_patterns(
            answer
        ):
            score -= 20

        if reference_answer:
            reference_tokens = (
                self._content_tokens(
                    reference_answer
                )
            )

            answer_tokens = (
                self._content_tokens(
                    answer
                )
            )

            if reference_tokens:
                overlap = (
                    len(
                        reference_tokens
                        & answer_tokens
                    )
                    / len(reference_tokens)
                )

                score += min(
                    15.0,
                    overlap * 15.0,
                )

        score = max(
            0.0,
            min(100.0, score),
        )

        strengths: List[str] = []
        improvements: List[str] = []

        if score >= 80:
            strengths.append(
                "The technical explanation appears internally consistent."
            )

        elif score < 65:
            improvements.append(
                "Use more precise technical definitions and explanations."
            )

        return TechnicalDimension(
            name="correctness",
            score=score,
            weight=self.weights[
                "correctness"
            ],
            feedback=(
                "The response appears technically coherent."
                if score >= 75
                else
                "The response would benefit from more technically precise explanation."
            ),
            strengths=strengths,
            improvements=improvements,
        )

    # ------------------------------------------------------------------
    # Explanation
    # ------------------------------------------------------------------

    def _score_explanation(
        self,
        answer: str,
    ) -> TechnicalDimension:
        """Evaluate how well the answer explains the concept."""

        score = 50.0

        words = self._word_count(
            answer
        )

        sentences = self._sentence_count(
            answer
        )

        if words >= 25:
            score += 10

        if words >= 60:
            score += 10

        if sentences >= 2:
            score += 8

        if self._contains_definition(
            answer
        ):
            score += 8

        if self._contains_example(
            answer
        ):
            score += 8

        if self._contains_reasoning(
            answer
        ):
            score += 6

        score = min(
            100.0,
            score,
        )

        strengths: List[str] = []
        improvements: List[str] = []

        if self._contains_example(
            answer
        ):
            strengths.append(
                "The answer uses a practical example."
            )

        if self._contains_definition(
            answer
        ):
            strengths.append(
                "The answer provides a definition or conceptual explanation."
            )

        if score < 70:
            improvements.append(
                "Explain the concept step by step rather than only giving a short definition."
            )

        return TechnicalDimension(
            name="explanation",
            score=score,
            weight=self.weights[
                "explanation"
            ],
            feedback=(
                "The answer provides a useful technical explanation."
                if score >= 75
                else
                "The technical explanation could be developed further."
            ),
            strengths=strengths,
            improvements=improvements,
        )

    # ------------------------------------------------------------------
    # Reasoning
    # ------------------------------------------------------------------

    def _score_reasoning(
        self,
        answer: str,
    ) -> TechnicalDimension:
        """Evaluate evidence of technical reasoning."""

        score = 50.0

        reasoning_markers = [
            "because",
            "therefore",
            "however",
            "trade-off",
            "tradeoff",
            "depends on",
            "the reason",
            "as a result",
            "this means",
            "which means",
            "if",
            "otherwise",
            "instead",
        ]

        answer_lower = answer.lower()

        matches = sum(
            1
            for marker in reasoning_markers
            if marker in answer_lower
        )

        score += min(
            35.0,
            matches * 7.0,
        )

        if self._contains_comparison(
            answer
        ):
            score += 10

        score = min(
            100.0,
            score,
        )

        strengths: List[str] = []
        improvements: List[str] = []

        if matches >= 2:
            strengths.append(
                "The answer demonstrates technical reasoning."
            )

        if self._contains_comparison(
            answer
        ):
            strengths.append(
                "The answer discusses alternatives or trade-offs."
            )

        if score < 65:
            improvements.append(
                "Explain why a particular technical approach should be used."
            )

        return TechnicalDimension(
            name="reasoning",
            score=score,
            weight=self.weights[
                "reasoning"
            ],
            feedback=(
                "The answer demonstrates useful technical reasoning."
                if score >= 70
                else
                "More reasoning or trade-off discussion would strengthen the answer."
            ),
            strengths=strengths,
            improvements=improvements,
        )

    # ------------------------------------------------------------------
    # Practical Application
    # ------------------------------------------------------------------

    def _score_practical_application(
        self,
        answer: str,
        question_type: Optional[str],
    ) -> TechnicalDimension:
        """Evaluate practical implementation discussion."""

        score = 50.0

        if self._contains_example(
            answer
        ):
            score += 15

        if self._contains_code_pattern(
            answer
        ):
            score += 15

        if self._contains_real_world_language(
            answer
        ):
            score += 10

        if self._contains_implementation_terms(
            answer
        ):
            score += 10

        score = min(
            100.0,
            score,
        )

        strengths: List[str] = []
        improvements: List[str] = []

        if self._contains_example(
            answer
        ):
            strengths.append(
                "The response connects the concept to practical usage."
            )

        if self._contains_code_pattern(
            answer
        ):
            strengths.append(
                "The response includes implementation-oriented details."
            )

        if score < 65:
            improvements.append(
                "Add a practical implementation example where appropriate."
            )

        return TechnicalDimension(
            name="practical_application",
            score=score,
            weight=self.weights[
                "practical_application"
            ],
            feedback=(
                "The answer contains practical technical context."
                if score >= 70
                else
                "The answer could include more implementation or real-world context."
            ),
            strengths=strengths,
            improvements=improvements,
        )

    # ------------------------------------------------------------------
    # Score Calculation
    # ------------------------------------------------------------------

    def _calculate_weighted_score(
        self,
        dimensions: Sequence[
            TechnicalDimension
        ],
    ) -> float:
        """Calculate weighted technical score."""

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

    def _apply_difficulty_context(
        self,
        score: float,
        difficulty: Optional[str],
    ) -> float:
        """
        Apply only a small difficulty normalization.

        The difficulty multiplier is capped so that a hard question
        cannot artificially turn a weak answer into a strong answer.
        """

        if not difficulty:
            return round(
                max(0.0, min(100.0, score)),
                2,
            )

        multiplier = self.DIFFICULTY_MULTIPLIERS.get(
            difficulty.lower(),
            1.0,
        )

        adjusted = score * multiplier

        return round(
            max(
                0.0,
                min(100.0, adjusted),
            ),
            2,
        )

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    @staticmethod
    def _determine_technical_level(
        score: float,
    ) -> str:
        """Convert score into an interpretable level."""

        if score >= 90:
            return "expert"

        if score >= 80:
            return "advanced"

        if score >= 70:
            return "competent"

        if score >= 60:
            return "developing"

        return "beginner"

    @staticmethod
    def _generate_recommendation(
        score: float,
    ) -> str:
        """Generate technical recommendation."""

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
    # Feedback Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _topic_improvements(
        missing_topics: Sequence[str],
    ) -> List[str]:
        """Generate improvement suggestions for missing topics."""

        if not missing_topics:
            return []

        return [
            f"Address the technical concept: {topic}."
            for topic in missing_topics[:5]
        ]

    @staticmethod
    def _collect_strengths(
        dimensions: Sequence[
            TechnicalDimension
        ],
    ) -> List[str]:
        """Collect dimension strengths."""

        result: List[str] = []

        for dimension in dimensions:
            result.extend(
                dimension.strengths
            )

        return result

    @staticmethod
    def _collect_improvements(
        dimensions: Sequence[
            TechnicalDimension
        ],
    ) -> List[str]:
        """Collect dimension improvements."""

        result: List[str] = []

        for dimension in dimensions:
            result.extend(
                dimension.improvements
            )

        return result

    @staticmethod
    def _unique(
        values: Sequence[str],
    ) -> List[str]:
        """Return unique strings while preserving order."""

        result: List[str] = []

        for value in values:
            if value and value not in result:
                result.append(value)

        return result

    # ------------------------------------------------------------------
    # Text Heuristics
    # ------------------------------------------------------------------

    @staticmethod
    def _content_tokens(
        text: str,
    ) -> set[str]:
        """Extract content tokens."""

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
            "from",
            "that",
            "this",
            "these",
            "those",
            "what",
            "why",
            "how",
            "when",
            "where",
            "which",
            "can",
            "could",
            "would",
            "should",
            "does",
            "did",
            "do",
            "it",
            "they",
            "them",
            "you",
            "your",
            "i",
            "we",
        }

        tokens = re.findall(
            r"\b[a-zA-Z][a-zA-Z0-9_+#.-]*\b",
            text.lower(),
        )

        return {
            token
            for token in tokens
            if token not in stop_words
            and len(token) > 2
        }

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
    def _contains_definition(
        text: str,
    ) -> bool:
        """Detect definition-style language."""

        markers = (
            "is defined as",
            "means",
            "refers to",
            "is a",
            "is an",
            "is the",
            "can be defined",
        )

        text_lower = text.lower()

        return any(
            marker in text_lower
            for marker in markers
        )

    @staticmethod
    def _contains_example(
        text: str,
    ) -> bool:
        """Detect examples."""

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
    def _contains_reasoning(
        text: str,
    ) -> bool:
        """Detect reasoning language."""

        markers = (
            "because",
            "therefore",
            "however",
            "as a result",
            "this means",
            "which means",
            "the reason",
            "depends on",
            "trade-off",
            "tradeoff",
        )

        text_lower = text.lower()

        return any(
            marker in text_lower
            for marker in markers
        )

    @staticmethod
    def _contains_comparison(
        text: str,
    ) -> bool:
        """Detect comparison/trade-off discussion."""

        markers = (
            "versus",
            "vs",
            "compared to",
            "compared with",
            "better than",
            "worse than",
            "advantage",
            "disadvantage",
            "trade-off",
            "tradeoff",
        )

        text_lower = text.lower()

        return any(
            marker in text_lower
            for marker in markers
        )

    @staticmethod
    def _contains_code_pattern(
        text: str,
    ) -> bool:
        """Detect code or implementation patterns."""

        patterns = (
            r"\bdef\s+\w+\s*\(",
            r"\bclass\s+\w+",
            r"\bSELECT\s+.+\bFROM\b",
            r"\bfor\s+\w+\s+in\s+",
            r"\bif\s+.+:",
            r"\{\s*.*:\s*.*\}",
            r"=>",
            r"->",
            r"\(\)\s*\{",
        )

        return any(
            re.search(
                pattern,
                text,
                re.IGNORECASE,
            )
            for pattern in patterns
        )

    @staticmethod
    def _contains_real_world_language(
        text: str,
    ) -> bool:
        """Detect practical implementation language."""

        markers = (
            "production",
            "project",
            "application",
            "system",
            "real world",
            "real-world",
            "deployment",
            "database",
            "api",
            "service",
            "users",
            "scaling",
            "performance",
        )

        text_lower = text.lower()

        return any(
            marker in text_lower
            for marker in markers
        )

    @staticmethod
    def _contains_implementation_terms(
        text: str,
    ) -> bool:
        """Detect implementation terminology."""

        markers = (
            "implement",
            "implementation",
            "algorithm",
            "complexity",
            "memory",
            "time complexity",
            "cache",
            "index",
            "query",
            "endpoint",
            "function",
            "class",
            "object",
            "interface",
            "inheritance",
            "exception",
            "transaction",
        )

        text_lower = text.lower()

        return any(
            marker in text_lower
            for marker in markers
        )

    @staticmethod
    def _contains_contradictory_patterns(
        text: str,
    ) -> bool:
        """
        Detect obvious contradiction patterns.

        This is intentionally conservative. It should not be treated
        as a proof of technical incorrectness.
        """

        patterns = [
            (
                "always",
                "never",
            ),
            (
                "same",
                "completely different",
            ),
        ]

        text_lower = text.lower()

        for first, second in patterns:
            if (
                first in text_lower
                and second in text_lower
            ):
                return True

        return False

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_question(
        question: str,
    ) -> str:
        """Validate question."""

        if question is None:
            raise InvalidTechnicalInputError(
                "Question cannot be None."
            )

        question = str(
            question
        ).strip()

        if not question:
            raise InvalidTechnicalInputError(
                "Question cannot be empty."
            )

        return question

    @staticmethod
    def _validate_answer(
        answer: str,
    ) -> str:
        """Validate answer."""

        if answer is None:
            raise EmptyTechnicalAnswerError(
                "Technical answer cannot be None."
            )

        answer = str(
            answer
        ).strip()

        if not answer:
            raise EmptyTechnicalAnswerError(
                "Technical answer cannot be empty."
            )

        return answer

    def _validate_weights(self) -> None:
        """Validate dimension weights."""

        required = set(
            self.DEFAULT_WEIGHTS.keys()
        )

        missing = (
            required
            - set(self.weights.keys())
        )

        if missing:
            raise InvalidTechnicalInputError(
                "Missing technical evaluation weights: "
                + ", ".join(
                    sorted(missing)
                )
            )

        if any(
            weight < 0
            for weight in self.weights.values()
        ):
            raise InvalidTechnicalInputError(
                "Technical evaluation weights cannot be negative."
            )

        if sum(
            self.weights.values()
        ) <= 0:
            raise InvalidTechnicalInputError(
                "At least one technical evaluation weight "
                "must be greater than zero."
            )


# ----------------------------------------------------------------------
# Convenience Function
# ----------------------------------------------------------------------


def evaluate_technical_answer(
    question: str,
    answer: str,
    expected_topics: Optional[
        Sequence[str]
    ] = None,
    difficulty: Optional[str] = None,
    question_type: Optional[str] = None,
    reference_answer: Optional[str] = None,
    technical_keywords: Optional[
        Sequence[str]
    ] = None,
) -> TechnicalEvaluation:
    """
    Convenience wrapper around TechnicalEvaluator.
    """

    evaluator = TechnicalEvaluator()

    return evaluator.evaluate(
        question=question,
        answer=answer,
        expected_topics=expected_topics,
        difficulty=difficulty,
        question_type=question_type,
        reference_answer=reference_answer,
        technical_keywords=technical_keywords,
    )


__all__ = [
    "TechnicalEvaluator",
    "TechnicalEvaluation",
    "TechnicalDimension",
    "TechnicalEvaluationError",
    "EmptyTechnicalAnswerError",
    "InvalidTechnicalInputError",
    "evaluate_technical_answer",
]