"""
ai/resume_parser/parser.py

Main resume parsing orchestrator.

Responsibilities:
- Detect resume file type
- Delegate parsing to PDF/DOCX parsers
- Clean extracted text
- Return a consistent parsing result
- Provide useful metadata and errors
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .text_cleaner import clean_text


@dataclass
class ParsedResume:
    """Normalized output returned by the resume parser."""

    file_name: str
    file_type: str
    text: str
    character_count: int
    word_count: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert the parsed resume into a JSON-serializable dictionary."""
        return {
            "file_name": self.file_name,
            "file_type": self.file_type,
            "text": self.text,
            "character_count": self.character_count,
            "word_count": self.word_count,
            "metadata": self.metadata,
        }


class ResumeParserError(Exception):
    """Base exception for resume parsing errors."""


class UnsupportedFileTypeError(ResumeParserError):
    """Raised when the supplied resume format is unsupported."""


class ResumeParser:
    """
    Main resume parser.

    Supported formats:
        - PDF
        - DOCX
        - TXT
    """

    SUPPORTED_EXTENSIONS = {
        ".pdf": "pdf",
        ".docx": "docx",
        ".txt": "txt",
    }

    MAX_FILE_SIZE_MB = 20

    def __init__(self, max_file_size_mb: int = MAX_FILE_SIZE_MB) -> None:
        self.max_file_size_mb = max_file_size_mb

    def parse(self, file_path: str | Path) -> ParsedResume:
        """
        Parse a resume from a local file.

        Args:
            file_path: Path to the resume.

        Returns:
            ParsedResume containing cleaned resume text and metadata.

        Raises:
            FileNotFoundError:
                If the file does not exist.

            UnsupportedFileTypeError:
                If the file extension is unsupported.

            ResumeParserError:
                If parsing fails.
        """

        path = Path(file_path)

        self._validate_file(path)

        file_type = self._detect_file_type(path)

        try:
            raw_text, metadata = self._extract_text(path, file_type)
        except Exception as exc:
            raise ResumeParserError(
                f"Failed to parse resume '{path.name}': {exc}"
            ) from exc

        text = clean_text(raw_text)

        if not text.strip():
            raise ResumeParserError(
                f"No readable text was extracted from '{path.name}'."
            )

        return ParsedResume(
            file_name=path.name,
            file_type=file_type,
            text=text,
            character_count=len(text),
            word_count=self._count_words(text),
            metadata=metadata,
        )

    def parse_bytes(
        self,
        file_bytes: bytes,
        file_name: str,
    ) -> ParsedResume:
        """
        Parse a resume from raw bytes.

        This method is useful for FastAPI file uploads.

        Args:
            file_bytes: Uploaded file content.
            file_name: Original filename.

        Returns:
            ParsedResume.
        """

        if not file_bytes:
            raise ResumeParserError("Uploaded file is empty.")

        path = Path(file_name)
        file_type = self._detect_file_type(path)

        max_bytes = self.max_file_size_mb * 1024 * 1024

        if len(file_bytes) > max_bytes:
            raise ResumeParserError(
                f"File exceeds the maximum size of "
                f"{self.max_file_size_mb} MB."
            )

        try:
            raw_text, metadata = self._extract_from_bytes(
                file_bytes,
                file_name,
                file_type,
            )
        except Exception as exc:
            raise ResumeParserError(
                f"Failed to parse uploaded resume "
                f"'{file_name}': {exc}"
            ) from exc

        text = clean_text(raw_text)

        if not text.strip():
            raise ResumeParserError(
                f"No readable text was extracted from '{file_name}'."
            )

        return ParsedResume(
            file_name=file_name,
            file_type=file_type,
            text=text,
            character_count=len(text),
            word_count=self._count_words(text),
            metadata=metadata,
        )

    def _validate_file(self, path: Path) -> None:
        """Validate a local resume file."""

        if not path.exists():
            raise FileNotFoundError(
                f"Resume file not found: {path}"
            )

        if not path.is_file():
            raise ResumeParserError(
                f"Expected a file but received: {path}"
            )

        if path.stat().st_size == 0:
            raise ResumeParserError(
                f"Resume file is empty: {path.name}"
            )

        max_bytes = self.max_file_size_mb * 1024 * 1024

        if path.stat().st_size > max_bytes:
            raise ResumeParserError(
                f"Resume exceeds the maximum allowed size "
                f"of {self.max_file_size_mb} MB."
            )

    def _detect_file_type(self, path: Path) -> str:
        """Detect the supported file type from its extension."""

        extension = path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            supported = ", ".join(
                self.SUPPORTED_EXTENSIONS.keys()
            )

            raise UnsupportedFileTypeError(
                f"Unsupported file type '{extension}'. "
                f"Supported formats: {supported}"
            )

        return self.SUPPORTED_EXTENSIONS[extension]

    def _extract_text(
        self,
        path: Path,
        file_type: str,
    ) -> tuple[str, dict[str, Any]]:
        """Delegate parsing based on file type."""

        if file_type == "pdf":
            from .pdf_parser import PDFParser

            parser = PDFParser()
            return parser.parse(path)

        if file_type == "docx":
            from .docx_parser import DOCXParser

            parser = DOCXParser()
            return parser.parse(path)

        if file_type == "txt":
            return self._parse_text_file(path)

        raise UnsupportedFileTypeError(
            f"No parser registered for '{file_type}'."
        )

    def _extract_from_bytes(
        self,
        file_bytes: bytes,
        file_name: str,
        file_type: str,
    ) -> tuple[str, dict[str, Any]]:
        """Extract text from uploaded bytes."""

        if file_type == "pdf":
            from .pdf_parser import PDFParser

            parser = PDFParser()
            return parser.parse_bytes(file_bytes, file_name)

        if file_type == "docx":
            from .docx_parser import DOCXParser

            parser = DOCXParser()
            return parser.parse_bytes(file_bytes, file_name)

        if file_type == "txt":
            text = self._decode_text(file_bytes)

            return text, {
                "encoding": "utf-8",
                "source": "text_file",
            }

        raise UnsupportedFileTypeError(
            f"No parser registered for '{file_type}'."
        )

    @staticmethod
    def _parse_text_file(
        path: Path,
    ) -> tuple[str, dict[str, Any]]:
        """Parse a plain-text resume."""

        raw_bytes = path.read_bytes()
        text = ResumeParser._decode_text(raw_bytes)

        return text, {
            "encoding": "utf-8",
            "source": "text_file",
        }

    @staticmethod
    def _decode_text(file_bytes: bytes) -> str:
        """Decode text while handling common encodings."""

        encodings = (
            "utf-8",
            "utf-8-sig",
            "latin-1",
        )

        for encoding in encodings:
            try:
                return file_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue

        raise ResumeParserError(
            "Unable to decode text file."
        )

    @staticmethod
    def _count_words(text: str) -> int:
        """Return an approximate word count."""

        return len(text.split())


def parse_resume(
    file_path: str | Path,
) -> ParsedResume:
    """
    Convenience function for parsing a resume.

    Example:
        result = parse_resume("resume.pdf")
    """

    parser = ResumeParser()
    return parser.parse(file_path)