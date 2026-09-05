# Project scaffold file
"""
AI Resume Screening & Interview System
=======================================

File:
    scripts/seed_database.py

Purpose:
    Seed the application database with development/demo data.

Creates:
    - Users
    - Jobs
    - Candidates
    - Resumes
    - Interviews
    - Scores
    - Audit logs

Usage:
    python scripts/seed_database.py

    python scripts/seed_database.py --reset

    python scripts/seed_database.py --users 5 --jobs 5 --candidates 10

    python scripts/seed_database.py --dry-run

Notes:
    This script is intended for development/testing.
    Do not use demo passwords or demo data in production.
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import secrets
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger(
    "database-seeder"
)


# ============================================================
# DATABASE IMPORTS
# ============================================================

try:
    from sqlalchemy import delete, select
    from sqlalchemy.orm import Session

except ImportError as exc:

    logger.error(
        "SQLAlchemy is required: %s",
        exc,
    )

    sys.exit(1)


# ============================================================
# APPLICATION IMPORTS
# ============================================================

try:

    from backend.app.database.connection import (
        engine,
    )

except ImportError:

    try:

        from backend.app.database.session import (
            engine,
        )

    except ImportError as exc:

        logger.error(
            "Could not import database engine. "
            "Check backend/app/database configuration: %s",
            exc,
        )

        sys.exit(1)


# ============================================================
# MODEL IMPORTS
# ============================================================

def import_models() -> dict[str, Any]:
    """
    Import project models.

    The project currently defines:
        User
        Resume
        Job
        Candidate
        Interview
        Score
        AuditLog
    """

    models: dict[str, Any] = {}

    try:

        from backend.app.models.user import User

        models["User"] = User

    except ImportError as exc:

        logger.warning(
            "Could not import User model: %s",
            exc,
        )

    try:

        from backend.app.models.resume import Resume

        models["Resume"] = Resume

    except ImportError as exc:

        logger.warning(
            "Could not import Resume model: %s",
            exc,
        )

    try:

        from backend.app.models.job import Job

        models["Job"] = Job

    except ImportError as exc:

        logger.warning(
            "Could not import Job model: %s",
            exc,
        )

    try:

        from backend.app.models.candidate import Candidate

        models["Candidate"] = Candidate

    except ImportError as exc:

        logger.warning(
            "Could not import Candidate model: %s",
            exc,
        )

    try:

        from backend.app.models.interview import Interview

        models["Interview"] = Interview

    except ImportError as exc:

        logger.warning(
            "Could not import Interview model: %s",
            exc,
        )

    try:

        from backend.app.models.score import Score

        models["Score"] = Score

    except ImportError as exc:

        logger.warning(
            "Could not import Score model: %s",
            exc,
        )

    try:

        from backend.app.models.audit_log import AuditLog

        models["AuditLog"] = AuditLog

    except ImportError as exc:

        logger.warning(
            "Could not import AuditLog model: %s",
            exc,
        )

    return models


MODELS = import_models()


# ============================================================
# DEMO DATA
# ============================================================

DEMO_USERS = [
    {
        "email": "admin@example.com",
        "first_name": "System",
        "last_name": "Admin",
        "role": "admin",
        "is_active": True,
    },
    {
        "email": "recruiter@example.com",
        "first_name": "Sarah",
        "last_name": "Recruiter",
        "role": "recruiter",
        "is_active": True,
    },
    {
        "email": "hr@example.com",
        "first_name": "Michael",
        "last_name": "HR",
        "role": "recruiter",
        "is_active": True,
    },
]


DEMO_JOBS = [
    {
        "title": "Python Backend Developer",
        "department": "Engineering",
        "location": "Remote",
        "employment_type": "Full-time",
        "description": (
            "We are looking for a Python backend developer "
            "to build scalable APIs and data services."
        ),
        "requirements": (
            "Python, FastAPI, SQL, PostgreSQL, Docker, "
            "REST APIs, Git and cloud deployment."
        ),
        "responsibilities": (
            "Develop APIs, design backend services, "
            "write tests, review code and improve "
            "application performance."
        ),
        "status": "open",
    },
    {
        "title": "Machine Learning Engineer",
        "department": "AI",
        "location": "Bangalore, India",
        "employment_type": "Full-time",
        "description": (
            "Build and deploy machine learning models "
            "for intelligent recruiting products."
        ),
        "requirements": (
            "Python, scikit-learn, PyTorch, NLP, "
            "machine learning, embeddings and MLOps."
        ),
        "responsibilities": (
            "Train models, evaluate experiments, "
            "build ML pipelines and deploy inference services."
        ),
        "status": "open",
    },
    {
        "title": "Frontend Developer",
        "department": "Engineering",
        "location": "Remote",
        "employment_type": "Full-time",
        "description": (
            "Build responsive and accessible interfaces "
            "for the recruiter platform."
        ),
        "requirements": (
            "JavaScript, HTML, CSS, React, REST APIs, "
            "Git and responsive design."
        ),
        "responsibilities": (
            "Develop reusable components, integrate APIs, "
            "optimize frontend performance and fix UI issues."
        ),
        "status": "open",
    },
    {
        "title": "Data Analyst",
        "department": "Analytics",
        "location": "Kochi, India",
        "employment_type": "Full-time",
        "description": (
            "Analyze recruiting data and create actionable "
            "business intelligence reports."
        ),
        "requirements": (
            "SQL, Python, Pandas, Excel, Power BI, "
            "statistics and data visualization."
        ),
        "responsibilities": (
            "Build reports, analyze recruitment metrics, "
            "identify trends and communicate insights."
        ),
        "status": "open",
    },
    {
        "title": "DevOps Engineer",
        "department": "Infrastructure",
        "location": "Hyderabad, India",
        "employment_type": "Full-time",
        "description": (
            "Manage cloud infrastructure and CI/CD "
            "pipelines for production services."
        ),
        "requirements": (
            "AWS, Docker, Kubernetes, Terraform, "
            "Linux, CI/CD and monitoring."
        ),
        "responsibilities": (
            "Automate deployments, manage infrastructure, "
            "monitor services and improve reliability."
        ),
        "status": "open",
    },
]


DEMO_CANDIDATES = [
    {
        "first_name": "Arjun",
        "last_name": "Nair",
        "email": "arjun.nair@example.com",
        "phone": "+91 9876543210",
        "location": "Kochi, India",
        "years_experience": 2,
        "summary": (
            "Python developer with experience building "
            "REST APIs and data processing applications."
        ),
        "skills": [
            "Python",
            "FastAPI",
            "SQL",
            "PostgreSQL",
            "Docker",
            "Git",
        ],
        "education": "B.Tech Computer Science",
    },
    {
        "first_name": "Ananya",
        "last_name": "Menon",
        "email": "ananya.menon@example.com",
        "phone": "+91 9876543211",
        "location": "Bangalore, India",
        "years_experience": 3,
        "summary": (
            "Machine learning engineer specializing in "
            "NLP, deep learning and model deployment."
        ),
        "skills": [
            "Python",
            "PyTorch",
            "NLP",
            "Machine Learning",
            "TensorFlow",
            "Docker",
        ],
        "education": "M.Tech Artificial Intelligence",
    },
    {
        "first_name": "Rahul",
        "last_name": "Kumar",
        "email": "rahul.kumar@example.com",
        "phone": "+91 9876543212",
        "location": "Chennai, India",
        "years_experience": 4,
        "summary": (
            "Frontend engineer experienced in modern "
            "JavaScript applications and responsive UI."
        ),
        "skills": [
            "JavaScript",
            "React",
            "HTML",
            "CSS",
            "REST APIs",
            "Git",
        ],
        "education": "B.E. Computer Science",
    },
    {
        "first_name": "Meera",
        "last_name": "Joseph",
        "email": "meera.joseph@example.com",
        "phone": "+91 9876543213",
        "location": "Kochi, India",
        "years_experience": 1,
        "summary": (
            "Junior data analyst with strong SQL and "
            "Python skills and experience creating dashboards."
        ),
        "skills": [
            "SQL",
            "Python",
            "Pandas",
            "Excel",
            "Power BI",
            "Statistics",
        ],
        "education": "B.Sc Statistics",
    },
    {
        "first_name": "Vivek",
        "last_name": "Sharma",
        "email": "vivek.sharma@example.com",
        "phone": "+91 9876543214",
        "location": "Hyderabad, India",
        "years_experience": 5,
        "summary": (
            "DevOps engineer experienced with AWS, Docker, "
            "Terraform, Kubernetes and CI/CD."
        ),
        "skills": [
            "AWS",
            "Docker",
            "Kubernetes",
            "Terraform",
            "Linux",
            "CI/CD",
        ],
        "education": "B.Tech Information Technology",
    },
    {
        "first_name": "Diya",
        "last_name": "Thomas",
        "email": "diya.thomas@example.com",
        "phone": "+91 9876543215",
        "location": "Trivandrum, India",
        "years_experience": 2,
        "summary": (
            "Software developer with experience in Python, "
            "REST APIs and machine learning applications."
        ),
        "skills": [
            "Python",
            "FastAPI",
            "Machine Learning",
            "SQL",
            "Git",
            "Docker",
        ],
        "education": "B.Tech Information Technology",
    },
]


# ============================================================
# PASSWORD UTILITIES
# ============================================================

def hash_password(
    password: str,
) -> str:
    """
    Hash a development password.

    If the application's security module provides a password
    hashing function, use it. Otherwise use PBKDF2 for the
    development seed script.
    """

    try:

        from backend.app.core.security import (
            get_password_hash,
        )

        return get_password_hash(
            password
        )

    except (
        ImportError,
        AttributeError,
    ):

        salt = secrets.token_bytes(
            16
        )

        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(
                "utf-8"
            ),
            salt,
            100_000,
        )

        return (
            "pbkdf2_sha256$"
            f"{salt.hex()}$"
            f"{digest.hex()}"
        )


# ============================================================
# MODEL FIELD HELPERS
# ============================================================

def model_columns(
    model: Any,
) -> set[str]:

    return {
        column.name
        for column
        in model.__table__.columns
    }


def filter_fields(
    model: Any,
    values: dict[str, Any],
) -> dict[str, Any]:
    """
    Only pass values that actually exist on the model.

    This makes the seed script tolerant of small schema
    differences between development versions.
    """

    columns = model_columns(
        model
    )

    return {
        key: value
        for key, value in values.items()
        if key in columns
    }


def set_if_present(
    values: dict[str, Any],
    model: Any,
    field: str,
    value: Any,
) -> None:

    if field in model_columns(
        model
    ):

        values[field] = value


# ============================================================
# GENERIC DATABASE HELPERS
# ============================================================

def find_by_field(
    session: Session,
    model: Any,
    field: str,
    value: Any,
) -> Any | None:

    if field not in model_columns(
        model
    ):

        return None

    column = getattr(
        model,
        field,
    )

    return session.execute(
        select(model).where(
            column == value
        )
    ).scalar_one_or_none()


def safe_add(
    session: Session,
    model: Any,
    values: dict[str, Any],
) -> Any:

    filtered = filter_fields(
        model,
        values,
    )

    instance = model(
        **filtered
    )

    session.add(
        instance
    )

    session.flush()

    return instance


# ============================================================
# USER SEEDING
# ============================================================

def seed_users(
    session: Session,
) -> list[Any]:

    model = MODELS.get(
        "User"
    )

    if model is None:

        logger.warning(
            "User model unavailable. "
            "Skipping users."
        )

        return []

    users = []

    for data in DEMO_USERS:

        email = data[
            "email"
        ]

        existing = find_by_field(
            session,
            model,
            "email",
            email,
        )

        if existing:

            users.append(
                existing
            )

            logger.info(
                "User already exists: %s",
                email,
            )

            continue

        values = {
            "email": email,
            "first_name": data[
                "first_name"
            ],
            "last_name": data[
                "last_name"
            ],
            "role": data[
                "role"
            ],
            "is_active": data[
                "is_active"
            ],
            "password": hash_password(
                "ChangeMe123!"
            ),
            "hashed_password": hash_password(
                "ChangeMe123!"
            ),
            "created_at": datetime.now(
                timezone.utc
            ),
        }

        values = filter_fields(
            model,
            values,
        )

        # Avoid passing both password and hashed_password
        # if the model supports only one of them.
        if (
            "hashed_password"
            in values
            and "password"
            in values
        ):

            values.pop(
                "password",
                None,
            )

        user = safe_add(
            session,
            model,
            values,
        )

        users.append(
            user
        )

        logger.info(
            "Created user: %s",
            email,
        )

    return users


# ============================================================
# JOB SEEDING
# ============================================================

def seed_jobs(
    session: Session,
    recruiter: Any | None,
    limit: int,
) -> list[Any]:

    model = MODELS.get(
        "Job"
    )

    if model is None:

        logger.warning(
            "Job model unavailable. "
            "Skipping jobs."
        )

        return []

    jobs = []

    recruiter_id = (
        getattr(
            recruiter,
            "id",
            None,
        )
        if recruiter
        else None
    )

    for data in DEMO_JOBS[:limit]:

        existing = find_by_field(
            session,
            model,
            "title",
            data[
                "title"
            ],
        )

        if existing:

            jobs.append(
                existing
            )

            logger.info(
                "Job already exists: %s",
                data[
                    "title"
                ],
            )

            continue

        values = {
            "title": data[
                "title"
            ],
            "department": data[
                "department"
            ],
            "location": data[
                "location"
            ],
            "employment_type": data[
                "employment_type"
            ],
            "description": data[
                "description"
            ],
            "requirements": data[
                "requirements"
            ],
            "responsibilities": data[
                "responsibilities"
            ],
            "status": data[
                "status"
            ],
            "created_at": datetime.now(
                timezone.utc
            ),
        }

        if recruiter_id is not None:

            values[
                "created_by"
            ] = recruiter_id

            values[
                "recruiter_id"
            ] = recruiter_id

            values[
                "user_id"
            ] = recruiter_id

        job = safe_add(
            session,
            model,
            values,
        )

        jobs.append(
            job
        )

        logger.info(
            "Created job: %s",
            data[
                "title"
            ],
        )

    return jobs


# ============================================================
# CANDIDATE SEEDING
# ============================================================

def seed_candidates(
    session: Session,
    limit: int,
) -> list[Any]:

    model = MODELS.get(
        "Candidate"
    )

    if model is None:

        logger.warning(
            "Candidate model unavailable. "
            "Skipping candidates."
        )

        return []

    candidates = []

    for data in DEMO_CANDIDATES[:limit]:

        email = data[
            "email"
        ]

        existing = find_by_field(
            session,
            model,
            "email",
            email,
        )

        if existing:

            candidates.append(
                existing
            )

            logger.info(
                "Candidate already exists: %s",
                email,
            )

            continue

        values = {
            "first_name": data[
                "first_name"
            ],
            "last_name": data[
                "last_name"
            ],
            "email": email,
            "phone": data[
                "phone"
            ],
            "location": data[
                "location"
            ],
            "years_experience": data[
                "years_experience"
            ],
            "summary": data[
                "summary"
            ],
            "skills": data[
                "skills"
            ],
            "education": data[
                "education"
            ],
            "created_at": datetime.now(
                timezone.utc
            ),
        }

        candidate = safe_add(
            session,
            model,
            values,
        )

        candidates.append(
            candidate
        )

        logger.info(
            "Created candidate: %s %s",
            data[
                "first_name"
            ],
            data[
                "last_name"
            ],
        )

    return candidates


# ============================================================
# RESUME SEEDING
# ============================================================

def seed_resumes(
    session: Session,
    candidates: list[Any],
) -> list[Any]:

    model = MODELS.get(
        "Resume"
    )

    if model is None:

        logger.warning(
            "Resume model unavailable. "
            "Skipping resumes."
        )

        return []

    resumes = []

    for index, candidate in enumerate(
        candidates
    ):

        candidate_id = getattr(
            candidate,
            "id",
            None,
        )

        if candidate_id is None:

            continue

        # Try candidate_id first.
        existing = find_by_field(
            session,
            model,
            "candidate_id",
            candidate_id,
        )

        if existing:

            resumes.append(
                existing
            )

            continue

        first_name = getattr(
            candidate,
            "first_name",
            f"candidate_{index + 1}",
        )

        last_name = getattr(
            candidate,
            "last_name",
            "",
        )

        filename = (
            f"{first_name.lower()}_"
            f"{last_name.lower()}_resume.txt"
        )

        sample_text = (
            f"{first_name} {last_name}\n\n"
            "Professional Resume\n\n"
            f"Summary:\n"
            f"{getattr(candidate, 'summary', '')}\n\n"
            f"Skills:\n"
            f"{', '.join(getattr(candidate, 'skills', []) or [])}\n\n"
            f"Education:\n"
            f"{getattr(candidate, 'education', '')}\n"
        )

        values = {
            "candidate_id": candidate_id,
            "filename": filename,
            "file_name": filename,
            "original_filename": filename,
            "file_path": (
                f"storage/resumes/{filename}"
            ),
            "storage_path": (
                f"storage/resumes/{filename}"
            ),
            "content": sample_text,
            "text": sample_text,
            "parsed_text": sample_text,
            "status": "processed",
            "created_at": datetime.now(
                timezone.utc
            ),
        }

        resume = safe_add(
            session,
            model,
            values,
        )

        resumes.append(
            resume
        )

        logger.info(
            "Created resume for %s %s",
            first_name,
            last_name,
        )

    return resumes


# ============================================================
# SCORE SEEDING
# ============================================================

def seed_scores(
    session: Session,
    candidates: list[Any],
    jobs: list[Any],
) -> list[Any]:

    model = MODELS.get(
        "Score"
    )

    if model is None:

        logger.warning(
            "Score model unavailable. "
            "Skipping scores."
        )

        return []

    scores = []

    if not candidates or not jobs:

        return scores

    # Generate a manageable candidate/job matrix.
    pairs = []

    for index, candidate in enumerate(
        candidates
    ):

        job = jobs[
            index % len(jobs)
        ]

        pairs.append(
            (
                candidate,
                job,
            )
        )

    for index, (
        candidate,
        job,
    ) in enumerate(
        pairs
    ):

        candidate_id = getattr(
            candidate,
            "id",
            None,
        )

        job_id = getattr(
            job,
            "id",
            None,
        )

        if (
            candidate_id is None
            or job_id is None
        ):

            continue

        # Score decreases slightly across demo candidates
        # to make ranking dashboards visually meaningful.
        ats_score = max(
            55.0,
            94.0 - (
                index * 4.0
            ),
        )

        skill_score = max(
            50.0,
            91.0 - (
                index * 3.5
            ),
        )

        experience_score = max(
            45.0,
            88.0 - (
                index * 3.0
            ),
        )

        education_score = max(
            60.0,
            90.0 - (
                index * 2.0
            ),
        )

        overall_score = round(
            (
                ats_score * 0.30
                + skill_score * 0.30
                + experience_score * 0.25
                + education_score * 0.15
            ),
            2,
        )

        values = {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "ats_score": round(
                ats_score,
                2,
            ),
            "skill_score": round(
                skill_score,
                2,
            ),
            "experience_score": round(
                experience_score,
                2,
            ),
            "education_score": round(
                education_score,
                2,
            ),
            "overall_score": overall_score,
            "score": overall_score,
            "created_at": datetime.now(
                timezone.utc
            ),
        }

        # Avoid duplicate candidate/job scores.
        existing = None

        if (
            "candidate_id"
            in model_columns(model)
            and "job_id"
            in model_columns(model)
        ):

            existing = session.execute(
                select(model).where(
                    getattr(
                        model,
                        "candidate_id",
                    )
                    == candidate_id,
                    getattr(
                        model,
                        "job_id",
                    )
                    == job_id,
                )
            ).scalar_one_or_none()

        if existing:

            scores.append(
                existing
            )

            continue

        score = safe_add(
            session,
            model,
            values,
        )

        scores.append(
            score
        )

    logger.info(
        "Created/loaded %d score records.",
        len(scores),
    )

    return scores


# ============================================================
# INTERVIEW SEEDING
# ============================================================

def seed_interviews(
    session: Session,
    candidates: list[Any],
    jobs: list[Any],
    recruiter: Any | None,
) -> list[Any]:

    model = MODELS.get(
        "Interview"
    )

    if model is None:

        logger.warning(
            "Interview model unavailable. "
            "Skipping interviews."
        )

        return []

    interviews = []

    if not candidates:

        return interviews

    now = datetime.now(
        timezone.utc
    )

    for index, candidate in enumerate(
        candidates[:5]
    ):

        candidate_id = getattr(
            candidate,
            "id",
            None,
        )

        if candidate_id is None:

            continue

        job = (
            jobs[
                index % len(jobs)
            ]
            if jobs
            else None
        )

        job_id = (
            getattr(
                job,
                "id",
                None,
            )
            if job
            else None
        )

        existing = find_by_field(
            session,
            model,
            "candidate_id",
            candidate_id,
        )

        if existing:

            interviews.append(
                existing
            )

            continue

        status_values = [
            "completed",
            "completed",
            "scheduled",
            "in_progress",
            "cancelled",
        ]

        status = status_values[
            index % len(
                status_values
            )
        ]

        scheduled_at = (
            now
            - timedelta(
                days=2
            )
            if status == "completed"
            else now
            + timedelta(
                days=index + 1
            )
        )

        values = {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "title": (
                "AI Technical Interview"
            ),
            "interview_type": (
                "technical"
            ),
            "status": status,
            "scheduled_at": scheduled_at,
            "duration_minutes": 45,
            "score": (
                78.0 + (
                    index * 3.0
                )
                if status == "completed"
                else None
            ),
            "created_at": (
                now
                - timedelta(
                    days=7 - index
                )
            ),
        }

        recruiter_id = (
            getattr(
                recruiter,
                "id",
                None,
            )
            if recruiter
            else None
        )

        if recruiter_id is not None:

            values[
                "created_by"
            ] = recruiter_id

            values[
                "recruiter_id"
            ] = recruiter_id

        interview = safe_add(
            session,
            model,
            values,
        )

        interviews.append(
            interview
        )

        logger.info(
            "Created interview for candidate ID %s",
            candidate_id,
        )

    return interviews


# ============================================================
# AUDIT LOG SEEDING
# ============================================================

def seed_audit_logs(
    session: Session,
    users: list[Any],
) -> list[Any]:

    model = MODELS.get(
        "AuditLog"
    )

    if model is None:

        logger.warning(
            "AuditLog model unavailable. "
            "Skipping audit logs."
        )

        return []

    logs = []

    if not users:

        return logs

    actions = [
        (
            "LOGIN",
            "User logged into the application.",
        ),
        (
            "RESUME_ANALYSIS",
            "Resume analysis completed.",
        ),
        (
            "CANDIDATE_RANKING",
            "Candidate ranking generated.",
        ),
        (
            "INTERVIEW_CREATED",
            "AI interview created.",
        ),
        (
            "JOB_CREATED",
            "Job posting created.",
        ),
    ]

    now = datetime.now(
        timezone.utc
    )

    for index, user in enumerate(
        users
    ):

        user_id = getattr(
            user,
            "id",
            None,
        )

        action, description = actions[
            index % len(actions)
        ]

        values = {
            "user_id": user_id,
            "action": action,
            "event": action,
            "description": description,
            "resource_type": "system",
            "resource_id": None,
            "created_at": (
                now
                - timedelta(
                    hours=index
                )
            ),
        }

        log = safe_add(
            session,
            model,
            values,
        )

        logs.append(
            log
        )

    logger.info(
        "Created %d audit log records.",
        len(logs),
    )

    return logs


# ============================================================
# RESET DATABASE
# ============================================================

def reset_database(
    session: Session,
) -> None:
    """
    Delete seeded application records.

    Deletes child records first to reduce foreign-key
    constraint issues.
    """

    delete_order = [
        "AuditLog",
        "Score",
        "Interview",
        "Resume",
        "Candidate",
        "Job",
        "User",
    ]

    for model_name in delete_order:

        model = MODELS.get(
            model_name
        )

        if model is None:
            continue

        try:

            result = session.execute(
                delete(model)
            )

            logger.info(
                "Deleted %d %s records.",
                result.rowcount or 0,
                model_name,
            )

        except Exception as exc:

            logger.warning(
                "Could not delete %s: %s",
                model_name,
                exc,
            )


# ============================================================
# DATABASE STATUS
# ============================================================

def count_records(
    session: Session,
) -> dict[str, int]:

    counts = {}

    for name, model in MODELS.items():

        try:

            count = session.execute(
                select(model)
            ).scalars().all()

            counts[
                name
            ] = len(
                count
            )

        except Exception:

            counts[
                name
            ] = 0

    return counts


# ============================================================
# DRY RUN
# ============================================================

def print_dry_run(
    user_limit: int,
    job_limit: int,
    candidate_limit: int,
) -> None:

    print()
    print("=" * 72)
    print(
        "DATABASE SEED DRY RUN"
    )
    print("=" * 72)

    print(
        f"Users to process      : "
        f"{user_limit}"
    )

    print(
        f"Jobs to process       : "
        f"{job_limit}"
    )

    print(
        f"Candidates to process : "
        f"{candidate_limit}"
    )

    print()
    print(
        "Demo credentials:"
    )

    print(
        "  admin@example.com"
    )

    print(
        "  recruiter@example.com"
    )

    print(
        "  Password: ChangeMe123!"
    )

    print()
    print(
        "No database changes were made."
    )

    print("=" * 72)
    print()


# ============================================================
# SEED DATABASE
# ============================================================

def seed_database(
    reset: bool = False,
    user_limit: int = 3,
    job_limit: int = 5,
    candidate_limit: int = 6,
) -> dict[str, int]:

    logger.info(
        "Starting database seed."
    )

    with Session(
        bind=engine
    ) as session:

        try:

            # ------------------------------------------------
            # Reset
            # ------------------------------------------------

            if reset:

                logger.warning(
                    "Reset requested. "
                    "Deleting existing application records."
                )

                reset_database(
                    session
                )

                session.commit()

            # ------------------------------------------------
            # Users
            # ------------------------------------------------

            users = seed_users(
                session
            )

            session.flush()

            recruiter = next(
                (
                    user
                    for user in users
                    if getattr(
                        user,
                        "role",
                        "",
                    )
                    == "recruiter"
                ),
                users[0]
                if users
                else None,
            )

            # ------------------------------------------------
            # Jobs
            # ------------------------------------------------

            jobs = seed_jobs(
                session,
                recruiter,
                job_limit,
            )

            session.flush()

            # ------------------------------------------------
            # Candidates
            # ------------------------------------------------

            candidates = seed_candidates(
                session,
                candidate_limit,
            )

            session.flush()

            # ------------------------------------------------
            # Resumes
            # ------------------------------------------------

            resumes = seed_resumes(
                session,
                candidates,
            )

            session.flush()

            # ------------------------------------------------
            # Scores
            # ------------------------------------------------

            scores = seed_scores(
                session,
                candidates,
                jobs,
            )

            session.flush()

            # ------------------------------------------------
            # Interviews
            # ------------------------------------------------

            interviews = seed_interviews(
                session,
                candidates,
                jobs,
                recruiter,
            )

            session.flush()

            # ------------------------------------------------
            # Audit logs
            # ------------------------------------------------

            audit_logs = seed_audit_logs(
                session,
                users,
            )

            session.flush()

            # ------------------------------------------------
            # Commit
            # ------------------------------------------------

            session.commit()

            counts = count_records(
                session
            )

            logger.info(
                "Database seed completed successfully."
            )

            return {
                "users": len(users),
                "jobs": len(jobs),
                "candidates": len(candidates),
                "resumes": len(resumes),
                "scores": len(scores),
                "interviews": len(interviews),
                "audit_logs": len(audit_logs),
                "total_database_records": sum(
                    counts.values()
                ),
            }

        except Exception:

            session.rollback()

            logger.exception(
                "Database seed failed. "
                "Transaction rolled back."
            )

            raise


# ============================================================
# REPORT
# ============================================================

def print_report(
    result: dict[str, int],
) -> None:

    print()
    print("=" * 72)
    print(
        "AI RESUME SCREENING & INTERVIEW SYSTEM"
    )
    print(
        "DATABASE SEED REPORT"
    )
    print("=" * 72)

    print(
        f"Users               : "
        f"{result['users']}"
    )

    print(
        f"Jobs                : "
        f"{result['jobs']}"
    )

    print(
        f"Candidates          : "
        f"{result['candidates']}"
    )

    print(
        f"Resumes             : "
        f"{result['resumes']}"
    )

    print(
        f"Scores              : "
        f"{result['scores']}"
    )

    print(
        f"Interviews          : "
        f"{result['interviews']}"
    )

    print(
        f"Audit logs          : "
        f"{result['audit_logs']}"
    )

    print(
        f"Total records       : "
        f"{result['total_database_records']}"
    )

    print()
    print(
        "Demo login:"
    )

    print(
        "  Email    : admin@example.com"
    )

    print(
        "  Password : ChangeMe123!"
    )

    print()
    print(
        "IMPORTANT: Change/remove demo credentials "
        "before production deployment."
    )

    print("=" * 72)
    print()


# ============================================================
# ARGUMENT PARSER
# ============================================================

def parse_arguments() -> argparse.Namespace:

    parser = argparse.ArgumentParser(
        description=(
            "Seed the AI Resume Screening "
            "and Interview System database."
        )
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help=(
            "Delete existing application data "
            "before inserting seed data."
        ),
    )

    parser.add_argument(
        "--users",
        type=int,
        default=3,
        help=(
            "Number of demo users."
        ),
    )

    parser.add_argument(
        "--jobs",
        type=int,
        default=5,
        help=(
            "Number of demo jobs."
        ),
    )

    parser.add_argument(
        "--candidates",
        type=int,
        default=6,
        help=(
            "Number of demo candidates."
        ),
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Show what would be seeded without "
            "changing the database."
        ),
    )

    return parser.parse_args()


# ============================================================
# VALIDATION
# ============================================================

def validate_arguments(
    args: argparse.Namespace,
) -> None:

    if args.users < 1:

        raise ValueError(
            "--users must be at least 1."
        )

    if args.jobs < 1:

        raise ValueError(
            "--jobs must be at least 1."
        )

    if args.candidates < 1:

        raise ValueError(
            "--candidates must be at least 1."
        )

    if args.users > len(
        DEMO_USERS
    ):

        logger.warning(
            "Only %d predefined users exist. "
            "User count will be capped.",
            len(DEMO_USERS),
        )

        args.users = len(
            DEMO_USERS
        )

    if args.jobs > len(
        DEMO_JOBS
    ):

        logger.warning(
            "Only %d predefined jobs exist. "
            "Job count will be capped.",
            len(DEMO_JOBS),
        )

        args.jobs = len(
            DEMO_JOBS
        )

    if args.candidates > len(
        DEMO_CANDIDATES
    ):

        logger.warning(
            "Only %d predefined candidates exist. "
            "Candidate count will be capped.",
            len(DEMO_CANDIDATES),
        )

        args.candidates = len(
            DEMO_CANDIDATES
        )


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    args = parse_arguments()

    try:

        validate_arguments(
            args
        )

        if args.dry_run:

            print_dry_run(
                user_limit=args.users,
                job_limit=args.jobs,
                candidate_limit=args.candidates,
            )

            return 0

        result = seed_database(
            reset=args.reset,
            user_limit=args.users,
            job_limit=args.jobs,
            candidate_limit=args.candidates,
        )

        print_report(
            result
        )

        return 0

    except KeyboardInterrupt:

        logger.warning(
            "Database seeding cancelled."
        )

        return 130

    except Exception as exc:

        logger.exception(
            "Database seeding failed: %s",
            exc,
        )

        return 1


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    sys.exit(
        main()
    )