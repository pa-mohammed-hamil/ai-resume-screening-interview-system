# Project scaffold file
"""create candidates table"""

from alembic import op
import sqlalchemy as sa


# ================================================================
# REVISION IDENTIFIERS
# ================================================================

revision = "004_candidates"
down_revision = "003_resumes"
branch_labels = None
depends_on = None


# ================================================================
# UPGRADE
# ================================================================

def upgrade() -> None:
    """Create the candidates table."""

    op.create_table(
        "candidates",

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

        # Job being applied for
        sa.Column(
            "job_id",
            sa.Integer(),
            nullable=True,
        ),

        # Candidate information
        sa.Column(
            "name",
            sa.String(255),
            nullable=False,
        ),

        sa.Column(
            "email",
            sa.String(255),
            nullable=True,
        ),

        sa.Column(
            "phone",
            sa.String(50),
            nullable=True,
        ),

        # Candidate pipeline status
        # new / screening / shortlisted / interview /
        # selected / rejected
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="new",
        ),

        # AI-generated scores
        sa.Column(
            "match_score",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "skill_score",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "experience_score",
            sa.Float(),
            nullable=True,
        ),

        # AI ranking position
        sa.Column(
            "ranking",
            sa.Integer(),
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

        # User relationship
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_candidates_user_id_users",
            ondelete="CASCADE",
        ),

        # Job relationship
        sa.ForeignKeyConstraint(
            ["job_id"],
            ["jobs.id"],
            name="fk_candidates_job_id_jobs",
            ondelete="SET NULL",
        ),
    )

    # ============================================================
    # INDEXES
    # ============================================================

    op.create_index(
        "ix_candidates_user_id",
        "candidates",
        ["user_id"],
    )

    op.create_index(
        "ix_candidates_job_id",
        "candidates",
        ["job_id"],
    )

    op.create_index(
        "ix_candidates_email",
        "candidates",
        ["email"],
    )

    op.create_index(
        "ix_candidates_status",
        "candidates",
        ["status"],
    )

    op.create_index(
        "ix_candidates_match_score",
        "candidates",
        ["match_score"],
    )

    op.create_index(
        "ix_candidates_ranking",
        "candidates",
        ["ranking"],
    )


# ================================================================
# DOWNGRADE
# ================================================================

def downgrade() -> None:
    """Drop the candidates table."""

    op.drop_index(
        "ix_candidates_ranking",
        table_name="candidates",
    )

    op.drop_index(
        "ix_candidates_match_score",
        table_name="candidates",
    )

    op.drop_index(
        "ix_candidates_status",
        table_name="candidates",
    )

    op.drop_index(
        "ix_candidates_email",
        table_name="candidates",
    )

    op.drop_index(
        "ix_candidates_job_id",
        table_name="candidates",
    )

    op.drop_index(
        "ix_candidates_user_id",
        table_name="candidates",
    )

    op.drop_table("candidates")