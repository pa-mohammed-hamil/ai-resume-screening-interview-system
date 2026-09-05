# Project scaffold file
"""
Skill Normalizer
----------------
Normalizes extracted skills into canonical skill names.

Location:
    ai/skill_intelligence/skill_normalizer.py

Responsibilities:
    - Convert aliases to canonical skill names
    - Normalize capitalization and punctuation
    - Handle common technology aliases
    - Deduplicate skills
    - Categorize normalized skills
    - Compare skills reliably
    - Normalize complete skill lists

Example:

    "JS"       -> "javascript"
    "React.js" -> "react"
    "Sklearn"  -> "scikit-learn"
    "Postgres" -> "postgresql"
    "GCP"      -> "google cloud"
    "K8s"      -> "kubernetes"

Typical flow:

    Resume
       |
       v
    skill_extractor.py
       |
       v
    skill_normalizer.py
       |
       +---- canonical skills
       |
       v
    matching/
       |
       +---- scoring/
       |
       +---- skill_gap.py
       |
       +---- ranking/
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class NormalizedSkill:
    """Represents a normalized skill."""

    canonical_name: str
    original_name: str
    category: str
    matched_alias: str | None = None
    confidence: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        """Convert normalized skill to dictionary."""

        return {
            "canonical_name": self.canonical_name,
            "original_name": self.original_name,
            "category": self.category,
            "matched_alias": self.matched_alias,
            "confidence": round(
                self.confidence,
                4,
            ),
        }


@dataclass
class NormalizationResult:
    """Result of normalizing a collection of skills."""

    skills: list[NormalizedSkill]
    canonical_skills: list[str]
    unknown_skills: list[str]
    duplicate_count: int
    total_input_skills: int

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary."""

        return {
            "skills": [
                skill.to_dict()
                for skill in self.skills
            ],
            "canonical_skills": self.canonical_skills,
            "unknown_skills": self.unknown_skills,
            "duplicate_count": self.duplicate_count,
            "total_input_skills": self.total_input_skills,
        }


# ---------------------------------------------------------------------------
# Default canonical taxonomy
# ---------------------------------------------------------------------------

