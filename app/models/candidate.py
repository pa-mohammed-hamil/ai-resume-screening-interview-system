# backend/app/models/candidate.py

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


class Candidate(Base):
    """
    Candidate model.

    Represents a candidate created from a resume and associated
    with a recruiter/job.

    Stores:
    - Candidate profile information
    - Resume relationship
    - Job relationship
    - AI matching and ranking scores
    - Skill-gap analysis
    - Recruitment status
    """

    __tablename__ = "candidates"

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
    # Ownership
    # ------------------------------------------------------------------

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Resume / Job References
    # ------------------------------------------------------------------

    resume_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("resumes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    job_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ------------------------------------------------------------------
    # Candidate Identity
    # ------------------------------------------------------------------

    first_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    last_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    phone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    location: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    linkedin_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    github_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    portfolio_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Professional Information
    # ------------------------------------------------------------------

    current_title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    current_company: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    total_experience_years: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    highest_education: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    skills: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    experience: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    education: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    certifications: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Matching Scores
    # ------------------------------------------------------------------

    match_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        index=True,
    )

    semantic_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    keyword_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    skill_match_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    experience_match_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    education_match_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Ranking
    # ------------------------------------------------------------------

    ranking_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        index=True,
    )

    rank: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    ranking_explanation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    ranking_features: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Skill Gap
    # ------------------------------------------------------------------

    matched_skills: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    missing_skills: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    skill_gap_analysis: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # AI Candidate Analysis
    # ------------------------------------------------------------------

    ai_summary: Mapped[Optional[str]] = mapped_column(
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

    # ------------------------------------------------------------------
    # Recruitment Status
    # ------------------------------------------------------------------

    status: Mapped[str] = mapped_column(
        String(50),
        default="new",
        nullable=False,
        index=True,
    )

    is_shortlisted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_rejected: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_hired: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Recruiter Notes
    # ------------------------------------------------------------------

    recruiter_notes: Mapped[Optional[str]] = mapped_column(
        Text,
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

    shortlisted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    rejected_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    hired_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    user = relationship(
        "User",
        back_populates="candidates",
    )

    resume = relationship(
        "Resume",
        foreign_keys=[resume_id],
    )

    job = relationship(
        "Job",
        foreign_keys=[job_id],
    )

    interviews = relationship(
        "Interview",
        back_populates="candidate",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ------------------------------------------------------------------
    # Helper Properties
    # ------------------------------------------------------------------

    @property
    def full_name(self) -> str:
        """Return candidate's full name."""

        name = " ".join(
            part
            for part in [self.first_name, self.last_name]
            if part
        )

        return name or self.email or "Unknown Candidate"

    @property
    def is_active(self) -> bool:
        """Return whether the candidate is still active."""

        return not self.is_rejected and self.status not in {
            "rejected",
            "withdrawn",
        }

    @property
    def has_match_score(self) -> bool:
        """Return whether the candidate has been matched."""

        return self.match_score is not None

    @property
    def has_skill_gap(self) -> bool:
        """Return whether missing skills were identified."""

        return bool(self.missing_skills)

    @property
    def score_label(self) -> str:
        """Return a human-readable score category."""

        if self.match_score is None:
            return "Not Scored"

        if self.match_score >= 80:
            return "Excellent Match"

        if self.match_score >= 65:
            return "Good Match"

        if self.match_score >= 50:
            return "Moderate Match"

        return "Low Match"

    def __repr__(self) -> str:
        return (
            f"<Candidate("
            f"id={self.id}, "
            f"name='{self.full_name}', "
            f"status='{self.status}', "
            f"match_score={self.match_score}, "
            f"rank={self.rank}"
            f")>"
        )