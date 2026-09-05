# Project scaffold file
"""
Audio Processor

Processes interview audio before speech-to-text and voice analysis.

Responsibilities:
- Validate audio files
- Detect supported formats
- Extract audio metadata
- Normalize audio
- Convert audio formats
- Trim leading/trailing silence
- Split long audio into chunks
- Prepare audio for STT
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------


class AudioProcessingError(Exception):
    """Base exception for audio processing errors."""


class AudioFileNotFoundError(AudioProcessingError):
    """Raised when an audio file cannot be found."""


class UnsupportedAudioFormatError(AudioProcessingError):
    """Raised when an audio format is not supported."""


class FFmpegNotFoundError(AudioProcessingError):
    """Raised when FFmpeg is required but unavailable."""


# ----------------------------------------------------------------------
# Data Models
# ----------------------------------------------------------------------


@dataclass
class AudioMetadata:
    """Metadata describing an audio file."""

    path: str
    format: Optional[str] = None
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    bit_rate: Optional[int] = None
    size_bytes: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "format": self.format,
            "duration": self.duration,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "bit_rate": self.bit_rate,
            "size_bytes": self.size_bytes,
        }


@dataclass
class ProcessedAudio:
    """Result returned after audio processing."""

    source_path: str
    output_path: str
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    format: Optional[str] = None
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_path": self.source_path,
            "output_path": self.output_path,
            "duration": self.duration,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "format": self.format,
            "metadata": self.metadata,
        }


# ----------------------------------------------------------------------
# Audio Processor
# ----------------------------------------------------------------------


class AudioProcessor:
    """
    Audio preprocessing service.

    FFmpeg is used for conversion and normalization.

    Example:

        processor = AudioProcessor()

        result = processor.prepare_for_stt(
            "storage/interview_audio/interview.webm"
        )

        print(result.output_path)
    """

    SUPPORTED_FORMATS = {
        ".wav",
        ".mp3",
        ".m4a",
        ".mp4",
        ".webm",
        ".ogg",
        ".flac",
        ".aac",
        ".opus",
    }

    STT_SAMPLE_RATE = 16000
    STT_CHANNELS = 1

    def __init__(
        self,
        output_dir: str | Path = "storage/temporary/audio",
        sample_rate: int = STT_SAMPLE_RATE,
        channels: int = STT_CHANNELS,
    ) -> None:

        self.output_dir = Path(output_dir)

        self.sample_rate = sample_rate
        self.channels = channels

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(
        self,
        audio_path: str | Path,
    ) -> Path:
        """Validate an audio file."""

        path = Path(audio_path)

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
            raise AudioProcessingError(
                f"Audio file is empty: {path}"
            )

        return path

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def get_metadata(
        self,
        audio_path: str | Path,
    ) -> AudioMetadata:
        """
        Extract audio metadata using FFprobe.
        """

        path = self.validate(audio_path)

        self._check_ffmpeg()

        command = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=format_name,duration,bit_rate:"
            "stream=sample_rate,channels",
            "-of",
            "default=noprint_wrappers=1",
            str(path),
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise AudioProcessingError(
                f"Unable to read audio metadata: "
                f"{exc.stderr}"
            ) from exc

        values = self._parse_ffprobe_output(
            result.stdout
        )

        return AudioMetadata(
            path=str(path),
            format=values.get("format_name"),
            duration=self._to_float(
                values.get("duration")
            ),
            sample_rate=self._to_int(
                values.get("sample_rate")
            ),
            channels=self._to_int(
                values.get("channels")
            ),
            bit_rate=self._to_int(
                values.get("bit_rate")
            ),
            size_bytes=path.stat().st_size,
        )

    # ------------------------------------------------------------------
    # STT Preparation
    # ------------------------------------------------------------------

    def prepare_for_stt(
        self,
        audio_path: str | Path,
        output_path: Optional[str | Path] = None,
    ) -> ProcessedAudio:
        """
        Convert audio into an STT-friendly WAV file.

        Default:
            16 kHz
            mono
            PCM WAV
        """

        source = self.validate(audio_path)

        if output_path:
            destination = Path(output_path)
        else:
            destination = (
                self.output_dir
                / f"stt_{uuid.uuid4().hex}.wav"
            )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._check_ffmpeg()

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-ac",
            str(self.channels),
            "-ar",
            str(self.sample_rate),
            "-c:a",
            "pcm_s16le",
            str(destination),
        ]

        self._run_ffmpeg(command)

        metadata = self.get_metadata(destination)

        return ProcessedAudio(
            source_path=str(source),
            output_path=str(destination),
            duration=metadata.duration,
            sample_rate=metadata.sample_rate,
            channels=metadata.channels,
            format=metadata.format,
            metadata={
                "purpose": "speech_to_text",
                "sample_rate": self.sample_rate,
                "channels": self.channels,
            },
        )

    # ------------------------------------------------------------------
    # Normalize
    # ------------------------------------------------------------------

    def normalize(
        self,
        audio_path: str | Path,
        output_path: Optional[str | Path] = None,
    ) -> ProcessedAudio:
        """
        Normalize audio volume.

        Loudness normalization helps make speech more consistent
        before transcription and voice analysis.
        """

        source = self.validate(audio_path)

        destination = self._create_output_path(
            output_path,
            source.suffix or ".wav",
            prefix="normalized",
        )

        self._check_ffmpeg()

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11",
            str(destination),
        ]

        self._run_ffmpeg(command)

        metadata = self.get_metadata(destination)

        return ProcessedAudio(
            source_path=str(source),
            output_path=str(destination),
            duration=metadata.duration,
            sample_rate=metadata.sample_rate,
            channels=metadata.channels,
            format=metadata.format,
            metadata={
                "operation": "loudness_normalization",
            },
        )

    # ------------------------------------------------------------------
    # Silence Trimming
    # ------------------------------------------------------------------

    def trim_silence(
        self,
        audio_path: str | Path,
        output_path: Optional[str | Path] = None,
        silence_start: float = 0.5,
        silence_end: float = 0.5,
    ) -> ProcessedAudio:
        """
        Remove leading and trailing silence.

        The silence thresholds are intentionally conservative so that
        normal pauses during an interview are not removed.
        """

        source = self.validate(audio_path)

        destination = self._create_output_path(
            output_path,
            source.suffix or ".wav",
            prefix="trimmed",
        )

        self._check_ffmpeg()

        filter_expression = (
            f"silenceremove="
            f"start_periods=1:"
            f"start_duration={silence_start}:"
            f"start_threshold=-40dB:"
            f"stop_periods=1:"
            f"stop_duration={silence_end}:"
            f"stop_threshold=-40dB"
        )

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-af",
            filter_expression,
            str(destination),
        ]

        self._run_ffmpeg(command)

        metadata = self.get_metadata(destination)

        return ProcessedAudio(
            source_path=str(source),
            output_path=str(destination),
            duration=metadata.duration,
            sample_rate=metadata.sample_rate,
            channels=metadata.channels,
            format=metadata.format,
            metadata={
                "operation": "silence_trim",
                "silence_start": silence_start,
                "silence_end": silence_end,
            },
        )

    # ------------------------------------------------------------------
    # Convert
    # ------------------------------------------------------------------

    def convert(
        self,
        audio_path: str | Path,
        output_format: str = "wav",
        output_path: Optional[str | Path] = None,
    ) -> ProcessedAudio:
        """Convert an audio file to another format."""

        source = self.validate(audio_path)

        output_format = (
            output_format.lower().lstrip(".")
        )

        allowed_formats = {
            fmt.lstrip(".")
            for fmt in self.SUPPORTED_FORMATS
        }

        if output_format not in allowed_formats:
            raise UnsupportedAudioFormatError(
                f"Unsupported output format: "
                f"{output_format}"
            )

        destination = self._create_output_path(
            output_path,
            f".{output_format}",
            prefix="converted",
        )

        self._check_ffmpeg()

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            str(destination),
        ]

        self._run_ffmpeg(command)

        metadata = self.get_metadata(destination)

        return ProcessedAudio(
            source_path=str(source),
            output_path=str(destination),
            duration=metadata.duration,
            sample_rate=metadata.sample_rate,
            channels=metadata.channels,
            format=metadata.format,
            metadata={
                "operation": "format_conversion",
                "output_format": output_format,
            },
        )

    # ------------------------------------------------------------------
    # Resampling
    # ------------------------------------------------------------------

    def resample(
        self,
        audio_path: str | Path,
        sample_rate: Optional[int] = None,
        output_path: Optional[str | Path] = None,
    ) -> ProcessedAudio:
        """Change the audio sample rate."""

        source = self.validate(audio_path)

        sample_rate = sample_rate or self.sample_rate

        destination = self._create_output_path(
            output_path,
            ".wav",
            prefix="resampled",
        )

        self._check_ffmpeg()

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-ar",
            str(sample_rate),
            str(destination),
        ]

        self._run_ffmpeg(command)

        metadata = self.get_metadata(destination)

        return ProcessedAudio(
            source_path=str(source),
            output_path=str(destination),
            duration=metadata.duration,
            sample_rate=metadata.sample_rate,
            channels=metadata.channels,
            format=metadata.format,
            metadata={
                "operation": "resampling",
                "sample_rate": sample_rate,
            },
        )

    # ------------------------------------------------------------------
    # Mono Conversion
    # ------------------------------------------------------------------

    def to_mono(
        self,
        audio_path: str | Path,
        output_path: Optional[str | Path] = None,
    ) -> ProcessedAudio:
        """Convert stereo/multi-channel audio to mono."""

        source = self.validate(audio_path)

        destination = self._create_output_path(
            output_path,
            ".wav",
            prefix="mono",
        )

        self._check_ffmpeg()

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-ac",
            "1",
            str(destination),
        ]

        self._run_ffmpeg(command)

        metadata = self.get_metadata(destination)

        return ProcessedAudio(
            source_path=str(source),
            output_path=str(destination),
            duration=metadata.duration,
            sample_rate=metadata.sample_rate,
            channels=metadata.channels,
            format=metadata.format,
            metadata={
                "operation": "mono_conversion",
            },
        )

    # ------------------------------------------------------------------
    # Chunking
    # ------------------------------------------------------------------

    def split(
        self,
        audio_path: str | Path,
        chunk_duration: int = 60,
        output_dir: Optional[str | Path] = None,
    ) -> List[ProcessedAudio]:
        """
        Split audio into fixed-duration chunks.

        Useful when a long interview recording needs to be processed
        in multiple STT requests.
        """

        source = self.validate(audio_path)

        if chunk_duration <= 0:
            raise ValueError(
                "chunk_duration must be greater than zero."
            )

        destination_dir = Path(
            output_dir
            or (
                self.output_dir
                / f"chunks_{uuid.uuid4().hex}"
            )
        )

        destination_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._check_ffmpeg()

        output_pattern = (
            destination_dir
            / "chunk_%03d.wav"
        )

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-f",
            "segment",
            "-segment_time",
            str(chunk_duration),
            "-reset_timestamps",
            "1",
            "-ac",
            str(self.channels),
            "-ar",
            str(self.sample_rate),
            "-c:a",
            "pcm_s16le",
            str(output_pattern),
        ]

        self._run_ffmpeg(command)

        chunks: List[ProcessedAudio] = []

        for chunk_path in sorted(
            destination_dir.glob("chunk_*.wav")
        ):
            metadata = self.get_metadata(chunk_path)

            chunks.append(
                ProcessedAudio(
                    source_path=str(source),
                    output_path=str(chunk_path),
                    duration=metadata.duration,
                    sample_rate=metadata.sample_rate,
                    channels=metadata.channels,
                    format=metadata.format,
                    metadata={
                        "operation": "chunk",
                        "chunk_duration": chunk_duration,
                    },
                )
            )

        return chunks

    # ------------------------------------------------------------------
    # Complete Pipeline
    # ------------------------------------------------------------------

    def process_for_interview(
        self,
        audio_path: str | Path,
    ) -> ProcessedAudio:
        """
        Run the standard interview audio preprocessing pipeline.

        Pipeline:

            Validate
              ↓
            Normalize
              ↓
            Convert to mono
              ↓
            Resample to 16 kHz
        """

        source = self.validate(audio_path)

        normalized = self.normalize(source)

        prepared = self.prepare_for_stt(
            normalized.output_path
        )

        # Remove intermediate normalized file when possible.
        if (
            normalized.output_path
            != prepared.output_path
        ):
            self._safe_remove(
                normalized.output_path
            )

        prepared.metadata.update(
            {
                "pipeline": [
                    "validation",
                    "normalization",
                    "mono_conversion",
                    "16khz_resampling",
                ]
            }
        )

        return prepared

    # ------------------------------------------------------------------
    # FFmpeg Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _check_ffmpeg() -> None:
        """Ensure FFmpeg and FFprobe are available."""

        if shutil.which("ffmpeg") is None:
            raise FFmpegNotFoundError(
                "FFmpeg is not installed or not available "
                "on PATH."
            )

        if shutil.which("ffprobe") is None:
            raise FFmpegNotFoundError(
                "FFprobe is not installed or not available "
                "on PATH."
            )

    @staticmethod
    def _run_ffmpeg(
        command: Sequence[str],
    ) -> None:
        """Execute an FFmpeg command."""

        logger.debug(
            "Running audio command: %s",
            " ".join(command),
        )

        try:
            result = subprocess.run(
                list(command),
                capture_output=True,
                text=True,
                check=True,
            )

        except FileNotFoundError as exc:
            raise FFmpegNotFoundError(
                "FFmpeg is not installed."
            ) from exc

        except subprocess.CalledProcessError as exc:
            raise AudioProcessingError(
                "Audio processing failed: "
                f"{exc.stderr}"
            ) from exc

        if result.returncode != 0:
            raise AudioProcessingError(
                "FFmpeg returned a non-zero exit code."
            )

    # ------------------------------------------------------------------
    # Path Helpers
    # ------------------------------------------------------------------

    def _create_output_path(
        self,
        output_path: Optional[str | Path],
        suffix: str,
        prefix: str,
    ) -> Path:
        """Create an output path."""

        if output_path:
            destination = Path(output_path)

            if not destination.suffix:
                destination = destination.with_suffix(
                    suffix
                )
        else:
            self.output_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            destination = (
                self.output_dir
                / f"{prefix}_{uuid.uuid4().hex}{suffix}"
            )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        return destination

    # ------------------------------------------------------------------
    # FFprobe Parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_ffprobe_output(
        output: str,
    ) -> Dict[str, str]:
        """Parse FFprobe key=value output."""

        values: Dict[str, str] = {}

        for line in output.splitlines():
            if "=" not in line:
                continue

            key, value = line.split(
                "=",
                1,
            )

            values[key.strip()] = value.strip()

        return values

    @staticmethod
    def _to_float(
        value: Optional[str],
    ) -> Optional[float]:
        """Safely convert a value to float."""

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_int(
        value: Optional[str],
    ) -> Optional[int]:
        """Safely convert a value to integer."""

        if value is None:
            return None

        try:
            return int(float(value))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _safe_remove(
        path: str | Path,
    ) -> None:
        """Remove a temporary file safely."""

        try:
            Path(path).unlink(
                missing_ok=True
            )
        except OSError:
            logger.warning(
                "Unable to remove temporary file: %s",
                path,
            )


# ----------------------------------------------------------------------
# Convenience Functions
# ----------------------------------------------------------------------


def prepare_audio_for_stt(
    audio_path: str | Path,
) -> ProcessedAudio:
    """Prepare an audio file for speech recognition."""

    processor = AudioProcessor()

    return processor.prepare_for_stt(
        audio_path
    )


def get_audio_metadata(
    audio_path: str | Path,
) -> AudioMetadata:
    """Get metadata for an audio file."""

    processor = AudioProcessor()

    return processor.get_metadata(
        audio_path
    )


__all__ = [
    "AudioProcessor",
    "AudioMetadata",
    "ProcessedAudio",
    "AudioProcessingError",
    "AudioFileNotFoundError",
    "UnsupportedAudioFormatError",
    "FFmpegNotFoundError",
    "prepare_audio_for_stt",
    "get_audio_metadata",
]