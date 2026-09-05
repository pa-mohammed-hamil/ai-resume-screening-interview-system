"""
Interview Scorecard.

Provides a structured scorecard for interview results.

Responsibilities:
- Store interview category scores
- Calculate weighted overall score
- Calculate performance levels
- Track question-level scores
- Identify strengths and improvement areas
- Provide recruiter-friendly and candidate-friendly views
- Produce JSON-serializable output

This module is intentionally separate from report_generator.py:
    scorecard.py       -> scoring/score representation
    report_generator.py -> narrative report generation
    recommendations.py -> next-step recommendations
    pdf_report.py      -> PDF presentation
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from statistics import mean
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------


class ScorecardError(Exception):
    """Base exception for scorecard errors."""


class InvalidScoreError(ScorecardError):
    """Raised when a score is invalid."""


class EmptyScorecardError(ScorecardError):
    """Raised when no scores are available."""


# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------


DEFAULT_WEIGHTS: Dict[str, float] = {
    "technical": 0.45,
    "communication": 0.30,
    "confidence": 0.25,
}


PERFORMANCE_THRESHOLDS = {
    "excellent": 90,
    "very_good": 80,
    "good": 70,
    "developing": 60,
}


# ----------------------------------------------------------------------
# Data Classes
# ----------------------------------------------------------------------


@dataclass
class ScoreItem:
    """Represents one score category."""

    name: str
    score: float
    weight: float

    weighted_score: float = 0.0

    question_count: int = 0

    strengths: List[str] = field(
        default_factory=list
    )

    improvement_areas: List[str] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        self.score = clamp_score(
            self.score
        )

        self.weight = max(
            0.0,
            float(self.weight),
        )

        self.weighted_score = (
            self.score * self.weight
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class QuestionScore:
    """Score information for an individual interview question."""

    question_id: str
    question: str

    overall_score: float

    technical_score: Optional[float] = None
    communication_score: Optional[float] = None
    confidence_score: Optional[float] = None

    strengths: List[str] = field(
        default_factory=list
    )

    improvement_areas: List[str] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        self.overall_score = clamp_score(
            self.overall_score
        )

        if self.technical_score is not None:
            self.technical_score = clamp_score(
                self.technical_score
            )

        if self.communication_score is not None:
            self.communication_score = clamp_score(
                self.communication_score
            )

        if self.confidence_score is not None:
            self.confidence_score = clamp_score(
                self.confidence_score
            )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class InterviewScorecard:
    """Complete interview scorecard."""

    interview_id: Optional[str]

    overall_score: float

    performance_level: str

    categories: List[ScoreItem]

    questions: List[QuestionScore]

    strengths: List[str]

    improvement_areas: List[str]

    generated_at: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interview_id": self.interview_id,
            "overall_score": self.overall_score,
            "performance_level": self.performance_level,
            "categories": [
                category.to_dict()
                for category in self.categories
            ],
            "questions": [
                question.to_dict()
                for question in self.questions
            ],
            "strengths": self.strengths,
            "improvement_areas": self.improvement_areas,
            "generated_at": self.generated_at,
            "metadata": self.metadata,
        }

    def category(
        self,
        name: str,
    ) -> Optional[ScoreItem]:
        """Return a category by name."""

        name = name.lower()

        for category in self.categories:
            if category.name.lower() == name:
                return category

        return None

    def strongest_category(
        self,
    ) -> Optional[ScoreItem]:
        """Return the highest-scoring category."""

        if not self.categories:
            return None

        return max(
            self.categories,
            key=lambda item: item.score,
        )

    def weakest_category(
        self,
    ) -> Optional[ScoreItem]:
        """Return the lowest-scoring category."""

        if not self.categories:
            return None

        return min(
            self.categories,
            key=lambda item: item.score,
        )


# ----------------------------------------------------------------------
# Scorecard Builder
# ----------------------------------------------------------------------


class InterviewScorecardBuilder:
    """
    Builds an InterviewScorecard from question-level evaluations.

    Supported input:

        {
            "question_id": "q1",
            "question": "Explain REST.",
            "overall_score": 85,
            "technical": {"score": 90},
            "communication": {"score": 80},
            "confidence": {"score": 85},
            "strengths": [...],
            "improvements": [...]
        }

    Direct scores are also supported:

        {
            "technical_score": 90,
            "communication_score": 80,
            "confidence_score": 85,
            "overall_score": 85
        }
    """

    def __init__(
        self,
        weights: Optional[
            Mapping[str, float]
        ] = None,
    ) -> None:

        self.weights = dict(
            weights
            or DEFAULT_WEIGHTS
        )

        self._validate_weights()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build(
        self,
        evaluations: Sequence[Any],
        interview_id: Optional[str] = None,
        metadata: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> InterviewScorecard:
        """
        Build an interview scorecard.

        Args:
            evaluations:
                Question-level evaluation results.

            interview_id:
                Optional interview identifier.

            metadata:
                Optional metadata.

        Returns:
            InterviewScorecard
        """

        if not evaluations:
            raise EmptyScorecardError(
                "Cannot build a scorecard without evaluations."
            )

        question_scores = [
            self._normalize_question(
                evaluation,
                index,
            )
            for index, evaluation
            in enumerate(
                evaluations,
                start=1,
            )
        ]

        categories = (
            self._build_categories(
                question_scores
            )
        )

        overall_score = (
            self._calculate_overall(
                categories,
                question_scores,
            )
        )

        strengths = (
            collect_feedback(
                question_scores,
                "strengths",
            )
        )

        improvement_areas = (
            collect_feedback(
                question_scores,
                "improvement_areas",
            )
        )

        return InterviewScorecard(
            interview_id=interview_id,
            overall_score=round(
                overall_score,
                2,
            ),
            performance_level=(
                performance_level(
                    overall_score
                )
            ),
            categories=categories,
            questions=question_scores,
            strengths=strengths,
            improvement_areas=improvement_areas,
            generated_at=(
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
            metadata=dict(
                metadata or {}
            ),
        )

    # ------------------------------------------------------------------
    # Question Normalization
    # ------------------------------------------------------------------

    def _normalize_question(
        self,
        evaluation: Any,
        index: int,
    ) -> QuestionScore:
        """Normalize an evaluation object."""

        if isinstance(
            evaluation,
            QuestionScore,
        ):
            return evaluation

        evaluation = self._to_dict(
            evaluation
        )

        if not isinstance(
            evaluation,
            dict,
        ):
            raise InvalidScoreError(
                f"Evaluation #{index} is not a valid mapping."
            )

        question_id = str(
            evaluation.get(
                "question_id",
                f"question-{index}",
            )
        )

        question = str(
            evaluation.get(
                "question",
                "",
            )
        )

        technical = self._extract_score(
            evaluation,
            "technical",
            "technical_score",
        )

        communication = self._extract_score(
            evaluation,
            "communication",
            "communication_score",
        )

        confidence = self._extract_score(
            evaluation,
            "confidence",
            "confidence_score",
        )

        overall = self._extract_score(
            evaluation,
            "overall_score",
        )

        if overall is None:
            overall = self._calculate_question_overall(
                technical,
                communication,
                confidence,
            )

        if overall is None:
            raise InvalidScoreError(
                f"Evaluation #{index} contains no usable score."
            )

        strengths = extract_list(
            evaluation.get(
                "strengths",
                [],
            )
        )

        improvements = extract_list(
            evaluation.get(
                "improvements",
                evaluation.get(
                    "improvement_areas",
                    [],
                ),
            )
        )

        return QuestionScore(
            question_id=question_id,
            question=question,
            overall_score=overall,
            technical_score=technical,
            communication_score=communication,
            confidence_score=confidence,
            strengths=strengths,
            improvement_areas=improvements,
        )

    # ------------------------------------------------------------------
    # Category Building
    # ------------------------------------------------------------------

    def _build_categories(
        self,
        questions: Sequence[
            QuestionScore
        ],
    ) -> List[ScoreItem]:
        """Build category score objects."""

        categories: List[ScoreItem] = []

        for category_name in (
            "technical",
            "communication",
            "confidence",
        ):
            scores = []

            for question in questions:
                score = getattr(
                    question,
                    f"{category_name}_score",
                )

                if score is not None:
                    scores.append(
                        score
                    )

            if scores:
                category_score = mean(
                    scores
                )
            else:
                category_score = mean(
                    question.overall_score
                    for question in questions
                )

            category_questions = [
                question
                for question in questions
                if getattr(
                    question,
                    f"{category_name}_score",
                )
                is not None
            ]

            strengths = self._category_feedback(
                category_questions,
                category_name,
                feedback_type="strengths",
            )

            improvements = self._category_feedback(
                category_questions,
                category_name,
                feedback_type="improvement_areas",
            )

            categories.append(
                ScoreItem(
                    name=category_name,
                    score=category_score,
                    weight=self.weights[
                        category_name
                    ],
                    question_count=len(
                        scores
                    ),
                    strengths=strengths,
                    improvement_areas=improvements,
                )
            )

        return categories

    def _category_feedback(
        self,
        questions: Sequence[
            QuestionScore
        ],
        category_name: str,
        feedback_type: str,
    ) -> List[str]:
        """
        Extract feedback associated with a category.

        Since question-level feedback can be broad, the method uses
        the category score to decide whether the feedback is relevant.
        """

        result: List[str] = []

        for question in questions:

            score = getattr(
                question,
                f"{category_name}_score",
            )

            if score is None:
                continue

            if (
                feedback_type == "strengths"
                and score >= 80
            ):
                result.extend(
                    question.strengths
                )

            elif (
                feedback_type
                == "improvement_areas"
                and score < 75
            ):
                result.extend(
                    question.improvement_areas
                )

        return unique_values(
            result
        )[:5]

    # ------------------------------------------------------------------
    # Overall Calculation
    # ------------------------------------------------------------------

    def _calculate_overall(
        self,
        categories: Sequence[
            ScoreItem
        ],
        questions: Sequence[
            QuestionScore
        ],
    ) -> float:
        """
        Calculate weighted overall interview score.

        Categories without actual scores are excluded from the weighted
        calculation and the remaining weights are normalized.
        """

        available = [
            category
            for category in categories
            if category.question_count > 0
        ]

        if not available:
            return mean(
                question.overall_score
                for question in questions
            )

        total_weight = sum(
            category.weight
            for category in available
        )

        if total_weight <= 0:
            return mean(
                question.overall_score
                for question in questions
            )

        return (
            sum(
                category.score
                * category.weight
                for category in available
            )
            / total_weight
        )

    def _calculate_question_overall(
        self,
        technical: Optional[float],
        communication: Optional[float],
        confidence: Optional[float],
    ) -> Optional[float]:
        """Calculate weighted question score."""

        values = []

        if technical is not None:
            values.append(
                (
                    technical,
                    self.weights[
                        "technical"
                    ],
                )
            )

        if communication is not None:
            values.append(
                (
                    communication,
                    self.weights[
                        "communication"
                    ],
                )
            )

        if confidence is not None:
            values.append(
                (
                    confidence,
                    self.weights[
                        "confidence"
                    ],
                )
            )

        if not values:
            return None

        total_weight = sum(
            weight
            for _, weight in values
        )

        return (
            sum(
                score * weight
                for score, weight in values
            )
            / total_weight
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_dict(
        value: Any,
    ) -> Any:
        """Convert supported objects into dictionaries."""

        if isinstance(
            value,
            dict,
        ):
            return value

        if hasattr(
            value,
            "to_dict",
        ):
            return value.to_dict()

        if hasattr(
            value,
            "__dict__",
        ):
            return vars(
                value
            )

        return value

    @staticmethod
    def _extract_score(
        data: Mapping[str, Any],
        nested_key: str,
        direct_key: Optional[str] = None,
    ) -> Optional[float]:
        """Extract a score from nested or direct fields."""

        value = data.get(
            nested_key
        )

        if value is None and direct_key:
            value = data.get(
                direct_key
            )

        if isinstance(
            value,
            Mapping,
        ):
            value = value.get(
                "score"
            )

        if value is None:
            return None

        try:
            return clamp_score(
                float(value)
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise InvalidScoreError(
                f"Invalid score for '{nested_key}': {value}"
            ) from exc

    def _validate_weights(self) -> None:
        """Validate score weights."""

        required = {
            "technical",
            "communication",
            "confidence",
        }

        missing = (
            required
            - set(
                self.weights
            )
        )

        if missing:
            raise InvalidScoreError(
                "Missing score weights: "
                + ", ".join(
                    sorted(missing)
                )
            )

        if any(
            weight < 0
            for weight
            in self.weights.values()
        ):
            raise InvalidScoreError(
                "Score weights cannot be negative."
            )

        if sum(
            self.weights.values()
        ) <= 0:
            raise InvalidScoreError(
                "At least one score weight must be positive."
            )


# ----------------------------------------------------------------------
# Public Utility Functions
# ----------------------------------------------------------------------


def clamp_score(
    score: float,
) -> float:
    """Clamp a score to the 0-100 range."""

    score = float(
        score
    )

    if score < 0:
        return 0.0

    if score > 100:
        return 100.0

    return score


def performance_level(
    score: float,
) -> str:
    """Convert numeric score to performance level."""

    score = clamp_score(
        score
    )

    if score >= PERFORMANCE_THRESHOLDS[
        "excellent"
    ]:
        return "excellent"

    if score >= PERFORMANCE_THRESHOLDS[
        "very_good"
    ]:
        return "very_good"

    if score >= PERFORMANCE_THRESHOLDS[
        "good"
    ]:
        return "good"

    if score >= PERFORMANCE_THRESHOLDS[
        "developing"
    ]:
        return "developing"

    return "needs_improvement"


def collect_feedback(
    questions: Sequence[
        QuestionScore
    ],
    attribute: str,
    limit: int = 6,
) -> List[str]:
    """Collect unique feedback from question scores."""

    result: List[str] = []

    for question in questions:
        values = getattr(
            question,
            attribute,
            [],
        )

        for value in values:

            text = str(
                value
            ).strip()

            if (
                text
                and text not in result
            ):
                result.append(
                    text
                )

            if len(result) >= limit:
                return result

    return result


def extract_list(
    value: Any,
) -> List[str]:
    """Normalize feedback input into a list of strings."""

    if value is None:
        return []

    if isinstance(
        value,
        str,
    ):
        return (
            [value.strip()]
            if value.strip()
            else []
        )

    if isinstance(
        value,
        Iterable,
    ):
        result = []

        for item in value:
            text = str(
                item
            ).strip()

            if text:
                result.append(
                    text
                )

        return result

    return []


def unique_values(
    values: Sequence[str],
) -> List[str]:
    """Return unique non-empty strings."""

    result: List[str] = []

    for value in values:
        text = str(
            value
        ).strip()

        if (
            text
            and text not in result
        ):
            result.append(
                text
            )

    return result


# ----------------------------------------------------------------------
# Convenience API
# ----------------------------------------------------------------------


def build_scorecard(
    evaluations: Sequence[Any],
    interview_id: Optional[str] = None,
    metadata: Optional[
        Mapping[str, Any]
    ] = None,
    weights: Optional[
        Mapping[str, float]
    ] = None,
) -> InterviewScorecard:
    """
    Convenience function for building an interview scorecard.
    """

    builder = InterviewScorecardBuilder(
        weights=weights
    )

    return builder.build(
        evaluations=evaluations,
        interview_id=interview_id,
        metadata=metadata,
    )


# ----------------------------------------------------------------------
# Exports
# ----------------------------------------------------------------------


__all__ = [
    "ScoreItem",
    "QuestionScore",
    "InterviewScorecard",
    "InterviewScorecardBuilder",
    "ScorecardError",
    "InvalidScoreError",
    "EmptyScorecardError",
    "DEFAULT_WEIGHTS",
    "PERFORMANCE_THRESHOLDS",
    "clamp_score",
    "performance_level",
    "collect_feedback",
    "extract_list",
    "unique_values",
    "build_scorecard",
]