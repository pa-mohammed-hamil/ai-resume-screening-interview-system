# Project scaffold file
"""
genai/rag/vector_store.py

Vector storage and similarity search for the RAG pipeline.

Pipeline:

    DocumentLoader
          ↓
       Chunker
          ↓
      Embeddings
          ↓
    VectorStore
          ↓
      Retriever
          ↓
    RAG Pipeline
          ↓
         LLM

Backend:
    FAISS

The vector store maintains:
    - FAISS vector index
    - Document chunk metadata
    - Original chunk text
    - Similarity search
    - Persistent save/load
"""

from __future__ import annotations

import json
import logging
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from .embeddings import EmbeddedChunk

logger = logging.getLogger(__name__)


DEFAULT_TOP_K = 5


# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------


class VectorStoreError(Exception):
    """Base exception for vector-store errors."""


class VectorStoreConfigurationError(VectorStoreError):
    """Raised when vector-store configuration is invalid."""


class VectorStoreNotFoundError(VectorStoreError):
    """Raised when a vector store cannot be found."""


# ----------------------------------------------------------------------
# Search result
# ----------------------------------------------------------------------


@dataclass
class SearchResult:
    """
    Result returned by similarity search.
    """

    content: str
    score: float
    metadata: dict[str, Any]

    @property
    def chunk_id(self) -> str | None:
        return self.metadata.get("chunk_id")

    @property
    def source(self) -> str | None:
        return self.metadata.get("source")


# ----------------------------------------------------------------------
# FAISS Vector Store
# ----------------------------------------------------------------------


