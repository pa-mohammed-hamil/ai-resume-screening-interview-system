# Project scaffold file
"""
Semantic Resume ↔ Job Matcher
==============================

Location:
    ai/matching/semantic_matcher.py

Purpose:
    Calculate semantic similarity between resume content and job
    descriptions using embeddings.

Primary approach:
    sentence-transformers

Fallback:
    Deterministic TF-IDF-style cosine similarity using token counts.

This module is intentionally independent from the API/backend layer so
it can be used by:

    - resume_job_matcher.py
    - candidate_ranker.py
    - ranking_explainer.py
    - evaluation scripts
    - batch matching jobs
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence


# ============================================================================
# Optional sentence-transformers dependency
# ============================================================================

try:
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False


# ============================================================================
# Constants
# ============================================================================

DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"

DEFAULT_THRESHOLD = 0.60

MIN_SIMILARITY = 0.0
MAX_SIMILARITY = 1.0

TOKEN_PATTERN = re.compile(
    r"[a-zA-Z0-9+#.\-]+"
)

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "were",
    "will",
    "with",
    "you",
    "your",
}


# ============================================================================
# Data Models
# ============================================================================


@dataclass
class SemanticMatch:
    """
    Represents semantic similarity between two text segments.
    """

    score: float

    matched: bool

    threshold: float

    resume_text: str = ""

    job_text: str = ""

    model: str = "fallback"

    method: str = "token_cosine"

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "matched": self.matched,
            "threshold": self.threshold,
            "resume_text": self.resume_text,
            "job_text": self.job_text,
            "model": self.model,
            "method": self.method,
            "metadata": self.metadata,
        }


@dataclass
class SemanticBatchResult:
    """
    Results for multiple resume/job comparisons.
    """

    scores: list[float]

    average_score: float

    maximum_score: float

    minimum_score: float

    threshold: float

    matched_count: int

    total_count: int

    results: list[SemanticMatch] = field(
        default_factory=list
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "scores": self.scores,
            "average_score": self.average_score,
            "maximum_score": self.maximum_score,
            "minimum_score": self.minimum_score,
            "threshold": self.threshold,
            "matched_count": self.matched_count,
            "total_count": self.total_count,
            "results": [
                result.to_dict()
                for result in self.results
            ],
        }


# ============================================================================
# Text Utilities
# ============================================================================


def _clean_text(text: Any) -> str:
    """
    Normalize input text.
    """

    if text is None:
        return ""

    return " ".join(
        str(text)
        .lower()
        .split()
    )


def _tokenize(text: str) -> list[str]:
    """
    Tokenize text while preserving useful technical tokens.

    Examples:
        Python
        C++
        C#
        React.js
        PostgreSQL
        FastAPI
    """

    text = _clean_text(text)

    tokens = TOKEN_PATTERN.findall(
        text
    )

    return [
        token
        for token in tokens
        if token not in STOP_WORDS
    ]


def _token_counts(
    text: str,
) -> Counter[str]:
    """
    Create token-frequency representation.
    """

    return Counter(
        _tokenize(text)
    )


# ============================================================================
# Vector Similarity
# ============================================================================


def cosine_similarity(
    vector_a: Sequence[float],
    vector_b: Sequence[float],
) -> float:
    """
    Calculate cosine similarity.

    Returns:
        Value between 0 and 1.
    """

    if not vector_a or not vector_b:
        return 0.0

    if len(vector_a) != len(vector_b):
        raise ValueError(
            "Vectors must have the same length."
        )

    dot_product = sum(
        a * b
        for a, b in zip(
            vector_a,
            vector_b,
        )
    )

    norm_a = math.sqrt(
        sum(
            value * value
            for value in vector_a
        )
    )

    norm_b = math.sqrt(
        sum(
            value * value
            for value in vector_b
        )
    )

    if norm_a == 0 or norm_b == 0:
        return 0.0

    similarity = (
        dot_product
        / (norm_a * norm_b)
    )

    return max(
        MIN_SIMILARITY,
        min(
            MAX_SIMILARITY,
            similarity,
        ),
    )


def _counter_cosine_similarity(
    counter_a: Counter[str],
    counter_b: Counter[str],
) -> float:
    """
    Calculate cosine similarity between token-frequency vectors.
    """

    if not counter_a or not counter_b:
        return 0.0

    vocabulary = set(counter_a) | set(
        counter_b
    )

    vector_a = [
        float(counter_a.get(token, 0))
        for token in vocabulary
    ]

    vector_b = [
        float(counter_b.get(token, 0))
        for token in vocabulary
    ]

    return cosine_similarity(
        vector_a,
        vector_b,
    )


# ============================================================================
# Fallback Semantic Matcher
# ============================================================================


class FallbackSemanticMatcher:
    """
    Lightweight semantic matcher used when sentence-transformers
    is unavailable.

    This is not a true language-model semantic embedding.
    It provides deterministic lexical similarity and keeps the
    application functional in minimal environments.
    """

    def similarity(
        self,
        text_a: str,
        text_b: str,
    ) -> float:
        """
        Calculate token-based cosine similarity.
        """

        return _counter_cosine_similarity(
            _token_counts(text_a),
            _token_counts(text_b),
        )

    def batch_similarity(
        self,
        texts_a: Sequence[str],
        texts_b: Sequence[str],
    ) -> list[float]:
        """
        Calculate pairwise similarities.
        """

        if len(texts_a) != len(texts_b):
            raise ValueError(
                "texts_a and texts_b must have the same length."
            )

        return [
            self.similarity(
                text_a,
                text_b,
            )
            for text_a, text_b
            in zip(texts_a, texts_b)
        ]


# ============================================================================
# Main Semantic Matcher
# ============================================================================


class SemanticMatcher:
    """
    Semantic similarity engine.

    Uses SentenceTransformer when installed.

    Example:

        matcher = SemanticMatcher()

        score = matcher.similarity(
            resume_text,
            job_description,
        )

        print(score)

    Score:
        0.0 -> no semantic similarity
        1.0 -> highly similar
    """

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        threshold: float = DEFAULT_THRESHOLD,
        use_embeddings: bool = True,
    ) -> None:

        if not 0.0 <= threshold <= 1.0:
            raise ValueError(
                "threshold must be between 0 and 1."
            )

        self.model_name = model_name

        self.threshold = threshold

        self.model = None

        self.method = "token_cosine"

        self._fallback = (
            FallbackSemanticMatcher()
        )

        if (
            use_embeddings
            and SENTENCE_TRANSFORMERS_AVAILABLE
            and SentenceTransformer is not None
        ):
            try:
                self.model = (
                    SentenceTransformer(
                        model_name
                    )
                )

                self.method = "sentence_transformer"

            except Exception:
                self.model = None
                self.method = "token_cosine"

    # ----------------------------------------------------------------------
    # Properties
    # ----------------------------------------------------------------------

    @property
    def using_embeddings(self) -> bool:
        """
        Return whether a transformer model is active.
        """

        return self.model is not None

    # ----------------------------------------------------------------------
    # Encoding
    # ----------------------------------------------------------------------

    def encode(
        self,
        texts: str | Sequence[str],
    ) -> Any:
        """
        Encode text using the configured embedding model.

        Raises:
            RuntimeError if embeddings are unavailable.
        """

        if self.model is None:
            raise RuntimeError(
                "SentenceTransformer model is not available."
            )

        if isinstance(
            texts,
            str,
        ):
            texts = [texts]

        return self.model.encode(
            list(texts),
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

    # ----------------------------------------------------------------------
    # Embedding Similarity
    # ----------------------------------------------------------------------

    def _embedding_similarity(
        self,
        text_a: str,
        text_b: str,
    ) -> float:
        """
        Calculate cosine similarity from normalized embeddings.
        """

        embeddings = self.encode(
            [
                text_a,
                text_b,
            ]
        )

        vector_a = embeddings[0]
        vector_b = embeddings[1]

        score = cosine_similarity(
            vector_a.tolist(),
            vector_b.tolist(),
        )

        return float(score)

    # ----------------------------------------------------------------------
    # Similarity
    # ----------------------------------------------------------------------

    def similarity(
        self,
        text_a: str,
        text_b: str,
    ) -> float:
        """
        Calculate semantic similarity.

        Returns:
            Float from 0 to 1.
        """

        text_a = _clean_text(
            text_a
        )

        text_b = _clean_text(
            text_b
        )

        if not text_a or not text_b:
            return 0.0

        if self.model is not None:

            try:
                return round(
                    self._embedding_similarity(
                        text_a,
                        text_b,
                    ),
                    6,
                )

            except Exception:
                # Graceful fallback.
                pass

        return round(
            self._fallback.similarity(
                text_a,
                text_b,
            ),
            6,
        )

    # ----------------------------------------------------------------------
    # Percentage Similarity
    # ----------------------------------------------------------------------

    def similarity_percentage(
        self,
        text_a: str,
        text_b: str,
    ) -> float:
        """
        Return semantic similarity as 0-100.
        """

        return round(
            self.similarity(
                text_a,
                text_b,
            )
            * 100,
            2,
        )

    # ----------------------------------------------------------------------
    # Threshold Match
    # ----------------------------------------------------------------------

    def is_match(
        self,
        text_a: str,
        text_b: str,
        threshold: float | None = None,
    ) -> bool:
        """
        Determine whether two texts meet the semantic threshold.
        """

        threshold = (
            self.threshold
            if threshold is None
            else threshold
        )

        if not 0.0 <= threshold <= 1.0:
            raise ValueError(
                "threshold must be between 0 and 1."
            )

        return (
            self.similarity(
                text_a,
                text_b,
            )
            >= threshold
        )

    # ----------------------------------------------------------------------
    # Detailed Match
    # ----------------------------------------------------------------------

    def match(
        self,
        resume_text: str,
        job_text: str,
        threshold: float | None = None,
    ) -> dict[str, Any]:
        """
        Return detailed semantic match information.
        """

        threshold = (
            self.threshold
            if threshold is None
            else threshold
        )

        score = self.similarity(
            resume_text,
            job_text,
        )

        result = SemanticMatch(
            score=score,
            matched=score >= threshold,
            threshold=threshold,
            resume_text=resume_text,
            job_text=job_text,
            model=(
                self.model_name
                if self.model is not None
                else "fallback"
            ),
            method=self.method,
            metadata={
                "embedding_available": (
                    self.model is not None
                ),
            },
        )

        return result.to_dict()

    # ----------------------------------------------------------------------
    # Batch Similarity
    # ----------------------------------------------------------------------

    def batch_similarity(
        self,
        texts_a: Sequence[str],
        texts_b: Sequence[str],
    ) -> list[float]:
        """
        Calculate pairwise similarity for multiple text pairs.
        """

        if len(texts_a) != len(texts_b):
            raise ValueError(
                "texts_a and texts_b must have the same length."
            )

        if (
            self.model is not None
            and texts_a
        ):
            try:
                embeddings_a = self.encode(
                    texts_a
                )

                embeddings_b = self.encode(
                    texts_b
                )

                scores: list[float] = []

                for vector_a, vector_b in zip(
                    embeddings_a,
                    embeddings_b,
                ):
                    score = cosine_similarity(
                        vector_a.tolist(),
                        vector_b.tolist(),
                    )

                    scores.append(
                        round(
                            float(score),
                            6,
                        )
                    )

                return scores

            except Exception:
                pass

        return self._fallback.batch_similarity(
            texts_a,
            texts_b,
        )

    # ----------------------------------------------------------------------
    # Batch Detailed Match
    # ----------------------------------------------------------------------

    def batch_match(
        self,
        texts_a: Sequence[str],
        texts_b: Sequence[str],
        threshold: float | None = None,
    ) -> SemanticBatchResult:
        """
        Calculate detailed results for multiple text pairs.
        """

        threshold = (
            self.threshold
            if threshold is None
            else threshold
        )

        scores = self.batch_similarity(
            texts_a,
            texts_b,
        )

        results = [
            SemanticMatch(
                score=score,
                matched=score >= threshold,
                threshold=threshold,
                resume_text=text_a,
                job_text=text_b,
                model=(
                    self.model_name
                    if self.model is not None
                    else "fallback"
                ),
                method=self.method,
            )
            for text_a, text_b, score
            in zip(
                texts_a,
                texts_b,
                scores,
            )
        ]

        if scores:
            average_score = (
                sum(scores)
                / len(scores)
            )

            maximum_score = max(
                scores
            )

            minimum_score = min(
                scores
            )

        else:
            average_score = 0.0
            maximum_score = 0.0
            minimum_score = 0.0

        matched_count = sum(
            result.matched
            for result in results
        )

        return SemanticBatchResult(
            scores=scores,
            average_score=round(
                average_score,
                6,
            ),
            maximum_score=round(
                maximum_score,
                6,
            ),
            minimum_score=round(
                minimum_score,
                6,
            ),
            threshold=threshold,
            matched_count=matched_count,
            total_count=len(results),
            results=results,
        )

    # ----------------------------------------------------------------------
    # Resume ↔ Job API
    # ----------------------------------------------------------------------

    def match_resume_to_job(
        self,
        resume_text: str,
        job_text: str,
    ) -> dict[str, Any]:
        """
        Convenience API specifically for resume-job matching.
        """

        return self.match(
            resume_text=resume_text,
            job_text=job_text,
        )

    # ----------------------------------------------------------------------
    # Resume ↔ Multiple Jobs
    # ----------------------------------------------------------------------

    def rank_jobs_for_resume(
        self,
        resume_text: str,
        jobs: Sequence[
            Mapping[str, Any]
        ],
        text_key: str = "description",
    ) -> list[dict[str, Any]]:
        """
        Rank multiple jobs against one resume.

        Expected input:

            [
                {
                    "id": 1,
                    "title": "Python Developer",
                    "description": "..."
                },
                ...
            ]
        """

        if not jobs:
            return []

        job_texts = [
            str(
                job.get(
                    text_key,
                    "",
                )
            )
            for job in jobs
        ]

        resume_texts = [
            resume_text
            for _ in jobs
        ]

        scores = self.batch_similarity(
            resume_texts,
            job_texts,
        )

        ranked: list[dict[str, Any]] = []

        for job, score in zip(
            jobs,
            scores,
        ):
            item = dict(job)

            item["semantic_score"] = round(
                score * 100,
                2,
            )

            item["semantic_match"] = (
                score >= self.threshold
            )

            ranked.append(item)

        ranked.sort(
            key=lambda item: item[
                "semantic_score"
            ],
            reverse=True,
        )

        return ranked

    # ----------------------------------------------------------------------
    # Job ↔ Multiple Resumes
    # ----------------------------------------------------------------------

    def rank_resumes_for_job(
        self,
        job_text: str,
        resumes: Sequence[
            Mapping[str, Any]
        ],
        text_key: str = "resume_text",
    ) -> list[dict[str, Any]]:
        """
        Rank multiple resumes against one job.
        """

        if not resumes:
            return []

        resume_texts = [
            str(
                resume.get(
                    text_key,
                    "",
                )
            )
            for resume in resumes
        ]

        job_texts = [
            job_text
            for _ in resumes
        ]

        scores = self.batch_similarity(
            resume_texts,
            job_texts,
        )

        ranked: list[dict[str, Any]] = []

        for resume, score in zip(
            resumes,
            scores,
        ):
            item = dict(resume)

            item["semantic_score"] = round(
                score * 100,
                2,
            )

            item["semantic_match"] = (
                score >= self.threshold
            )

            ranked.append(item)

        ranked.sort(
            key=lambda item: item[
                "semantic_score"
            ],
            reverse=True,
        )

        return ranked


# ============================================================================
# Section-Level Matching
# ============================================================================


def section_similarity(
    matcher: SemanticMatcher,
    resume_sections: Mapping[str, str],
    job_sections: Mapping[str, str],
) -> dict[str, float]:
    """
    Compare corresponding resume and job sections.

    Example:

        resume_sections = {
            "summary": "...",
            "experience": "...",
            "skills": "...",
        }

        job_sections = {
            "summary": "...",
            "experience": "...",
            "skills": "...",
        }
    """

    result: dict[str, float] = {}

    for section, job_text in job_sections.items():

        resume_text = resume_sections.get(
            section,
            "",
        )

        result[section] = (
            matcher.similarity(
                resume_text,
                job_text,
            )
        )

    return result


def weighted_section_similarity(
    matcher: SemanticMatcher,
    resume_sections: Mapping[str, str],
    job_sections: Mapping[str, str],
    weights: Mapping[str, float] | None = None,
) -> float:
    """
    Calculate weighted semantic similarity across sections.

    Example weights:

        {
            "experience": 0.40,
            "skills": 0.35,
            "summary": 0.15,
            "education": 0.10,
        }
    """

    similarities = section_similarity(
        matcher,
        resume_sections,
        job_sections,
    )

    if not similarities:
        return 0.0

    if weights is None:
        weights = {
            section: 1.0
            for section in similarities
        }

    total_weight = 0.0
    weighted_score = 0.0

    for section, score in similarities.items():

        weight = float(
            weights.get(
                section,
                1.0,
            )
        )

        if weight <= 0:
            continue

        weighted_score += (
            score * weight
        )

        total_weight += weight

    if total_weight <= 0:
        return 0.0

    return round(
        weighted_score / total_weight,
        6,
    )


# ============================================================================
# Similarity Classification
# ============================================================================


def classify_similarity(
    score: float,
) -> str:
    """
    Convert similarity score into a human-readable category.

    Input:
        0.0 - 1.0

    Output:
        very_low
        low
        moderate
        high
        very_high
    """

    score = max(
        0.0,
        min(1.0, score),
    )

    if score >= 0.85:
        return "very_high"

    if score >= 0.70:
        return "high"

    if score >= 0.50:
        return "moderate"

    if score >= 0.30:
        return "low"

    return "very_low"


# ============================================================================
# Functional API
# ============================================================================


_default_matcher: SemanticMatcher | None = None


def get_default_matcher() -> SemanticMatcher:
    """
    Lazily create the default semantic matcher.
    """

    global _default_matcher

    if _default_matcher is None:
        _default_matcher = SemanticMatcher()

    return _default_matcher


def semantic_similarity(
    text_a: str,
    text_b: str,
) -> float:
    """
    Functional API returning a score from 0 to 1.
    """

    return get_default_matcher().similarity(
        text_a,
        text_b,
    )


def semantic_similarity_percentage(
    text_a: str,
    text_b: str,
) -> float:
    """
    Functional API returning a score from 0 to 100.
    """

    return get_default_matcher().similarity_percentage(
        text_a,
        text_b,
    )


def semantic_match(
    text_a: str,
    text_b: str,
    threshold: float = DEFAULT_THRESHOLD,
) -> bool:
    """
    Functional API for threshold-based matching.
    """

    return get_default_matcher().is_match(
        text_a,
        text_b,
        threshold=threshold,
    )


def match_resume_to_job(
    resume_text: str,
    job_text: str,
    threshold: float = DEFAULT_THRESHOLD,
) -> dict[str, Any]:
    """
    Functional resume-job semantic matching API.
    """

    matcher = get_default_matcher()

    return matcher.match(
        resume_text=resume_text,
        job_text=job_text,
        threshold=threshold,
    )


def rank_resumes_for_job(
    job_text: str,
    resumes: Sequence[
        Mapping[str, Any]
    ],
    text_key: str = "resume_text",
) -> list[dict[str, Any]]:
    """
    Rank resumes by semantic similarity.
    """

    return get_default_matcher().rank_resumes_for_job(
        job_text=job_text,
        resumes=resumes,
        text_key=text_key,
    )


def rank_jobs_for_resume(
    resume_text: str,
    jobs: Sequence[
        Mapping[str, Any]
    ],
    text_key: str = "description",
) -> list[dict[str, Any]]:
    """
    Rank jobs by semantic similarity.
    """

    return get_default_matcher().rank_jobs_for_resume(
        resume_text=resume_text,
        jobs=jobs,
        text_key=text_key,
    )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "SemanticMatch",
    "SemanticBatchResult",
    "SemanticMatcher",
    "FallbackSemanticMatcher",
    "cosine_similarity",
    "section_similarity",
    "weighted_section_similarity",
    "classify_similarity",
    "get_default_matcher",
    "semantic_similarity",
    "semantic_similarity_percentage",
    "semantic_match",
    "match_resume_to_job",
    "rank_resumes_for_job",
    "rank_jobs_for_resume",
]