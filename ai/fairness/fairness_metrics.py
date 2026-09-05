"""
Fairness metrics for the AI Resume Screening & Interview System.

This module provides statistical metrics for auditing candidate
screening and ranking outcomes across groups.

Important:
- Group/protected attributes are used ONLY for fairness auditing.
- They must not be used as features for candidate ranking or scoring.
- Metrics are indicators for review, not proof of discrimination.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional


# ================================================================
# CONSTANTS
# ================================================================

DEFAULT_SELECTION_THRESHOLD = 70.0
DEFAULT_RELEVANCE_THRESHOLD = 70.0

DEFAULT_DISPARITY_THRESHOLD = 0.80
DEFAULT_SCORE_GAP_THRESHOLD = 10.0


# ================================================================
# DATA CLASSES
# ================================================================


@dataclass
class GroupFairnessMetrics:
    """Fairness metrics calculated for one group."""

    group: str

    total: int

    selected: int

    selection_rate: float

    average_score: float

    median_score: float

    true_positives: int

    false_positives: int

    true_negatives: int

    false_negatives: int

    true_positive_rate: float

    false_positive_rate: float


@dataclass
class FairnessComparison:
    """Comparison between a group and a reference group."""

    group: str

    reference_group: str

    selection_rate_ratio: float

    selection_rate_difference: float

    average_score_gap: float

    true_positive_rate_difference: float

    false_positive_rate_difference: float

    disparate_impact: float


@dataclass
class FairnessMetricsResult:
    """Complete fairness-analysis result."""

    total_candidates: int

    groups: Dict[str, GroupFairnessMetrics]

    reference_group: Optional[str]

    comparisons: List[FairnessComparison]

    warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics into a JSON-compatible dictionary."""

        return {
            "total_candidates": self.total_candidates,
            "reference_group": self.reference_group,

            "groups": {
                group: {
                    "group": metrics.group,
                    "total": metrics.total,
                    "selected": metrics.selected,
                    "selection_rate": metrics.selection_rate,
                    "average_score": metrics.average_score,
                    "median_score": metrics.median_score,
                    "true_positives": metrics.true_positives,
                    "false_positives": metrics.false_positives,
                    "true_negatives": metrics.true_negatives,
                    "false_negatives": metrics.false_negatives,
                    "true_positive_rate": metrics.true_positive_rate,
                    "false_positive_rate": metrics.false_positive_rate,
                }
                for group, metrics in self.groups.items()
            },

            "comparisons": [
                {
                    "group": comparison.group,
                    "reference_group": comparison.reference_group,
                    "selection_rate_ratio": (
                        comparison.selection_rate_ratio
                    ),
                    "selection_rate_difference": (
                        comparison.selection_rate_difference
                    ),
                    "average_score_gap": (
                        comparison.average_score_gap
                    ),
                    "true_positive_rate_difference": (
                        comparison.true_positive_rate_difference
                    ),
                    "false_positive_rate_difference": (
                        comparison.false_positive_rate_difference
                    ),
                    "disparate_impact": (
                        comparison.disparate_impact
                    ),
                }
                for comparison in self.comparisons
            ],

            "warnings": self.warnings,
        }


# ================================================================
# FAIRNESS METRICS CALCULATOR
# ================================================================