class FAISSVectorStore:
    """
    FAISS-based vector store.

    Example:

        store = FAISSVectorStore(
            dimension=1536,
            index_path="storage/vector_store"
        )

        store.add_chunks(embedded_chunks)

        results = store.search(
            query_embedding,
            top_k=5
        )

        store.save()
    """

    INDEX_FILE = "index.faiss"
    METADATA_FILE = "metadata.json"

    def __init__(
        self,
        dimension: int,
        index_path: str | Path = "storage/vector_store",
        metric: str = "cosine",
    ) -> None:

        if dimension <= 0:
            raise ValueError(
                "Vector dimension must be greater than zero."
            )

        if metric not in {
            "cosine",
            "l2",
            "ip",
        }:
            raise ValueError(
                "metric must be one of: "
                "cosine, l2, ip"
            )

        self.dimension = dimension
        self.index_path = Path(index_path)
        self.metric = metric

        self._faiss = self._load_faiss()

        self.index = self._create_index()

        self.metadata: list[dict[str, Any]] = []

        self.texts: list[str] = []

    # ------------------------------------------------------------------
    # FAISS
    # ------------------------------------------------------------------

    @staticmethod
    def _load_faiss():

        try:
            import faiss

            return faiss

        except ImportError as exc:
            raise VectorStoreConfigurationError(
                "FAISS is required. Install it with:\n"
                "pip install faiss-cpu"
            ) from exc

    def _create_index(self):

        if self.metric == "cosine":
            # Cosine similarity is implemented using normalized
            # vectors + inner product.
            return self._faiss.IndexFlatIP(
                self.dimension
            )

        if self.metric == "ip":
            return self._faiss.IndexFlatIP(
                self.dimension
            )

        return self._faiss.IndexFlatL2(
            self.dimension
        )

    # ------------------------------------------------------------------
    # Add vectors
    # ------------------------------------------------------------------

    def add_chunk(
        self,
        chunk: EmbeddedChunk,
    ) -> int:
        """
        Add one embedded chunk.

        Returns:
            Integer vector ID.
        """

        return self.add_chunks([chunk])[0]

    def add_chunks(
        self,
        chunks: Sequence[EmbeddedChunk],
    ) -> list[int]:
        """
        Add multiple embedded chunks.
        """

        if not chunks:
            return []

        vectors = np.asarray(
            [
                chunk.embedding
                for chunk in chunks
            ],
            dtype="float32",
        )

        self._validate_vectors(vectors)

        if self.metric == "cosine":
            vectors = self._normalize_vectors(
                vectors
            )

        start_id = self.index.ntotal

        self.index.add(vectors)

        ids = list(
            range(
                start_id,
                start_id + len(chunks),
            )
        )

        for chunk in chunks:

            self.metadata.append(
                dict(chunk.metadata)
            )

            self.texts.append(
                chunk.content
            )

        return ids

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        query_embedding: Sequence[float],
        top_k: int = DEFAULT_TOP_K,
        min_score: float | None = None,
    ) -> list[SearchResult]:
        """
        Perform similarity search.

        Args:
            query_embedding:
                Query vector.

            top_k:
                Maximum number of results.

            min_score:
                Optional minimum similarity score.

        Returns:
            Ranked search results.
        """

        if top_k <= 0:
            return []

        if self.index.ntotal == 0:
            return []

        query = np.asarray(
            [query_embedding],
            dtype="float32",
        )

        self._validate_vectors(query)

        if self.metric == "cosine":
            query = self._normalize_vectors(
                query
            )

        actual_k = min(
            top_k,
            self.index.ntotal,
        )

        scores, indices = self.index.search(
            query,
            actual_k,
        )

        results: list[SearchResult] = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):

            if index < 0:
                continue

            score = float(score)

            if (
                min_score is not None
                and score < min_score
            ):
                continue

            if index >= len(self.metadata):
                logger.warning(
                    "Vector index %s has no metadata.",
                    index,
                )
                continue

            results.append(
                SearchResult(
                    content=self.texts[index],
                    score=score,
                    metadata=dict(
                        self.metadata[index]
                    ),
                )
            )

        return results

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete_by_chunk_id(
        self,
        chunk_id: str,
    ) -> int:
        """
        Remove chunks matching a chunk_id.

        FAISS IndexFlat does not support arbitrary deletion
        without rebuilding the index, so the index is rebuilt.
        """

        indexes_to_keep = []

        deleted = 0

        for index, metadata in enumerate(
            self.metadata
        ):

            if metadata.get("chunk_id") == chunk_id:
                deleted += 1
            else:
                indexes_to_keep.append(index)

        if deleted == 0:
            return 0

        self._rebuild(
            indexes_to_keep
        )

        return deleted

    def delete_by_source(
        self,
        source: str,
    ) -> int:
        """
        Delete all chunks belonging to a source document.
        """

        indexes_to_keep = []

        deleted = 0

        for index, metadata in enumerate(
            self.metadata
        ):

            if metadata.get("source") == source:
                deleted += 1
            else:
                indexes_to_keep.append(index)

        if deleted == 0:
            return 0

        self._rebuild(
            indexes_to_keep
        )

        return deleted

    # ------------------------------------------------------------------
    # Rebuild
    # ------------------------------------------------------------------

    def _rebuild(
        self,
        indexes_to_keep: Sequence[int],
    ) -> None:

        if indexes_to_keep:

            old_vectors = self._get_vectors()

            vectors = old_vectors[
                list(indexes_to_keep)
            ]

            if vectors.size:

                self.index = self._create_index()

                self.index.add(
                    vectors.astype("float32")
                )

        else:
            self.index = self._create_index()

        self.metadata = [
            self.metadata[index]
            for index in indexes_to_keep
        ]

        self.texts = [
            self.texts[index]
            for index in indexes_to_keep
        ]

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(
        self,
        path: str | Path | None = None,
    ) -> Path:
        """
        Persist FAISS index and metadata to disk.
        """

        directory = Path(
            path
            if path is not None
            else self.index_path
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        index_file = (
            directory / self.INDEX_FILE
        )

        metadata_file = (
            directory / self.METADATA_FILE
        )

        try:

            self._faiss.write_index(
                self.index,
                str(index_file),
            )

            payload = {
                "dimension": self.dimension,
                "metric": self.metric,
                "metadata": self.metadata,
                "texts": self.texts,
                "count": self.index.ntotal,
            }

            metadata_file.write_text(
                json.dumps(
                    payload,
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            logger.info(
                "Vector store saved to %s",
                directory,
            )

            return directory

        except Exception as exc:

            logger.exception(
                "Failed to save vector store."
            )

            raise VectorStoreError(
                f"Failed to save vector store: {exc}"
            ) from exc

    @classmethod
    def load(
        cls,
        path: str | Path,
    ) -> "FAISSVectorStore":
        """
        Load a previously persisted vector store.
        """

        directory = Path(path)

        index_file = (
            directory / cls.INDEX_FILE
        )

        metadata_file = (
            directory / cls.METADATA_FILE
        )

        if not index_file.exists():
            raise VectorStoreNotFoundError(
                f"FAISS index not found: {index_file}"
            )

        if not metadata_file.exists():
            raise VectorStoreNotFoundError(
                f"Metadata not found: {metadata_file}"
            )

        try:

            payload = json.loads(
                metadata_file.read_text(
                    encoding="utf-8"
                )
            )

            store = cls(
                dimension=int(
                    payload["dimension"]
                ),
                index_path=directory,
                metric=payload.get(
                    "metric",
                    "cosine",
                ),
            )

            store.index = (
                store._faiss.read_index(
                    str(index_file)
                )
            )

            store.metadata = payload.get(
                "metadata",
                [],
            )

            store.texts = payload.get(
                "texts",
                [],
            )

            if store.index.ntotal != len(
                store.metadata
            ):
                raise VectorStoreError(
                    "Vector count and metadata count "
                    "do not match."
                )

            if store.index.ntotal != len(
                store.texts
            ):
                raise VectorStoreError(
                    "Vector count and text count "
                    "do not match."
                )

            return store

        except VectorStoreError:
            raise

        except Exception as exc:

            logger.exception(
                "Failed to load vector store."
            )

            raise VectorStoreError(
                f"Failed to load vector store: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Information
    # ------------------------------------------------------------------

    def count(self) -> int:
        """Return number of stored vectors."""

        return int(self.index.ntotal)

    def is_empty(self) -> bool:
        """Return True if no vectors are stored."""

        return self.index.ntotal == 0

    def clear(self) -> None:
        """Remove all vectors and metadata."""

        self.index = self._create_index()

        self.metadata.clear()

        self.texts.clear()

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------

    def _get_vectors(self) -> np.ndarray:
        """
        Extract all vectors from an IndexFlat index.

        This is mainly used when rebuilding the index after deletion.
        """

        if self.index.ntotal == 0:
            return np.empty(
                (0, self.dimension),
                dtype="float32",
            )

        return np.asarray(
            self.index.reconstruct_n(
                0,
                self.index.ntotal,
            ),
            dtype="float32",
        )

    def _validate_vectors(
        self,
        vectors: np.ndarray,
    ) -> None:

        if vectors.ndim != 2:
            raise ValueError(
                "Vectors must be a 2D array."
            )

        if vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Embedding dimension mismatch. "
                f"Expected {self.dimension}, "
                f"received {vectors.shape[1]}."
            )

        if not np.isfinite(vectors).all():
            raise ValueError(
                "Embedding vectors contain "
                "NaN or infinite values."
            )

    @staticmethod
    def _normalize_vectors(
        vectors: np.ndarray,
    ) -> np.ndarray:

        norms = np.linalg.norm(
            vectors,
            axis=1,
            keepdims=True,
        )

        norms = np.maximum(
            norms,
            1e-12,
        )

        return vectors / norms


# ----------------------------------------------------------------------
# High-level VectorStore service
# ----------------------------------------------------------------------


class VectorStore:
    """
    High-level wrapper around FAISSVectorStore.

    This class is the interface that retriever.py should normally use.
    """

    def __init__(
        self,
        dimension: int,
        path: str | Path = "storage/vector_store",
        metric: str = "cosine",
    ) -> None:

        self.store = FAISSVectorStore(
            dimension=dimension,
            index_path=path,
            metric=metric,
        )

    def add(
        self,
        chunks: Sequence[EmbeddedChunk],
    ) -> list[int]:

        return self.store.add_chunks(
            chunks
        )

    def search(
        self,
        query_embedding: Sequence[float],
        top_k: int = DEFAULT_TOP_K,
        min_score: float | None = None,
    ) -> list[SearchResult]:

        return self.store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            min_score=min_score,
        )

    def delete_source(
        self,
        source: str,
    ) -> int:

        return self.store.delete_by_source(
            source
        )

    def delete_chunk(
        self,
        chunk_id: str,
    ) -> int:

        return self.store.delete_by_chunk_id(
            chunk_id
        )

    def save(self) -> Path:

        return self.store.save()

    def count(self) -> int:

        return self.store.count()

    def clear(self) -> None:

        self.store.clear()


# ----------------------------------------------------------------------
# Factory
# ----------------------------------------------------------------------


def create_vector_store(
    dimension: int,
    path: str | Path | None = None,
    metric: str = "cosine",
) -> VectorStore:
    """
    Create a VectorStore using environment configuration.

    Environment:

        VECTOR_STORE_PATH=storage/vector_store
    """

    store_path = (
        path
        or os.getenv(
            "VECTOR_STORE_PATH",
            "storage/vector_store",
        )
    )

    return VectorStore(
        dimension=dimension,
        path=store_path,
        metric=metric,
    )


__all__ = [
    "SearchResult",
    "VectorStore",
    "FAISSVectorStore",
    "VectorStoreError",
    "VectorStoreConfigurationError",
    "VectorStoreNotFoundError",
    "create_vector_store",
]