# Project scaffold file
"""
Bias detection utilities for the AI Resume Screening System.

This module analyzes candidate screening/ranking outcomes for potential
disparities across groups.

Important:
- Protected attributes should NOT be used as ranking features.
- This module is for auditing and monitoring model behavior.
- Results should be reviewed by qualified humans.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional


# ================================================================
# CONSTANTS
# ================================================================

DEFAULT_SELECTION_THRESHOLD = 70.0
DEFAULT_DISPARITY_THRESHOLD = 0.80
DEFAULT_SCORE_GAP_THRESHOLD = 10.0


# ================================================================
# DATA CLASSES
# ================================================================


@dataclass
class GroupMetrics:
    """Metrics calculated for one candidate group."""

    group: str
    total_candidates: int
    selected_candidates: int
    selection_rate: float
    average_score: float
    median_score: float
    min_score: Optional[float] = None
    max_score: Optional[float] = None

    @property
    def rejection_rate(self) -> float:
        """Return the percentage of candidates not selected."""

        if self.total_candidates == 0:
            return 0.0

        return round(
            1.0 - self.selection_rate,
            4,
        )


@dataclass
class BiasFinding:
    """Represents one potential fairness issue."""

    metric: str
    group: str
    reference_group: str
    value: float
    threshold: float
    severity: str
    message: str


@dataclass
class BiasDetectionResult:
    """Complete result returned by the bias detector."""

    total_candidates: int
    groups: Dict[str, GroupMetrics]
    reference_group: Optional[str]
    findings: List[BiasFinding] = field(default_factory=list)

    @property
    def has_potential_bias(self) -> bool:
        """Return True when one or more potential issues are detected."""

        return len(self.findings) > 0

    @property
    def risk_level(self) -> str:
        """Calculate overall risk level."""

        if not self.findings:
            return "low"

        severities = {
            finding.severity
            for finding in self.findings
        }

        if "high" in severities:
            return "high"

        if "medium" in severities:
            return "medium"

        return "low"

    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a JSON-compatible dictionary."""

        return {
            "total_candidates": self.total_candidates,
            "reference_group": self.reference_group,
            "risk_level": self.risk_level,
            "has_potential_bias": self.has_potential_bias,
            "groups": {
                name: {
                    "group": metrics.group,
                    "total_candidates": metrics.total_candidates,
                    "selected_candidates": metrics.selected_candidates,
                    "selection_rate": metrics.selection_rate,
                    "rejection_rate": metrics.rejection_rate,
                    "average_score": metrics.average_score,
                    "median_score": metrics.median_score,
                    "min_score": metrics.min_score,
                    "max_score": metrics.max_score,
                }
                for name, metrics in self.groups.items()
            },
            "findings": [
                {
                    "metric": finding.metric,
                    "group": finding.group,
                    "reference_group": finding.reference_group,
                    "value": finding.value,
                    "threshold": finding.threshold,
                    "severity": finding.severity,
                    "message": finding.message,
                }
                for finding in self.findings
            ],
        }


# ================================================================
# BIAS DETECTOR
# ================================================================


