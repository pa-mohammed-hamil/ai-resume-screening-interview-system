"""
Fairness reporting module.

File:
    ai/fairness/fairness_report.py

Purpose:
    - Build fairness audit reports
    - Summarize group-level fairness metrics
    - Identify potential disparities
    - Generate recommendations
    - Provide JSON-compatible output
    - Provide human-readable report output

Important:
    Fairness auditing is separate from candidate ranking.
    Protected attributes must not be used as ranking features.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional


# ============================================================
# CONSTANTS
# ============================================================

REPORT_VERSION = "1.0"

RISK_LOW = "low"
RISK_MEDIUM = "medium"
RISK_HIGH = "high"

DEFAULT_SELECTION_RATE_RATIO = 0.80
DEFAULT_SCORE_GAP = 10.0
DEFAULT_RATE_DIFFERENCE = 0.10
DEFAULT_HIGH_RISK_RATIO = 0.50


# ============================================================
# DATA CLASSES
# ============================================================


@dataclass
class FairnessFinding:
    """Represents one detected fairness finding."""

    category: str
    severity: str
    message: str
    group: Optional[str] = None
    reference_group: Optional[str] = None
    metric: Optional[str] = None
    value: Optional[float] = None
    threshold: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FairnessRecommendation:
    """Recommended action for a fairness finding."""

    priority: str
    category: str
    action: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FairnessReport:
    """Complete fairness audit report."""

    report_id: str
    generated_at: str
    report_version: str

    total_candidates: int
    reference_group: Optional[str]

    overall_risk: str
    bias_detected: bool

    group_metrics: Dict[str, Dict[str, Any]] = field(
        default_factory=dict
    )

    comparisons: List[Dict[str, Any]] = field(
        default_factory=list
    )

    findings: List[FairnessFinding] = field(
        default_factory=list
    )

    recommendations: List[FairnessRecommendation] = field(
        default_factory=list
    )

    limitations: List[str] = field(
        default_factory=list
    )

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-compatible dictionary."""

        return {
            "report_id": self.report_id,
            "generated_at": self.generated_at,
            "report_version": self.report_version,
            "total_candidates": self.total_candidates,
            "reference_group": self.reference_group,
            "overall_risk": self.overall_risk,
            "bias_detected": self.bias_detected,
            "group_metrics": self.group_metrics,
            "comparisons": self.comparisons,
            "findings": [
                finding.to_dict()
                for finding in self.findings
            ],
            "recommendations": [
                recommendation.to_dict()
                for recommendation in self.recommendations
            ],
            "limitations": self.limitations,
        }


# ============================================================
# FAIRNESS REPORT GENERATOR
# ============================================================


