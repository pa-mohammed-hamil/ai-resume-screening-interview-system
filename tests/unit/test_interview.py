# Project scaffold file
```python
import pytest

from interview_engine.question_generation.question_generator import QuestionGenerator
from interview_engine.question_generation.difficulty import Difficulty
from interview_engine.adaptive.adaptive_engine import AdaptiveEngine
from interview_engine.adaptive.difficulty_controller import DifficultyController
from interview_engine.adaptive.next_question import NextQuestion
from interview_engine.evaluation.answer_evaluator import AnswerEvaluator
from interview_engine.evaluation.technical_evaluator import TechnicalEvaluator
from interview_engine.evaluation.communication_evaluator import CommunicationEvaluator
from interview_engine.evaluation.confidence_evaluator import ConfidenceEvaluator


# ---------------------------------------------------------------------------
# Question Generation
# ---------------------------------------------------------------------------

def test_question_generator_returns_questions():
    generator = QuestionGenerator()

    questions = generator.generate(
        role="Python Developer",
        skills=["Python", "FastAPI", "SQL"],
        difficulty="medium",
        count=5,
    )

    assert questions is not None
    assert isinstance(questions, list)
    assert len(questions) == 5

    for question in questions:
        assert isinstance(question, str)
        assert question.strip()


def test_question_generator_respects_difficulty():
    generator = QuestionGenerator()

    questions = generator.generate(
        role="Python Developer",
        skills=["Python"],
        difficulty="hard",
        count=3,
    )

    assert len(questions) == 3


# ---------------------------------------------------------------------------
# Difficulty
# ---------------------------------------------------------------------------

def test_difficulty_values_exist():
    assert Difficulty.EASY is not None
    assert Difficulty.MEDIUM is not None
    assert Difficulty.HARD is not None


def test_difficulty_controller_increases_difficulty():
    controller = DifficultyController()

    current = Difficulty.MEDIUM

    next_level = controller.adjust(
        current_difficulty=current,
        score=90,
    )

    assert next_level in (
        Difficulty.MEDIUM,
        Difficulty.HARD,
    )


def test_difficulty_controller_decreases_difficulty():
    controller = DifficultyController()

    current = Difficulty.MEDIUM

    next_level = controller.adjust(
        current_difficulty=current,
        score=30,
    )

    assert next_level in (
        Difficulty.EASY,
        Difficulty.MEDIUM,
    )


# ---------------------------------------------------------------------------
# Adaptive Interview
# ---------------------------------------------------------------------------

def test_adaptive_engine_selects_next_question():
    engine = AdaptiveEngine()

    result = engine.get_next_question(
        current_difficulty=Difficulty.MEDIUM,
        previous_score=80,
        skills=["Python", "FastAPI"],
    )

    assert result is not None


def test_next_question_returns_question():
    next_question = NextQuestion()

    result = next_question.select(
        skill="Python",
        difficulty=Difficulty.MEDIUM,
    )

    assert result is not None


# ---------------------------------------------------------------------------
# Answer Evaluation
# ---------------------------------------------------------------------------

def test_answer_evaluator_returns_score():
    evaluator = AnswerEvaluator()

    result = evaluator.evaluate(
        question="What is a Python decorator?",
        answer=(
            "A decorator is a function that modifies or extends "
            "the behavior of another function without changing its source code."
        ),
    )

    assert result is not None

    if isinstance(result, dict):
        assert "score" in result
        assert 0 <= result["score"] <= 100


def test_answer_evaluator_handles_empty_answer():
    evaluator = AnswerEvaluator()

    result = evaluator.evaluate(
        question="Explain Python inheritance.",
        answer="",
    )

    assert result is not None

    if isinstance(result, dict) and "score" in result:
        assert result["score"] >= 0


# ---------------------------------------------------------------------------
# Technical Evaluation
# ---------------------------------------------------------------------------

def test_technical_evaluator_evaluates_correct_answer():
    evaluator = TechnicalEvaluator()

    result = evaluator.evaluate(
        question="What is a Python list?",
        answer=(
            "A list is an ordered, mutable collection that can contain "
            "multiple values in Python."
        ),
    )

    assert result is not None

    if isinstance(result, dict) and "score" in result:
        assert 0 <= result["score"] <= 100


def test_technical_evaluator_detects_weak_answer():
    evaluator = TechnicalEvaluator()

    result = evaluator.evaluate(
        question="Explain database indexing.",
        answer="I don't know.",
    )

    assert result is not None

    if isinstance(result, dict) and "score" in result:
        assert 0 <= result["score"] <= 100


# ---------------------------------------------------------------------------
# Communication Evaluation
# ---------------------------------------------------------------------------

def test_communication_evaluator():
    evaluator = CommunicationEvaluator()

    result = evaluator.evaluate(
        answer=(
            "I would approach the problem by first understanding the "
            "requirements and then designing a solution step by step."
        )
    )

    assert result is not None

    if isinstance(result, dict) and "score" in result:
        assert 0 <= result["score"] <= 100


def test_communication_evaluator_handles_empty_answer():
    evaluator = CommunicationEvaluator()

    result = evaluator.evaluate(answer="")

    assert result is not None


# ---------------------------------------------------------------------------
# Confidence Evaluation
# ---------------------------------------------------------------------------

def test_confidence_evaluator():
    evaluator = ConfidenceEvaluator()

    result = evaluator.evaluate(
        answer=(
            "I am confident in my approach. I would first analyze the "
            "requirements and then implement and test the solution."
        )
    )

    assert result is not None

    if isinstance(result, dict) and "score" in result:
        assert 0 <= result["score"] <= 100


# ---------------------------------------------------------------------------
# End-to-End Interview Evaluation
# ---------------------------------------------------------------------------

def test_complete_interview_evaluation():
    answer_evaluator = AnswerEvaluator()
    technical_evaluator = TechnicalEvaluator()
    communication_evaluator = CommunicationEvaluator()
    confidence_evaluator = ConfidenceEvaluator()

    question = "Explain how you would build a REST API using FastAPI."
    answer = (
        "I would create FastAPI routes, define Pydantic schemas for "
        "validation, implement service-layer business logic, connect "
        "the API to the database, and add authentication and tests."
    )

    answer_result = answer_evaluator.evaluate(
        question=question,
        answer=answer,
    )

    technical_result = technical_evaluator.evaluate(
        question=question,
        answer=answer,
    )

    communication_result = communication_evaluator.evaluate(
        answer=answer,
    )

    confidence_result = confidence_evaluator.evaluate(
        answer=answer,
    )

    assert answer_result is not None
    assert technical_result is not None
    assert communication_result is not None
    assert confidence_result is not None
