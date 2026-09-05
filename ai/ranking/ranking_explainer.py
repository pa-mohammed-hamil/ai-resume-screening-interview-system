# Project scaffold file
"""
Ranking Explainer
=================

File:
    ai/ranking/ranking_explainer.py

Purpose:
    - Explain why a candidate received a particular ranking
    - Explain score contributions
    - Identify strengths and weaknesses
    - Generate human-readable explanations
    - Compare candidates
    - Generate recruiter-friendly summaries
    - Keep protected attributes completely outside explanations

This module does NOT calculate the candidate's ranking score.
The ranking calculation belongs to candidate_ranker.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


# ============================================================
# CONSTANTS
# ============================================================

MIN_SCORE = 0.0
MAX_SCORE = 100.0

STRONG_THRESHOLD = 80.0
MODERATE_THRESHOLD = 60.0
WEAK_THRESHOLD = 50.0

DEFAULT_TOP_FEATURES = 3
DEFAULT_TOP_CONTRIBUTORS = 3

FEATURE_LABELS = {
    "skill_score": "Skills",
    "experience_score": "Experience",
    "education_score": "Education",
    "ats_score": "ATS compatibility",
    "semantic_score": "Semantic match",
    "keyword_score": "Keyword match",
}

FEATURE_DESCRIPTIONS = {
    "skill_score": (
        "How closely the candidate's skills match "
        "the required job skills."
    ),
    "experience_score": (
        "How well the candidate's experience matches "
        "the required experience."
    ),
    "education_score": (
        "How well the candidate's education matches "
        "the job requirements."
    ),
    "ats_score": (
        "How compatible the resume is with ATS parsing "
        "and formatting requirements."
    ),
    "semantic_score": (
        "How semantically similar the resume is to "
        "the job description."
    ),
    "keyword_score": (
        "How closely important job keywords appear "
        "in the candidate's resume."
    ),
}


PROTECTED_ATTRIBUTES = {
    "age",
    "date_of_birth",
    "dob",
    "gender",
    "sex",
    "race",
    "ethnicity",
    "religion",
    "marital_status",
    "disability",
    "nationality",
    "citizenship",
    "pregnancy_status",
    "medical_status",
    "health_status",
}


# ============================================================
# DATA CLASSES
# ============================================================


@dataclass
class FeatureExplanation:
    """Explanation for one ranking feature."""

    feature: str
    label: str
    score: float
    contribution: float
    importance: float
    category: str
    description: str
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feature": self.feature,
            "label": self.label,
            "score": self.score,
            "contribution": self.contribution,
            "importance": self.importance,
            "category": self.category,
            "description": self.description,
            "explanation": self.explanation,
        }


@dataclass
class RankingExplanation:
    """Complete explanation for one candidate."""

    candidate_id: Any

    final_score: float

    rank: Optional[int]

    summary: str

    feature_explanations: List[
        FeatureExplanation
    ] = field(default_factory=list)

    strengths: List[str] = field(
        default_factory=list
    )

    weaknesses: List[str] = field(
        default_factory=list
    )

    recommendations: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "final_score": self.final_score,
            "rank": self.rank,
            "summary": self.summary,
            "feature_explanations": [
                feature.to_dict()
                for feature in self.feature_explanations
            ],
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "recommendations": self.recommendations,
            "metadata": self.metadata,
        }


@dataclass
class CandidateComparison:
    """Comparison between two candidates."""

    candidate_a: Any
    candidate_b: Any

    score_a: float
    score_b: float

    score_difference: float

    winner: Optional[Any]

    advantages_a: List[str] = field(
        default_factory=list
    )

    advantages_b: List[str] = field(
        default_factory=list
    )

    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_a": self.candidate_a,
            "candidate_b": self.candidate_b,
            "score_a": self.score_a,
            "score_b": self.score_b,
            "score_difference": self.score_difference,
            "winner": self.winner,
            "advantages_a": self.advantages_a,
            "advantages_b": self.advantages_b,
            "summary": self.summary,
        }


# ============================================================
# RANKING EXPLAINER
# ============================================================


class RankingExplainer:
    """
    Generate explainable candidate-ranking results.

    Expected ranking input:

    {
        "candidate_id": 101,
        "rank": 1,
        "score": 89.4,

        "breakdown": {
            "skill_score": 95,
            "experience_score": 90,
            "education_score": 80,
            "ats_score": 88,
            "semantic_score": 91,
            "keyword_score": 86
        },

        "weighted_breakdown": {
            "skill_score": 28.5,
            "experience_score": 18.0,
            ...
        }
    }
    """

    def __init__(
        self,
        weights: Optional[
            Mapping[str, float]
        ] = None,
    ) -> None:

        if weights is None:

            weights = {
                "skill_score": 0.30,
                "experience_score": 0.20,
                "education_score": 0.10,
                "ats_score": 0.15,
                "semantic_score": 0.15,
                "keyword_score": 0.10,
            }

        self.weights = self._normalize_weights(
            weights
        )

    # ========================================================
    # MAIN EXPLANATION
    # ========================================================

    def explain(
        self,
        ranking: Any,
    ) -> RankingExplanation:
        """
        Generate a complete explanation.

        Supports:
            - CandidateRanking dataclass
            - dictionary-based ranking result
        """

        data = self._to_dict(
            ranking
        )

        candidate_id = data.get(
            "candidate_id"
        )

        final_score = self._safe_score(
            data.get(
                "score",
                0.0,
            )
        )

        rank = data.get(
            "rank"
        )

        breakdown = data.get(
            "breakdown",
            {},
        )

        weighted_breakdown = data.get(
            "weighted_breakdown",
            {},
        )

        feature_explanations = (
            self.explain_features(
                breakdown,
                weighted_breakdown,
            )
        )

        strengths = (
            self._extract_strengths(
                breakdown
            )
        )

        weaknesses = (
            self._extract_weaknesses(
                breakdown
            )
        )

        recommendations = (
            self.generate_recommendations(
                breakdown
            )
        )

        summary = self.generate_summary(
            final_score=final_score,
            rank=rank,
            breakdown=breakdown,
            strengths=strengths,
            weaknesses=weaknesses,
        )

        metadata = self._safe_metadata(
            data.get(
                "metadata",
                {},
            )
        )

        return RankingExplanation(
            candidate_id=candidate_id,
            final_score=final_score,
            rank=rank,
            summary=summary,
            feature_explanations=feature_explanations,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            metadata=metadata,
        )

    # ========================================================
    # FEATURE EXPLANATION
    # ========================================================

    def explain_features(
        self,
        breakdown: Mapping[str, Any],
        weighted_breakdown: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> List[FeatureExplanation]:
        """Explain every ranking feature."""

        if weighted_breakdown is None:
            weighted_breakdown = {}

        explanations = []

        for feature, raw_score in breakdown.items():

            score = self._safe_score(
                raw_score
            )

            contribution = self._safe_score(
                weighted_breakdown.get(
                    feature,
                    score
                    * self.weights.get(
                        feature,
                        0.0,
                    ),
                )
            )

            importance = self.weights.get(
                feature,
                0.0,
            )

            category = (
                self._score_category(
                    score
                )
            )

            label = FEATURE_LABELS.get(
                feature,
                self._humanize(
                    feature
                ),
            )

            description = (
                FEATURE_DESCRIPTIONS.get(
                    feature,
                    f"{label} ranking signal.",
                )
            )

            explanation = (
                self._build_feature_sentence(
                    label=label,
                    score=score,
                    contribution=contribution,
                    category=category,
                )
            )

            explanations.append(
                FeatureExplanation(
                    feature=feature,
                    label=label,
                    score=score,
                    contribution=round(
                        contribution,
                        2,
                    ),
                    importance=round(
                        importance,
                        4,
                    ),
                    category=category,
                    description=description,
                    explanation=explanation,
                )
            )

        explanations.sort(
            key=lambda item: item.contribution,
            reverse=True,
        )

        return explanations

    # ========================================================
    # SUMMARY
    # ========================================================

    def generate_summary(
        self,
        final_score: float,
        rank: Optional[int],
        breakdown: Mapping[str, Any],
        strengths: Optional[
            Sequence[str]
        ] = None,
        weaknesses: Optional[
            Sequence[str]
        ] = None,
    ) -> str:
        """Generate recruiter-friendly ranking summary."""

        if strengths is None:
            strengths = self._extract_strengths(
                breakdown
            )

        if weaknesses is None:
            weaknesses = self._extract_weaknesses(
                breakdown
            )

        score_text = (
            f"{final_score:.1f}/100"
        )

        if rank is not None:

            opening = (
                f"The candidate ranks #{rank} "
                f"with an overall score of "
                f"{score_text}."
            )

        else:

            opening = (
                f"The candidate has an overall "
                f"score of {score_text}."
            )

        if strengths:

            strength_text = (
                " Strong areas include "
                + ", ".join(
                    strengths[:3]
                )
                + "."
            )

        else:

            strength_text = ""

        if weaknesses:

            weakness_text = (
                " Areas requiring review include "
                + ", ".join(
                    weaknesses[:3]
                )
                + "."
            )

        else:

            weakness_text = ""

        return (
            opening
            + strength_text
            + weakness_text
        )

    # ========================================================
    # STRENGTHS
    # ========================================================

    def get_strengths(
        self,
        ranking: Any,
    ) -> List[str]:
        """Return the candidate's strongest ranking signals."""

        data = self._to_dict(
            ranking
        )

        return self._extract_strengths(
            data.get(
                "breakdown",
                {},
            )
        )

    # ========================================================
    # WEAKNESSES
    # ========================================================

    def get_weaknesses(
        self,
        ranking: Any,
    ) -> List[str]:
        """Return the candidate's weakest ranking signals."""

        data = self._to_dict(
            ranking
        )

        return self._extract_weaknesses(
            data.get(
                "breakdown",
                {},
            )
        )

    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    def generate_recommendations(
        self,
        breakdown: Mapping[str, Any],
    ) -> List[str]:
        """Generate improvement/review recommendations."""

        recommendations = []

        for feature, raw_score in breakdown.items():

            score = self._safe_score(
                raw_score
            )

            label = FEATURE_LABELS.get(
                feature,
                self._humanize(
                    feature
                ),
            )

            if score < 40:

                recommendations.append(
                    f"Review the candidate's "
                    f"{label.lower()} because "
                    f"the current score is low."
                )

            elif score < WEAK_THRESHOLD:

                recommendations.append(
                    f"Investigate the candidate's "
                    f"{label.lower()} for potential gaps."
                )

            elif score < MODERATE_THRESHOLD:

                recommendations.append(
                    f"Consider validating the "
                    f"candidate's {label.lower()} "
                    f"during screening."
                )

        return recommendations

    # ========================================================
    # TOP CONTRIBUTORS
    # ========================================================

    def top_contributors(
        self,
        ranking: Any,
        limit: int = DEFAULT_TOP_CONTRIBUTORS,
    ) -> List[FeatureExplanation]:
        """Return features contributing most to final score."""

        if limit < 1:
            raise ValueError(
                "limit must be >= 1."
            )

        explanation = self.explain(
            ranking
        )

        return explanation.feature_explanations[
            :limit
        ]

    # ========================================================
    # LOWEST CONTRIBUTORS
    # ========================================================

    def lowest_contributors(
        self,
        ranking: Any,
        limit: int = DEFAULT_TOP_CONTRIBUTORS,
    ) -> List[FeatureExplanation]:
        """Return features contributing least to final score."""

        if limit < 1:
            raise ValueError(
                "limit must be >= 1."
            )

        explanation = self.explain(
            ranking
        )

        features = list(
            explanation.feature_explanations
        )

        features.sort(
            key=lambda item: item.contribution
        )

        return features[
            :limit
        ]

    # ========================================================
    # SCORE BREAKDOWN
    # ========================================================

    def score_breakdown(
        self,
        ranking: Any,
    ) -> Dict[str, Any]:
        """
        Return a recruiter-friendly score breakdown.
        """

        data = self._to_dict(
            ranking
        )

        breakdown = data.get(
            "breakdown",
            {},
        )

        weighted = data.get(
            "weighted_breakdown",
            {},
        )

        result = {}

        for feature, raw_score in breakdown.items():

            score = self._safe_score(
                raw_score
            )

            contribution = weighted.get(
                feature
            )

            if contribution is None:

                contribution = (
                    score
                    * self.weights.get(
                        feature,
                        0.0,
                    )
                )

            result[
                feature
            ] = {
                "label": FEATURE_LABELS.get(
                    feature,
                    self._humanize(
                        feature
                    ),
                ),
                "score": round(
                    score,
                    2,
                ),
                "weight": round(
                    self.weights.get(
                        feature,
                        0.0,
                    ),
                    4,
                ),
                "weight_percentage": round(
                    self.weights.get(
                        feature,
                        0.0,
                    )
                    * 100,
                    2,
                ),
                "contribution": round(
                    float(
                        contribution
                    ),
                    2,
                ),
                "category": self._score_category(
                    score
                ),
            }

        return result

    # ========================================================
    # COMPARISON
    # ========================================================

    def compare(
        self,
        ranking_a: Any,
        ranking_b: Any,
    ) -> CandidateComparison:
        """Compare two ranked candidates."""

        a = self._to_dict(
            ranking_a
        )

        b = self._to_dict(
            ranking_b
        )

        candidate_a = a.get(
            "candidate_id"
        )

        candidate_b = b.get(
            "candidate_id"
        )

        score_a = self._safe_score(
            a.get(
                "score",
                0.0,
            )
        )

        score_b = self._safe_score(
            b.get(
                "score",
                0.0,
            )
        )

        difference = round(
            abs(
                score_a
                - score_b
            ),
            2,
        )

        if score_a > score_b:
            winner = candidate_a

        elif score_b > score_a:
            winner = candidate_b

        else:
            winner = None

        advantages_a = (
            self._feature_advantages(
                a.get(
                    "breakdown",
                    {},
                ),
                b.get(
                    "breakdown",
                    {},
                ),
            )
        )

        advantages_b = (
            self._feature_advantages(
                b.get(
                    "breakdown",
                    {},
                ),
                a.get(
                    "breakdown",
                    {},
                ),
            )
        )

        summary = self._comparison_summary(
            candidate_a=candidate_a,
            candidate_b=candidate_b,
            score_a=score_a,
            score_b=score_b,
            winner=winner,
            difference=difference,
        )

        return CandidateComparison(
            candidate_a=candidate_a,
            candidate_b=candidate_b,
            score_a=score_a,
            score_b=score_b,
            score_difference=difference,
            winner=winner,
            advantages_a=advantages_a,
            advantages_b=advantages_b,
            summary=summary,
        )

    # ========================================================
    # RANKING SUMMARY
    # ========================================================

    def explain_ranking_list(
        self,
        rankings: Iterable[Any],
    ) -> List[Dict[str, Any]]:
        """
        Generate compact explanations for a complete ranking list.
        """

        results = []

        for ranking in rankings:

            explanation = self.explain(
                ranking
            )

            results.append(
                {
                    "candidate_id": (
                        explanation.candidate_id
                    ),
                    "rank": explanation.rank,
                    "score": explanation.final_score,
                    "summary": explanation.summary,
                    "strengths": (
                        explanation.strengths
                    ),
                    "weaknesses": (
                        explanation.weaknesses
                    ),
                }
            )

        return results

    # ========================================================
    # RECRUITER SUMMARY
    # ========================================================

    def recruiter_summary(
        self,
        ranking: Any,
    ) -> Dict[str, Any]:
        """
        Generate a compact dashboard-ready explanation.
        """

        explanation = self.explain(
            ranking
        )

        top_contributors = (
            explanation.feature_explanations[
                :DEFAULT_TOP_FEATURES
            ]
        )

        return {
            "candidate_id": (
                explanation.candidate_id
            ),
            "rank": explanation.rank,
            "score": explanation.final_score,
            "summary": explanation.summary,
            "top_contributors": [
                {
                    "feature": item.label,
                    "score": item.score,
                    "contribution": item.contribution,
                }
                for item in top_contributors
            ],
            "strengths": (
                explanation.strengths
            ),
            "weaknesses": (
                explanation.weaknesses
            ),
            "recommendations": (
                explanation.recommendations
            ),
        }

    # ========================================================
    # TEXT REPORT
    # ========================================================

    def to_text(
        self,
        ranking: Any,
    ) -> str:
        """Convert ranking explanation into readable text."""

        explanation = self.explain(
            ranking
        )

        lines = [
            "Candidate Ranking Explanation",
            "=" * 60,
            f"Candidate ID: "
            f"{explanation.candidate_id}",
            f"Rank: "
            f"{explanation.rank if explanation.rank is not None else 'N/A'}",
            f"Overall Score: "
            f"{explanation.final_score:.1f}/100",
            "",
            "Summary:",
            explanation.summary,
            "",
            "Score Breakdown:",
        ]

        for feature in (
            explanation.feature_explanations
        ):

            lines.append(
                f"- {feature.label}: "
                f"{feature.score:.1f}/100 "
                f"(contribution "
                f"{feature.contribution:.2f})"
            )

        if explanation.strengths:

            lines.extend(
                [
                    "",
                    "Strengths:",
                ]
            )

            for strength in (
                explanation.strengths
            ):
                lines.append(
                    f"- {strength}"
                )

        if explanation.weaknesses:

            lines.extend(
                [
                    "",
                    "Areas to Review:",
                ]
            )

            for weakness in (
                explanation.weaknesses
            ):
                lines.append(
                    f"- {weakness}"
                )

        if explanation.recommendations:

            lines.extend(
                [
                    "",
                    "Recommendations:",
                ]
            )

            for recommendation in (
                explanation.recommendations
            ):
                lines.append(
                    f"- {recommendation}"
                )

        return "\n".join(
            lines
        )

    # ========================================================
    # INTERNAL: STRENGTHS
    # ========================================================

    def _extract_strengths(
        self,
        breakdown: Mapping[str, Any],
    ) -> List[str]:

        strengths = []

        ordered = sorted(
            breakdown.items(),
            key=lambda item: self._safe_score(
                item[1]
            ),
            reverse=True,
        )

        for feature, raw_score in ordered:

            score = self._safe_score(
                raw_score
            )

            if score >= STRONG_THRESHOLD:

                label = FEATURE_LABELS.get(
                    feature,
                    self._humanize(
                        feature
                    ),
                )

                strengths.append(
                    f"{label} ({score:.1f}/100)"
                )

        return strengths

    # ========================================================
    # INTERNAL: WEAKNESSES
    # ========================================================

    def _extract_weaknesses(
        self,
        breakdown: Mapping[str, Any],
    ) -> List[str]:

        weaknesses = []

        ordered = sorted(
            breakdown.items(),
            key=lambda item: self._safe_score(
                item[1]
            ),
        )

        for feature, raw_score in ordered:

            score = self._safe_score(
                raw_score
            )

            if score < WEAK_THRESHOLD:

                label = FEATURE_LABELS.get(
                    feature,
                    self._humanize(
                        feature
                    ),
                )

                weaknesses.append(
                    f"{label} ({score:.1f}/100)"
                )

        return weaknesses

    # ========================================================
    # INTERNAL: FEATURE CATEGORY
    # ========================================================

    @staticmethod
    def _score_category(
        score: float,
    ) -> str:

        if score >= STRONG_THRESHOLD:
            return "strong"

        if score >= MODERATE_THRESHOLD:
            return "moderate"

        if score >= WEAK_THRESHOLD:
            return "below_average"

        return "weak"

    # ========================================================
    # INTERNAL: FEATURE SENTENCE
    # ========================================================

    @staticmethod
    def _build_feature_sentence(
        label: str,
        score: float,
        contribution: float,
        category: str,
    ) -> str:

        if category == "strong":

            quality = "strong"

        elif category == "moderate":

            quality = "moderate"

        elif category == "below_average":

            quality = "below-average"

        else:

            quality = "weak"

        return (
            f"{label} has a {quality} score of "
            f"{score:.1f}/100 and contributes "
            f"{contribution:.2f} points to the "
            f"overall ranking."
        )

    # ========================================================
    # INTERNAL: COMPARISON
    # ========================================================

    def _feature_advantages(
        self,
        primary: Mapping[str, Any],
        secondary: Mapping[str, Any],
    ) -> List[str]:

        advantages = []

        for feature, raw_score in primary.items():

            primary_score = self._safe_score(
                raw_score
            )

            secondary_score = self._safe_score(
                secondary.get(
                    feature,
                    0.0,
                )
            )

            if (
                primary_score
                > secondary_score
            ):

                label = FEATURE_LABELS.get(
                    feature,
                    self._humanize(
                        feature
                    ),
                )

                difference = round(
                    primary_score
                    - secondary_score,
                    2,
                )

                advantages.append(
                    f"{label} (+{difference:.1f})"
                )

        return advantages

    @staticmethod
    def _comparison_summary(
        candidate_a: Any,
        candidate_b: Any,
        score_a: float,
        score_b: float,
        winner: Optional[Any],
        difference: float,
    ) -> str:

        if winner is None:

            return (
                f"Candidates {candidate_a} and "
                f"{candidate_b} have the same "
                f"overall score of {score_a:.1f}/100."
            )

        if winner == candidate_a:

            return (
                f"Candidate {candidate_a} scores "
                f"{difference:.1f} points higher than "
                f"candidate {candidate_b}."
            )

        return (
            f"Candidate {candidate_b} scores "
            f"{difference:.1f} points higher than "
            f"candidate {candidate_a}."
        )

    # ========================================================
    # INTERNAL: METADATA
    # ========================================================

    @staticmethod
    def _safe_metadata(
        metadata: Mapping[str, Any],
    ) -> Dict[str, Any]:

        safe = {}

        for key, value in metadata.items():

            normalized_key = (
                str(key)
                .strip()
                .lower()
            )

            if normalized_key in (
                PROTECTED_ATTRIBUTES
            ):
                continue

            safe[key] = value

        return safe

    # ========================================================
    # INTERNAL: CONVERSION
    # ========================================================

    @staticmethod
    def _to_dict(
        value: Any,
    ) -> Dict[str, Any]:

        if isinstance(
            value,
            Mapping,
        ):

            return dict(
                value
            )

        if hasattr(
            value,
            "to_dict",
        ):

            return dict(
                value.to_dict()
            )

        if hasattr(
            value,
            "__dict__",
        ):

            return dict(
                vars(value)
            )

        raise TypeError(
            "Ranking must be a mapping, "
            "dataclass with to_dict(), or "
            "object with __dict__."
        )

    # ========================================================
    # INTERNAL: SCORE
    # ========================================================

    @staticmethod
    def _safe_score(
        value: Any,
    ) -> float:

        if value is None:
            return 0.0

        try:
            score = float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            return 0.0

        return max(
            MIN_SCORE,
            min(
                MAX_SCORE,
                score,
            ),
        )

    # ========================================================
    # INTERNAL: WEIGHTS
    # ========================================================

    @staticmethod
    def _normalize_weights(
        weights: Mapping[str, float],
    ) -> Dict[str, float]:

        clean = {}

        for feature, value in weights.items():

            try:

                numeric = float(
                    value
                )

            except (
                TypeError,
                ValueError,
            ) as exc:

                raise ValueError(
                    f"Invalid weight for "
                    f"{feature}: {value}"
                ) from exc

            if numeric < 0:

                raise ValueError(
                    f"Weight cannot be negative: "
                    f"{feature}"
                )

            clean[feature] = numeric

        total = sum(
            clean.values()
        )

        if total <= 0:

            raise ValueError(
                "Total ranking weight must "
                "be greater than zero."
            )

        return {
            feature: weight / total
            for feature, weight
            in clean.items()
        }

    # ========================================================
    # INTERNAL: HUMANIZE
    # ========================================================

    @staticmethod
    def _humanize(
        value: str,
    ) -> str:

        value = value.replace(
            "_",
            " ",
        )

        value = value.replace(
            "-",
            " ",
        )

        return value.title()


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================