class FairnessMetrics:
    """
    Calculate fairness metrics for candidate screening outcomes.

    Candidate format:

    {
        "candidate_id": 1,
        "group": "group_a",
        "score": 85,
        "qualified": True
    }

    ``group`` is used only for auditing.

    ``score`` represents the AI screening/ranking score.

    ``qualified`` represents an independent ground-truth label when
    available. It should ideally come from a validated evaluation
    dataset rather than from the same AI model being audited.
    """

    def __init__(
        self,
        selection_threshold: float = DEFAULT_SELECTION_THRESHOLD,
        relevance_threshold: float = DEFAULT_RELEVANCE_THRESHOLD,
        disparity_threshold: float = DEFAULT_DISPARITY_THRESHOLD,
        score_gap_threshold: float = DEFAULT_SCORE_GAP_THRESHOLD,
    ) -> None:

        self.selection_threshold = selection_threshold
        self.relevance_threshold = relevance_threshold
        self.disparity_threshold = disparity_threshold
        self.score_gap_threshold = score_gap_threshold

        self._validate_configuration()

    # ============================================================
    # MAIN API
    # ============================================================

    def calculate(
        self,
        candidates: Iterable[Mapping[str, Any]],
        group_field: str = "group",
        score_field: str = "score",
        label_field: str = "qualified",
    ) -> FairnessMetricsResult:
        """
        Calculate fairness metrics.

        Args:
            candidates:
                Candidate records.

            group_field:
                Field containing the audit group.

            score_field:
                Field containing AI screening score.

            label_field:
                Optional independent ground-truth qualification label.

        Returns:
            FairnessMetricsResult
        """

        candidate_list = list(candidates)

        if not candidate_list:
            return FairnessMetricsResult(
                total_candidates=0,
                groups={},
                reference_group=None,
                comparisons=[],
                warnings=[
                    "No candidates were supplied for fairness analysis."
                ],
            )

        groups = self._calculate_group_metrics(
            candidates=candidate_list,
            group_field=group_field,
            score_field=score_field,
            label_field=label_field,
        )

        reference_group = self._select_reference_group(groups)

        comparisons = self._calculate_comparisons(
            groups=groups,
            reference_group=reference_group,
        )

        warnings = self._generate_warnings(
            groups=groups,
            comparisons=comparisons,
        )

        return FairnessMetricsResult(
            total_candidates=len(candidate_list),
            groups=groups,
            reference_group=reference_group,
            comparisons=comparisons,
            warnings=warnings,
        )

    # ============================================================
    # GROUP METRICS
    # ============================================================

    def _calculate_group_metrics(
        self,
        candidates: List[Mapping[str, Any]],
        group_field: str,
        score_field: str,
        label_field: str,
    ) -> Dict[str, GroupFairnessMetrics]:

        grouped: Dict[str, List[Mapping[str, Any]]] = {}

        for candidate in candidates:

            group = self._get_group(
                candidate,
                group_field,
            )

            grouped.setdefault(group, []).append(candidate)

        result: Dict[str, GroupFairnessMetrics] = {}

        for group, group_candidates in grouped.items():

            scores = [
                self._get_score(
                    candidate,
                    score_field,
                )
                for candidate in group_candidates
            ]

            selected = sum(
                score >= self.selection_threshold
                for score in scores
            )

            total = len(group_candidates)

            selection_rate = (
                selected / total
                if total
                else 0.0
            )

            # ----------------------------------------------------
            # Confusion matrix
            # ----------------------------------------------------

            tp = 0
            fp = 0
            tn = 0
            fn = 0

            for candidate in group_candidates:

                score = self._get_score(
                    candidate,
                    score_field,
                )

                predicted_positive = (
                    score >= self.selection_threshold
                )

                actual_positive = self._get_label(
                    candidate,
                    label_field,
                )

                if actual_positive is None:
                    continue

                if predicted_positive and actual_positive:
                    tp += 1

                elif predicted_positive and not actual_positive:
                    fp += 1

                elif not predicted_positive and actual_positive:
                    fn += 1

                else:
                    tn += 1

            tpr = self._safe_divide(
                tp,
                tp + fn,
            )

            fpr = self._safe_divide(
                fp,
                fp + tn,
            )

            sorted_scores = sorted(scores)

            result[group] = GroupFairnessMetrics(
                group=group,
                total=total,
                selected=selected,
                selection_rate=round(
                    selection_rate,
                    4,
                ),
                average_score=round(
                    self._average(scores),
                    2,
                ),
                median_score=round(
                    self._median(sorted_scores),
                    2,
                ),
                true_positives=tp,
                false_positives=fp,
                true_negatives=tn,
                false_negatives=fn,
                true_positive_rate=round(
                    tpr,
                    4,
                ),
                false_positive_rate=round(
                    fpr,
                    4,
                ),
            )

        return result

    # ============================================================
    # REFERENCE GROUP
    # ============================================================

    @staticmethod
    def _select_reference_group(
        groups: Dict[str, GroupFairnessMetrics],
    ) -> Optional[str]:

        if not groups:
            return None

        return max(
            groups,
            key=lambda group: groups[group].selection_rate,
        )

    # ============================================================
    # GROUP COMPARISONS
    # ============================================================

    def _calculate_comparisons(
        self,
        groups: Dict[str, GroupFairnessMetrics],
        reference_group: Optional[str],
    ) -> List[FairnessComparison]:

        if not reference_group:
            return []

        reference = groups[reference_group]

        comparisons: List[FairnessComparison] = []

        for group, metrics in groups.items():

            if group == reference_group:
                continue

            selection_ratio = self._safe_divide(
                metrics.selection_rate,
                reference.selection_rate,
            )

            selection_difference = (
                metrics.selection_rate
                - reference.selection_rate
            )

            score_gap = (
                reference.average_score
                - metrics.average_score
            )

            tpr_difference = (
                metrics.true_positive_rate
                - reference.true_positive_rate
            )

            fpr_difference = (
                metrics.false_positive_rate
                - reference.false_positive_rate
            )

            comparisons.append(
                FairnessComparison(
                    group=group,
                    reference_group=reference_group,
                    selection_rate_ratio=round(
                        selection_ratio,
                        4,
                    ),
                    selection_rate_difference=round(
                        selection_difference,
                        4,
                    ),
                    average_score_gap=round(
                        score_gap,
                        2,
                    ),
                    true_positive_rate_difference=round(
                        tpr_difference,
                        4,
                    ),
                    false_positive_rate_difference=round(
                        fpr_difference,
                        4,
                    ),
                    disparate_impact=round(
                        selection_ratio,
                        4,
                    ),
                )
            )

        return comparisons

    # ============================================================
    # WARNINGS
    # ============================================================

    def _generate_warnings(
        self,
        groups: Dict[str, GroupFairnessMetrics],
        comparisons: List[FairnessComparison],
    ) -> List[str]:

        warnings: List[str] = []

        # --------------------------------------------------------
        # Small group warning
        # --------------------------------------------------------

        for group, metrics in groups.items():

            if metrics.total < 10:
                warnings.append(
                    f"Group '{group}' has only "
                    f"{metrics.total} candidate(s). "
                    "Metrics may be statistically unstable."
                )

        # --------------------------------------------------------
        # Disparate impact warning
        # --------------------------------------------------------

        for comparison in comparisons:

            if (
                comparison.selection_rate_ratio
                < self.disparity_threshold
            ):
                warnings.append(
                    f"Potential selection-rate disparity detected "
                    f"for group '{comparison.group}' compared with "
                    f"'{comparison.reference_group}'."
                )

        # --------------------------------------------------------
        # Score gap warning
        # --------------------------------------------------------

        for comparison in comparisons:

            if (
                comparison.average_score_gap
                > self.score_gap_threshold
            ):
                warnings.append(
                    f"Average score gap of "
                    f"{comparison.average_score_gap:.2f} points "
                    f"detected for group '{comparison.group}'."
                )

        # --------------------------------------------------------
        # Missing ground truth warning
        # --------------------------------------------------------

        if groups and all(
            metrics.true_positives
            + metrics.false_positives
            + metrics.true_negatives
            + metrics.false_negatives
            == 0
            for metrics in groups.values()
        ):
            warnings.append(
                "No independent ground-truth labels were available. "
                "TPR/FPR metrics could not be meaningfully evaluated."
            )

        return warnings

    # ============================================================
    # BASIC METRICS
    # ============================================================

    def selection_rate(
        self,
        selected: int,
        total: int,
    ) -> float:
        """
        Calculate selection rate.

        Formula:

            selected / total
        """

        return round(
            self._safe_divide(
                selected,
                total,
            ),
            4,
        )

    def demographic_parity_ratio(
        self,
        group_selection_rate: float,
        reference_selection_rate: float,
    ) -> float:
        """
        Calculate demographic parity ratio.

        Formula:

            group selection rate
            ---------------------
            reference selection rate
        """

        return round(
            self._safe_divide(
                group_selection_rate,
                reference_selection_rate,
            ),
            4,
        )

    def score_gap(
        self,
        group_scores: Iterable[float],
        reference_scores: Iterable[float],
    ) -> float:
        """
        Calculate average score difference.

        Positive value means the reference group has the higher
        average score.
        """

        group_values = [
            float(score)
            for score in group_scores
        ]

        reference_values = [
            float(score)
            for score in reference_scores
        ]

        return round(
            self._average(reference_values)
            - self._average(group_values),
            2,
        )

    def true_positive_rate(
        self,
        true_positives: int,
        false_negatives: int,
    ) -> float:
        """
        Calculate True Positive Rate.

        Formula:

            TP
            ------
            TP + FN
        """

        return round(
            self._safe_divide(
                true_positives,
                true_positives + false_negatives,
            ),
            4,
        )

    def false_positive_rate(
        self,
        false_positives: int,
        true_negatives: int,
    ) -> float:
        """
        Calculate False Positive Rate.

        Formula:

            FP
            ------
            FP + TN
        """

        return round(
            self._safe_divide(
                false_positives,
                false_positives + true_negatives,
            ),
            4,
        )

    # ============================================================
    # VALIDATION
    # ============================================================

    @staticmethod
    def _get_group(
        candidate: Mapping[str, Any],
        group_field: str,
    ) -> str:

        value = candidate.get(group_field)

        if value is None:
            raise ValueError(
                f"Candidate is missing group field "
                f"'{group_field}'."
            )

        value = str(value).strip()

        if not value:
            raise ValueError(
                f"Candidate has an empty group field "
                f"'{group_field}'."
            )

        return value

    @staticmethod
    def _get_score(
        candidate: Mapping[str, Any],
        score_field: str,
    ) -> float:

        value = candidate.get(score_field)

        if value is None:
            raise ValueError(
                f"Candidate is missing score field "
                f"'{score_field}'."
            )

        try:
            score = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid candidate score: {value!r}"
            ) from exc

        if not 0 <= score <= 100:
            raise ValueError(
                f"Candidate score must be between 0 and 100. "
                f"Received: {score}"
            )

        return score

    @staticmethod
    def _get_label(
        candidate: Mapping[str, Any],
        label_field: str,
    ) -> Optional[bool]:

        value = candidate.get(label_field)

        if value is None:
            return None

        if isinstance(value, bool):
            return value

        if isinstance(value, str):

            normalized = value.strip().lower()

            if normalized in {
                "true",
                "1",
                "yes",
                "qualified",
                "positive",
            }:
                return True

            if normalized in {
                "false",
                "0",
                "no",
                "unqualified",
                "negative",
            }:
                return False

        if isinstance(value, (int, float)):
            return bool(value)

        raise ValueError(
            f"Invalid ground-truth label: {value!r}"
        )

    def _validate_configuration(self) -> None:

        if not 0 <= self.selection_threshold <= 100:
            raise ValueError(
                "selection_threshold must be between 0 and 100."
            )

        if not 0 <= self.relevance_threshold <= 100:
            raise ValueError(
                "relevance_threshold must be between 0 and 100."
            )

        if not 0 < self.disparity_threshold <= 1:
            raise ValueError(
                "disparity_threshold must be greater than 0 "
                "and less than or equal to 1."
            )

        if self.score_gap_threshold < 0:
            raise ValueError(
                "score_gap_threshold cannot be negative."
            )

    # ============================================================
    # HELPERS
    # ============================================================

    @staticmethod
    def _safe_divide(
        numerator: float,
        denominator: float,
    ) -> float:

        if denominator == 0:
            return 0.0

        return numerator / denominator

    @staticmethod
    def _average(
        values: List[float],
    ) -> float:

        if not values:
            return 0.0

        return sum(values) / len(values)

    @staticmethod
    def _median(
        values: List[float],
    ) -> float:

        if not values:
            return 0.0

        length = len(values)
        middle = length // 2

        if length % 2:
            return values[middle]

        return (
            values[middle - 1]
            + values[middle]
        ) / 2


