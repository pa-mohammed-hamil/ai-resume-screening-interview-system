"""create audit logs table"""

from alembic import op
import sqlalchemy as sa


# ================================================================
# REVISION IDENTIFIERS
# ================================================================

revision = "007_audit_logs"
down_revision = "006_scores"
branch_labels = None
depends_on = None


# ================================================================
# UPGRADE
# ================================================================

def upgrade() -> None:
    """Create the audit_logs table."""

    op.create_table(
        "audit_logs",

        # Primary key
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),

        # User who performed the action
        # Nullable so logs can remain even if a user is deleted.
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=True,
        ),

        # Action performed
        # Examples:
        # LOGIN, LOGOUT, CREATE_JOB, UPLOAD_RESUME,
        # ANALYZE_RESUME, CREATE_INTERVIEW, DELETE_CANDIDATE
        sa.Column(
            "action",
            sa.String(100),
            nullable=False,
        ),

        # Entity affected by the action
        # Examples: User, Resume, Job, Candidate, Interview
        sa.Column(
            "entity_type",
            sa.String(100),
            nullable=True,
        ),

        # ID of the affected entity
        sa.Column(
            "entity_id",
            sa.Integer(),
            nullable=True,
        ),

        # Human-readable description
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),

        # Request IP address
        # IPv4 max = 15 chars, IPv6 max = 45 chars
        sa.Column(
            "ip_address",
            sa.String(45),
            nullable=True,
        ),

        # Browser / client information
        sa.Column(
            "user_agent",
            sa.String(500),
            nullable=True,
        ),

        # Additional structured information
        #
        # Example:
        # {
        #     "old_status": "new",
        #     "new_status": "shortlisted"
        # }
        sa.Column(
            "metadata",
            sa.JSON(),
            nullable=True,
        ),

        # Timestamp
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),

        # ========================================================
        # FOREIGN KEY
        # ========================================================

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_audit_logs_user_id_users",
            ondelete="SET NULL",
        ),
    )

    # ============================================================
    # INDEXES
    # ============================================================

    op.create_index(
        "ix_audit_logs_user_id",
        "audit_logs",
        ["user_id"],
    )

    op.create_index(
        "ix_audit_logs_action",
        "audit_logs",
        ["action"],
    )

    op.create_index(
        "ix_audit_logs_entity_type",
        "audit_logs",
        ["entity_type"],
    )

    op.create_index(
        "ix_audit_logs_entity_id",
        "audit_logs",
        ["entity_id"],
    )

    op.create_index(
        "ix_audit_logs_created_at",
        "audit_logs",
        ["created_at"],
    )


# ================================================================
# DOWNGRADE
# ================================================================

def downgrade() -> None:
    """Drop the audit_logs table."""

    op.drop_index(
        "ix_audit_logs_created_at",
        table_name="audit_logs",
    )

    op.drop_index(
        "ix_audit_logs_entity_id",
        table_name="audit_logs",
    )

    op.drop_index(
        "ix_audit_logs_entity_type",
        table_name="audit_logs",
    )

    op.drop_index(
        "ix_audit_logs_action",
        table_name="audit_logs",
    )

    op.drop_index(
        "ix_audit_logs_user_id",
        table_name="audit_logs",
    )

    op.drop_table("audit_logs")