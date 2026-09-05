"""
============================================================
AI Resume Screening & Interview System
Candidate Ranking Evaluation
File: scripts/evaluate_ranking.py
============================================================

Purpose:
    Evaluate the candidate ranking model against a labeled
    ranking dataset.

Expected evaluation file:

    data/evaluation/expected_results/ranking.json

Example:

    {
        "candidates": [
            {
                "id": "candidate_001",
                "resume": "resume_001.pdf",
                "relevance": 5
            },
            {
                "id": "candidate_002",
                "resume": "resume_002.pdf",
                "relevance": 3
            },
            {
                "id": "candidate_003",
                "resume": "resume_003.pdf",
                "relevance": 1
            }
        ]
    }

The script supports:
    - CandidateRanker from ai/ranking/candidate_ranker.py
    - Expected ranking labels
    - Pairwise accuracy
    - Spearman rank correlation
    - NDCG@K
    - Precision@K
    - Recall@K
    - Mean absolute rank error
    - Ranking report export

Usage:

    python scripts/evaluate_ranking.py

    python scripts/evaluate_ranking.py --k 5

    python scripts/evaluate_ranking.py \
        --input data/evaluation/expected_results/ranking.json

    python scripts/evaluate_ranking.py \
        --output data/evaluation/ranking_results.json
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from pathlib import Path
from typing import Any


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"

EVALUATION_DIR = DATA_DIR / "evaluation"

TEST_RESUMES_DIR = EVALUATION_DIR / "test_resumes"

DEFAULT_INPUT = (
    EVALUATION_DIR
    / "expected_results"
    / "ranking.json"
)

DEFAULT_OUTPUT = (
    EVALUATION_DIR
    / "ranking_results.json"
)


# ============================================================
# LOGGING
# ============================================================

def log(message: str) -> None:
    """Print an informational message."""

    print(f"[INFO] {message}")


def warning(message: str) -> None:
    """Print a warning message."""

    print(f"[WARNING] {message}")


def error(message: str) -> None:
    """Print an error message."""

    print(f"[ERROR] {message}")


# ============================================================
# GENERAL HELPERS
# ============================================================

def normalize_text(value: Any) -> str:
    """Normalize arbitrary values into text."""

    if value is None:
        return ""

    return " ".join(
        str(value)
        .lower()
        .strip()
        .split()
    )


def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """Safely convert a value to float."""

    try:
        number = float(value)

        if math.isnan(number):
            return default

        if math.isinf(number):
            return default

        return number

    except (TypeError, ValueError):
        return default


def get_value(
    obj: Any,
    *names: str,
    default: Any = None,
) -> Any:
    """Read a value from a dictionary or Python object."""

    if obj is None:
        return default

    if isinstance(obj, dict):

        for name in names:

            if name in obj:
                return obj[name]

    for name in names:

        if hasattr(obj, name):
            return getattr(
                obj,
                name,
            )

    return default


# ============================================================
# JSON
# ============================================================

def load_json(
    path: Path,
) -> Any:
    """Load a JSON file."""

    if not path.exists():
        raise FileNotFoundError(
            f"Input file does not exist: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def save_json(
    path: Path,
    data: Any,
) -> None:
    """Save JSON data."""

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )


# ============================================================
# RESUME TEXT
# ============================================================

def read_resume(
    filename: str,
) -> str:
    """
    Read a resume file.

    TXT resumes are read directly.

    PDF/DOCX extraction uses the project's parser when
    available.
    """

    path = TEST_RESUMES_DIR / filename

    if not path.exists():
        warning(
            f"Resume not found: {path}"
        )
        return ""

    if path.suffix.lower() == ".txt":

        return path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

    # --------------------------------------------------------
    # Project resume parser
    # --------------------------------------------------------

    try:

        from ai.resume_parser.parser import (
            ResumeParser,
        )

        parser = ResumeParser()

        if hasattr(parser, "parse"):

            result = parser.parse(
                str(path)
            )

            if isinstance(
                result,
                str,
            ):
                return result

            if isinstance(
                result,
                dict,
            ):
                return json.dumps(
                    result,
                    ensure_ascii=False,
                )

    except Exception as exc:

        warning(
            f"ResumeParser failed for "
            f"{filename}: {exc}"
        )

    # --------------------------------------------------------
    # PDF parser fallback
    # --------------------------------------------------------

    if path.suffix.lower() == ".pdf":

        try:

            from ai.resume_parser.pdf_parser import (
                PDFResumeParser,
            )

            parser = PDFResumeParser()

            if hasattr(
                parser,
                "parse",
            ):

                result = parser.parse(
                    str(path)
                )

                if isinstance(
                    result,
                    str,
                ):
                    return result

        except Exception:
            pass

    # --------------------------------------------------------
    # DOCX parser fallback
    # --------------------------------------------------------

    if path.suffix.lower() == ".docx":

        try:

            from ai.resume_parser.docx_parser import (
                DOCXResumeParser,
            )

            parser = DOCXResumeParser()

            if hasattr(
                parser,
                "parse",
            ):

                result = parser.parse(
                    str(path)
                )

                if isinstance(
                    result,
                    str,
                ):
                    return result

        except Exception:
            pass

    return ""


# ============================================================
# RANKING MODEL
# ============================================================

def load_ranker():
    """Load the project's candidate ranker."""

    try:

        from ai.ranking.candidate_ranker import (
            CandidateRanker,
        )

        return CandidateRanker()

    except Exception as exc:

        warning(
            "Unable to load CandidateRanker: "
            f"{exc}"
        )

        return None


