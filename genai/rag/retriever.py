# Project scaffold file
"""
genai/rag/retriever.py

Retriever layer for the RAG pipeline.

Pipeline:

    User Query
        ↓
    Retriever
        ↓
    Query Embedding
        ↓
    Vector Store
        ↓
    Similarity Search
        ↓
    Filtering / Ranking
        ↓
    Relevant Chunks
        ↓
    RAG Pipeline
        ↓
        LLM

Responsibilities:
    - Convert queries into embeddings
    - Search the vector store
    - Filter low-quality results
    - Remove duplicate chunks
    - Optionally filter by metadata
    - Return structured retrieval results
    - Build context for the LLM
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Sequence

from .embeddings import EmbeddingService
from .vector_store import (
    SearchResult,
    VectorStore,
)

logger = logging.getLogger(__name__)


DEFAULT_TOP_K = 5
DEFAULT_MIN_SCORE = 0.20


# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------


class RetrieverError(Exception):
    """Base exception for retriever errors."""


class RetrieverConfigurationError(RetrieverError):
    """Raised when retriever configuration is invalid."""


# ----------------------------------------------------------------------
# Retrieved document
# ----------------------------------------------------------------------


@dataclass
class RetrievedDocument:
    """
    Represents a document retrieved from the vector store.
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

    @property
    def file_name(self) -> str | None:
        return self.metadata.get("file_name")


# ----------------------------------------------------------------------
# Retrieval response
# ----------------------------------------------------------------------


@dataclass
class RetrievalResponse:
    """
    Complete response returned by the retriever.
    """

    query: str
    documents: list[RetrievedDocument]
    top_k: int

    @property
    def count(self) -> int:
        return len(self.documents)

    @property
    def context(self) -> str:
        """
        Combine retrieved documents into context suitable
        for an LLM prompt.
        """

        if not self.documents:
            return ""

        sections: list[str] = []

        for index, document in enumerate(
            self.documents,
            start=1,
        ):
            source = (
                document.file_name
                or document.source
                or "Unknown source"
            )

            sections.append(
                f"[Context {index}]\n"
                f"Source: {source}\n"
                f"Relevance: {document.score:.4f}\n"
                f"{document.content}"
            )

        return "\n\n".join(sections)


# ----------------------------------------------------------------------
# Retriever
# ----------------------------------------------------------------------


