"""
AI Resume Screening & Interview System
=======================================

File:
    scripts/generate_embeddings.py

Purpose:
    Generate embeddings for processed resumes and job
    descriptions and save them for semantic search,
    candidate matching, and RAG.

Usage:
    python scripts/generate_embeddings.py

    python scripts/generate_embeddings.py --type resumes

    python scripts/generate_embeddings.py --type jobs

    python scripts/generate_embeddings.py --type all --force

    python scripts/generate_embeddings.py \
        --model sentence-transformers/all-MiniLM-L6-v2 \
        --batch-size 32
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"

PROCESSED_DIR = DATA_DIR / "processed"

RESUMES_DIR = PROCESSED_DIR / "resumes"

JOBS_DIR = PROCESSED_DIR / "job_descriptions"

DEFAULT_OUTPUT = (
    PROCESSED_DIR / "embeddings.json"
)


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger(
    "embedding-generator"
)


# ============================================================
# SUPPORTED FILES
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".json",
}


# ============================================================
# TEXT UTILITIES
# ============================================================

def normalize_text(
    text: str,
) -> str:
    """
    Normalize document text before embedding.
    """

    if not text:
        return ""

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if line:
            lines.append(line)

    return " ".join(
        " ".join(lines).split()
    )


def read_document(
    path: Path,
) -> str:
    """
    Read a document from disk.
    """

    try:

        content = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

    except OSError as exc:

        logger.error(
            "Failed to read %s: %s",
            path,
            exc,
        )

        return ""

    # --------------------------------------------------------
    # JSON documents
    # --------------------------------------------------------

    if path.suffix.lower() == ".json":

        try:

            data = json.loads(
                content
            )

            return json.dumps(
                data,
                ensure_ascii=False,
                sort_keys=True,
            )

        except json.JSONDecodeError:

            logger.warning(
                "Invalid JSON: %s",
                path,
            )

    return content


def text_hash(
    text: str,
) -> str:
    """
    Generate SHA-256 hash of document text.
    """

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


# ============================================================
# DOCUMENT DISCOVERY
# ============================================================

def find_documents(
    directory: Path,
) -> list[Path]:
    """
    Find all supported documents recursively.
    """

    if not directory.exists():

        logger.warning(
            "Directory does not exist: %s",
            directory,
        )

        return []

    documents = []

    for path in directory.rglob("*"):

        if not path.is_file():
            continue

        if path.suffix.lower() not in (
            SUPPORTED_EXTENSIONS
        ):
            continue

        documents.append(path)

    return sorted(
        documents
    )


# ============================================================
# EMBEDDING PROVIDER
# ============================================================

class EmbeddingProvider:
    """
    Embedding provider abstraction.

    Priority:

    1. Project implementation:
       genai.rag.embeddings

    2. sentence-transformers

    3. Deterministic fallback.

    The fallback is intended only for development/testing.
    """

    def __init__(
        self,
        model_name: str | None = None,
    ) -> None:

        self.model_name = (
            model_name
            or "sentence-transformers/all-MiniLM-L6-v2"
        )

        self.provider: Any = None

        self.provider_name = (
            "fallback"
        )

        self.dimension = 384

        self._initialize()

    # --------------------------------------------------------
    # Initialize
    # --------------------------------------------------------

    def _initialize(
        self,
    ) -> None:

        # ----------------------------------------------------
        # Project provider
        # ----------------------------------------------------

        try:

            from genai.rag.embeddings import (
                EmbeddingGenerator,
            )

            try:

                self.provider = (
                    EmbeddingGenerator(
                        model_name=self.model_name
                    )
                )

            except TypeError:

                self.provider = (
                    EmbeddingGenerator()
                )

            self.provider_name = (
                "project"
            )

            logger.info(
                "Using project embedding provider."
            )

            return

        except ImportError:

            pass

        except Exception as exc:

            logger.warning(
                "Project embedding provider "
                "failed: %s",
                exc,
            )

        # ----------------------------------------------------
        # Sentence Transformers
        # ----------------------------------------------------

        try:

            from sentence_transformers import (
                SentenceTransformer,
            )

            self.provider = (
                SentenceTransformer(
                    self.model_name
                )
            )

            self.provider_name = (
                "sentence-transformers"
            )

            try:

                self.dimension = int(
                    self.provider.get_sentence_embedding_dimension()
                )

            except Exception:
                self.dimension = 384

            logger.info(
                "Using SentenceTransformer model: %s",
                self.model_name,
            )

            return

        except ImportError:

            logger.warning(
                "sentence-transformers is not installed."
            )

        except Exception as exc:

            logger.warning(
                "Could not initialize SentenceTransformer: %s",
                exc,
            )

        # ----------------------------------------------------
        # Fallback
        # ----------------------------------------------------

        logger.warning(
            "Using deterministic fallback embeddings."
        )

    # --------------------------------------------------------
    # Fallback embedding
    # --------------------------------------------------------

    def _fallback(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate deterministic pseudo-embedding.

        This does NOT provide true semantic similarity.
        It exists so development/test pipelines can run
        without an embedding model.
        """

        digest = hashlib.sha512(
            text.encode("utf-8")
        ).digest()

        vector = []

        for index in range(
            self.dimension
        ):

            value = digest[
                index % len(digest)
            ]

            normalized = (
                value / 127.5
            ) - 1.0

            vector.append(
                normalized
            )

        # L2 normalization.
        norm = sum(
            value * value
            for value in vector
        ) ** 0.5

        if norm == 0:
            return vector

        return [
            value / norm
            for value in vector
        ]

    # --------------------------------------------------------
    # Single embedding
    # --------------------------------------------------------

    def embed(
        self,
        text: str,
    ) -> list[float]:

        if not text:
            return []

        # Project provider.
        if (
            self.provider_name
            == "project"
        ):

            for method_name in (
                "embed",
                "encode",
                "generate_embedding",
            ):

                method = getattr(
                    self.provider,
                    method_name,
                    None,
                )

                if not callable(method):
                    continue

                try:

                    result = method(
                        text
                    )

                    embedding = (
                        self._convert_embedding(
                            result
                        )
                    )

                    if embedding:

                        return embedding

                except Exception as exc:

                    logger.warning(
                        "Embedding method %s failed: %s",
                        method_name,
                        exc,
                    )

        # SentenceTransformer.
        if (
            self.provider_name
            == "sentence-transformers"
        ):

            try:

                result = (
                    self.provider.encode(
                        text,
                        normalize_embeddings=True,
                    )
                )

                return self._convert_embedding(
                    result
                )

            except Exception as exc:

                logger.warning(
                    "SentenceTransformer "
                    "embedding failed: %s",
                    exc,
                )

        return self._fallback(
            text
        )

    # --------------------------------------------------------
    # Batch embedding
    # --------------------------------------------------------

    def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        if not texts:
            return []

        # SentenceTransformer.
        if (
            self.provider_name
            == "sentence-transformers"
        ):

            try:

                results = (
                    self.provider.encode(
                        texts,
                        normalize_embeddings=True,
                        show_progress_bar=False,
                    )
                )

                return [
                    self._convert_embedding(
                        result
                    )
                    for result in results
                ]

            except Exception as exc:

                logger.warning(
                    "Batch encoding failed: %s",
                    exc,
                )

        # Project provider.
        if (
            self.provider_name
            == "project"
        ):

            method = getattr(
                self.provider,
                "embed_batch",
                None,
            )

            if callable(method):

                try:

                    results = method(
                        texts
                    )

                    return [
                        self._convert_embedding(
                            result
                        )
                        for result in results
                    ]

                except Exception as exc:

                    logger.warning(
                        "Project batch embedding failed: %s",
                        exc,
                    )

        # Generic fallback.
        return [
            self.embed(text)
            for text in texts
        ]

    # --------------------------------------------------------
    # Convert result
    # --------------------------------------------------------

    @staticmethod
    def _convert_embedding(
        result: Any,
    ) -> list[float]:

        if result is None:
            return []

        if hasattr(
            result,
            "tolist",
        ):

            result = result.tolist()

        if isinstance(
            result,
            tuple,
        ):

            result = list(result)

        # Handle [[...]].
        if (
            isinstance(result, list)
            and result
            and isinstance(
                result[0],
                list,
            )
        ):

            result = result[0]

        try:

            return [
                float(value)
                for value in result
            ]

        except (
            TypeError,
            ValueError,
        ):

            return []