def predict_scores(
    candidates: list[dict[str, Any]],
) -> dict[str, float]:
    """
    Generate ranking scores.

    First attempts the project's CandidateRanker.

    Falls back to a deterministic resume-length baseline
    when the model is unavailable.
    """

    ranker = load_ranker()

    predicted: dict[str, float] = {}

    # --------------------------------------------------------
    # Model-based ranking
    # --------------------------------------------------------

    if ranker is not None:

        model_candidates = []

        for candidate in candidates:

            candidate_id = str(
                candidate.get("id")
            )

            resume_filename = candidate.get(
                "resume",
                "",
            )

            resume_text = read_resume(
                resume_filename
            )

            model_candidates.append(
                {
                    "id": candidate_id,
                    "resume_text": resume_text,
                    "candidate_id": candidate_id,
                }
            )

        try:

            if hasattr(
                ranker,
                "rank",
            ):

                result = ranker.rank(
                    model_candidates
                )

                if isinstance(
                    result,
                    list,
                ):

                    for item in result:

                        candidate_id = get_value(
                            item,
                            "id",
                            "candidate_id",
                        )

                        if candidate_id is None:
                            continue

                        score = get_value(
                            item,
                            "score",
                            "ranking_score",
                            "rank_score",
                            "similarity",
                            default=0.0,
                        )

                        predicted[
                            str(candidate_id)
                        ] = safe_float(
                            score
                        )

                elif isinstance(
                    result,
                    dict,
                ):

                    for candidate_id, score in (
                        result.items()
                    ):

                        predicted[
                            str(candidate_id)
                        ] = safe_float(
                            score
                        )

        except Exception as exc:

            warning(
                f"CandidateRanker failed: {exc}"
            )

    # --------------------------------------------------------
    # Fallback baseline
    # --------------------------------------------------------

    for candidate in candidates:

        candidate_id = str(
            candidate.get("id")
        )

        if candidate_id in predicted:
            continue

        resume_filename = candidate.get(
            "resume",
            "",
        )

        resume_text = read_resume(
            resume_filename
        )

        # Deterministic baseline.
        #
        # This is intentionally simple and should not be
        # interpreted as the production ranking algorithm.
        predicted[candidate_id] = float(
            len(
                normalize_text(
                    resume_text
                ).split()
            )
        )

    return predicted


# ============================================================
# RANKING UTILITIES
# ============================================================