class Retriever:
    """
    Semantic retriever for the RAG system.

    Example:

        retriever = Retriever(
            embedding_service=embedding_service,
            vector_store=vector_store,
        )

        response = retriever.retrieve(
            "Python FastAPI experience",
            top_k=5,
        )

        for document in response.documents:
            print(document.content)
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
        default_top_k: int = DEFAULT_TOP_K,
        default_min_score: float | None = DEFAULT_MIN_SCORE,
    ) -> None:

        if default_top_k <= 0:
            raise RetrieverConfigurationError(
                "default_top_k must be greater than zero."
            )

        if (
            default_min_score is not None
            and default_min_score < 0
        ):
            raise RetrieverConfigurationError(
                "default_min_score cannot be negative."
            )

        self.embedding_service = (
            embedding_service
        )

        self.vector_store = vector_store

        self.default_top_k = default_top_k
        self.default_min_score = default_min_score

    # ------------------------------------------------------------------
    # Main retrieval
    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        min_score: float | None = None,
        metadata_filter: dict[str, Any] | None = None,
        deduplicate: bool = True,
    ) -> RetrievalResponse:
        """
        Retrieve relevant chunks for a query.

        Args:
            query:
                Natural-language search query.

            top_k:
                Number of results to return.

            min_score:
                Minimum similarity score.

            metadata_filter:
                Optional metadata constraints.

            deduplicate:
                Remove duplicate chunks.

        Returns:
            RetrievalResponse.
        """

        query = self._validate_query(query)

        top_k = (
            top_k
            if top_k is not None
            else self.default_top_k
        )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        if min_score is None:
            min_score = self.default_min_score

        try:

            query_embedding = (
                self.embedding_service.embed_text(
                    query
                )
            )

            # Retrieve more candidates when metadata filtering
            # or deduplication is requested.
            search_k = top_k

            if metadata_filter or deduplicate:
                search_k = max(
                    top_k * 3,
                    top_k,
                )

            results = self.vector_store.search(
                query_embedding=query_embedding,
                top_k=search_k,
                min_score=min_score,
            )

            if metadata_filter:
                results = self._filter_metadata(
                    results,
                    metadata_filter,
                )

            if deduplicate:
                results = self._deduplicate(
                    results
                )

            results = results[:top_k]

            documents = [
                self._convert_result(result)
                for result in results
            ]

            return RetrievalResponse(
                query=query,
                documents=documents,
                top_k=top_k,
            )

        except RetrieverError:
            raise

        except Exception as exc:

            logger.exception(
                "Retrieval failed for query."
            )

            raise RetrieverError(
                f"Failed to retrieve documents: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Simple retrieval
    # ------------------------------------------------------------------

    def retrieve_documents(
        self,
        query: str,
        top_k: int | None = None,
        min_score: float | None = None,
    ) -> list[RetrievedDocument]:
        """
        Convenience method that returns only documents.
        """

        response = self.retrieve(
            query=query,
            top_k=top_k,
            min_score=min_score,
        )

        return response.documents

    # ------------------------------------------------------------------
    # Context retrieval
    # ------------------------------------------------------------------

    def retrieve_context(
        self,
        query: str,
        top_k: int | None = None,
        min_score: float | None = None,
        metadata_filter: dict[str, Any] | None = None,
    ) -> str:
        """
        Retrieve relevant chunks and return formatted
        context for an LLM prompt.
        """

        response = self.retrieve(
            query=query,
            top_k=top_k,
            min_score=min_score,
            metadata_filter=metadata_filter,
        )

        return response.context

    # ------------------------------------------------------------------
    # Source-specific retrieval
    # ------------------------------------------------------------------

    def retrieve_from_source(
        self,
        query: str,
        source: str,
        top_k: int | None = None,
        min_score: float | None = None,
    ) -> RetrievalResponse:
        """
        Retrieve only chunks belonging to a specific source.
        """

        return self.retrieve(
            query=query,
            top_k=top_k,
            min_score=min_score,
            metadata_filter={
                "source": source,
            },
        )

    def retrieve_from_file(
        self,
        query: str,
        file_name: str,
        top_k: int | None = None,
        min_score: float | None = None,
    ) -> RetrievalResponse:
        """
        Retrieve only chunks belonging to a specific file.
        """

        return self.retrieve(
            query=query,
            top_k=top_k,
            min_score=min_score,
            metadata_filter={
                "file_name": file_name,
            },
        )

    # ------------------------------------------------------------------
    # Resume-specific retrieval
    # ------------------------------------------------------------------

    def retrieve_resume(
        self,
        query: str,
        resume_source: str | None = None,
        top_k: int = 5,
    ) -> RetrievalResponse:
        """
        Resume-focused retrieval.

        Useful for questions such as:

            "What Python experience does this candidate have?"

            "Does this candidate have AWS experience?"

            "What projects did the candidate build?"
        """

        metadata_filter = None

        if resume_source:
            metadata_filter = {
                "source": resume_source,
            }

        return self.retrieve(
            query=query,
            top_k=top_k,
            metadata_filter=metadata_filter,
        )

    # ------------------------------------------------------------------
    # Job-description retrieval
    # ------------------------------------------------------------------

    def retrieve_job_description(
        self,
        query: str,
        job_source: str | None = None,
        top_k: int = 5,
    ) -> RetrievalResponse:
        """
        Retrieve relevant portions of a job description.
        """

        metadata_filter = None

        if job_source:
            metadata_filter = {
                "source": job_source,
            }

        return self.retrieve(
            query=query,
            top_k=top_k,
            metadata_filter=metadata_filter,
        )

    # ------------------------------------------------------------------
    # Metadata filtering
    # ------------------------------------------------------------------

    @staticmethod
    def _filter_metadata(
        results: Sequence[SearchResult],
        metadata_filter: dict[str, Any],
    ) -> list[SearchResult]:
        """
        Filter results by metadata.

        Supports exact matching.
        """

        if not metadata_filter:
            return list(results)

        filtered: list[SearchResult] = []

        for result in results:

            matches = True

            for key, expected_value in (
                metadata_filter.items()
            ):

                actual_value = result.metadata.get(
                    key
                )

                if isinstance(
                    expected_value,
                    (list, tuple, set),
                ):

                    if actual_value not in expected_value:
                        matches = False
                        break

                elif actual_value != expected_value:
                    matches = False
                    break

            if matches:
                filtered.append(result)

        return filtered

    # ------------------------------------------------------------------
    # Deduplication
    # ------------------------------------------------------------------

    @staticmethod
    def _deduplicate(
        results: Sequence[SearchResult],
    ) -> list[SearchResult]:
        """
        Remove duplicate chunks.

        Uses chunk_id when available and falls back
        to content.
        """

        seen_ids: set[str] = set()
        seen_content: set[str] = set()

        unique: list[SearchResult] = []

        for result in results:

            chunk_id = result.metadata.get(
                "chunk_id"
            )

            content_key = (
                result.content.strip().lower()
            )

            if chunk_id:

                if chunk_id in seen_ids:
                    continue

                seen_ids.add(chunk_id)

            elif content_key in seen_content:
                continue

            seen_content.add(content_key)

            unique.append(result)

        return unique

    # ------------------------------------------------------------------
    # Result conversion
    # ------------------------------------------------------------------

    @staticmethod
    def _convert_result(
        result: SearchResult,
    ) -> RetrievedDocument:

        return RetrievedDocument(
            content=result.content,
            score=result.score,
            metadata=dict(result.metadata),
        )

    # ------------------------------------------------------------------
    # Query validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_query(
        query: str,
    ) -> str:

        if not isinstance(query, str):
            raise ValueError(
                "Query must be a string."
            )

        query = query.strip()

        if not query:
            raise ValueError(
                "Query cannot be empty."
            )

        return query


# ----------------------------------------------------------------------
# Multi-query retriever
# ----------------------------------------------------------------------


class MultiQueryRetriever:
    """
    Retrieve documents using multiple queries.

    This is useful when a user question contains multiple
    concepts.

    Example:

        queries = [
            "Python experience",
            "FastAPI experience",
            "PostgreSQL experience",
        ]

    Results are merged and ranked by score.
    """

    def __init__(
        self,
        retriever: Retriever,
    ) -> None:

        self.retriever = retriever

    def retrieve(
        self,
        queries: Sequence[str],
        top_k: int = DEFAULT_TOP_K,
        min_score: float | None = None,
    ) -> RetrievalResponse:
        """
        Retrieve using multiple queries.
        """

        if not queries:
            return RetrievalResponse(
                query="",
                documents=[],
                top_k=top_k,
            )

        all_documents: list[
            RetrievedDocument
        ] = []

        for query in queries:

            response = self.retriever.retrieve(
                query=query,
                top_k=top_k,
                min_score=min_score,
            )

            all_documents.extend(
                response.documents
            )

        unique = self._merge_results(
            all_documents
        )

        unique.sort(
            key=lambda document: document.score,
            reverse=True,
        )

        return RetrievalResponse(
            query=" | ".join(queries),
            documents=unique[:top_k],
            top_k=top_k,
        )

    @staticmethod
    def _merge_results(
        documents: Sequence[RetrievedDocument],
    ) -> list[RetrievedDocument]:

        by_id: dict[str, RetrievedDocument] = {}
        by_content: dict[str, RetrievedDocument] = {}

        for document in documents:

            chunk_id = document.chunk_id

            if chunk_id:

                existing = by_id.get(
                    chunk_id
                )

                if (
                    existing is None
                    or document.score > existing.score
                ):
                    by_id[chunk_id] = document

            else:

                key = document.content.strip().lower()

                existing = by_content.get(key)

                if (
                    existing is None
                    or document.score > existing.score
                ):
                    by_content[key] = document

        return list(by_id.values()) + list(
            by_content.values()
        )


# ----------------------------------------------------------------------
# Convenience factory
# ----------------------------------------------------------------------


def create_retriever(
    embedding_service: EmbeddingService,
    vector_store: VectorStore,
    top_k: int = DEFAULT_TOP_K,
    min_score: float | None = DEFAULT_MIN_SCORE,
) -> Retriever:
    """
    Create a configured Retriever.
    """

    return Retriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
        default_top_k=top_k,
        default_min_score=min_score,
    )


__all__ = [
    "Retriever",
    "MultiQueryRetriever",
    "RetrievedDocument",
    "RetrievalResponse",
    "RetrieverError",
    "RetrieverConfigurationError",
    "create_retriever",
]