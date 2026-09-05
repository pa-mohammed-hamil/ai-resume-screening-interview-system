# Project scaffold file
"""
Interview Recommendations.

Generates structured recommendations from an interview scorecard.

Responsibilities:
- Analyze overall interview performance
- Analyze technical, communication, and confidence scores
- Identify priority development areas
- Suggest appropriate next interview steps
- Generate recruiter-facing recommendations
- Generate candidate-facing development suggestions

Important:
This module provides decision-support information only. It should not
automatically make a final hiring decision.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------


class RecommendationError(Exception):
    """Base exception for recommendation errors."""


class InvalidRecommendationInputError(
    RecommendationError
):
    """Raised when recommendation input is invalid."""


# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------


TECHNICAL = "technical"
COMMUNICATION = "communication"
CONFIDENCE = "confidence"

CATEGORY_NAMES = (
    TECHNICAL,
    COMMUNICATION,
    CONFIDENCE,
)


# ----------------------------------------------------------------------
# Data Models
# ----------------------------------------------------------------------


@dataclass
class RecommendationItem:
    """
    Represents one recommendation.
    """

    category: str

    priority: str

    title: str

    description: str

    action: str

    rationale: str

    score: Optional[float] = None

    evidence: List[str] = field(
        default_factory=list
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class InterviewRecommendations:
    """
    Complete recommendation result.
    """

    overall_score: float

    performance_level: str

    recommendation_status: str

    recruiter_recommendation: str

    candidate_recommendation: str

    recommendations: List[
        RecommendationItem
    ]

    priority_areas: List[str]

    strengths_to_retain: List[str]

    follow_up_actions: List[str]

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "performance_level": self.performance_level,
            "recommendation_status": (
                self.recommendation_status
            ),
            "recruiter_recommendation": (
                self.recruiter_recommendation
            ),
            "candidate_recommendation": (
                self.candidate_recommendation
            ),
            "recommendations": [
                recommendation.to_dict()
                for recommendation
                in self.recommendations
            ],
            "priority_areas": self.priority_areas,
            "strengths_to_retain": (
                self.strengths_to_retain
            ),
            "follow_up_actions": (
                self.follow_up_actions
            ),
            "metadata": self.metadata,
        }


# ----------------------------------------------------------------------
# Recommendation Generator
# ----------------------------------------------------------------------


class InterviewRecommendationEngine:
    """
    Generate recommendations from an InterviewScorecard.

    Expected scorecard structure:

        scorecard.overall_score
        scorecard.performance_level
        scorecard.categories
        scorecard.questions
        scorecard.strengths
        scorecard.improvement_areas

    The implementation also supports dictionary-based scorecards.
    """

    def __init__(
        self,
        technical_threshold: float = 65.0,
        communication_threshold: float = 65.0,
        confidence_threshold: float = 65.0,
        strong_score: float = 80.0,
        excellent_score: float = 90.0,
    ) -> None:

        self.technical_threshold = (
            technical_threshold
        )

        self.communication_threshold = (
            communication_threshold
        )

        self.confidence_threshold = (
            confidence_threshold
        )

        self.strong_score = strong_score
        self.excellent_score = excellent_score

        self._validate_thresholds()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        scorecard: Any,
        metadata: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> InterviewRecommendations:
        """
        Generate interview recommendations.

        Args:
            scorecard:
                InterviewScorecard or dictionary.

            metadata:
                Optional metadata.

        Returns:
            InterviewRecommendations
        """

        data = self._normalize_scorecard(
            scorecard
        )

        overall_score = self._get_overall_score(
            data
        )

        performance_level = (
            self._get_performance_level(
                data,
                overall_score,
            )
        )

        categories = (
            self._get_categories(
                data
            )
        )

        questions = (
            self._get_questions(
                data
            )
        )

        recommendations = (
            self._generate_category_recommendations(
                categories,
                questions,
            )
        )

        priority_areas = (
            self._identify_priority_areas(
                categories
            )
        )

        strengths = (
            self._get_strengths(
                data
            )
        )

        strengths_to_retain = (
            self._generate_strengths_to_retain(
                categories,
                strengths,
            )
        )

        status = (
            self._generate_status(
                overall_score,
                categories,
            )
        )

        recruiter_recommendation = (
            self._generate_recruiter_recommendation(
                overall_score,
                performance_level,
                categories,
                status,
            )
        )

        candidate_recommendation = (
            self._generate_candidate_recommendation(
                overall_score,
                categories,
            )
        )

        follow_up_actions = (
            self._generate_follow_up_actions(
                overall_score,
                categories,
            )
        )

        result_metadata = dict(
            metadata or {}
        )

        return InterviewRecommendations(
            overall_score=round(
                overall_score,
                2,
            ),
            performance_level=performance_level,
            recommendation_status=status,
            recruiter_recommendation=(
                recruiter_recommendation
            ),
            candidate_recommendation=(
                candidate_recommendation
            ),
            recommendations=recommendations,
            priority_areas=priority_areas,
            strengths_to_retain=(
                strengths_to_retain
            ),
            follow_up_actions=(
                follow_up_actions
            ),
            metadata=result_metadata,
        )

    # ------------------------------------------------------------------
    # Scorecard Normalization
    # ------------------------------------------------------------------

    def _normalize_scorecard(
        self,
        scorecard: Any,
    ) -> Dict[str, Any]:
        """
        Convert a scorecard object into a dictionary.
        """

        if isinstance(
            scorecard,
            Mapping,
        ):
            return dict(
                scorecard
            )

        if hasattr(
            scorecard,
            "to_dict",
        ):
            result = scorecard.to_dict()

            if isinstance(
                result,
                Mapping,
            ):
                return dict(
                    result
                )

        if hasattr(
            scorecard,
            "__dict__",
        ):
            return vars(
                scorecard
            )

        raise InvalidRecommendationInputError(
            "Scorecard must be a mapping or scorecard object."
        )

    # ------------------------------------------------------------------
    # Category Analysis
    # ------------------------------------------------------------------

    def _get_categories(
        self,
        scorecard: Mapping[str, Any],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Extract category scores.
        """

        categories = scorecard.get(
            "categories",
            [],
        )

        result: Dict[str, Dict[str, Any]] = {}

        if isinstance(
            categories,
            Mapping,
        ):
            for name, value in categories.items():

                if isinstance(
                    value,
                    Mapping,
                ):
                    result[
                        str(name).lower()
                    ] = dict(value)

                else:
                    result[
                        str(name).lower()
                    ] = {
                        "score": value
                    }

            return result

        for category in categories:

            if isinstance(
                category,
                Mapping,
            ):
                name = category.get(
                    "name"
                )

                if name:
                    result[
                        str(name).lower()
                    ] = dict(category)

            elif hasattr(
                category,
                "__dict__",
            ):
                name = getattr(
                    category,
                    "name",
                    None,
                )

                if name:
                    result[
                        str(name).lower()
                    ] = vars(
                        category
                    )

        return result

    def _get_questions(
        self,
        scorecard: Mapping[str, Any],
    ) -> List[Dict[str, Any]]:
        """Extract question scores."""

        questions = scorecard.get(
            "questions",
            [],
        )

        result = []

        for question in questions:

            if isinstance(
                question,
                Mapping,
            ):
                result.append(
                    dict(question)
                )

            elif hasattr(
                question,
                "__dict__",
            ):
                result.append(
                    vars(question)
                )

        return result

    def _get_overall_score(
        self,
        scorecard: Mapping[str, Any],
    ) -> float:
        """Extract and validate overall score."""

        value = scorecard.get(
            "overall_score"
        )

        if value is None:
            raise InvalidRecommendationInputError(
                "Scorecard does not contain overall_score."
            )

        try:
            score = float(
                value
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise InvalidRecommendationInputError(
                f"Invalid overall score: {value}"
            ) from exc

        return clamp(
            score
        )

    # ------------------------------------------------------------------
    # Recommendation Generation
    # ------------------------------------------------------------------

    def _generate_category_recommendations(
        self,
        categories: Mapping[
            str,
            Mapping[str, Any],
        ],
        questions: Sequence[
            Mapping[str, Any]
        ],
    ) -> List[
        RecommendationItem
    ]:
        """Generate recommendations for weak or moderate categories."""

        result: List[
            RecommendationItem
        ] = []

        for category_name in CATEGORY_NAMES:

            category = categories.get(
                category_name
            )

            if category is None:
                continue

            score = self._category_score(
                category
            )

            evidence = (
                self._category_evidence(
                    category_name,
                    questions,
                )
            )

            if score < 50:
                result.append(
                    RecommendationItem(
                        category=category_name,
                        priority="high",
                        title=(
                            f"Improve {category_name} performance"
                        ),
                        description=(
                            f"The {category_name} score is "
                            f"{score:.1f}/100 and should be "
                            "reviewed carefully."
                        ),
                        action=(
                            self._action_for_category(
                                category_name
                            )
                        ),
                        rationale=(
                            "The category score is below "
                            "the recommended baseline."
                        ),
                        score=score,
                        evidence=evidence,
                    )
                )

            elif score < 65:
                result.append(
                    RecommendationItem(
                        category=category_name,
                        priority="high",
                        title=(
                            f"Develop {category_name} skills"
                        ),
                        description=(
                            f"The {category_name} score is "
                            f"{score:.1f}/100."
                        ),
                        action=(
                            self._action_for_category(
                                category_name
                            )
                        ),
                        rationale=(
                            "The score indicates a meaningful "
                            "development opportunity."
                        ),
                        score=score,
                        evidence=evidence,
                    )
                )

            elif score < 75:
                result.append(
                    RecommendationItem(
                        category=category_name,
                        priority="medium",
                        title=(
                            f"Strengthen {category_name}"
                        ),
                        description=(
                            f"The {category_name} score is "
                            f"{score:.1f}/100."
                        ),
                        action=(
                            self._action_for_category(
                                category_name
                            )
                        ),
                        rationale=(
                            "The category is adequate but "
                            "could be strengthened."
                        ),
                        score=score,
                        evidence=evidence,
                    )
                )

        return result

    def _action_for_category(
        self,
        category: str,
    ) -> str:
        """Return a targeted improvement action."""

        actions = {
            TECHNICAL: (
                "Review core technical concepts, practice "
                "problem-solving questions, and explain "
                "solutions using concrete examples."
            ),
            COMMUNICATION: (
                "Practice structured answers using a clear "
                "beginning, explanation, example, and conclusion."
            ),
            CONFIDENCE: (
                "Practice answering aloud, reduce unnecessary "
                "pauses, and use concise, direct responses."
            ),
        }

        return actions.get(
            category,
            "Practice this area using structured interview questions.",
        )

    # ------------------------------------------------------------------
    # Priority Areas
    # ------------------------------------------------------------------

    def _identify_priority_areas(
        self,
        categories: Mapping[
            str,
            Mapping[str, Any],
        ],
    ) -> List[str]:
        """Identify categories requiring attention."""

        scored = []

        for category_name in CATEGORY_NAMES:

            category = categories.get(
                category_name
            )

            if category is None:
                continue

            score = self._category_score(
                category
            )

            scored.append(
                (
                    category_name,
                    score,
                )
            )

        scored.sort(
            key=lambda item: item[1]
        )

        return [
            category
            for category, score
            in scored
            if score < 75
        ][:3]

    # ------------------------------------------------------------------
    # Strengths
    # ------------------------------------------------------------------

    def _get_strengths(
        self,
        scorecard: Mapping[str, Any],
    ) -> List[str]:
        """Extract strengths."""

        strengths = scorecard.get(
            "strengths",
            [],
        )

        return normalize_list(
            strengths
        )

    def _generate_strengths_to_retain(
        self,
        categories: Mapping[
            str,
            Mapping[str, Any],
        ],
        strengths: Sequence[str],
    ) -> List[str]:
        """Generate strengths worth retaining."""

        result = list(
            strengths[:5]
        )

        for category_name in CATEGORY_NAMES:

            category = categories.get(
                category_name
            )

            if category is None:
                continue

            score = self._category_score(
                category
            )

            if score >= self.excellent_score:
                result.append(
                    f"Maintain strong {category_name} performance."
                )

            elif score >= self.strong_score:
                result.append(
                    f"Continue building on your {category_name} strengths."
                )

        return unique(
            result
        )[:6]

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def _generate_status(
        self,
        overall_score: float,
        categories: Mapping[
            str,
            Mapping[str, Any],
        ],
    ) -> str:
        """
        Generate a screening status.

        Status is intentionally not named "hire" or "reject".
        """

        technical = self._category_score(
            categories.get(
                TECHNICAL
            )
        )

        communication = self._category_score(
            categories.get(
                COMMUNICATION
            )
        )

        confidence = self._category_score(
            categories.get(
                CONFIDENCE
            )
        )

        if (
            overall_score >= 85
            and technical >= 75
        ):
            return "strong_positive_signal"

        if (
            overall_score >= 75
            and technical >= 65
        ):
            return "positive_signal"

        if (
            overall_score >= 65
            and technical >= 60
        ):
            return "mixed_signal"

        if (
            technical < 60
        ):
            return "technical_follow_up_needed"

        if (
            communication < 60
            or confidence < 60
        ):
            return "communication_follow_up_needed"

        return "additional_evidence_needed"

    # ------------------------------------------------------------------
    # Recruiter Recommendation
    # ------------------------------------------------------------------

    def _generate_recruiter_recommendation(
        self,
        overall_score: float,
        performance_level: str,
        categories: Mapping[
            str,
            Mapping[str, Any],
        ],
        status: str,
    ) -> str:
        """Generate recruiter-facing recommendation."""

        technical = self._category_score(
            categories.get(
                TECHNICAL
            )
        )

        communication = self._category_score(
            categories.get(
                COMMUNICATION
            )
        )

        confidence = self._category_score(
            categories.get(
                CONFIDENCE
            )
        )

        if status == "strong_positive_signal":
            return (
                f"Interview evidence is strong "
                f"({overall_score:.1f}/100). "
                "Consider progressing the candidate to the "
                "next appropriate stage, subject to job requirements "
                "and other selection criteria."
            )

        if status == "positive_signal":
            return (
                f"Interview evidence is generally positive "
                f"({overall_score:.1f}/100). "
                "Review question-level evidence and role-specific "
                "requirements before progressing."
            )

        if status == "technical_follow_up_needed":
            return (
                f"Overall performance was {overall_score:.1f}/100, "
                f"but technical performance was {technical:.1f}/100. "
                "Consider a focused technical assessment or "
                "structured technical follow-up."
            )

        if status == "communication_follow_up_needed":
            return (
                f"Overall performance was {overall_score:.1f}/100. "
                f"Communication ({communication:.1f}) and/or "
                f"confidence ({confidence:.1f}) suggests that a "
                "structured follow-up interview may provide additional evidence."
            )

        return (
            f"The interview produced mixed evidence "
            f"({overall_score:.1f}/100). "
            "Review the detailed answers and consider additional "
            "structured evidence before making a selection decision."
        )

    # ------------------------------------------------------------------
    # Candidate Recommendation
    # ------------------------------------------------------------------

    def _generate_candidate_recommendation(
        self,
        overall_score: float,
        categories: Mapping[
            str,
            Mapping[str, Any],
        ],
    ) -> str:
        """Generate candidate-facing recommendation."""

        if overall_score >= 85:
            opening = (
                "Your interview performance was strong."
            )
        elif overall_score >= 75:
            opening = (
                "Your interview performance was generally positive."
            )
        elif overall_score >= 65:
            opening = (
                "Your interview performance showed a solid foundation "
                "with some areas to strengthen."
            )
        else:
            opening = (
                "Your interview performance has several areas "
                "that could benefit from additional practice."
            )

        priorities = []

        for category_name in CATEGORY_NAMES:

            category = categories.get(
                category_name
            )

            if category is None:
                continue

            score = self._category_score(
                category
            )

            if score < 65:
                priorities.append(
                    category_name
                )

        if priorities:
            return (
                f"{opening} "
                "Prioritize practice in "
                + ", ".join(
                    priorities
                )
                + "."
            )

        return (
            f"{opening} Continue practicing structured answers, "
            "specific examples, and concise explanations."
        )

    # ------------------------------------------------------------------
    # Follow-up Actions
    # ------------------------------------------------------------------

    def _generate_follow_up_actions(
        self,
        overall_score: float,
        categories: Mapping[
            str,
            Mapping[str, Any],
        ],
    ) -> List[str]:
        """Generate suggested follow-up actions."""

        actions: List[str] = []

        technical = self._category_score(
            categories.get(
                TECHNICAL
            )
        )

        communication = self._category_score(
            categories.get(
                COMMUNICATION
            )
        )

        confidence = self._category_score(
            categories.get(
                CONFIDENCE
            )
        )

        if technical < self.technical_threshold:
            actions.append(
                "Conduct a focused technical assessment."
            )

        if communication < self.communication_threshold:
            actions.append(
                "Use a structured behavioral or communication-focused follow-up."
            )

        if confidence < self.confidence_threshold:
            actions.append(
                "Review interview delivery and answer clarity using another structured interview."
            )

        if (
            overall_score >= self.excellent_score
            and technical >= self.strong_score
        ):
            actions.append(
                "Review the complete evidence and proceed to the next appropriate stage if other criteria are satisfied."
            )

        if not actions:
            actions.append(
                "Review the complete interview evidence against the job requirements."
            )

        return actions

    # ------------------------------------------------------------------
    # Evidence
    # ------------------------------------------------------------------

    def _category_evidence(
        self,
        category_name: str,
        questions: Sequence[
            Mapping[str, Any]
        ],
    ) -> List[str]:
        """Extract question-level evidence for a category."""

        result: List[str] = []

        field_name = (
            f"{category_name}_score"
        )

        for question in questions:

            score = question.get(
                field_name
            )

            if score is None:

                nested = question.get(
                    category_name
                )

                if isinstance(
                    nested,
                    Mapping,
                ):
                    score = nested.get(
                        "score"
                    )

            if score is None:
                continue

            try:
                score = float(
                    score
                )
            except (
                TypeError,
                ValueError,
            ):
                continue

            question_id = str(
                question.get(
                    "question_id",
                    "question",
                )
            )

            if score < 65:
                result.append(
                    f"{question_id}: {category_name} score {score:.1f}"
                )

        return result[:5]

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def _category_score(
        category: Optional[
            Mapping[str, Any]
        ],
    ) -> float:
        """Extract category score."""

        if not category:
            return 0.0

        value = category.get(
            "score",
            0,
        )

        try:
            return clamp(
                float(value)
            )
        except (
            TypeError,
            ValueError,
        ):
            return 0.0

    def _get_performance_level(
        self,
        scorecard: Mapping[str, Any],
        score: float,
    ) -> str:
        """Use scorecard level when available."""

        level = scorecard.get(
            "performance_level"
        )

        if level:
            return str(
                level
            )

        if score >= 90:
            return "excellent"

        if score >= 80:
            return "very_good"

        if score >= 70:
            return "good"

        if score >= 60:
            return "developing"

        return "needs_improvement"

    def _validate_thresholds(
        self,
    ) -> None:
        """Validate configuration."""

        values = (
            self.technical_threshold,
            self.communication_threshold,
            self.confidence_threshold,
            self.strong_score,
            self.excellent_score,
        )

        if any(
            value < 0
            or value > 100
            for value in values
        ):
            raise InvalidRecommendationInputError(
                "Recommendation thresholds must be between 0 and 100."
            )

        if (
            self.strong_score
            > self.excellent_score
        ):
            raise InvalidRecommendationInputError(
                "strong_score cannot exceed excellent_score."
            )


# ----------------------------------------------------------------------
# Utility Functions
# ----------------------------------------------------------------------


def clamp(
    value: float,
) -> float:
    """Clamp score between 0 and 100."""

    return max(
        0.0,
        min(
            100.0,
            float(value),
        ),
    )


def normalize_list(
    value: Any,
) -> List[str]:
    """Convert arbitrary feedback input to a list."""

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


def unique(
    values: Sequence[str],
) -> List[str]:
    """Return unique values while preserving order."""

    result: List[str] = []

    for value in values:
        if (
            value
            and value not in result
        ):
            result.append(
                value
            )

    return result


# ----------------------------------------------------------------------
# Convenience API
# ----------------------------------------------------------------------


def generate_recommendations(
    scorecard: Any,
    metadata: Optional[
        Mapping[str, Any]
    ] = None,
) -> InterviewRecommendations:
    """
    Convenience wrapper around InterviewRecommendationEngine.
    """

    engine = InterviewRecommendationEngine()

    return engine.generate(
        scorecard=scorecard,
        metadata=metadata,
    )


# ----------------------------------------------------------------------
# Exports
# ----------------------------------------------------------------------


__all__ = [
    "RecommendationItem",
    "InterviewRecommendations",
    "InterviewRecommendationEngine",
    "RecommendationError",
    "InvalidRecommendationInputError",
    "generate_recommendations",
    "clamp",
    "normalize_list",
    "unique",
]