def sort_scores(
    scores: dict[str, float],
) -> list[str]:
    """Sort candidates from highest to lowest score."""

    return [
        candidate_id
        for candidate_id, _ in sorted(
            scores.items(),
            key=lambda item: (
                item[1],
                item[0],
            ),
            reverse=True,
        )
    ]


def rank_positions(
    ranking: list[str],
) -> dict[str, int]:
    """Convert ranking list to 1-based positions."""

    return {
        candidate_id: index + 1
        for index, candidate_id
        in enumerate(ranking)
    }


# ============================================================
# PAIRWISE ACCURACY
# ============================================================

def pairwise_accuracy(
    expected_ranking: list[str],
    predicted_ranking: list[str],
) -> float:
    """
    Calculate pairwise ranking accuracy.

    A pair is correct when the predicted ordering matches
    the expected ordering.
    """

    expected_positions = rank_positions(
        expected_ranking
    )

    predicted_positions = rank_positions(
        predicted_ranking
    )

    common_ids = [
        candidate_id
        for candidate_id in expected_ranking
        if candidate_id in predicted_positions
    ]

    if len(common_ids) < 2:
        return 0.0

    correct = 0
    total = 0

    for index, first in enumerate(
        common_ids
    ):

        for second in common_ids[
            index + 1:
        ]:

            expected_order = (
                expected_positions[first]
                < expected_positions[second]
            )

            predicted_order = (
                predicted_positions[first]
                < predicted_positions[second]
            )

            total += 1

            if expected_order == predicted_order:
                correct += 1

    if total == 0:
        return 0.0

    return correct / total


# ============================================================
# SPEARMAN CORRELATION
# ============================================================

def spearman_correlation(
    expected_ranking: list[str],
    predicted_ranking: list[str],
) -> float:
    """Calculate Spearman rank correlation."""

    expected_positions = rank_positions(
        expected_ranking
    )

    predicted_positions = rank_positions(
        predicted_ranking
    )

    common_ids = [
        candidate_id
        for candidate_id in expected_ranking
        if candidate_id in predicted_positions
    ]

    n = len(common_ids)

    if n < 2:
        return 0.0

    sum_squared_difference = 0.0

    for candidate_id in common_ids:

        difference = (
            expected_positions[candidate_id]
            - predicted_positions[candidate_id]
        )

        sum_squared_difference += (
            difference ** 2
        )

    denominator = (
        n * (n ** 2 - 1)
    )

    if denominator == 0:
        return 0.0

    return (
        1.0
        - (
            6.0
            * sum_squared_difference
            / denominator
        )
    )


# ============================================================
# NDCG
# ============================================================

def dcg(
    relevance_scores: list[float],
) -> float:
    """Calculate Discounted Cumulative Gain."""

    total = 0.0

    for index, relevance in enumerate(
        relevance_scores
    ):

        denominator = math.log2(
            index + 2
        )

        total += (
            (2 ** relevance - 1)
            / denominator
        )

    return total


def ndcg_at_k(
    predicted_ranking: list[str],
    relevance: dict[str, float],
    k: int,
) -> float:
    """Calculate NDCG@K."""

    if k <= 0:
        return 0.0

    predicted_top_k = predicted_ranking[
        :k
    ]

    predicted_relevance = [
        relevance.get(
            candidate_id,
            0.0,
        )
        for candidate_id
        in predicted_top_k
    ]

    ideal_relevance = sorted(
        relevance.values(),
        reverse=True,
    )[:k]

    actual_dcg = dcg(
        predicted_relevance
    )

    ideal_dcg = dcg(
        ideal_relevance
    )

    if ideal_dcg == 0:
        return 0.0

    return actual_dcg / ideal_dcg


# ============================================================
# PRECISION@K
# ============================================================

def precision_at_k(
    predicted_ranking: list[str],
    relevant_ids: set[str],
    k: int,
) -> float:
    """Calculate Precision@K."""

    if k <= 0:
        return 0.0

    top_k = predicted_ranking[
        :k
    ]

    if not top_k:
        return 0.0

    relevant_count = sum(
        1
        for candidate_id in top_k
        if candidate_id in relevant_ids
    )

    return (
        relevant_count
        / len(top_k)
    )


