# Project scaffold file
"""
Confidence Interview Answer Evaluator.

Evaluates observable confidence indicators in an interview response.

The evaluator can work with:
1. Text-only answers.
2. Text + optional voice/audio metrics.

Supported indicators include:
- Directness
- Assertiveness
- Hedging
- Uncertainty
- Answer completion
- Self-correction
- Voice stability metrics when supplied

Important:
    Confidence is not inferred from accent, dialect, gender, personality,
    native language, or other protected/personal characteristics.

The result is an interview communication signal, not a psychological
diagnosis or hiring decision.
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


class ConfidenceEvaluationError(Exception):
    """Base exception for confidence evaluation errors."""


class EmptyConfidenceAnswerError(
    ConfidenceEvaluationError
):
    """Raised when an answer is empty."""


class InvalidConfidenceInputError(
    ConfidenceEvaluationError
):
    """Raised when confidence evaluation input is invalid."""


# ----------------------------------------------------------------------
# Data Models
# ----------------------------------------------------------------------


@dataclass
class ConfidenceDimension:
    """Represents one confidence scoring dimension."""

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
class ConfidenceEvaluation:
    """Complete confidence evaluation."""

    question: str
    answer: str
    score: float

    confidence_level: str = "unknown"

    dimensions: List[ConfidenceDimension] = field(
        default_factory=list
    )

    strengths: List[str] = field(
        default_factory=list
    )

    improvements: List[str] = field(
        default_factory=list
    )

    indicators: Dict[str, Any] = field(
        default_factory=dict
    )

    recommendation: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question": self.question,
            "answer": self.answer,
            "score": round(self.score, 2),
            "confidence_level": self.confidence_level,
            "dimensions": [
                dimension.to_dict()
                for dimension in self.dimensions
            ],
            "strengths": self.strengths,
            "improvements": self.improvements,
            "indicators": self.indicators,
            "recommendation": self.recommendation,
            "metadata": self.metadata,
        }


# ----------------------------------------------------------------------
# Evaluator
# ----------------------------------------------------------------------


class ConfidenceEvaluator:
    """
    Evaluate observable confidence indicators in an interview answer.

    Default weights:

        directness       25%
        assertiveness    20%
        uncertainty      20%
        fluency          15%
        completeness     10%
        stability        10%

    Example:

        evaluator = ConfidenceEvaluator()

        result = evaluator.evaluate(
            question="Why should we hire you?",
            answer=(
                "I have strong Python experience and have built "
                "backend APIs in several projects. I can contribute "
                "quickly because I am comfortable working with FastAPI "
                "and PostgreSQL."
            ),
        )

        print(result.score)
    """

    DEFAULT_WEIGHTS = {
        "directness": 0.25,
        "assertiveness": 0.20,
        "uncertainty": 0.20,
        "fluency": 0.15,
        "completeness": 0.10,
        "stability": 0.10,
    }

    # Observable hedging expressions.
    HEDGE_WORDS = {
        "maybe",
        "perhaps",
        "possibly",
        "probably",
        "might",
        "could",
        "somewhat",
        "generally",
        "i think",
        "i guess",
        "i believe",
        "i suppose",
        "kind of",
        "sort of",
        "hopefully",
        "likely",
    }

    UNCERTAINTY_PHRASES = {
        "i don't know",
        "not sure",
        "i am not sure",
        "i'm not sure",
        "i have no idea",
        "cannot remember",
        "can't remember",
        "i don't really know",
        "i'm unsure",
        "i am unsure",
    }

    ASSERTIVE_PHRASES = {
        "i achieved",
        "i implemented",
        "i designed",
        "i developed",
        "i solved",
        "i improved",
        "i led",
        "i delivered",
        "i built",
        "i managed",
        "i contributed",
        "i am confident",
        "i can",
        "i would",
        "my approach",
        "the result was",
    }

    SELF_CORRECTION_MARKERS = {
        "i mean",
        "sorry",
        "let me correct",
        "what i meant",
        "rather",
        "actually",
        "no,",
        "sorry,",
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
        voice_metrics: Optional[
            Dict[str, Any]
        ] = None,
        expected_points: Optional[
            List[str]
        ] = None,
    ) -> ConfidenceEvaluation:
        """
        Evaluate confidence indicators.

        Args:
            question:
                Interview question.

            answer:
                Candidate's answer.

            voice_metrics:
                Optional metrics produced by voice_analyzer.py.

                Supported examples:

                    {
                        "speech_rate_wpm": 135,
                        "pause_ratio": 0.12,
                        "volume_variation": 0.18,
                        "pitch_variation": 0.20,
                        "long_pause_count": 1
                    }

            expected_points:
                Optional points expected in the answer.

        Returns:
            ConfidenceEvaluation
        """

        question = self._validate_question(
            question
        )

        answer = self._validate_answer(
            answer
        )

        voice_metrics = (
            voice_metrics or {}
        )

        expected_points = (
            expected_points or []
        )

        directness = (
            self._score_directness(
                answer
            )
        )

        assertiveness = (
            self._score_assertiveness(
                answer
            )
        )

        uncertainty = (
            self._score_uncertainty(
                answer
            )
        )

        fluency = (
            self._score_fluency(
                answer
            )
        )

        completeness = (
            self._score_completeness(
                answer,
                expected_points,
            )
        )

        stability = (
            self._score_stability(
                voice_metrics
            )
        )

        dimensions = [
            directness,
            assertiveness,
            uncertainty,
            fluency,
            completeness,
            stability,
        ]

        score = self._calculate_weighted_score(
            dimensions
        )

        indicators = (
            self._extract_indicators(
                answer,
                voice_metrics,
            )
        )

        strengths = self._collect_strengths(
            dimensions
        )

        improvements = self._collect_improvements(
            dimensions
        )

        score = round(
            self._clamp(score),
            2,
        )

        confidence_level = (
            self._determine_level(
                score
            )
        )

        recommendation = (
            self._generate_recommendation(
                score
            )
        )

        return ConfidenceEvaluation(
            question=question,
            answer=answer,
            score=score,
            confidence_level=confidence_level,
            dimensions=dimensions,
            strengths=self._unique(
                strengths
            ),
            improvements=self._unique(
                improvements
            ),
            indicators=indicators,
            recommendation=recommendation,
            metadata={
                "voice_metrics_available": bool(
                    voice_metrics
                ),
                "expected_points_available": bool(
                    expected_points
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
    # Directness
    # ------------------------------------------------------------------

    def _score_directness(
        self,
        answer: str,
    ) -> ConfidenceDimension:
        """Evaluate whether the candidate answers directly."""

        score = 65.0

        words = self._word_count(
            answer
        )

        if words >= 10:
            score += 8

        if words >= 20:
            score += 7

        if self._has_direct_opening(
            answer
        ):
            score += 10

        if self._has_excessive_fillers(
            answer
        ):
            score -= 12

        if self._has_excessive_hedging(
            answer
        ):
            score -= 15

        score = self._clamp(
            score
        )

        strengths: List[str] = []
        improvements: List[str] = []

        if self._has_direct_opening(
            answer
        ):
            strengths.append(
                "The response gets to the main point directly."
            )

        if self._has_excessive_hedging(
            answer
        ):
            improvements.append(
                "Use more direct wording when you are certain about the point being made."
            )

        if self._has_excessive_fillers(
            answer
        ):
            improvements.append(
                "Reduce filler expressions before stating the main point."
            )

        return ConfidenceDimension(
            name="directness",
            score=score,
            weight=self.weights[
                "directness"
            ],
            feedback=(
                "The answer communicates its main point directly."
                if score >= 75
                else
                "The answer could be more direct."
            ),
            strengths=strengths,
            improvements=improvements,
        )

    # ------------------------------------------------------------------
    # Assertiveness
    # ------------------------------------------------------------------

    def _score_assertiveness(
        self,
        answer: str,
    ) -> CommunicationDimension:
        """Evaluate confident, evidence-based wording."""

        score = 60.0

        text = answer.lower()

        assertive_count = sum(
            1
            for phrase in self.ASSERTIVE_PHRASES
            if phrase in text
        )

        hedge_count = self._count_hedges(
            answer
        )

        score += min(
            25.0,
            assertive_count * 5.0,
        )

        score -= min(
            25.0,
            hedge_count * 4.0,
        )

        if self._contains_evidence_language(
            answer
        ):
            score += 10

        score = self._clamp(
            score
        )

        strengths: List[str] = []
        improvements: List[str] = []

        if assertive_count >= 2:
            strengths.append(
                "The response uses clear, evidence-based statements."
            )

        if self._contains_evidence_language(
            answer
        ):
            strengths.append(
                "The answer supports claims with outcomes or evidence."
            )

        if hedge_count >= 3:
            improvements.append(
                "Reduce unnecessary hedging and state your contribution more clearly."
            )

        return CommunicationDimension(
            name="assertiveness",
            score=score,
            weight=self.weights[
                "assertiveness"
            ],
            feedback=(
                "The wording is appropriately assertive."
                if score >= 75
                else
                "The response could communicate achievements and decisions more confidently."
            ),
            strengths=strengths,
            improvements=improvements,
        )

    # ------------------------------------------------------------------
    # Uncertainty
    # ------------------------------------------------------------------

    def _score_uncertainty(
        self,
        answer: str,
    ) -> CommunicationDimension:
        """
        Evaluate observable uncertainty markers.

        This does not claim to measure internal psychological
        confidence.
        """

        score = 85.0

        uncertainty_count = (
            self._count_uncertainty_markers(
                answer
            )
        )

        hedge_count = (
            self._count_hedges(
                answer
            )
        )

        correction_count = (
            self._count_self_corrections(
                answer
            )
        )

        score -= min(
            40.0,
            uncertainty_count * 12.0,
        )

        score -= min(
            25.0,
            max(0, hedge_count - 1) * 4.0,
        )

        score -= min(
            15.0,
            correction_count * 5.0,
        )

        score = self._clamp(
            score
        )

        strengths: List[str] = []
        improvements: List[str] = []

        if uncertainty_count == 0:
            strengths.append(
                "The answer contains few explicit uncertainty markers."
            )

        if uncertainty_count >= 2:
            improvements.append(
                "When you know the answer, replace repeated uncertainty phrases with a clear explanation."
            )

        if correction_count >= 2:
            improvements.append(
                "Pause briefly before answering to reduce unnecessary self-corrections."
            )

        return CommunicationDimension(
            name="uncertainty",
            score=score,
            weight=self.weights[
                "uncertainty"
            ],
            feedback=(
                "The response contains limited explicit uncertainty."
                if score >= 75
                else
                "The response contains several observable uncertainty markers."
            ),
            strengths=strengths,
            improvements=improvements,
        )

    # ------------------------------------------------------------------
    # Fluency
    # ------------------------------------------------------------------

    def _score_fluency(
        self,
        answer: str,
    ) -> CommunicationDimension:
        """Evaluate textual fluency indicators."""

        score = 70.0

        words = self._word_count(
            answer
        )

        sentences = self._sentence_count(
            answer
        )

        if words >= 20:
            score += 8

        if sentences >= 2:
            score += 7

        if self._has_excessive_fillers(
            answer
        ):
            score -= 15

        if self._has_fragmented_answer(
            answer
        ):
            score -= 15

        if self._has_long_sentences(
            answer
        ):
            score -= 8

        score = self._clamp(
            score
        )

        strengths: List[str] = []
        improvements: List[str] = []

        if not self._has_excessive_fillers(
            answer
        ):
            strengths.append(
                "The response has relatively few filler expressions."
            )

        if self._has_excessive_fillers(
            answer
        ):
            improvements.append(
                "Reduce filler words and allow short pauses instead."
            )

        if self._has_fragmented_answer(
            answer
        ):
            improvements.append(
                "Complete one thought before moving to the next."
            )

        return CommunicationDimension(
            name="fluency",
            score=score,
            weight=self.weights[
                "fluency"
            ],
            feedback=(
                "The answer flows reasonably well."
                if score >= 75
                else
                "The answer contains some observable fluency issues."
            ),
            strengths=strengths,
            improvements=improvements,
        )

    # ------------------------------------------------------------------
    # Completeness
    # ------------------------------------------------------------------

    def _score_completeness(
        self,
        answer: str,
        expected_points: List[str],
    ) -> ConfidenceDimension:
        """Evaluate whether the answer is sufficiently complete."""

        if not expected_points:
            score = 75.0

            if self._word_count(answer) >= 20:
                score += 10

            if self._sentence_count(answer) >= 3:
                score += 5

        else:
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

            valid_points = len(
                [
                    point
                    for point in expected_points
                    if str(point).strip()
                ]
            )

            if valid_points:
                score = (
                    covered
                    / valid_points
                    * 100.0
                )
            else:
                score = 75.0

        score = self._clamp(
            score
        )

        strengths: List[str] = []
        improvements: List[str] = []

        if score >= 80:
            strengths.append(
                "The response gives enough information to support the main answer."
            )

        if score < 65:
            improvements.append(
                "Give a complete answer before stopping or changing topics."
            )

        return ConfidenceDimension(
            name="completeness",
            score=score,
            weight=self.weights[
                "completeness"
            ],
            feedback=(
                "The answer is sufficiently developed."
                if score >= 75
                else
                "The answer could be more complete."
            ),
            strengths=strengths,
            improvements=improvements,
        )

    # ------------------------------------------------------------------
    # Voice Stability
    # ------------------------------------------------------------------

    def _score_stability(
        self,
        voice_metrics: Dict[str, Any],
    ) -> ConfidenceDimension:
        """
        Evaluate optional voice stability metrics.

        If no voice metrics are available, the dimension receives a
        neutral score rather than penalizing the candidate.
        """

        if not voice_metrics:
            return CommunicationDimension(
                name="stability",
                score=75.0,
                weight=self.weights[
                    "stability"
                ],
                feedback=(
                    "No voice stability metrics were provided; "
                    "a neutral score was used."
                ),
                strengths=[],
                improvements=[],
            )

        score = 75.0

        pause_ratio = self._number(
            voice_metrics.get(
                "pause_ratio"
            )
        )

        long_pause_count = self._number(
            voice_metrics.get(
                "long_pause_count"
            )
        )

        speech_rate = self._number(
            voice_metrics.get(
                "speech_rate_wpm"
            )
        )

        volume_variation = self._number(
            voice_metrics.get(
                "volume_variation"
            )
        )

        if pause_ratio is not None:
            if 0.05 <= pause_ratio <= 0.25:
                score += 10

            elif pause_ratio > 0.45:
                score -= 15

        if long_pause_count is not None:
            if long_pause_count <= 2:
                score += 5

            elif long_pause_count >= 6:
                score -= 15

        if speech_rate is not None:
            if 100 <= speech_rate <= 180:
                score += 5

            elif speech_rate < 70:
                score -= 10

            elif speech_rate > 220:
                score -= 10

        if volume_variation is not None:
            if 0.05 <= volume_variation <= 0.40:
                score += 5

        score = self._clamp(
            score
        )

        strengths: List[str] = []
        improvements: List[str] = []

        if score >= 80:
            strengths.append(
                "Available voice metrics indicate reasonably stable delivery."
            )

        if pause_ratio is not None and pause_ratio > 0.45:
            improvements.append(
                "Consider shorter pauses between ideas."
            )

        if speech_rate is not None and speech_rate > 220:
            improvements.append(
                "Slow down slightly so key points remain easy to follow."
            )

        if speech_rate is not None and speech_rate < 70:
            improvements.append(
                "A slightly more consistent speaking pace may improve delivery."
            )

        return CommunicationDimension(
            name="stability",
            score=score,
            weight=self.weights[
                "stability"
            ],
            feedback=(
                "Available voice metrics indicate stable delivery."
                if score >= 75
                else
                "Available voice metrics suggest that delivery could be more stable."
            ),
            strengths=strengths,
            improvements=improvements,
        )

    # ------------------------------------------------------------------
    # Indicators
    # ------------------------------------------------------------------

    def _extract_indicators(
        self,
        answer: str,
        voice_metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Extract explainable confidence indicators."""

        return {
            "hedge_count": self._count_hedges(
                answer
            ),
            "uncertainty_count": (
                self._count_uncertainty_markers(
                    answer
                )
            ),
            "assertive_phrase_count": sum(
                1
                for phrase in self.ASSERTIVE_PHRASES
                if phrase in answer.lower()
            ),
            "self_correction_count": (
                self._count_self_corrections(
                    answer
                )
            ),
            "filler_detected": (
                self._has_excessive_fillers(
                    answer
                )
            ),
            "direct_opening": (
                self._has_direct_opening(
                    answer
                )
            ),
            "evidence_language_detected": (
                self._contains_evidence_language(
                    answer
                )
            ),
            "voice_metrics": dict(
                voice_metrics
            ),
        }

    # ------------------------------------------------------------------
    # Text Helpers
    # ------------------------------------------------------------------

    def _count_hedges(
        self,
        answer: str,
    ) -> int:
        """Count observable hedge expressions."""

        text = answer.lower()

        count = 0

        for phrase in self.HEDGE_WORDS:
            if " " in phrase:
                count += text.count(
                    phrase
                )
            else:
                count += len(
                    re.findall(
                        rf"\b{re.escape(phrase)}\b",
                        text,
                    )
                )

        return count

    def _count_uncertainty_markers(
        self,
        answer: str,
    ) -> int:
        """Count explicit uncertainty phrases."""

        text = answer.lower()

        return sum(
            text.count(
                phrase
            )
            for phrase in self.UNCERTAINTY_PHRASES
        )

    def _count_self_corrections(
        self,
        answer: str,
    ) -> int:
        """Count observable self-correction markers."""

        text = answer.lower()

        return sum(
            text.count(
                marker
            )
            for marker in self.SELF_CORRECTION_MARKERS
        )

    @staticmethod
    def _has_direct_opening(
        answer: str,
    ) -> bool:
        """Detect a direct answer opening."""

        phrases = [
            "yes,",
            "no,",
            "my answer is",
            "the main reason",
            "the key reason",
            "i would",
            "i can",
            "my approach",
            "i have",
            "i believe",
            "in my experience",
        ]

        text = answer.lower().strip()

        return any(
            text.startswith(
                phrase
            )
            for phrase in phrases
        )

    @staticmethod
    def _contains_evidence_language(
        answer: str,
    ) -> bool:
        """Detect evidence/outcome language."""

        markers = [
            "result",
            "improved",
            "increased",
            "reduced",
            "achieved",
            "delivered",
            "measured",
            "percent",
            "%",
            "users",
            "response time",
            "performance",
            "completed",
        ]

        text = answer.lower()

        return any(
            marker in text
            for marker in markers
        )

    @staticmethod
    def _has_excessive_hedging(
        answer: str,
    ) -> bool:
        """Detect excessive hedge usage."""

        text = answer.lower()

        phrases = [
            "maybe",
            "perhaps",
            "probably",
            "i think",
            "i guess",
            "i believe",
            "might",
            "could",
            "kind of",
            "sort of",
        ]

        count = sum(
            text.count(
                phrase
            )
            for phrase in phrases
        )

        return count >= 4

    @staticmethod
    def _has_excessive_fillers(
        answer: str,
    ) -> bool:
        """Detect repeated filler words."""

        text = answer.lower()

        fillers = [
            "um",
            "uh",
            "like",
            "basically",
            "actually",
            "literally",
            "you know",
            "kind of",
            "sort of",
        ]

        count = 0

        for filler in fillers:
            if " " in filler:
                count += text.count(
                    filler
                )
            else:
                count += len(
                    re.findall(
                        rf"\b{re.escape(filler)}\b",
                        text,
                    )
                )

        return count >= 5

    @staticmethod
    def _has_fragmented_answer(
        answer: str,
    ) -> bool:
        """Detect repeated incomplete fragments."""

        fragments = re.findall(
            r"(?:^|[.!?])\s*(?:yes|no|because|and|but)\s*[.!?]",
            answer,
            flags=re.IGNORECASE,
        )

        return len(fragments) >= 3

    @staticmethod
    def _has_long_sentences(
        answer: str,
    ) -> bool:
        """Detect excessively long sentences."""

        sentences = re.split(
            r"[.!?]+",
            answer,
        )

        return any(
            len(
                sentence.split()
            ) > 40
            for sentence in sentences
            if sentence.strip()
        )

    # ------------------------------------------------------------------
    # Scoring Helpers
    # ------------------------------------------------------------------

    def _calculate_weighted_score(
        self,
        dimensions: List[
            ConfidenceDimension
        ],
    ) -> float:
        """Calculate weighted confidence score."""

        total_weight = sum(
            dimension.weight
            for dimension in dimensions
        )

        if total_weight <= 0:
            return 0.0

        return sum(
            dimension.score
            * dimension.weight
            for dimension in dimensions
        ) / total_weight

    @staticmethod
    def _determine_level(
        score: float,
    ) -> str:
        """Map confidence score to a level."""

        if score >= 90:
            return "very_high"

        if score >= 80:
            return "high"

        if score >= 70:
            return "moderate"

        if score >= 60:
            return "developing"

        return "low"

    @staticmethod
    def _generate_recommendation(
        score: float,
    ) -> str:
        """Generate actionable recommendation."""

        if score >= 90:
            return "excellent_delivery"

        if score >= 80:
            return "strong_delivery"

        if score >= 70:
            return "good_delivery"

        if score >= 60:
            return "practice_clearer_delivery"

        return "focus_on_direct_and_structured_answers"

    @staticmethod
    def _collect_strengths(
        dimensions: List[
            ConfidenceDimension
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
            ConfidenceDimension
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
        """Remove duplicate feedback."""

        result: List[str] = []

        for value in values:
            if value and value not in result:
                result.append(value)

        return result

    @staticmethod
    def _clamp(
        value: float,
    ) -> float:
        """Clamp score to 0-100."""

        return max(
            0.0,
            min(100.0, value),
        )

    @staticmethod
    def _number(
        value: Any,
    ) -> Optional[float]:
        """Safely convert a value to float."""

        if value is None:
            return None

        try:
            return float(value)
        except (
            TypeError,
            ValueError,
        ):
            return None

    @staticmethod
    def _tokens(
        text: str,
    ) -> set[str]:
        """Extract normalized tokens."""

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
        """Validate question."""

        if question is None:
            raise InvalidConfidenceInputError(
                "Question cannot be None."
            )

        question = str(
            question
        ).strip()

        if not question:
            raise InvalidConfidenceInputError(
                "Question cannot be empty."
            )

        return question

    @staticmethod
    def _validate_answer(
        answer: str,
    ) -> str:
        """Validate answer."""

        if answer is None:
            raise EmptyConfidenceAnswerError(
                "Answer cannot be None."
            )

        answer = str(
            answer
        ).strip()

        if not answer:
            raise EmptyConfidenceAnswerError(
                "Answer cannot be empty."
            )

        return answer

    def _validate_weights(self) -> None:
        """Validate confidence weights."""

        required = set(
            self.DEFAULT_WEIGHTS.keys()
        )

        missing = (
            required
            - set(self.weights.keys())
        )

        if missing:
            raise InvalidConfidenceInputError(
                "Missing confidence weights: "
                + ", ".join(
                    sorted(missing)
                )
            )

        if any(
            weight < 0
            for weight in self.weights.values()
        ):
            raise InvalidConfidenceInputError(
                "Confidence weights cannot be negative."
            )

        if sum(
            self.weights.values()
        ) <= 0:
            raise InvalidConfidenceInputError(
                "At least one confidence weight "
                "must be greater than zero."
            )


# ----------------------------------------------------------------------
# Convenience Function
# ----------------------------------------------------------------------


def evaluate_confidence(
    question: str,
    answer: str,
    voice_metrics: Optional[
        Dict[str, Any]
    ] = None,
    expected_points: Optional[
        List[str]
    ] = None,
) -> ConfidenceEvaluation:
    """
    Convenience wrapper for ConfidenceEvaluator.
    """

    evaluator = ConfidenceEvaluator()

    return evaluator.evaluate(
        question=question,
        answer=answer,
        voice_metrics=voice_metrics,
        expected_points=expected_points,
    )


__all__ = [
    "ConfidenceEvaluator",
    "ConfidenceEvaluation",
    "ConfidenceDimension",
    "ConfidenceEvaluationError",
    "EmptyConfidenceAnswerError",
    "InvalidConfidenceInputError",
    "evaluate_confidence",
]