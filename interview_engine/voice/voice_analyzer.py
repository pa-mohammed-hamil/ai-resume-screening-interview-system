# Project scaffold file
"""
Voice Analyzer

Analyzes interview audio for speech-related characteristics.

Responsibilities:
- Calculate speaking duration
- Estimate words-per-minute
- Analyze pauses and silence
- Analyze audio volume
- Detect basic speech fluency indicators
- Produce structured metrics for interview reporting

This module intentionally focuses on observable audio/speech features.
It does not infer personality, mental state, emotion, or other sensitive
attributes from a candidate's voice.
"""

from __future__ import annotations

import logging
import math
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------


class VoiceAnalysisError(Exception):
    """Base exception for voice analysis failures."""


class AudioFileNotFoundError(VoiceAnalysisError):
    """Raised when the audio file does not exist."""


class UnsupportedAudioFormatError(VoiceAnalysisError):
    """Raised when the audio format is unsupported."""


class AudioAnalysisDependencyError(VoiceAnalysisError):
    """Raised when an audio analysis dependency is unavailable."""


# ----------------------------------------------------------------------
# Data Models
# ----------------------------------------------------------------------


@dataclass
class Pause:
    """Represents a detected pause in speech."""

    start: float
    end: float
    duration: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start": round(self.start, 3),
            "end": round(self.end, 3),
            "duration": round(self.duration, 3),
        }


@dataclass
class VoiceMetrics:
    """Observable speech/audio metrics."""

    duration_seconds: float = 0.0

    speech_duration_seconds: float = 0.0
    silence_duration_seconds: float = 0.0

    pause_count: int = 0
    long_pause_count: int = 0
    average_pause_seconds: float = 0.0
    longest_pause_seconds: float = 0.0

    word_count: int = 0
    words_per_minute: float = 0.0

    rms_db: Optional[float] = None
    peak_db: Optional[float] = None

    estimated_speech_ratio: float = 0.0

    fluency_score: Optional[float] = None

    pauses: List[Pause] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "duration_seconds": round(
                self.duration_seconds,
                3,
            ),
            "speech_duration_seconds": round(
                self.speech_duration_seconds,
                3,
            ),
            "silence_duration_seconds": round(
                self.silence_duration_seconds,
                3,
            ),
            "pause_count": self.pause_count,
            "long_pause_count": self.long_pause_count,
            "average_pause_seconds": round(
                self.average_pause_seconds,
                3,
            ),
            "longest_pause_seconds": round(
                self.longest_pause_seconds,
                3,
            ),
            "word_count": self.word_count,
            "words_per_minute": round(
                self.words_per_minute,
                2,
            ),
            "rms_db": (
                round(self.rms_db, 2)
                if self.rms_db is not None
                else None
            ),
            "peak_db": (
                round(self.peak_db, 2)
                if self.peak_db is not None
                else None
            ),
            "estimated_speech_ratio": round(
                self.estimated_speech_ratio,
                3,
            ),
            "fluency_score": (
                round(self.fluency_score, 2)
                if self.fluency_score is not None
                else None
            ),
            "pauses": [
                pause.to_dict()
                for pause in self.pauses
            ],
            "warnings": self.warnings,
        }


@dataclass
class VoiceAnalysisResult:
    """Complete voice-analysis result."""

    audio_path: str
    metrics: VoiceMetrics
    transcript: Optional[str] = None
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audio_path": self.audio_path,
            "transcript": self.transcript,
            "metrics": self.metrics.to_dict(),
            "metadata": self.metadata,
        }


# ----------------------------------------------------------------------
# Voice Analyzer
# ----------------------------------------------------------------------