# ============================================================
# DOCUMENT ID
# ============================================================

def create_document_id(
    path: Path,
) -> str:
    """
    Create a stable document ID from the relative path.
    """

    relative = str(
        path.relative_to(
            PROJECT_ROOT
        )
    )

    return hashlib.sha256(
        relative.encode("utf-8")
    ).hexdigest()[:24]


# ============================================================
# DOCUMENT RECORD
# ============================================================

def create_record(
    path: Path,
    document_type: str,
    text: str,
    embedding: list[float],
) -> dict[str, Any]:

    relative_path = str(
        path.relative_to(
            PROJECT_ROOT
        )
    )

    return {
        "id": create_document_id(
            path
        ),
        "type": document_type,
        "filename": path.name,
        "path": relative_path,
        "text_hash": text_hash(
            text
        ),
        "text_length": len(text),
        "embedding_dimension": len(
            embedding
        ),
        "embedding": embedding,
        "metadata": {
            "source": relative_path,
            "filename": path.name,
            "extension": path.suffix.lower(),
        },
    }


# ============================================================
# EXISTING DATA
# ============================================================

def load_existing(
    path: Path,
) -> dict[str, Any]:

    if not path.exists():

        return {
            "version": "1.0",
            "documents": [],
        }

    try:

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(
                file
            )

        if not isinstance(
            data,
            dict,
        ):

            return {
                "version": "1.0",
                "documents": [],
            }

        if not isinstance(
            data.get(
                "documents"
            ),
            list,
        ):

            data[
                "documents"
            ] = []

        return data

    except (
        OSError,
        json.JSONDecodeError,
    ) as exc:

        logger.warning(
            "Could not load existing embeddings: %s",
            exc,
        )

        return {
            "version": "1.0",
            "documents": [],
        }


