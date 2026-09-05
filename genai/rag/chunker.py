"""
genai/rag/chunker.py

Text chunking utilities for the RAG pipeline.

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
       LLM/RAG

The chunker:
    - Splits large documents into manageable pieces
    - Preserves document metadata
    - Supports configurable chunk size and overlap
    - Uses recursive separators
    - Adds chunk-level metadata
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

from .document_loader import Document

logger = logging.getLogger(__name__)


DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 150

DEFAULT_SEPARATORS = [
    "\n\n",
    "\n",
    ". ",
    "! ",
    "? ",
    "; ",
    ", ",
    " ",
    "",
]


@dataclass
class DocumentChunk:
    """
    Represents one chunk generated from a Document.
    """

    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def text(self) -> str:
        """Alias for content."""
        return self.content

    @property
    def chunk_id(self) -> str | None:
        """Return the chunk ID if available."""
        return self.metadata.get("chunk_id")


class ChunkingError(Exception):
    """Raised when document chunking fails."""


class TextChunker:
    """
    Recursive text chunker for RAG applications.

    The chunker attempts to split text at natural boundaries:

        paragraph
            ↓
        line
            ↓
        sentence
            ↓
        punctuation
            ↓
        word
            ↓
        character

    Example:
        chunker = TextChunker(
            chunk_size=1000,
            chunk_overlap=150,
        )

        chunks = chunker.chunk_document(document)
    """

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        separators: Sequence[str] | None = None,
        min_chunk_size: int = 50,
    ) -> None:

        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        if min_chunk_size < 0:
            raise ValueError(
                "min_chunk_size cannot be negative"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

        self.separators = list(
            separators
            if separators is not None
            else DEFAULT_SEPARATORS
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chunk_document(
        self,
        document: Document,
    ) -> list[DocumentChunk]:
        """
        Chunk a single Document.

        Args:
            document: Document loaded by DocumentLoader.

        Returns:
            List of DocumentChunk objects.
        """

        if not document.content or not document.content.strip():
            return []

        raw_chunks = self.split_text(document.content)

        chunks: list[DocumentChunk] = []

        for index, content in enumerate(raw_chunks):

            content = self._clean_chunk(content)

            if not content:
                continue

            if (
                len(content) < self.min_chunk_size
                and chunks
                and len(chunks[-1].content) + len(content)
                <= self.chunk_size
            ):
                chunks[-1].content = (
                    chunks[-1].content.rstrip()
                    + "\n"
                    + content
                )
                continue

            metadata = dict(document.metadata)

            metadata.update(
                {
                    "chunk_id": self._create_chunk_id(
                        document,
                        index,
                    ),
                    "chunk_index": index,
                    "chunk_size": len(content),
                    "total_chunks": len(raw_chunks),
                }
            )

            chunks.append(
                DocumentChunk(
                    content=content,
                    metadata=metadata,
                )
            )

        return chunks

    def chunk_documents(
        self,
        documents: Iterable[Document],
    ) -> list[DocumentChunk]:
        """
        Chunk multiple documents.

        Args:
            documents: Iterable of Documents.

        Returns:
            Flattened list of DocumentChunk objects.
        """

        chunks: list[DocumentChunk] = []

        for document in documents:
            chunks.extend(
                self.chunk_document(document)
            )

        return chunks

    def split_text(self, text: str) -> list[str]:
        """
        Split raw text into chunks.

        Uses recursive splitting to preserve natural text structure.
        """

        text = self._clean_text(text)

        if not text:
            return []

        if len(text) <= self.chunk_size:
            return [text]

        pieces = self._recursive_split(
            text=text,
            separators=self.separators,
        )

        pieces = [
            self._clean_chunk(piece)
            for piece in pieces
            if piece.strip()
        ]

        return self._merge_with_overlap(pieces)

    # ------------------------------------------------------------------
    # Recursive splitting
    # ------------------------------------------------------------------

    def _recursive_split(
        self,
        text: str,
        separators: Sequence[str],
    ) -> list[str]:

        if len(text) <= self.chunk_size:
            return [text]

        if not separators:
            return self._hard_split(text)

        separator = separators[0]

        # Last separator means character-level splitting.
        if separator == "":
            return self._hard_split(text)

        if separator not in text:
            return self._recursive_split(
                text,
                separators[1:],
            )

        parts = text.split(separator)

        chunks: list[str] = []
        current = ""

        for part in parts:

            if not part:
                continue

            candidate = (
                part
                if not current
                else current + separator + part
            )

            if len(candidate) <= self.chunk_size:
                current = candidate
                continue

            if current:
                chunks.extend(
                    self._recursive_split(
                        current,
                        separators[1:],
                    )
                )

            if len(part) <= self.chunk_size:
                current = part
            else:
                chunks.extend(
                    self._recursive_split(
                        part,
                        separators[1:],
                    )
                )
                current = ""

        if current:
            chunks.extend(
                self._recursive_split(
                    current,
                    separators[1:],
                )
            )

        return chunks

    # ------------------------------------------------------------------
    # Hard splitting
    # ------------------------------------------------------------------

    def _hard_split(self, text: str) -> list[str]:
        """
        Split text when no natural separator can keep chunks
        within the configured size.
        """

        chunks: list[str] = []

        start = 0
        length = len(text)

        step = max(
            1,
            self.chunk_size - self.chunk_overlap,
        )

        while start < length:

            end = min(
                start + self.chunk_size,
                length,
            )

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= length:
                break

            start += step

        return chunks

    # ------------------------------------------------------------------
    # Overlap
    # ------------------------------------------------------------------

    def _merge_with_overlap(
        self,
        pieces: list[str],
    ) -> list[str]:

        if not pieces:
            return []

        if self.chunk_overlap == 0:
            return pieces

        chunks: list[str] = []

        current = ""

        for piece in pieces:

            piece = piece.strip()

            if not piece:
                continue

            if not current:
                current = piece
                continue

            candidate = current + "\n" + piece

            if len(candidate) <= self.chunk_size:
                current = candidate
                continue

            chunks.append(current.strip())

            overlap = self._get_overlap(
                current
            )

            current = (
                overlap + "\n" + piece
                if overlap
                else piece
            )

            # If overlap causes the chunk to exceed the limit,
            # hard-split it.
            if len(current) > self.chunk_size:

                split_chunks = self._hard_split(
                    current
                )

                if split_chunks:
                    chunks.extend(
                        split_chunks[:-1]
                    )
                    current = split_chunks[-1]

        if current.strip():
            chunks.append(current.strip())

        return chunks

    def _get_overlap(self, text: str) -> str:
        """
        Extract the last chunk_overlap characters.

        Attempts to avoid cutting through a word.
        """

        if not text:
            return ""

        overlap = text[-self.chunk_overlap:]

        # Prefer starting at a word boundary.
        match = re.search(
            r"\s",
            overlap,
        )

        if match:
            overlap = overlap[match.end():]

        return overlap.strip()

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    @staticmethod
    def _create_chunk_id(
        document: Document,
        index: int,
    ) -> str:

        source = document.metadata.get(
            "source",
            "document",
        )

        source_name = (
            document.metadata.get(
                "file_stem"
            )
            or source.split("/")[-1]
        )

        safe_name = re.sub(
            r"[^a-zA-Z0-9_-]+",
            "_",
            str(source_name),
        )

        return f"{safe_name}_chunk_{index}"

    # ------------------------------------------------------------------
    # Cleaning
    # ------------------------------------------------------------------

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Normalize source text before splitting.
        """

        text = text.replace(
            "\r\n",
            "\n",
        )

        text = text.replace(
            "\r",
            "\n",
        )

        text = text.replace(
            "\x00",
            "",
        )

        # Normalize tabs.
        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        # Collapse excessive blank lines.
        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()

    @staticmethod
    def _clean_chunk(text: str) -> str:
        """
        Clean an individual chunk while preserving paragraphs.
        """

        text = text.strip()

        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()


