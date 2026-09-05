
"""
Ranking Features
================

File:
    ai/ranking/ranking_features.py

Purpose:
    - Extract ranking features from candidate/job data
    - Normalize scoring signals
    - Calculate feature completeness
    - Build ranking-ready feature dictionaries
    - Keep protected attributes out of ranking features
    - Provide feature metadata for explainability

This module does NOT perform final candidate ranking.
That responsibility belongs to candidate_ranker.py.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


# ============================================================
# CONSTANTS
# ============================================================

MIN_SCORE = 0.0
MAX_SCORE = 100.0

DEFAULT_FEATURES = (
    "skill_score",
    "experience_score",
    "education_score",
    "ats_score",
    "semantic_score",
    "keyword_score",
)

# Protected attributes are excluded from ranking features.
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

# Fields that are useful for audit/explanation but should not
# directly become numerical ranking features.
NON_RANKING_FIELDS = {
    "candidate_id",
    "name",
    "email",
    "phone",
    "address",
    "resume_id",
    "job_id",
    "created_at",
    "updated_at",
}


# ============================================================
# DATA CLASSES
# ============================================================


@dataclass
class FeatureDefinition:
    """Definition of a ranking feature."""

    name: str
    description: str
    min_value: float = MIN_SCORE
    max_value: float = MAX_SCORE
    required: bool = False
    weight: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "required": self.required,
            "weight": self.weight,
        }


@dataclass
class FeatureSet:
    """Collection of ranking features for one candidate."""

    candidate_id: Any

    features: Dict[str, float]

    missing_features: List[str] = field(
        default_factory=list
    )

    completeness: float = 100.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "features": self.features,
            "missing_features": self.missing_features,
            "completeness": self.completeness,
            "metadata": self.metadata,
        }


# ============================================================
# FEATURE DEFINITIONS
# ============================================================


FEATURE_DEFINITIONS: Dict[str, FeatureDefinition] = {
    "skill_score": FeatureDefinition(
        name="skill_score",
        description=(
            "Candidate skill match against job requirements."
        ),
        weight=0.30,
    ),

    "experience_score": FeatureDefinition(
        name="experience_score",
        description=(
            "Candidate experience relevance and seniority match."
        ),
        weight=0.20,
    ),

    "education_score": FeatureDefinition(
        name="education_score",
        description=(
            "Education qualification match against job requirements."
        ),
        weight=0.10,
    ),

    "ats_score": FeatureDefinition(
        name="ats_score",
        description=(
            "Resume compatibility with ATS parsing and formatting."
        ),
        weight=0.15,
    ),

    "semantic_score": FeatureDefinition(
        name="semantic_score",
        description=(
            "Semantic similarity between resume and job description."
        ),
        weight=0.15,
    ),

    "keyword_score": FeatureDefinition(
        name="keyword_score",
        description=(
            "Keyword overlap between candidate resume and job requirements."
        ),
        weight=0.10,
    ),
}


# ============================================================
# RANKING FEATURE EXTRACTOR
# ============================================================


class RankingFeatureExtractor:
    """
    Extracts and prepares ranking features.

    Example:

        extractor = RankingFeatureExtractor()

        feature_set = extractor.extract(candidate)

        print(feature_set.features)
    """

    def __init__(
        self,
        feature_names: Optional[
            Sequence[str]
        ] = None,
    ) -> None:

        self.feature_names = tuple(
            feature_names
            if feature_names is not None
            else DEFAULT_FEATURES
        )

        self._validate_feature_names()

    # ========================================================
    # PUBLIC API
    # ========================================================

    def extract(
        self,
        candidate: Mapping[str, Any],
    ) -> FeatureSet:
        """
        Extract ranking features from a candidate.

        Missing feature values are represented as 0.0.
        """

        candidate_id = candidate.get(
            "candidate_id"
        )

        features: Dict[str, float] = {}

        missing_features: List[str] = []

        for feature_name in self.feature_names:

            raw_value = candidate.get(
                feature_name
            )

            if raw_value is None:

                missing_features.append(
                    feature_name
                )

                features[feature_name] = 0.0

                continue

            features[feature_name] = (
                self.normalize_score(
                    raw_value
                )
            )

        completeness = (
            self.calculate_completeness(
                features=features,
                missing_features=missing_features,
            )
        )

        metadata = self.extract_safe_metadata(
            candidate
        )

        return FeatureSet(
            candidate_id=candidate_id,
            features=features,
            missing_features=missing_features,
            completeness=completeness,
            metadata=metadata,
        )

    # ========================================================
    # BATCH EXTRACTION
    # ========================================================

    def extract_many(
        self,
        candidates: Iterable[
            Mapping[str, Any]
        ],
    ) -> List[FeatureSet]:
        """Extract features for multiple candidates."""

        return [
            self.extract(candidate)
            for candidate in candidates
        ]

    # ========================================================
    # NORMALIZATION
    # ========================================================

    @staticmethod
    def normalize_score(
        value: Any,
        source_min: float = MIN_SCORE,
        source_max: float = MAX_SCORE,
    ) -> float:
        """
        Normalize a value to a 0-100 scale.

        Example:

            0.85 -> 85
        """

        if value is None:
            return 0.0

        try:
            numeric_value = float(value)

        except (
            TypeError,
            ValueError,
        ) as exc:

            raise ValueError(
                f"Invalid feature value: {value!r}"
            ) from exc

        if not (
            math.isfinite(numeric_value)
        ):
            raise ValueError(
                f"Feature value must be finite: "
                f"{numeric_value!r}"
            )

        if source_max <= source_min:
            raise ValueError(
                "source_max must be greater than "
                "source_min."
            )

        normalized = (
            (
                numeric_value
                - source_min
            )
            / (
                source_max
                - source_min
            )
        ) * MAX_SCORE

        return round(
            max(
                MIN_SCORE,
                min(
                    MAX_SCORE,
                    normalized,
                ),
            ),
            4,
        )

    # ========================================================
    # PERCENTAGE NORMALIZATION
    # ========================================================

    @staticmethod
    def percentage_to_score(
        percentage: Any,
    ) -> float:
        """
        Convert a percentage to a 0-100 score.

        Examples:
            85 -> 85
            0.85 -> 85
        """

        if percentage is None:
            return 0.0

        try:
            value = float(
                percentage
            )

        except (
            TypeError,
            ValueError,
        ) as exc:

            raise ValueError(
                f"Invalid percentage: {percentage!r}"
            ) from exc

        if 0 <= value <= 1:
            value *= 100

        return round(
            max(
                MIN_SCORE,
                min(
                    MAX_SCORE,
                    value,
                ),
            ),
            4,
        )

    # ========================================================
    # COMPLETENESS
    # ========================================================

    def calculate_completeness(
        self,
        features: Mapping[str, Any],
        missing_features: Optional[
            Sequence[str]
        ] = None,
    ) -> float:
        """
        Calculate percentage of available ranking features.

        A candidate with all six features available gets 100%.
        """

        total = len(
            self.feature_names
        )

        if total == 0:
            return 100.0

        if missing_features is not None:

            missing = len(
                missing_features
            )

        else:

            missing = sum(
                1
                for feature in self.feature_names
                if features.get(feature) is None
            )

        completeness = (
            (total - missing)
            / total
        ) * 100

        return round(
            completeness,
            2,
        )

    # ========================================================
    # WEIGHTED FEATURES
    # ========================================================

    def weighted_features(
        self,
        features: Mapping[str, Any],
        weights: Optional[
            Mapping[str, float]
        ] = None,
    ) -> Dict[str, float]:
        """
        Calculate weighted contribution of each feature.

        The returned values are still on the 0-100 contribution
        scale.
        """

        if weights is None:

            weights = {
                name: definition.weight
                for name, definition
                in FEATURE_DEFINITIONS.items()
            }

        self._validate_weights(
            weights
        )

        total_weight = sum(
            weights.get(
                feature,
                0.0,
            )
            for feature in self.feature_names
        )

        if total_weight <= 0:
            raise ValueError(
                "Total feature weight must be greater than zero."
            )

        normalized_weights = {
            feature: (
                weights.get(
                    feature,
                    0.0,
                )
                / total_weight
            )
            for feature in self.feature_names
        }

        result = {}

        for feature in self.feature_names:

            value = self._safe_score(
                features.get(
                    feature,
                    0.0,
                )
            )

            result[feature] = round(
                value
                * normalized_weights[feature],
                4,
            )

        return result

    # ========================================================
    # FEATURE VECTOR
    # ========================================================

    def to_vector(
        self,
        features: Mapping[str, Any],
    ) -> List[float]:
        """
        Convert feature dictionary to ordered numerical vector.

        The order is the same as self.feature_names.
        """

        return [
            self._safe_score(
                features.get(
                    feature,
                    0.0,
                )
            )
            for feature in self.feature_names
        ]

    # ========================================================
    # FEATURE DICTIONARY
    # ========================================================

    def from_vector(
        self,
        vector: Sequence[Any],
    ) -> Dict[str, float]:
        """Convert an ordered feature vector to a dictionary."""

        if len(vector) != len(
            self.feature_names
        ):
            raise ValueError(
                "Vector length does not match "
                "the number of configured features."
            )

        return {
            feature: self._safe_score(
                vector[index]
            )
            for index, feature
            in enumerate(
                self.feature_names
            )
        }

    # ========================================================
    # FEATURE QUALITY
    # ========================================================

    def feature_quality(
        self,
        features: Mapping[str, Any],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Return quality information for every feature.
        """

        result = {}

        for feature in self.feature_names:

            value = features.get(
                feature
            )

            if value is None:

                result[feature] = {
                    "value": 0.0,
                    "available": False,
                    "quality": "missing",
                }

                continue

            try:

                score = self._safe_score(
                    value
                )

            except ValueError:

                result[feature] = {
                    "value": value,
                    "available": False,
                    "quality": "invalid",
                }

                continue

            if score >= 80:

                quality = "strong"

            elif score >= 50:

                quality = "moderate"

            else:

                quality = "weak"

            result[feature] = {
                "value": score,
                "available": True,
                "quality": quality,
            }

        return result

    # ========================================================
    # FEATURE IMPORTANCE
    # ========================================================

    def feature_importance(
        self,
        weights: Optional[
            Mapping[str, float]
        ] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return features sorted by ranking importance.
        """

        if weights is None:

            weights = {
                name: definition.weight
                for name, definition
                in FEATURE_DEFINITIONS.items()
            }

        self._validate_weights(
            weights
        )

        items = []

        for feature in self.feature_names:

            definition = (
                FEATURE_DEFINITIONS.get(
                    feature
                )
            )

            items.append(
                {
                    "feature": feature,
                    "weight": weights.get(
                        feature,
                        0.0,
                    ),
                    "description": (
                        definition.description
                        if definition
                        else feature
                    ),
                }
            )

        items.sort(
            key=lambda item: item["weight"],
            reverse=True,
        )

        return items

    # ========================================================
    # STRENGTH DETECTION
    # ========================================================

    def detect_strengths(
        self,
        features: Mapping[str, Any],
        threshold: float = 80.0,
    ) -> List[str]:
        """Return features above a strength threshold."""

        strengths = []

        for feature in self.feature_names:

            score = self._safe_score(
                features.get(
                    feature,
                    0.0,
                )
            )

            if score >= threshold:

                strengths.append(
                    feature
                )

        return strengths

    # ========================================================
    # WEAKNESS DETECTION
    # ========================================================

    def detect_weaknesses(
        self,
        features: Mapping[str, Any],
        threshold: float = 50.0,
    ) -> List[str]:
        """Return features below a weakness threshold."""

        weaknesses = []

        for feature in self.feature_names:

            score = self._safe_score(
                features.get(
                    feature,
                    0.0,
                )
            )

            if score < threshold:

                weaknesses.append(
                    feature
                )

        return weaknesses

    # ========================================================
    # TOP FEATURES
    # ========================================================

    def top_features(
        self,
        features: Mapping[str, Any],
        limit: int = 3,
    ) -> List[Dict[str, Any]]:
        """Return highest scoring features."""

        if limit < 1:
            raise ValueError(
                "limit must be >= 1."
            )

        result = []

        for feature in self.feature_names:

            score = self._safe_score(
                features.get(
                    feature,
                    0.0,
                )
            )

            result.append(
                {
                    "feature": feature,
                    "score": score,
                }
            )

        result.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return result[
            :limit
        ]

    # ========================================================
    # SAFE METADATA
    # ========================================================

    @staticmethod
    def extract_safe_metadata(
        candidate: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract non-sensitive metadata.

        This metadata is not used to calculate the ranking score.
        """

        allowed = {
            "candidate_id",
            "name",
            "job_id",
            "resume_id",
            "current_title",
            "years_of_experience",
        }

        metadata = {}

        for key in allowed:

            if key not in candidate:
                continue

            if (
                key.lower()
                in PROTECTED_ATTRIBUTES
            ):
                continue

            metadata[key] = candidate[
                key
            ]

        return metadata

    # ========================================================
    # REMOVE PROTECTED ATTRIBUTES
    # ========================================================

    @staticmethod
    def remove_protected_attributes(
        data: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """
        Remove protected attributes from a candidate dictionary.

        Useful before sending candidate data into the ranking
        pipeline.
        """

        cleaned = {}

        for key, value in data.items():

            normalized_key = (
                str(key)
                .strip()
                .lower()
            )

            if normalized_key in (
                PROTECTED_ATTRIBUTES
            ):
                continue

            cleaned[key] = value

        return cleaned

    # ========================================================
    # RANKING READINESS
    # ========================================================

    def ranking_readiness(
        self,
        candidate: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """
        Check whether candidate data is ready for ranking.
        """

        feature_set = self.extract(
            candidate
        )

        errors = []

        for feature in feature_set.missing_features:

            errors.append(
                f"Missing feature: {feature}"
            )

        protected_present = []

        for key in candidate:

            normalized_key = (
                str(key)
                .strip()
                .lower()
            )

            if normalized_key in (
                PROTECTED_ATTRIBUTES
            ):

                protected_present.append(
                    key
                )

        return {
            "candidate_id": feature_set.candidate_id,
            "ready": not bool(
                errors
            ),
            "completeness": (
                feature_set.completeness
            ),
            "missing_features": (
                feature_set.missing_features
            ),
            "protected_attributes_detected": (
                protected_present
            ),
            "errors": errors,
        }

    # ========================================================
    # DEFINITIONS
    # ========================================================

    @staticmethod
    def get_feature_definitions() -> Dict[
        str,
        Dict[str, Any],
    ]:
        """Return metadata for all standard features."""

        return {
            name: definition.to_dict()
            for name, definition
            in FEATURE_DEFINITIONS.items()
        }

    # ========================================================
    # INTERNAL HELPERS
    # ========================================================

    def _validate_feature_names(
        self,
    ) -> None:

        unknown = [
            feature
            for feature in self.feature_names
            if feature
            not in FEATURE_DEFINITIONS
        ]

        if unknown:

            raise ValueError(
                "Unknown ranking features: "
                + ", ".join(unknown)
            )

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
        ) as exc:

            raise ValueError(
                f"Invalid feature score: {value!r}"
            ) from exc

        if not math.isfinite(
            score
        ):
            raise ValueError(
                "Feature score must be finite."
            )

        return round(
            max(
                MIN_SCORE,
                min(
                    MAX_SCORE,
                    score,
                ),
            ),
            4,
        )

    @staticmethod
    def _validate_weights(
        weights: Mapping[str, float],
    ) -> None:

        for feature, weight in weights.items():

            try:
                numeric_weight = float(
                    weight
                )

            except (
                TypeError,
                ValueError,
            ) as exc:

                raise ValueError(
                    f"Invalid weight for "
                    f"{feature!r}: {weight!r}"
                ) from exc

            if numeric_weight < 0:

                raise ValueError(
                    f"Weight for {feature!r} "
                    f"cannot be negative."
                )


# ============================================================
# FEATURE ENGINEERING HELPERS
# ============================================================


def calculate_experience_score(
    candidate_years: float,
    required_years: float,
    preferred_years: Optional[float] = None,
) -> float:
    """
    Calculate experience compatibility.

    Logic:
        - Meets required experience -> at least 70
        - Meets preferred experience -> 100
        - Below required -> proportional score
    """

    candidate_years = max(
        0.0,
        float(candidate_years),
    )

    required_years = max(
        0.0,
        float(required_years),
    )

    if preferred_years is None:

        preferred_years = required_years

    preferred_years = max(
        required_years,
        float(preferred_years),
    )

    if preferred_years == 0:

        return 100.0

    if candidate_years >= preferred_years:

        return 100.0

    if candidate_years >= required_years:

        span = (
            preferred_years
            - required_years
        )

        if span == 0:
            return 100.0

        progress = (
            candidate_years
            - required_years
        ) / span

        return round(
            70
            + (
                progress
                * 30
            ),
            2,
        )

    if required_years == 0:

        return 100.0

    score = (
        candidate_years
        / required_years
    ) * 70

    return round(
        max(
            0.0,
            min(
                70.0,
                score,
            ),
        ),
        2,
    )


def calculate_keyword_score(
    matched_keywords: int,
    required_keywords: int,
) -> float:
    """Calculate keyword matching score."""

    matched_keywords = max(
        0,
        int(matched_keywords),
    )

    required_keywords = max(
        0,
        int(required_keywords),
    )

    if required_keywords == 0:

        return 100.0

    return round(
        min(
            100.0,
            (
                matched_keywords
                / required_keywords
            )
            * 100,
        ),
        2,
    )


def calculate_skill_score(
    matched_skills: int,
    required_skills: int,
    preferred_skills: int = 0,
    matched_preferred_skills: int = 0,
) -> float:
    """
    Calculate skill matching score.

    Required skills have higher importance than preferred skills.
    """

    required_skills = max(
        0,
        int(required_skills),
    )

    matched_skills = max(
        0,
        int(matched_skills),
    )

    preferred_skills = max(
        0,
        int(preferred_skills),
    )

    matched_preferred_skills = max(
        0,
        int(matched_preferred_skills),
    )

    required_ratio = (
        matched_skills
        / required_skills
        if required_skills
        else 1.0
    )

    preferred_ratio = (
        matched_preferred_skills
        / preferred_skills
        if preferred_skills
        else 1.0
    )

    score = (
        required_ratio * 80
        + preferred_ratio * 20
    )

    return round(
        max(
            0.0,
            min(
                100.0,
                score,
            ),
        ),
        2,
    )


def calculate_semantic_score(
    similarity: float,
) -> float:
    """
    Convert semantic similarity into a 0-100 score.

    Supports:
        0.0 - 1.0
        0   - 100
    """

    return RankingFeatureExtractor.percentage_to_score(
        similarity
    )


def calculate_education_score(
    education_match: bool,
    degree_match: bool = True,
    field_match: bool = True,
) -> float:
    """Calculate education compatibility."""

    score = 0.0

    if education_match:
        score += 50

    if degree_match:
        score += 25

    if field_match:
        score += 25

    return round(
        min(
            100.0,
            score,
        ),
        2,
    )


# ============================================================
# DEFAULT FEATURE FACTORY
# ============================================================


def build_ranking_features(
    candidate: Mapping[str, Any],
) -> Dict[str, float]:
    """
    Build a standard ranking feature dictionary.

    This is the easiest function to use from services.
    """

    extractor = RankingFeatureExtractor()

    feature_set = extractor.extract(
        candidate
    )

    return feature_set.features


# ============================================================
# FEATURE VECTOR FACTORY
# ============================================================


def build_feature_vector(
    candidate: Mapping[str, Any],
) -> List[float]:
    """Build an ordered numerical ranking vector."""

    extractor = RankingFeatureExtractor()

    features = extractor.extract(
        candidate
    )

    return extractor.to_vector(
        features.features
    )


# ============================================================
# EXAMPLE
# ============================================================


if __name__ == "__main__":

    candidate = {
        "candidate_id": 101,
        "name": "Candidate A",

        "skill_score": 92,
        "experience_score": 88,
        "education_score": 80,
        "ats_score": 91,
        "semantic_score": 90,
        "keyword_score": 85,

        # These are deliberately excluded from
        # ranking calculations.
        "age": 29,
        "gender": "female",
        "religion": "example",
    }

    extractor = RankingFeatureExtractor()

    # --------------------------------------------------------
    # Extract features
    # --------------------------------------------------------

    feature_set = extractor.extract(
        candidate
    )

    print("FEATURE SET")
    print("=" * 60)

    print(
        feature_set.to_dict()
    )

    # --------------------------------------------------------
    # Feature vector
    # --------------------------------------------------------

    vector = extractor.to_vector(
        feature_set.features
    )

    print("\nFEATURE VECTOR")
    print("=" * 60)

    print(vector)

    # --------------------------------------------------------
    # Feature quality
    # --------------------------------------------------------

    quality = extractor.feature_quality(
        feature_set.features
    )

    print("\nFEATURE QUALITY")
    print("=" * 60)

    for feature, details in quality.items():

        print(
            f"{feature}: "
            f"{details}"
        )

    # --------------------------------------------------------
    # Strengths
    # --------------------------------------------------------

    strengths = extractor.detect_strengths(
        feature_set.features
    )

    print("\nSTRENGTHS")
    print("=" * 60)

    print(strengths)

    # --------------------------------------------------------
    # Weaknesses
    # --------------------------------------------------------

    weaknesses = extractor.detect_weaknesses(
        feature_set.features
    )

    print("\nWEAKNESSES")
    print("=" * 60)

    print(weaknesses)

    # --------------------------------------------------------
    # Feature importance
    # --------------------------------------------------------

    importance = (
        extractor.feature_importance()
    )

    print("\nFEATURE IMPORTANCE")
    print("=" * 60)

    for item in importance:

        print(
            f"{item['feature']}: "
            f"{item['weight']:.2%}"
        )

    # --------------------------------------------------------
    # Ranking readiness
    # --------------------------------------------------------

    readiness = (
        extractor.ranking_readiness(
            candidate
        )
    )

    print("\nRANKING READINESS")
    print("=" * 60)

    print(readiness)