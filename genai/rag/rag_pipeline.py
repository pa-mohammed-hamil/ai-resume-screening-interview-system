# Project scaffold file
"""
genai/rag/rag_pipeline.py

End-to-end Retrieval-Augmented Generation (RAG) pipeline.

Pipeline:

    Documents
        ↓
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
    Retrieved Context
        ↓
    LLM
        ↓
    Grounded Response

Responsibilities:
    - Ingest documents
    - Chunk documents
    - Generate embeddings
    - Store vectors
    - Retrieve relevant context
    - Build grounded prompts
    - Generate LLM responses
    - Return sources and retrieval information
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

from .chunker import DocumentChunk, TextChunker
from .document_loader import Document, DocumentLoader
from .embeddings import (
    EmbeddedChunk,
    EmbeddingService,
)
from .retriever import (
    RetrievedDocument,
    RetrievalResponse,
    Retriever,
)
from .vector_store import VectorStore

logger = logging.getLogger(__name__)


DEFAULT_TOP_K = 5
DEFAULT_MIN_SCORE = 0.20


# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------


class RAGPipelineError(Exception):
    """Base exception for RAG pipeline errors."""


class RAGConfigurationError(RAGPipelineError):
    """Raised when RAG configuration is invalid."""


class RAGGenerationError(RAGPipelineError):
    """Raised when LLM generation fails."""


# ----------------------------------------------------------------------
# LLM interface
# ----------------------------------------------------------------------


class LLMProvider:
    """
    Minimal interface expected from an LLM provider.

    Your existing genai/llm/client.py can implement this interface.

    Required method:

        generate(prompt: str) -> str
    """

    def generate(self, prompt: str) -> str:
        raise NotImplementedError


# ----------------------------------------------------------------------
# RAG response
# ----------------------------------------------------------------------


@dataclass
class RAGSource:
    """
    Source citation information returned with a RAG response.
    """

    content: str
    score: float
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def chunk_id(self) -> str | None:
        return self.metadata.get("chunk_id")

    @property
    def file_name(self) -> str | None:
        return self.metadata.get("file_name")

    @property
    def source(self) -> str | None:
        return self.metadata.get("source")


@dataclass
class RAGResponse:
    """
    Complete RAG response.
    """

    question: str
    answer: str
    sources: list[RAGSource]
    context: str
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def source_count(self) -> int:
        return len(self.sources)


# ----------------------------------------------------------------------
# RAG Pipeline
# ----------------------------------------------------------------------


class RAGPipeline:
    """
    End-to-end RAG orchestration service.

    Example:

        pipeline = RAGPipeline(
            document_loader=loader,
            chunker=chunker,
            embedding_service=embedding_service,
            vector_store=vector_store,
            retriever=retriever,
            llm=llm,
        )

        pipeline.ingest_file(
            "data/raw/resumes/resume.pdf"
        )

        response = pipeline.ask(
            "Does the candidate know Python?"
        )

        print(response.answer)
    """

    def __init__(
        self,
        document_loader: DocumentLoader,
        chunker: TextChunker,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
        retriever: Retriever,
        llm: LLMProvider,
        top_k: int = DEFAULT_TOP_K,
        min_score: float | None = DEFAULT_MIN_SCORE,
        system_prompt: str | None = None,
    ) -> None:

        if top_k <= 0:
            raise RAGConfigurationError(
                "top_k must be greater than zero."
            )

        self.document_loader = document_loader
        self.chunker = chunker
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.retriever = retriever
        self.llm = llm

        self.top_k = top_k
        self.min_score = min_score

        self.system_prompt = (
            system_prompt
            or self._default_system_prompt()
        )

    # ==================================================================
    # DOCUMENT INGESTION
    # ==================================================================

    def ingest_file(
        self,
        path: str | Path,
        save: bool = True,
    ) -> list[DocumentChunk]:
        """
        Load, chunk, embed, and store one document.

        Args:
            path:
                Document path.

            save:
                Persist vector store after ingestion.

        Returns:
            Created document chunks.
        """

        logger.info(
            "Starting ingestion: %s",
            path,
        )

        document = (
            self.document_loader.load_file(path)
        )

        return self.ingest_document(
            document=document,
            save=save,
        )

    def ingest_directory(
        self,
        directory: str | Path,
        save: bool = True,
    ) -> list[DocumentChunk]:
        """
        Ingest all supported documents in a directory.
        """

        logger.info(
            "Starting directory ingestion: %s",
            directory,
        )

        documents = (
            self.document_loader.load_directory(
                directory
            )
        )

        return self.ingest_documents(
            documents=documents,
            save=save,
        )

    def ingest_document(
        self,
        document: Document,
        save: bool = True,
    ) -> list[DocumentChunk]:
        """
        Ingest one already-loaded Document.
        """

        chunks = self.chunker.chunk_document(
            document
        )

        if not chunks:
            logger.warning(
                "No chunks generated for document."
            )
            return []

        embedded_chunks = (
            self.embedding_service.embed_chunks(
                chunks
            )
        )

        self.vector_store.add(
            embedded_chunks
        )

        if save:
            self.vector_store.save()

        logger.info(
            "Ingested %d chunks from %s",
            len(chunks),
            document.metadata.get(
                "file_name",
                "document",
            ),
        )

        return chunks

    def ingest_documents(
        self,
        documents: Iterable[Document],
        save: bool = True,
    ) -> list[DocumentChunk]:
        """
        Ingest multiple documents.
        """

        documents = list(documents)

        if not documents:
            return []

        all_chunks: list[DocumentChunk] = []

        for document in documents:

            chunks = self.chunker.chunk_document(
                document
            )

            all_chunks.extend(chunks)

        if not all_chunks:
            return []

        embedded_chunks = (
            self.embedding_service.embed_chunks(
                all_chunks
            )
        )

        self.vector_store.add(
            embedded_chunks
        )

        if save:
            self.vector_store.save()

        logger.info(
            "Ingested %d chunks from %d documents.",
            len(all_chunks),
            len(documents),
        )

        return all_chunks

    # ==================================================================
    # DOCUMENT MANAGEMENT
    # ==================================================================

    def delete_source(
        self,
        source: str,
        save: bool = True,
    ) -> int:
        """
        Delete all vectors associated with a source.
        """

        deleted = (
            self.vector_store.delete_source(
                source
            )
        )

        if deleted and save:
            self.vector_store.save()

        return deleted

    def clear_vector_store(
        self,
        save: bool = True,
    ) -> None:
        """
        Clear the entire vector store.
        """

        self.vector_store.clear()

        if save:
            self.vector_store.save()

    # ==================================================================
    # QUESTION ANSWERING
    # ==================================================================

    def ask(
        self,
        question: str,
        top_k: int | None = None,
        min_score: float | None = None,
        metadata_filter: dict[str, Any] | None = None,
    ) -> RAGResponse:
        """
        Ask a question using retrieved context.

        Args:
            question:
                User's natural-language question.

            top_k:
                Number of chunks to retrieve.

            min_score:
                Minimum retrieval similarity.

            metadata_filter:
                Optional metadata filter.

        Returns:
            RAGResponse.
        """

        question = self._validate_question(
            question
        )

        top_k = (
            top_k
            if top_k is not None
            else self.top_k
        )

        if min_score is None:
            min_score = self.min_score

        logger.info(
            "RAG question: %s",
            question,
        )

        retrieval = self.retriever.retrieve(
            query=question,
            top_k=top_k,
            min_score=min_score,
            metadata_filter=metadata_filter,
        )

        context = retrieval.context

        prompt = self.build_prompt(
            question=question,
            context=context,
        )

        answer = self._generate(
            prompt
        )

        sources = [
            self._source_from_document(
                document
            )
            for document in retrieval.documents
        ]

        return RAGResponse(
            question=question,
            answer=answer,
            sources=sources,
            context=context,
            metadata={
                "retrieved_count": retrieval.count,
                "top_k": top_k,
                "min_score": min_score,
            },
        )

    # ==================================================================
    # CONTEXT-ONLY RETRIEVAL
    # ==================================================================

    def retrieve(
        self,
        question: str,
        top_k: int | None = None,
        min_score: float | None = None,
        metadata_filter: dict[str, Any] | None = None,
    ) -> RetrievalResponse:
        """
        Retrieve context without calling the LLM.
        """

        return self.retriever.retrieve(
            query=question,
            top_k=(
                top_k
                if top_k is not None
                else self.top_k
            ),
            min_score=(
                min_score
                if min_score is not None
                else self.min_score
            ),
            metadata_filter=metadata_filter,
        )

    def get_context(
        self,
        question: str,
        top_k: int | None = None,
        min_score: float | None = None,
        metadata_filter: dict[str, Any] | None = None,
    ) -> str:
        """
        Retrieve only the formatted context.
        """

        response = self.retrieve(
            question=question,
            top_k=top_k,
            min_score=min_score,
            metadata_filter=metadata_filter,
        )

        return response.context

    # ==================================================================
    # PROMPT BUILDING
    # ==================================================================

    def build_prompt(
        self,
        question: str,
        context: str,
    ) -> str:
        """
        Build a grounded prompt for the LLM.
        """

        if context.strip():

            return f"""
{self.system_prompt}

