# Project scaffold file
"""
Interview Question Difficulty Management

Location:
    interview_engine/question_generation/difficulty.py

Purpose:
    Provides difficulty levels, scoring rules, normalization utilities,
    and adaptive difficulty selection for interview questions.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class DifficultyLevel(str, Enum):
    """Supported interview difficulty levels."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass(frozen=True)
class DifficultyConfig:
    """Configuration for a difficulty level."""

    level: DifficultyLevel
    score_min: float
    score_max: float
    complexity: float
    follow_up_depth: int
    expected_reasoning: str
    description: str


DIFFICULTY_CONFIGS: dict[DifficultyLevel, DifficultyConfig] = {
    DifficultyLevel.EASY: DifficultyConfig(
        level=DifficultyLevel.EASY,
        score_min=0.0,
        score_max=45.0,
        complexity=0.30,
        follow_up_depth=1,
        expected_reasoning="basic",
        description="Fundamental questions requiring straightforward reasoning.",
    ),
    DifficultyLevel.MEDIUM: DifficultyConfig(
        level=DifficultyLevel.MEDIUM,
        score_min=45.0,
        score_max=75.0,
        complexity=0.60,
        follow_up_depth=2,
        expected_reasoning="intermediate",
        description="Questions requiring practical experience and structured reasoning.",
    ),
    DifficultyLevel.HARD: DifficultyConfig(
        level=DifficultyLevel.HARD,
        score_min=75.0,
        score_max=100.0,
        complexity=0.90,
        follow_up_depth=3,
        expected_reasoning="advanced",
        description="Complex questions requiring deep reasoning, trade-offs, and strong experience.",
    ),
}


DIFFICULTY_ORDER: tuple[DifficultyLevel, ...] = (
    DifficultyLevel.EASY,
    DifficultyLevel.MEDIUM,
    DifficultyLevel.HARD,
)