# ================================================================
# CONVENIENCE FUNCTION
# ================================================================


def calculate_fairness_metrics(
    candidates: Iterable[Mapping[str, Any]],
    selection_threshold: float = DEFAULT_SELECTION_THRESHOLD,
    relevance_threshold: float = DEFAULT_RELEVANCE_THRESHOLD,
    disparity_threshold: float = DEFAULT_DISPARITY_THRESHOLD,
    score_gap_threshold: float = DEFAULT_SCORE_GAP_THRESHOLD,
    group_field: str = "group",
    score_field: str = "score",
    label_field: str = "qualified",
) -> Dict[str, Any]:
    """
    Convenience function for calculating fairness metrics.

    Returns:
        JSON-compatible dictionary.
    """

    calculator = FairnessMetrics(
        selection_threshold=selection_threshold,
        relevance_threshold=relevance_threshold,
        disparity_threshold=disparity_threshold,
        score_gap_threshold=score_gap_threshold,
    )

    result = calculator.calculate(
        candidates=candidates,
        group_field=group_field,
        score_field=score_field,
        label_field=label_field,
    )

    return result.to_dict()


# ================================================================
# EXAMPLE
# ================================================================

if __name__ == "__main__":

    candidates = [
        {
            "candidate_id": 1,
            "group": "group_a",
            "score": 92,
            "qualified": True,
        },
        {
            "candidate_id": 2,
            "group": "group_a",
            "score": 85,
            "qualified": True,
        },
        {
            "candidate_id": 3,
            "group": "group_a",
            "score": 65,
            "qualified": False,
        },
        {
            "candidate_id": 4,
            "group": "group_b",
            "score": 72,
            "qualified": True,
        },
        {
            "candidate_id": 5,
            "group": "group_b",
            "score": 60,
            "qualified": True,
        },
        {
            "candidate_id": 6,
            "group": "group_b",
            "score": 55,
            "qualified": False,
        },
    ]

    metrics = calculate_fairness_metrics(
        candidates=candidates,
        selection_threshold=70,
    )

    print(metrics)