CONTEXT:
--------------------
{context}
--------------------

QUESTION:
{question}

INSTRUCTIONS:
1. Answer using the provided context.
2. Do not invent candidate information.
3. If the answer is not present in the context,
   explicitly say that the information was not found.
4. Prefer specific evidence from the context.
5. Keep the answer clear and concise.

ANSWER:
""".strip()

        return f"""
{self.system_prompt}

There is no relevant information available
in the knowledge base.

QUESTION:
{question}

INSTRUCTIONS:
Do not invent an answer. State that the requested
information was not found in the available documents.

ANSWER:
""".strip()

    # ==================================================================
    # LLM
    # ==================================================================

    def _generate(
        self,
        prompt: str,
    ) -> str:
        """
        Generate an answer using the configured LLM.
        """

        try:

            answer = self.llm.generate(
                prompt
            )

        except Exception as exc:

            logger.exception(
                "LLM generation failed."
            )

            raise RAGGenerationError(
                f"LLM generation failed: {exc}"
            ) from exc

        if answer is None:
            raise RAGGenerationError(
                "LLM returned no response."
            )

        answer = str(answer).strip()

        if not answer:
            raise RAGGenerationError(
                "LLM returned an empty response."
            )

        return answer

    # ==================================================================
    # SOURCE CONVERSION
    # ==================================================================

    @staticmethod
    def _source_from_document(
        document: RetrievedDocument,
    ) -> RAGSource:

        return RAGSource(
            content=document.content,
            score=document.score,
            metadata=dict(
                document.metadata
            ),
        )

    # ==================================================================
    # VALIDATION
    # ==================================================================

    @staticmethod
    def _validate_question(
        question: str,
    ) -> str:

        if not isinstance(question, str):
            raise ValueError(
                "Question must be a string."
            )

        question = question.strip()

        if not question:
            raise ValueError(
                "Question cannot be empty."
            )

        return question

    @staticmethod
    def _default_system_prompt() -> str:

        return """
