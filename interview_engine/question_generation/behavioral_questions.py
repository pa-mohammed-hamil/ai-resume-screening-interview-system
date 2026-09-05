# Project scaffold file
"""
Behavioral Interview Question Bank

Location:
    interview_engine/question_generation/behavioral_questions.py

Purpose:
    Provides behavioral interview questions organized by competency,
    difficulty, and common interview themes.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


# ============================================================================
# Data Model
# ============================================================================


@dataclass(frozen=True)
class BehavioralQuestion:
    """Represents a behavioral interview question."""

    question: str
    competency: str
    difficulty: str = "medium"
    expected_answer_points: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ============================================================================
# Behavioral Question Banks
# ============================================================================


COMMUNICATION_QUESTIONS = {
    "easy": [
        "Tell me about yourself.",
        "How do you explain a complex technical concept to a non-technical person?",
        "How do you make sure your message is understood by others?",
        "Tell me about a time you had to communicate an important update.",
        "How do you handle misunderstandings at work?",
    ],
    "medium": [
        "Tell me about a time you had to explain a difficult technical issue to a stakeholder.",
        "Describe a situation where communication helped resolve a problem.",
        "Tell me about a time you received feedback about your communication style.",
        "Describe a time when you had to communicate bad news to your team.",
        "Tell me about a time when poor communication caused a problem and what you learned.",
    ],
    "hard": [
        "Describe a situation where you had to align multiple stakeholders with conflicting expectations.",
        "Tell me about a time you influenced a decision without having direct authority.",
        "Describe how you handled a communication failure during a high-pressure situation.",
        "Tell me about a time you had to communicate an unpopular technical decision.",
    ],
}


TEAMWORK_QUESTIONS = {
    "easy": [
        "Tell me about a time you worked successfully in a team.",
        "What role do you usually take in a team?",
        "How do you support your teammates?",
        "How do you handle disagreements with teammates?",
        "What makes a team successful?",
    ],
    "medium": [
        "Tell me about a time you had a disagreement with a teammate.",
        "Describe a team project where you had to collaborate closely with others.",
        "Tell me about a time you helped a struggling teammate.",
        "Describe a situation where your team had different opinions about a solution.",
        "Tell me about a time you had to compromise for the benefit of the team.",
    ],
    "hard": [
        "Tell me about a time you resolved a serious conflict within a team.",
        "Describe a situation where you had to lead a team without formal authority.",
        "Tell me about a time you worked with someone whose working style was very different from yours.",
        "Describe how you handled a team failure when responsibility was shared.",
    ],
}


LEADERSHIP_QUESTIONS = {
    "easy": [
        "What does leadership mean to you?",
        "Tell me about a time you took initiative.",
        "Tell me about a time you helped guide others.",
        "How do you motivate yourself and others?",
        "Have you ever led a project?",
    ],
    "medium": [
        "Tell me about a time you led a difficult project.",
        "Describe a situation where you had to make a difficult decision as a leader.",
        "Tell me about a time you delegated an important task.",
        "Describe how you handled a team member who was not meeting expectations.",
        "Tell me about a time you motivated a team under pressure.",
    ],
    "hard": [
        "Describe a situation where you had to lead through major uncertainty.",
        "Tell me about a time you made a decision that your team initially disagreed with.",
        "Describe how you handled a major failure as a leader.",
        "Tell me about a time you built alignment across multiple teams.",
        "Describe a situation where you had to balance business goals with team well-being.",
    ],
}


PROBLEM_SOLVING_QUESTIONS = {
    "easy": [
        "Tell me about a difficult problem you solved.",
        "How do you approach a new problem?",
        "Tell me about a time you had to think creatively.",
        "How do you prioritize problems?",
        "What do you do when you do not know the answer?",
    ],
    "medium": [
        "Tell me about a complex problem you solved at work.",
        "Describe a time when your first solution did not work.",
        "Tell me about a time you solved a problem with limited information.",
        "Describe a situation where you identified a problem before others noticed it.",
        "Tell me about a time you had to make a decision with incomplete information.",
    ],
    "hard": [
        "Describe the most ambiguous problem you have solved.",
        "Tell me about a time when you had to solve a problem with significant technical and business constraints.",
        "Describe a situation where several possible solutions existed and you had to choose one.",
        "Tell me about a time you challenged an existing approach and proposed a better solution.",
    ],
}


CONFLICT_QUESTIONS = {
    "easy": [
        "How do you handle disagreements with coworkers?",
        "Tell me about a time you disagreed with someone.",
        "How do you respond when someone disagrees with your idea?",
        "What do you do when a team member has a different opinion?",
    ],
    "medium": [
        "Tell me about a conflict you had with a teammate and how you resolved it.",
        "Describe a time you disagreed with your manager.",
        "Tell me about a situation where two teammates disagreed and you helped resolve it.",
        "Describe a time when a disagreement affected a project.",
    ],
    "hard": [
        "Tell me about a serious workplace conflict that required significant effort to resolve.",
        "Describe a time when you strongly disagreed with a senior stakeholder.",
        "Tell me about a conflict where neither side initially wanted to compromise.",
        "Describe how you handled a conflict that involved competing organizational priorities.",
    ],
}


ADAPTABILITY_QUESTIONS = {
    "easy": [
        "How do you handle change?",
        "Tell me about a time your priorities changed unexpectedly.",
        "How do you learn a new technology?",
        "Tell me about a time you had to adapt to a new situation.",
    ],
    "medium": [
        "Tell me about a time you had to adapt quickly to a major change.",
        "Describe a project where requirements changed significantly.",
        "Tell me about a time you had to learn something quickly to complete a task.",
        "Describe how you handled an unexpected change in project scope.",
    ],
    "hard": [
        "Tell me about a time you had to completely change your approach because circumstances changed.",
        "Describe a situation where you had to operate effectively despite significant uncertainty.",
        "Tell me about a time you helped your team adapt to a major organizational change.",
        "Describe how you handled rapidly changing requirements on a critical project.",
    ],
}


ACCOUNTABILITY_QUESTIONS = {
    "easy": [
        "Tell me about a mistake you made.",
        "How do you handle responsibility for your work?",
        "What do you do when you make an error?",
        "Tell me about a time you took ownership of a problem.",
    ],
    "medium": [
        "Tell me about a significant mistake you made and what you learned.",
        "Describe a time you took responsibility for a project failure.",
        "Tell me about a time you discovered an error in your own work.",
        "Describe a situation where you had to take ownership of a problem caused by someone else.",
    ],
    "hard": [
        "Tell me about a failure that had significant consequences and how you handled it.",
        "Describe a time when you had to publicly acknowledge a mistake.",
        "Tell me about a time you accepted responsibility even though the failure was not entirely your fault.",
        "Describe how you rebuilt trust after making a serious mistake.",
    ],
}


TIME_MANAGEMENT_QUESTIONS = {
    "easy": [
        "How do you prioritize your tasks?",
        "How do you manage deadlines?",
        "What do you do when you have multiple urgent tasks?",
        "How do you organize your workday?",
    ],
    "medium": [
        "Tell me about a time you had several competing deadlines.",
        "Describe how you prioritized tasks during a busy project.",
        "Tell me about a time you had to deliver something under a tight deadline.",
        "Describe a situation where your original schedule became unrealistic.",
    ],
    "hard": [
        "Tell me about a time you had to choose between two high-priority projects.",
        "Describe how you handled competing priorities from multiple stakeholders.",
        "Tell me about a time you had to deliver critical work with significantly limited resources.",
        "Describe a situation where you had to renegotiate deadlines.",
    ],
}


CUSTOMER_FOCUS_QUESTIONS = {
    "easy": [
        "How do you handle customer requests?",
        "Tell me about a time you helped a customer.",
        "How do you respond to difficult customers?",
        "What does good customer service mean to you?",
    ],
    "medium": [
        "Tell me about a difficult customer situation you resolved.",
        "Describe a time you went beyond expectations for a customer.",
        "Tell me about a time you had to balance customer needs with technical constraints.",
        "Describe a situation where you received negative customer feedback.",
    ],
    "hard": [
        "Tell me about a time you had to make a difficult trade-off between customer expectations and business constraints.",
        "Describe how you handled a high-impact customer escalation.",
        "Tell me about a time you changed a product or process based on customer feedback.",
    ],
}


INNOVATION_QUESTIONS = {
    "easy": [
        "Tell me about a new idea you introduced.",
        "How do you identify opportunities for improvement?",
        "Tell me about a process you improved.",
        "How do you encourage innovation?",
    ],
    "medium": [
        "Tell me about a time you introduced a new approach to solve a problem.",
        "Describe an improvement you made to an existing process.",
        "Tell me about an idea that initially faced resistance.",
        "Describe a time you automated a repetitive task.",
    ],
    "hard": [
        "Tell me about an innovation that produced measurable business impact.",
        "Describe a time you challenged a long-standing process.",
        "Tell me about a risky idea you proposed and how you evaluated the risk.",
        "Describe how you convinced others to adopt an unconventional solution.",
    ],
}


LEARNING_QUESTIONS = {
    "easy": [
        "How do you learn new skills?",
        "What is the most recent skill you learned?",
        "Tell me about a time you learned from a mistake.",
        "How do you stay current with technology?",
    ],
    "medium": [
        "Tell me about a skill you had to learn quickly for a project.",
        "Describe a time feedback changed the way you worked.",
        "Tell me about a technical mistake that taught you something important.",
        "Describe how you improved an area where you were initially weak.",
    ],
    "hard": [
        "Tell me about a major professional setback and how it changed your approach.",
        "Describe how you transformed critical feedback into measurable improvement.",
        "Tell me about a time you had to become effective in a completely unfamiliar domain.",
    ],
}


_DECISION_MAKING_QUESTIONS = {
    "easy": [
        "How do you make decisions?",
        "Tell me about a decision you made recently.",
        "What factors do you consider before making an important decision?",
        "How do you handle uncertainty when making decisions?",
    ],
    "medium": [
        "Tell me about a difficult decision you made.",
        "Describe a time when you had limited information but needed to make a decision.",
        "Tell me about a decision that had an unexpected outcome.",
        "Describe how you evaluated different options before making a decision.",
    ],
    "hard": [
        "Tell me about a high-impact decision you made under significant uncertainty.",
        "Describe a time when you had to make a decision that involved substantial risk.",
        "Tell me about a decision you would make differently today.",
        "Describe how you balanced short-term and long-term consequences.",
    ],
}


_INITIATIVE_QUESTIONS = {
    "easy": [
        "Tell me about a time you took initiative.",
        "Describe something you improved without being asked.",
        "Tell me about a time you volunteered for an important task.",
        "How do you identify opportunities to contribute?",
    ],
    "medium": [
        "Tell me about a time you identified a problem and solved it before being asked.",
        "Describe a project you started on your own initiative.",
        "Tell me about a time you took ownership beyond your formal responsibilities.",
        "Describe an improvement you initiated that benefited your team.",
    ],
    "hard": [
        "Tell me about a major initiative you started that created measurable impact.",
        "Describe a time you took initiative despite significant uncertainty or resistance.",
        "Tell me about a time you identified a strategic opportunity before others did.",
    ],
}


# ============================================================================
# Failure & Success
# ============================================================================


FAILURE_QUESTIONS = {
    "easy": [
        "Tell me about a time you failed.",
        "What is a mistake you learned from?",
        "How do you respond when something does not go as planned?",
    ],
    "medium": [
        "Tell me about a project that failed and what you learned.",
        "Describe a time you missed an important goal.",
        "Tell me about a professional failure that changed your approach.",
    ],
    "hard": [
        "Tell me about your biggest professional failure and how you recovered.",
        "Describe a failure that affected other people and how you handled the consequences.",
        "Tell me about a failure where you initially misunderstood the root cause.",
    ],
}


ACHIEVEMENT_QUESTIONS = {
    "easy": [
        "What accomplishment are you most proud of?",
        "Tell me about a successful project you completed.",
        "What achievement demonstrates your strengths?",
    ],
    "medium": [
        "Tell me about an accomplishment that had measurable impact.",
        "Describe a project where you exceeded expectations.",
        "Tell me about a difficult goal you successfully achieved.",
    ],
    "hard": [
        "Tell me about your highest-impact professional achievement.",
        "Describe an achievement that required you to influence others.",
        "Tell me about a result you achieved despite significant constraints.",
    ],
}


# ============================================================================
# Motivation & Career
# ============================================================================


MOTIVATION_QUESTIONS = {
    "easy": [
        "Why are you interested in this role?",
        "What motivates you at work?",
        "What type of work do you enjoy most?",
        "What are your career goals?",
    ],
    "medium": [
        "Why do you want to work for our company?",
        "What type of environment helps you perform your best?",
        "What motivates you when working on repetitive tasks?",
        "What are you looking for in your next role?",
    ],
    "hard": [
        "Why is this role the right next step in your career?",
        "What type of problems do you find most intellectually motivating?",
        "What would make you leave a role even if compensation were attractive?",
        "How do you evaluate whether a job opportunity aligns with your long-term goals?",
    ],
}


STRESS_MANAGEMENT_QUESTIONS = {
    "easy": [
        "How do you handle stress?",
        "How do you stay productive under pressure?",
        "Tell me about a time you worked under a tight deadline.",
    ],
    "medium": [
        "Tell me about a particularly stressful project and how you handled it.",
        "Describe a time when you had several urgent problems at once.",
        "How do you maintain quality when working under pressure?",
    ],
    "hard": [
        "Tell me about a high-pressure situation where the consequences of failure were significant.",
        "Describe how you handled sustained pressure over a long project.",
        "Tell me about a time you had to remain calm while others were under significant stress.",
    ],
}


# ============================================================================
# Remote Work
# ============================================================================


REMOTE_WORK_QUESTIONS = {
    "easy": [
        "How do you stay productive while working remotely?",
        "How do you communicate with remote teammates?",
        "How do you organize your remote workday?",
    ],
    "medium": [
        "Tell me about a successful remote collaboration experience.",
        "How do you handle communication gaps in a remote team?",
        "Tell me about a time you solved a problem without immediate access to your teammates.",
    ],
    "hard": [
        "How would you maintain alignment across a globally distributed team?",
        "Tell me about a complex project you delivered with a distributed team.",
        "How would you prevent communication overhead from slowing a remote organization?",
    ],
}


# ============================================================================
# Competency Registry
# ============================================================================


BEHAVIORAL_QUESTION_BANK = {
    "communication": COMMUNICATION_QUESTIONS,
    "teamwork": TEAMWORK_QUESTIONS,
    "leadership": LEADERSHIP_QUESTIONS,
    "problem solving": PROBLEM_SOLVING_QUESTIONS,
    "problem-solving": PROBLEM_SOLVING_QUESTIONS,
    "conflict": CONFLICT_QUESTIONS,
    "conflict resolution": CONFLICT_QUESTIONS,
    "adaptability": ADAPTABILITY_QUESTIONS,
    "accountability": ACCOUNTABILITY_QUESTIONS,
    "ownership": ACCOUNTABILITY_QUESTIONS,
    "time management": TIME_MANAGEMENT_QUESTIONS,
    "customer focus": CUSTOMER_FOCUS_QUESTIONS,
    "customer service": CUSTOMER_FOCUS_QUESTIONS,
    "innovation": INNOVATION_QUESTIONS,
    "learning": LEARNING_QUESTIONS,
    "growth mindset": LEARNING_QUESTIONS,
    "decision making": _DECISION_MAKING_QUESTIONS,
    "decision-making": _DECISION_MAKING_QUESTIONS,
    "initiative": _INITIATIVE_QUESTIONS,
    "failure": FAILURE_QUESTIONS,
    "achievement": ACHIEVEMENT_QUESTIONS,
    "motivation": MOTIVATION_QUESTIONS,
    "stress management": STRESS_MANAGEMENT_QUESTIONS,
    "pressure management": STRESS_MANAGEMENT_QUESTIONS,
    "remote work": REMOTE_WORK_QUESTIONS,
}


COMPETENCY_ALIASES = {
    "communication skills": "communication",
    "communicating": "communication",
    "team": "teamwork",
    "collaboration": "teamwork",
    "lead": "leadership",
    "leading": "leadership",
    "problem solving skills": "problem solving",
    "problem_solving": "problem solving",
    "conflict resolution": "conflict",
    "adaptable": "adaptability",
    "flexibility": "adaptability",
    "responsibility": "accountability",
    "ownership": "accountability",
    "time-management": "time management",
    "customer-centric": "customer focus",
    "customer centric": "customer focus",
    "creativity": "innovation",
    "continuous learning": "learning",
    "learning ability": "learning",
    "decision": "decision making",
    "decision making skills": "decision making",
    "self motivation": "motivation",
    "work under pressure": "stress management",
    "stress": "stress management",
    "remote": "remote work",
}


# ============================================================================
# Behavioral Question Bank Class
# ============================================================================


class BehavioralQuestionBank:
    """
    Interface for retrieving behavioral interview questions.

    Example:

        bank = BehavioralQuestionBank()

        questions = bank.get_questions(
            competency="leadership",
            difficulty="medium",
            count=5,
        )
    """

    def __init__(
        self,
        question_bank: dict[str, dict[str, list[str]]] | None = None,
    ) -> None:

        self.question_bank = (
            question_bank
            if question_bank is not None
            else BEHAVIORAL_QUESTION_BANK
        )

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_competency(
        competency: str,
    ) -> str:
        """Normalize competency names."""

        value = str(
            competency
        ).strip().lower()

        value = COMPETENCY_ALIASES.get(
            value,
            value,
        )

        return value

    @staticmethod
    def normalize_difficulty(
        difficulty: str,
    ) -> str:
        """Normalize difficulty."""

        value = str(
            difficulty
        ).strip().lower()

        if value not in {
            "easy",
            "medium",
            "hard",
        }:
            return "medium"

        return value

    # ------------------------------------------------------------------
    # Supported Competencies
    # ------------------------------------------------------------------

    def supported_competencies(self) -> list[str]:
        """Return supported behavioral competencies."""

        return sorted(
            self.question_bank.keys()
        )

    def has_competency(
        self,
        competency: str,
    ) -> bool:
        """Check whether a competency is supported."""

        normalized = (
            self.normalize_competency(
                competency
            )
        )

        return normalized in self.question_bank

    # ------------------------------------------------------------------
    # Question Retrieval
    # ------------------------------------------------------------------

    def get_questions(
        self,
        *,
        competency: str,
        difficulty: str = "medium",
        count: int | None = None,
    ) -> list[BehavioralQuestion]:
        """Return behavioral questions."""

        normalized_competency = (
            self.normalize_competency(
                competency
            )
        )

        difficulty = (
            self.normalize_difficulty(
                difficulty
            )
        )

        bank = self.question_bank.get(
            normalized_competency
        )

        if not bank:
            return []

        questions = bank.get(
            difficulty,
            bank.get(
                "medium",
                [],
            ),
        )

        if count is not None:

            count = max(
                0,
                int(count),
            )

            questions = questions[
                :count
            ]

        return [
            BehavioralQuestion(
                question=question,
                competency=normalized_competency,
                difficulty=difficulty,
                tags=(
                    normalized_competency,
                    "behavioral",
                ),
            )
            for question in questions
        ]

    def get_all_questions(
        self,
        *,
        competency: str,
    ) -> list[BehavioralQuestion]:
        """Return all questions for a competency."""

        normalized = (
            self.normalize_competency(
                competency
            )
        )

        bank = self.question_bank.get(
            normalized,
            {},
        )

        result: list[
            BehavioralQuestion
        ] = []

        for difficulty in (
            "easy",
            "medium",
            "hard",
        ):

            for question in bank.get(
                difficulty,
                [],
            ):

                result.append(
                    BehavioralQuestion(
                        question=question,
                        competency=normalized,
                        difficulty=difficulty,
                        tags=(
                            normalized,
                            "behavioral",
                        ),
                    )
                )

        return result

    # ------------------------------------------------------------------
    # Random Question
    # ------------------------------------------------------------------

    def random_question(
        self,
        *,
        competency: str,
        difficulty: str = "medium",
    ) -> BehavioralQuestion | None:
        """Return one random behavioral question."""

        import random

        questions = self.get_questions(
            competency=competency,
            difficulty=difficulty,
        )

        if not questions:
            return None

        return random.choice(
            questions
        )

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        keyword: str,
        *,
        difficulty: str | None = None,
        competency: str | None = None,
    ) -> list[BehavioralQuestion]:
        """Search behavioral questions."""

        keyword = str(
            keyword
        ).strip().lower()

        difficulties = (
            [self.normalize_difficulty(difficulty)]
            if difficulty
            else [
                "easy",
                "medium",
                "hard",
            ]
        )

        competencies = (
            [self.normalize_competency(competency)]
            if competency
            else list(
                self.question_bank.keys()
            )
        )

        results: list[
            BehavioralQuestion
        ] = []

        seen: set[str] = set()

        for current_competency in competencies:

            bank = self.question_bank.get(
                current_competency,
                {},
            )

            for current_difficulty in difficulties:

                for question in bank.get(
                    current_difficulty,
                    [],
                ):

                    if keyword not in question.lower():
                        continue

                    key = question.lower()

                    if key in seen:
                        continue

                    seen.add(key)

                    results.append(
                        BehavioralQuestion(
                            question=question,
                            competency=current_competency,
                            difficulty=current_difficulty,
                            tags=(
                                current_competency,
                                "behavioral",
                            ),
                        )
                    )

        return results

    # ------------------------------------------------------------------
    # Mixed Competencies
    # ------------------------------------------------------------------

    def get_mixed_questions(
        self,
        *,
        competencies: list[str],
        difficulty: str = "medium",
        count: int = 10,
    ) -> list[BehavioralQuestion]:
        """Get questions across multiple competencies."""

        count = max(
            1,
            int(count),
        )

        normalized = []

        for competency in competencies:

            value = (
                self.normalize_competency(
                    competency
                )
            )

            if value not in normalized:
                normalized.append(
                    value
                )

        if not normalized:
            return []

        result: list[
            BehavioralQuestion
        ] = []

        seen: set[str] = set()

        index = 0

        while (
            len(result) < count
            and index < count * 5
        ):

            competency = normalized[
                index
                % len(normalized)
            ]

            index += 1

            question = (
                self.random_question(
                    competency=competency,
                    difficulty=difficulty,
                )
            )

            if question is None:
                continue

            key = question.question.lower()

            if key in seen:
                continue

            seen.add(key)

            result.append(
                question
            )

        return result

    # ------------------------------------------------------------------
    # STAR Follow-Up Questions
    # ------------------------------------------------------------------

    @staticmethod
    def star_follow_up_questions() -> list[str]:
        """
        Return standard STAR-method follow-up questions.
        """

        return [
            "What was the situation?",
            "What was your specific responsibility?",
            "What actions did you personally take?",
            "Why did you choose that approach?",
            "What challenges did you face?",
            "What was the result?",
            "Can you quantify the impact?",
            "What did you learn from the experience?",
            "What would you do differently today?",
        ]

    # ------------------------------------------------------------------
    # Adaptive Difficulty
    # ------------------------------------------------------------------

    def next_difficulty(
        self,
        *,
        current_difficulty: str,
        score: float,
    ) -> str:
        """
        Adjust difficulty based on interview performance.

        Score is expected to be between 0 and 100.
        """

        current = (
            self.normalize_difficulty(
                current_difficulty
            )
        )

        try:
            score = float(
                score
            )
        except (
            TypeError,
            ValueError,
        ):
            return current

        if score >= 85:

            if current == "easy":
                return "medium"

            return "hard"

        if score <= 45:

            if current == "hard":
                return "medium"

            return "easy"

        return current

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    @staticmethod
    def to_dict(
        questions: list[BehavioralQuestion],
    ) -> list[dict[str, Any]]:
        """Serialize questions to dictionaries."""

        return [
            question.to_dict()
            for question in questions
        ]


# ============================================================================
# Convenience API
# ============================================================================


_default_bank = BehavioralQuestionBank()


def get_behavioral_questions(
    competency: str,
    difficulty: str = "medium",
    count: int | None = None,
) -> list[dict[str, Any]]:
    """Return behavioral questions."""

    questions = _default_bank.get_questions(
        competency=competency,
        difficulty=difficulty,
        count=count,
    )

    return _default_bank.to_dict(
        questions
    )


def get_random_behavioral_question(
    competency: str,
    difficulty: str = "medium",
) -> dict[str, Any] | None:
    """Return one random behavioral question."""

    question = _default_bank.random_question(
        competency=competency,
        difficulty=difficulty,
    )

    if question is None:
        return None

    return question.to_dict()


def search_behavioral_questions(
    keyword: str,
    difficulty: str | None = None,
    competency: str | None = None,
) -> list[dict[str, Any]]:
    """Search behavioral questions."""

    questions = _default_bank.search(
        keyword,
        difficulty=difficulty,
        competency=competency,
    )

    return _default_bank.to_dict(
        questions
    )


def get_star_follow_up_questions() -> list[str]:
    """Return STAR follow-up questions."""

    return BehavioralQuestionBank.star_follow_up_questions()


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "BehavioralQuestion",
    "BehavioralQuestionBank",
    "BEHAVIORAL_QUESTION_BANK",
    "COMMUNICATION_QUESTIONS",
    "TEAMWORK_QUESTIONS",
    "LEADERSHIP_QUESTIONS",
    "PROBLEM_SOLVING_QUESTIONS",
    "CONFLICT_QUESTIONS",
    "ADAPTABILITY_QUESTIONS",
    "ACCOUNTABILITY_QUESTIONS",
    "TIME_MANAGEMENT_QUESTIONS",
    "CUSTOMER_FOCUS_QUESTIONS",
    "INNOVATION_QUESTIONS",
    "LEARNING_QUESTIONS",
    "FAILURE_QUESTIONS",
    "ACHIEVEMENT_QUESTIONS",
    "MOTIVATION_QUESTIONS",
    "STRESS_MANAGEMENT_QUESTIONS",
    "REMOTE_WORK_QUESTIONS",
    "get_behavioral_questions",
    "get_random_behavioral_question",
    "search_behavioral_questions",
    "get_star_follow_up_questions",
]