class BiasDetector:
    """
    Detect potential disparities in candidate screening outcomes.

    Expected candidate format:

    {
        "candidate_id": 1,
        "group": "group_a",
        "score": 82.5
    }

    The ``group`` field is supplied only for fairness auditing and must
    not be passed into the candidate ranking model as a ranking feature.
    """

    def __init__(
        self,
        selection_threshold: float = DEFAULT_SELECTION_THRESHOLD,
        disparity_threshold: float = DEFAULT_DISPARITY_THRESHOLD,
        score_gap_threshold: float = DEFAULT_SCORE_GAP_THRESHOLD,
    ) -> None:
        self.selection_threshold = selection_threshold
        self.disparity_threshold = disparity_threshold
        self.score_gap_threshold = score_gap_threshold

        self._validate_configuration()

    # ============================================================
    # PUBLIC API
    # ============================================================

    def detect(
        self,
        candidates: Iterable[Mapping[str, Any]],
        group_field: str = "group",
        score_field: str = "score",
    ) -> BiasDetectionResult:
        """
        Analyze candidates for potential selection and score disparities.

        Args:
            candidates:
                Iterable containing candidate records.

            group_field:
                Field containing the audit group.

            score_field:
                Field containing the candidate score.

        Returns:
            BiasDetectionResult
        """

        candidate_list = list(candidates)

        if not candidate_list:
            return BiasDetectionResult(
                total_candidates=0,
                groups={},
                reference_group=None,
                findings=[],
            )

        groups = self._calculate_group_metrics(
            candidate_list,
            group_field=group_field,
            score_field=score_field,
        )

        reference_group = self._select_reference_group(groups)

        findings = self._detect_disparities(
            groups=groups,
            reference_group=reference_group,
        )

        return BiasDetectionResult(
            total_candidates=len(candidate_list),
            groups=groups,
            reference_group=reference_group,
            findings=findings,
        )

    # ============================================================
    # GROUP METRICS
    # ============================================================

    def _calculate_group_metrics(
        self,
        candidates: List[Mapping[str, Any]],
        group_field: str,
        score_field: str,
    ) -> Dict[str, GroupMetrics]:
        """Calculate screening metrics for each group."""

        grouped: Dict[str, List[float]] = {}

        for candidate in candidates:
            group = self._get_group(candidate, group_field)
            score = self._get_score(candidate, score_field)

            grouped.setdefault(group, []).append(score)

        metrics: Dict[str, GroupMetrics] = {}

        for group, scores in grouped.items():
            total = len(scores)

            selected = sum(
                score >= self.selection_threshold
                for score in scores
            )

            selection_rate = (
                selected / total
                if total > 0
                else 0.0
            )

            sorted_scores = sorted(scores)

            average_score = sum(scores) / total

            median_score = self._median(sorted_scores)

            metrics[group] = GroupMetrics(
                group=group,
                total_candidates=total,
                selected_candidates=selected,
                selection_rate=round(selection_rate, 4),
                average_score=round(average_score, 2),
                median_score=round(median_score, 2),
                min_score=round(min(scores), 2),
                max_score=round(max(scores), 2),
            )

        return metrics

    # ============================================================
    # REFERENCE GROUP
    # ============================================================

    @staticmethod
    def _select_reference_group(
        groups: Dict[str, GroupMetrics],
    ) -> Optional[str]:
        """
        Select the group with the highest selection rate as reference.

        This is a monitoring heuristic, not a legal determination of
        which group is privileged or disadvantaged.
        """

        if not groups:
            return None

        return max(
            groups,
            key=lambda group: groups[group].selection_rate,
        )

    # ============================================================
    # DISPARITY DETECTION
    # ============================================================

    def _detect_disparities(
        self,
        groups: Dict[str, GroupMetrics],
        reference_group: Optional[str],
    ) -> List[BiasFinding]:
        """Detect selection-rate and score disparities."""

        if not reference_group:
            return []

        reference = groups[reference_group]

        findings: List[BiasFinding] = []

        for group_name, metrics in groups.items():

            if group_name == reference_group:
                continue

            # ----------------------------------------------------
            # Selection-rate ratio
            # ----------------------------------------------------

            selection_ratio = self._selection_rate_ratio(
                metrics.selection_rate,
                reference.selection_rate,
            )

            if selection_ratio < self.disparity_threshold:
                findings.append(
                    BiasFinding(
                        metric="selection_rate_ratio",
                        group=group_name,
                        reference_group=reference_group,
                        value=round(selection_ratio, 4),
                        threshold=self.disparity_threshold,
                        severity=self._severity_from_ratio(
                            selection_ratio
                        ),
                        message=(
                            f"Selection rate for '{group_name}' "
                            f"is substantially lower than the "
                            f"reference group '{reference_group}'."
                        ),
                    )
                )

            # ----------------------------------------------------
            # Average score gap
            # ----------------------------------------------------

            score_gap = (
                reference.average_score
                - metrics.average_score
            )

            if score_gap > self.score_gap_threshold:
                findings.append(
                    BiasFinding(
                        metric="average_score_gap",
                        group=group_name,
                        reference_group=reference_group,
                        value=round(score_gap, 2),
                        threshold=self.score_gap_threshold,
                        severity=self._severity_from_score_gap(
                            score_gap
                        ),
                        message=(
                            f"Average score for '{group_name}' "
                            f"is lower than the reference group "
                            f"'{reference_group}' by "
                            f"{score_gap:.2f} points."
                        ),
                    )
                )

        return findings

    # ============================================================
    # STATISTICAL HELPERS
    # ============================================================

    @staticmethod
    def _selection_rate_ratio(
        group_rate: float,
        reference_rate: float,
    ) -> float:
        """Calculate group selection rate / reference rate."""

        if reference_rate <= 0:
            return 1.0

        return group_rate / reference_rate

    @staticmethod
    def _severity_from_ratio(
        ratio: float,
    ) -> str:
        """Assign severity from selection-rate ratio."""

        if ratio < 0.50:
            return "high"

        if ratio < 0.70:
            return "medium"

        return "low"

    @staticmethod
    def _severity_from_score_gap(
        gap: float,
    ) -> str:
        """Assign severity from average score gap."""

        if gap >= 20:
            return "high"

        if gap >= 15:
            return "medium"

        return "low"

    @staticmethod
    def _median(values: List[float]) -> float:
        """Calculate median."""

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

    # ============================================================
    # VALIDATION
    # ============================================================

    @staticmethod
    def _get_group(
        candidate: Mapping[str, Any],
        group_field: str,
    ) -> str:
        """Get and validate candidate group."""

        value = candidate.get(group_field)

        if value is None:
            raise ValueError(
                f"Candidate is missing group field: "
                f"'{group_field}'."
            )

        value = str(value).strip()

        if not value:
            raise ValueError(
                f"Candidate has an empty group field: "
                f"'{group_field}'."
            )

        return value

    @staticmethod
    def _get_score(
        candidate: Mapping[str, Any],
        score_field: str,
    ) -> float:
        """Get and validate candidate score."""

        value = candidate.get(score_field)

        if value is None:
            raise ValueError(
                f"Candidate is missing score field: "
                f"'{score_field}'."
            )

        try:
            score = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid candidate score: {value!r}"
            ) from exc

        if score < 0 or score > 100:
            raise ValueError(
                f"Candidate score must be between 0 and 100: "
                f"{score}"
            )

        return score

    def _validate_configuration(self) -> None:
        """Validate detector configuration."""

        if not 0 <= self.selection_threshold <= 100:
            raise ValueError(
                "selection_threshold must be between 0 and 100."
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


# ================================================================
# CONVENIENCE FUNCTION
# ================================================================


def detect_bias(
    candidates: Iterable[Mapping[str, Any]],
    selection_threshold: float = DEFAULT_SELECTION_THRESHOLD,
    disparity_threshold: float = DEFAULT_DISPARITY_THRESHOLD,
    score_gap_threshold: float = DEFAULT_SCORE_GAP_THRESHOLD,
    group_field: str = "group",
    score_field: str = "score",
) -> Dict[str, Any]:
    """
    Convenience wrapper around BiasDetector.

    Returns:
        JSON-compatible dictionary.
    """

    detector = BiasDetector(
        selection_threshold=selection_threshold,
        disparity_threshold=disparity_threshold,
        score_gap_threshold=score_gap_threshold,
    )

    result = detector.detect(
        candidates=candidates,
        group_field=group_field,
        score_field=score_field,
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
            "score": 90,
        },
        {
            "candidate_id": 2,
            "group": "group_a",
            "score": 85,
        },
        {
            "candidate_id": 3,
            "group": "group_a",
            "score": 80,
        },
        {
            "candidate_id": 4,
            "group": "group_b",
            "score": 65,
        },
        {
            "candidate_id": 5,
            "group": "group_b",
            "score": 60,
        },
        {
            "candidate_id": 6,
            "group": "group_b",
            "score": 75,
        },
    ]

    result = detect_bias(candidates)

    print(result)