# ============================================================
# RECALL@K
# ============================================================

def recall_at_k(
    predicted_ranking: list[str],
    relevant_ids: set[str],
    k: int,
) -> float:
    """Calculate Recall@K."""

    if not relevant_ids:
        return 0.0

    top_k = predicted_ranking[
        :k
    ]

    relevant_count = sum(
        1
        for candidate_id in top_k
        if candidate_id in relevant_ids
    )

    return (
        relevant_count
        / len(relevant_ids)
    )


# ============================================================
# MEAN ABSOLUTE RANK ERROR
# ============================================================

def mean_absolute_rank_error(
    expected_ranking: list[str],
    predicted_ranking: list[str],
) -> float:
    """Calculate mean absolute rank difference."""

    expected_positions = rank_positions(
        expected_ranking
    )

    predicted_positions = rank_positions(
        predicted_ranking
    )

    common_ids = [
        candidate_id
        for candidate_id in expected_ranking
        if candidate_id in predicted_positions
    ]

    if not common_ids:
        return 0.0

    differences = [
        abs(
            expected_positions[candidate_id]
            - predicted_positions[candidate_id]
        )
        for candidate_id in common_ids
    ]

    return statistics.mean(
        differences
    )


# ============================================================
# TOP-K ACCURACY
# ============================================================

def top_k_overlap(
    expected_ranking: list[str],
    predicted_ranking: list[str],
    k: int,
) -> float:
    """Calculate overlap between expected and predicted top-K."""

    expected_top = set(
        expected_ranking[:k]
    )

    predicted_top = set(
        predicted_ranking[:k]
    )

    if not expected_top:
        return 0.0

    return (
        len(
            expected_top
            & predicted_top
        )
        / len(expected_top)
    )


# ============================================================
# BUILD EXPECTED RANKING
# ============================================================

def extract_expected_ranking(
    data: dict[str, Any],
) -> tuple[list[str], dict[str, float]]:
    """
    Extract expected ranking and relevance values.

    Supported input formats:

        {
            "candidates": [
                {
                    "id": "candidate_001",
                    "relevance": 5
                }
            ]
        }

    Or:

        {
            "ranking": [
                "candidate_001",
                "candidate_002"
            ]
        }
    """

    candidates = data.get(
        "candidates"
    )

    if candidates:

        parsed = []

        for index, candidate in enumerate(
            candidates
        ):

            candidate_id = get_value(
                candidate,
                "id",
                "candidate_id",
            )

            if candidate_id is None:
                continue

            relevance = get_value(
                candidate,
                "relevance",
                "relevance_score",
                "label",
                "score",
                default=(
                    len(candidates)
                    - index
                ),
            )

            parsed.append(
                (
                    str(candidate_id),
                    safe_float(
                        relevance
                    ),
                    index,
                )
            )

        # If relevance labels exist, sort by relevance.
        #
        # The original order is used as a tie-breaker.
        parsed.sort(
            key=lambda item: (
                item[1],
                -item[2],
            ),
            reverse=True,
        )

        ranking = [
            item[0]
            for item in parsed
        ]

        relevance = {
            item[0]: item[1]
            for item in parsed
        }

        return ranking, relevance

    ranking = data.get(
        "ranking",
        []
    )

    ranking = [
        str(candidate_id)
        for candidate_id in ranking
    ]

    relevance = {
        candidate_id: float(
            len(ranking) - index
        )
        for index, candidate_id
        in enumerate(ranking)
    }

    return ranking, relevance


# ============================================================
# EVALUATION
# ============================================================