You are an AI recruitment assistant using
retrieval-augmented generation.

Your job is to answer questions about resumes,
job descriptions, candidates, interviews, skills,
and recruitment documents.

Use retrieved information as evidence.

Never fabricate:
- candidate experience
- skills
- education
- employment history
- certifications
- interview results
- job requirements

If the retrieved documents do not contain enough
information, clearly state that the information
is unavailable.
""".strip()


# ----------------------------------------------------------------------
# Resume RAG
# ----------------------------------------------------------------------


class ResumeRAGPipeline:
    """
    Specialized RAG pipeline for candidate resumes.

    Provides convenient methods for recruiter workflows.
    """

    def __init__(
        self,
        pipeline: RAGPipeline,
    ) -> None:

        self.pipeline = pipeline

    def ask_about_resume(
        self,
        question: str,
        resume_source: str | None = None,
        top_k: int = 5,
    ) -> RAGResponse:
        """
        Ask a question about a resume.
        """

        metadata_filter = None

        if resume_source:
            metadata_filter = {
                "source": resume_source,
            }

        return self.pipeline.ask(
            question=question,
            top_k=top_k,
            metadata_filter=metadata_filter,
        )

    def find_skills(
        self,
        skills: Sequence[str],
        resume_source: str | None = None,
    ) -> RAGResponse:
        """
        Find evidence of specific skills.
        """

        skill_query = (
            "Candidate skills and experience: "
            + ", ".join(skills)
        )

        return self.ask_about_resume(
            question=skill_query,
            resume_source=resume_source,
        )

    def find_experience(
        self,
        technology: str,
        resume_source: str | None = None,
    ) -> RAGResponse:
        """
        Find experience related to a technology.
        """

        question = (
            f"What experience does the candidate "
            f"have with {technology}?"
        )

        return self.ask_about_resume(
            question=question,
            resume_source=resume_source,
        )

    def find_projects(
        self,
        resume_source: str | None = None,
    ) -> RAGResponse:
        """
        Find project information.
        """

        return self.ask_about_resume(
            question=(
                "What projects has the candidate "
                "worked on? Include technologies "
                "and responsibilities."
            ),
            resume_source=resume_source,
        )

    def find_education(
        self,
        resume_source: str | None = None,
    ) -> RAGResponse:
        """
        Find education information.
        """

        return self.ask_about_resume(
            question=(
                "What is the candidate's educational "
                "background?"
            ),
            resume_source=resume_source,
        )


# ----------------------------------------------------------------------
# Job Description RAG
# ----------------------------------------------------------------------


class JobDescriptionRAGPipeline:
    """
    Specialized RAG pipeline for job descriptions.
    """

    def __init__(
        self,
        pipeline: RAGPipeline,
    ) -> None:

        self.pipeline = pipeline

    def ask_about_job(
        self,
        question: str,
        job_source: str | None = None,
        top_k: int = 5,
    ) -> RAGResponse:
        """
        Ask a question about a job description.
        """

        metadata_filter = None

        if job_source:
            metadata_filter = {
                "source": job_source,
            }

        return self.pipeline.ask(
            question=question,
            top_k=top_k,
            metadata_filter=metadata_filter,
        )

    def find_requirements(
        self,
        job_source: str | None = None,
    ) -> RAGResponse:
        """
        Retrieve required skills and qualifications.
        """

        return self.ask_about_job(
            question=(
                "What are the required skills, "
                "qualifications, and experience "
                "for this position?"
            ),
            job_source=job_source,
        )

    def find_responsibilities(
        self,
        job_source: str | None = None,
    ) -> RAGResponse:
        """
        Retrieve job responsibilities.
        """

        return self.ask_about_job(
            question=(
                "What are the main responsibilities "
                "for this position?"
            ),
            job_source=job_source,
        )


# ----------------------------------------------------------------------
# Factory
# ----------------------------------------------------------------------


def create_rag_pipeline(
    document_loader: DocumentLoader,
    chunker: TextChunker,
    embedding_service: EmbeddingService,
    vector_store: VectorStore,
    retriever: Retriever,
    llm: LLMProvider,
    top_k: int = DEFAULT_TOP_K,
    min_score: float | None = DEFAULT_MIN_SCORE,
) -> RAGPipeline:
    """
    Create a configured RAG pipeline.
    """

    return RAGPipeline(
        document_loader=document_loader,
        chunker=chunker,
        embedding_service=embedding_service,
        vector_store=vector_store,
        retriever=retriever,
        llm=llm,
        top_k=top_k,
        min_score=min_score,
    )


__all__ = [
    "LLMProvider",
    "RAGPipeline",
    "RAGResponse",
    "RAGSource",
    "ResumeRAGPipeline",
    "JobDescriptionRAGPipeline",
    "RAGPipelineError",
    "RAGConfigurationError",
    "RAGGenerationError",
    "create_rag_pipeline",
]