class FairnessReportGenerator:
    """
    Generates a fairness audit report from fairness metrics.

    Expected metrics structure:

        {
            "total_candidates": 100,
            "reference_group": "group_a",
            "groups": {
                "group_a": {
                    "total": 50,
                    "selected": 30,
                    "selection_rate": 0.60,
                    "average_score": 78.5,
                    "true_positive_rate": 0.75,
                    "false_positive_rate": 0.15
                },
                ...
            },
            "comparisons": [...]
        }

    The class is intentionally flexible so it can consume
    dictionaries returned by fairness_metrics.py.
    """

    def __init__(
        self,
        selection_rate_ratio_threshold: float = (
            DEFAULT_SELECTION_RATE_RATIO
        ),
        score_gap_threshold: float = DEFAULT_SCORE_GAP,
        rate_difference_threshold: float = (
            DEFAULT_RATE_DIFFERENCE
        ),
    ) -> None:

        self.selection_rate_ratio_threshold = (
            selection_rate_ratio_threshold
        )

        self.score_gap_threshold = (
            score_gap_threshold
        )

        self.rate_difference_threshold = (
            rate_difference_threshold
        )

        self._validate_thresholds()

    # ========================================================
    # PUBLIC API
    # ========================================================

    def generate(
        self,
        metrics: Any,
        report_id: Optional[str] = None,
    ) -> FairnessReport:
        """
        Generate a complete fairness report.

        Args:
            metrics:
                Output from fairness_metrics.py.

            report_id:
                Optional report identifier.

        Returns:
            FairnessReport
        """

        if report_id is None:
            report_id = self._generate_report_id()

        normalized = self._normalize_metrics(
            metrics
        )

        findings = self._detect_findings(
            normalized
        )

        recommendations = (
            self._generate_recommendations(
                findings
            )
        )

        risk = self._calculate_risk(
            findings
        )

        limitations = self._generate_limitations(
            normalized
        )

        return FairnessReport(
            report_id=report_id,
            generated_at=self._timestamp(),
            report_version=REPORT_VERSION,
            total_candidates=normalized[
                "total_candidates"
            ],
            reference_group=normalized[
                "reference_group"
            ],
            overall_risk=risk,
            bias_detected=bool(findings),
            group_metrics=normalized[
                "groups"
            ],
            comparisons=normalized[
                "comparisons"
            ],
            findings=findings,
            recommendations=recommendations,
            limitations=limitations,
        )

    # ========================================================
    # NORMALIZATION
    # ========================================================

    def _normalize_metrics(
        self,
        metrics: Any,
    ) -> Dict[str, Any]:
        """Normalize dataclass or dictionary metric output."""

        if hasattr(metrics, "to_dict"):
            data = metrics.to_dict()

        elif hasattr(metrics, "__dict__"):
            data = vars(metrics)

        elif isinstance(metrics, Mapping):
            data = dict(metrics)

        else:
            raise TypeError(
                "metrics must be a mapping or an object "
                "with to_dict()/__dict__."
            )

        groups = data.get(
            "groups",
            data.get(
                "group_metrics",
                {},
            ),
        )

        comparisons = data.get(
            "comparisons",
            [],
        )

        total_candidates = data.get(
            "total_candidates",
            data.get(
                "total",
                0,
            ),
        )

        reference_group = data.get(
            "reference_group"
        )

        return {
            "total_candidates": int(
                total_candidates or 0
            ),
            "reference_group": reference_group,
            "groups": self._normalize_groups(
                groups
            ),
            "comparisons": self._normalize_comparisons(
                comparisons
            ),
        }

    def _normalize_groups(
        self,
        groups: Any,
    ) -> Dict[str, Dict[str, Any]]:
        """Normalize group metric objects."""

        if not isinstance(
            groups,
            Mapping,
        ):
            return {}

        result: Dict[str, Dict[str, Any]] = {}

        for group_name, values in groups.items():

            if hasattr(values, "to_dict"):
                values = values.to_dict()

            elif hasattr(values, "__dict__"):
                values = vars(values)

            elif isinstance(values, Mapping):
                values = dict(values)

            else:
                continue

            result[str(group_name)] = dict(
                values
            )

        return result

    def _normalize_comparisons(
        self,
        comparisons: Any,
    ) -> List[Dict[str, Any]]:
        """Normalize comparison metric objects."""

        if comparisons is None:
            return []

        result = []

        for comparison in comparisons:

            if hasattr(comparison, "to_dict"):
                comparison = comparison.to_dict()

            elif hasattr(comparison, "__dict__"):
                comparison = vars(comparison)

            elif isinstance(
                comparison,
                Mapping,
            ):
                comparison = dict(comparison)

            else:
                continue

            result.append(
                dict(comparison)
            )

        return result

    # ========================================================
    # FINDING DETECTION
    # ========================================================

    def _detect_findings(
        self,
        metrics: Mapping[str, Any],
    ) -> List[FairnessFinding]:
        """Detect potentially important disparities."""

        findings: List[FairnessFinding] = []

        groups = metrics["groups"]

        reference_group = metrics[
            "reference_group"
        ]

        # ----------------------------------------------------
        # Analyze explicit comparisons
        # ----------------------------------------------------

        for comparison in metrics[
            "comparisons"
        ]:

            group = self._get_value(
                comparison,
                "group",
            )

            comparison_reference = (
                self._get_value(
                    comparison,
                    "reference_group",
                    reference_group,
                )
            )

            ratio = self._number(
                comparison,
                [
                    "selection_rate_ratio",
                    "disparate_impact",
                ],
            )

            score_gap = self._number(
                comparison,
                [
                    "average_score_gap",
                    "score_gap",
                ],
            )

            tpr_difference = self._number(
                comparison,
                [
                    "true_positive_rate_difference",
                    "tpr_difference",
                ],
            )

            fpr_difference = self._number(
                comparison,
                [
                    "false_positive_rate_difference",
                    "fpr_difference",
                ],
            )

            selection_difference = self._number(
                comparison,
                [
                    "selection_rate_difference",
                ],
            )

            # Selection rate ratio
            if (
                ratio is not None
                and ratio
                < self.selection_rate_ratio_threshold
            ):
                severity = (
                    RISK_HIGH
                    if ratio
                    < DEFAULT_HIGH_RISK_RATIO
                    else RISK_MEDIUM
                )

                findings.append(
                    FairnessFinding(
                        category="selection_rate",
                        severity=severity,
                        message=(
                            f"Selection-rate disparity detected "
                            f"for group '{group}' relative to "
                            f"'{comparison_reference}'."
                        ),
                        group=group,
                        reference_group=(
                            comparison_reference
                        ),
                        metric="selection_rate_ratio",
                        value=ratio,
                        threshold=(
                            self.selection_rate_ratio_threshold
                        ),
                    )
                )

            # Score gap
            if (
                score_gap is not None
                and abs(score_gap)
                > self.score_gap_threshold
            ):
                findings.append(
                    FairnessFinding(
                        category="score_gap",
                        severity=RISK_MEDIUM,
                        message=(
                            f"Average screening scores differ "
                            f"by {abs(score_gap):.2f} points "
                            f"between '{group}' and "
                            f"'{comparison_reference}'."
                        ),
                        group=group,
                        reference_group=(
                            comparison_reference
                        ),
                        metric="average_score_gap",
                        value=score_gap,
                        threshold=(
                            self.score_gap_threshold
                        ),
                    )
                )

            # TPR
            if (
                tpr_difference is not None
                and abs(tpr_difference)
                >= self.rate_difference_threshold
            ):
                severity = (
                    RISK_HIGH
                    if abs(tpr_difference) >= 0.20
                    else RISK_MEDIUM
                )

                findings.append(
                    FairnessFinding(
                        category="true_positive_rate",
                        severity=severity,
                        message=(
                            f"True-positive-rate difference "
                            f"detected between '{group}' "
                            f"and '{comparison_reference}'."
                        ),
                        group=group,
                        reference_group=(
                            comparison_reference
                        ),
                        metric=(
                            "true_positive_rate_difference"
                        ),
                        value=tpr_difference,
                        threshold=(
                            self.rate_difference_threshold
                        ),
                    )
                )

            # FPR
            if (
                fpr_difference is not None
                and abs(fpr_difference)
                >= self.rate_difference_threshold
            ):
                severity = (
                    RISK_HIGH
                    if abs(fpr_difference) >= 0.20
                    else RISK_MEDIUM
                )

                findings.append(
                    FairnessFinding(
                        category="false_positive_rate",
                        severity=severity,
                        message=(
                            f"False-positive-rate difference "
                            f"detected between '{group}' "
                            f"and '{comparison_reference}'."
                        ),
                        group=group,
                        reference_group=(
                            comparison_reference
                        ),
                        metric=(
                            "false_positive_rate_difference"
                        ),
                        value=fpr_difference,
                        threshold=(
                            self.rate_difference_threshold
                        ),
                    )
                )

            # Selection rate difference
            if (
                selection_difference is not None
                and abs(selection_difference)
                >= self.rate_difference_threshold
            ):
                findings.append(
                    FairnessFinding(
                        category="selection_rate_difference",
                        severity=RISK_MEDIUM,
                        message=(
                            f"Selection rates differ by "
                            f"{abs(selection_difference):.2%} "
                            f"between '{group}' and "
                            f"'{comparison_reference}'."
                        ),
                        group=group,
                        reference_group=(
                            comparison_reference
                        ),
                        metric=(
                            "selection_rate_difference"
                        ),
                        value=selection_difference,
                        threshold=(
                            self.rate_difference_threshold
                        ),
                    )
                )

        # ----------------------------------------------------
        # Fallback group-level analysis
        # ----------------------------------------------------

        if not metrics["comparisons"]:

            findings.extend(
                self._analyze_groups(
                    groups=groups,
                    reference_group=reference_group,
                )
            )

        return self._deduplicate_findings(
            findings
        )

    # ========================================================
    # GROUP ANALYSIS
    # ========================================================

    def _analyze_groups(
        self,
        groups: Mapping[str, Mapping[str, Any]],
        reference_group: Optional[str],
    ) -> List[FairnessFinding]:
        """Analyze group metrics when comparisons are unavailable."""

        findings: List[FairnessFinding] = []

        if not groups:
            return findings

        if reference_group not in groups:
            reference_group = next(
                iter(groups),
                None,
            )

        if reference_group is None:
            return findings

        reference = groups[
            reference_group
        ]

        reference_selection = self._read_metric(
            reference,
            "selection_rate",
        )

        reference_score = self._read_metric(
            reference,
            "average_score",
        )

        reference_tpr = self._read_metric(
            reference,
            "true_positive_rate",
        )

        reference_fpr = self._read_metric(
            reference,
            "false_positive_rate",
        )

        for group_name, group in groups.items():

            if group_name == reference_group:
                continue

            selection = self._read_metric(
                group,
                "selection_rate",
            )

            score = self._read_metric(
                group,
                "average_score",
            )

            tpr = self._read_metric(
                group,
                "true_positive_rate",
            )

            fpr = self._read_metric(
                group,
                "false_positive_rate",
            )

            # Selection ratio
            if (
                selection is not None
                and reference_selection
                not in (None, 0)
            ):

                ratio = (
                    selection
                    / reference_selection
                )

                if (
                    ratio
                    < self.selection_rate_ratio_threshold
                ):
                    severity = (
                        RISK_HIGH
                        if ratio
                        < DEFAULT_HIGH_RISK_RATIO
                        else RISK_MEDIUM
                    )

                    findings.append(
                        FairnessFinding(
                            category="selection_rate",
                            severity=severity,
                            message=(
                                f"Selection-rate ratio for "
                                f"'{group_name}' is "
                                f"{ratio:.2f} relative to "
                                f"'{reference_group}'."
                            ),
                            group=group_name,
                            reference_group=(
                                reference_group
                            ),
                            metric="selection_rate_ratio",
                            value=ratio,
                            threshold=(
                                self.selection_rate_ratio_threshold
                            ),
                        )
                    )

            # Score gap
            if (
                score is not None
                and reference_score is not None
            ):

                gap = (
                    score
                    - reference_score
                )

                if (
                    abs(gap)
                    > self.score_gap_threshold
                ):
                    findings.append(
                        FairnessFinding(
                            category="score_gap",
                            severity=RISK_MEDIUM,
                            message=(
                                f"Average score difference "
                                f"between '{group_name}' "
                                f"and '{reference_group}' "
                                f"is {gap:.2f} points."
                            ),
                            group=group_name,
                            reference_group=(
                                reference_group
                            ),
                            metric="average_score_gap",
                            value=gap,
                            threshold=(
                                self.score_gap_threshold
                            ),
                        )
                    )

            # TPR
            if (
                tpr is not None
                and reference_tpr is not None
            ):

                difference = (
                    tpr - reference_tpr
                )

                if (
                    abs(difference)
                    >= self.rate_difference_threshold
                ):
                    findings.append(
                        FairnessFinding(
                            category="true_positive_rate",
                            severity=RISK_MEDIUM,
                            message=(
                                f"True-positive-rate difference "
                                f"between '{group_name}' and "
                                f"'{reference_group}' is "
                                f"{difference:.2%}."
                            ),
                            group=group_name,
                            reference_group=(
                                reference_group
                            ),
                            metric=(
                                "true_positive_rate_difference"
                            ),
                            value=difference,
                            threshold=(
                                self.rate_difference_threshold
                            ),
                        )
                    )

            # FPR
            if (
                fpr is not None
                and reference_fpr is not None
            ):

                difference = (
                    fpr - reference_fpr
                )

                if (
                    abs(difference)
                    >= self.rate_difference_threshold
                ):
                    findings.append(
                        FairnessFinding(
                            category="false_positive_rate",
                            severity=RISK_MEDIUM,
                            message=(
                                f"False-positive-rate difference "
                                f"between '{group_name}' and "
                                f"'{reference_group}' is "
                                f"{difference:.2%}."
                            ),
                            group=group_name,
                            reference_group=(
                                reference_group
                            ),
                            metric=(
                                "false_positive_rate_difference"
                            ),
                            value=difference,
                            threshold=(
                                self.rate_difference_threshold
                            ),
                        )
                    )

        return findings

    # ========================================================
    # RISK
    # ========================================================

    @staticmethod
    def _calculate_risk(
        findings: List[FairnessFinding],
    ) -> str:
        """Calculate overall audit risk."""

        if any(
            finding.severity == RISK_HIGH
            for finding in findings
        ):
            return RISK_HIGH

        if any(
            finding.severity == RISK_MEDIUM
            for finding in findings
        ):
            return RISK_MEDIUM

        return RISK_LOW

    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    @staticmethod
    def _generate_recommendations(
        findings: List[FairnessFinding],
    ) -> List[FairnessRecommendation]:
        """Generate recommendations based on findings."""

        if not findings:
            return [
                FairnessRecommendation(
                    priority="low",
                    category="monitoring",
                    action=(
                        "Continue periodic fairness evaluation "
                        "using representative validation data."
                    ),
                )
            ]

        recommendations: List[
            FairnessRecommendation
        ] = []

        categories = {
            finding.category
            for finding in findings
        }

        if "selection_rate" in categories:
            recommendations.append(
                FairnessRecommendation(
                    priority="high",
                    category="selection_rate",
                    action=(
                        "Review the screening and ranking pipeline "
                        "for possible sources of unequal selection "
                        "rates."
                    ),
                )
            )

        if "score_gap" in categories:
            recommendations.append(
                FairnessRecommendation(
                    priority="medium",
                    category="scoring",
                    action=(
                        "Review scoring features, normalization, "
                        "training data, and job-specific requirements "
                        "to understand the observed score gap."
                    ),
                )
            )

        if "true_positive_rate" in categories:
            recommendations.append(
                FairnessRecommendation(
                    priority="high",
                    category="true_positive_rate",
                    action=(
                        "Validate qualification labels and examine "
                        "whether qualified candidates are being "
                        "missed disproportionately."
                    ),
                )
            )

        if "false_positive_rate" in categories:
            recommendations.append(
                FairnessRecommendation(
                    priority="high",
                    category="false_positive_rate",
                    action=(
                        "Review false-positive behavior and validate "
                        "whether candidates are being incorrectly "
                        "advanced at different rates."
                    ),
                )
            )

        recommendations.append(
            FairnessRecommendation(
                priority="medium",
                category="human_review",
                action=(
                    "Require appropriate human review before making "
                    "employment decisions based on automated "
                    "screening results."
                ),
            )
        )

        recommendations.append(
            FairnessRecommendation(
                priority="medium",
                category="data_quality",
                action=(
                    "Increase the size and representativeness of "
                    "the evaluation dataset where necessary."
                ),
            )
        )

        return recommendations

    # ========================================================
    # LIMITATIONS
    # ========================================================

    @staticmethod
    def _generate_limitations(
        metrics: Mapping[str, Any],
    ) -> List[str]:

        limitations = [
            (
                "Statistical disparity does not by itself establish "
                "the cause of the disparity."
            ),
            (
                "Small group sizes can make fairness metrics "
                "statistically unstable."
            ),
            (
                "Results depend on the quality and representativeness "
                "of the evaluation dataset."
            ),
            (
                "Ground-truth labels should be independently "
                "validated."
            ),
            (
                "Protected attributes should not be used as ranking "
                "features."
            ),
            (
                "Fairness metrics should be interpreted together "
                "rather than relying on a single metric."
            ),
            (
                "This report is an engineering audit tool and is "
                "not a legal or regulatory determination."
            ),
        ]

        if metrics["total_candidates"] < 100:
            limitations.append(
                (
                    "The evaluation dataset contains fewer than "
                    "100 candidates; conclusions should therefore "
                    "be treated cautiously."
                )
            )

        return limitations

    # ========================================================
    # REPORT FORMATS
    # ========================================================

    def to_json_dict(
        self,
        report: FairnessReport,
    ) -> Dict[str, Any]:
        """Return JSON-ready report."""

        return report.to_dict()

    def to_text(
        self,
        report: FairnessReport,
    ) -> str:
        """Render the report as plain text."""

        lines = []

        lines.append(
            "=" * 70
        )
        lines.append(
            "AI RESUME SCREENING FAIRNESS AUDIT"
        )
        lines.append(
            "=" * 70
        )

        lines.append(
            f"Report ID       : {report.report_id}"
        )

        lines.append(
            f"Generated At    : {report.generated_at}"
        )

        lines.append(
            f"Total Candidates: {report.total_candidates}"
        )

        lines.append(
            f"Reference Group : "
            f"{report.reference_group or 'N/A'}"
        )

        lines.append(
            f"Overall Risk    : "
            f"{report.overall_risk.upper()}"
        )

        lines.append(
            f"Bias Detected   : "
            f"{'YES' if report.bias_detected else 'NO'}"
        )

        # ----------------------------------------------------
        # Group metrics
        # ----------------------------------------------------

        lines.append("")
        lines.append(
            "-" * 70
        )
        lines.append(
            "GROUP METRICS"
        )
        lines.append(
            "-" * 70
        )

        if report.group_metrics:

            for group, values in (
                report.group_metrics.items()
            ):

                lines.append("")
                lines.append(
                    f"Group: {group}"
                )

                for key, value in values.items():

                    if isinstance(
                        value,
                        float,
                    ):

                        if (
                            "rate" in key.lower()
                            or key.lower()
                            in {
                                "tpr",
                                "fpr",
                            }
                        ):
                            formatted = (
                                f"{value:.2%}"
                            )
                        else:
                            formatted = (
                                f"{value:.2f}"
                            )

                    else:
                        formatted = str(value)

                    lines.append(
                        f"  {key}: {formatted}"
                    )

        else:
            lines.append(
                "No group metrics available."
            )

        # ----------------------------------------------------
        # Findings
        # ----------------------------------------------------

        lines.append("")
        lines.append(
            "-" * 70
        )
        lines.append(
            "FINDINGS"
        )
        lines.append(
            "-" * 70
        )

        if report.findings:

            for index, finding in enumerate(
                report.findings,
                start=1,
            ):

                lines.append(
                    f"{index}. "
                    f"[{finding.severity.upper()}] "
                    f"{finding.message}"
                )

        else:

            lines.append(
                "No potential fairness disparities "
                "were detected under the configured thresholds."
            )

        # ----------------------------------------------------
        # Recommendations
        # ----------------------------------------------------

        lines.append("")
        lines.append(
            "-" * 70
        )
        lines.append(
            "RECOMMENDATIONS"
        )
        lines.append(
            "-" * 70
        )

        for index, recommendation in enumerate(
            report.recommendations,
            start=1,
        ):

            lines.append(
                f"{index}. "
                f"[{recommendation.priority.upper()}] "
                f"{recommendation.action}"
            )

        # ----------------------------------------------------
        # Limitations
        # ----------------------------------------------------

        lines.append("")
        lines.append(
            "-" * 70
        )
        lines.append(
            "LIMITATIONS"
        )
        lines.append(
            "-" * 70
        )

        for limitation in report.limitations:

            lines.append(
                f"- {limitation}"
            )

        lines.append("")
        lines.append(
            "=" * 70
        )

        return "\n".join(lines)

    # ========================================================
    # HELPERS
    # ========================================================

    def _validate_thresholds(self) -> None:

        if not (
            0 < self.selection_rate_ratio_threshold <= 1
        ):
            raise ValueError(
                "selection_rate_ratio_threshold must "
                "be between 0 and 1."
            )

        if self.score_gap_threshold < 0:
            raise ValueError(
                "score_gap_threshold cannot be negative."
            )

        if not (
            0 < self.rate_difference_threshold <= 1
        ):
            raise ValueError(
                "rate_difference_threshold must "
                "be between 0 and 1."
            )

    @staticmethod
    def _generate_report_id() -> str:

        timestamp = datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%d%H%M%S"
        )

        return (
            f"FAIRNESS-{timestamp}"
        )

    @staticmethod
    def _timestamp() -> str:

        return datetime.now(
            timezone.utc
        ).isoformat()

    @staticmethod
    def _get_value(
        mapping: Mapping[str, Any],
        key: str,
        default: Any = None,
    ) -> Any:

        return mapping.get(
            key,
            default,
        )

    @staticmethod
    def _number(
        mapping: Mapping[str, Any],
        keys: List[str],
    ) -> Optional[float]:

        for key in keys:

            value = mapping.get(
                key
            )

            if value is None:
                continue

            try:
                return float(value)

            except (
                TypeError,
                ValueError,
            ):
                continue

        return None

    @staticmethod
    def _read_metric(
        mapping: Mapping[str, Any],
        key: str,
    ) -> Optional[float]:

        value = mapping.get(
            key
        )

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
    def _deduplicate_findings(
        findings: List[FairnessFinding],
    ) -> List[FairnessFinding]:

        result = []
        seen = set()

        for finding in findings:

            key = (
                finding.category,
                finding.group,
                finding.reference_group,
            )

            if key in seen:
                continue

            seen.add(key)
            result.append(finding)

        return result


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================


