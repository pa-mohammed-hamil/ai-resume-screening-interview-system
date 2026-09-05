"""
Application configuration.

Loads configuration values from environment variables / .env file
and exposes them through a single `settings` object.
"""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Global application settings.
    """

    # -----------------------------------------------------------------------
    # Application
    # -----------------------------------------------------------------------

    APP_NAME: str = "AI Resume Screening & Interview System"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    API_V1_PREFIX: str = "/api/v1"

    # -----------------------------------------------------------------------
    # Security
    # -----------------------------------------------------------------------

    SECRET_KEY: str = Field(
        default="change-this-secret-key-in-production",
        min_length=16,
    )

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # -----------------------------------------------------------------------
    # CORS
    # -----------------------------------------------------------------------

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
    ]

    # -----------------------------------------------------------------------
    # Database
    # -----------------------------------------------------------------------

    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres"
        "@localhost:5432/resume_screening"
    )

    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 1800

    # -----------------------------------------------------------------------
    # Redis
    # -----------------------------------------------------------------------

    REDIS_URL: str = "redis://localhost:6379/0"

    # -----------------------------------------------------------------------
    # Celery
    # -----------------------------------------------------------------------

    CELERY_BROKER_URL: str = "redis://localhost:6379/1"

    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # -----------------------------------------------------------------------
    # Storage
    # -----------------------------------------------------------------------

    STORAGE_PATH: str = "storage"

    RESUME_STORAGE_PATH: str = "storage/resumes"

    GENERATED_RESUME_PATH: str = "storage/generated_resumes"

    INTERVIEW_AUDIO_PATH: str = "storage/interview_audio"

    INTERVIEW_REPORT_PATH: str = "storage/interview_reports"

    EMBEDDING_STORAGE_PATH: str = "storage/embeddings"

    TEMPORARY_STORAGE_PATH: str = "storage/temporary"

    # -----------------------------------------------------------------------
    # File Upload
    # -----------------------------------------------------------------------

    MAX_UPLOAD_SIZE_MB: int = 10

    ALLOWED_RESUME_EXTENSIONS: List[str] = [
        ".pdf",
        ".doc",
        ".docx",
    ]

    # -----------------------------------------------------------------------
    # AI / LLM
    # -----------------------------------------------------------------------

    OPENAI_API_KEY: str | None = None

    OPENAI_MODEL: str = "gpt-4o-mini"

    ANTHROPIC_API_KEY: str | None = None

    ANTHROPIC_MODEL: str = "claude-3-5-sonnet"

    LLM_PROVIDER: str = "openai"

    LLM_TEMPERATURE: float = 0.2

    LLM_MAX_TOKENS: int = 2000

    # -----------------------------------------------------------------------
    # Embeddings
    # -----------------------------------------------------------------------

    EMBEDDING_MODEL: str = "text-embedding-3-small"

    EMBEDDING_DIMENSION: int = 1536

    # -----------------------------------------------------------------------
    # Vector Database
    # -----------------------------------------------------------------------

    VECTOR_DB_PROVIDER: str = "pgvector"

    VECTOR_DB_URL: str | None = None

    # -----------------------------------------------------------------------
    # RAG
    # -----------------------------------------------------------------------

    RAG_TOP_K: int = 5

    RAG_CHUNK_SIZE: int = 1000

    RAG_CHUNK_OVERLAP: int = 200

    # -----------------------------------------------------------------------
    # Resume Screening
    # -----------------------------------------------------------------------

    SKILL_MATCH_WEIGHT: float = 0.40

    EXPERIENCE_MATCH_WEIGHT: float = 0.25

    SEMANTIC_MATCH_WEIGHT: float = 0.20

    EDUCATION_MATCH_WEIGHT: float = 0.15

    MIN_CANDIDATE_SCORE: float = 0.0

    MAX_CANDIDATE_SCORE: float = 100.0

    # -----------------------------------------------------------------------
    # Interview
    # -----------------------------------------------------------------------

    DEFAULT_INTERVIEW_DURATION_MINUTES: int = 30

    DEFAULT_QUESTION_COUNT: int = 10

    MIN_INTERVIEW_QUESTIONS: int = 5

    MAX_INTERVIEW_QUESTIONS: int = 30

    # -----------------------------------------------------------------------
    # Voice Interview
    # -----------------------------------------------------------------------

    STT_PROVIDER: str = "openai"

    TTS_PROVIDER: str = "openai"

    VOICE_LANGUAGE: str = "en"

    # -----------------------------------------------------------------------
    # Email
    # -----------------------------------------------------------------------

    SMTP_HOST: str | None = None

    SMTP_PORT: int = 587

    SMTP_USERNAME: str | None = None

    SMTP_PASSWORD: str | None = None

    SMTP_FROM_EMAIL: str | None = None

    SMTP_USE_TLS: bool = True

    # -----------------------------------------------------------------------
    # Monitoring
    # -----------------------------------------------------------------------

    ENABLE_METRICS: bool = True

    PROMETHEUS_PORT: int = 9090

    LOG_LEVEL: str = "INFO"

    # -----------------------------------------------------------------------
    # AWS / S3
    # -----------------------------------------------------------------------

    AWS_ACCESS_KEY_ID: str | None = None

    AWS_SECRET_ACCESS_KEY: str | None = None

    AWS_REGION: str = "ap-south-1"

    AWS_S3_BUCKET: str | None = None

    # -----------------------------------------------------------------------
    # Pydantic Settings Configuration
    # -----------------------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # -----------------------------------------------------------------------
    # Validators
    # -----------------------------------------------------------------------

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        """
        Allow CORS_ORIGINS to be supplied as either:

        JSON:
            ["http://localhost:3000"]

        or comma-separated:
            http://localhost:3000,http://localhost:5173
        """

        if isinstance(value, str):
            value = value.strip()

            if value.startswith("["):
                import json

                return json.loads(value)

            return [
                origin.strip()
                for origin in value.split(",")
                if origin.strip()
            ]

        return value

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, value: str) -> str:
        """
        Validate supported JWT algorithms.
        """

        allowed_algorithms = {
            "HS256",
            "HS384",
            "HS512",
        }

        if value not in allowed_algorithms:
            raise ValueError(
                f"Unsupported JWT algorithm: {value}"
            )

        return value


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    Using a cached instance prevents repeatedly loading
    environment configuration.
    """

    return Settings()


# Global settings instance used throughout the application.
settings = get_settings()
