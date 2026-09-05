# Project scaffold file
"""add performance indexes"""

from alembic import op


# ================================================================
# REVISION IDENTIFIERS
# ================================================================

revision = "008_add_indexes"
down_revision = "007_audit_logs"
branch_labels = None
depends_on = None


# ================================================================
# UPGRADE
# ================================================================

def upgrade() -> None:
    """Add additional indexes for frequently queried fields."""

    # ============================================================
    # JOBS
    # ============================================================

    op.create_index(
        "ix_jobs_created_at",
        "jobs",
        ["created_at"],
    )

    op.create_index(
        "ix_jobs_employment_type",
        "jobs",
        ["employment_type"],
    )

    # ============================================================
    # RESUMES
    # ============================================================

    op.create_index(
        "ix_resumes_file_name",
        "resumes",
        ["file_name"],
    )

    op.create_index(
        "ix_resumes_created_at",
        "resumes",
        ["created_at"],
    )

    # ============================================================
    # CANDIDATES
    # ============================================================

    op.create_index(
        "ix_candidates_created_at",
        "candidates",
        ["created_at"],
    )

    op.create_index(
        "ix_candidates_experience_score",
        "candidates",
        ["experience_score"],
    )

    # Composite index for job candidate ranking/filtering
    op.create_index(
        "ix_candidates_job_status",
        "candidates",
        ["job_id", "status"],
    )

    # Composite index for ranking candidates within a job
    op.create_index(
        "ix_candidates_job_ranking",
        "candidates",
        ["job_id", "ranking"],
    )

    # ============================================================
    # INTERVIEWS
    # ============================================================

    op.create_index(
        "ix_interviews_created_at",
        "interviews",
        ["created_at"],
    )

    op.create_index(
        "ix_interviews_interview_type",
        "interviews",
        ["interview_type"],
    )

    # Useful for upcoming interview queries
    op.create_index(
        "ix_interviews_status_scheduled",
        "interviews",
        ["status", "scheduled_at"],
    )

    # ============================================================
    # SCORES
    # ============================================================

    op.create_index(
        "ix_scores_created_at",
        "scores",
        ["created_at"],
    )

    op.create_index(
        "ix_scores_skill_score",
        "scores",
        ["skill_score"],
    )

    op.create_index(
        "ix_scores_semantic_score",
        "scores",
        ["semantic_score"],
    )

    # Useful for candidate/job score lookups
    op.create_index(
        "ix_scores_candidate_job",
        "scores",
        ["candidate_id", "job_id"],
    )

    # ============================================================
    # AUDIT LOGS
    # ============================================================

    op.create_index(
        "ix_audit_logs_entity",
        "audit_logs",
        ["entity_type", "entity_id"],
    )

    # Useful for chronological user activity queries
    op.create_index(
        "ix_audit_logs_user_created",
        "audit_logs",
        ["user_id", "created_at"],
    )


# ================================================================
# DOWNGRADE
# ================================================================

def downgrade() -> None:
    """Remove performance indexes."""

    # Audit logs
    op.drop_index(
        "ix_audit_logs_user_created",
        table_name="audit_logs",
    )

    op.drop_index(
        "ix_audit_logs_entity",
        table_name="audit_logs",
    )

    # Scores
    op.drop_index(
        "ix_scores_candidate_job",
        table_name="scores",
    )

    op.drop_index(
        "ix_scores_semantic_score",
        table_name="scores",
    )

    op.drop_index(
        "ix_scores_skill_score",
        table_name="scores",
    )

    op.drop_index(
        "ix_scores_created_at",
        table_name="scores",
    )

    # Interviews
    op.drop_index(
        "ix_interviews_status_scheduled",
        table_name="interviews",
    )

    op.drop_index(
        "ix_interviews_interview_type",
        table_name="interviews",
    )

    op.drop_index(
        "ix_interviews_created_at",
        table_name="interviews",
    )

    # Candidates
    op.drop_index(
        "ix_candidates_job_ranking",
        table_name="candidates",
    )

    op.drop_index(
        "ix_candidates_job_status",
        table_name="candidates",
    )

    op.drop_index(
        "ix_candidates_experience_score",
        table_name="candidates",
    )

    op.drop_index(
        "ix_candidates_created_at",
        table_name="candidates",
    )

    # Resumes
    op.drop_index(
        "ix_resumes_created_at",
        table_name="resumes",
    )

    op.drop_index(
        "ix_resumes_file_name",
        table_name="resumes",
    )

    # Jobs
    op.drop_index(
        "ix_jobs_employment_type",
        table_name="jobs",
    )

    op.drop_index(
        "ix_jobs_created_at",
        table_name="jobs",
    )