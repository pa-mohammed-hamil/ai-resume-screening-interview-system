# Project scaffold file
# backend/app/models/interview.py

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Interview(Base):
    """
    AI interview model.

    Stores:
    - Interview configuration
    - Candidate/job references
    - Interview questions and answers
    - AI evaluation scores
    - Voice interview information
    - Final interview report
    """

    __tablename__ = "interviews"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    # ------------------------------------------------------------------
    # Ownership / References
    # ------------------------------------------------------------------

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    job_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ------------------------------------------------------------------
    # Interview Information
    # ------------------------------------------------------------------

    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    interview_type: Mapped[str] = mapped_column(
        String(50),
        default="technical",
        nullable=False,
    )

    mode: Mapped[str] = mapped_column(
        String(50),
        default="text",
        nullable=False,
    )

    difficulty: Mapped[str] = mapped_column(
        String(50),
        default="medium",
        nullable=False,
    )

    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Interview Configuration
    # ------------------------------------------------------------------

    total_questions: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False,
    )

    current_question: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    questions: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    interview_config: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    focus_areas: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Answers
    # ------------------------------------------------------------------

    answers: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    answered_questions: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # AI Evaluation Scores
    # ------------------------------------------------------------------

    overall_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        index=True,
    )

    technical_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    communication_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    confidence_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    problem_solving_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    behavioral_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Evaluation Results
    # ------------------------------------------------------------------

    evaluation: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    strengths: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    weaknesses: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    recommendations: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    question_scores: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Voice Interview
    # ------------------------------------------------------------------

    audio_file_path: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    transcript: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    voice_analysis: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    speech_rate: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    confidence_level: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Final Report
    # ------------------------------------------------------------------

    report_data: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    report_file_path: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    hiring_recommendation: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    recruiter_feedback: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    status: Mapped[str] = mapped_column(
        String(50),
        default="scheduled",
        nullable=False,
        index=True,
    )

    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_evaluated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Scheduling
    # ------------------------------------------------------------------

    scheduled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    evaluated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Timestamps
    # ------------------------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    user = relationship(
        "User",
        back_populates="interviews",
    )

    candidate = relationship(
        "Candidate",
        back_populates="interviews",
    )

    job = relationship(
        "Job",
        foreign_keys=[job_id],
    )

    # ------------------------------------------------------------------
    # Helper Properties
    # ------------------------------------------------------------------

    @property
    def progress_percentage(self) -> float:
        """Return interview completion percentage."""

        if self.total_questions <= 0:
            return 0.0

        progress = (
            self.answered_questions
            / self.total_questions
        ) * 100

        return min(progress, 100.0)

    @property
    def is_in_progress(self) -> bool:
        """Return whether the interview is currently running."""

        return self.status == "in_progress"

    @property
    def is_pending(self) -> bool:
        """Return whether the interview has not started."""

        return self.status == "scheduled"

    @property
    def is_cancelled(self) -> bool:
        """Return whether the interview was cancelled."""

        return self.status == "cancelled"

    @property
    def score_label(self) -> str:
        """Return a human-readable interview score."""

        if self.overall_score is None:
            return "Not Evaluated"

        if self.overall_score >= 80:
            return "Excellent"

        if self.overall_score >= 65:
            return "Good"

        if self.overall_score >= 50:
            return "Average"

        return "Needs Improvement"

    def __repr__(self) -> str:
        return (
            f"<Interview("
            f"id={self.id}, "
            f"candidate_id={self.candidate_id}, "
            f"type='{self.interview_type}', "
            f"status='{self.status}', "
            f"overall_score={self.overall_score}"
            f")>"
        )