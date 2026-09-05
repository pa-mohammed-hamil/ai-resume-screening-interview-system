"""create jobs table"""

from alembic import op
import sqlalchemy as sa


# ================================================================
# REVISION IDENTIFIERS
# ================================================================

revision = "002_jobs"
down_revision = "001_users"
branch_labels = None
depends_on = None


# ================================================================
# UPGRADE
# ================================================================

def upgrade() -> None:
    """Create the jobs table."""

    op.create_table(
        "jobs",

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

        # Job information
        sa.Column(
            "title",
            sa.String(255),
            nullable=False,
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),

        # AI-extracted job requirements
        sa.Column(
            "requirements",
            sa.Text(),
            nullable=True,
        ),

        # Job responsibilities
        sa.Column(
            "responsibilities",
            sa.Text(),
            nullable=True,
        ),

        # Job location
        sa.Column(
            "location",
            sa.String(255),
            nullable=True,
        ),

        # Full-time / Part-time / Contract / Internship
        sa.Column(
            "employment_type",
            sa.String(50),
            nullable=True,
        ),

        # draft / active / closed / archived
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="draft",
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

        # Relationship with users
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_jobs_user_id_users",
            ondelete="CASCADE",
        ),
    )

    # ============================================================
    # INDEXES
    # ============================================================

    op.create_index(
        "ix_jobs_user_id",
        "jobs",
        ["user_id"],
    )

    op.create_index(
        "ix_jobs_status",
        "jobs",
        ["status"],
    )

    op.create_index(
        "ix_jobs_title",
        "jobs",
        ["title"],
    )


# ================================================================
# DOWNGRADE
# ================================================================

def downgrade() -> None:
    """Drop the jobs table."""

    op.drop_index(
        "ix_jobs_title",
        table_name="jobs",
    )

    op.drop_index(
        "ix_jobs_status",
        table_name="jobs",
    )

    op.drop_index(
        "ix_jobs_user_id",
        table_name="jobs",
    )

    op.drop_table("jobs")