def evaluate(
    input_path: Path,
    k: int,
) -> dict[str, Any]:
    """Run the complete ranking evaluation."""

    start = time.perf_counter()

    data = load_json(
        input_path
    )

    if not isinstance(
        data,
        dict,
    ):
        raise ValueError(
            "Ranking evaluation input must be a JSON object."
        )

    expected_ranking, relevance = (
        extract_expected_ranking(
            data
        )
    )

    candidates = data.get(
        "candidates",
        [],
    )

    if not candidates:

        # Support simple ranking-only input.
        candidates = [
            {
                "id": candidate_id,
                "resume": "",
            }
            for candidate_id
            in expected_ranking
        ]

    if not expected_ranking:

        raise ValueError(
            "No expected candidates were found."
        )

    log(
        f"Evaluating {len(candidates)} candidates..."
    )

    predicted_scores = predict_scores(
        candidates
    )

    predicted_ranking = sort_scores(
        predicted_scores
    )

    # Only compare candidates present in both rankings.
    common_ids = [
        candidate_id
        for candidate_id in expected_ranking
        if candidate_id in predicted_scores
    ]

    if not common_ids:

        raise ValueError(
            "No candidates could be ranked."
        )

    filtered_expected = [
        candidate_id
        for candidate_id
        in expected_ranking
        if candidate_id in predicted_scores
    ]

    filtered_predicted = [
        candidate_id
        for candidate_id
        in predicted_ranking
        if candidate_id in set(common_ids)
    ]

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    pairwise = pairwise_accuracy(
        filtered_expected,
        filtered_predicted,
    )

    spearman = spearman_correlation(
        filtered_expected,
        filtered_predicted,
    )

    ndcg = ndcg_at_k(
        filtered_predicted,
        relevance,
        k,
    )

    # Relevant = candidates with positive relevance.
    relevant_ids = {
        candidate_id
        for candidate_id, score
        in relevance.items()
        if score > 0
    }

    precision = precision_at_k(
        filtered_predicted,
        relevant_ids,
        k,
    )

    recall = recall_at_k(
        filtered_predicted,
        relevant_ids,
        k,
    )

    rank_error = mean_absolute_rank_error(
        filtered_expected,
        filtered_predicted,
    )

    overlap = top_k_overlap(
        filtered_expected,
        filtered_predicted,
        k,
    )

    duration = (
        time.perf_counter()
        - start
    )

    # --------------------------------------------------------
    # Per-candidate details
    # --------------------------------------------------------

    expected_positions = rank_positions(
        filtered_expected
    )

    predicted_positions = rank_positions(
        filtered_predicted
    )

    candidate_details = []

    for candidate_id in filtered_expected:

        candidate_details.append(
            {
                "candidate_id": candidate_id,
                "expected_rank": expected_positions[
                    candidate_id
                ],
                "predicted_rank": predicted_positions[
                    candidate_id
                ],
                "rank_difference": (
                    predicted_positions[
                        candidate_id
                    ]
                    - expected_positions[
                        candidate_id
                    ]
                ),
                "absolute_rank_difference": abs(
                    predicted_positions[
                        candidate_id
                    ]
                    - expected_positions[
                        candidate_id
                    ]
                ),
                "predicted_score": predicted_scores[
                    candidate_id
                ],
                "relevance": relevance.get(
                    candidate_id,
                    0.0,
                ),
            }
        )

    return {
        "project": (
            "ai-resume-screening-interview-system"
        ),
        "evaluation": "candidate_ranking",
        "input_file": str(
            input_path
        ),
        "k": k,
        "candidate_count": len(
            filtered_expected
        ),
        "metrics": {
            "pairwise_accuracy": pairwise,
            "spearman_correlation": spearman,
            "ndcg_at_k": ndcg,
            "precision_at_k": precision,
            "recall_at_k": recall,
            "top_k_overlap": overlap,
            "mean_absolute_rank_error": rank_error,
        },
        "expected_ranking": filtered_expected,
        "predicted_ranking": filtered_predicted,
        "predicted_scores": predicted_scores,
        "candidates": candidate_details,
        "duration_seconds": duration,
    }


# ============================================================
# PRINT REPORT
# ============================================================

