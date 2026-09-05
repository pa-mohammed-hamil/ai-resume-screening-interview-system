# Project scaffold file
"""
Text-to-Speech Service

Converts AI-generated interview text into speech.

Responsibilities:
- Validate input text
- Generate speech audio
- Save audio to storage
- Support configurable voice/model
- Return metadata about generated audio
"""

from __future__ import annotations

import logging
import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------


class TextToSpeechError(Exception):
    """Base exception for text-to-speech failures."""


class EmptyTextError(TextToSpeechError):
    """Raised when no text is supplied."""


class AudioGenerationError(TextToSpeechError):
    """Raised when speech generation fails."""


# ----------------------------------------------------------------------
# Data Models
# ----------------------------------------------------------------------


@dataclass
class SpeechResult:
    """Result returned after generating speech."""

    text: str
    audio_path: str
    format: str = "mp3"
    voice: Optional[str] = None
    model: Optional[str] = None
    duration: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to a dictionary."""

        return {
            "text": self.text,
            "audio_path": self.audio_path,
            "format": self.format,
            "voice": self.voice,
            "model": self.model,
            "duration": self.duration,
            "metadata": self.metadata or {},
        }


# ----------------------------------------------------------------------
# Text-to-Speech Service
# ----------------------------------------------------------------------


class TextToSpeech:
    """
    Provider-agnostic text-to-speech service.

    Example:

        tts = TextToSpeech()

        result = tts.synthesize(
            "Welcome to your AI interview."
        )

        print(result.audio_path)
    """

    SUPPORTED_FORMATS = {
        "mp3",
        "wav",
        "opus",
        "aac",
        "flac",
    }

    def __init__(
        self,
        model: Optional[str] = None,
        voice: Optional[str] = None,
        output_dir: str | Path = "storage/interview_audio",
        api_key: Optional[str] = None,
        response_format: str = "mp3",
    ) -> None:

        self.model = (
            model
            or os.getenv("TTS_MODEL")
            or "gpt-4o-mini-tts"
        )

        self.voice = (
            voice
            or os.getenv("TTS_VOICE")
            or "alloy"
        )

        self.api_key = (
            api_key
            or os.getenv("OPENAI_API_KEY")
        )

        self.response_format = response_format.lower()

        self.output_dir = Path(output_dir)

        self._client = None

        self._validate_format()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def synthesize(
        self,
        text: str,
        output_path: Optional[str | Path] = None,
        voice: Optional[str] = None,
        model: Optional[str] = None,
    ) -> SpeechResult:
        """
        Convert text into speech.

        Args:
            text:
                Text that should be spoken.

            output_path:
                Optional path where the audio should be saved.

            voice:
                Optional voice override.

            model:
                Optional model override.

        Returns:
            SpeechResult
        """

        text = self._validate_text(text)

        selected_voice = voice or self.voice
        selected_model = model or self.model

        path = self._prepare_output_path(
            output_path
        )

        logger.info(
            "Generating speech using model=%s voice=%s",
            selected_model,
            selected_voice,
        )

        try:
            self._generate_audio(
                text=text,
                output_path=path,
                voice=selected_voice,
                model=selected_model,
            )

        except TextToSpeechError:
            raise

        except Exception as exc:
            logger.exception(
                "Text-to-speech generation failed."
            )

            raise AudioGenerationError(
                f"Failed to generate speech: {exc}"
            ) from exc

        return SpeechResult(
            text=text,
            audio_path=str(path),
            format=self.response_format,
            voice=selected_voice,
            model=selected_model,
            duration=self.estimate_duration(text),
            metadata={
                "provider": "openai",
                "word_count": self.word_count(text),
            },
        )

    # ------------------------------------------------------------------
    # Audio Generation
    # ------------------------------------------------------------------

    def _generate_audio(
        self,
        text: str,
        output_path: Path,
        voice: str,
        model: str,
    ) -> None:
        """
        Generate audio using the configured TTS provider.
        """

        if not self.api_key:
            raise AudioGenerationError(
                "No text-to-speech provider is configured. "
                "Set OPENAI_API_KEY."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise AudioGenerationError(
                "OpenAI package is not installed."
            ) from exc

        if self._client is None:
            self._client = OpenAI(
                api_key=self.api_key
            )

        try:
            with self._client.audio.speech.with_streaming_response.create(
                model=model,
                voice=voice,
                input=text,
                response_format=self.response_format,
            ) as response:

                response.stream_to_file(output_path)

        except Exception as exc:
            raise AudioGenerationError(
                f"TTS provider failed: {exc}"
            ) from exc

        if not output_path.exists():
            raise AudioGenerationError(
                "TTS provider did not create the audio file."
            )

        if output_path.stat().st_size == 0:
            raise AudioGenerationError(
                "Generated audio file is empty."
            )

        logger.info(
            "Speech generated successfully: %s",
            output_path,
        )

    # ------------------------------------------------------------------
    # Output Path
    # ------------------------------------------------------------------

    def _prepare_output_path(
        self,
        output_path: Optional[str | Path],
    ) -> Path:
        """Create and validate the output path."""

        if output_path:
            path = Path(output_path)

            if not path.suffix:
                path = path.with_suffix(
                    f".{self.response_format}"
                )
        else:
            self.output_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            filename = (
                f"tts_{uuid.uuid4().hex}"
                f".{self.response_format}"
            )

            path = self.output_dir / filename

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        return path

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_text(self, text: str) -> str:
        """Validate and normalize text."""

        if text is None:
            raise EmptyTextError(
                "Text cannot be None."
            )

        text = str(text).strip()

        if not text:
            raise EmptyTextError(
                "Text cannot be empty."
            )

        return text

    def _validate_format(self) -> None:
        """Validate the requested audio format."""

        if self.response_format not in self.SUPPORTED_FORMATS:
            raise TextToSpeechError(
                f"Unsupported audio format: "
                f"{self.response_format}. "
                f"Supported formats: "
                f"{', '.join(sorted(self.SUPPORTED_FORMATS))}"
            )

    # ------------------------------------------------------------------
    # Text Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def word_count(text: str) -> int:
        """Return the number of words."""

        if not text:
            return 0

        return len(text.split())

    @staticmethod
    def character_count(text: str) -> int:
        """Return the number of characters."""

        return len(text or "")

    @staticmethod
    def estimate_duration(
        text: str,
        words_per_minute: int = 130,
    ) -> float:
        """
        Estimate generated speech duration in seconds.

        130 WPM is used as a reasonable conversational
        interview speaking rate.
        """

        if words_per_minute <= 0:
            words_per_minute = 130

        words = TextToSpeech.word_count(text)

        return round(
            (words / words_per_minute) * 60,
            2,
        )

    # ------------------------------------------------------------------
    # Interview-specific Helpers
    # ------------------------------------------------------------------

    def speak_question(
        self,
        question: str,
        output_path: Optional[str | Path] = None,
    ) -> SpeechResult:
        """Generate speech for an interview question."""

        return self.synthesize(
            text=question,
            output_path=output_path,
        )

    def speak_feedback(
        self,
        feedback: str,
        output_path: Optional[str | Path] = None,
    ) -> SpeechResult:
        """Generate speech for interviewer feedback."""

        return self.synthesize(
            text=feedback,
            output_path=output_path,
        )

    def speak_intro(
        self,
        intro: str,
        output_path: Optional[str | Path] = None,
    ) -> SpeechResult:
        """Generate speech for interview introduction."""

        return self.synthesize(
            text=intro,
            output_path=output_path,
        )


# ----------------------------------------------------------------------
# Convenience Function
# ----------------------------------------------------------------------


def synthesize_speech(
    text: str,
    output_path: Optional[str | Path] = None,
    voice: Optional[str] = None,
    model: Optional[str] = None,
) -> SpeechResult:
    """
    Convenience function for one-off speech generation.

    Example:

        result = synthesize_speech(
            "Tell me about yourself."
        )

        print(result.audio_path)
    """

    service = TextToSpeech(
        voice=voice,
        model=model,
    )

    return service.synthesize(
        text=text,
        output_path=output_path,
    )


__all__ = [
    "TextToSpeech",
    "SpeechResult",
    "TextToSpeechError",
    "EmptyTextError",
    "AudioGenerationError",
    "synthesize_speech",
]