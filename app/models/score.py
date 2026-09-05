# backend/app/models/score.py

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Score(Base):
    """
    Stores AI-generated scores for resumes, candidates, jobs,
    and interviews.

    A Score represents one scoring event/category and can store
    both the numerical score and the explanation/features used
    to produce it.
    """

    __tablename__ = "scores"

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
    # References
    # ------------------------------------------------------------------

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    resume_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    candidate_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    job_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    interview_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # ------------------------------------------------------------------
    # Score Information
    # ------------------------------------------------------------------

    score_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    max_score: Mapped[float] = mapped_column(
        Float,
        default=100.0,
        nullable=False,
    )

    percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    grade: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Score Details
    # ------------------------------------------------------------------

    explanation: Mapped[Optional[str]] = mapped_column(
        Text,
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

    features: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # AI Model Information
    # ------------------------------------------------------------------

    model_name: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
    )

    model_version: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    scoring_version: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Timestamp
    # ------------------------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    user = relationship(
        "User",
        foreign_keys=[user_id],
    )

    resume = relationship(
        "Resume",
        foreign_keys=[resume_id],
    )

    candidate = relationship(
        "Candidate",
        foreign_keys=[candidate_id],
    )

    job = relationship(
        "Job",
        foreign_keys=[job_id],
    )

    interview = relationship(
        "Interview",
        foreign_keys=[interview_id],
    )

    # ------------------------------------------------------------------
    # Helper Properties
    # ------------------------------------------------------------------

    @property
    def normalized_score(self) -> float:
        """
        Return score normalized to a 0-100 scale.
        """

        if self.max_score <= 0:
            return 0.0

        value = (self.score / self.max_score) * 100

        return round(min(max(value, 0.0), 100.0), 2)

    @property
    def score_label(self) -> str:
        """
        Return a human-readable score label.
        """

        percentage = self.percentage

        if percentage >= 80:
            return "Excellent"

        if percentage >= 65:
            return "Good"

        if percentage >= 50:
            return "Average"

        return "Needs Improvement"

    def __repr__(self) -> str:
        return (
            f"<Score("
            f"id={self.id}, "
            f"type='{self.score_type}', "
            f"score={self.score}, "
            f"percentage={self.percentage}"
            f")>"
        )