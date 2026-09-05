"""
Resume Parser
-------------
Central orchestration layer for parsing resumes.

Supported formats:
    - PDF
    - DOCX
    - TXT

Flow:
    File
      ↓
    ResumeParser
      ↓
    Format-specific parser
      ↓
    Text cleaner
      ↓
    ParsedResume
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ResumeParserError(Exception):
    """Base exception for resume parsing."""


class UnsupportedFileTypeError(ResumeParserError):
    """Raised when the resume format is not supported."""


@dataclass
class ParsedResume:
    """Standardized resume parsing result."""

    file_name: str
    file_type: str
    text: str
    character_count: int
    word_count: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return the result as a dictionary."""
        return {
            "file_name": self.file_name,
            "file_type": self.file_type,
            "text": self.text,
            "character_count": self.character_count,
            "word_count": self.word_count,
            "metadata": self.metadata,
        }


class ResumeParser:
    """Main entry point for resume parsing."""

    SUPPORTED_EXTENSIONS = {
        ".pdf": "pdf",
        ".docx": "docx",
        ".txt": "txt",
    }

    DEFAULT_MAX_FILE_SIZE_MB = 20

    def __init__(
        self,
        max_file_size_mb: int = DEFAULT_MAX_FILE_SIZE_MB,
    ) -> None:
        self.max_file_size_mb = max_file_size_mb

    def parse(self, file_path: str | Path) -> ParsedResume:
        """
        Parse a resume from a file path.

        Args:
            file_path: Path to PDF, DOCX, or TXT resume.

        Returns:
            ParsedResume object.
        """

        path = Path(file_path)

        self._validate_file(path)

        file_type = self._detect_file_type(path)

        raw_text, metadata = self._extract_text(
            path,
            file_type,
        )

        text = self._clean_text(raw_text)

        if not text:
            raise ResumeParserError(
                f"No readable text found in '{path.name}'."
            )

        return self._build_result(
            file_name=path.name,
            file_type=file_type,
            text=text,
            metadata=metadata,
        )

    def parse_bytes(
        self,
        file_bytes: bytes,
        file_name: str,
    ) -> ParsedResume:
        """
        Parse a resume received as bytes.

        Useful for FastAPI UploadFile.
        """

        if not file_bytes:
            raise ResumeParserError(
                "Uploaded resume is empty."
            )

        if len(file_bytes) > self._max_file_size_bytes():
            raise ResumeParserError(
                f"Resume exceeds the maximum size of "
                f"{self.max_file_size_mb} MB."
            )

        path = Path(file_name)

        file_type = self._detect_file_type(path)

        raw_text, metadata = self._extract_from_bytes(
            file_bytes,
            file_name,
            file_type,
        )

        text = self._clean_text(raw_text)

        if not text:
            raise ResumeParserError(
                f"No readable text found in '{file_name}'."
            )

        return self._build_result(
            file_name=file_name,
            file_type=file_type,
            text=text,
            metadata=metadata,
        )

    def _validate_file(self, path: Path) -> None:
        """Validate a local resume file."""

        if not path.exists():
            raise FileNotFoundError(
                f"Resume not found: {path}"
            )

        if not path.is_file():
            raise ResumeParserError(
                f"Expected a file: {path}"
            )

        if path.stat().st_size == 0:
            raise ResumeParserError(
                f"Resume is empty: {path.name}"
            )

        if path.stat().st_size > self._max_file_size_bytes():
            raise ResumeParserError(
                f"Resume exceeds the maximum size of "
                f"{self.max_file_size_mb} MB."
            )

    def _detect_file_type(self, path: Path) -> str:
        """Determine file type from extension."""

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
        """Delegate extraction to the correct parser."""

        if file_type == "pdf":
            from .pdf_parser import PDFParser

            parser = PDFParser()
            return parser.parse(path)

        if file_type == "docx":
            from .docx_parser import DOCXParser

            parser = DOCXParser()
            return parser.parse(path)

        if file_type == "txt":
            return self._parse_txt(path)

        raise UnsupportedFileTypeError(
            f"No parser available for: {file_type}"
        )

    def _extract_from_bytes(
        self,
        file_bytes: bytes,
        file_name: str,
        file_type: str,
    ) -> tuple[str, dict[str, Any]]:
        """Delegate byte-based extraction."""

        if file_type == "pdf":
            from .pdf_parser import PDFParser

            parser = PDFParser()
            return parser.parse_bytes(
                file_bytes,
                file_name,
            )

        if file_type == "docx":
            from .docx_parser import DOCXParser

            parser = DOCXParser()
            return parser.parse_bytes(
                file_bytes,
                file_name,
            )

        if file_type == "txt":
            return (
                self._decode_text(file_bytes),
                {
                    "source": "txt",
                    "encoding": "utf-8",
                },
            )

        raise UnsupportedFileTypeError(
            f"No parser available for: {file_type}"
        )

    @staticmethod
    def _parse_txt(
        path: Path,
    ) -> tuple[str, dict[str, Any]]:
        """Parse a plain-text resume."""

        data = path.read_bytes()

        return (
            ResumeParser._decode_text(data),
            {
                "source": "txt",
                "encoding": "utf-8",
            },
        )

    @staticmethod
    def _decode_text(data: bytes) -> str:
        """Decode text using common encodings."""

        for encoding in (
            "utf-8",
            "utf-8-sig",
            "latin-1",
        ):
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue

        raise ResumeParserError(
            "Unable to decode text file."
        )

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean extracted resume text."""

        # Import here to avoid unnecessary dependency loading
        # when parser.py is imported.
        from .text_cleaner import clean_text

        return clean_text(text)

    @staticmethod
    def _build_result(
        file_name: str,
        file_type: str,
        text: str,
        metadata: dict[str, Any],
    ) -> ParsedResume:
        """Create the standardized parsing result."""

        return ParsedResume(
            file_name=file_name,
            file_type=file_type,
            text=text,
            character_count=len(text),
            word_count=len(text.split()),
            metadata=metadata,
        )

    def _max_file_size_bytes(self) -> int:
        """Return maximum allowed file size in bytes."""

        return self.max_file_size_mb * 1024 * 1024


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