def explain_candidate_ranking(
    ranking: Any,
    weights: Optional[
        Mapping[str, float]
    ] = None,
) -> Dict[str, Any]:
    """
    Convenience function for API/service usage.
    """

    explainer = RankingExplainer(
        weights=weights
    )

    return explainer.explain(
        ranking
    ).to_dict()


def generate_ranking_summary(
    ranking: Any,
    weights: Optional[
        Mapping[str, float]
    ] = None,
) -> str:
    """Generate a simple human-readable summary."""

    explainer = RankingExplainer(
        weights=weights
    )

    return explainer.to_text(
        ranking
    )


def compare_candidate_rankings(
    ranking_a: Any,
    ranking_b: Any,
    weights: Optional[
        Mapping[str, float]
    ] = None,
) -> Dict[str, Any]:
    """Compare two candidates."""

    explainer = RankingExplainer(
        weights=weights
    )

    return explainer.compare(
        ranking_a,
        ranking_b,
    ).to_dict()


# ============================================================
# EXAMPLE
# ============================================================


if __name__ == "__main__":

    candidate = {
        "candidate_id": 101,
        "rank": 1,
        "score": 89.45,

        "breakdown": {
            "skill_score": 95,
            "experience_score": 90,
            "education_score": 82,
            "ats_score": 88,
            "semantic_score": 91,
            "keyword_score": 84,
        },

        "weighted_breakdown": {
            "skill_score": 28.50,
            "experience_score": 18.00,
            "education_score": 8.20,
            "ats_score": 13.20,
            "semantic_score": 13.65,
            "keyword_score": 8.40,
        },

        "metadata": {
            "name": "Candidate A",
            "job_id": 501,
            "resume_id": 1001,

            # These should never appear in the
            # ranking explanation.
            "age": 29,
            "gender": "example",
        },
    }

    explainer = RankingExplainer()

    # --------------------------------------------------------
    # Complete explanation
    # --------------------------------------------------------

    explanation = explainer.explain(
        candidate
    )

    print(
        explainer.to_text(
            candidate
        )
    )

    # --------------------------------------------------------
    # Score breakdown
    # --------------------------------------------------------

    print("\nSCORE BREAKDOWN")
    print("=" * 60)

    for feature, details in (
        explainer.score_breakdown(
            candidate
        ).items()
    ):

        print(
            f"{details['label']}: "
            f"{details['score']}/100 | "
            f"Weight: "
            f"{details['weight_percentage']}% | "
            f"Contribution: "
            f"{details['contribution']}"
        )

    # --------------------------------------------------------
    # Recruiter summary
    # --------------------------------------------------------

    print("\nRECRUITER SUMMARY")
    print("=" * 60)

    print(
        explainer.recruiter_summary(
            candidate
        )
    )

    # --------------------------------------------------------
    # Convenience API
    # --------------------------------------------------------

    print("\nJSON RESULT")
    print("=" * 60)

    print(
        explain_candidate_ranking(
            candidate
        )
    )