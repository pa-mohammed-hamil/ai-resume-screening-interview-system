# Project scaffold file
"""create scores table"""

from alembic import op
import sqlalchemy as sa


# ================================================================
# REVISION IDENTIFIERS
# ================================================================

revision = "006_scores"
down_revision = "005_interviews"
branch_labels = None
depends_on = None


# ================================================================
# UPGRADE
# ================================================================

def upgrade() -> None:
    """Create the scores table."""

    op.create_table(
        "scores",

        # Primary key
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),

        # Candidate being scored
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

        # Related resume
        sa.Column(
            "resume_id",
            sa.Integer(),
            nullable=True,
        ),

        # Related interview
        sa.Column(
            "interview_id",
            sa.Integer(),
            nullable=True,
        ),

        # ========================================================
        # AI / ATS SCORES
        # ========================================================

        # Resume ATS compatibility score
        sa.Column(
            "ats_score",
            sa.Float(),
            nullable=True,
        ),

        # Skills matching score
        sa.Column(
            "skill_score",
            sa.Float(),
            nullable=True,
        ),

        # Experience matching score
        sa.Column(
            "experience_score",
            sa.Float(),
            nullable=True,
        ),

        # Education matching score
        sa.Column(
            "education_score",
            sa.Float(),
            nullable=True,
        ),

        # Semantic similarity score
        sa.Column(
            "semantic_score",
            sa.Float(),
            nullable=True,
        ),

        # Overall candidate score
        sa.Column(
            "overall_score",
            sa.Float(),
            nullable=True,
        ),

        # AI explanation of the score
        sa.Column(
            "explanation",
            sa.Text(),
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
        # FOREIGN KEYS
        # ========================================================

        sa.ForeignKeyConstraint(
            ["candidate_id"],
            ["candidates.id"],
            name="fk_scores_candidate_id_candidates",
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["job_id"],
            ["jobs.id"],
            name="fk_scores_job_id_jobs",
            ondelete="SET NULL",
        ),

        sa.ForeignKeyConstraint(
            ["resume_id"],
            ["resumes.id"],
            name="fk_scores_resume_id_resumes",
            ondelete="SET NULL",
        ),

        sa.ForeignKeyConstraint(
            ["interview_id"],
            ["interviews.id"],
            name="fk_scores_interview_id_interviews",
            ondelete="SET NULL",
        ),
    )

    # ============================================================
    # INDEXES
    # ============================================================

    op.create_index(
        "ix_scores_candidate_id",
        "scores",
        ["candidate_id"],
    )

    op.create_index(
        "ix_scores_job_id",
        "scores",
        ["job_id"],
    )

    op.create_index(
        "ix_scores_resume_id",
        "scores",
        ["resume_id"],
    )

    op.create_index(
        "ix_scores_interview_id",
        "scores",
        ["interview_id"],
    )

    op.create_index(
        "ix_scores_overall_score",
        "scores",
        ["overall_score"],
    )

    op.create_index(
        "ix_scores_ats_score",
        "scores",
        ["ats_score"],
    )


# ================================================================
# DOWNGRADE
# ================================================================

def downgrade() -> None:
    """Drop the scores table."""

    op.drop_index(
        "ix_scores_ats_score",
        table_name="scores",
    )

    op.drop_index(
        "ix_scores_overall_score",
        table_name="scores",
    )

    op.drop_index(
        "ix_scores_interview_id",
        table_name="scores",
    )

    op.drop_index(
        "ix_scores_resume_id",
        table_name="scores",
    )

    op.drop_index(
        "ix_scores_job_id",
        table_name="scores",
    )

    op.drop_index(
        "ix_scores_candidate_id",
        table_name="scores",
    )

    op.drop_table("scores")