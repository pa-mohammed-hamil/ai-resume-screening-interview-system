# Project scaffold file
"""
Next Question Selector

Responsible for selecting the next interview question based on:
- Current difficulty
- Interview category
- Candidate performance
- Previous questions
- Weak skill areas
- Question diversity
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence


@dataclass
class QuestionSelection:
    """Represents a selected interview question."""

    question: Dict[str, Any]
    score: float
    reason: str


class NextQuestionSelector:
    """
    Selects the next question for an adaptive interview.

    Expected question format:

        {
            "id": "q001",
            "question": "Explain Python decorators.",
            "category": "python",
            "difficulty": "medium",
            "type": "technical",
            "skills": ["python", "decorators"],
            "topic": "advanced-python"
        }
    """

    VALID_DIFFICULTIES = ("easy", "medium", "hard")

    def __init__(
        self,
        difficulty_weight: float = 0.40,
        category_weight: float = 0.25,
        skill_weight: float = 0.20,
        diversity_weight: float = 0.15,
    ) -> None:
        self.difficulty_weight = difficulty_weight
        self.category_weight = category_weight
        self.skill_weight = skill_weight
        self.diversity_weight = diversity_weight

    # ------------------------------------------------------------------
    # Main Selection
    # ------------------------------------------------------------------

    def select(
        self,
        questions: Sequence[Dict[str, Any]],
        difficulty: str = "medium",
        category: Optional[str] = None,
        history: Optional[List[Dict[str, Any]]] = None,
        weak_categories: Optional[List[str]] = None,
        weak_skills: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Select the best next question.

        Returns:
            Selected question dictionary or None.
        """

        if not questions:
            return None

        difficulty = self._normalize_difficulty(difficulty)
        history = history or []
        weak_categories = weak_categories or []
        weak_skills = weak_skills or []

        available = self._remove_previous_questions(
            questions,
            history,
        )

        # If all questions were previously used, allow reuse as a
        # fallback rather than returning nothing.
        if not available:
            available = list(questions)

        ranked = []

        for question in available:
            score = self._calculate_score(
                question=question,
                target_difficulty=difficulty,
                target_category=category,
                history=history,
                weak_categories=weak_categories,
                weak_skills=weak_skills,
            )

            ranked.append(
                QuestionSelection(
                    question=question,
                    score=score,
                    reason=self._build_reason(
                        question=question,
                        target_difficulty=difficulty,
                        target_category=category,
                    ),
                )
            )

        ranked.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        return ranked[0].question

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def _calculate_score(
        self,
        question: Dict[str, Any],
        target_difficulty: str,
        target_category: Optional[str],
        history: List[Dict[str, Any]],
        weak_categories: List[str],
        weak_skills: List[str],
    ) -> float:
        """Calculate a ranking score for a question."""

        difficulty_score = self._difficulty_score(
            question.get("difficulty"),
            target_difficulty,
        )

        category_score = self._category_score(
            question.get("category"),
            target_category,
            weak_categories,
        )

        skill_score = self._skill_score(
            question.get("skills", []),
            weak_skills,
        )

        diversity_score = self._diversity_score(
            question,
            history,
        )

        return (
            difficulty_score * self.difficulty_weight
            + category_score * self.category_weight
            + skill_score * self.skill_weight
            + diversity_score * self.diversity_weight
        )

    # ------------------------------------------------------------------
    # Difficulty
    # ------------------------------------------------------------------

    def _difficulty_score(
        self,
        question_difficulty: Optional[str],
        target_difficulty: str,
    ) -> float:
        """
        Score how closely the question difficulty matches the
        requested difficulty.

        Exact match = 1.0
        One level away = 0.5
        Two levels away = 0.0
        """

        if not question_difficulty:
            return 0.0

        question_difficulty = self._normalize_difficulty(
            question_difficulty
        )

        target_difficulty = self._normalize_difficulty(
            target_difficulty
        )

        question_index = self.VALID_DIFFICULTIES.index(
            question_difficulty
        )

        target_index = self.VALID_DIFFICULTIES.index(
            target_difficulty
        )

        distance = abs(question_index - target_index)

        if distance == 0:
            return 1.0

        if distance == 1:
            return 0.5

        return 0.0

    # ------------------------------------------------------------------
    # Category
    # ------------------------------------------------------------------

    def _category_score(
        self,
        question_category: Optional[str],
        target_category: Optional[str],
        weak_categories: List[str],
    ) -> float:
        """Score category relevance."""

        if not question_category:
            return 0.0

        question_category = question_category.lower().strip()

        if target_category:
            target_category = target_category.lower().strip()

            if question_category == target_category:
                return 1.0

        if question_category in {
            category.lower().strip()
            for category in weak_categories
        }:
            return 0.9

        return 0.2

    # ------------------------------------------------------------------
    # Skills
    # ------------------------------------------------------------------

    def _skill_score(
        self,
        question_skills: Sequence[str],
        weak_skills: Sequence[str],
    ) -> float:
        """Score overlap between question skills and weak skills."""

        if not question_skills:
            return 0.0

        if not weak_skills:
            return 0.5

        question_skill_set = {
            str(skill).lower().strip()
            for skill in question_skills
        }

        weak_skill_set = {
            str(skill).lower().strip()
            for skill in weak_skills
        }

        overlap = question_skill_set.intersection(
            weak_skill_set
        )

        if not overlap:
            return 0.2

        return min(
            1.0,
            len(overlap) / max(1, len(weak_skill_set)),
        )

    # ------------------------------------------------------------------
    # Diversity
    # ------------------------------------------------------------------

    def _diversity_score(
        self,
        question: Dict[str, Any],
        history: List[Dict[str, Any]],
    ) -> float:
        """
        Encourage topic/category diversity.

        A question from a recently used topic receives a lower score.
        """

        if not history:
            return 1.0

        question_topic = str(
            question.get("topic", "")
        ).lower().strip()

        question_category = str(
            question.get("category", "")
        ).lower().strip()

        recent_history = history[-3:]

        recent_topics = {
            str(item.get("topic", "")).lower().strip()
            for item in recent_history
            if item.get("topic")
        }

        recent_categories = {
            str(item.get("category", "")).lower().strip()
            for item in recent_history
            if item.get("category")
        }

        if question_topic and question_topic in recent_topics:
            return 0.2

        if (
            question_category
            and question_category in recent_categories
        ):
            return 0.6

        return 1.0

    # ------------------------------------------------------------------
    # Previous Questions
    # ------------------------------------------------------------------

    def _remove_previous_questions(
        self,
        questions: Sequence[Dict[str, Any]],
        history: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Remove questions already used in the interview."""

        if not history:
            return list(questions)

        previous_ids = {
            str(item.get("question_id"))
            for item in history
            if item.get("question_id") is not None
        }

        previous_text = {
            str(item.get("question", "")).strip().lower()
            for item in history
            if item.get("question")
        }

        result = []

        for question in questions:
            question_id = str(
                question.get("id")
                or question.get("question_id")
                or ""
            )

            question_text = str(
                question.get("question", "")
            ).strip().lower()

            if question_id and question_id in previous_ids:
                continue

            if question_text and question_text in previous_text:
                continue

            result.append(question)

        return result

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def filter_questions(
        self,
        questions: Sequence[Dict[str, Any]],
        difficulty: Optional[str] = None,
        category: Optional[str] = None,
        question_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Filter questions by difficulty/category/type."""

        result = list(questions)

        if difficulty:
            difficulty = self._normalize_difficulty(difficulty)

            result = [
                question
                for question in result
                if self._normalize_difficulty(
                    question.get("difficulty", "medium")
                )
                == difficulty
            ]

        if category:
            category = category.lower().strip()

            result = [
                question
                for question in result
                if str(
                    question.get("category", "")
                ).lower().strip()
                == category
            ]

        if question_type:
            question_type = question_type.lower().strip()

            result = [
                question
                for question in result
                if str(
                    question.get("type", "")
                ).lower().strip()
                == question_type
            ]

        return result

    # ------------------------------------------------------------------
    # Specialized Selection
    # ------------------------------------------------------------------

    def select_technical_question(
        self,
        questions: Sequence[Dict[str, Any]],
        difficulty: str,
        history: Optional[List[Dict[str, Any]]] = None,
        weak_skills: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Select a technical interview question."""

        technical_questions = self.filter_questions(
            questions,
            question_type="technical",
        )

        if not technical_questions:
            technical_questions = list(questions)

        return self.select(
            questions=technical_questions,
            difficulty=difficulty,
            history=history,
            weak_skills=weak_skills,
        )

    def select_behavioral_question(
        self,
        questions: Sequence[Dict[str, Any]],
        difficulty: str,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Select a behavioral interview question."""

        behavioral_questions = self.filter_questions(
            questions,
            question_type="behavioral",
        )

        if not behavioral_questions:
            behavioral_questions = list(questions)

        return self.select(
            questions=behavioral_questions,
            difficulty=difficulty,
            history=history,
        )

    # ------------------------------------------------------------------
    # Reasoning
    # ------------------------------------------------------------------

    def _build_reason(
        self,
        question: Dict[str, Any],
        target_difficulty: str,
        target_category: Optional[str],
    ) -> str:
        """Generate a human-readable selection reason."""

        question_difficulty = self._normalize_difficulty(
            question.get("difficulty", "medium")
        )

        if question_difficulty == target_difficulty:
            difficulty_reason = (
                f"matches target difficulty '{target_difficulty}'"
            )
        else:
            difficulty_reason = (
                f"is closest to target difficulty "
                f"'{target_difficulty}'"
            )

        if target_category:
            category = str(
                question.get("category", "")
            ).lower().strip()

            if category == target_category.lower().strip():
                category_reason = (
                    f" and matches category '{target_category}'"
                )
            else:
                category_reason = ""

        else:
            category_reason = ""

        return (
            f"Selected because it {difficulty_reason}"
            f"{category_reason}."
        )

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def _normalize_difficulty(
        self,
        difficulty: Any,
    ) -> str:
        """Normalize invalid difficulty values to medium."""

        if difficulty is None:
            return "medium"

        difficulty = str(difficulty).lower().strip()

        if difficulty not in self.VALID_DIFFICULTIES:
            return "medium"

        return difficulty