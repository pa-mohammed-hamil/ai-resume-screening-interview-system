# Project scaffold file
"""
LLM model configuration for the AI Resume Screening & Interview System.

Responsibilities:
- Store LLM provider configuration
- Manage model names and generation parameters
- Read configuration from environment variables
- Provide task-specific model settings
- Keep secrets out of source code
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, Optional


# ============================================================================
# Helpers
# ============================================================================


def _get_env(
    name: str,
    default: Optional[str] = None,
) -> Optional[str]:
    """Read an environment variable."""

    value = os.getenv(name)

    if value is None:
        return default

    value = value.strip()

    return value if value else default


def _get_int(
    name: str,
    default: int,
) -> int:
    """Read an integer environment variable."""

    value = _get_env(name)

    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        return default


def _get_float(
    name: str,
    default: float,
) -> float:
    """Read a floating-point environment variable."""

    value = _get_env(name)

    if value is None:
        return default

    try:
        return float(value)
    except ValueError:
        return default


def _get_bool(
    name: str,
    default: bool,
) -> bool:
    """Read a boolean environment variable."""

    value = _get_env(name)

    if value is None:
        return default

    return value.lower() in {
        "1",
        "true",
        "yes",
        "y",
        "on",
    }


# ============================================================================
# Model Configuration
# ============================================================================


@dataclass(frozen=True)
class ModelConfig:
    """
    Configuration for a single LLM model.
    """

    provider: str
    model: str

    temperature: float = 0.2

    max_tokens: int = 2000

    top_p: float = 1.0

    frequency_penalty: float = 0.0

    presence_penalty: float = 0.0

    timeout: int = 60

    max_retries: int = 3

    response_format: str = "json"

    enabled: bool = True

    def validate(self) -> None:
        """Validate model configuration."""

        if not self.provider:
            raise ValueError(
                "LLM provider cannot be empty."
            )

        if not self.model:
            raise ValueError(
                "LLM model cannot be empty."
            )

        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError(
                "Temperature must be between 0 and 2."
            )

        if self.max_tokens <= 0:
            raise ValueError(
                "max_tokens must be greater than zero."
            )

        if not 0.0 < self.top_p <= 1.0:
            raise ValueError(
                "top_p must be greater than 0 and <= 1."
            )

        if self.timeout <= 0:
            raise ValueError(
                "timeout must be greater than zero."
            )

        if self.max_retries < 0:
            raise ValueError(
                "max_retries cannot be negative."
            )


# ============================================================================
# Embedding Configuration
# ============================================================================


@dataclass(frozen=True)
class EmbeddingConfig:
    """
    Configuration for embedding models.

    Used by the RAG/vector-search pipeline.
    """

    provider: str

    model: str

    dimensions: int = 1536

    batch_size: int = 32

    timeout: int = 60

    max_retries: int = 3

    enabled: bool = True

    def validate(self) -> None:
        """Validate embedding configuration."""

        if not self.provider:
            raise ValueError(
                "Embedding provider cannot be empty."
            )

        if not self.model:
            raise ValueError(
                "Embedding model cannot be empty."
            )

        if self.dimensions <= 0:
            raise ValueError(
                "Embedding dimensions must be positive."
            )

        if self.batch_size <= 0:
            raise ValueError(
                "Embedding batch size must be positive."
            )


# ============================================================================
# Application LLM Settings
# ============================================================================


@dataclass
class LLMSettings:
    """
    Complete LLM configuration for the application.
    """

    # ------------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------------

    api_key: Optional[str] = None

    base_url: Optional[str] = None

    organization: Optional[str] = None

    # ------------------------------------------------------------------------
    # Default model
    # ------------------------------------------------------------------------

    default_model: str = "gpt-4.1-mini"

    default_provider: str = "openai"

    # ------------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------------

    temperature: float = 0.2

    max_tokens: int = 2000

    top_p: float = 1.0

    # ------------------------------------------------------------------------
    # Reliability
    # ------------------------------------------------------------------------

    timeout: int = 60

    max_retries: int = 3

    retry_delay: float = 1.0

    # ------------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------------

    response_format: str = "json"

    # ------------------------------------------------------------------------
    # Feature flags
    # ------------------------------------------------------------------------

    enable_llm: bool = True

    enable_streaming: bool = False

    enable_logging: bool = True

    # ------------------------------------------------------------------------
    # Task-specific models
    # ------------------------------------------------------------------------

    models: Dict[str, ModelConfig] = field(
        default_factory=dict
    )

    # ------------------------------------------------------------------------
    # Embeddings
    # ------------------------------------------------------------------------

    embedding: Optional[
        EmbeddingConfig
    ] = None

    def get_model(
        self,
        task: str,
    ) -> ModelConfig:
        """
        Return the model configuration for a task.

        Falls back to the default model.
        """

        if task in self.models:
            return self.models[task]

        return ModelConfig(
            provider=self.default_provider,
            model=self.default_model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            timeout=self.timeout,
            max_retries=self.max_retries,
            response_format=self.response_format,
            enabled=self.enable_llm,
        )

    def validate(self) -> None:
        """Validate all settings."""

        if self.temperature < 0:
            raise ValueError(
                "Temperature cannot be negative."
            )

        if self.max_tokens <= 0:
            raise ValueError(
                "max_tokens must be greater than zero."
            )

        if self.timeout <= 0:
            raise ValueError(
                "timeout must be greater than zero."
            )

        if self.max_retries < 0:
            raise ValueError(
                "max_retries cannot be negative."
            )

        for config in self.models.values():
            config.validate()

        if self.embedding:
            self.embedding.validate()


# ============================================================================
# Environment Configuration
# ============================================================================


def load_settings_from_env() -> LLMSettings:
    """
    Build LLM settings from environment variables.

    Supported variables include:

        LLM_ENABLED
        LLM_PROVIDER
        LLM_MODEL
        LLM_TEMPERATURE
        LLM_MAX_TOKENS
        LLM_TOP_P
        LLM_TIMEOUT
        LLM_MAX_RETRIES
        LLM_RETRY_DELAY

        OPENAI_API_KEY
        OPENAI_BASE_URL
        OPENAI_ORGANIZATION

        EMBEDDING_PROVIDER
        EMBEDDING_MODEL
        EMBEDDING_DIMENSIONS
        EMBEDDING_BATCH_SIZE
    """

    provider = _get_env(
        "LLM_PROVIDER",
        "openai",
    )

    model = _get_env(
        "LLM_MODEL",
        "gpt-4.1-mini",
    )

    default_config = ModelConfig(
        provider=provider or "openai",
        model=model or "gpt-4.1-mini",
        temperature=_get_float(
            "LLM_TEMPERATURE",
            0.2,
        ),
        max_tokens=_get_int(
            "LLM_MAX_TOKENS",
            2000,
        ),
        top_p=_get_float(
            "LLM_TOP_P",
            1.0,
        ),
        timeout=_get_int(
            "LLM_TIMEOUT",
            60,
        ),
        max_retries=_get_int(
            "LLM_MAX_RETRIES",
            3,
        ),
        response_format=_get_env(
            "LLM_RESPONSE_FORMAT",
            "json",
        ) or "json",
        enabled=_get_bool(
            "LLM_ENABLED",
            True,
        ),
    )

    settings = LLMSettings(
        api_key=_get_env(
            "OPENAI_API_KEY"
        ),
        base_url=_get_env(
            "OPENAI_BASE_URL"
        ),
        organization=_get_env(
            "OPENAI_ORGANIZATION"
        ),
        default_model=default_config.model,
        default_provider=default_config.provider,
        temperature=default_config.temperature,
        max_tokens=default_config.max_tokens,
        top_p=default_config.top_p,
        timeout=default_config.timeout,
        max_retries=default_config.max_retries,
        retry_delay=_get_float(
            "LLM_RETRY_DELAY",
            1.0,
        ),
        response_format=default_config.response_format,
        enable_llm=_get_bool(
            "LLM_ENABLED",
            True,
        ),
        enable_streaming=_get_bool(
            "LLM_STREAMING",
            False,
        ),
        enable_logging=_get_bool(
            "LLM_LOGGING",
            True,
        ),
    )

    # ------------------------------------------------------------------------
    # Task-specific configurations
    # ------------------------------------------------------------------------

    settings.models.update(
        {
            "resume_analysis": ModelConfig(
                provider=provider or "openai",
                model=_get_env(
                    "RESUME_MODEL",
                    default_config.model,
                ) or default_config.model,
                temperature=0.1,
                max_tokens=3000,
                timeout=60,
                max_retries=3,
                response_format="json",
            ),
            "resume_extraction": ModelConfig(
                provider=provider or "openai",
                model=_get_env(
                    "RESUME_EXTRACTION_MODEL",
                    default_config.model,
                ) or default_config.model,
                temperature=0.0,
                max_tokens=3000,
                timeout=60,
                max_retries=3,
                response_format="json",
            ),
            "jd_analysis": ModelConfig(
                provider=provider or "openai",
                model=_get_env(
                    "JD_MODEL",
                    default_config.model,
                ) or default_config.model,
                temperature=0.1,
                max_tokens=2500,
                timeout=60,
                max_retries=3,
                response_format="json",
            ),
            "matching": ModelConfig(
                provider=provider or "openai",
                model=_get_env(
                    "MATCHING_MODEL",
                    default_config.model,
                ) or default_config.model,
                temperature=0.1,
                max_tokens=2500,
                timeout=60,
                max_retries=3,
                response_format="json",
            ),
            "ranking": ModelConfig(
                provider=provider or "openai",
                model=_get_env(
                    "RANKING_MODEL",
                    default_config.model,
                ) or default_config.model,
                temperature=0.1,
                max_tokens=3000,
                timeout=60,
                max_retries=3,
                response_format="json",
            ),
            "interview_question": ModelConfig(
                provider=provider or "openai",
                model=_get_env(
                    "INTERVIEW_MODEL",
                    default_config.model,
                ) or default_config.model,
                temperature=0.7,
                max_tokens=1500,
                timeout=60,
                max_retries=3,
                response_format="json",
            ),
            "interview_evaluation": ModelConfig(
                provider=provider or "openai",
                model=_get_env(
                    "INTERVIEW_EVALUATION_MODEL",
                    default_config.model,
                ) or default_config.model,
                temperature=0.1,
                max_tokens=2500,
                timeout=60,
                max_retries=3,
                response_format="json",
            ),
            "resume_optimizer": ModelConfig(
                provider=provider or "openai",
                model=_get_env(
                    "RESUME_OPTIMIZER_MODEL",
                    default_config.model,
                ) or default_config.model,
                temperature=0.4,
                max_tokens=3000,
                timeout=60,
                max_retries=3,
                response_format="json",
            ),
            "copilot": ModelConfig(
                provider=provider or "openai",
                model=_get_env(
                    "COPILOT_MODEL",
                    default_config.model,
                ) or default_config.model,
                temperature=0.4,
                max_tokens=2500,
                timeout=60,
                max_retries=3,
                response_format="json",
            ),
            "analytics": ModelConfig(
                provider=provider or "openai",
                model=_get_env(
                    "ANALYTICS_MODEL",
                    default_config.model,
                ) or default_config.model,
                temperature=0.2,
                max_tokens=2500,
                timeout=60,
                max_retries=3,
                response_format="json",
            ),
        }
    )

    # ------------------------------------------------------------------------
    # Embedding model
    # ------------------------------------------------------------------------

    embedding_provider = _get_env(
        "EMBEDDING_PROVIDER",
        "openai",
    )

    embedding_model = _get_env(
        "EMBEDDING_MODEL",
        "text-embedding-3-small",
    )

    settings.embedding = EmbeddingConfig(
        provider=(
            embedding_provider
            or "openai"
        ),
        model=(
            embedding_model
            or "text-embedding-3-small"
        ),
        dimensions=_get_int(
            "EMBEDDING_DIMENSIONS",
            1536,
        ),
        batch_size=_get_int(
            "EMBEDDING_BATCH_SIZE",
            32,
        ),
        timeout=_get_int(
            "EMBEDDING_TIMEOUT",
            60,
        ),
        max_retries=_get_int(
            "EMBEDDING_MAX_RETRIES",
            3,
        ),
        enabled=_get_bool(
            "EMBEDDING_ENABLED",
            True,
        ),
    )

    settings.validate()

    return settings


# ============================================================================
# Default Settings
# ============================================================================


settings = load_settings_from_env()


# ============================================================================
# Convenience Functions
# ============================================================================


def get_model_config(
    task: Optional[str] = None,
) -> ModelConfig:
    """
    Get model configuration.

    Example:

        config = get_model_config("resume_analysis")
    """

    if task:
        return settings.get_model(
            task
        )

    return settings.get_model(
        "default"
    )


def get_embedding_config() -> EmbeddingConfig:
    """
    Get embedding configuration.
    """

    if settings.embedding is None:
        raise RuntimeError(
            "Embedding configuration is not available."
        )

    return settings.embedding


def is_llm_enabled() -> bool:
    """Return whether LLM functionality is enabled."""

    return settings.enable_llm


def is_streaming_enabled() -> bool:
    """Return whether streaming is enabled."""

    return settings.enable_streaming


def get_api_key() -> Optional[str]:
    """
    Return configured LLM API key.

    Keep this value private and never log it.
    """

    return settings.api_key


# ============================================================================
# Environment Variable Documentation
# ============================================================================


ENVIRONMENT_VARIABLES = {
    "OPENAI_API_KEY": (
        "API key for the configured LLM provider."
    ),
    "OPENAI_BASE_URL": (
        "Optional custom OpenAI-compatible API base URL."
    ),
    "OPENAI_ORGANIZATION": (
        "Optional provider organization identifier."
    ),
    "LLM_ENABLED": (
        "Enable or disable LLM functionality."
    ),
    "LLM_PROVIDER": (
        "Default LLM provider."
    ),
    "LLM_MODEL": (
        "Default LLM model."
    ),
    "LLM_TEMPERATURE": (
        "Default generation temperature."
    ),
    "LLM_MAX_TOKENS": (
        "Default maximum output tokens."
    ),
    "LLM_TOP_P": (
        "Default nucleus sampling value."
    ),
    "LLM_TIMEOUT": (
        "LLM request timeout in seconds."
    ),
    "LLM_MAX_RETRIES": (
        "Maximum number of request retries."
    ),
    "LLM_RETRY_DELAY": (
        "Delay between retries."
    ),
    "LLM_RESPONSE_FORMAT": (
        "Expected response format."
    ),
    "LLM_STREAMING": (
        "Enable streaming responses."
    ),
    "LLM_LOGGING": (
        "Enable LLM request logging."
    ),
    "RESUME_MODEL": (
        "Model used for resume analysis."
    ),
    "RESUME_EXTRACTION_MODEL": (
        "Model used for resume information extraction."
    ),
    "JD_MODEL": (
        "Model used for job-description analysis."
    ),
    "MATCHING_MODEL": (
        "Model used for candidate-job matching."
    ),
    "RANKING_MODEL": (
        "Model used for candidate ranking."
    ),
    "INTERVIEW_MODEL": (
        "Model used for interview question generation."
    ),
    "INTERVIEW_EVALUATION_MODEL": (
        "Model used for interview evaluation."
    ),
    "RESUME_OPTIMIZER_MODEL": (
        "Model used for resume optimization."
    ),
    "COPILOT_MODEL": (
        "Model used by recruiter copilot."
    ),
    "ANALYTICS_MODEL": (
        "Model used for recruiting analytics."
    ),
    "EMBEDDING_PROVIDER": (
        "Embedding provider."
    ),
    "EMBEDDING_MODEL": (
        "Embedding model."
    ),
    "EMBEDDING_DIMENSIONS": (
        "Embedding vector dimensions."
    ),
    "EMBEDDING_BATCH_SIZE": (
        "Embedding batch size."
    ),
    "EMBEDDING_TIMEOUT": (
        "Embedding request timeout."
    ),
    "EMBEDDING_MAX_RETRIES": (
        "Maximum embedding request retries."
    ),
    "EMBEDDING_ENABLED": (
        "Enable or disable embeddings."
    ),
}


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "ModelConfig",
    "EmbeddingConfig",
    "LLMSettings",
    "load_settings_from_env",
    "settings",
    "get_model_config",
    "get_embedding_config",
    "is_llm_enabled",
    "is_streaming_enabled",
    "get_api_key",
    "ENVIRONMENT_VARIABLES",
]