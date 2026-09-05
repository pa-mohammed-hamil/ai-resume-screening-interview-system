"""
Candidate Ranking Engine
========================

File:
    ai/ranking/candidate_ranker.py

Purpose:
    - Rank candidates against a job
    - Combine multiple scoring signals
    - Generate explainable ranking results
    - Handle missing scores safely
    - Support configurable weights
    - Provide top-K candidates
    - Keep fairness auditing separate from ranking

Expected candidate input:

{
    "candidate_id": 101,
    "name": "John Doe",
    "skill_score": 90,
    "experience_score": 85,
    "education_score": 80,
    "ats_score": 88,
    "semantic_score": 92,
    "keyword_score": 84
}

All ranking scores are expected to be between 0 and 100.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional


# ============================================================
# CONSTANTS
# ============================================================

MIN_SCORE = 0.0
MAX_SCORE = 100.0

STRONG_SCORE = 80.0
WEAK_SCORE = 50.0

DEFAULT_TOP_K = 50

DEFAULT_WEIGHTS = {
    "skill_score": 0.30,
    "experience_score": 0.20,
    "education_score": 0.10,
    "ats_score": 0.15,
    "semantic_score": 0.15,
    "keyword_score": 0.10,
}


# Protected attributes are never used by the ranking algorithm.
# They can be retained separately for fairness auditing.
PROTECTED_FIELDS = {
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
class RankingWeights:
    """Weights used by the candidate ranking engine."""

    skill_score: float = 0.30
    experience_score: float = 0.20
    education_score: float = 0.10
    ats_score: float = 0.15
    semantic_score: float = 0.15
    keyword_score: float = 0.10

    def to_dict(self) -> Dict[str, float]:
        return {
            "skill_score": self.skill_score,
            "experience_score": self.experience_score,
            "education_score": self.education_score,
            "ats_score": self.ats_score,
            "semantic_score": self.semantic_score,
            "keyword_score": self.keyword_score,
        }

    def validate(self) -> None:
        """Validate ranking weights."""

        weights = self.to_dict()

        for name, value in weights.items():

            if value < 0:
                raise ValueError(
                    f"Weight '{name}' cannot be negative."
                )

        if sum(weights.values()) <= 0:
            raise ValueError(
                "At least one ranking weight must be greater than zero."
            )


@dataclass
class CandidateRanking:
    """Ranking result for an individual candidate."""

    candidate_id: Any
    rank: int
    score: float

    breakdown: Dict[str, float]

    weighted_breakdown: Dict[str, float]

    strengths: List[str] = field(
        default_factory=list
    )

    weaknesses: List[str] = field(
        default_factory=list
    )

    explanation: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "rank": self.rank,
            "score": self.score,
            "breakdown": self.breakdown,
            "weighted_breakdown": self.weighted_breakdown,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "explanation": self.explanation,
            "metadata": self.metadata,
        }


@dataclass
class RankingResult:
    """Complete ranking response."""

    total_candidates: int

    ranked_candidates: List[CandidateRanking]

    weights: Dict[str, float]

    top_k: Optional[int]

    skipped_candidates: List[Any] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_candidates": self.total_candidates,
            "ranked_candidates": [
                candidate.to_dict()
                for candidate in self.ranked_candidates
            ],
            "weights": self.weights,
            "top_k": self.top_k,
            "skipped_candidates": self.skipped_candidates,
            "warnings": self.warnings,
        }


# ============================================================
# CANDIDATE RANKER
# ============================================================


class CandidateRanker:
    """
    Explainable weighted candidate ranking engine.

    Ranking pipeline:

        Skill Score
             +
        Experience Score
             +
        Education Score
             +
        ATS Score
             +
        Semantic Score
             +
        Keyword Score
             ↓
        Weighted Final Score
             ↓
        Candidate Ranking

    Protected/sensitive attributes are deliberately excluded.
    """

    def __init__(
        self,
        weights: Optional[
            Mapping[str, float]
        ] = None,
    ) -> None:

        self.weights = self._build_weights(
            weights
        )

        self.weights.validate()

        self.normalized_weights = (
            self._normalize_weights(
                self.weights.to_dict()
            )
        )

    # ========================================================
    # PUBLIC API
    # ========================================================

    def rank(
        self,
        candidates: Iterable[Mapping[str, Any]],
        top_k: Optional[int] = DEFAULT_TOP_K,
    ) -> RankingResult:
        """
        Rank a collection of candidates.

        Args:
            candidates:
                Candidate scoring records.

            top_k:
                Maximum number of candidates to return.
                None returns all candidates.
        """

        candidate_list = list(candidates)

        if not candidate_list:
            return RankingResult(
                total_candidates=0,
                ranked_candidates=[],
                weights=self.normalized_weights,
                top_k=top_k,
                warnings=[
                    "No candidates supplied."
                ],
            )

        ranked: List[CandidateRanking] = []

        skipped: List[Any] = []

        warnings: List[str] = []

        for candidate in candidate_list:

            candidate_id = candidate.get(
                "candidate_id"
            )

            try:

                ranking = self.rank_one(
                    candidate
                )

                ranked.append(
                    ranking
                )

            except ValueError as exc:

                skipped.append(
                    candidate_id
                )

                warnings.append(
                    f"Candidate {candidate_id!r} "
                    f"was skipped: {exc}"
                )

        # Highest score first.
        ranked.sort(
            key=lambda item: (
                -item.score,
                str(item.candidate_id),
            )
        )

        # Assign rank.
        self._assign_ranks(
            ranked
        )

        # Top K.
        if top_k is not None:

            if top_k < 1:
                raise ValueError(
                    "top_k must be >= 1 or None."
                )

            ranked = ranked[
                :top_k
            ]

        return RankingResult(
            total_candidates=len(
                candidate_list
            ),
            ranked_candidates=ranked,
            weights=self.normalized_weights,
            top_k=top_k,
            skipped_candidates=skipped,
            warnings=warnings,
        )

    # ========================================================
    # SINGLE CANDIDATE
    # ========================================================

    def rank_one(
        self,
        candidate: Mapping[str, Any],
    ) -> CandidateRanking:
        """Rank one candidate."""

        candidate_id = candidate.get(
            "candidate_id"
        )

        if candidate_id is None:
            raise ValueError(
                "candidate_id is required."
            )

        breakdown: Dict[str, float] = {}

        for feature in self.normalized_weights:

            value = candidate.get(
                feature,
                0.0,
            )

            breakdown[feature] = (
                self._validate_score(
                    value,
                    feature,
                )
            )

        weighted_breakdown = {
            feature: round(
                breakdown[feature]
                * self.normalized_weights[feature],
                4,
            )
            for feature in breakdown
        }

        final_score = sum(
            weighted_breakdown.values()
        )

        final_score = round(
            max(
                MIN_SCORE,
                min(
                    MAX_SCORE,
                    final_score,
                ),
            ),
            2,
        )

        strengths = self._get_strengths(
            breakdown
        )

        weaknesses = self._get_weaknesses(
            breakdown
        )

        explanation = self._build_explanation(
            breakdown,
            strengths,
            weaknesses,
        )

        metadata = self._get_safe_metadata(
            candidate
        )

        return CandidateRanking(
            candidate_id=candidate_id,
            rank=0,
            score=final_score,
            breakdown=breakdown,
            weighted_breakdown=weighted_breakdown,
            strengths=strengths,
            weaknesses=weaknesses,
            explanation=explanation,
            metadata=metadata,
        )

    # ========================================================
    # WEIGHT MANAGEMENT
    # ========================================================

    def _build_weights(
        self,
        weights: Optional[
            Mapping[str, float]
        ],
    ) -> RankingWeights:

        values = DEFAULT_WEIGHTS.copy()

        if weights:

            for feature, weight in weights.items():

                if feature not in values:
                    raise ValueError(
                        f"Unknown ranking feature: "
                        f"{feature}"
                    )

                values[feature] = float(
                    weight
                )

        return RankingWeights(
            skill_score=values[
                "skill_score"
            ],
            experience_score=values[
                "experience_score"
            ],
            education_score=values[
                "education_score"
            ],
            ats_score=values[
                "ats_score"
            ],
            semantic_score=values[
                "semantic_score"
            ],
            keyword_score=values[
                "keyword_score"
            ],
        )

    @staticmethod
    def _normalize_weights(
        weights: Mapping[str, float],
    ) -> Dict[str, float]:

        total = sum(
            weights.values()
        )

        if total <= 0:
            raise ValueError(
                "Ranking weights must have "
                "a positive total."
            )

        return {
            feature: weight / total
            for feature, weight
            in weights.items()
        }

    # ========================================================
    # SCORE VALIDATION
    # ========================================================

    @staticmethod
    def _validate_score(
        value: Any,
        field_name: str,
    ) -> float:

        # Missing scores are treated as zero.
        if value is None:
            return 0.0

        try:
            score = float(
                value
            )

        except (
            TypeError,
            ValueError,
        ) as exc:

            raise ValueError(
                f"Invalid score for "
                f"'{field_name}': {value!r}"
            ) from exc

        if not (
            MIN_SCORE
            <= score
            <= MAX_SCORE
        ):
            raise ValueError(
                f"'{field_name}' must be "
                f"between {MIN_SCORE} "
                f"and {MAX_SCORE}."
            )

        return score

    # ========================================================
    # STRENGTHS
    # ========================================================

    @staticmethod
    def _get_strengths(
        breakdown: Mapping[str, float],
    ) -> List[str]:

        labels = {
            "skill_score": "Strong skill match",
            "experience_score": "Strong experience",
            "education_score": "Strong education match",
            "ats_score": "Strong ATS compatibility",
            "semantic_score": "Strong semantic match",
            "keyword_score": "Strong keyword match",
        }

        strengths = []

        for feature, score in breakdown.items():

            if score >= STRONG_SCORE:

                strengths.append(
                    labels.get(
                        feature,
                        feature,
                    )
                )

        return strengths

    # ========================================================
    # WEAKNESSES
    # ========================================================

    @staticmethod
    def _get_weaknesses(
        breakdown: Mapping[str, float],
    ) -> List[str]:

        labels = {
            "skill_score": "Skill gap",
            "experience_score": "Experience gap",
            "education_score": "Education mismatch",
            "ats_score": "ATS compatibility issue",
            "semantic_score": "Low semantic similarity",
            "keyword_score": "Missing keywords",
        }

        weaknesses = []

        for feature, score in breakdown.items():

            if score < WEAK_SCORE:

                weaknesses.append(
                    labels.get(
                        feature,
                        feature,
                    )
                )

        return weaknesses

    # ========================================================
    # EXPLANATION
    # ========================================================

    @staticmethod
    def _build_explanation(
        breakdown: Mapping[str, float],
        strengths: List[str],
        weaknesses: List[str],
    ) -> str:

        labels = {
            "skill_score": "skills",
            "experience_score": "experience",
            "education_score": "education",
            "ats_score": "ATS compatibility",
            "semantic_score": "semantic similarity",
            "keyword_score": "keyword matching",
        }

        ordered = sorted(
            breakdown.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        if not ordered:

            return (
                "No ranking signals were available."
            )

        strongest = ordered[:2]

        explanation = (
            "The candidate ranking is primarily "
            f"supported by "
            f"{labels.get(strongest[0][0], strongest[0][0])} "
            f"({strongest[0][1]:.1f})"
        )

        if len(strongest) > 1:

            explanation += (
                f" and "
                f"{labels.get(strongest[1][0], strongest[1][0])} "
                f"({strongest[1][1]:.1f})"
            )

        explanation += "."

        if weaknesses:

            explanation += (
                " Review areas: "
                + ", ".join(
                    weaknesses
                )
                + "."
            )

        return explanation

    # ========================================================
    # SAFE METADATA
    # ========================================================

    @staticmethod
    def _get_safe_metadata(
        candidate: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """
        Return safe candidate metadata.

        Protected attributes are intentionally excluded.
        """

        allowed = {
            "name",
            "job_id",
            "resume_id",
            "current_title",
            "years_of_experience",
            "skills",
        }

        metadata = {}

        for field_name in allowed:

            if field_name not in candidate:
                continue

            if (
                field_name.lower()
                in PROTECTED_FIELDS
            ):
                continue

            metadata[field_name] = (
                candidate[field_name]
            )

        return metadata

    # ========================================================
    # RANK ASSIGNMENT
    # ========================================================

    @staticmethod
    def _assign_ranks(
        candidates: List[CandidateRanking],
    ) -> None:
        """Assign ranks with ties receiving the same rank."""

        previous_score: Optional[
            float
        ] = None

        current_rank = 0

        for index, candidate in enumerate(
            candidates,
            start=1,
        ):

            if (
                previous_score is None
                or candidate.score
                < previous_score
            ):
                current_rank = index

            candidate.rank = current_rank

            previous_score = candidate.score

    # ========================================================
    # TOP CANDIDATES
    # ========================================================

    def top_candidates(
        self,
        candidates: Iterable[Mapping[str, Any]],
        limit: int = 10,
    ) -> List[CandidateRanking]:
        """Return the highest-ranked candidates."""

        result = self.rank(
            candidates,
            top_k=limit,
        )

        return result.ranked_candidates

    # ========================================================
    # JOB RANKING
    # ========================================================

    def rank_against_job(
        self,
        candidates: Iterable[Mapping[str, Any]],
        job: Mapping[str, Any],
        top_k: Optional[int] = DEFAULT_TOP_K,
    ) -> RankingResult:
        """
        Rank candidates for a specific job.

        The actual resume/JD scoring should happen before this
        method. This method combines those scores.
        """

        result = self.rank(
            candidates,
            top_k=top_k,
        )

        job_id = job.get(
            "job_id"
        )

        for candidate in result.ranked_candidates:

            if job_id is not None:

                candidate.metadata[
                    "job_id"
                ] = job_id

        return result

    # ========================================================
    # STATISTICS
    # ========================================================

    @staticmethod
    def statistics(
        rankings: Iterable[CandidateRanking],
    ) -> Dict[str, float]:

        scores = [
            ranking.score
            for ranking in rankings
        ]

        if not scores:

            return {
                "count": 0,
                "average": 0.0,
                "minimum": 0.0,
                "maximum": 0.0,
            }

        return {
            "count": len(scores),
            "average": round(
                sum(scores)
                / len(scores),
                2,
            ),
            "minimum": round(
                min(scores),
                2,
            ),
            "maximum": round(
                max(scores),
                2,
            ),
        }

    # ========================================================
    # FAIRNESS AUDIT EXPORT
    # ========================================================

    def export_for_fairness_audit(
        self,
        candidates: Iterable[Mapping[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Export ranking outcomes for separate fairness analysis.

        Protected/group attributes may be retained here ONLY for
        auditing purposes. They are never passed into the scoring
        calculation.
        """

        result = []

        for candidate in candidates:

            ranking = self.rank_one(
                candidate
            )

            record = {
                "candidate_id": (
                    candidate.get(
                        "candidate_id"
                    )
                ),
                "score": ranking.score,
            }

            # Optional audit-only grouping.
            if "group" in candidate:

                record["group"] = (
                    candidate["group"]
                )

            if "qualified" in candidate:

                record["qualified"] = (
                    candidate["qualified"]
                )

            result.append(
                record
            )

        return result


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================


