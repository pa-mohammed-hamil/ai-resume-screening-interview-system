# Project scaffold file
# ============================================================
# AI Resume Screening & Interview System
# Celery Worker Dockerfile
# ============================================================

FROM python:3.12-slim

# ------------------------------------------------------------
# Environment
# ------------------------------------------------------------

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# ------------------------------------------------------------
# System dependencies
# ------------------------------------------------------------

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    ffmpeg \
    poppler-utils \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Application directory
# ------------------------------------------------------------

WORKDIR /app

# ------------------------------------------------------------
# Python dependencies
# ------------------------------------------------------------

COPY backend/requirements.txt /app/backend/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r /app/backend/requirements.txt

# ------------------------------------------------------------
# Backend
# ------------------------------------------------------------

COPY backend/app /app/backend/app

# ------------------------------------------------------------
# AI modules
# ------------------------------------------------------------

COPY ai /app/ai

# ------------------------------------------------------------
# GenAI modules
# ------------------------------------------------------------

COPY genai /app/genai

# ------------------------------------------------------------
# Interview engine
# ------------------------------------------------------------

COPY interview_engine /app/interview_engine

# ------------------------------------------------------------
# Project configuration
# ------------------------------------------------------------

COPY pyproject.toml /app/pyproject.toml

# ------------------------------------------------------------
# Runtime directories
# ------------------------------------------------------------

RUN mkdir -p \
    /app/storage/resumes \
    /app/storage/generated_resumes \
    /app/storage/interview_audio \
    /app/storage/interview_reports \
    /app/storage/temporary \
    /app/data/raw/resumes \
    /app/data/raw/job_descriptions \
    /app/data/processed/resumes \
    /app/data/processed/job_descriptions

# ------------------------------------------------------------
# Non-root user
# ------------------------------------------------------------

RUN groupadd --system appgroup && \
    useradd --system \
    --gid appgroup \
    --create-home \
    appuser && \
    chown -R appuser:appgroup /app

USER appuser

# ------------------------------------------------------------
# Health check
# ------------------------------------------------------------

HEALTHCHECK --interval=30s \
    --timeout=10s \
    --start-period=30s \
    --retries=3 \
    CMD celery \
    -A backend.app.workers.celery_app inspect ping \
    --destination=celery@$HOSTNAME || exit 1

# ------------------------------------------------------------
# Start Celery worker
# ------------------------------------------------------------

CMD [
    "celery",
    "-A",
    "backend.app.workers.celery_app",
    "worker",
    "--loglevel=INFO",
    "--concurrency=2"
]