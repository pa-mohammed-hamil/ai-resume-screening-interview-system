# backend/app/models/user.py

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class User(Base):
    """
    User model for recruiters, administrators, and other system users.
    """

    __tablename__ = "users"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    # ------------------------------------------------------------------
    # Account Information
    # ------------------------------------------------------------------

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Profile Information
    # ------------------------------------------------------------------

    first_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    last_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    phone: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True,
    )

    company_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    job_title: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
    )

    avatar_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Authorization
    # ------------------------------------------------------------------

    role: Mapped[str] = mapped_column(
        String(50),
        default="recruiter",
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Account Security
    # ------------------------------------------------------------------

    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    password_changed_at: Mapped[Optional[datetime]] = mapped_column(
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

    resumes = relationship(
        "Resume",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    jobs = relationship(
        "Job",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    candidates = relationship(
        "Candidate",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    interviews = relationship(
        "Interview",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def full_name(self) -> str:
        """Return the user's full name."""
        name = " ".join(
            part
            for part in [self.first_name, self.last_name]
            if part
        )

        return name or self.email

    def __repr__(self) -> str:
        return (
            f"<User("
            f"id={self.id}, "
            f"email='{self.email}', "
            f"role='{self.role}', "
            f"is_active={self.is_active}"
            f")>"
        )