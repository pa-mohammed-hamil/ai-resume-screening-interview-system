# Project scaffold file
"""
Adaptive Interview Engine

Responsible for:
- Tracking interview performance
- Adjusting question difficulty
- Selecting the next question category
- Preventing difficulty from changing too aggressively
- Maintaining an adaptive interview state
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .difficulty_controller import DifficultyController
from .next_question import NextQuestionSelector


@dataclass
class AnswerResult:
    """Represents the evaluation result of one candidate answer."""

    score: float
    technical_score: float = 0.0
    communication_score: float = 0.0
    confidence_score: float = 0.0
    correct: Optional[bool] = None
    category: str = "general"
    difficulty: str = "medium"
    feedback: Optional[str] = None

    def normalized_score(self) -> float:
        """Return the overall score normalized to 0-100."""
        score = self.score

        if score <= 1:
            score *= 100

        return max(0.0, min(100.0, score))


@dataclass
class InterviewState:
    """Maintains the current adaptive interview state."""

    current_difficulty: str = "medium"
    current_category: str = "technical"

    questions_asked: int = 0
    questions_answered: int = 0

    consecutive_good_answers: int = 0
    consecutive_poor_answers: int = 0

    total_score: float = 0.0
    average_score: float = 0.0

    category_scores: Dict[str, List[float]] = field(default_factory=dict)
    difficulty_history: List[str] = field(default_factory=list)
    answer_history: List[Dict[str, Any]] = field(default_factory=list)

    completed: bool = False


class AdaptiveInterviewEngine:
    """
    Adaptive interview controller.

    Example:

        engine = AdaptiveInterviewEngine()

        result = engine.process_answer(
            AnswerResult(
                score=85,
                technical_score=90,
                communication_score=80,
                category="python",
                difficulty="medium",
            )
        )

        next_question = engine.get_next_question()
    """

    VALID_DIFFICULTIES = ("easy", "medium", "hard")

    def __init__(
        self,
        difficulty_controller: Optional[DifficultyController] = None,
        question_selector: Optional[NextQuestionSelector] = None,
        max_questions: int = 10,
        min_questions: int = 5,
    ) -> None:
        self.difficulty_controller = (
            difficulty_controller or DifficultyController()
        )

        self.question_selector = (
            question_selector or NextQuestionSelector()
        )

        self.max_questions = max(1, max_questions)
        self.min_questions = max(1, min_questions)

        self.state = InterviewState()

    # ------------------------------------------------------------------
    # Answer Processing
    # ------------------------------------------------------------------

    def process_answer(self, result: AnswerResult) -> Dict[str, Any]:
        """
        Process a candidate's answer and update the interview state.

        Returns information about the adaptive decision.
        """

        score = result.normalized_score()

        self.state.questions_answered += 1
        self.state.total_score += score

        self.state.average_score = (
            self.state.total_score / self.state.questions_answered
        )

        category = result.category or "general"

        if category not in self.state.category_scores:
            self.state.category_scores[category] = []

        self.state.category_scores[category].append(score)

        self.state.answer_history.append(
            {
                "score": score,
                "technical_score": result.technical_score,
                "communication_score": result.communication_score,
                "confidence_score": result.confidence_score,
                "correct": result.correct,
                "category": category,
                "difficulty": result.difficulty,
                "feedback": result.feedback,
            }
        )

        self._update_performance_streak(score)

        old_difficulty = self.state.current_difficulty

        new_difficulty = self._calculate_next_difficulty(score)

        self.state.current_difficulty = new_difficulty

        self.state.difficulty_history.append(new_difficulty)

        return {
            "score": score,
            "average_score": round(self.state.average_score, 2),
            "previous_difficulty": old_difficulty,
            "next_difficulty": new_difficulty,
            "performance": self._performance_level(score),
            "should_continue": self.should_continue(),
        }

    # ------------------------------------------------------------------
    # Difficulty Adaptation
    # ------------------------------------------------------------------

    def _calculate_next_difficulty(self, score: float) -> str:
        """
        Calculate the next question difficulty.

        Strong performance:
            easy -> medium
            medium -> hard

        Weak performance:
            hard -> medium
            medium -> easy
        """

        current = self.state.current_difficulty

        if current not in self.VALID_DIFFICULTIES:
            current = "medium"

        # Strong performance.
        if score >= 80:
            self.state.consecutive_good_answers += 1
            self.state.consecutive_poor_answers = 0

            if self.state.consecutive_good_answers >= 2:
                return self._increase_difficulty(current)

            return current

        # Weak performance.
        if score < 50:
            self.state.consecutive_poor_answers += 1
            self.state.consecutive_good_answers = 0

            if self.state.consecutive_poor_answers >= 2:
                return self._decrease_difficulty(current)

            return current

        # Average performance.
        self.state.consecutive_good_answers = 0
        self.state.consecutive_poor_answers = 0

        return current

    def _increase_difficulty(self, difficulty: str) -> str:
        """Increase difficulty by one level."""

        levels = list(self.VALID_DIFFICULTIES)
        index = levels.index(difficulty)

        return levels[min(index + 1, len(levels) - 1)]

    def _decrease_difficulty(self, difficulty: str) -> str:
        """Decrease difficulty by one level."""

        levels = list(self.VALID_DIFFICULTIES)
        index = levels.index(difficulty)

        return levels[max(index - 1, 0)]

    # ------------------------------------------------------------------
    # Question Selection
    # ------------------------------------------------------------------

    def get_next_question(
        self,
        available_questions: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Select the next question using the current adaptive state.
        """

        if not self.should_continue():
            self.state.completed = True
            return None

        self.state.questions_asked += 1

        questions = available_questions or []

        # Try the dedicated selector first.
        try:
            question = self.question_selector.select(
                questions=questions,
                difficulty=self.state.current_difficulty,
                category=self.state.current_category,
                history=self.state.answer_history,
            )
        except (AttributeError, TypeError):
            question = self._fallback_question(questions)

        if question is None:
            question = self._fallback_question(questions)

        return question

    def _fallback_question(
        self,
        questions: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Simple fallback question selection."""

        if not questions:
            return None

        matching = [
            question
            for question in questions
            if question.get("difficulty") == self.state.current_difficulty
        ]

        if not matching:
            matching = questions

        # Prefer questions that have not already been asked.
        asked_questions = {
            item.get("question")
            for item in self.state.answer_history
        }

        unused = [
            question
            for question in matching
            if question.get("question") not in asked_questions
        ]

        return (unused or matching)[0]

    # ------------------------------------------------------------------
    # Category Adaptation
    # ------------------------------------------------------------------

    def set_category(self, category: str) -> None:
        """Change the interview question category."""

        if not category:
            return

        self.state.current_category = category

    def get_weak_categories(self) -> List[str]:
        """
        Return categories where the candidate's average score is below 60.
        """

        weak_categories = []

        for category, scores in self.state.category_scores.items():
            if not scores:
                continue

            average = sum(scores) / len(scores)

            if average < 60:
                weak_categories.append(category)

        return weak_categories

    def get_strong_categories(self) -> List[str]:
        """Return categories where the candidate performs strongly."""

        strong_categories = []

        for category, scores in self.state.category_scores.items():
            if not scores:
                continue

            average = sum(scores) / len(scores)

            if average >= 80:
                strong_categories.append(category)

        return strong_categories

    def select_next_category(self) -> str:
        """
        Select the next category.

        Weak areas receive priority so the interview can evaluate
        candidate weaknesses more thoroughly.
        """

        weak_categories = self.get_weak_categories()

        if weak_categories:
            return weak_categories[0]

        return self.state.current_category

    # ------------------------------------------------------------------
    # Interview Control
    # ------------------------------------------------------------------

    def should_continue(self) -> bool:
        """Determine whether the interview should continue."""

        if self.state.completed:
            return False

        if self.state.questions_answered >= self.max_questions:
            return False

        if self.state.questions_answered < self.min_questions:
            return True

        # If enough questions have been answered, stop when
        # performance is consistently very high or very low.
        if self.state.questions_answered >= self.min_questions:
            if self.state.average_score >= 92:
                return False

            if (
                self.state.average_score < 35
                and self.state.questions_answered >= 7
            ):
                return False

        return True

    def complete(self) -> None:
        """Manually complete the interview."""

        self.state.completed = True

    # ------------------------------------------------------------------
    # Performance
    # ------------------------------------------------------------------

    @staticmethod
    def _performance_level(score: float) -> str:
        """Convert numerical score into a performance label."""

        if score >= 85:
            return "excellent"

        if score >= 70:
            return "good"

        if score >= 50:
            return "average"

        return "needs_improvement"

    def get_performance_summary(self) -> Dict[str, Any]:
        """Return the current interview performance summary."""

        return {
            "questions_asked": self.state.questions_asked,
            "questions_answered": self.state.questions_answered,
            "average_score": round(self.state.average_score, 2),
            "current_difficulty": self.state.current_difficulty,
            "current_category": self.state.current_category,
            "strong_categories": self.get_strong_categories(),
            "weak_categories": self.get_weak_categories(),
            "completed": self.state.completed,
        }

    # ------------------------------------------------------------------
    # State Management
    # ------------------------------------------------------------------

    def get_state(self) -> Dict[str, Any]:
        """Serialize the current engine state."""

        return {
            "current_difficulty": self.state.current_difficulty,
            "current_category": self.state.current_category,
            "questions_asked": self.state.questions_asked,
            "questions_answered": self.state.questions_answered,
            "consecutive_good_answers": self.state.consecutive_good_answers,
            "consecutive_poor_answers": self.state.consecutive_poor_answers,
            "total_score": self.state.total_score,
            "average_score": self.state.average_score,
            "category_scores": self.state.category_scores,
            "difficulty_history": self.state.difficulty_history,
            "completed": self.state.completed,
        }

    def reset(self) -> None:
        """Reset the interview engine."""

        self.state = InterviewState()