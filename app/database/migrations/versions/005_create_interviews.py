# Project scaffold file
"""create interviews table"""

from alembic import op
import sqlalchemy as sa


# ================================================================
# REVISION IDENTIFIERS
# ================================================================

revision = "005_interviews"
down_revision = "004_candidates"
branch_labels = None
depends_on = None


# ================================================================
# UPGRADE
# ================================================================

def upgrade() -> None:
    """Create the interviews table."""

    op.create_table(
        "interviews",

        # Primary key
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),

        # Recruiter / owner
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),

        # Candidate being interviewed
        sa.Column(
            "candidate_id",
            sa.Integer(),
            nullable=False,
        ),

        # Related job
        sa.Column(
            "job_id",
            sa.Integer(),
            nullable=True,
        ),

        # Interview type
        # technical / behavioral / mixed / screening
        sa.Column(
            "interview_type",
            sa.String(50),
            nullable=False,
            server_default="technical",
        ),

        # Interview status
        # scheduled / in_progress / completed / cancelled
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="scheduled",
        ),

        # Interview scheduling
        sa.Column(
            "scheduled_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        # Interview lifecycle timestamps
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        # Duration in seconds
        sa.Column(
            "duration_seconds",
            sa.Integer(),
            nullable=True,
        ),

        # AI-generated overall interview score
        sa.Column(
            "overall_score",
            sa.Float(),
            nullable=True,
        ),

        # Generated interview report
        sa.Column(
            "report_path",
            sa.String(500),
            nullable=True,
        ),

        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),

        # ========================================================
        # FOREIGN KEYS
        # ========================================================

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_interviews_user_id_users",
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["candidate_id"],
            ["candidates.id"],
            name="fk_interviews_candidate_id_candidates",
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["job_id"],
            ["jobs.id"],
            name="fk_interviews_job_id_jobs",
            ondelete="SET NULL",
        ),
    )

    # ============================================================
    # INDEXES
    # ============================================================

    op.create_index(
        "ix_interviews_user_id",
        "interviews",
        ["user_id"],
    )

    op.create_index(
        "ix_interviews_candidate_id",
        "interviews",
        ["candidate_id"],
    )

    op.create_index(
        "ix_interviews_job_id",
        "interviews",
        ["job_id"],
    )

    op.create_index(
        "ix_interviews_status",
        "interviews",
        ["status"],
    )

    op.create_index(
        "ix_interviews_scheduled_at",
        "interviews",
        ["scheduled_at"],
    )

    op.create_index(
        "ix_interviews_overall_score",
        "interviews",
        ["overall_score"],
    )


# ================================================================
# DOWNGRADE
# ================================================================

def downgrade() -> None:
    """Drop the interviews table."""

    op.drop_index(
        "ix_interviews_overall_score",
        table_name="interviews",
    )

    op.drop_index(
        "ix_interviews_scheduled_at",
        table_name="interviews",
    )

    op.drop_index(
        "ix_interviews_status",
        table_name="interviews",
    )

    op.drop_index(
        "ix_interviews_job_id",
        table_name="interviews",
    )

    op.drop_index(
        "ix_interviews_candidate_id",
        table_name="interviews",
    )

    op.drop_index(
        "ix_interviews_user_id",
        table_name="interviews",
    )

    op.drop_table("interviews")