# ----------------------------------------------------------------------
# Specialized resume chunker
# ----------------------------------------------------------------------

class ResumeChunker(TextChunker):
    """
    Resume-specific chunker.

    Resumes often contain sections such as:

        Summary
        Skills
        Experience
        Education
        Projects
        Certifications

    This class gives section boundaries higher priority.
    """

    RESUME_SEPARATORS = [
        "\n\n",
        "\n",
        ". ",
        "; ",
        ", ",
        " ",
        "",
    ]

    def __init__(
        self,
        chunk_size: int = 900,
        chunk_overlap: int = 120,
        min_chunk_size: int = 40,
    ) -> None:

        super().__init__(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=self.RESUME_SEPARATORS,
            min_chunk_size=min_chunk_size,
        )


# ----------------------------------------------------------------------
# Convenience functions
# ----------------------------------------------------------------------

_default_chunker = TextChunker()


def chunk_document(
    document: Document,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[DocumentChunk]:
    """
    Convenience function for chunking one document.
    """

    chunker = TextChunker(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    return chunker.chunk_document(document)


def chunk_documents(
    documents: Iterable[Document],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[DocumentChunk]:
    """
    Convenience function for chunking multiple documents.
    """

    chunker = TextChunker(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    return chunker.chunk_documents(documents)


def chunk_resume(
    document: Document,
) -> list[DocumentChunk]:
    """
    Convenience function specifically for resumes.
    """

    return ResumeChunker().chunk_document(document)


__all__ = [
    "DocumentChunk",
    "ChunkingError",
    "TextChunker",
    "ResumeChunker",
    "chunk_document",
    "chunk_documents",
    "chunk_resume",
]