def generate_fairness_report(
    metrics: Any,
    report_id: Optional[str] = None,
    selection_rate_ratio_threshold: float = (
        DEFAULT_SELECTION_RATE_RATIO
    ),
    score_gap_threshold: float = DEFAULT_SCORE_GAP,
    rate_difference_threshold: float = (
        DEFAULT_RATE_DIFFERENCE
    ),
) -> Dict[str, Any]:
    """
    Generate a JSON-compatible fairness report.

    Example:

        report = generate_fairness_report(metrics)

        return report
    """

    generator = FairnessReportGenerator(
        selection_rate_ratio_threshold=(
            selection_rate_ratio_threshold
        ),
        score_gap_threshold=(
            score_gap_threshold
        ),
        rate_difference_threshold=(
            rate_difference_threshold
        ),
    )

    report = generator.generate(
        metrics=metrics,
        report_id=report_id,
    )

    return report.to_dict()


# ============================================================
# EXAMPLE
# ============================================================


if __name__ == "__main__":

    sample_metrics = {
        "total_candidates": 200,
        "reference_group": "group_a",

        "groups": {
            "group_a": {
                "total": 100,
                "selected": 70,
                "selection_rate": 0.70,
                "average_score": 82.0,
                "true_positive_rate": 0.80,
                "false_positive_rate": 0.10,
            },
            "group_b": {
                "total": 100,
                "selected": 45,
                "selection_rate": 0.45,
                "average_score": 69.0,
                "true_positive_rate": 0.62,
                "false_positive_rate": 0.22,
            },
        },

        "comparisons": [
            {
                "group": "group_b",
                "reference_group": "group_a",
                "selection_rate_ratio": 0.6429,
                "selection_rate_difference": -0.25,
                "average_score_gap": -13.0,
                "true_positive_rate_difference": -0.18,
                "false_positive_rate_difference": 0.12,
            }
        ],
    }

    generator = FairnessReportGenerator()

    report = generator.generate(
        sample_metrics
    )

    print(
        generator.to_text(report)
    )