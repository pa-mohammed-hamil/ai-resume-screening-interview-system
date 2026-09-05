# backend/app/models/job.py

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Job(Base):
    """
    Job / Job Description model.

    Stores:
    - Job posting information
    - Job description
    - Requirements and responsibilities
    - AI-extracted skills
    - JD analysis results
    - Job status and timestamps
    """

    __tablename__ = "jobs"

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
    # Basic Job Information
    # ------------------------------------------------------------------

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    company_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    department: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
    )

    location: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    employment_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    work_mode: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    experience_level: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Compensation
    # ------------------------------------------------------------------

    salary_min: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    salary_max: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    salary_currency: Mapped[Optional[str]] = mapped_column(
        String(10),
        default="USD",
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Job Description
    # ------------------------------------------------------------------

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    requirements: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    responsibilities: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    qualifications: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    preferred_qualifications: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    benefits: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # AI Extracted Skills
    # ------------------------------------------------------------------

    required_skills: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    preferred_skills: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    technical_skills: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    soft_skills: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # AI / JD Analysis
    # ------------------------------------------------------------------

    jd_analysis: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    keywords: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    must_have_keywords: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    nice_to_have_keywords: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Scoring Configuration
    # ------------------------------------------------------------------

    skill_weight: Mapped[float] = mapped_column(
        default=0.40,
        nullable=False,
    )

    experience_weight: Mapped[float] = mapped_column(
        default=0.25,
        nullable=False,
    )

    education_weight: Mapped[float] = mapped_column(
        default=0.15,
        nullable=False,
    )

    keyword_weight: Mapped[float] = mapped_column(
        default=0.20,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Job Status
    # ------------------------------------------------------------------

    status: Mapped[str] = mapped_column(
        String(50),
        default="draft",
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_analyzed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Application Information
    # ------------------------------------------------------------------

    application_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    application_deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    openings: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
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

    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    analyzed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    user = relationship(
        "User",
        back_populates="jobs",
    )

    # Candidate matching relationship can be added when a
    # CandidateJobMatch model/table is introduced.

    # ------------------------------------------------------------------
    # Helper Properties
    # ------------------------------------------------------------------

    @property
    def salary_range(self) -> Optional[str]:
        """Return a formatted salary range."""

        if self.salary_min is None and self.salary_max is None:
            return None

        if self.salary_min is None:
            return f"{self.salary_currency} {self.salary_max:,.0f}"

        if self.salary_max is None:
            return f"{self.salary_currency} {self.salary_min:,.0f}+"

        return (
            f"{self.salary_currency} "
            f"{self.salary_min:,.0f} - "
            f"{self.salary_max:,.0f}"
        )

    @property
    def is_published(self) -> bool:
        """Return whether the job is published."""

        return self.status == "published"

    @property
    def is_closed(self) -> bool:
        """Return whether the job is closed."""

        return self.status == "closed"

    @property
    def is_draft(self) -> bool:
        """Return whether the job is still a draft."""

        return self.status == "draft"

    @property
    def total_weight(self) -> float:
        """Return the total scoring weight."""

        return (
            self.skill_weight
            + self.experience_weight
            + self.education_weight
            + self.keyword_weight
        )

    def __repr__(self) -> str:
        return (
            f"<Job("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"status='{self.status}', "
            f"is_active={self.is_active}"
            f")>"
        )