def print_report(
    report: dict[str, Any],
) -> None:
    """Print a readable evaluation report."""

    metrics = report[
        "metrics"
    ]

    print()
    print("=" * 72)
    print(
        "AI RESUME SCREENING & INTERVIEW SYSTEM"
    )
    print(
        "CANDIDATE RANKING EVALUATION"
    )
    print("=" * 72)

    print()
    print(
        f"Candidates: "
        f"{report['candidate_count']}"
    )

    print(
        f"K: "
        f"{report['k']}"
    )

    print(
        f"Duration: "
        f"{report['duration_seconds']:.3f}s"
    )

    print()
    print("-" * 72)
    print("METRICS")
    print("-" * 72)

    print(
        "Pairwise Accuracy       : "
        f"{metrics['pairwise_accuracy'] * 100:.2f}%"
    )

    print(
        "Spearman Correlation    : "
        f"{metrics['spearman_correlation']:.4f}"
    )

    print(
        f"NDCG@{report['k']}                  : "
        f"{metrics['ndcg_at_k']:.4f}"
    )

    print(
        f"Precision@{report['k']}             : "
        f"{metrics['precision_at_k'] * 100:.2f}%"
    )

    print(
        f"Recall@{report['k']}                : "
        f"{metrics['recall_at_k'] * 100:.2f}%"
    )

    print(
        f"Top-{report['k']} Overlap            : "
        f"{metrics['top_k_overlap'] * 100:.2f}%"
    )

    print(
        "Mean Absolute Rank Error: "
        f"{metrics['mean_absolute_rank_error']:.2f}"
    )

    print()
    print("-" * 72)
    print("EXPECTED RANKING")
    print("-" * 72)

    for index, candidate_id in enumerate(
        report["expected_ranking"],
        start=1,
    ):

        print(
            f"{index:>3}. {candidate_id}"
        )

    print()
    print("-" * 72)
    print("PREDICTED RANKING")
    print("-" * 72)

    for index, candidate_id in enumerate(
        report["predicted_ranking"],
        start=1,
    ):

        score = report[
            "predicted_scores"
        ].get(
            candidate_id,
            0.0,
        )

        print(
            f"{index:>3}. "
            f"{candidate_id:<25} "
            f"score={score:.4f}"
        )

    print()
    print("-" * 72)
    print("CANDIDATE RANK DIFFERENCES")
    print("-" * 72)

    print(
        f"{'Candidate':<25}"
        f"{'Expected':>10}"
        f"{'Predicted':>11}"
        f"{'Difference':>12}"
    )

    for candidate in report[
        "candidates"
    ]:

        print(
            f"{candidate['candidate_id']:<25}"
            f"{candidate['expected_rank']:>10}"
            f"{candidate['predicted_rank']:>11}"
            f"{candidate['rank_difference']:>12}"
        )

    print()
    print("=" * 72)
    print("Evaluation complete.")
    print("=" * 72)
    print()


# ============================================================
# ARGUMENTS
# ============================================================

def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Evaluate the candidate ranking "
            "model."
        )
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=(
            "Path to ranking evaluation JSON."
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=(
            "Path for generated evaluation report."
        ),
    )

    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help=(
            "K value used for NDCG, "
            "precision, recall, and top-K overlap."
        ),
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help=(
            "Do not print the detailed report."
        ),
    )

    return parser.parse_args()


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """Application entry point."""

    args = parse_arguments()

    if args.k <= 0:

        error(
            "--k must be greater than zero."
        )

        return 1

    log(
        "Starting candidate ranking evaluation..."
    )

    log(
        f"Input: {args.input}"
    )

    try:

        report = evaluate(
            input_path=args.input,
            k=args.k,
        )

        save_json(
            args.output,
            report,
        )

        log(
            f"Report saved to {args.output}"
        )

        if not args.quiet:

            print_report(
                report
            )

        return 0

    except FileNotFoundError as exc:

        error(
            str(exc)
        )

        return 1

    except KeyboardInterrupt:

        print()

        warning(
            "Evaluation cancelled."
        )

        return 130

    except Exception as exc:

        error(
            f"Ranking evaluation failed: {exc}"
        )

        return 1


# ============================================================
# SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":
    raise SystemExit(
        main()
    )