class DifficultyManager:
    """
    Manages interview question difficulty.

    The manager can:
        - normalize difficulty values
        - compare difficulty levels
        - increase/decrease difficulty
        - select difficulty from performance
        - calculate adaptive difficulty
        - generate difficulty metadata
    """

    def __init__(
        self,
        configs: dict[DifficultyLevel, DifficultyConfig] | None = None,
    ) -> None:
        self.configs = configs or DIFFICULTY_CONFIGS

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    @staticmethod
    def normalize(
        difficulty: str | DifficultyLevel | None,
        default: DifficultyLevel = DifficultyLevel.MEDIUM,
    ) -> DifficultyLevel:
        """Normalize a difficulty value."""

        if isinstance(difficulty, DifficultyLevel):
            return difficulty

        if difficulty is None:
            return default

        value = str(difficulty).strip().lower()

        aliases = {
            "beginner": DifficultyLevel.EASY,
            "basic": DifficultyLevel.EASY,
            "low": DifficultyLevel.EASY,
            "easy": DifficultyLevel.EASY,
            "intermediate": DifficultyLevel.MEDIUM,
            "moderate": DifficultyLevel.MEDIUM,
            "medium": DifficultyLevel.MEDIUM,
            "mid": DifficultyLevel.MEDIUM,
            "advanced": DifficultyLevel.HARD,
            "expert": DifficultyLevel.HARD,
            "high": DifficultyLevel.HARD,
            "hard": DifficultyLevel.HARD,
        }

        return aliases.get(value, default)

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def get_config(
        self,
        difficulty: str | DifficultyLevel,
    ) -> DifficultyConfig:
        """Return configuration for a difficulty."""

        level = self.normalize(difficulty)
        return self.configs[level]

    def get_description(
        self,
        difficulty: str | DifficultyLevel,
    ) -> str:
        """Return a human-readable difficulty description."""

        return self.get_config(difficulty).description

    def get_complexity(
        self,
        difficulty: str | DifficultyLevel,
    ) -> float:
        """Return normalized complexity between 0 and 1."""

        return self.get_config(difficulty).complexity

    # ------------------------------------------------------------------
    # Level Operations
    # ------------------------------------------------------------------

    @staticmethod
    def rank(
        difficulty: str | DifficultyLevel,
    ) -> int:
        """Return numeric difficulty rank."""

        level = DifficultyManager.normalize(difficulty)

        return DIFFICULTY_ORDER.index(level)

    @staticmethod
    def compare(
        first: str | DifficultyLevel,
        second: str | DifficultyLevel,
    ) -> int:
        """
        Compare two difficulty levels.

        Returns:
            -1 if first < second
             0 if equal
             1 if first > second
        """

        first_rank = DifficultyManager.rank(first)
        second_rank = DifficultyManager.rank(second)

        if first_rank < second_rank:
            return -1

        if first_rank > second_rank:
            return 1

        return 0

    @staticmethod
    def increase(
        difficulty: str | DifficultyLevel,
        steps: int = 1,
    ) -> DifficultyLevel:
        """Increase difficulty by the requested number of steps."""

        current = DifficultyManager.rank(difficulty)

        target = min(
            current + max(0, int(steps)),
            len(DIFFICULTY_ORDER) - 1,
        )

        return DIFFICULTY_ORDER[target]

    @staticmethod
    def decrease(
        difficulty: str | DifficultyLevel,
        steps: int = 1,
    ) -> DifficultyLevel:
        """Decrease difficulty by the requested number of steps."""

        current = DifficultyManager.rank(difficulty)

        target = max(
            current - max(0, int(steps)),
            0,
        )

        return DIFFICULTY_ORDER[target]

    # ------------------------------------------------------------------
    # Score-Based Selection
    # ------------------------------------------------------------------

    def from_score(
        self,
        score: float,
    ) -> DifficultyLevel:
        """
        Select a difficulty level from a performance score.

        Score:
            0-44   -> easy
            45-74  -> medium
            75-100 -> hard
        """

        try:
            score = float(score)
        except (TypeError, ValueError):
            return DifficultyLevel.MEDIUM

        score = max(
            0.0,
            min(100.0, score),
        )

        if score < 45:
            return DifficultyLevel.EASY

        if score < 75:
            return DifficultyLevel.MEDIUM

        return DifficultyLevel.HARD

    # ------------------------------------------------------------------
    # Adaptive Difficulty
    # ------------------------------------------------------------------

    def adapt(
        self,
        current_difficulty: str | DifficultyLevel,
        score: float,
        *,
        increase_threshold: float = 80.0,
        decrease_threshold: float = 45.0,
    ) -> DifficultyLevel:
        """
        Adapt difficulty based on the candidate's performance.

        High score:
            Increase difficulty.

        Low score:
            Decrease difficulty.

        Middle score:
            Keep current difficulty.
        """

        current = self.normalize(current_difficulty)

        try:
            score = float(score)
        except (TypeError, ValueError):
            return current

        score = max(
            0.0,
            min(100.0, score),
        )

        if score >= increase_threshold:
            return self.increase(current)

        if score < decrease_threshold:
            return self.decrease(current)

        return current

    # ------------------------------------------------------------------
    # Weighted Adaptive Difficulty
    # ------------------------------------------------------------------

    def adaptive_score(
        self,
        *,
        answer_score: float,
        technical_score: float | None = None,
        communication_score: float | None = None,
        confidence_score: float | None = None,
    ) -> float:
        """
        Calculate an overall performance score for difficulty adaptation.
        """

        scores: list[tuple[float, float]] = [
            (float(answer_score), 0.50),
        ]

        if technical_score is not None:
            scores.append(
                (float(technical_score), 0.25)
            )

        if communication_score is not None:
            scores.append(
                (float(communication_score), 0.15)
            )

        if confidence_score is not None:
            scores.append(
                (float(confidence_score), 0.10)
            )

        total_weight = sum(
            weight for _, weight in scores
        )

        if total_weight <= 0:
            return 50.0

        weighted_score = sum(
            max(0.0, min(100.0, score)) * weight
            for score, weight in scores
        )

        return round(
            weighted_score / total_weight,
            2,
        )

    def adapt_from_performance(
        self,
        current_difficulty: str | DifficultyLevel,
        *,
        answer_score: float,
        technical_score: float | None = None,
        communication_score: float | None = None,
        confidence_score: float | None = None,
    ) -> DifficultyLevel:
        """Adapt difficulty from multiple interview performance signals."""

        score = self.adaptive_score(
            answer_score=answer_score,
            technical_score=technical_score,
            communication_score=communication_score,
            confidence_score=confidence_score,
        )

        return self.adapt(
            current_difficulty,
            score,
        )

    # ------------------------------------------------------------------
    # Question Complexity
    # ------------------------------------------------------------------

    def complexity_requirements(
        self,
        difficulty: str | DifficultyLevel,
    ) -> dict[str, Any]:
        """Return requirements used by question generation."""

        config = self.get_config(difficulty)

        return {
            "difficulty": config.level.value,
            "complexity": config.complexity,
            "follow_up_depth": config.follow_up_depth,
            "expected_reasoning": config.expected_reasoning,
            "score_range": {
                "min": config.score_min,
                "max": config.score_max,
            },
            "description": config.description,
        }

    # ------------------------------------------------------------------
    # Difficulty From Experience
    # ------------------------------------------------------------------

    def from_experience(
        self,
        years: float,
    ) -> DifficultyLevel:
        """
        Estimate starting difficulty from years of experience.

        < 1 year      -> easy
        1-3 years     -> medium
        > 3 years     -> hard
        """

        try:
            years = max(
                0.0,
                float(years),
            )
        except (TypeError, ValueError):
            return DifficultyLevel.MEDIUM

        if years < 1:
            return DifficultyLevel.EASY

        if years < 3:
            return DifficultyLevel.MEDIUM

        return DifficultyLevel.HARD

    # ------------------------------------------------------------------
    # Role-Aware Starting Difficulty
    # ------------------------------------------------------------------

    def starting_difficulty(
        self,
        *,
        experience_years: float | None = None,
        role_level: str | None = None,
        requested_difficulty: str | DifficultyLevel | None = None,
    ) -> DifficultyLevel:
        """
        Determine the initial interview difficulty.

        Explicit requested difficulty takes priority.
        """

        if requested_difficulty is not None:
            return self.normalize(
                requested_difficulty
            )

        if role_level:
            role = role_level.strip().lower()

            role_mapping = {
                "intern": DifficultyLevel.EASY,
                "internship": DifficultyLevel.EASY,
                "fresher": DifficultyLevel.EASY,
                "junior": DifficultyLevel.EASY,
                "entry": DifficultyLevel.EASY,
                "entry-level": DifficultyLevel.EASY,
                "mid": DifficultyLevel.MEDIUM,
                "mid-level": DifficultyLevel.MEDIUM,
                "senior": DifficultyLevel.HARD,
                "senior-level": DifficultyLevel.HARD,
                "lead": DifficultyLevel.HARD,
                "principal": DifficultyLevel.HARD,
                "staff": DifficultyLevel.HARD,
                "architect": DifficultyLevel.HARD,
            }

            if role in role_mapping:
                return role_mapping[role]

        if experience_years is not None:
            return self.from_experience(
                experience_years
            )

        return DifficultyLevel.MEDIUM

    # ------------------------------------------------------------------
    # Difficulty Validation
    # ------------------------------------------------------------------

    def validate(
        self,
        difficulty: str | DifficultyLevel,
    ) -> bool:
        """Check whether a difficulty value is valid."""

        if isinstance(difficulty, DifficultyLevel):
            return True

        value = str(
            difficulty
        ).strip().lower()

        return value in {
            "easy",
            "medium",
            "hard",
            "beginner",
            "basic",
            "low",
            "intermediate",
            "moderate",
            "mid",
            "advanced",
            "expert",
            "high",
        }

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(
        self,
        difficulty: str | DifficultyLevel,
    ) -> dict[str, Any]:
        """Serialize difficulty configuration."""

        config = self.get_config(difficulty)

        return {
            "level": config.level.value,
            "score_min": config.score_min,
            "score_max": config.score_max,
            "complexity": config.complexity,
            "follow_up_depth": config.follow_up_depth,
            "expected_reasoning": config.expected_reasoning,
            "description": config.description,
        }

    def all_levels(self) -> list[dict[str, Any]]:
        """Return all difficulty levels."""

        return [
            self.to_dict(level)
            for level in DIFFICULTY_ORDER
        ]


