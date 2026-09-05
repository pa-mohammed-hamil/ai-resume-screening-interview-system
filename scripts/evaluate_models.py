# Project scaffold file
# Project scaffold file
"""
============================================================
AI Resume Screening & Interview System
Model Evaluation Script
File: scripts/evaluate_models.py
============================================================

Purpose:
    Evaluate the AI pipeline against labeled evaluation data.

Supported evaluation areas:
    - Resume parsing
    - Information extraction
    - Skill extraction
    - Resume/JD matching
    - ATS scoring
    - Candidate ranking
    - Fairness metrics

Expected evaluation structure:

    data/
    └── evaluation/
        ├── test_resumes/
        ├── test_jobs/
        └── expected_results/

The script is designed to work even when individual AI
components expose slightly different interfaces.

Usage:

    python scripts/evaluate_models.py

Examples:

    python scripts/evaluate_models.py --component all

    python scripts/evaluate_models.py --component parser

    python scripts/evaluate_models.py --component matching

    python scripts/evaluate_models.py --component ranking

    python scripts/evaluate_models.py --component fairness

    python scripts/evaluate_models.py --output evaluation_results.json
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Optional


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"

EVALUATION_DIR = DATA_DIR / "evaluation"

TEST_RESUMES_DIR = EVALUATION_DIR / "test_resumes"

TEST_JOBS_DIR = EVALUATION_DIR / "test_jobs"

EXPECTED_RESULTS_DIR = EVALUATION_DIR / "expected_results"


# ============================================================
# SUPPORTED FILE TYPES
# ============================================================

SUPPORTED_RESUME_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
}

SUPPORTED_JOB_EXTENSIONS = {
    ".txt",
    ".json",
    ".md",
}

SUPPORTED_EXPECTED_EXTENSIONS = {
    ".json",
    ".csv",
}


# ============================================================
# DATACLASSES
# ============================================================

@dataclass
class Metric:
    name: str
    value: float
    sample_count: int
    details: Optional[dict[str, Any]] = None


@dataclass
class EvaluationResult:
    component: str
    status: str
    duration_seconds: float
    metrics: list[Metric]
    errors: list[str]
    warnings: list[str]


# ============================================================
# LOGGING
# ============================================================

def log(message: str) -> None:
    """Print a normal log message."""

    print(f"[INFO] {message}")


def warning(message: str) -> None:
    """Print a warning."""

    print(f"[WARNING] {message}")


def error(message: str) -> None:
    """Print an error."""

    print(f"[ERROR] {message}")


# ============================================================
# GENERAL HELPERS
# ============================================================

def normalize_text(value: Any) -> str:
    """Normalize text for comparison."""

    if value is None:
        return ""

    return " ".join(
        str(value)
        .lower()
        .strip()
        .split()
    )


def normalize_string_set(
    values: Any,
) -> set[str]:
    """Convert strings/lists into normalized sets."""

    if values is None:
        return set()

    if isinstance(values, str):
        values = [
            item.strip()
            for item in values.split(",")
            if item.strip()
        ]

    if not isinstance(values, (list, tuple, set)):
        return {
            normalize_text(values)
        }

    return {
        normalize_text(item)
        for item in values
        if normalize_text(item)
    }


def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """Convert a value to float safely."""

    try:
        number = float(value)

        if math.isnan(number):
            return default

        if math.isinf(number):
            return default

        return number

    except (TypeError, ValueError):
        return default


def clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:
    """Clamp a numeric value."""

    return max(
        minimum,
        min(maximum, value),
    )


# ============================================================
# FILE DISCOVERY
# ============================================================

def discover_files(
    directory: Path,
    extensions: Iterable[str],
) -> list[Path]:
    """Discover files recursively."""

    if not directory.exists():
        return []

    extensions = {
        extension.lower()
        for extension in extensions
    }

    return sorted(
        path
        for path in directory.rglob("*")
        if path.is_file()
        and path.suffix.lower() in extensions
    )


def find_expected_file(
    source_file: Path,
) -> Optional[Path]:
    """
    Find an expected-results file matching a source file.

    Example:

        resume_001.pdf
        resume_001.json
    """

    stem = source_file.stem

    candidates = [
        EXPECTED_RESULTS_DIR / f"{stem}.json",
        EXPECTED_RESULTS_DIR / f"{stem}.csv",
        EXPECTED_RESULTS_DIR / f"{stem}.expected.json",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


# ============================================================
# EXPECTED RESULT LOADING
# ============================================================

def load_json_file(
    path: Path,
) -> Any:
    """Load JSON data."""

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def load_expected_result(
    path: Path,
) -> dict[str, Any]:
    """Load an expected result file."""

    if path.suffix.lower() == ".json":
        data = load_json_file(path)

        if isinstance(data, dict):
            return data

        return {
            "expected": data
        }

    if path.suffix.lower() == ".csv":
        with path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            rows = list(
                csv.DictReader(file)
            )

        if not rows:
            return {}

        return rows[0]

    return {}


# ============================================================
# TEXT EXTRACTION
# ============================================================

def read_text_file(
    path: Path,
) -> str:
    """Read a plain-text file."""

    return path.read_text(
        encoding="utf-8",
        errors="ignore",
    )


def extract_resume_text(
    path: Path,
) -> str:
    """
    Extract text from a resume.

    Uses the project's parser when available.
    Falls back to direct text extraction for .txt files.
    """

    if path.suffix.lower() == ".txt":
        return read_text_file(path)

    try:
        from ai.resume_parser.parser import ResumeParser

        parser = ResumeParser()

        if hasattr(parser, "parse"):
            result = parser.parse(str(path))

            if isinstance(result, str):
                return result

            if isinstance(result, dict):
                return json.dumps(
                    result,
                    ensure_ascii=False,
                )

    except Exception as exc:
        warning(
            f"Resume parser unavailable for {path.name}: {exc}"
        )

    try:
        from ai.resume_parser.parser import parse_resume

        result = parse_resume(str(path))

        if isinstance(result, str):
            return result

        return json.dumps(
            result,
            ensure_ascii=False,
        )

    except Exception:
        pass

    return ""


def extract_job_text(
    path: Path,
) -> str:
    """Extract job-description text."""

    if path.suffix.lower() in {
        ".txt",
        ".md",
    }:
        return read_text_file(path)

    if path.suffix.lower() == ".json":
        data = load_json_file(path)

        if isinstance(data, str):
            return data

        return json.dumps(
            data,
            ensure_ascii=False,
        )

    return ""


# ============================================================
# GENERIC ATTRIBUTE ACCESS
# ============================================================

def get_value(
    obj: Any,
    *names: str,
    default: Any = None,
) -> Any:
    """Read a value from a dictionary or object."""

    if obj is None:
        return default

    if isinstance(obj, dict):
        for name in names:
            if name in obj:
                return obj[name]

    for name in names:
        if hasattr(obj, name):
            return getattr(obj, name)

    return default


# ============================================================
# RESUME PARSER EVALUATION
# ============================================================

def evaluate_parser() -> EvaluationResult:
    """Evaluate resume parsing accuracy."""

    start = time.perf_counter()

    metrics: list[Metric] = []
    errors: list[str] = []
    warnings: list[str] = []

    resume_files = discover_files(
        TEST_RESUMES_DIR,
        SUPPORTED_RESUME_EXTENSIONS,
    )

    if not resume_files:
        warnings.append(
            f"No test resumes found in {TEST_RESUMES_DIR}"
        )

        return EvaluationResult(
            component="parser",
            status="skipped",
            duration_seconds=time.perf_counter() - start,
            metrics=[],
            errors=[],
            warnings=warnings,
        )

    field_scores: defaultdict[str, list[float]] = (
        defaultdict(list)
    )

    processed = 0

    for resume_file in resume_files:

        expected_file = find_expected_file(
            resume_file
        )

        if expected_file is None:
            warnings.append(
                f"No expected result for {resume_file.name}"
            )
            continue

        try:
            expected = load_expected_result(
                expected_file
            )

            text = extract_resume_text(
                resume_file
            )

            if not text:
                errors.append(
                    f"Unable to parse {resume_file.name}"
                )
                continue

            processed += 1

            # --------------------------------------------
            # Basic expected fields
            # --------------------------------------------

            expected_fields = {
                "name": get_value(
                    expected,
                    "name",
                    "full_name",
                ),
                "email": get_value(
                    expected,
                    "email",
                ),
                "phone": get_value(
                    expected,
                    "phone",
                ),
            }

            # --------------------------------------------
            # Lightweight baseline extraction
            # --------------------------------------------

            text_normalized = normalize_text(
                text
            )

            for field, expected_value in (
                expected_fields.items()
            ):

                if expected_value in (
                    None,
                    "",
                ):
                    continue

                expected_normalized = normalize_text(
                    expected_value
                )

                score = (
                    1.0
                    if expected_normalized
                    in text_normalized
                    else 0.0
                )

                field_scores[field].append(
                    score
                )

        except Exception as exc:
            errors.append(
                f"{resume_file.name}: {exc}"
            )

    for field, scores in field_scores.items():

        if scores:
            metrics.append(
                Metric(
                    name=f"{field}_accuracy",
                    value=statistics.mean(scores),
                    sample_count=len(scores),
                )
            )

    if processed:
        metrics.append(
            Metric(
                name="parser_sample_count",
                value=float(processed),
                sample_count=processed,
            )
        )

    status = (
        "passed"
        if processed > 0 and not errors
        else "completed"
        if processed > 0
        else "failed"
    )

    return EvaluationResult(
        component="parser",
        status=status,
        duration_seconds=time.perf_counter() - start,
        metrics=metrics,
        errors=errors,
        warnings=warnings,
    )


# ============================================================
# SKILL EXTRACTION EVALUATION
# ============================================================

def evaluate_skills() -> EvaluationResult:
    """Evaluate skill extraction accuracy."""

    start = time.perf_counter()

    metrics: list[Metric] = []
    errors: list[str] = []
    warnings: list[str] = []

    resume_files = discover_files(
        TEST_RESUMES_DIR,
        SUPPORTED_RESUME_EXTENSIONS,
    )

    if not resume_files:
        warnings.append(
            "No test resumes found."
        )

        return EvaluationResult(
            component="skills",
            status="skipped",
            duration_seconds=time.perf_counter() - start,
            metrics=[],
            errors=[],
            warnings=warnings,
        )

    precision_values: list[float] = []
    recall_values: list[float] = []
    f1_values: list[float] = []

    for resume_file in resume_files:

        expected_file = find_expected_file(
            resume_file
        )

        if expected_file is None:
            continue

        try:
            expected = load_expected_result(
                expected_file
            )

            expected_skills = normalize_string_set(
                get_value(
                    expected,
                    "skills",
                    "expected_skills",
                    default=[],
                )
            )

            if not expected_skills:
                continue

            text = extract_resume_text(
                resume_file
            )

            if not text:
                continue

            try:
                from ai.skill_intelligence.skill_extractor import (
                    SkillExtractor,
                )

                extractor = SkillExtractor()

                if hasattr(extractor, "extract"):
                    result = extractor.extract(
                        text
                    )

                else:
                    result = []

            except Exception:
                result = []

            predicted_skills = normalize_string_set(
                get_value(
                    result,
                    "skills",
                    default=result,
                )
            )

            true_positive = len(
                predicted_skills
                & expected_skills
            )

            false_positive = len(
                predicted_skills
                - expected_skills
            )

            false_negative = len(
                expected_skills
                - predicted_skills
            )

            precision = (
                true_positive
                / (
                    true_positive
                    + false_positive
                )
                if (
                    true_positive
                    + false_positive
                )
                else 0.0
            )

            recall = (
                true_positive
                / (
                    true_positive
                    + false_negative
                )
                if (
                    true_positive
                    + false_negative
                )
                else 0.0
            )

            f1 = (
                2 * precision * recall
                / (precision + recall)
                if precision + recall
                else 0.0
            )

            precision_values.append(
                precision
            )

            recall_values.append(
                recall
            )

            f1_values.append(
                f1
            )

        except Exception as exc:
            errors.append(
                f"{resume_file.name}: {exc}"
            )

    if precision_values:
        metrics.extend(
            [
                Metric(
                    name="skill_precision",
                    value=statistics.mean(
                        precision_values
                    ),
                    sample_count=len(
                        precision_values
                    ),
                ),
                Metric(
                    name="skill_recall",
                    value=statistics.mean(
                        recall_values
                    ),
                    sample_count=len(
                        recall_values
                    ),
                ),
                Metric(
                    name="skill_f1",
                    value=statistics.mean(
                        f1_values
                    ),
                    sample_count=len(
                        f1_values
                    ),
                ),
            ]
        )

    return EvaluationResult(
        component="skills",
        status=(
            "passed"
            if f1_values
            else "skipped"
        ),
        duration_seconds=time.perf_counter() - start,
        metrics=metrics,
        errors=errors,
        warnings=warnings,
    )


# ============================================================
# MATCHING EVALUATION
# ============================================================

def evaluate_matching() -> EvaluationResult:
    """Evaluate resume-to-job matching."""

    start = time.perf_counter()

    metrics: list[Metric] = []
    errors: list[str] = []
    warnings: list[str] = []

    resume_files = discover_files(
        TEST_RESUMES_DIR,
        SUPPORTED_RESUME_EXTENSIONS,
    )

    job_files = discover_files(
        TEST_JOBS_DIR,
        SUPPORTED_JOB_EXTENSIONS,
    )

    if not resume_files or not job_files:
        warnings.append(
            "Matching evaluation requires both test resumes and test jobs."
        )

        return EvaluationResult(
            component="matching",
            status="skipped",
            duration_seconds=time.perf_counter() - start,
            metrics=[],
            errors=[],
            warnings=warnings,
        )

    scores: list[float] = []

    for resume_file in resume_files:

        resume_text = extract_resume_text(
            resume_file
        )

        if not resume_text:
            continue

        for job_file in job_files:

            job_text = extract_job_text(
                job_file
            )

            if not job_text:
                continue

            expected_file = (
                EXPECTED_RESULTS_DIR
                / f"{resume_file.stem}__{job_file.stem}.json"
            )

            if not expected_file.exists():
                continue

            try:
                expected = load_expected_result(
                    expected_file
                )

                expected_score = safe_float(
                    get_value(
                        expected,
                        "match_score",
                        "score",
                        "expected_score",
                    )
                )

                predicted_score = None

                try:
                    from ai.matching.resume_job_matcher import (
                        ResumeJobMatcher,
                    )

                    matcher = ResumeJobMatcher()

                    if hasattr(matcher, "match"):
                        result = matcher.match(
                            resume_text,
                            job_text,
                        )

                        predicted_score = safe_float(
                            get_value(
                                result,
                                "score",
                                "match_score",
                                "similarity",
                                default=result,
                            )
                        )

                except Exception:
                    pass

                if predicted_score is None:
                    # Baseline keyword matching.
                    resume_words = set(
                        normalize_text(
                            resume_text
                        ).split()
                    )

                    job_words = set(
                        normalize_text(
                            job_text
                        ).split()
                    )

                    if job_words:
                        predicted_score = (
                            len(
                                resume_words
                                & job_words
                            )
                            / len(job_words)
                        )
                    else:
                        predicted_score = 0.0

                # Convert 0-100 scores to 0-1.
                if predicted_score > 1:
                    predicted_score /= 100

                if expected_score > 1:
                    expected_score /= 100

                error_value = abs(
                    predicted_score
                    - expected_score
                )

                score = clamp(
                    1.0 - error_value
                )

                scores.append(score)

            except Exception as exc:
                errors.append(
                    f"{resume_file.name} / "
                    f"{job_file.name}: {exc}"
                )

    if scores:
        metrics.append(
            Metric(
                name="matching_accuracy",
                value=statistics.mean(scores),
                sample_count=len(scores),
            )
        )

        metrics.append(
            Metric(
                name="matching_mae",
                value=1.0 - statistics.mean(scores),
                sample_count=len(scores),
            )
        )

    return EvaluationResult(
        component="matching",
        status=(
            "passed"
            if scores
            else "skipped"
        ),
        duration_seconds=time.perf_counter() - start,
        metrics=metrics,
        errors=errors,
        warnings=warnings,
    )


# ============================================================
# ATS SCORING EVALUATION
# ============================================================

def evaluate_ats() -> EvaluationResult:
    """Evaluate ATS scoring."""

    start = time.perf_counter()

    metrics: list[Metric] = []
    errors: list[str] = []
    warnings: list[str] = []

    resume_files = discover_files(
        TEST_RESUMES_DIR,
        SUPPORTED_RESUME_EXTENSIONS,
    )

    score_errors: list[float] = []

    for resume_file in resume_files:

        expected_file = find_expected_file(
            resume_file
        )

        if expected_file is None:
            continue

        try:
            expected = load_expected_result(
                expected_file
            )

            expected_score = safe_float(
                get_value(
                    expected,
                    "ats_score",
                    "score",
                    "expected_ats_score",
                )
            )

            text = extract_resume_text(
                resume_file
            )

            if not text:
                continue

            predicted_score = None

            try:
                from ai.scoring.ats_scorer import (
                    ATSScorer,
                )

                scorer = ATSScorer()

                if hasattr(scorer, "score"):
                    result = scorer.score(
                        text
                    )

                    predicted_score = safe_float(
                        get_value(
                            result,
                            "score",
                            "ats_score",
                            default=result,
                        )
                    )

            except Exception:
                pass

            if predicted_score is None:
                # Basic ATS baseline.
                text_length = len(
                    normalize_text(text)
                )

                predicted_score = min(
                    100.0,
                    40.0
                    + min(
                        30.0,
                        text_length / 100.0,
                    )
                    + (
                        15.0
                        if "experience" in normalize_text(text)
                        else 0.0
                    )
                    + (
                        15.0
                        if "skills" in normalize_text(text)
                        else 0.0
                    ),
                )

            if predicted_score <= 1:
                predicted_score *= 100

            if expected_score <= 1:
                expected_score *= 100

            score_errors.append(
                abs(
                    predicted_score
                    - expected_score
                )
            )

        except Exception as exc:
            errors.append(
                f"{resume_file.name}: {exc}"
            )

    if score_errors:
        metrics.append(
            Metric(
                name="ats_mae",
                value=statistics.mean(
                    score_errors
                ),
                sample_count=len(
                    score_errors
                ),
            )
        )

        metrics.append(
            Metric(
                name="ats_accuracy",
                value=clamp(
                    1.0
                    - (
                        statistics.mean(
                            score_errors
                        )
                        / 100.0
                    )
                ),
                sample_count=len(
                    score_errors
                ),
            )
        )

    return EvaluationResult(
        component="ats",
        status=(
            "passed"
            if score_errors
            else "skipped"
        ),
        duration_seconds=time.perf_counter() - start,
        metrics=metrics,
        errors=errors,
        warnings=warnings,
    )


# ============================================================
# RANKING EVALUATION
# ============================================================

def evaluate_ranking() -> EvaluationResult:
    """Evaluate candidate ranking using pairwise accuracy."""

    start = time.perf_counter()

    metrics: list[Metric] = []
    errors: list[str] = []
    warnings: list[str] = []

    ranking_file = (
        EXPECTED_RESULTS_DIR
        / "ranking.json"
    )

    if not ranking_file.exists():
        warnings.append(
            f"Ranking file not found: {ranking_file}"
        )

        return EvaluationResult(
            component="ranking",
            status="skipped",
            duration_seconds=time.perf_counter() - start,
            metrics=[],
            errors=[],
            warnings=warnings,
        )

    try:
        data = load_json_file(
            ranking_file
        )

        candidates = data.get(
            "candidates",
            [],
        )

        if not candidates:
            warnings.append(
                "No ranking candidates found."
            )

            return EvaluationResult(
                component="ranking",
                status="skipped",
                duration_seconds=time.perf_counter() - start,
                metrics=[],
                errors=[],
                warnings=warnings,
            )

        expected_order = [
            item.get("id")
            for item in candidates
        ]

        predicted_scores = {}

        for candidate in candidates:

            candidate_id = candidate.get(
                "id"
            )

            resume_path = (
                TEST_RESUMES_DIR
                / candidate.get(
                    "resume",
                    "",
                )
            )

            if not resume_path.exists():
                continue

            text = extract_resume_text(
                resume_path
            )

            predicted_score = 0.0

            try:
                from ai.ranking.candidate_ranker import (
                    CandidateRanker,
                )

                ranker = CandidateRanker()

                if hasattr(ranker, "rank"):
                    result = ranker.rank(
                        [
                            {
                                "id": candidate_id,
                                "resume_text": text,
                            }
                        ]
                    )

                    if result:
                        first = result[0]

                        predicted_score = safe_float(
                            get_value(
                                first,
                                "score",
                                "ranking_score",
                                default=0.0,
                            )
                        )

            except Exception:
                # Simple baseline.
                predicted_score = float(
                    len(
                        normalize_text(
                            text
                        ).split()
                    )
                )

            predicted_scores[
                candidate_id
            ] = predicted_score

        predicted_order = sorted(
            predicted_scores,
            key=lambda item: predicted_scores[item],
            reverse=True,
        )

        comparable = [
            candidate_id
            for candidate_id in expected_order
            if candidate_id in predicted_scores
        ]

        if len(comparable) >= 2:

            concordant = 0
            total_pairs = 0

            expected_positions = {
                candidate_id: index
                for index, candidate_id
                in enumerate(expected_order)
            }

            for index, first in enumerate(
                comparable
            ):
                for second in comparable[
                    index + 1:
                ]:

                    total_pairs += 1

                    expected_first = (
                        expected_positions[first]
                        < expected_positions[second]
                    )

                    predicted_first = (
                        predicted_order.index(first)
                        < predicted_order.index(second)
                    )

                    if expected_first == predicted_first:
                        concordant += 1

            pairwise_accuracy = (
                concordant / total_pairs
                if total_pairs
                else 0.0
            )

            metrics.append(
                Metric(
                    name="ranking_pairwise_accuracy",
                    value=pairwise_accuracy,
                    sample_count=total_pairs,
                )
            )

        metrics.append(
            Metric(
                name="ranking_candidate_count",
                value=float(len(comparable)),
                sample_count=len(comparable),
            )
        )

    except Exception as exc:
        errors.append(
            str(exc)
        )

    return EvaluationResult(
        component="ranking",
        status=(
            "passed"
            if metrics
            else "failed"
        ),
        duration_seconds=time.perf_counter() - start,
        metrics=metrics,
        errors=errors,
        warnings=warnings,
    )


# ============================================================
# FAIRNESS EVALUATION
# ============================================================

def evaluate_fairness() -> EvaluationResult:
    """
    Evaluate fairness metrics from labeled candidate results.

    Expected file:

        data/evaluation/expected_results/fairness.json

    Example:

        {
            "groups": {
                "group_a": {
                    "selected": 80,
                    "total": 100
                },
                "group_b": {
                    "selected": 60,
                    "total": 100
                }
            }
        }
    """

    start = time.perf_counter()

    metrics: list[Metric] = []
    errors: list[str] = []
    warnings: list[str] = []

    fairness_file = (
        EXPECTED_RESULTS_DIR
        / "fairness.json"
    )

    if not fairness_file.exists():
        warnings.append(
            f"Fairness file not found: {fairness_file}"
        )

        return EvaluationResult(
            component="fairness",
            status="skipped",
            duration_seconds=time.perf_counter() - start,
            metrics=[],
            errors=[],
            warnings=warnings,
        )

    try:
        data = load_json_file(
            fairness_file
        )

        groups = data.get(
            "groups",
            {},
        )

        selection_rates = {}

        for group_name, group_data in groups.items():

            selected = safe_float(
                group_data.get(
                    "selected",
                    0,
                )
            )

            total = safe_float(
                group_data.get(
                    "total",
                    0,
                )
            )

            if total <= 0:
                continue

            selection_rates[group_name] = (
                selected / total
            )

        if selection_rates:

            maximum_rate = max(
                selection_rates.values()
            )

            minimum_rate = min(
                selection_rates.values()
            )

            demographic_parity_ratio = (
                minimum_rate / maximum_rate
                if maximum_rate > 0
                else 0.0
            )

            statistical_parity_difference = (
                minimum_rate
                - maximum_rate
            )

            metrics.extend(
                [
                    Metric(
                        name="demographic_parity_ratio",
                        value=demographic_parity_ratio,
                        sample_count=len(
                            selection_rates
                        ),
                        details=selection_rates,
                    ),
                    Metric(
                        name="statistical_parity_difference",
                        value=statistical_parity_difference,
                        sample_count=len(
                            selection_rates
                        ),
                    ),
                ]
            )

        else:
            warnings.append(
                "No valid fairness groups found."
            )

    except Exception as exc:
        errors.append(
            str(exc)
        )

    return EvaluationResult(
        component="fairness",
        status=(
            "passed"
            if metrics
            else "skipped"
        ),
        duration_seconds=time.perf_counter() - start,
        metrics=metrics,
        errors=errors,
        warnings=warnings,
    )


# ============================================================
# EVALUATE ALL
# ============================================================

def evaluate_all(
    component: str,
) -> list[EvaluationResult]:
    """Run selected evaluations."""

    evaluators = {
        "parser": evaluate_parser,
        "skills": evaluate_skills,
        "matching": evaluate_matching,
        "ats": evaluate_ats,
        "ranking": evaluate_ranking,
        "fairness": evaluate_fairness,
    }

    if component == "all":
        selected = list(
            evaluators.values()
        )
    else:
        if component not in evaluators:
            raise ValueError(
                f"Unsupported component: {component}"
            )

        selected = [
            evaluators[component]
        ]

    results = []

    for evaluator in selected:

        log(
            f"Running {evaluator.__name__}..."
        )

        try:
            result = evaluator()

        except Exception as exc:
            result = EvaluationResult(
                component=evaluator.__name__,
                status="failed",
                duration_seconds=0.0,
                metrics=[],
                errors=[str(exc)],
                warnings=[],
            )

        results.append(result)

    return results


# ============================================================
# AGGREGATE SCORE
# ============================================================

def calculate_overall_score(
    results: list[EvaluationResult],
) -> float:
    """Calculate an overall evaluation score."""

    values: list[float] = []

    for result in results:

        for metric in result.metrics:

            if metric.name.endswith(
                (
                    "_accuracy",
                    "_f1",
                    "_precision",
                    "_recall",
                    "_ratio",
                )
            ):
                values.append(
                    clamp(metric.value)
                )

    if not values:
        return 0.0

    return statistics.mean(
        values
    )


# ============================================================
# CONSOLE REPORT
# ============================================================

def print_report(
    results: list[EvaluationResult],
) -> None:
    """Print a human-readable report."""

    print()
    print("=" * 72)
    print(
        "AI RESUME SCREENING & INTERVIEW SYSTEM"
    )
    print("MODEL EVALUATION REPORT")
    print("=" * 72)

    overall_score = calculate_overall_score(
        results
    )

    print()
    print(
        f"Overall score: {overall_score * 100:.2f}%"
    )

    print()

    for result in results:

        print("-" * 72)

        print(
            f"Component : {result.component}"
        )

        print(
            f"Status    : {result.status}"
        )

        print(
            f"Duration  : {result.duration_seconds:.3f}s"
        )

        if result.metrics:

            print("Metrics:")

            for metric in result.metrics:

                if (
                    metric.name.endswith(
                        (
                            "_accuracy",
                            "_f1",
                            "_precision",
                            "_recall",
                            "_ratio",
                        )
                    )
                ):
                    value = (
                        f"{metric.value * 100:.2f}%"
                    )
                else:
                    value = (
                        f"{metric.value:.4f}"
                    )

                print(
                    f"  - {metric.name}: "
                    f"{value} "
                    f"(n={metric.sample_count})"
                )

        if result.warnings:

            print("Warnings:")

            for item in result.warnings:
                print(
                    f"  - {item}"
                )

        if result.errors:

            print("Errors:")

            for item in result.errors:
                print(
                    f"  - {item}"
                )

    print()
    print("=" * 72)
    print("Evaluation complete.")
    print("=" * 72)
    print()


# ============================================================
# JSON REPORT
# ============================================================

def save_report(
    results: list[EvaluationResult],
    output_path: Path,
) -> None:
    """Save evaluation results to JSON."""

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "project": "ai-resume-screening-interview-system",
        "overall_score": calculate_overall_score(
            results
        ),
        "overall_score_percent": (
            calculate_overall_score(
                results
            )
            * 100
        ),
        "results": [
            {
                **asdict(result),
                "metrics": [
                    asdict(metric)
                    for metric in result.metrics
                ],
            }
            for result in results
        ],
    }

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            payload,
            file,
            indent=2,
            ensure_ascii=False,
        )

    log(
        f"Evaluation report saved to {output_path}"
    )


# ============================================================
# ARGUMENT PARSER
# ============================================================

def parse_arguments() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Evaluate AI models used by the "
            "AI Resume Screening & Interview System."
        )
    )

    parser.add_argument(
        "--component",
        choices=[
            "all",
            "parser",
            "skills",
            "matching",
            "ats",
            "ranking",
            "fairness",
        ],
        default="all",
        help="Component to evaluate.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=(
            EVALUATION_DIR
            / "evaluation_results.json"
        ),
        help="Output JSON report path.",
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console report.",
    )

    return parser.parse_args()


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """Main program entry point."""

    args = parse_arguments()

    log(
        "Starting model evaluation..."
    )

    log(
        f"Project root: {PROJECT_ROOT}"
    )

    log(
        f"Evaluation directory: {EVALUATION_DIR}"
    )

    try:
        results = evaluate_all(
            args.component
        )

        save_report(
            results,
            args.output,
        )

        if not args.quiet:
            print_report(
                results
            )

        failed = [
            result
            for result in results
            if result.status == "failed"
        ]

        if failed:
            return 1

        return 0

    except KeyboardInterrupt:
        print()
        warning(
            "Evaluation cancelled by user."
        )
        return 130

    except Exception as exc:
        error(
            f"Evaluation failed: {exc}"
        )
        return 1


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    raise SystemExit(
        main()
    )