class VoiceAnalyzer:
    """
    Analyze observable speech characteristics from interview audio.

    The analyzer uses:
        - FFmpeg / FFprobe for audio information
        - Optional librosa for detailed signal analysis

    Example:

        analyzer = VoiceAnalyzer()

        result = analyzer.analyze(
            "storage/interview_audio/interview.wav",
            transcript="I have five years of Python experience."
        )

        print(result.metrics.words_per_minute)
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

    DEFAULT_SILENCE_THRESHOLD_DB = -40.0
    DEFAULT_LONG_PAUSE_SECONDS = 2.0

    def __init__(
        self,
        silence_threshold_db: float = DEFAULT_SILENCE_THRESHOLD_DB,
        long_pause_seconds: float = DEFAULT_LONG_PAUSE_SECONDS,
    ) -> None:

        self.silence_threshold_db = silence_threshold_db
        self.long_pause_seconds = max(
            0.1,
            long_pause_seconds,
        )

    # ------------------------------------------------------------------
    # Main API
    # ------------------------------------------------------------------

    def analyze(
        self,
        audio_path: str | Path,
        transcript: Optional[str] = None,
    ) -> VoiceAnalysisResult:
        """
        Analyze an interview recording.

        Args:
            audio_path:
                Path to the interview audio.

            transcript:
                Optional transcript from speech_to_text.py.

        Returns:
            VoiceAnalysisResult
        """

        path = self._validate_audio(audio_path)

        logger.info(
            "Starting voice analysis: %s",
            path,
        )

        duration = self._get_duration(path)

        audio_stats = self._analyze_audio_signal(
            path
        )

        pauses = self.detect_pauses(
            path,
            duration=duration,
        )

        word_count = self._word_count(
            transcript
        )

        speech_duration = max(
            0.0,
            duration
            - sum(
                pause.duration
                for pause in pauses
            ),
        )

        silence_duration = max(
            0.0,
            duration - speech_duration,
        )

        words_per_minute = self.calculate_wpm(
            word_count=word_count,
            speech_duration=speech_duration,
        )

        speech_ratio = (
            speech_duration / duration
            if duration > 0
            else 0.0
        )

        fluency_score = self.calculate_fluency_score(
            words_per_minute=words_per_minute,
            pause_count=len(pauses),
            long_pause_count=sum(
                1
                for pause in pauses
                if pause.duration
                >= self.long_pause_seconds
            ),
            speech_ratio=speech_ratio,
        )

        warnings = self._generate_warnings(
            duration=duration,
            words_per_minute=words_per_minute,
            speech_ratio=speech_ratio,
            pauses=pauses,
            rms_db=audio_stats.get("rms_db"),
        )

        metrics = VoiceMetrics(
            duration_seconds=duration,
            speech_duration_seconds=speech_duration,
            silence_duration_seconds=silence_duration,
            pause_count=len(pauses),
            long_pause_count=sum(
                1
                for pause in pauses
                if pause.duration
                >= self.long_pause_seconds
            ),
            average_pause_seconds=(
                self._average_pause(pauses)
            ),
            longest_pause_seconds=(
                max(
                    (pause.duration for pause in pauses),
                    default=0.0,
                )
            ),
            word_count=word_count,
            words_per_minute=words_per_minute,
            rms_db=audio_stats.get("rms_db"),
            peak_db=audio_stats.get("peak_db"),
            estimated_speech_ratio=speech_ratio,
            fluency_score=fluency_score,
            pauses=pauses,
            warnings=warnings,
        )

        logger.info(
            "Voice analysis completed: %s",
            path,
        )

        return VoiceAnalysisResult(
            audio_path=str(path),
            transcript=transcript,
            metrics=metrics,
            metadata={
                "analyzer": "VoiceAnalyzer",
                "silence_threshold_db": (
                    self.silence_threshold_db
                ),
                "long_pause_seconds": (
                    self.long_pause_seconds
                ),
            },
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_audio(
        self,
        audio_path: str | Path,
    ) -> Path:
        """Validate audio input."""

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
                f"Unsupported audio format: {path.suffix}"
            )

        if path.stat().st_size == 0:
            raise VoiceAnalysisError(
                "Audio file is empty."
            )

        return path

    # ------------------------------------------------------------------
    # Duration
    # ------------------------------------------------------------------

    def _get_duration(
        self,
        audio_path: Path,
    ) -> float:
        """Get audio duration using FFprobe."""

        self._check_ffprobe()

        command = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise VoiceAnalysisError(
                f"Unable to determine audio duration: "
                f"{exc.stderr}"
            ) from exc

        try:
            return max(
                0.0,
                float(result.stdout.strip()),
            )
        except ValueError as exc:
            raise VoiceAnalysisError(
                "Invalid duration returned by FFprobe."
            ) from exc

    # ------------------------------------------------------------------
    # Signal Analysis
    # ------------------------------------------------------------------

    def _analyze_audio_signal(
        self,
        audio_path: Path,
    ) -> Dict[str, Optional[float]]:
        """
        Analyze RMS and peak volume.

        Uses librosa when available. If librosa is unavailable,
        returns metadata without failing the complete analysis.
        """

        try:
            import librosa
            import numpy as np
        except ImportError:
            logger.warning(
                "librosa/numpy unavailable; "
                "skipping detailed signal analysis."
            )

            return {
                "rms_db": None,
                "peak_db": None,
            }

        try:
            audio, _ = librosa.load(
                str(audio_path),
                sr=None,
                mono=True,
            )

            if audio.size == 0:
                return {
                    "rms_db": None,
                    "peak_db": None,
                }

            rms = float(
                np.sqrt(
                    np.mean(
                        np.square(audio)
                    )
                )
            )

            peak = float(
                np.max(
                    np.abs(audio)
                )
            )

            return {
                "rms_db": self._amplitude_to_db(
                    rms
                ),
                "peak_db": self._amplitude_to_db(
                    peak
                ),
            }

        except Exception as exc:
            logger.warning(
                "Signal analysis failed: %s",
                exc,
            )

            return {
                "rms_db": None,
                "peak_db": None,
            }

    # ------------------------------------------------------------------
    # Pause Detection
    # ------------------------------------------------------------------

    def detect_pauses(
        self,
        audio_path: str | Path,
        duration: Optional[float] = None,
    ) -> List[Pause]:
        """
        Detect silent regions using FFmpeg's silencedetect filter.

        Returns:
            List of detected pauses.
        """

        path = self._validate_audio(audio_path)

        self._check_ffmpeg()

        command = [
            "ffmpeg",
            "-i",
            str(path),
            "-af",
            (
                "silencedetect="
                f"noise={self.silence_threshold_db}dB:"
                "d=0.5"
            ),
            "-f",
            "null",
            "-",
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
            )

        except FileNotFoundError as exc:
            raise AudioAnalysisDependencyError(
                "FFmpeg is not installed."
            ) from exc

        output = (
            result.stderr
            + "\n"
            + result.stdout
        )

        pauses = self._parse_silence_output(
            output
        )

        if duration is not None:
            pauses = [
                pause
                for pause in pauses
                if pause.start < duration
            ]

        return pauses

    def _parse_silence_output(
        self,
        output: str,
    ) -> List[Pause]:
        """Parse FFmpeg silencedetect output."""

        pauses: List[Pause] = []

        current_start: Optional[float] = None

        for line in output.splitlines():
            line = line.strip()

            if "silence_start:" in line:
                try:
                    value = line.split(
                        "silence_start:",
                        1,
                    )[1].strip()

                    current_start = float(
                        value.split()[0]
                    )

                except (
                    ValueError,
                    IndexError,
                ):
                    current_start = None

            elif "silence_end:" in line:
                try:
                    value = line.split(
                        "silence_end:",
                        1,
                    )[1].strip()

                    parts = value.split()

                    end = float(parts[0])

                    if current_start is not None:
                        duration = max(
                            0.0,
                            end - current_start,
                        )

                        pauses.append(
                            Pause(
                                start=current_start,
                                end=end,
                                duration=duration,
                            )
                        )

                    current_start = None

                except (
                    ValueError,
                    IndexError,
                ):
                    current_start = None

        return pauses

    # ------------------------------------------------------------------
    # Speaking Rate
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_wpm(
        word_count: int,
        speech_duration: float,
    ) -> float:
        """
        Calculate words per minute.

        Returns 0 when there is insufficient information.
        """

        if word_count <= 0:
            return 0.0

        if speech_duration <= 0:
            return 0.0

        return round(
            word_count
            / (speech_duration / 60.0),
            2,
        )

    # ------------------------------------------------------------------
    # Fluency Metrics
    # ------------------------------------------------------------------

    def calculate_fluency_score(
        self,
        words_per_minute: float,
        pause_count: int,
        long_pause_count: int,
        speech_ratio: float,
    ) -> float:
        """
        Calculate a simple speech-flow score.

        This is an operational audio metric, not a measure of
        intelligence, personality, confidence, or employability.

        Score range:
            0-100
        """

        score = 100.0

        # Conversational speaking-rate range.
        if words_per_minute == 0:
            score -= 40

        elif words_per_minute < 70:
            score -= 20

        elif words_per_minute < 90:
            score -= 10

        elif words_per_minute > 190:
            score -= 20

        elif words_per_minute > 170:
            score -= 10

        # Penalize excessive long pauses.
        score -= min(
            30,
            long_pause_count * 5,
        )

        # Penalize extremely low speech ratio.
        if speech_ratio < 0.35:
            score -= 20

        elif speech_ratio < 0.50:
            score -= 10

        # Avoid over-penalizing ordinary pauses.
        if pause_count == 0 and words_per_minute > 0:
            score -= 2

        return round(
            max(0.0, min(100.0, score)),
            2,
        )

    # ------------------------------------------------------------------
    # Warnings
    # ------------------------------------------------------------------

    def _generate_warnings(
        self,
        duration: float,
        words_per_minute: float,
        speech_ratio: float,
        pauses: Sequence[Pause],
        rms_db: Optional[float],
    ) -> List[str]:
        """Generate technical speech-quality warnings."""

        warnings: List[str] = []

        if duration < 2:
            warnings.append(
                "Audio duration is very short for reliable analysis."
            )

        if words_per_minute > 0:
            if words_per_minute < 60:
                warnings.append(
                    "Speech rate is unusually slow."
                )

            elif words_per_minute > 200:
                warnings.append(
                    "Speech rate is unusually fast."
                )

        if speech_ratio < 0.30:
            warnings.append(
                "A large portion of the recording is silent."
            )

        long_pauses = [
            pause
            for pause in pauses
            if pause.duration
            >= self.long_pause_seconds
        ]

        if len(long_pauses) >= 3:
            warnings.append(
                "Multiple long pauses were detected."
            )

        if rms_db is not None:
            if rms_db < -35:
                warnings.append(
                    "Audio level may be too quiet."
                )

            elif rms_db > -3:
                warnings.append(
                    "Audio level may be too loud or clipped."
                )

        return warnings

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _word_count(
        transcript: Optional[str],
    ) -> int:
        """Count words in a transcript."""

        if not transcript:
            return 0

        return len(
            transcript.strip().split()
        )

    @staticmethod
    def _average_pause(
        pauses: Sequence[Pause],
    ) -> float:
        """Calculate average pause duration."""

        if not pauses:
            return 0.0

        return round(
            sum(
                pause.duration
                for pause in pauses
            ) / len(pauses),
            3,
        )

    @staticmethod
    def _amplitude_to_db(
        amplitude: float,
    ) -> float:
        """Convert linear amplitude to decibels."""

        if amplitude <= 0:
            return -float("inf")

        return 20.0 * math.log10(
            amplitude
        )

    @staticmethod
    def _check_ffmpeg() -> None:
        """Check that FFmpeg is installed."""

        if shutil.which("ffmpeg") is None:
            raise AudioAnalysisDependencyError(
                "FFmpeg is not installed or unavailable "
                "on PATH."
            )

    @staticmethod
    def _check_ffprobe() -> None:
        """Check that FFprobe is installed."""

        if shutil.which("ffprobe") is None:
            raise AudioAnalysisDependencyError(
                "FFprobe is not installed or unavailable "
                "on PATH."
            )


# ----------------------------------------------------------------------
# Convenience Functions
# ----------------------------------------------------------------------


def analyze_voice(
    audio_path: str | Path,
    transcript: Optional[str] = None,
) -> VoiceAnalysisResult:
    """
    Analyze interview voice/audio.

    Example:

        result = analyze_voice(
            "storage/interview_audio/answer.wav",
            transcript="I worked with Python and FastAPI."
        )
    """

    analyzer = VoiceAnalyzer()

    return analyzer.analyze(
        audio_path=audio_path,
        transcript=transcript,
    )


def calculate_speaking_rate(
    transcript: str,
    duration_seconds: float,
) -> float:
    """Calculate words per minute from transcript and duration."""

    word_count = len(
        transcript.strip().split()
    )

    return VoiceAnalyzer.calculate_wpm(
        word_count=word_count,
        speech_duration=duration_seconds,
    )


__all__ = [
    "VoiceAnalyzer",
    "VoiceMetrics",
    "VoiceAnalysisResult",
    "Pause",
    "VoiceAnalysisError",
    "AudioFileNotFoundError",
    "UnsupportedAudioFormatError",
    "AudioAnalysisDependencyError",
    "analyze_voice",
    "calculate_speaking_rate",
]