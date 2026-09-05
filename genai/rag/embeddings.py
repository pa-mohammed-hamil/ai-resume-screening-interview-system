# Project scaffold file
"""
genai/rag/embeddings.py

Embedding generation for the RAG pipeline.

Pipeline:

    DocumentLoader
          ↓
       Chunker
          ↓
     Embeddings
          ↓
    Vector Store
          ↓
      Retriever
          ↓
    RAG Pipeline

This module provides:
    - EmbeddingProvider interface
    - OpenAIEmbeddingProvider
    - LocalEmbeddingProvider
    - EmbeddingService
    - Batch embedding
    - Query embedding
    - Document/chunk embedding
"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Sequence

from .chunker import DocumentChunk

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

DEFAULT_MODEL = "text-embedding-3-small"
DEFAULT_BATCH_SIZE = 64


# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------


class EmbeddingError(Exception):
    """Base exception for embedding-related errors."""


class EmbeddingConfigurationError(EmbeddingError):
    """Raised when the embedding provider is incorrectly configured."""


class EmbeddingProviderError(EmbeddingError):
    """Raised when an embedding provider fails."""


# ----------------------------------------------------------------------
# Result objects
# ----------------------------------------------------------------------


@dataclass
class EmbeddedChunk:
    """
    A document chunk together with its vector embedding.
    """

    content: str
    embedding: list[float]
    metadata: dict

    @property
    def chunk_id(self) -> str | None:
        return self.metadata.get("chunk_id")


# ----------------------------------------------------------------------
# Provider interface
# ----------------------------------------------------------------------


class EmbeddingProvider(ABC):
    """
    Abstract embedding provider.

    Any embedding backend used by the application should implement
    this interface.
    """

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Generate an embedding for one text."""

    @abstractmethod
    def embed_texts(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts."""

    @abstractmethod
    def dimension(self) -> int:
        """Return embedding vector dimension."""


# ----------------------------------------------------------------------
# OpenAI provider
# ----------------------------------------------------------------------


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    OpenAI embedding provider.

    Requires:

        OPENAI_API_KEY

    Optional:

        EMBEDDING_MODEL

    Example:

        provider = OpenAIEmbeddingProvider()

        vector = provider.embed_text(
            "Python FastAPI developer"
        )
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        dimensions: int | None = None,
    ) -> None:

        self.api_key = (
            api_key
            or os.getenv("OPENAI_API_KEY")
        )

        if not self.api_key:
            raise EmbeddingConfigurationError(
                "OPENAI_API_KEY is not configured."
            )

        self.model = (
            model
            or os.getenv(
                "EMBEDDING_MODEL",
                DEFAULT_MODEL,
            )
        )

        self.dimensions = dimensions

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise EmbeddingConfigurationError(
                "The OpenAI package is required. "
                "Install it with: pip install openai"
            ) from exc

        self.client = OpenAI(
            api_key=self.api_key,
        )

        self._dimension: int | None = None

    def embed_text(
        self,
        text: str,
    ) -> list[float]:

        embeddings = self.embed_texts([text])

        if not embeddings:
            raise EmbeddingProviderError(
                "No embedding was returned."
            )

        return embeddings[0]

    def embed_texts(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:

        if not texts:
            return []

        cleaned_texts = [
            self._prepare_text(text)
            for text in texts
        ]

        try:
            kwargs = {
                "model": self.model,
                "input": cleaned_texts,
            }

            if self.dimensions is not None:
                kwargs["dimensions"] = self.dimensions

            response = self.client.embeddings.create(
                **kwargs
            )

            # OpenAI normally returns embeddings in input order,
            # but sort explicitly by index for safety.
            data = sorted(
                response.data,
                key=lambda item: item.index,
            )

            vectors = [
                list(item.embedding)
                for item in data
            ]

            if vectors:
                self._dimension = len(vectors[0])

            return vectors

        except Exception as exc:
            logger.exception(
                "OpenAI embedding generation failed."
            )

            raise EmbeddingProviderError(
                f"Failed to generate embeddings: {exc}"
            ) from exc

    def dimension(self) -> int:
        """
        Return vector dimension.

        If no embedding has been generated yet, the dimension is
        obtained by embedding a small probe string.
        """

        if self._dimension is None:
            self.embed_text("embedding dimension probe")

        if self._dimension is None:
            raise EmbeddingProviderError(
                "Unable to determine embedding dimension."
            )

        return self._dimension

    @staticmethod
    def _prepare_text(text: str) -> str:

        if not isinstance(text, str):
            text = str(text)

        text = text.strip()

        if not text:
            raise ValueError(
                "Cannot create an embedding for empty text."
            )

        return text


# ----------------------------------------------------------------------
# Local Sentence Transformer provider
# ----------------------------------------------------------------------


class LocalEmbeddingProvider(EmbeddingProvider):
    """
    Local embedding provider using Sentence Transformers.

    Example:

        provider = LocalEmbeddingProvider(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    """

    def __init__(
        self,
        model_name: str = (
            "sentence-transformers/all-MiniLM-L6-v2"
        ),
        device: str | None = None,
    ) -> None:

        try:
            from sentence_transformers import (
                SentenceTransformer,
            )
        except ImportError as exc:
            raise EmbeddingConfigurationError(
                "sentence-transformers is required for "
                "LocalEmbeddingProvider. "
                "Install it with: "
                "pip install sentence-transformers"
            ) from exc

        try:
            self.model = SentenceTransformer(
                model_name,
                device=device,
            )

        except Exception as exc:
            raise EmbeddingProviderError(
                f"Failed to load local embedding model: {exc}"
            ) from exc

        self.model_name = model_name
        self._dimension = int(
            self.model.get_sentence_embedding_dimension()
        )

    def embed_text(
        self,
        text: str,
    ) -> list[float]:

        return self.embed_texts([text])[0]

    def embed_texts(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:

        if not texts:
            return []

        cleaned = [
            self._prepare_text(text)
            for text in texts
        ]

        try:
            vectors = self.model.encode(
                cleaned,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )

            return [
                vector.astype(float).tolist()
                for vector in vectors
            ]

        except Exception as exc:
            logger.exception(
                "Local embedding generation failed."
            )

            raise EmbeddingProviderError(
                f"Failed to generate local embeddings: {exc}"
            ) from exc

    def dimension(self) -> int:
        return self._dimension

    @staticmethod
    def _prepare_text(text: str) -> str:

        if not isinstance(text, str):
            text = str(text)

        text = text.strip()

        if not text:
            raise ValueError(
                "Cannot create an embedding for empty text."
            )

        return text


# ----------------------------------------------------------------------
# Embedding service
# ----------------------------------------------------------------------


class EmbeddingService:
    """
    High-level embedding service used by the RAG pipeline.

    It hides provider-specific implementation details from the rest
    of the application.

    Example:

        service = EmbeddingService(
            provider=OpenAIEmbeddingProvider()
        )

        vectors = service.embed_texts(
            ["Python", "FastAPI", "PostgreSQL"]
        )
    """

    def __init__(
        self,
        provider: EmbeddingProvider,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:

        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than zero."
            )

        self.provider = provider
        self.batch_size = batch_size

    # ------------------------------------------------------------------
    # Text embedding
    # ------------------------------------------------------------------

    def embed_text(
        self,
        text: str,
    ) -> list[float]:

        return self.provider.embed_text(text)

    def embed_texts(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:

        if not texts:
            return []

        results: list[list[float]] = []

        for batch in self._batches(
            texts,
            self.batch_size,
        ):
            results.extend(
                self.provider.embed_texts(batch)
            )

        return results

    # ------------------------------------------------------------------
    # Chunk embedding
    # ------------------------------------------------------------------

    def embed_chunk(
        self,
        chunk: DocumentChunk,
    ) -> EmbeddedChunk:

        vector = self.embed_text(
            chunk.content
        )

        return EmbeddedChunk(
            content=chunk.content,
            embedding=vector,
            metadata=dict(chunk.metadata),
        )

    def embed_chunks(
        self,
        chunks: Sequence[DocumentChunk],
    ) -> list[EmbeddedChunk]:

        if not chunks:
            return []

        texts = [
            chunk.content
            for chunk in chunks
        ]

        vectors = self.embed_texts(texts)

        if len(vectors) != len(chunks):
            raise EmbeddingProviderError(
                "Number of embeddings does not match "
                "number of chunks."
            )

        return [
            EmbeddedChunk(
                content=chunk.content,
                embedding=vector,
                metadata=dict(chunk.metadata),
            )
            for chunk, vector in zip(
                chunks,
                vectors,
            )
        ]

    # ------------------------------------------------------------------
    # Dimension
    # ------------------------------------------------------------------

    def dimension(self) -> int:
        """Return embedding vector dimension."""

        return self.provider.dimension()

    # ------------------------------------------------------------------
    # Batch utility
    # ------------------------------------------------------------------

    @staticmethod
    def _batches(
        items: Sequence[str],
        batch_size: int,
    ):

        for start in range(
            0,
            len(items),
            batch_size,
        ):
            yield items[
                start:start + batch_size
            ]


# ----------------------------------------------------------------------
# Factory
# ----------------------------------------------------------------------


def create_embedding_service(
    provider: str | None = None,
    model: str | None = None,
) -> EmbeddingService:
    """
    Create an embedding service from configuration.

    Supported providers:

        openai
        local

    Environment variables:

        EMBEDDING_PROVIDER=openai
        EMBEDDING_MODEL=text-embedding-3-small
    """

    provider_name = (
        provider
        or os.getenv(
            "EMBEDDING_PROVIDER",
            "openai",
        )
    ).lower()

    if provider_name == "openai":

        embedding_provider = (
            OpenAIEmbeddingProvider(
                model=model,
            )
        )

    elif provider_name == "local":

        embedding_provider = (
            LocalEmbeddingProvider(
                model_name=(
                    model
                    or os.getenv(
                        "LOCAL_EMBEDDING_MODEL",
                        "sentence-transformers/"
                        "all-MiniLM-L6-v2",
                    )
                )
            )
        )

    else:
        raise EmbeddingConfigurationError(
            f"Unsupported embedding provider: "
            f"{provider_name}"
        )

    return EmbeddingService(
        provider=embedding_provider
    )


# ----------------------------------------------------------------------
# Convenience functions
# ----------------------------------------------------------------------


def embed_text(
    text: str,
    provider: str | None = None,
) -> list[float]:
    """
    Generate an embedding for one text.
    """

    service = create_embedding_service(
        provider=provider
    )

    return service.embed_text(text)


def embed_texts(
    texts: Sequence[str],
    provider: str | None = None,
) -> list[list[float]]:
    """
    Generate embeddings for multiple texts.
    """

    service = create_embedding_service(
        provider=provider
    )

    return service.embed_texts(texts)


def embed_chunks(
    chunks: Sequence[DocumentChunk],
    provider: str | None = None,
) -> list[EmbeddedChunk]:
    """
    Generate embeddings for document chunks.
    """

    service = create_embedding_service(
        provider=provider
    )

    return service.embed_chunks(chunks)


__all__ = [
    "EmbeddingProvider",
    "OpenAIEmbeddingProvider",
    "LocalEmbeddingProvider",
    "EmbeddingService",
    "EmbeddedChunk",
    "EmbeddingError",
    "EmbeddingConfigurationError",
    "EmbeddingProviderError",
    "create_embedding_service",
    "embed_text",
    "embed_texts",
    "embed_chunks",
]