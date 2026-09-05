# Project scaffold file
"""
Keyword Resume ↔ Job Matcher
=============================

Location:
    ai/matching/keyword_matcher.py

Purpose:
    Match resume text against job-description keywords.

Features:
    - Exact keyword matching
    - Case-insensitive matching
    - Phrase matching
    - Technical keyword normalization
    - Skill-aware matching
    - Required/preferred keyword scoring
    - Missing keyword detection
    - Explainable match results
    - Batch matching
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence


# ============================================================================
# Constants
# ============================================================================

DEFAULT_REQUIRED_WEIGHT = 0.80
DEFAULT_PREFERRED_WEIGHT = 0.20

MIN_SCORE = 0.0
MAX_SCORE = 100.0

TOKEN_PATTERN = re.compile(
    r"[a-zA-Z0-9+#.\-/]+"
)

WHITESPACE_PATTERN = re.compile(
    r"\s+"
)


# ============================================================================
# Keyword Aliases
# ============================================================================

KEYWORD_ALIASES: dict[str, set[str]] = {
    "python": {
        "python",
        "python3",
        "py",
    },
    "javascript": {
        "javascript",
        "js",
        "ecmascript",
    },
    "typescript": {
        "typescript",
        "ts",
    },
    "react": {
        "react",
        "reactjs",
        "react.js",
    },
    "node.js": {
        "node",
        "nodejs",
        "node.js",
    },
    "fastapi": {
        "fastapi",
        "fast-api",
    },
    "postgresql": {
        "postgresql",
        "postgres",
        "psql",
    },
    "mongodb": {
        "mongodb",
        "mongo",
        "mongo db",
    },
    "mysql": {
        "mysql",
        "my sql",
    },
    "docker": {
        "docker",
        "docker container",
        "docker containers",
    },
    "kubernetes": {
        "kubernetes",
        "k8s",
    },
    "amazon web services": {
        "aws",
        "amazon web services",
    },
    "google cloud platform": {
        "gcp",
        "google cloud",
        "google cloud platform",
    },
    "microsoft azure": {
        "azure",
        "microsoft azure",
    },
    "machine learning": {
        "machine learning",
        "ml",
    },
    "deep learning": {
        "deep learning",
        "dl",
    },
    "artificial intelligence": {
        "artificial intelligence",
        "ai",
    },
    "natural language processing": {
        "natural language processing",
        "nlp",
    },
    "large language model": {
        "large language model",
        "large language models",
        "llm",
        "llms",
    },
    "generative ai": {
        "generative ai",
        "genai",
        "gen ai",
    },
    "rest api": {
        "rest api",
        "rest apis",
        "restful api",
        "restful apis",
    },
    "graphql": {
        "graphql",
        "graph ql",
    },
    "git": {
        "git",
    },
    "github": {
        "github",
        "git hub",
    },
    "ci/cd": {
        "ci/cd",
        "cicd",
        "continuous integration",
        "continuous delivery",
        "continuous deployment",
    },
}


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class KeywordMatch:
    """Result for a single keyword."""

    keyword: str

    matched: bool

    matched_text: str | None = None

    canonical_keyword: str | None = None

    match_type: str = "exact"

    occurrences: int = 0

    weight: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "keyword": self.keyword,
            "matched": self.matched,
            "matched_text": self.matched_text,
            "canonical_keyword": self.canonical_keyword,
            "match_type": self.match_type,
            "occurrences": self.occurrences,
            "weight": self.weight,
        }


@dataclass
class KeywordMatchResult:
    """Complete keyword matching result."""

    score: float

    matched_keywords: list[str] = field(
        default_factory=list
    )

    missing_keywords: list[str] = field(
        default_factory=list
    )

    matched_required: list[str] = field(
        default_factory=list
    )

    missing_required: list[str] = field(
        default_factory=list
    )

    matched_preferred: list[str] = field(
        default_factory=list
    )

    missing_preferred: list[str] = field(
        default_factory=list
    )

    details: list[KeywordMatch] = field(
        default_factory=list
    )

    required_score: float = 0.0

    preferred_score: float = 0.0

    keyword_count: int = 0

    matched_count: int = 0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "matched_keywords": self.matched_keywords,
            "missing_keywords": self.missing_keywords,
            "matched_required": self.matched_required,
            "missing_required": self.missing_required,
            "matched_preferred": self.matched_preferred,
            "missing_preferred": self.missing_preferred,
            "details": [
                detail.to_dict()
                for detail in self.details
            ],
            "required_score": self.required_score,
            "preferred_score": self.preferred_score,
            "keyword_count": self.keyword_count,
            "matched_count": self.matched_count,
            "metadata": self.metadata,
        }


# ============================================================================
# Text Normalization
# ============================================================================


def normalize_text(
    text: Any,
) -> str:
    """
    Normalize text for keyword matching.

    Converts:
        Python → python
        React.JS → react.js
        Multiple spaces → single space
    """

    if text is None:
        return ""

    text = str(text).lower()

    text = WHITESPACE_PATTERN.sub(
        " ",
        text,
    )

    return text.strip()


def normalize_keyword(
    keyword: Any,
) -> str:
    """Normalize a keyword."""

    return normalize_text(
        keyword
    )


def tokenize(
    text: str,
) -> list[str]:
    """Tokenize normalized text."""

    return TOKEN_PATTERN.findall(
        normalize_text(text)
    )


# ============================================================================
# Alias Handling
# ============================================================================


def build_alias_map() -> dict[str, str]:
    """
    Build alias → canonical keyword map.
    """

    alias_map: dict[str, str] = {}

    for canonical, aliases in KEYWORD_ALIASES.items():

        alias_map[
            normalize_keyword(canonical)
        ] = normalize_keyword(canonical)

        for alias in aliases:
            alias_map[
                normalize_keyword(alias)
            ] = normalize_keyword(
                canonical
            )

    return alias_map


ALIAS_MAP = build_alias_map()


def canonicalize_keyword(
    keyword: str,
) -> str:
    """
    Convert a keyword or alias into its canonical form.
    """

    normalized = normalize_keyword(
        keyword
    )

    return ALIAS_MAP.get(
        normalized,
        normalized,
    )


def get_keyword_aliases(
    keyword: str,
) -> set[str]:
    """
    Return all known aliases for a keyword.
    """

    canonical = canonicalize_keyword(
        keyword
    )

    aliases = KEYWORD_ALIASES.get(
        canonical,
        set(),
    )

    return {
        normalize_keyword(alias)
        for alias in aliases
    } | {canonical}


# ============================================================================
# Keyword Extraction
# ============================================================================


def extract_keywords_from_text(
    text: str,
    *,
    min_length: int = 2,
    exclude: Iterable[str] | None = None,
) -> list[str]:
    """
    Extract candidate keywords from text.

    This is a lightweight extractor. For production JD analysis,
    requirement_extractor.py should provide the authoritative
    keyword list.
    """

    excluded = {
        normalize_keyword(item)
        for item in (exclude or [])
    }

    tokens = tokenize(text)

    result: list[str] = []

    for token in tokens:

        if len(token) < min_length:
            continue

        if token in excluded:
            continue

        if token not in result:
            result.append(token)

    return result


def extract_phrases(
    text: str,
    min_words: int = 2,
    max_words: int = 4,
) -> list[str]:
    """
    Extract simple n-gram phrases.
    """

    tokens = tokenize(text)

    phrases: list[str] = []

    for size in range(
        min_words,
        max_words + 1,
    ):

        for index in range(
            0,
            len(tokens) - size + 1,
        ):

            phrase = " ".join(
                tokens[
                    index : index + size
                ]
            )

            if phrase not in phrases:
                phrases.append(phrase)

    return phrases


# ============================================================================
# Matching Helpers
# ============================================================================


def _contains_exact(
    text: str,
    keyword: str,
) -> tuple[bool, int]:
    """
    Match a keyword using word boundaries.
    """

    text = normalize_text(text)
    keyword = normalize_keyword(
        keyword
    )

    if not text or not keyword:
        return False, 0

    pattern = re.compile(
        rf"(?<!\w){re.escape(keyword)}(?!\w)",
        flags=re.IGNORECASE,
    )

    matches = pattern.findall(
        text
    )

    return (
        bool(matches),
        len(matches),
    )


def _contains_alias(
    text: str,
    keyword: str,
) -> tuple[bool, str | None, int]:
    """
    Check a keyword against known aliases.
    """

    aliases = get_keyword_aliases(
        keyword
    )

    for alias in sorted(
        aliases,
        key=len,
        reverse=True,
    ):

        matched, occurrences = (
            _contains_exact(
                text,
                alias,
            )
        )

        if matched:
            return (
                True,
                alias,
                occurrences,
            )

    return False, None, 0


def match_keyword(
    text: str,
    keyword: str,
    *,
    allow_aliases: bool = True,
    weight: float = 1.0,
) -> KeywordMatch:
    """
    Match one keyword against text.
    """

    normalized_keyword = normalize_keyword(
        keyword
    )

    if not normalized_keyword:
        return KeywordMatch(
            keyword="",
            matched=False,
            weight=weight,
        )

    # Exact match first.
    matched, occurrences = (
        _contains_exact(
            text,
            normalized_keyword,
        )
    )

    if matched:
        return KeywordMatch(
            keyword=keyword,
            matched=True,
            matched_text=normalized_keyword,
            canonical_keyword=canonicalize_keyword(
                normalized_keyword
            ),
            match_type="exact",
            occurrences=occurrences,
            weight=weight,
        )

    # Alias match.
    if allow_aliases:

        (
            matched,
            matched_text,
            occurrences,
        ) = _contains_alias(
            text,
            normalized_keyword,
        )

        if matched:
            return KeywordMatch(
                keyword=keyword,
                matched=True,
                matched_text=matched_text,
                canonical_keyword=canonicalize_keyword(
                    normalized_keyword
                ),
                match_type="alias",
                occurrences=occurrences,
                weight=weight,
            )

    return KeywordMatch(
        keyword=keyword,
        matched=False,
        canonical_keyword=canonicalize_keyword(
            normalized_keyword
        ),
        match_type="none",
        occurrences=0,
        weight=weight,
    )


# ============================================================================
# Keyword Scoring
# ============================================================================


def calculate_keyword_score(
    matched_keywords: Iterable[str],
    required_keywords: Iterable[str],
) -> float:
    """
    Calculate simple keyword coverage.

    Returns:
        0-100
    """

    required = {
        canonicalize_keyword(
            keyword
        )
        for keyword in required_keywords
        if normalize_keyword(keyword)
    }

    matched = {
        canonicalize_keyword(
            keyword
        )
        for keyword in matched_keywords
        if normalize_keyword(keyword)
    }

    if not required:
        return 100.0

    return round(
        (
            len(
                required & matched
            )
            / len(required)
        )
        * 100,
        2,
    )


def calculate_weighted_keyword_score(
    required_matches: Sequence[KeywordMatch],
    preferred_matches: Sequence[KeywordMatch],
    *,
    required_weight: float = DEFAULT_REQUIRED_WEIGHT,
    preferred_weight: float = DEFAULT_PREFERRED_WEIGHT,
) -> tuple[float, float, float]:
    """
    Calculate required/preferred/final keyword scores.
    """

    if required_weight < 0:
        raise ValueError(
            "required_weight cannot be negative."
        )

    if preferred_weight < 0:
        raise ValueError(
            "preferred_weight cannot be negative."
        )

    total_weight = (
        required_weight
        + preferred_weight
    )

    if total_weight <= 0:
        raise ValueError(
            "At least one keyword weight must be positive."
        )

    required_weight /= total_weight
    preferred_weight /= total_weight

    # Required score.
    required_total = sum(
        match.weight
        for match in required_matches
    )

    required_matched = sum(
        match.weight
        for match in required_matches
        if match.matched
    )

    if required_total > 0:
        required_score = (
            required_matched
            / required_total
            * 100
        )
    else:
        required_score = 100.0

    # Preferred score.
    preferred_total = sum(
        match.weight
        for match in preferred_matches
    )

    preferred_matched = sum(
        match.weight
        for match in preferred_matches
        if match.matched
    )

    if preferred_total > 0:
        preferred_score = (
            preferred_matched
            / preferred_total
            * 100
        )
    else:
        preferred_score = 100.0

    final_score = (
        required_score
        * required_weight
        + preferred_score
        * preferred_weight
    )

    return (
        round(required_score, 2),
        round(preferred_score, 2),
        round(final_score, 2),
    )


# ============================================================================
# Main Keyword Matcher
# ============================================================================


class KeywordMatcher:
    """
    Main keyword matching engine.

    Example:

        matcher = KeywordMatcher()

        result = matcher.match(
            resume_text=resume,
            job_text=job,
            keywords=[
                "Python",
                "FastAPI",
                "Docker",
                "AWS",
            ],
        )
    """

    def __init__(
        self,
        *,
        allow_aliases: bool = True,
        required_weight: float = DEFAULT_REQUIRED_WEIGHT,
        preferred_weight: float = DEFAULT_PREFERRED_WEIGHT,
    ) -> None:

        self.allow_aliases = (
            allow_aliases
        )

        self.required_weight = (
            required_weight
        )

        self.preferred_weight = (
            preferred_weight
        )

    # ----------------------------------------------------------------------
    # Single Keyword
    # ----------------------------------------------------------------------

    def match_keyword(
        self,
        text: str,
        keyword: str,
        weight: float = 1.0,
    ) -> KeywordMatch:
        """Match one keyword."""

        return match_keyword(
            text,
            keyword,
            allow_aliases=self.allow_aliases,
            weight=weight,
        )

    # ----------------------------------------------------------------------
    # Multiple Keywords
    # ----------------------------------------------------------------------

    def match_keywords(
        self,
        text: str,
        keywords: Iterable[str],
    ) -> list[KeywordMatch]:
        """Match multiple keywords."""

        unique_keywords: list[str] = []

        for keyword in keywords:

            normalized = normalize_keyword(
                keyword
            )

            if (
                normalized
                and normalized
                not in unique_keywords
            ):
                unique_keywords.append(
                    normalized
                )

        return [
            self.match_keyword(
                text,
                keyword,
            )
            for keyword in unique_keywords
        ]

    # ----------------------------------------------------------------------
    # Main Match
    # ----------------------------------------------------------------------

    def match(
        self,
        resume_text: str,
        job_text: str = "",
        keywords: Iterable[str] | None = None,
        required_keywords: Iterable[str] | None = None,
        preferred_keywords: Iterable[str] | None = None,
    ) -> dict[str, Any]:
        """
        Match resume against job keywords.

        `keywords` can be used as a single required keyword list.

        Alternatively:

            required_keywords=[...]
            preferred_keywords=[...]

        can be supplied separately.
        """

        # --------------------------------------------------------------
        # Determine keyword groups
        # --------------------------------------------------------------

        if keywords is not None:

            required = list(
                keywords
            )

        else:
            required = list(
                required_keywords or []
            )

        preferred = list(
            preferred_keywords or []
        )

        # Remove duplicates by canonical form.
        required = self._deduplicate(
            required
        )

        preferred = self._deduplicate(
            preferred
        )

        # Don't double-count preferred keywords
        # that are already required.
        required_canonical = {
            canonicalize_keyword(
                keyword
            )
            for keyword in required
        }

        preferred = [
            keyword
            for keyword in preferred
            if canonicalize_keyword(
                keyword
            )
            not in required_canonical
        ]

        # --------------------------------------------------------------
        # Match
        # --------------------------------------------------------------

        required_matches = (
            self.match_keywords(
                resume_text,
                required,
            )
        )

        preferred_matches = (
            self.match_keywords(
                resume_text,
                preferred,
            )
        )

        # --------------------------------------------------------------
        # Scores
        # --------------------------------------------------------------

        (
            required_score,
            preferred_score,
            final_score,
        ) = calculate_weighted_keyword_score(
            required_matches,
            preferred_matches,
            required_weight=self.required_weight,
            preferred_weight=self.preferred_weight,
        )

        # --------------------------------------------------------------
        # Lists
        # --------------------------------------------------------------

        matched_required = [
            match.keyword
            for match in required_matches
            if match.matched
        ]

        missing_required = [
            match.keyword
            for match in required_matches
            if not match.matched
        ]

        matched_preferred = [
            match.keyword
            for match in preferred_matches
            if match.matched
        ]

        missing_preferred = [
            match.keyword
            for match in preferred_matches
            if not match.matched
        ]

        matched_keywords = (
            matched_required
            + matched_preferred
        )

        missing_keywords = (
            missing_required
            + missing_preferred
        )

        details = (
            required_matches
            + preferred_matches
        )

        return KeywordMatchResult(
            score=final_score,
            matched_keywords=matched_keywords,
            missing_keywords=missing_keywords,
            matched_required=matched_required,
            missing_required=missing_required,
            matched_preferred=matched_preferred,
            missing_preferred=missing_preferred,
            details=details,
            required_score=required_score,
            preferred_score=preferred_score,
            keyword_count=len(details),
            matched_count=len(
                matched_keywords
            ),
            metadata={
                "allow_aliases": self.allow_aliases,
                "required_weight": (
                    self.required_weight
                ),
                "preferred_weight": (
                    self.preferred_weight
                ),
                "job_text_available": bool(
                    normalize_text(job_text)
                ),
            },
        ).to_dict()

    # ----------------------------------------------------------------------
    # Deduplication
    # ----------------------------------------------------------------------

    @staticmethod
    def _deduplicate(
        keywords: Iterable[str],
    ) -> list[str]:
        """Deduplicate keywords by canonical representation."""

        result: list[str] = []

        seen: set[str] = set()

        for keyword in keywords:

            normalized = normalize_keyword(
                keyword
            )

            if not normalized:
                continue

            canonical = canonicalize_keyword(
                normalized
            )

            if canonical in seen:
                continue

            seen.add(canonical)

            result.append(
                normalized
            )

        return result

    # ----------------------------------------------------------------------
    # Automatic Job Keyword Extraction
    # ----------------------------------------------------------------------

    def extract_job_keywords(
        self,
        job_text: str,
        *,
        exclude: Iterable[str] | None = None,
    ) -> list[str]:
        """
        Extract basic keywords from a job description.
        """

        return extract_keywords_from_text(
            job_text,
            exclude=exclude,
        )

    # ----------------------------------------------------------------------
    # Match Against Entire Job
    # ----------------------------------------------------------------------

    def match_job(
        self,
        resume_text: str,
        job_text: str,
        *,
        required_keywords: Iterable[str] | None = None,
        preferred_keywords: Iterable[str] | None = None,
    ) -> dict[str, Any]:
        """
        Match resume against a complete job description.

        If no keyword lists are provided, basic keywords are
        extracted from the job description.
        """

        required = list(
            required_keywords or []
        )

        preferred = list(
            preferred_keywords or []
        )

        if not required and not preferred:
            required = (
                self.extract_job_keywords(
                    job_text
                )
            )

        return self.match(
            resume_text=resume_text,
            job_text=job_text,
            required_keywords=required,
            preferred_keywords=preferred,
        )

    # ----------------------------------------------------------------------
    # Compare Keyword Sets
    # ----------------------------------------------------------------------

    def compare_keyword_sets(
        self,
        candidate_keywords: Iterable[str],
        job_keywords: Iterable[str],
    ) -> dict[str, Any]:
        """
        Compare normalized candidate and job keyword sets.
        """

        candidate = {
            canonicalize_keyword(
                keyword
            )
            for keyword in candidate_keywords
            if normalize_keyword(keyword)
        }

        job = {
            canonicalize_keyword(
                keyword
            )
            for keyword in job_keywords
            if normalize_keyword(keyword)
        }

        matched = sorted(
            candidate & job
        )

        missing = sorted(
            job - candidate
        )

        extra = sorted(
            candidate - job
        )

        score = (
            len(matched)
            / len(job)
            * 100
            if job
            else 100.0
        )

        return {
            "score": round(
                score,
                2,
            ),
            "matched": matched,
            "missing": missing,
            "extra": extra,
            "candidate_keyword_count": len(
                candidate
            ),
            "job_keyword_count": len(
                job
            ),
        }

    # ----------------------------------------------------------------------
    # Batch Matching
    # ----------------------------------------------------------------------

    def batch_match(
        self,
        resumes: Sequence[
            Mapping[str, Any]
        ],
        job_text: str,
        *,
        text_key: str = "resume_text",
        required_keywords: Iterable[str] | None = None,
        preferred_keywords: Iterable[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Match multiple resumes against one job.
        """

        results: list[dict[str, Any]] = []

        for resume in resumes:

            resume_text = str(
                resume.get(
                    text_key,
                    "",
                )
            )

            result = self.match_job(
                resume_text,
                job_text,
                required_keywords=required_keywords,
                preferred_keywords=preferred_keywords,
            )

            results.append(
                {
                    **dict(resume),
                    "keyword_match": result,
                }
            )

        return results

    # ----------------------------------------------------------------------
    # Ranking
    # ----------------------------------------------------------------------

    def rank_resumes(
        self,
        resumes: Sequence[
            Mapping[str, Any]
        ],
        job_text: str,
        *,
        text_key: str = "resume_text",
        required_keywords: Iterable[str] | None = None,
        preferred_keywords: Iterable[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Rank resumes by keyword score.
        """

        results = self.batch_match(
            resumes,
            job_text,
            text_key=text_key,
            required_keywords=required_keywords,
            preferred_keywords=preferred_keywords,
        )

        for item in results:

            item["keyword_score"] = (
                item[
                    "keyword_match"
                ]["score"]
            )

        results.sort(
            key=lambda item: item[
                "keyword_score"
            ],
            reverse=True,
        )

        return results


# ============================================================================
# Functional API
# ============================================================================


_default_matcher: KeywordMatcher | None = None


def get_default_matcher() -> KeywordMatcher:
    """Return a lazily-created default matcher."""

    global _default_matcher

    if _default_matcher is None:
        _default_matcher = KeywordMatcher()

    return _default_matcher


def keyword_match(
    resume_text: str,
    job_text: str = "",
    keywords: Iterable[str] | None = None,
    required_keywords: Iterable[str] | None = None,
    preferred_keywords: Iterable[str] | None = None,
) -> dict[str, Any]:
    """
    Functional API for keyword matching.
    """

    return get_default_matcher().match(
        resume_text=resume_text,
        job_text=job_text,
        keywords=keywords,
        required_keywords=required_keywords,
        preferred_keywords=preferred_keywords,
    )


def keyword_score(
    resume_text: str,
    keywords: Iterable[str],
) -> float:
    """
    Return only the keyword score.
    """

    result = get_default_matcher().match(
        resume_text=resume_text,
        keywords=keywords,
    )

    return float(
        result["score"]
    )


def extract_keywords(
    text: str,
) -> list[str]:
    """
    Functional keyword extraction API.
    """

    return extract_keywords_from_text(
        text
    )


def canonical_keyword(
    keyword: str,
) -> str:
    """
    Functional canonicalization API.
    """

    return canonicalize_keyword(
        keyword
    )


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "KeywordMatch",
    "KeywordMatchResult",
    "KeywordMatcher",
    "KEYWORD_ALIASES",
    "normalize_text",
    "normalize_keyword",
    "tokenize",
    "canonicalize_keyword",
    "get_keyword_aliases",
    "extract_keywords_from_text",
    "extract_phrases",
    "match_keyword",
    "calculate_keyword_score",
    "calculate_weighted_keyword_score",
    "keyword_match",
    "keyword_score",
    "extract_keywords",
    "canonical_keyword",
    "get_default_matcher",
]12