# ============================================================
# SAVE DATA
# ============================================================

def save_embeddings(
    path: Path,
    data: dict[str, Any],
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = path.with_suffix(
        ".tmp"
    )

    with temporary.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )

    temporary.replace(
        path
    )


# ============================================================
# PROCESS DIRECTORY
# ============================================================

def process_directory(
    directory: Path,
    document_type: str,
    provider: EmbeddingProvider,
    existing: dict[str, Any],
    force: bool,
    batch_size: int,
) -> tuple[
    list[dict[str, Any]],
    int,
    int,
]:

    documents = find_documents(
        directory
    )

    logger.info(
        "Found %d %s documents.",
        len(documents),
        document_type,
    )

    existing_by_path = {}

    for record in existing.get(
        "documents",
        [],
    ):

        if not isinstance(
            record,
            dict,
        ):
            continue

        path = record.get(
            "path"
        )

        if path:
            existing_by_path[
                path
            ] = record

    results = []

    generated = 0

    skipped = 0

    pending = []

    # --------------------------------------------------------
    # Read and inspect documents
    # --------------------------------------------------------

    for path in documents:

        text = normalize_text(
            read_document(
                path
            )
        )

        if not text:

            logger.warning(
                "Skipping empty file: %s",
                path,
            )

            skipped += 1

            continue

        relative_path = str(
            path.relative_to(
                PROJECT_ROOT
            )
        )

        current_hash = text_hash(
            text
        )

        old_record = (
            existing_by_path.get(
                relative_path
            )
        )

        # ----------------------------------------------------
        # Reuse existing embedding
        # ----------------------------------------------------

        if (
            not force
            and old_record
            and old_record.get(
                "text_hash"
            ) == current_hash
            and old_record.get(
                "embedding"
            )
        ):

            results.append(
                old_record
            )

            skipped += 1

            continue

        pending.append(
            (
                path,
                text,
            )
        )

    # --------------------------------------------------------
    # Generate embeddings in batches
    # --------------------------------------------------------

    for start in range(
        0,
        len(pending),
        batch_size,
    ):

        batch = pending[
            start:start + batch_size
        ]

        texts = [
            item[1]
            for item in batch
        ]

        logger.info(
            "Embedding %d-%d of %d %s documents.",
            start + 1,
            min(
                start + batch_size,
                len(pending),
            ),
            len(pending),
            document_type,
        )

        embeddings = (
            provider.embed_batch(
                texts
            )
        )

        # Safety fallback if provider returned
        # the wrong number of vectors.
        if len(embeddings) != len(
            batch
        ):

            logger.warning(
                "Embedding count mismatch. "
                "Generating individually."
            )

            embeddings = [
                provider.embed(
                    text
                )
                for text in texts
            ]

        for (
            (path, text),
            embedding,
        ) in zip(
            batch,
            embeddings,
        ):

            if not embedding:

                logger.error(
                    "Empty embedding generated for %s",
                    path,
                )

                continue

            record = create_record(
                path=path,
                document_type=document_type,
                text=text,
                embedding=embedding,
            )

            results.append(
                record
            )

            generated += 1

    return (
        results,
        generated,
        skipped,
    )


