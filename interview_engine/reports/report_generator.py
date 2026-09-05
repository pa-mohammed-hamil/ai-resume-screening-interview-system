"""
Interview Report Generator.

Combines interview evaluation results into a structured report.

The generator is responsible for:
- Aggregating question-level evaluations
- Calculating category scores
- Generating strengths and improvement areas
- Producing an overall recommendation
- Creating a recruiter-friendly summary
- Creating a candidate-friendly feedback section
- Returning JSON-serializable report data

This module does not make hiring decisions by itself. It summarizes
observable interview evaluation signals supplied by the evaluation layer.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional, Sequence

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------


class ReportGenerationError(Exception):
    """Base exception for report generation."""


class InvalidReportInputError(ReportGenerationError):
    """Raised when report input is invalid."""


class EmptyInterviewError(ReportGenerationError):
    """Raised when no interview evaluations are provided."""


# ----------------------------------------------------------------------
# Data Models
# ----------------------------------------------------------------------


@dataclass
class QuestionReport:
    """Normalized report for one interview question."""

    question_id: str
    question: str
    answer: str

    overall_score: float

    technical_score: Optional[float] = None
    communication_score: Optional[float] = None
    confidence_score: Optional[float] = None

    strengths: List[str] = field(
        default_factory=list
    )

    improvements: List[str] = field(
        default_factory=list
    )

    feedback: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CategoryScore:
    """Aggregated score for one evaluation category."""

    name: str
    score: float
    weight: float

    question_count: int = 0

    strengths: List[str] = field(
        default_factory=list
    )

    improvements: List[str] = field(
        default_factory=list
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class InterviewReport:
    """Complete generated interview report."""

    interview_id: Optional[str]

    generated_at: str

    overall_score: float

    performance_level: str

    recommendation: str

    summary: str

    recruiter_summary: str

    candidate_feedback: str

    category_scores: List[CategoryScore]

    question_reports: List[QuestionReport]

    strengths: List[str]

    improvement_areas: List[str]

    technical_summary: str

    communication_summary: str

    confidence_summary: str

    next_steps: List[str]

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)

        data["category_scores"] = [
            category.to_dict()
            for category in self.category_scores
        ]

        data["question_reports"] = [
            question.to_dict()
            for question in self.question_reports
        ]

        return data


# ----------------------------------------------------------------------
# Report Generator
# ----------------------------------------------------------------------


class InterviewReportGenerator:
    """
    Generate structured reports from interview evaluation results.

    Expected question evaluation format:

        {
            "question_id": "q1",
            "question": "Explain REST APIs.",
            "answer": "REST is ...",

            "technical": {
                "score": 85
            },

            "communication": {
                "score": 78
            },

            "confidence": {
                "score": 82
            },

            "overall_score": 82,

            "strengths": [
                "Good technical explanation"
            ],

            "improvements": [
                "Add a practical example"
            ]
        }

    The generator also accepts the dataclass objects produced by the
    evaluation layer.
    """

    DEFAULT_CATEGORY_WEIGHTS = {
        "technical": 0.45,
        "communication": 0.30,
        "confidence": 0.25,
    }

    def __init__(
        self,
        category_weights: Optional[
            Dict[str, float]
        ] = None,
    ) -> None:

        self.category_weights = (
            category_weights
            or self.DEFAULT_CATEGORY_WEIGHTS.copy()
        )

        self._validate_weights()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        evaluations: Sequence[Any],
        interview_id: Optional[str] = None,
        candidate_name: Optional[str] = None,
        job_title: Optional[str] = None,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> InterviewReport:
        """
        Generate a complete interview report.

        Args:
            evaluations:
                Question-level evaluation results.

            interview_id:
                Optional interview identifier.

            candidate_name:
                Optional candidate name.

            job_title:
                Optional job title.

            metadata:
                Optional report metadata.

        Returns:
            InterviewReport
        """

        if not evaluations:
            raise EmptyInterviewError(
                "At least one evaluation is required."
            )

        normalized = [
            self._normalize_evaluation(
                evaluation,
                index=index,
            )
            for index, evaluation
            in enumerate(evaluations, start=1)
        ]

        category_scores = (
            self._calculate_category_scores(
                normalized
            )
        )

        overall_score = (
            self._calculate_overall_score(
                category_scores,
                normalized,
            )
        )

        performance_level = (
            self._performance_level(
                overall_score
            )
        )

        recommendation = (
            self._generate_recommendation(
                overall_score,
                category_scores,
            )
        )

        strengths = (
            self._collect_strengths(
                normalized
            )
        )

        improvement_areas = (
            self._collect_improvements(
                normalized
            )
        )

        technical_summary = (
            self._generate_category_summary(
                category_scores,
                "technical",
            )
        )

        communication_summary = (
            self._generate_category_summary(
                category_scores,
                "communication",
            )
        )

        confidence_summary = (
            self._generate_category_summary(
                category_scores,
                "confidence",
            )
        )

        summary = (
            self._generate_overall_summary(
                overall_score,
                performance_level,
                category_scores,
            )
        )

        recruiter_summary = (
            self._generate_recruiter_summary(
                overall_score,
                category_scores,
                strengths,
                improvement_areas,
            )
        )

        candidate_feedback = (
            self._generate_candidate_feedback(
                overall_score,
                strengths,
                improvement_areas,
            )
        )

        next_steps = (
            self._generate_next_steps(
                overall_score,
                category_scores,
            )
        )

        report_metadata = dict(
            metadata or {}
        )

        if candidate_name:
            report_metadata[
                "candidate_name"
            ] = candidate_name

        if job_title:
            report_metadata[
                "job_title"
            ] = job_title

        report_metadata[
            "question_count"
        ] = len(normalized)

        return InterviewReport(
            interview_id=interview_id,
            generated_at=(
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
            overall_score=round(
                overall_score,
                2,
            ),
            performance_level=performance_level,
            recommendation=recommendation,
            summary=summary,
            recruiter_summary=recruiter_summary,
            candidate_feedback=candidate_feedback,
            category_scores=category_scores,
            question_reports=normalized,
            strengths=strengths,
            improvement_areas=improvement_areas,
            technical_summary=technical_summary,
            communication_summary=communication_summary,
            confidence_summary=confidence_summary,
            next_steps=next_steps,
            metadata=report_metadata,
        )

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    def _normalize_evaluation(
        self,
        evaluation: Any,
        index: int,
    ) -> QuestionReport:
        """
        Normalize dictionaries or evaluation dataclasses into a
        QuestionReport.
        """

        if isinstance(
            evaluation,
            QuestionReport,
        ):
            return evaluation

        if hasattr(
            evaluation,
            "to_dict",
        ):
            evaluation = (
                evaluation.to_dict()
            )

        elif hasattr(
            evaluation,
            "__dict__",
        ):
            evaluation = vars(
                evaluation
            )

        if not isinstance(
            evaluation,
            dict,
        ):
            raise InvalidReportInputError(
                f"Evaluation #{index} must be a dictionary "
                "or evaluation object."
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
        ).strip()

        answer = str(
            evaluation.get(
                "answer",
                "",
            )
        ).strip()

        technical_score = (
            self._extract_score(
                evaluation,
                "technical",
            )
        )

        communication_score = (
            self._extract_score(
                evaluation,
                "communication",
            )
        )

        confidence_score = (
            self._extract_score(
                evaluation,
                "confidence",
            )
        )

        overall_score = (
            self._extract_score(
                evaluation,
                "overall_score",
            )
        )

        if overall_score is None:
            overall_score = (
                self._calculate_question_score(
                    technical_score,
                    communication_score,
                    confidence_score,
                )
            )

        if overall_score is None:
            raise InvalidReportInputError(
                f"Evaluation #{index} does not contain "
                "a usable score."
            )

        strengths = self._extract_list(
            evaluation.get(
                "strengths",
                [],
            )
        )

        improvements = self._extract_list(
            evaluation.get(
                "improvements",
                evaluation.get(
                    "improvement_areas",
                    [],
                ),
            )
        )

        feedback = str(
            evaluation.get(
                "feedback",
                evaluation.get(
                    "summary",
                    "",
                ),
            )
        )

        return QuestionReport(
            question_id=question_id,
            question=question,
            answer=answer,
            overall_score=self._clamp(
                overall_score
            ),
            technical_score=(
                self._clamp(
                    technical_score
                )
                if technical_score is not None
                else None
            ),
            communication_score=(
                self._clamp(
                    communication_score
                )
                if communication_score is not None
                else None
            ),
            confidence_score=(
                self._clamp(
                    confidence_score
                )
                if confidence_score is not None
                else None
            ),
            strengths=strengths,
            improvements=improvements,
            feedback=feedback,
            metadata=dict(
                evaluation.get(
                    "metadata",
                    {},
                )
                or {}
            ),
        )

    # ------------------------------------------------------------------
    # Category Scores
    # ------------------------------------------------------------------

    def _calculate_category_scores(
        self,
        evaluations: Sequence[
            QuestionReport
        ],
    ) -> List[CategoryScore]:
        """Calculate average scores for each category."""

        categories = {
            "technical": [],
            "communication": [],
            "confidence": [],
        }

        for evaluation in evaluations:

            if (
                evaluation.technical_score
                is not None
            ):
                categories[
                    "technical"
                ].append(
                    evaluation.technical_score
                )

            if (
                evaluation.communication_score
                is not None
            ):
                categories[
                    "communication"
                ].append(
                    evaluation.communication_score
                )

            if (
                evaluation.confidence_score
                is not None
            ):
                categories[
                    "confidence"
                ].append(
                    evaluation.confidence_score
                )

        results: List[CategoryScore] = []

        for name, scores in categories.items():

            score = (
                mean(scores)
                if scores
                else self._fallback_category_score(
                    evaluations
                )
            )

            category_evaluations = [
                evaluation
                for evaluation in evaluations
                if (
                    getattr(
                        evaluation,
                        f"{name}_score",
                        None,
                    )
                    is not None
                )
            ]

            strengths = self._collect_category_strengths(
                category_evaluations,
                name,
            )

            improvements = (
                self._collect_category_improvements(
                    category_evaluations,
                    name,
                )
            )

            results.append(
                CategoryScore(
                    name=name,
                    score=round(
                        self._clamp(score),
                        2,
                    ),
                    weight=self.category_weights[
                        name
                    ],
                    question_count=len(
                        scores
                    ),
                    strengths=strengths,
                    improvements=improvements,
                )
            )

        return results

    def _calculate_overall_score(
        self,
        categories: Sequence[
            CategoryScore
        ],
        evaluations: Sequence[
            QuestionReport
        ],
    ) -> float:
        """
        Calculate weighted overall score.

        Missing categories are excluded and weights are renormalized.
        """

        available = [
            category
            for category in categories
            if category.question_count > 0
        ]

        if not available:
            return mean(
                evaluation.overall_score
                for evaluation in evaluations
            )

        total_weight = sum(
            category.weight
            for category in available
        )

        if total_weight <= 0:
            return mean(
                evaluation.overall_score
                for evaluation in evaluations
            )

        return sum(
            category.score
            * category.weight
            for category in available
        ) / total_weight

    # ------------------------------------------------------------------
    # Question Score
    # ------------------------------------------------------------------

    def _calculate_question_score(
        self,
        technical: Optional[float],
        communication: Optional[float],
        confidence: Optional[float],
    ) -> Optional[float]:
        """Calculate a question-level score."""

        values = []

        if technical is not None:
            values.append(
                (
                    technical,
                    self.category_weights[
                        "technical"
                    ],
                )
            )

        if communication is not None:
            values.append(
                (
                    communication,
                    self.category_weights[
                        "communication"
                    ],
                )
            )

        if confidence is not None:
            values.append(
                (
                    confidence,
                    self.category_weights[
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

        return sum(
            score * weight
            for score, weight in values
        ) / total_weight

    # ------------------------------------------------------------------
    # Strengths / Improvements
    # ------------------------------------------------------------------

    def _collect_strengths(
        self,
        evaluations: Sequence[
            QuestionReport
        ],
    ) -> List[str]:
        """Collect and rank strengths."""

        counts: Dict[str, int] = {}

        for evaluation in evaluations:
            for strength in evaluation.strengths:
                normalized = strength.strip()

                if normalized:
                    counts[
                        normalized
                    ] = counts.get(
                        normalized,
                        0,
                    ) + 1

        return self._rank_items(
            counts,
            limit=6,
        )

    def _collect_improvements(
        self,
        evaluations: Sequence[
            QuestionReport
        ],
    ) -> List[str]:
        """Collect and rank improvement areas."""

        counts: Dict[str, int] = {}

        for evaluation in evaluations:
            for improvement in evaluation.improvements:
                normalized = improvement.strip()

                if normalized:
                    counts[
                        normalized
                    ] = counts.get(
                        normalized,
                        0,
                    ) + 1

        return self._rank_items(
            counts,
            limit=6,
        )

    def _collect_category_strengths(
        self,
        evaluations: Sequence[
            QuestionReport
        ],
        category: str,
    ) -> List[str]:
        """Collect category-specific strengths."""

        result: List[str] = []

        for evaluation in evaluations:
            score = getattr(
                evaluation,
                f"{category}_score",
                None,
            )

            if (
                score is not None
                and score >= 80
            ):
                result.extend(
                    evaluation.strengths
                )

        return self._unique(
            result
        )[:5]

    def _collect_category_improvements(
        self,
        evaluations: Sequence[
            QuestionReport
        ],
        category: str,
    ) -> List[str]:
        """Collect category-specific improvements."""

        result: List[str] = []

        for evaluation in evaluations:
            score = getattr(
                evaluation,
                f"{category}_score",
                None,
            )

            if (
                score is not None
                and score < 75
            ):
                result.extend(
                    evaluation.improvements
                )

        return self._unique(
            result
        )[:5]

    # ------------------------------------------------------------------
    # Summaries
    # ------------------------------------------------------------------

    def _generate_overall_summary(
        self,
        score: float,
        level: str,
        categories: Sequence[
            CategoryScore
        ],
    ) -> str:
        """Generate overall summary."""

        strongest = max(
            categories,
            key=lambda category: category.score,
        )

        weakest = min(
            categories,
            key=lambda category: category.score,
        )

        return (
            f"The candidate demonstrated {level.replace('_', ' ')} "
            f"overall interview performance with a score of "
            f"{score:.1f}/100. "
            f"The strongest area was {strongest.name} "
            f"({strongest.score:.1f}/100), while "
            f"{weakest.name} ({weakest.score:.1f}/100) "
            f"offers the greatest opportunity for improvement."
        )

    def _generate_recruiter_summary(
        self,
        score: float,
        categories: Sequence[
            CategoryScore
        ],
        strengths: Sequence[str],
        improvements: Sequence[str],
    ) -> str:
        """Generate recruiter-facing summary."""

        strongest = max(
            categories,
            key=lambda category: category.score,
        )

        weakest = min(
            categories,
            key=lambda category: category.score,
        )

        return (
            f"Overall interview score: {score:.1f}/100. "
            f"Strongest category: {strongest.name} "
            f"({strongest.score:.1f}). "
            f"Primary development area: {weakest.name} "
            f"({weakest.score:.1f}). "
            f"The report contains {len(strengths)} identified "
            f"strength(s) and {len(improvements)} improvement "
            f"area(s). Review the underlying question-level "
            f"evidence before making any hiring decision."
        )

    def _generate_candidate_feedback(
        self,
        score: float,
        strengths: Sequence[str],
        improvements: Sequence[str],
    ) -> str:
        """Generate candidate-friendly feedback."""

        if score >= 85:
            opening = (
                "You performed strongly in this interview."
            )
        elif score >= 70:
            opening = (
                "You demonstrated a solid interview performance."
            )
        elif score >= 60:
            opening = (
                "You showed a developing level of interview readiness."
            )
        else:
            opening = (
                "There are several areas where additional interview practice "
                "could improve your performance."
            )

        if improvements:
            focus = (
                "The main areas to work on are: "
                + "; ".join(
                    improvements[:3]
                )
                + "."
            )
        else:
            focus = (
                "Continue practicing concise, evidence-based answers."
            )

        return (
            f"{opening} {focus} "
            "Use specific examples and measurable outcomes "
            "where possible."
        )

    def _generate_category_summary(
        self,
        categories: Sequence[
            CategoryScore
        ],
        category_name: str,
    ) -> str:
        """Generate category summary."""

        category = next(
            (
                item
                for item in categories
                if item.name
                == category_name
            ),
            None,
        )

        if category is None:
            return (
                f"No {category_name} evaluation was available."
            )

        if category.score >= 85:
            level = "strong"
        elif category.score >= 70:
            level = "solid"
        elif category.score >= 60:
            level = "developing"
        else:
            level = "needs improvement"

        return (
            f"{category_name.capitalize()} performance was "
            f"{level}, with an average score of "
            f"{category.score:.1f}/100 across "
            f"{category.question_count} evaluated question(s)."
        )

    # ------------------------------------------------------------------
    # Recommendation
    # ------------------------------------------------------------------

    def _generate_recommendation(
        self,
        score: float,
        categories: Sequence[
            CategoryScore
        ],
    ) -> str:
        """
        Generate a non-binding recommendation.

        This is a screening summary only. It should not be treated
        as an automated hiring decision.
        """

        technical = self._category_score(
            categories,
            "technical",
        )

        communication = self._category_score(
            categories,
            "communication",
        )

        confidence = self._category_score(
            categories,
            "confidence",
        )

        if (
            score >= 85
            and technical >= 80
        ):
            return "strong_interview_performance"

        if (
            score >= 75
            and technical >= 70
        ):
            return "positive_review"

        if (
            technical < 60
            and score < 70
        ):
            return "additional_technical_assessment"

        if (
            communication < 60
            or confidence < 60
        ):
            return "consider_follow_up_interview"

        if score >= 65:
            return "mixed_results_review_evidence"

        return "additional_assessment_recommended"

    # ------------------------------------------------------------------
    # Next Steps
    # ------------------------------------------------------------------

    def _generate_next_steps(
        self,
        score: float,
        categories: Sequence[
            CategoryScore
        ],
    ) -> List[str]:
        """Generate recommended next steps."""

        technical = self._category_score(
            categories,
            "technical",
        )

        communication = self._category_score(
            categories,
            "communication",
        )

        confidence = self._category_score(
            categories,
            "confidence",
        )

        steps: List[str] = []

        if technical < 65:
            steps.append(
                "Consider a focused technical assessment."
            )

        if communication < 65:
            steps.append(
                "Consider a structured follow-up interview focused on communication."
            )

        if confidence < 65:
            steps.append(
                "Review answer delivery and clarity during the next interview stage."
            )

        if score >= 80:
            steps.append(
                "Review question-level evidence and continue with the appropriate hiring workflow if other criteria are satisfied."
            )

        if not steps:
            steps.append(
                "Review the full interview evidence alongside the job requirements and other selection criteria."
            )

        return steps

    # ------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_score(
        data: Dict[str, Any],
        key: str,
    ) -> Optional[float]:
        """Extract score from direct or nested data."""

        value = data.get(
            key
        )

        if isinstance(
            value,
            dict,
        ):
            value = value.get(
                "score"
            )

        if value is None:
            return None

        try:
            return float(
                value
            )
        except (
            TypeError,
            ValueError,
        ):
            return None

    @staticmethod
    def _extract_list(
        value: Any,
    ) -> List[str]:
        """Normalize a list-like feedback field."""

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

    @staticmethod
    def _rank_items(
        counts: Dict[str, int],
        limit: int,
    ) -> List[str]:
        """Rank feedback items by frequency."""

        ordered = sorted(
            counts.items(),
            key=lambda item: (
                -item[1],
                item[0],
            ),
        )

        return [
            item[0]
            for item in ordered[:limit]
        ]

    @staticmethod
    def _unique(
        values: Sequence[str],
    ) -> List[str]:
        """Return unique values preserving order."""

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

    @staticmethod
    def _category_score(
        categories: Sequence[
            CategoryScore
        ],
        name: str,
    ) -> float:
        """Get a category score."""

        for category in categories:
            if category.name == name:
                return category.score

        return 0.0

    @staticmethod
    def _fallback_category_score(
        evaluations: Sequence[
            QuestionReport
        ],
    ) -> float:
        """Use overall question scores if category data is missing."""

        if not evaluations:
            return 0.0

        return mean(
            evaluation.overall_score
            for evaluation in evaluations
        )

    @staticmethod
    def _performance_level(
        score: float,
    ) -> str:
        """Map score to performance level."""

        if score >= 90:
            return "excellent"

        if score >= 80:
            return "very_good"

        if score >= 70:
            return "good"

        if score >= 60:
            return "developing"

        return "needs_improvement"

    @staticmethod
    def _clamp(
        value: float,
    ) -> float:
        """Clamp a score between 0 and 100."""

        return max(
            0.0,
            min(100.0, float(value)),
        )

    def _validate_weights(self) -> None:
        """Validate category weights."""

        required = {
            "technical",
            "communication",
            "confidence",
        }

        missing = (
            required
            - set(
                self.category_weights.keys()
            )
        )

        if missing:
            raise InvalidReportInputError(
                "Missing category weights: "
                + ", ".join(
                    sorted(missing)
                )
            )

        if any(
            value < 0
            for value
            in self.category_weights.values()
        ):
            raise InvalidReportInputError(
                "Category weights cannot be negative."
            )

        if sum(
            self.category_weights.values()
        ) <= 0:
            raise InvalidReportInputError(
                "At least one category weight must be positive."
            )


# ----------------------------------------------------------------------
# Convenience Function
# ----------------------------------------------------------------------


def generate_interview_report(
    evaluations: Sequence[Any],
    interview_id: Optional[str] = None,
    candidate_name: Optional[str] = None,
    job_title: Optional[str] = None,
    metadata: Optional[
        Dict[str, Any]
    ] = None,
) -> InterviewReport:
    """
    Convenience wrapper around InterviewReportGenerator.
    """

    generator = InterviewReportGenerator()

    return generator.generate(
        evaluations=evaluations,
        interview_id=interview_id,
        candidate_name=candidate_name,
        job_title=job_title,
        metadata=metadata,
    )


__all__ = [
    "QuestionReport",
    "CategoryScore",
    "InterviewReport",
    "InterviewReportGenerator",
    "ReportGenerationError",
    "InvalidReportInputError",
    "EmptyInterviewError",
    "generate_interview_report",
]