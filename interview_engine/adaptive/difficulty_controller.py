# Project scaffold file
"""
Difficulty Controller

Controls the difficulty level of adaptive interviews.

Responsibilities:
- Validate difficulty levels
- Increase/decrease difficulty
- Calculate difficulty from candidate performance
- Avoid sudden difficulty jumps
- Track performance trends
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class DifficultyDecision:
    """Represents a difficulty adjustment decision."""

    previous: str
    current: str
    changed: bool
    direction: str
    reason: str
    score: Optional[float] = None


class DifficultyController:
    """
    Controls adaptive interview difficulty.

    Difficulty levels:

        easy -> medium -> hard

    Example:

        controller = DifficultyController()

        result = controller.calculate_next_difficulty(
            current="medium",
            score=88,
        )

        print(result.current)
    """

    LEVELS = ("easy", "medium", "hard")

    SCORE_THRESHOLDS = {
        "excellent": 85,
        "good": 70,
        "average": 50,
    }

    def __init__(
        self,
        increase_threshold: float = 80.0,
        decrease_threshold: float = 50.0,
        strong_streak_required: int = 2,
        weak_streak_required: int = 2,
    ) -> None:
        self.increase_threshold = increase_threshold
        self.decrease_threshold = decrease_threshold

        self.strong_streak_required = max(
            1,
            strong_streak_required,
        )

        self.weak_streak_required = max(
            1,
            weak_streak_required,
        )

        self.good_streak = 0
        self.poor_streak = 0

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_difficulty(self, difficulty: str) -> str:
        """
        Validate and normalize a difficulty level.

        Invalid values default to medium.
        """

        if not difficulty:
            return "medium"

        difficulty = difficulty.lower().strip()

        if difficulty not in self.LEVELS:
            return "medium"

        return difficulty

    # ------------------------------------------------------------------
    # Basic Difficulty Movement
    # ------------------------------------------------------------------

    def increase(self, difficulty: str) -> str:
        """
        Increase difficulty by one level.

        easy -> medium
        medium -> hard
        hard -> hard
        """

        difficulty = self.validate_difficulty(difficulty)

        index = self.LEVELS.index(difficulty)

        return self.LEVELS[
            min(index + 1, len(self.LEVELS) - 1)
        ]

    def decrease(self, difficulty: str) -> str:
        """
        Decrease difficulty by one level.

        hard -> medium
        medium -> easy
        easy -> easy
        """

        difficulty = self.validate_difficulty(difficulty)

        index = self.LEVELS.index(difficulty)

        return self.LEVELS[
            max(index - 1, 0)
        ]

    def maintain(self, difficulty: str) -> str:
        """Keep the current difficulty."""

        return self.validate_difficulty(difficulty)

    # ------------------------------------------------------------------
    # Performance Classification
    # ------------------------------------------------------------------

    def classify_score(self, score: float) -> str:
        """
        Classify candidate performance.

        Returns:
            excellent
            good
            average
            poor
        """

        score = self.normalize_score(score)

        if score >= self.SCORE_THRESHOLDS["excellent"]:
            return "excellent"

        if score >= self.SCORE_THRESHOLDS["good"]:
            return "good"

        if score >= self.SCORE_THRESHOLDS["average"]:
            return "average"

        return "poor"

    def normalize_score(self, score: float) -> float:
        """
        Normalize score to the range 0-100.

        Supports both:
            0.0 - 1.0
            0 - 100
        """

        try:
            score = float(score)
        except (TypeError, ValueError):
            return 0.0

        if score <= 1.0:
            score *= 100

        return max(0.0, min(100.0, score))

    # ------------------------------------------------------------------
    # Adaptive Decision
    # ------------------------------------------------------------------

    def calculate_next_difficulty(
        self,
        current: str,
        score: float,
        use_streak: bool = True,
    ) -> DifficultyDecision:
        """
        Calculate the next difficulty based on performance.

        Strong performance:
            Increase difficulty.

        Average performance:
            Maintain difficulty.

        Poor performance:
            Decrease difficulty.
        """

        current = self.validate_difficulty(current)
        score = self.normalize_score(score)

        performance = self.classify_score(score)

        if performance in ("excellent", "good"):
            self.good_streak += 1
            self.poor_streak = 0
        elif performance == "poor":
            self.poor_streak += 1
            self.good_streak = 0
        else:
            self.good_streak = 0
            self.poor_streak = 0

        # --------------------------------------------------------------
        # Increase difficulty
        # --------------------------------------------------------------

        if score >= self.increase_threshold:

            if (
                not use_streak
                or self.good_streak >= self.strong_streak_required
            ):
                next_level = self.increase(current)

                if next_level != current:
                    return DifficultyDecision(
                        previous=current,
                        current=next_level,
                        changed=True,
                        direction="increase",
                        reason=(
                            "Candidate is consistently performing "
                            "well."
                        ),
                        score=score,
                    )

        # --------------------------------------------------------------
        # Decrease difficulty
        # --------------------------------------------------------------

        if score < self.decrease_threshold:

            if (
                not use_streak
                or self.poor_streak >= self.weak_streak_required
            ):
                next_level = self.decrease(current)

                if next_level != current:
                    return DifficultyDecision(
                        previous=current,
                        current=next_level,
                        changed=True,
                        direction="decrease",
                        reason=(
                            "Candidate is consistently struggling "
                            "with the current difficulty."
                        ),
                        score=score,
                    )

        # --------------------------------------------------------------
        # Maintain difficulty
        # --------------------------------------------------------------

        return DifficultyDecision(
            previous=current,
            current=current,
            changed=False,
            direction="maintain",
            reason=(
                "Candidate performance does not justify "
                "a difficulty change."
            ),
            score=score,
        )

    # ------------------------------------------------------------------
    # Trend Analysis
    # ------------------------------------------------------------------

    def analyze_trend(
        self,
        scores: List[float],
    ) -> Dict[str, object]:
        """
        Analyze recent candidate performance.

        Example:

            [60, 70, 80, 90]

        indicates an improving trend.
        """

        if not scores:
            return {
                "trend": "stable",
                "average": 0.0,
                "recent_average": 0.0,
                "improving": False,
                "declining": False,
            }

        normalized = [
            self.normalize_score(score)
            for score in scores
        ]

        average = sum(normalized) / len(normalized)

        # Compare earlier and recent performance.
        if len(normalized) >= 4:
            midpoint = len(normalized) // 2

            earlier = normalized[:midpoint]
            recent = normalized[midpoint:]

            earlier_average = sum(earlier) / len(earlier)
            recent_average = sum(recent) / len(recent)

            difference = recent_average - earlier_average

            if difference >= 10:
                trend = "improving"
            elif difference <= -10:
                trend = "declining"
            else:
                trend = "stable"

        else:
            recent_average = sum(normalized) / len(normalized)
            trend = "stable"

        return {
            "trend": trend,
            "average": round(average, 2),
            "recent_average": round(recent_average, 2),
            "improving": trend == "improving",
            "declining": trend == "declining",
        }

    # ------------------------------------------------------------------
    # Batch Decision
    # ------------------------------------------------------------------

    def difficulty_from_history(
        self,
        current: str,
        scores: List[float],
    ) -> DifficultyDecision:
        """
        Calculate difficulty using the candidate's recent score history.

        This is useful when restoring an interview session.
        """

        current = self.validate_difficulty(current)

        if not scores:
            return DifficultyDecision(
                previous=current,
                current=current,
                changed=False,
                direction="maintain",
                reason="No performance history available.",
            )

        trend = self.analyze_trend(scores)

        recent_score = trend["recent_average"]

        # Strong upward trend.
        if trend["improving"] and recent_score >= 75:
            next_level = self.increase(current)

            return DifficultyDecision(
                previous=current,
                current=next_level,
                changed=next_level != current,
                direction="increase"
                if next_level != current
                else "maintain",
                reason="Recent performance is improving.",
                score=recent_score,
            )

        # Declining performance.
        if trend["declining"] and recent_score < 60:
            next_level = self.decrease(current)

            return DifficultyDecision(
                previous=current,
                current=next_level,
                changed=next_level != current,
                direction="decrease"
                if next_level != current
                else "maintain",
                reason="Recent performance is declining.",
                score=recent_score,
            )

        # Normal score-based decision.
        return self.calculate_next_difficulty(
            current=current,
            score=recent_score,
            use_streak=False,
        )

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Reset performance streaks."""

        self.good_streak = 0
        self.poor_streak = 0

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def get_state(self) -> Dict[str, object]:
        """Return the current controller state."""

        return {
            "levels": list(self.LEVELS),
            "increase_threshold": self.increase_threshold,
            "decrease_threshold": self.decrease_threshold,
            "strong_streak_required": self.strong_streak_required,
            "weak_streak_required": self.weak_streak_required,
            "good_streak": self.good_streak,
            "poor_streak": self.poor_streak,
        }