DEFAULT_SKILL_TAXONOMY: dict[str, dict[str, Any]] = {

    # -----------------------------------------------------------------------
    # Programming Languages
    # -----------------------------------------------------------------------

    "python": {
        "category": "programming_language",
        "aliases": ["py", "python3"],
    },

    "java": {
        "category": "programming_language",
        "aliases": ["java8", "java11", "java17", "java21"],
    },

    "javascript": {
        "category": "programming_language",
        "aliases": ["js", "javascript es6", "ecmascript"],
    },

    "typescript": {
        "category": "programming_language",
        "aliases": ["ts"],
    },

    "c": {
        "category": "programming_language",
        "aliases": [],
    },

    "c++": {
        "category": "programming_language",
        "aliases": ["cpp", "cplusplus"],
    },

    "c#": {
        "category": "programming_language",
        "aliases": ["csharp", "c sharp"],
    },

    "go": {
        "category": "programming_language",
        "aliases": ["golang"],
    },

    "rust": {
        "category": "programming_language",
        "aliases": [],
    },

    "php": {
        "category": "programming_language",
        "aliases": [],
    },

    "ruby": {
        "category": "programming_language",
        "aliases": [],
    },

    "kotlin": {
        "category": "programming_language",
        "aliases": [],
    },

    "swift": {
        "category": "programming_language",
        "aliases": [],
    },

    # -----------------------------------------------------------------------
    # Frontend / Backend Frameworks
    # -----------------------------------------------------------------------

    "react": {
        "category": "framework",
        "aliases": [
            "reactjs",
            "react.js",
        ],
    },

    "angular": {
        "category": "framework",
        "aliases": [
            "angularjs",
            "angular.js",
        ],
    },

    "vue": {
        "category": "framework",
        "aliases": [
            "vuejs",
            "vue.js",
        ],
    },

    "next.js": {
        "category": "framework",
        "aliases": [
            "nextjs",
            "next",
        ],
    },

    "node.js": {
        "category": "runtime",
        "aliases": [
            "nodejs",
            "node",
        ],
    },

    "express": {
        "category": "framework",
        "aliases": [
            "expressjs",
            "express.js",
        ],
    },

    "fastapi": {
        "category": "framework",
        "aliases": [],
    },

    "django": {
        "category": "framework",
        "aliases": [],
    },

    "flask": {
        "category": "framework",
        "aliases": [],
    },

    "spring boot": {
        "category": "framework",
        "aliases": [
            "springboot",
            "spring boot framework",
        ],
    },

    "spring": {
        "category": "framework",
        "aliases": [
            "spring framework",
        ],
    },

    ".net": {
        "category": "framework",
        "aliases": [
            "dotnet",
            "dot net",
            ".net core",
            "dotnet core",
        ],
    },

    "asp.net": {
        "category": "framework",
        "aliases": [
            "aspnet",
            "asp.net core",
            "aspnet core",
        ],
    },

    # -----------------------------------------------------------------------
    # AI / Machine Learning
    # -----------------------------------------------------------------------

    "machine learning": {
        "category": "machine_learning",
        "aliases": [
            "ml",
            "machine-learning",
        ],
    },

    "deep learning": {
        "category": "machine_learning",
        "aliases": [
            "dl",
            "deep-learning",
        ],
    },

    "natural language processing": {
        "category": "ai",
        "aliases": [
            "nlp",
            "natural-language processing",
        ],
    },

    "generative ai": {
        "category": "ai",
        "aliases": [
            "genai",
            "gen ai",
            "generative artificial intelligence",
        ],
    },

    "large language models": {
        "category": "ai",
        "aliases": [
            "llm",
            "llms",
            "large language model",
        ],
    },

    "computer vision": {
        "category": "ai",
        "aliases": [
            "cv",
            "computer-vision",
        ],
    },

    "pytorch": {
        "category": "machine_learning_framework",
        "aliases": [
            "torch",
        ],
    },

    "tensorflow": {
        "category": "machine_learning_framework",
        "aliases": [
            "tf",
        ],
    },

    "scikit-learn": {
        "category": "machine_learning_framework",
        "aliases": [
            "sklearn",
            "scikit learn",
            "scikit_learn",
        ],
    },

    "keras": {
        "category": "machine_learning_framework",
        "aliases": [],
    },

    "hugging face": {
        "category": "ai_tool",
        "aliases": [
            "huggingface",
            "hugging face transformers",
        ],
    },

    # -----------------------------------------------------------------------
    # Data Science
    # -----------------------------------------------------------------------

    "pandas": {
        "category": "data_science",
        "aliases": [],
    },

    "numpy": {
        "category": "data_science",
        "aliases": [],
    },

    "matplotlib": {
        "category": "data_visualization",
        "aliases": [],
    },

    "seaborn": {
        "category": "data_visualization",
        "aliases": [],
    },

    "jupyter": {
        "category": "data_science_tool",
        "aliases": [
            "jupyter notebook",
            "jupyter notebooks",
        ],
    },

    # -----------------------------------------------------------------------
    # Databases
    # -----------------------------------------------------------------------

    "postgresql": {
        "category": "database",
        "aliases": [
            "postgres",
            "postgre",
            "postgre sql",
        ],
    },

    "mysql": {
        "category": "database",
        "aliases": [],
    },

    "mongodb": {
        "category": "database",
        "aliases": [
            "mongo",
            "mongo db",
        ],
    },

    "redis": {
        "category": "database",
        "aliases": [],
    },

    "sqlite": {
        "category": "database",
        "aliases": [],
    },

    "oracle": {
        "category": "database",
        "aliases": [
            "oracle db",
            "oracle database",
        ],
    },

    "microsoft sql server": {
        "category": "database",
        "aliases": [
            "sql server",
            "mssql",
            "ms sql server",
        ],
    },

    "elasticsearch": {
        "category": "database",
        "aliases": [
            "elastic search",
            "elastic",
        ],
    },

    "dynamodb": {
        "category": "database",
        "aliases": [
            "dynamo db",
            "amazon dynamodb",
        ],
    },

    # -----------------------------------------------------------------------
    # Cloud
    # -----------------------------------------------------------------------

    "aws": {
        "category": "cloud",
        "aliases": [
            "amazon web services",
            "amazon aws",
        ],
    },

    "azure": {
        "category": "cloud",
        "aliases": [
            "microsoft azure",
            "ms azure",
        ],
    },

    "google cloud": {
        "category": "cloud",
        "aliases": [
            "gcp",
            "google cloud platform",
            "google cloud services",
        ],
    },

    # -----------------------------------------------------------------------
    # DevOps
    # -----------------------------------------------------------------------

    "docker": {
        "category": "devops",
        "aliases": [
            "docker containers",
        ],
    },

    "kubernetes": {
        "category": "devops",
        "aliases": [
            "k8s",
            "kube",
        ],
    },

    "terraform": {
        "category": "devops",
        "aliases": [],
    },

    "jenkins": {
        "category": "devops",
        "aliases": [],
    },

    "github actions": {
        "category": "devops",
        "aliases": [
            "github action",
        ],
    },

    "gitlab ci": {
        "category": "devops",
        "aliases": [
            "gitlab ci/cd",
            "gitlab cicd",
        ],
    },

    # -----------------------------------------------------------------------
    # Version Control
    # -----------------------------------------------------------------------

    "git": {
        "category": "version_control",
        "aliases": [],
    },

    "github": {
        "category": "version_control",
        "aliases": [],
    },

    "gitlab": {
        "category": "version_control",
        "aliases": [],
    },

    # -----------------------------------------------------------------------
    # API / Architecture
    # -----------------------------------------------------------------------

    "rest api": {
        "category": "api",
        "aliases": [
            "rest apis",
            "restful api",
            "restful apis",
            "rest",
        ],
    },

    "graphql": {
        "category": "api",
        "aliases": [],
    },

    "microservices": {
        "category": "architecture",
        "aliases": [
            "microservice",
            "microservice architecture",
        ],
    },

    "api development": {
        "category": "api",
        "aliases": [
            "api design",
        ],
    },

    # -----------------------------------------------------------------------
    # Soft Skills
    # -----------------------------------------------------------------------

    "communication": {
        "category": "soft_skill",
        "aliases": [
            "communication skills",
            "verbal communication",
            "written communication",
        ],
    },

    "leadership": {
        "category": "soft_skill",
        "aliases": [
            "leadership skills",
        ],
    },

    "teamwork": {
        "category": "soft_skill",
        "aliases": [
            "team work",
            "team player",
            "collaboration",
            "collaborative skills",
        ],
    },

    "problem solving": {
        "category": "soft_skill",
        "aliases": [
            "problem-solving",
            "analytical problem solving",
        ],
    },

    "time management": {
        "category": "soft_skill",
        "aliases": [
            "time-management",
        ],
    },
}