# ============================================================================
# Convenience Functions
# ============================================================================

_default_manager = DifficultyManager()


def normalize_difficulty(
    difficulty: str | DifficultyLevel | None,
) -> str:
    """Normalize a difficulty and return its string value."""

    return _default_manager.normalize(
        difficulty
    ).value


def increase_difficulty(
    difficulty: str | DifficultyLevel,
    steps: int = 1,
) -> str:
    """Increase interview difficulty."""

    return _default_manager.increase(
        difficulty,
        steps,
    ).value


def decrease_difficulty(
    difficulty: str | DifficultyLevel,
    steps: int = 1,
) -> str:
    """Decrease interview difficulty."""

    return _default_manager.decrease(
        difficulty,
        steps,
    ).value


def difficulty_from_score(
    score: float,
) -> str:
    """Get difficulty from a performance score."""

    return _default_manager.from_score(
        score
    ).value


def adaptive_difficulty(
    current_difficulty: str | DifficultyLevel,
    score: float,
) -> str:
    """Get the next adaptive difficulty."""

    return _default_manager.adapt(
        current_difficulty,
        score,
    ).value


def get_starting_difficulty(
    *,
    experience_years: float | None = None,
    role_level: str | None = None,
    requested_difficulty: str | DifficultyLevel | None = None,
) -> str:
    """Get an appropriate starting interview difficulty."""

    return _default_manager.starting_difficulty(
        experience_years=experience_years,
        role_level=role_level,
        requested_difficulty=requested_difficulty,
    ).value


# ============================================================================
# Public API
# ============================================================================

__all__ = [
    "DifficultyLevel",
    "DifficultyConfig",
    "DifficultyManager",
    "DIFFICULTY_CONFIGS",
    "DIFFICULTY_ORDER",
    "normalize_difficulty",
    "increase_difficulty",
    "decrease_difficulty",
    "difficulty_from_score",
    "adaptive_difficulty",
    "get_starting_difficulty",
]