# Project scaffold file
"""
Communication Interview Answer Evaluator.

Evaluates the communication quality of an interview answer using:
- Clarity
- Structure
- Conciseness
- Coherence
- Vocabulary
- Professional communication
- Answer completeness

This module evaluates communication only. Technical correctness should
be handled by technical_evaluator.py.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------


class CommunicationEvaluationError(Exception):
    """Base exception for communication evaluation errors."""


class EmptyCommunicationAnswerError(
    CommunicationEvaluationError
):
    """Raised when the answer is empty."""


class InvalidCommunicationInputError(
    CommunicationEvaluationError
):
    """Raised when evaluation input is invalid."""


# ----------------------------------------------------------------------
# Data Models
# ----------------------------------------------------------------------


@dataclass
class CommunicationDimension:
    """Represents one communication scoring dimension."""

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
class CommunicationEvaluation:
    """Complete communication evaluation."""

    question: str
    answer: str
    score: float

    dimensions: List[CommunicationDimension] = field(
        default_factory=list
    )

    strengths: List[str] = field(
        default_factory=list
    )

    improvements: List[str] = field(
        default_factory=list
    )

    communication_level: str = "unknown"

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
            "strengths": self.strengths,
            "improvements": self.improvements,
            "communication_level": self.communication_level,
            "recommendation": self.recommendation,
            "metadata": self.metadata,
        }


# ----------------------------------------------------------------------
# Evaluator
# ----------------------------------------------------------------------


class CommunicationEvaluator:
    """
    Evaluate communication quality of an interview answer.

    Default weights:

        clarity         25%
        structure       20%
        coherence       20%
        conciseness     15%
        vocabulary      10%
        professionalism 10%

    The evaluator intentionally does not judge:
    - accent
    - dialect
    - native/non-native language status
    - personality
    - protected characteristics

    Example:

        evaluator = CommunicationEvaluator()

        result = evaluator.evaluate(
            question="Tell me about a difficult project.",
            answer=(
                "In my previous project, we had a performance issue. "
                "I analyzed the database queries and found an inefficient "
                "query. I optimized it and reduced response time."
            ),
        )

        print(result.score)
    """

    DEFAULT_WEIGHTS = {
        "clarity": 0.25,
        "structure": 0.20,
        "coherence": 0.20,
        "conciseness": 0.15,
        "vocabulary": 0.10,
        "professionalism": 0.10,
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
        expected_points: Optional[
            List[str]
        ] = None,
        answer_type: Optional[str] = None,
    ) -> CommunicationEvaluation:
        """
        Evaluate communication quality.

        Args:
            question:
                Interview question.

            answer:
                Candidate answer.

            expected_points:
                Optional points that a complete answer should address.

            answer_type:
                behavioral, technical, introduction, situational, etc.

        Returns:
            CommunicationEvaluation
        """

        question = self._validate_question(
            question
        )

        answer = self._validate_answer(
            answer
        )

        expected_points = (
            expected_points or []
        )

        clarity = self._score_clarity(
            answer
        )

        structure = self._score_structure(
            answer
        )

        coherence = self._score_coherence(
            answer
        )

        conciseness = self._score_conciseness(
            answer
        )

        vocabulary = self._score_vocabulary(
            answer
        )

        professionalism = (
            self._score_professionalism(
                answer
            )
        )

        dimensions = [
            clarity,
            structure,
            coherence,
            conciseness,
            vocabulary,
            professionalism,
        ]

        score = self._calculate_score(
            dimensions
        )

        completeness = (
            self._calculate_completeness(
                answer,
                expected_points,
            )
        )

        # Completeness is used as a small adjustment rather
        # than being allowed to dominate communication scoring.
        if expected_points:
            score = (
                score * 0.90
                + completeness * 0.10
            )

        score = round(
            max(
                0.0,
                min(100.0, score),
            ),
            2,
        )

        strengths = self._collect_strengths(
            dimensions
        )

        improvements = self._collect_improvements(
            dimensions
        )

        if expected_points and completeness < 60:
            improvements.append(
                "Cover the main points needed to give a complete answer."
            )

        improvements = self._unique(
            improvements
        )

        level = (
            self._determine_level(
                score
            )
        )

        recommendation = (
            self._recommendation(
                score
            )
        )

        return CommunicationEvaluation(
            question=question,
            answer=answer,
            score=score,
            dimensions=dimensions,
            strengths=self._unique(
                strengths
            ),
            improvements=improvements,
            communication_level=level,
            recommendation=recommendation,
            metadata={
                "answer_type": answer_type,
                "expected_points": expected_points,
                "completeness_score": round(
                    completeness,
                    2,
                ),
                "word_count": self._word_count(
                    answer
                ),
                "sentence_count": self._sentence_count(
                    answer
                ),
            },
        )

    # ------------------------------------------------------------------
    # Clarity
    # ------------------------------------------------------------------

    def _score_clarity(
        self,
        answer: str,
    ) -> CommunicationDimension:
        """Evaluate how clearly the answer communicates its ideas."""

        score = 60.0

        words = self._word_count(
            answer
        )

        sentences = self._sentence_count(
            answer
        )

        if words >= 15:
            score += 8

        if words >= 30:
            score += 8

        if sentences >= 2:
            score += 5

        if self._has_clear_sentences(
            answer
        ):
            score += 8

        if self._has_excessive_fillers(
            answer
        ):
            score -= 15

        if self._has_long_sentences(
            answer
        ):
            score -= 10

        score = self._clamp(
            score
        )

        strengths: List[str] = []
        improvements: List[str] = []

        if score >= 80:
            strengths.append(
                "Ideas are communicated clearly."
            )

        if self._has_excessive_fillers(
            answer
        ):
            improvements.append(
                "Reduce filler words and get to the main point more directly."
            )

        if self._has_long_sentences(
            answer
        ):
            improvements.append(
                "Use shorter sentences to make explanations easier to follow."
            )

        return CommunicationDimension(
            name="clarity",
            score=score,
            weight=self.weights[
                "clarity"
            ],
            feedback=(
                "The response is clear and understandable."
                if score >= 75
                else
                "The response could communicate its main ideas more directly."
            ),
            strengths=strengths,
            improvements=improvements,
        )

    # ------------------------------------------------------------------
    # Structure
    # ------------------------------------------------------------------

    def _score_structure(
        self,
        answer: str,
    ) -> CommunicationDimension:
        """Evaluate organization of the response."""

        score = 55.0

        if self._has_opening_phrase(
            answer
        ):
            score += 8

        if self._has_sequence_markers(
            answer
        ):
            score += 12

        if self._has_conclusion(
            answer
        ):
            score += 10

        if self._sentence_count(
            answer
        ) >= 3:
            score += 5

        if self._has_list_structure(
            answer
        ):
            score += 10

        score = self._clamp(
            score
        )

        strengths: List[str] = []
        improvements: List[str] = []

        if self._has_sequence_markers(
            answer
        ):
            strengths.append(
                "The answer follows a logical sequence."
            )

        if self._has_conclusion(
            answer
        ):
            strengths.append(
                "The response provides a clear closing point."
            )

        if score < 70:
            improvements.append(
                "Organize the response into a beginning, key points, and conclusion."
            )

        return CommunicationDimension(
            name="structure",
            score=score,
            weight=self.weights[
                "structure"
            ],
            feedback=(
                "The response has a logical structure."
                if score >= 75
                else
                "The response could be organized more clearly."
            ),
            strengths=strengths,
            improvements=improvements,
        )

    # ------------------------------------------------------------------
    # Coherence
    # ------------------------------------------------------------------

    def _score_coherence(
        self,
        answer: str,
    ) -> CommunicationDimension:
        """Evaluate logical flow between ideas."""

        score = 60.0

        transition_words = [
            "because",
            "therefore",
            "however",
            "although",
            "also",
            "additionally",
            "first",
            "second",
            "finally",
            "then",
            "next",
            "as a result",
            "for example",
            "in addition",
            "on the other hand",
        ]

        answer_lower = answer.lower()

        transition_count = sum(
            1
            for word in transition_words
            if word in answer_lower
        )

        score += min(
            20.0,
            transition_count * 5.0,
        )

        if self._sentence_count(
            answer
        ) >= 3:
            score += 8

        if self._has_fragmented_answer(
            answer
        ):
            score -= 15

        score = self._clamp(
            score
        )

        strengths: List[str] = []
        improvements: List[str] = []

        if transition_count >= 2:
            strengths.append(
                "Ideas are connected using useful transitions."
            )

        if score < 70:
            improvements.append(
                "Connect ideas explicitly so the answer flows logically."
            )

        return CommunicationDimension(
            name="coherence",
            score=score,
            weight=self.weights[
                "coherence"
            ],
            feedback=(
                "The ideas generally flow logically."
                if score >= 75
                else
                "The connection between ideas could be stronger."
            ),
            strengths=strengths,
            improvements=improvements,
        )

    # ------------------------------------------------------------------
    # Conciseness
    # ------------------------------------------------------------------

    def _score_conciseness(
        self,
        answer: str,
    ) -> CommunicationDimension:
        """Evaluate whether the answer is appropriately concise."""

        words = self._word_count(
            answer
        )

        sentences = self._sentence_count(
            answer
        )

        score = 75.0

        if words < 8:
            score -= 25

        elif words < 15:
            score -= 10

        elif 15 <= words <= 180:
            score += 5

        elif 180 < words <= 300:
            score -= 5

        elif words > 300:
            score -= 20

        if self._has_repetition(
            answer
        ):
            score -= 15

        if self._has_excessive_fillers(
            answer
        ):
            score -= 10

        if sentences > 0:
            avg_sentence_length = (
                words / sentences
            )

            if avg_sentence_length > 35:
                score -= 10

        score = self._clamp(
            score
        )

        strengths: List[str] = []
        improvements: List[str] = []

        if 20 <= words <= 180:
            strengths.append(
                "The answer is reasonably focused in length."
            )

        if self._has_repetition(
            answer
        ):
            improvements.append(
                "Avoid repeating the same idea."
            )

        if words > 250:
            improvements.append(
                "Make the answer more concise by removing unnecessary details."
            )

        if words < 10:
            improvements.append(
                "Provide enough detail to fully answer the question."
            )

        return CommunicationDimension(
            name="conciseness",
            score=score,
            weight=self.weights[
                "conciseness"
            ],
            feedback=(
                "The response is appropriately focused."
                if score >= 75
                else
                "The response could be more focused or sufficiently detailed."
            ),
            strengths=strengths,
            improvements=improvements,
        )

    # ------------------------------------------------------------------
    # Vocabulary
    # ------------------------------------------------------------------

    def _score_vocabulary(
        self,
        answer: str,
    ) -> CommunicationDimension:
        """Evaluate vocabulary variety and appropriateness."""

        words = re.findall(
            r"\b[a-zA-Z]+\b",
            answer.lower(),
        )

        if not words:
            score = 0.0
        else:
            unique_words = set(
                words
            )

            lexical_diversity = (
                len(unique_words)
                / len(words)
            )

            score = 55.0

            if lexical_diversity >= 0.70:
                score += 25

            elif lexical_diversity >= 0.55:
                score += 15

            elif lexical_diversity >= 0.40:
                score += 8

            if len(unique_words) >= 30:
                score += 10

        if self._has_excessive_fillers(
            answer
        ):
            score -= 10

        score = self._clamp(
            score
        )

        strengths: List[str] = []
        improvements: List[str] = []

        if score >= 75:
            strengths.append(
                "The response uses varied and appropriate vocabulary."
            )

        if score < 70:
            improvements.append(
                "Use precise words instead of repeated or vague expressions."
            )

        return CommunicationDimension(
            name="vocabulary",
            score=score,
            weight=self.weights[
                "vocabulary"
            ],
            feedback=(
                "Vocabulary is varied and appropriate."
                if score >= 75
                else
                "Vocabulary could be more precise and varied."
            ),
            strengths=strengths,
            improvements=improvements,
        )

    # ------------------------------------------------------------------
    # Professionalism
    # ------------------------------------------------------------------

    def _score_professionalism(
        self,
        answer: str,
    ) -> CommunicationDimension:
        """Evaluate professional communication style."""

        score = 75.0

        answer_lower = answer.lower()

        unprofessional_markers = [
            "whatever",
            "stuff",
            "thingy",
            "you know",
            "i don't know anything",
            "no idea",
            "that's stupid",
            "obviously",
        ]

        filler_markers = [
            "um",
            "uh",
            "like",
            "basically",
            "actually",
            "literally",
            "you know",
        ]

        for marker in unprofessional_markers:
            if marker in answer_lower:
                score -= 8

        filler_count = sum(
            answer_lower.count(
                marker
            )
            for marker in filler_markers
        )

        if filler_count >= 4:
            score -= 10

        if self._has_positive_professional_language(
            answer
        ):
            score += 10

        score = self._clamp(
            score
        )

        strengths: List[str] = []
        improvements: List[str] = []

        if score >= 80:
            strengths.append(
                "The communication style is professional and interview-appropriate."
            )

        if filler_count >= 4:
            improvements.append(
                "Reduce repeated filler expressions."
            )

        if any(
            marker in answer_lower
            for marker in unprofessional_markers
        ):
            improvements.append(
                "Use more professional and precise wording."
            )

        return CommunicationDimension(
            name="professionalism",
            score=score,
            weight=self.weights[
                "professionalism"
            ],
            feedback=(
                "The response uses an appropriate professional tone."
                if score >= 75
                else
                "The response could use more professional wording."
            ),
            strengths=strengths,
            improvements=improvements,
        )

    # ------------------------------------------------------------------
    # Completeness
    # ------------------------------------------------------------------

    def _calculate_completeness(
        self,
        answer: str,
        expected_points: List[str],
    ) -> float:
        """Calculate coverage of expected communication points."""

        if not expected_points:
            return 100.0

        answer_lower = answer.lower()

        covered = 0

        for point in expected_points:
            point = str(
                point
            ).strip().lower()

            if not point:
                continue

            if point in answer_lower:
                covered += 1
                continue

            tokens = self._tokens(
                point
            )

            answer_tokens = self._tokens(
                answer_lower
            )

            if tokens:
                overlap = (
                    len(
                        tokens
                        & answer_tokens
                    )
                    / len(tokens)
                )

                if overlap >= 0.50:
                    covered += 1

        return (
            covered
            / len(expected_points)
            * 100.0
        )

    # ------------------------------------------------------------------
    # Utility Heuristics
    # ------------------------------------------------------------------

    @staticmethod
    def _has_clear_sentences(
        answer: str,
    ) -> bool:
        """Check whether sentences appear reasonably formed."""

        sentences = re.split(
            r"[.!?]+",
            answer,
        )

        valid = 0

        for sentence in sentences:
            words = sentence.split()

            if 3 <= len(words) <= 40:
                valid += 1

        return valid >= 1

    @staticmethod
    def _has_long_sentences(
        answer: str,
    ) -> bool:
        """Detect very long sentences."""

        sentences = re.split(
            r"[.!?]+",
            answer,
        )

        return any(
            len(sentence.split()) > 40
            for sentence in sentences
            if sentence.strip()
        )

    @staticmethod
    def _has_fragmented_answer(
        answer: str,
    ) -> bool:
        """Detect obviously fragmented responses."""

        fragments = re.findall(
            r"(?:^|[.!?])\s*[A-Z]?\s*(?:yes|no|because|and|but)\s*[.!?]",
            answer,
            flags=re.IGNORECASE,
        )

        return len(fragments) >= 3

    @staticmethod
    def _has_excessive_fillers(
        answer: str,
    ) -> bool:
        """Detect repeated filler expressions."""

        fillers = [
            "um",
            "uh",
            "like",
            "basically",
            "actually",
            "you know",
            "kind of",
            "sort of",
        ]

        text = answer.lower()

        count = sum(
            text.count(filler)
            for filler in fillers
        )

        return count >= 5

    @staticmethod
    def _has_repetition(
        answer: str,
    ) -> bool:
        """Detect repeated consecutive words."""

        words = re.findall(
            r"\b[a-zA-Z]+\b",
            answer.lower(),
        )

        if len(words) < 4:
            return False

        repeated = 0

        for first, second in zip(
            words,
            words[1:],
        ):
            if first == second:
                repeated += 1

        return repeated >= 2

    @staticmethod
    def _has_opening_phrase(
        answer: str,
    ) -> bool:
        """Detect useful opening phrases."""

        phrases = [
            "first",
            "to begin",
            "in my experience",
            "the main",
            "my approach",
            "i would",
            "i think",
            "in this situation",
        ]

        text = answer.lower()

        return any(
            phrase in text
            for phrase in phrases
        )

    @staticmethod
    def _has_sequence_markers(
        answer: str,
    ) -> bool:
        """Detect sequencing language."""

        markers = [
            "first",
            "second",
            "third",
            "then",
            "next",
            "finally",
            "after that",
            "initially",
            "later",
        ]

        text = answer.lower()

        return sum(
            marker in text
            for marker in markers
        ) >= 2

    @staticmethod
    def _has_conclusion(
        answer: str,
    ) -> bool:
        """Detect concluding language."""

        markers = [
            "finally",
            "in conclusion",
            "overall",
            "as a result",
            "ultimately",
            "this helped",
            "the result was",
            "so",
        ]

        text = answer.lower()

        return any(
            marker in text
            for marker in markers
        )

    @staticmethod
    def _has_list_structure(
        answer: str,
    ) -> bool:
        """Detect list-like organization."""

        markers = [
            "first",
            "second",
            "third",
            "one reason",
            "another reason",
            "finally",
        ]

        text = answer.lower()

        return sum(
            marker in text
            for marker in markers
        ) >= 2

    @staticmethod
    def _has_positive_professional_language(
        answer: str,
    ) -> bool:
        """Detect professional language."""

        markers = [
            "collaborated",
            "implemented",
            "improved",
            "resolved",
            "analyzed",
            "communicated",
            "coordinated",
            "delivered",
            "responsible",
            "experience",
        ]

        text = answer.lower()

        return any(
            marker in text
            for marker in markers
        )

    # ------------------------------------------------------------------
    # Score Helpers
    # ------------------------------------------------------------------

    def _calculate_score(
        self,
        dimensions: List[
            CommunicationDimension
        ],
    ) -> float:
        """Calculate weighted communication score."""

        total_weight = sum(
            dimension.weight
            for dimension in dimensions
        )

        if total_weight <= 0:
            return 0.0

        weighted_score = sum(
            dimension.score
            * dimension.weight
            for dimension in dimensions
        )

        return (
            weighted_score
            / total_weight
        )

    @staticmethod
    def _determine_level(
        score: float,
    ) -> str:
        """Map score to communication level."""

        if score >= 90:
            return "excellent"

        if score >= 80:
            return "strong"

        if score >= 70:
            return "good"

        if score >= 60:
            return "developing"

        return "needs_improvement"

    @staticmethod
    def _recommendation(
        score: float,
    ) -> str:
        """Generate communication recommendation."""

        if score >= 90:
            return "excellent_communication"

        if score >= 80:
            return "strong_communication"

        if score >= 70:
            return "good_communication"

        if score >= 60:
            return "communication_can_be_improved"

        return "significant_communication_improvement_needed"

    @staticmethod
    def _clamp(
        value: float,
    ) -> float:
        """Clamp score between 0 and 100."""

        return max(
            0.0,
            min(100.0, value),
        )

    @staticmethod
    def _collect_strengths(
        dimensions: List[
            CommunicationDimension
        ],
    ) -> List[str]:
        """Collect strengths."""

        result: List[str] = []

        for dimension in dimensions:
            result.extend(
                dimension.strengths
            )

        return result

    @staticmethod
    def _collect_improvements(
        dimensions: List[
            CommunicationDimension
        ],
    ) -> List[str]:
        """Collect improvements."""

        result: List[str] = []

        for dimension in dimensions:
            result.extend(
                dimension.improvements
            )

        return result

    @staticmethod
    def _unique(
        values: List[str],
    ) -> List[str]:
        """Remove duplicates while preserving order."""

        result: List[str] = []

        for value in values:
            if value and value not in result:
                result.append(value)

        return result

    @staticmethod
    def _tokens(
        text: str,
    ) -> set[str]:
        """Extract normalized content tokens."""

        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
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
            "that",
            "this",
            "it",
            "i",
            "we",
            "you",
        }

        tokens = re.findall(
            r"\b[a-zA-Z][a-zA-Z0-9_-]*\b",
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

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_question(
        question: str,
    ) -> str:
        """Validate interview question."""

        if question is None:
            raise InvalidCommunicationInputError(
                "Question cannot be None."
            )

        question = str(
            question
        ).strip()

        if not question:
            raise InvalidCommunicationInputError(
                "Question cannot be empty."
            )

        return question

    @staticmethod
    def _validate_answer(
        answer: str,
    ) -> str:
        """Validate candidate answer."""

        if answer is None:
            raise EmptyCommunicationAnswerError(
                "Answer cannot be None."
            )

        answer = str(
            answer
        ).strip()

        if not answer:
            raise EmptyCommunicationAnswerError(
                "Answer cannot be empty."
            )

        return answer

    def _validate_weights(self) -> None:
        """Validate scoring weights."""

        required = set(
            self.DEFAULT_WEIGHTS.keys()
        )

        missing = (
            required
            - set(self.weights.keys())
        )

        if missing:
            raise InvalidCommunicationInputError(
                "Missing communication weights: "
                + ", ".join(
                    sorted(missing)
                )
            )

        if any(
            weight < 0
            for weight in self.weights.values()
        ):
            raise InvalidCommunicationInputError(
                "Communication weights cannot be negative."
            )

        if sum(
            self.weights.values()
        ) <= 0:
            raise InvalidCommunicationInputError(
                "At least one communication weight "
                "must be greater than zero."
            )


# ----------------------------------------------------------------------
# Convenience Function
# ----------------------------------------------------------------------


def evaluate_communication(
    question: str,
    answer: str,
    expected_points: Optional[
        List[str]
    ] = None,
    answer_type: Optional[str] = None,
) -> CommunicationEvaluation:
    """
    Convenience wrapper for CommunicationEvaluator.
    """

    evaluator = CommunicationEvaluator()

    return evaluator.evaluate(
        question=question,
        answer=answer,
        expected_points=expected_points,
        answer_type=answer_type,
    )


__all__ = [
    "CommunicationEvaluator",
    "CommunicationEvaluation",
    "CommunicationDimension",
    "CommunicationEvaluationError",
    "EmptyCommunicationAnswerError",
    "InvalidCommunicationInputError",
    "evaluate_communication",
]