# ---------------------------------------------------------------------------
# Skill Normalizer
# ---------------------------------------------------------------------------

class SkillNormalizer:
    """Normalize extracted skills into canonical names."""

    def __init__(
        self,
        taxonomy: Mapping[
            str,
            Mapping[str, Any],
        ]
        | None = None,
        fuzzy_matching: bool = False,
        fuzzy_threshold: float = 0.90,
    ) -> None:
        self.taxonomy = dict(
            taxonomy or DEFAULT_SKILL_TAXONOMY
        )

        self.fuzzy_matching = fuzzy_matching

        self.fuzzy_threshold = fuzzy_threshold

        self.alias_map = self._build_alias_map()

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def normalize(
        self,
        skill: str,
    ) -> NormalizedSkill | None:
        """
        Normalize one skill.

        Example:
            normalize("React.js")
            -> react
        """

        if not skill or not skill.strip():
            return None

        original = skill.strip()

        normalized = self._normalize_string(
            original
        )

        # Exact canonical name.
        if normalized in self.taxonomy:
            config = self.taxonomy[normalized]

            return NormalizedSkill(
                canonical_name=normalized,
                original_name=original,
                category=str(
                    config.get(
                        "category",
                        "other",
                    )
                ),
                matched_alias=None,
                confidence=1.0,
            )

        # Alias lookup.
        canonical = self.alias_map.get(
            normalized
        )

        if canonical:
            config = self.taxonomy[canonical]

            return NormalizedSkill(
                canonical_name=canonical,
                original_name=original,
                category=str(
                    config.get(
                        "category",
                        "other",
                    )
                ),
                matched_alias=original,
                confidence=0.98,
            )

        # Optional fuzzy matching.
        if self.fuzzy_matching:
            fuzzy_result = self._fuzzy_resolve(
                normalized
            )

            if fuzzy_result:
                canonical, score = fuzzy_result

                config = self.taxonomy[canonical]

                return NormalizedSkill(
                    canonical_name=canonical,
                    original_name=original,
                    category=str(
                        config.get(
                            "category",
                            "other",
                        )
                    ),
                    matched_alias=original,
                    confidence=score,
                )

        return None

    def normalize_list(
        self,
        skills: Iterable[str],
    ) -> NormalizationResult:
        """
        Normalize a list of skills.

        Duplicates are removed after normalization.
        """

        input_skills = [
            str(skill)
            for skill in skills
            if skill
        ]

        normalized_skills: list[NormalizedSkill] = []
        canonical_seen: set[str] = set()
        unknown_skills: list[str] = []

        duplicate_count = 0

        for skill in input_skills:
            result = self.normalize(skill)

            if result is None:
                if skill not in unknown_skills:
                    unknown_skills.append(skill)

                continue

            canonical = result.canonical_name

            if canonical in canonical_seen:
                duplicate_count += 1
                continue

            canonical_seen.add(canonical)

            normalized_skills.append(result)

        return NormalizationResult(
            skills=normalized_skills,
            canonical_skills=[
                item.canonical_name
                for item in normalized_skills
            ],
            unknown_skills=unknown_skills,
            duplicate_count=duplicate_count,
            total_input_skills=len(input_skills),
        )

    def normalize_extracted_result(
        self,
        extraction_result: Any,
    ) -> NormalizationResult:
        """
        Normalize the output of skill_extractor.py.

        Accepts either:
            - SkillExtractionResult
            - list[str]
            - dictionaries containing skill names
        """

        if isinstance(
            extraction_result,
            (list, tuple, set),
        ):
            return self.normalize_list(
                extraction_result
            )

        if hasattr(
            extraction_result,
            "skills",
        ):
            skill_objects = (
                extraction_result.skills
            )

            names = []

            for skill in skill_objects:
                if hasattr(skill, "name"):
                    names.append(skill.name)
                elif isinstance(skill, Mapping):
                    name = skill.get("name")

                    if name:
                        names.append(name)
                else:
                    names.append(str(skill))

            return self.normalize_list(names)

        if isinstance(
            extraction_result,
            Mapping,
        ):
            skills = extraction_result.get(
                "skills",
                []
            )

            names = []

            for skill in skills:
                if isinstance(skill, Mapping):
                    name = (
                        skill.get(
                            "name"
                        )
                        or skill.get(
                            "canonical_name"
                        )
                    )

                    if name:
                        names.append(name)

                else:
                    names.append(str(skill))

            return self.normalize_list(names)

        raise TypeError(
            "Unsupported extraction result type."
        )

    # -----------------------------------------------------------------------
    # Comparison
    # -----------------------------------------------------------------------

    def canonicalize(
        self,
        skill: str,
    ) -> str | None:
        """Return canonical skill name."""

        result = self.normalize(skill)

        if result is None:
            return None

        return result.canonical_name

    def are_equivalent(
        self,
        skill_a: str,
        skill_b: str,
    ) -> bool:
        """Check whether two skill names represent the same skill."""

        normalized_a = self.canonicalize(
            skill_a
        )

        normalized_b = self.canonicalize(
            skill_b
        )

        if normalized_a is None:
            normalized_a = self._normalize_string(
                skill_a
            )

        if normalized_b is None:
            normalized_b = self._normalize_string(
                skill_b
            )

        return normalized_a == normalized_b

    def find_missing_skills(
        self,
        candidate_skills: Iterable[str],
        required_skills: Iterable[str],
    ) -> list[str]:
        """
        Find required skills missing from candidate skills.

        Used by skill_gap.py.
        """

        candidate_result = self.normalize_list(
            candidate_skills
        )

        required_result = self.normalize_list(
            required_skills
        )

        candidate_set = set(
            candidate_result.canonical_skills
        )

        return [
            skill
            for skill in required_result.canonical_skills
            if skill not in candidate_set
        ]

    def find_matching_skills(
        self,
        candidate_skills: Iterable[str],
        required_skills: Iterable[str],
    ) -> list[str]:
        """Return skills shared by candidate and requirements."""

        candidate_result = self.normalize_list(
            candidate_skills
        )

        required_result = self.normalize_list(
            required_skills
        )

        candidate_set = set(
            candidate_result.canonical_skills
        )

        return [
            skill
            for skill in required_result.canonical_skills
            if skill in candidate_set
        ]

    # -----------------------------------------------------------------------
    # Categories
    # -----------------------------------------------------------------------

    def get_category(
        self,
        skill: str,
    ) -> str | None:
        """Return category for a skill."""

        result = self.normalize(skill)

        if result is None:
            return None

        return result.category

    def group_by_category(
        self,
        skills: Iterable[str],
    ) -> dict[str, list[str]]:
        """Group normalized skills by category."""

        result = self.normalize_list(skills)

        grouped: dict[str, list[str]] = {}

        for skill in result.skills:
            grouped.setdefault(
                skill.category,
                [],
            ).append(
                skill.canonical_name
            )

        return grouped

    # -----------------------------------------------------------------------
    # Taxonomy management
    # -----------------------------------------------------------------------

    def add_skill(
        self,
        canonical_name: str,
        category: str = "other",
        aliases: Iterable[str] | None = None,
    ) -> None:
        """Add a canonical skill to the taxonomy."""

        canonical = self._normalize_string(
            canonical_name
        )

        if not canonical:
            raise ValueError(
                "Canonical skill name cannot be empty."
            )

        self.taxonomy[canonical] = {
            "category": category,
            "aliases": list(
                aliases or []
            ),
        }

        self._rebuild_alias_map()

    def add_alias(
        self,
        canonical_name: str,
        alias: str,
    ) -> None:
        """Add an alias to an existing skill."""

        canonical = self._normalize_string(
            canonical_name
        )

        if canonical not in self.taxonomy:
            raise ValueError(
                f"Unknown canonical skill: "
                f"{canonical_name}"
            )

        aliases = self.taxonomy[
            canonical
        ].setdefault(
            "aliases",
            [],
        )

        if alias not in aliases:
            aliases.append(alias)

        self._rebuild_alias_map()

    def remove_skill(
        self,
        skill: str,
    ) -> bool:
        """Remove a skill from taxonomy."""

        canonical = self.canonicalize(
            skill
        )

        if canonical is None:
            return False

        if canonical not in self.taxonomy:
            return False

        del self.taxonomy[canonical]

        self._rebuild_alias_map()

        return True

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _build_alias_map(
        self,
    ) -> dict[str, str]:
        """Build alias -> canonical skill mapping."""

        alias_map: dict[str, str] = {}

        for canonical, config in self.taxonomy.items():

            canonical_normalized = (
                self._normalize_string(
                    canonical
                )
            )

            alias_map[
                canonical_normalized
            ] = canonical

            for alias in config.get(
                "aliases",
                [],
            ):
                normalized_alias = (
                    self._normalize_string(
                        str(alias)
                    )
                )

                if normalized_alias:
                    alias_map[
                        normalized_alias
                    ] = canonical

        return alias_map

    def _rebuild_alias_map(self) -> None:
        """Rebuild internal alias mapping."""

        self.alias_map = (
            self._build_alias_map()
        )

    @staticmethod
    def _normalize_string(
        value: str,
    ) -> str:
        """
        Normalize a skill string.

        Keeps important technology characters such as:
            +, #, ., /
        """

        if not value:
            return ""

        value = unicodedata.normalize(
            "NFKC",
            value,
        )

        value = value.strip().lower()

        value = value.replace(
            "\u00a0",
            " ",
        )

        # Normalize common separators.
        value = value.replace(
            "\u2013",
            "-",
        )

        value = value.replace(
            "\u2014",
            "-",
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        # Remove surrounding punctuation only.
        value = value.strip(
            " \t\n,;:()[]{}"
        )

        return value

    # -----------------------------------------------------------------------
    # Fuzzy matching
    # -----------------------------------------------------------------------

    def _fuzzy_resolve(
        self,
        skill: str,
    ) -> tuple[str, float] | None:
        """
        Resolve a skill using fuzzy matching.

        Standard library only; no external dependency required.
        """

        candidates = list(
            self.alias_map.keys()
        )

        best_candidate: str | None = None
        best_score = 0.0

        for candidate in candidates:
            score = self._similarity(
                skill,
                candidate,
            )

            if score > best_score:
                best_score = score
                best_candidate = candidate

        if (
            best_candidate is None
            or best_score
            < self.fuzzy_threshold
        ):
            return None

        canonical = self.alias_map[
            best_candidate
        ]

        return (
            canonical,
            round(
                best_score,
                4,
            ),
        )

    @staticmethod
    def _similarity(
        first: str,
        second: str,
    ) -> float:
        """
        Calculate normalized edit similarity.

        Uses Levenshtein distance.
        """

        if first == second:
            return 1.0

        if not first or not second:
            return 0.0

        distance = (
            SkillNormalizer._levenshtein_distance(
                first,
                second,
            )
        )

        maximum = max(
            len(first),
            len(second),
        )

        if maximum == 0:
            return 1.0

        return 1.0 - (
            distance / maximum
        )

    @staticmethod
    def _levenshtein_distance(
        first: str,
        second: str,
    ) -> int:
        """Calculate Levenshtein edit distance."""

        if first == second:
            return 0

        if not first:
            return len(second)

        if not second:
            return len(first)

        previous_row = list(
            range(
                len(second) + 1
            )
        )

        for i, char_a in enumerate(
            first,
            start=1,
        ):
            current_row = [i]

            for j, char_b in enumerate(
                second,
                start=1,
            ):
                insertions = (
                    current_row[j - 1] + 1
                )

                deletions = (
                    previous_row[j] + 1
                )

                substitutions = (
                    previous_row[j - 1]
                    + (
                        char_a != char_b
                    )
                )

                current_row.append(
                    min(
                        insertions,
                        deletions,
                        substitutions,
                    )
                )

            previous_row = current_row

        return previous_row[-1]


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------

def normalize_skill(
    skill: str,
) -> str | None:
    """Normalize one skill."""

    normalizer = SkillNormalizer()

    return normalizer.canonicalize(
        skill
    )


def normalize_skills(
    skills: Iterable[str],
) -> list[str]:
    """Normalize a list of skills."""

    normalizer = SkillNormalizer()

    result = normalizer.normalize_list(
        skills
    )

    return result.canonical_skills


def skills_are_equivalent(
    skill_a: str,
    skill_b: str,
) -> bool:
    """Check whether two skills are equivalent."""

    normalizer = SkillNormalizer()

    return normalizer.are_equivalent(
        skill_a,
        skill_b,
    )


def find_missing_skills(
    candidate_skills: Iterable[str],
    required_skills: Iterable[str],
) -> list[str]:
    """Find required skills absent from candidate skills."""

    normalizer = SkillNormalizer()

    return normalizer.find_missing_skills(
        candidate_skills,
        required_skills,
    )