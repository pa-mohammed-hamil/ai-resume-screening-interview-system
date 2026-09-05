# Project scaffold file
"""
Speech-to-Text Service

Converts interview audio into text.

The implementation is provider-agnostic so that a real STT provider
such as Whisper/OpenAI can be plugged in without changing the rest
of the interview engine.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------


class SpeechToTextError(Exception):
    """Base exception for speech-to-text failures."""


class AudioFileNotFoundError(SpeechToTextError):
    """Raised when the audio file does not exist."""


class UnsupportedAudioFormatError(SpeechToTextError):
    """Raised when the audio format is not supported."""


class TranscriptionError(SpeechToTextError):
    """Raised when transcription fails."""


# ----------------------------------------------------------------------
# Data Models
# ----------------------------------------------------------------------


@dataclass
class TranscriptSegment:
    """Represents one segment of a transcript."""

    text: str
    start: float = 0.0
    end: float = 0.0
    confidence: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence,
        }


@dataclass
class TranscriptionResult:
    """Complete speech-to-text result."""

    text: str
    language: Optional[str] = None
    duration: Optional[float] = None
    confidence: Optional[float] = None
    segments: List[TranscriptSegment] = field(
        default_factory=list
    )
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "language": self.language,
            "duration": self.duration,
            "confidence": self.confidence,
            "segments": [
                segment.to_dict()
                for segment in self.segments
            ],
            "metadata": self.metadata,
        }


# ----------------------------------------------------------------------
# Speech-to-Text Service
# ----------------------------------------------------------------------


class SpeechToText:
    """
    Provider-agnostic speech-to-text service.

    Example:

        stt = SpeechToText()

        result = stt.transcribe(
            "storage/interview_audio/interview.wav"
        )

        print(result.text)
    """

    SUPPORTED_FORMATS = {
        ".wav",
        ".mp3",
        ".m4a",
        ".mp4",
        ".webm",
        ".ogg",
        ".flac",
    }

    def __init__(
        self,
        model: Optional[str] = None,
        language: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        self.model = (
            model
            or os.getenv("STT_MODEL")
            or "whisper-1"
        )

        self.language = (
            language
            or os.getenv("STT_LANGUAGE")
            or None
        )

        self.api_key = (
            api_key
            or os.getenv("OPENAI_API_KEY")
        )

        self._client = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def transcribe(
        self,
        audio_path: str | Path,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> TranscriptionResult:
        """
        Transcribe an audio file.

        Args:
            audio_path:
                Path to the interview audio.

            language:
                Optional language code such as "en".

            prompt:
                Optional context supplied to the STT model.

        Returns:
            TranscriptionResult
        """

        path = Path(audio_path)

        self._validate_audio_file(path)

        language = language or self.language

        logger.info(
            "Starting transcription: %s",
            path,
        )

        try:
            result = self._transcribe_with_provider(
                path=path,
                language=language,
                prompt=prompt,
            )

        except SpeechToTextError:
            raise

        except Exception as exc:
            logger.exception(
                "Speech transcription failed."
            )

            raise TranscriptionError(
                f"Failed to transcribe audio: {exc}"
            ) from exc

        logger.info(
            "Transcription completed: %s",
            path,
        )

        return result

    # ------------------------------------------------------------------
    # Provider
    # ------------------------------------------------------------------

    def _transcribe_with_provider(
        self,
        path: Path,
        language: Optional[str],
        prompt: Optional[str],
    ) -> TranscriptionResult:
        """
        Perform transcription using the configured provider.

        OpenAI Whisper-compatible API is used when the OpenAI SDK
        is available and an API key is configured.
        """

        if not self.api_key:
            return self._fallback_transcription(path)

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise TranscriptionError(
                "OpenAI package is not installed."
            ) from exc

        if self._client is None:
            self._client = OpenAI(
                api_key=self.api_key
            )

        try:
            with path.open("rb") as audio_file:
                request: Dict[str, Any] = {
                    "model": self.model,
                    "file": audio_file,
                }

                if language:
                    request["language"] = language

                if prompt:
                    request["prompt"] = prompt

                response = (
                    self._client.audio.transcriptions.create(
                        **request
                    )
                )

        except Exception as exc:
            raise TranscriptionError(
                f"Provider transcription failed: {exc}"
            ) from exc

        text = getattr(
            response,
            "text",
            "",
        )

        if not text:
            raise TranscriptionError(
                "The speech-to-text provider returned "
                "an empty transcript."
            )

        response_language = getattr(
            response,
            "language",
            language,
        )

        duration = getattr(
            response,
            "duration",
            None,
        )

        return TranscriptionResult(
            text=self.clean_transcript(text),
            language=response_language,
            duration=duration,
            metadata={
                "model": self.model,
                "provider": "openai",
                "source_file": str(path),
            },
        )

    # ------------------------------------------------------------------
    # Fallback
    # ------------------------------------------------------------------

    def _fallback_transcription(
        self,
        path: Path,
    ) -> TranscriptionResult:
        """
        Fallback used when no STT API key is configured.

        This deliberately does not pretend that audio was
        successfully transcribed.
        """

        raise TranscriptionError(
            "No speech-to-text provider is configured. "
            "Set OPENAI_API_KEY or provide a custom STT provider."
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_audio_file(
        self,
        path: Path,
    ) -> None:
        """Validate the supplied audio file."""

        if not path.exists():
            raise AudioFileNotFoundError(
                f"Audio file does not exist: {path}"
            )

        if not path.is_file():
            raise AudioFileNotFoundError(
                f"Audio path is not a file: {path}"
            )

        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise UnsupportedAudioFormatError(
                f"Unsupported audio format: {path.suffix}. "
                f"Supported formats: "
                f"{', '.join(sorted(self.SUPPORTED_FORMATS))}"
            )

        if path.stat().st_size == 0:
            raise SpeechToTextError(
                f"Audio file is empty: {path}"
            )

    # ------------------------------------------------------------------
    # Transcript Cleaning
    # ------------------------------------------------------------------

    @staticmethod
    def clean_transcript(text: str) -> str:
        """
        Clean raw transcript text.

        Removes excessive whitespace while preserving
        meaningful sentence structure.
        """

        if not text:
            return ""

        lines = [
            " ".join(line.split())
            for line in text.splitlines()
        ]

        lines = [
            line
            for line in lines
            if line
        ]

        return " ".join(lines).strip()

    # ------------------------------------------------------------------
    # Text Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def word_count(text: str) -> int:
        """Return the number of words in a transcript."""

        if not text:
            return 0

        return len(text.split())

    @staticmethod
    def character_count(text: str) -> int:
        """Return the number of characters in a transcript."""

        return len(text or "")

    @staticmethod
    def estimate_speaking_time(
        text: str,
        words_per_minute: int = 130,
    ) -> float:
        """
        Estimate speaking duration in minutes.

        Average interview speech is approximately 120-150 WPM.
        """

        if words_per_minute <= 0:
            words_per_minute = 130

        words = SpeechToText.word_count(text)

        return round(
            words / words_per_minute,
            2,
        )

    # ------------------------------------------------------------------
    # Transcript Analysis
    # ------------------------------------------------------------------

    def get_transcript_stats(
        self,
        result: TranscriptionResult,
    ) -> Dict[str, Any]:
        """Return useful statistics for interview evaluation."""

        text = result.text

        return {
            "word_count": self.word_count(text),
            "character_count": self.character_count(text),
            "estimated_speaking_minutes": (
                self.estimate_speaking_time(text)
            ),
            "language": result.language,
            "duration_seconds": result.duration,
            "confidence": result.confidence,
        }


# ----------------------------------------------------------------------
# Convenience Function
# ----------------------------------------------------------------------


def transcribe_audio(
    audio_path: str | Path,
    language: Optional[str] = None,
    model: Optional[str] = None,
) -> TranscriptionResult:
    """
    Convenience function for one-off transcription.

    Example:

        result = transcribe_audio(
            "interview.wav",
            language="en",
        )

        print(result.text)
    """

    service = SpeechToText(
        model=model,
        language=language,
    )

    return service.transcribe(
        audio_path=audio_path,
    )


__all__ = [
    "SpeechToText",
    "SpeechToTextError",
    "AudioFileNotFoundError",
    "UnsupportedAudioFormatError",
    "TranscriptionError",
    "TranscriptSegment",
    "TranscriptionResult",
    "transcribe_audio",
]