# ============================================================
# GENERATE EMBEDDINGS
# ============================================================

def generate_embeddings(
    document_type: str,
    output_path: Path,
    batch_size: int,
    force: bool,
    model_name: str | None,
) -> dict[str, Any]:

    start_time = time.perf_counter()

    existing = load_existing(
        output_path
    )

    provider = EmbeddingProvider(
        model_name=model_name
    )

    # Existing records indexed by path.
    records_by_path = {}

    for record in existing.get(
        "documents",
        [],
    ):

        if not isinstance(
            record,
            dict,
        ):
            continue

        path = record.get(
            "path"
        )

        if path:
            records_by_path[
                path
            ] = record

    generated_count = 0

    skipped_count = 0

    # --------------------------------------------------------
    # Resumes
    # --------------------------------------------------------

    if document_type in (
        "resumes",
        "all",
    ):

        (
            records,
            generated,
            skipped,
        ) = process_directory(
            directory=RESUMES_DIR,
            document_type="resume",
            provider=provider,
            existing=existing,
            force=force,
            batch_size=batch_size,
        )

        for record in records:

            records_by_path[
                record["path"]
            ] = record

        generated_count += generated

        skipped_count += skipped

    # --------------------------------------------------------
    # Job descriptions
    # --------------------------------------------------------

    if document_type in (
        "jobs",
        "all",
    ):

        (
            records,
            generated,
            skipped,
        ) = process_directory(
            directory=JOBS_DIR,
            document_type="job_description",
            provider=provider,
            existing=existing,
            force=force,
            batch_size=batch_size,
        )

        for record in records:

            records_by_path[
                record["path"]
            ] = record

        generated_count += generated

        skipped_count += skipped

    # --------------------------------------------------------
    # Remove stale records
    # --------------------------------------------------------

    valid_paths = set()

    if document_type in (
        "resumes",
        "all",
    ):

        for path in find_documents(
            RESUMES_DIR
        ):

            valid_paths.add(
                str(
                    path.relative_to(
                        PROJECT_ROOT
                    )
                )
            )

    if document_type in (
        "jobs",
        "all",
    ):

        for path in find_documents(
            JOBS_DIR
        ):

            valid_paths.add(
                str(
                    path.relative_to(
                        PROJECT_ROOT
                    )
                )
            )

    # Preserve records from document types that were not
    # requested in this run.
    if document_type == "resumes":

        valid_paths.update(
            record.get("path")
            for record in existing.get(
                "documents",
                []
            )
            if (
                isinstance(
                    record,
                    dict,
                )
                and record.get(
                    "type"
                )
                == "job_description"
            )
        )

    elif document_type == "jobs":

        valid_paths.update(
            record.get("path")
            for record in existing.get(
                "documents",
                []
            )
            if (
                isinstance(
                    record,
                    dict,
                )
                and record.get(
                    "type"
                )
                == "resume"
            )
        )

    final_records = [
        record
        for path, record
        in records_by_path.items()
        if path in valid_paths
    ]

    final_records.sort(
        key=lambda record: (
            record.get(
                "type",
                ""
            ),
            record.get(
                "path",
                ""
            ),
        )
    )

    # --------------------------------------------------------
    # Determine dimension
    # --------------------------------------------------------

    dimension = 0

    if final_records:

        dimension = int(
            final_records[0].get(
                "embedding_dimension",
                0,
            )
        )

    duration = (
        time.perf_counter()
        - start_time
    )

    result = {
        "version": "1.0",
        "generated_at": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ",
            time.gmtime(),
        ),
        "model": provider.model_name,
        "provider": provider.provider_name,
        "embedding_dimension": dimension,
        "document_count": len(
            final_records
        ),
        "statistics": {
            "generated": generated_count,
            "skipped": skipped_count,
            "duration_seconds": round(
                duration,
                4,
            ),
        },
        "documents": final_records,
    }

    save_embeddings(
        output_path,
        result,
    )

    return result