def rank_candidates(
    candidates: Iterable[Mapping[str, Any]],
    weights: Optional[
        Mapping[str, float]
    ] = None,
    top_k: Optional[int] = DEFAULT_TOP_K,
) -> Dict[str, Any]:
    """
    Simple functional API.

    Example:

        result = rank_candidates(
            candidates,
            top_k=10,
        )
    """

    ranker = CandidateRanker(
        weights=weights
    )

    result = ranker.rank(
        candidates,
        top_k=top_k,
    )

    return result.to_dict()


# ============================================================
# DEFAULT WEIGHTS
# ============================================================


def get_default_weights() -> Dict[str, float]:
    """Return a copy of the default ranking weights."""

    return DEFAULT_WEIGHTS.copy()


# ============================================================
# EXAMPLE
# ============================================================


if __name__ == "__main__":

    candidates = [
        {
            "candidate_id": 101,
            "name": "Candidate A",
            "skill_score": 92,
            "experience_score": 88,
            "education_score": 80,
            "ats_score": 91,
            "semantic_score": 90,
            "keyword_score": 85,
        },
        {
            "candidate_id": 102,
            "name": "Candidate B",
            "skill_score": 86,
            "experience_score": 92,
            "education_score": 78,
            "ats_score": 84,
            "semantic_score": 87,
            "keyword_score": 90,
        },
        {
            "candidate_id": 103,
            "name": "Candidate C",
            "skill_score": 70,
            "experience_score": 68,
            "education_score": 82,
            "ats_score": 74,
            "semantic_score": 72,
            "keyword_score": 65,
        },
    ]

    ranker = CandidateRanker()

    result = ranker.rank(
        candidates,
        top_k=10,
    )

    print("\nCandidate Ranking")
    print("=" * 60)

    for candidate in result.ranked_candidates:

        print(
            f"Rank: {candidate.rank} | "
            f"ID: {candidate.candidate_id} | "
            f"Score: {candidate.score}"
        )

        print(
            f"Strengths: "
            f"{', '.join(candidate.strengths) or 'None'}"
        )

        print(
            f"Weaknesses: "
            f"{', '.join(candidate.weaknesses) or 'None'}"
        )

        print(
            f"Explanation: "
            f"{candidate.explanation}"
        )

        print("-" * 60)

    print(
        "\nStatistics:",
        CandidateRanker.statistics(
            result.ranked_candidates
        ),
    )