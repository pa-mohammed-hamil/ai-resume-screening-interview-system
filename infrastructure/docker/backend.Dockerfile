# Project scaffold file
# ============================================================
# AI Resume Screening & Interview System
# Backend Dockerfile
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
# Copy backend
# ------------------------------------------------------------

COPY backend/app /app/backend/app

# ------------------------------------------------------------
# Copy AI / GenAI / Interview Engine
# ------------------------------------------------------------

COPY ai /app/ai
COPY genai /app/genai
COPY interview_engine /app/interview_engine

# ------------------------------------------------------------
# Copy configuration
# ------------------------------------------------------------

COPY pyproject.toml /app/pyproject.toml

# ------------------------------------------------------------
# Create required runtime directories
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
# Network
# ------------------------------------------------------------

EXPOSE 8000

# ------------------------------------------------------------
# Health check
# ------------------------------------------------------------

HEALTHCHECK --interval=30s \
    --timeout=10s \
    --start-period=20s \
    --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# ------------------------------------------------------------
# Start FastAPI
# ------------------------------------------------------------

CMD [
    "uvicorn",
    "backend.app.main:app",
    "--host",
    "0.0.0.0",
    "--port",
    "8000"
]