# ============================================================
# REPORT
# ============================================================

def print_report(
    result: dict[str, Any],
    output_path: Path,
) -> None:

    documents = result[
        "documents"
    ]

    resumes = sum(
        1
        for record in documents
        if record.get(
            "type"
        ) == "resume"
    )

    jobs = sum(
        1
        for record in documents
        if record.get(
            "type"
        ) == "job_description"
    )

    statistics = result[
        "statistics"
    ]

    print()
    print("=" * 72)
    print(
        "AI RESUME SCREENING & INTERVIEW SYSTEM"
    )
    print(
        "EMBEDDING GENERATION REPORT"
    )
    print("=" * 72)

    print(
        f"Provider              : "
        f"{result['provider']}"
    )

    print(
        f"Model                 : "
        f"{result['model']}"
    )

    print(
        f"Embedding dimension   : "
        f"{result['embedding_dimension']}"
    )

    print(
        f"Total documents       : "
        f"{result['document_count']}"
    )

    print(
        f"Resume documents      : "
        f"{resumes}"
    )

    print(
        f"Job descriptions      : "
        f"{jobs}"
    )

    print(
        f"Generated             : "
        f"{statistics['generated']}"
    )

    print(
        f"Reused/skipped        : "
        f"{statistics['skipped']}"
    )

    print(
        f"Duration              : "
        f"{statistics['duration_seconds']:.3f}s"
    )

    print(
        f"Output                : "
        f"{output_path}"
    )

    print("=" * 72)
    print(
        "Embedding generation completed."
    )
    print("=" * 72)
    print()


# ============================================================
# ARGUMENTS
# ============================================================

def parse_arguments() -> argparse.Namespace:

    parser = argparse.ArgumentParser(
        description=(
            "Generate embeddings for resumes "
            "and job descriptions."
        )
    )

    parser.add_argument(
        "--type",
        choices=[
            "resumes",
            "jobs",
            "all",
        ],
        default="all",
        help=(
            "Document type to process."
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=(
            "Output embeddings JSON file."
        ),
    )

    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help=(
            "Embedding model name."
        ),
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
        help=(
            "Embedding batch size."
        ),
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Regenerate embeddings even if "
            "documents have not changed."
        ),
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help=(
            "Suppress the final report."
        ),
    )

    return parser.parse_args()


# ============================================================
# VALIDATION
# ============================================================

def validate(
    args: argparse.Namespace,
) -> None:

    if args.batch_size <= 0:

        raise ValueError(
            "Batch size must be greater than zero."
        )


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    args = parse_arguments()

    try:

        validate(
            args
        )

        logger.info(
            "Starting embedding generation..."
        )

        logger.info(
            "Document type: %s",
            args.type,
        )

        result = generate_embeddings(
            document_type=args.type,
            output_path=args.output,
            batch_size=args.batch_size,
            force=args.force,
            model_name=args.model,
        )

        if not args.quiet:

            print_report(
                result,
                args.output,
            )

        return 0

    except KeyboardInterrupt:

        logger.warning(
            "Embedding generation cancelled."
        )

        return 130

    except Exception as exc:

        logger.exception(
            "Embedding generation failed: %s",
            exc,
        )

        return 1


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    sys.exit(
        main()
    )