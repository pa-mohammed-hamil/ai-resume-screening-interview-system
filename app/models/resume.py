# backend/app/models/resume.py

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


class Resume(Base):
    """
    Resume uploaded and analyzed by the system.

    Stores:
    - Original resume metadata
    - Extracted resume content
    - AI analysis results
    - ATS/skill scores
    - Processing status
    """

    __tablename__ = "resumes"

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
    # File Information
    # ------------------------------------------------------------------

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    original_filename: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    file_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    file_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    file_size: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Resume Information
    # ------------------------------------------------------------------

    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    candidate_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    candidate_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    candidate_phone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    location: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    raw_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Extracted Information
    # ------------------------------------------------------------------

    skills: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    education: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    experience: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    certifications: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    projects: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    languages: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # AI / ATS Analysis
    # ------------------------------------------------------------------

    ats_score: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    skill_score: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    experience_score: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    education_score: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )

    overall_score: Mapped[Optional[float]] = mapped_column(
        nullable=True,
        index=True,
    )

    # ------------------------------------------------------------------
    # AI Analysis Results
    # ------------------------------------------------------------------

    analysis: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    missing_skills: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    matched_skills: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    recommendations: Mapped[Optional[list[Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Processing Status
    # ------------------------------------------------------------------

    status: Mapped[str] = mapped_column(
        String(50),
        default="uploaded",
        nullable=False,
        index=True,
    )

    processing_error: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    is_analyzed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Versioning
    # ------------------------------------------------------------------

    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
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

    analyzed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    user = relationship(
        "User",
        back_populates="resumes",
    )

    # Candidate relationship can be enabled when candidate.py
    # contains the corresponding resume_id foreign key.
    #
    # candidate = relationship(
    #     "Candidate",
    #     back_populates="resume",
    #     uselist=False,
    # )

    # ------------------------------------------------------------------
    # Helper Properties
    # ------------------------------------------------------------------

    @property
    def display_name(self) -> str:
        """Return the best available resume display name."""
        return (
            self.candidate_name
            or self.title
            or self.original_filename
            or self.filename
        )

    @property
    def is_processing(self) -> bool:
        """Return True when resume processing is in progress."""
        return self.status in {
            "uploaded",
            "processing",
            "parsing",
            "analyzing",
        }

    @property
    def is_completed(self) -> bool:
        """Return True when resume processing is complete."""
        return self.status == "completed"

    @property
    def is_failed(self) -> bool:
        """Return True when resume processing failed."""
        return self.status == "failed"

    def __repr__(self) -> str:
        return (
            f"<Resume("
            f"id={self.id}, "
            f"filename='{self.filename}', "
            f"status='{self.status}', "
            f"overall_score={self.overall_score}"
            f")>"
        )