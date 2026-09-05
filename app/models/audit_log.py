# backend/app/models/audit_log.py

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AuditLog(Base):
    """
    Audit log model.

    Records important user and system actions such as:
    - Login / logout
    - Resume upload / deletion
    - Job creation / update / deletion
    - Candidate status changes
    - Interview actions
    - AI analysis
    - Settings/security changes
    - Administrative operations
    """

    __tablename__ = "audit_logs"

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
    # User Information
    # ------------------------------------------------------------------

    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ------------------------------------------------------------------
    # Action Information
    # ------------------------------------------------------------------

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    resource_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    resource_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Change Information
    # ------------------------------------------------------------------

    old_values: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    new_values: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Request Information
    # ------------------------------------------------------------------

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
    )

    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    request_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    endpoint: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    http_method: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Result Information
    # ------------------------------------------------------------------

    status: Mapped[str] = mapped_column(
        String(50),
        default="success",
        nullable=False,
        index=True,
    )

    status_code: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
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
    # Relationship
    # ------------------------------------------------------------------

    user = relationship(
        "User",
        back_populates="audit_logs",
    )

    # ------------------------------------------------------------------
    # Helper Properties
    # ------------------------------------------------------------------

    @property
    def is_success(self) -> bool:
        """Return whether the audited operation succeeded."""

        return self.status == "success"

    @property
    def is_failure(self) -> bool:
        """Return whether the audited operation failed."""

        return self.status in {
            "failed",
            "error",
        }

    @property
    def resource_reference(self) -> Optional[str]:
        """Return a readable resource reference."""

        if not self.resource_type:
            return None

        if self.resource_id:
            return f"{self.resource_type}:{self.resource_id}"

        return self.resource_type

    def __repr__(self) -> str:
        return (
            f"<AuditLog("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"action='{self.action}', "
            f"resource='{self.resource_reference}', "
            f"status='{self.status}'"
            f")>"
        )