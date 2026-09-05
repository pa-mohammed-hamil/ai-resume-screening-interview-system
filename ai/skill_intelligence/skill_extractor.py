# Project scaffold file
"""
Skill Extractor
---------------
Extracts technical and professional skills from resume text.

Location:
    ai/skill_intelligence/skill_extractor.py

Responsibilities:
    - Detect skills from resume text
    - Normalize skill names
    - Support aliases and abbreviations
    - Extract skill evidence/context
    - Return confidence scores
    - Separate technical and soft skills
    - Provide structured output for downstream scoring/ranking

Typical flow:

    Resume Text
         |
         v
    SkillExtractor
         |
         +---- Skill Taxonomy
         |
         +---- Alias Matching
         |
         +---- Phrase Matching
         |
         v
    Extracted Skills
         |
         +---- skill_normalizer.py
         |
         +---- skill_gap.py
         |
         +---- scoring/
         |
         +---- ranking/
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SkillMatch:
    """Represents one detected skill."""

    name: str
    category: str
    confidence: float
    occurrences: int = 1
    evidence: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert skill match to a dictionary."""

        return {
            "name": self.name,
            "category": self.category,
            "confidence": round(
                self.confidence,
                4,
            ),
            "occurrences": self.occurrences,
            "evidence": self.evidence,
            "aliases": self.aliases,
        }


@dataclass
class SkillExtractionResult:
    """Complete skill extraction result."""

    skills: list[SkillMatch]
    technical_skills: list[str]
    soft_skills: list[str]
    tools: list[str]
    frameworks: list[str]
    languages: list[str]
    databases: list[str]
    cloud: list[str]
    other_skills: list[str]
    total_skills: int
    source_text_length: int

    def to_dict(self) -> dict[str, Any]:
        """Convert extraction result to dictionary."""

        return {
            "skills": [
                skill.to_dict()
                for skill in self.skills
            ],
            "technical_skills": self.technical_skills,
            "soft_skills": self.soft_skills,
            "tools": self.tools,
            "frameworks": self.frameworks,
            "languages": self.languages,
            "databases": self.databases,
            "cloud": self.cloud,
            "other_skills": self.other_skills,
            "total_skills": self.total_skills,
            "source_text_length": self.source_text_length,
        }


# ---------------------------------------------------------------------------
# Default skill taxonomy
# ---------------------------------------------------------------------------

DEFAULT_SKILLS: dict[str, dict[str, Any]] = {
    # Programming languages
    "python": {
        "category": "programming_language",
        "aliases": ["py"],
    },
    "java": {
        "category": "programming_language",
        "aliases": [],
    },
    "javascript": {
        "category": "programming_language",
        "aliases": ["js"],
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
        "aliases": ["cpp"],
    },
    "c#": {
        "category": "programming_language",
        "aliases": ["csharp"],
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

    # Frameworks
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
    "react": {
        "category": "framework",
        "aliases": ["react.js", "reactjs"],
    },
    "angular": {
        "category": "framework",
        "aliases": ["angular.js"],
    },
    "vue": {
        "category": "framework",
        "aliases": ["vue.js"],
    },
    "spring boot": {
        "category": "framework",
        "aliases": ["springboot"],
    },
    "express": {
        "category": "framework",
        "aliases": ["express.js", "expressjs"],
    },
    "next.js": {
        "category": "framework",
        "aliases": ["nextjs"],
    },
    "pytorch": {
        "category": "framework",
        "aliases": ["torch"],
    },
    "tensorflow": {
        "category": "framework",
        "aliases": ["tf"],
    },
    "scikit-learn": {
        "category": "framework",
        "aliases": ["sklearn"],
    },

    # Databases
    "postgresql": {
        "category": "database",
        "aliases": ["postgres", "postgre sql"],
    },
    "mysql": {
        "category": "database",
        "aliases": [],
    },
    "mongodb": {
        "category": "database",
        "aliases": ["mongo"],
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
        "aliases": [],
    },
    "elasticsearch": {
        "category": "database",
        "aliases": ["elastic search"],
    },

    # Cloud
    "aws": {
        "category": "cloud",
        "aliases": ["amazon web services"],
    },
    "azure": {
        "category": "cloud",
        "aliases": ["microsoft azure"],
    },
    "google cloud": {
        "category": "cloud",
        "aliases": ["gcp"],
    },
    "docker": {
        "category": "devops",
        "aliases": [],
    },
    "kubernetes": {
        "category": "devops",
        "aliases": ["k8s"],
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
        "aliases": [],
    },

    # AI / ML
    "machine learning": {
        "category": "machine_learning",
        "aliases": ["ml"],
    },
    "deep learning": {
        "category": "machine_learning",
        "aliases": ["dl"],
    },
    "natural language processing": {
        "category": "ai",
        "aliases": ["nlp"],
    },
    "generative ai": {
        "category": "ai",
        "aliases": ["genai", "gen ai"],
    },
    "large language models": {
        "category": "ai",
        "aliases": ["llm", "llms"],
    },
    "computer vision": {
        "category": "ai",
        "aliases": ["cv"],
    },
    "pandas": {
        "category": "data_science",
        "aliases": [],
    },
    "numpy": {
        "category": "data_science",
        "aliases": [],
    },
    "matplotlib": {
        "category": "data_science",
        "aliases": [],
    },

    # APIs / architecture
    "rest api": {
        "category": "api",
        "aliases": ["restful api", "rest apis"],
    },
    "graphql": {
        "category": "api",
        "aliases": [],
    },
    "microservices": {
        "category": "architecture",
        "aliases": ["microservice architecture"],
    },
    "api development": {
        "category": "api",
        "aliases": [],
    },

    # Version control
    "git": {
        "category": "tool",
        "aliases": [],
    },
    "github": {
        "category": "tool",
        "aliases": [],
    },
    "gitlab": {
        "category": "tool",
        "aliases": [],
    },

    # Soft skills
    "communication": {
        "category": "soft_skill",
        "aliases": ["communication skills"],
    },
    "leadership": {
        "category": "soft_skill",
        "aliases": ["leadership skills"],
    },
    "teamwork": {
        "category": "soft_skill",
        "aliases": ["team work", "team player"],
    },
    "problem solving": {
        "category": "soft_skill",
        "aliases": ["problem-solving"],
    },
    "time management": {
        "category": "soft_skill",
        "aliases": [],
    },
}


# ---------------------------------------------------------------------------
# Skill extractor
# ---------------------------------------------------------------------------

class SkillExtractor:
    """Extract skills from resume or job-description text."""

    def __init__(
        self,
        taxonomy: Mapping[str, Mapping[str, Any]] | None = None,
        minimum_confidence: float = 0.50,
        max_evidence_per_skill: int = 3,
    ) -> None:
        self.taxonomy = dict(
            taxonomy or DEFAULT_SKILLS
        )

        self.minimum_confidence = (
            minimum_confidence
        )

        self.max_evidence_per_skill = (
            max_evidence_per_skill
        )

        self._patterns = self._build_patterns()

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def extract(
        self,
        text: str,
    ) -> SkillExtractionResult:
        """
        Extract skills from text.

        Args:
            text: Resume or job description text.

        Returns:
            SkillExtractionResult.
        """

        if not text or not text.strip():
            return self._empty_result()

        normalized_text = self._normalize_text(text)

        matches: list[SkillMatch] = []

        for skill_name, config in self.taxonomy.items():
            match = self._find_skill(
                normalized_text,
                skill_name,
                config,
            )

            if match is not None:
                if (
                    match.confidence
                    >= self.minimum_confidence
                ):
                    matches.append(match)

        matches.sort(
            key=lambda item: (
                -item.confidence,
                -item.occurrences,
                item.name,
            )
        )

        return self._build_result(
            matches,
            text,
        )

    def extract_skill_names(
        self,
        text: str,
    ) -> list[str]:
        """Return only normalized skill names."""

        result = self.extract(text)

        return [
            skill.name
            for skill in result.skills
        ]

    def extract_by_category(
        self,
        text: str,
    ) -> dict[str, list[str]]:
        """Return skills grouped by category."""

        result = self.extract(text)

        categories: dict[str, list[str]] = {}

        for skill in result.skills:
            categories.setdefault(
                skill.category,
                [],
            ).append(skill.name)

        return categories

    def contains_skill(
        self,
        text: str,
        skill: str,
    ) -> bool:
        """Check whether a specific skill exists in text."""

        if not text or not skill:
            return False

        normalized_text = self._normalize_text(text)

        skill_key = self._resolve_skill(skill)

        if skill_key is None:
            return False

        config = self.taxonomy[skill_key]

        return (
            self._find_skill(
                normalized_text,
                skill_key,
                config,
            )
            is not None
        )

    def extract_from_lines(
        self,
        lines: Iterable[str],
    ) -> SkillExtractionResult:
        """Extract skills from a collection of lines."""

        text = "\n".join(
            str(line)
            for line in lines
            if line
        )

        return self.extract(text)

    # -----------------------------------------------------------------------
    # Pattern generation
    # -----------------------------------------------------------------------

    def _build_patterns(
        self,
    ) -> dict[str, re.Pattern[str]]:
        """Build regex patterns for all skills and aliases."""

        patterns: dict[str, re.Pattern[str]] = {}

        for skill_name, config in self.taxonomy.items():
            terms = [
                skill_name,
                *config.get("aliases", []),
            ]

            escaped_terms = [
                re.escape(str(term).lower())
                for term in terms
                if term
            ]

            if not escaped_terms:
                continue

            pattern = (
                r"(?<![\w+#.])(?:"
                + "|".join(
                    sorted(
                        escaped_terms,
                        key=len,
                        reverse=True,
                    )
                )
                + r")(?![\w+#.])"
            )

            patterns[skill_name] = re.compile(
                pattern,
                flags=re.IGNORECASE,
            )

        return patterns

    # -----------------------------------------------------------------------
    # Skill matching
    # -----------------------------------------------------------------------

    def _find_skill(
        self,
        text: str,
        skill_name: str,
        config: Mapping[str, Any],
    ) -> SkillMatch | None:
        """Find a skill and calculate confidence."""

        pattern = self._patterns.get(
            skill_name
        )

        if pattern is None:
            return None

        matches = list(
            pattern.finditer(text)
        )

        if not matches:
            return None

        occurrences = len(matches)

        evidence = self._extract_evidence(
            text,
            matches,
        )

        aliases_found = self._find_aliases(
            text,
            skill_name,
            config,
        )

        confidence = self._calculate_confidence(
            skill_name=skill_name,
            config=config,
            occurrences=occurrences,
            evidence=evidence,
            aliases_found=aliases_found,
        )

        return SkillMatch(
            name=skill_name,
            category=str(
                config.get(
                    "category",
                    "other",
                )
            ),
            confidence=confidence,
            occurrences=occurrences,
            evidence=evidence,
            aliases=aliases_found,
        )

    def _calculate_confidence(
        self,
        skill_name: str,
        config: Mapping[str, Any],
        occurrences: int,
        evidence: list[str],
        aliases_found: list[str],
    ) -> float:
        """
        Calculate heuristic confidence.

        This is not an ML probability. It is a ranking-oriented
        confidence score.
        """

        score = 0.60

        # Multiple occurrences increase confidence.
        if occurrences >= 2:
            score += 0.10

        if occurrences >= 3:
            score += 0.05

        # Evidence indicates contextual occurrence.
        if evidence:
            score += 0.05

        # Exact canonical name gets a small boost.
        if skill_name.lower() not in {
            alias.lower()
            for alias in aliases_found
        }:
            score += 0.05

        # Skills in known technical categories are generally
        # stronger extraction candidates.
        technical_categories = {
            "programming_language",
            "framework",
            "database",
            "cloud",
            "devops",
            "machine_learning",
            "ai",
            "data_science",
            "api",
            "architecture",
            "tool",
        }

        if config.get("category") in technical_categories:
            score += 0.05

        return min(
            round(score, 4),
            1.0,
        )

    # -----------------------------------------------------------------------
    # Evidence extraction
    # -----------------------------------------------------------------------

    def _extract_evidence(
        self,
        text: str,
        matches: list[re.Match[str]],
    ) -> list[str]:
        """Extract short snippets surrounding skill mentions."""

        evidence: list[str] = []

        lines = text.splitlines()

        for match in matches:
            start_line = text.count(
                "\n",
                0,
                match.start(),
            )

            end_line = text.count(
                "\n",
                0,
                match.end(),
            )

            line_index = min(
                start_line,
                len(lines) - 1,
            )

            if line_index < 0:
                continue

            snippet = lines[line_index].strip()

            if not snippet:
                continue

            if len(snippet) > 250:
                snippet = snippet[:247] + "..."

            if snippet not in evidence:
                evidence.append(snippet)

            if len(evidence) >= (
                self.max_evidence_per_skill
            ):
                break

        return evidence

    def _find_aliases(
        self,
        text: str,
        skill_name: str,
        config: Mapping[str, Any],
    ) -> list[str]:
        """Return aliases that were explicitly found."""

        aliases_found: list[str] = []

        for alias in config.get(
            "aliases",
            [],
        ):
            pattern = re.compile(
                r"(?<![\w+#.])"
                + re.escape(str(alias))
                + r"(?![\w+#.])",
                flags=re.IGNORECASE,
            )

            if pattern.search(text):
                aliases_found.append(
                    str(alias)
                )

        return aliases_found

    # -----------------------------------------------------------------------
    # Taxonomy helpers
    # -----------------------------------------------------------------------

    def _resolve_skill(
        self,
        skill: str,
    ) -> str | None:
        """Resolve canonical skill name or alias."""

        query = skill.strip().lower()

        if query in self.taxonomy:
            return query

        for skill_name, config in self.taxonomy.items():
            aliases = config.get(
                "aliases",
                [],
            )

            if any(
                query == str(alias).lower()
                for alias in aliases
            ):
                return skill_name

        return None

    def add_skill(
        self,
        name: str,
        category: str = "other",
        aliases: list[str] | None = None,
    ) -> None:
        """Add a skill dynamically."""

        canonical_name = name.strip().lower()

        if not canonical_name:
            raise ValueError(
                "Skill name cannot be empty."
            )

        self.taxonomy[canonical_name] = {
            "category": category,
            "aliases": aliases or [],
        }

        self._patterns = self._build_patterns()

    def remove_skill(
        self,
        name: str,
    ) -> bool:
        """Remove a skill from the active taxonomy."""

        canonical_name = self._resolve_skill(name)

        if canonical_name is None:
            return False

        del self.taxonomy[canonical_name]

        self._patterns = self._build_patterns()

        return True

    # -----------------------------------------------------------------------
    # Result helpers
    # -----------------------------------------------------------------------

    def _build_result(
        self,
        matches: list[SkillMatch],
        source_text: str,
    ) -> SkillExtractionResult:
        """Build categorized extraction result."""

        technical = []
        soft = []
        tools = []
        frameworks = []
        languages = []
        databases = []
        cloud = []
        other = []

        for skill in matches:
            category = skill.category

            if category == "soft_skill":
                soft.append(skill.name)

            elif category == "framework":
                technical.append(skill.name)
                frameworks.append(skill.name)

            elif category == "programming_language":
                technical.append(skill.name)
                languages.append(skill.name)

            elif category == "database":
                technical.append(skill.name)
                databases.append(skill.name)

            elif category == "cloud":
                technical.append(skill.name)
                cloud.append(skill.name)

            elif category == "tool":
                technical.append(skill.name)
                tools.append(skill.name)

            else:
                technical.append(skill.name)
                other.append(skill.name)

        return SkillExtractionResult(
            skills=matches,
            technical_skills=self._unique(
                technical
            ),
            soft_skills=self._unique(
                soft
            ),
            tools=self._unique(
                tools
            ),
            frameworks=self._unique(
                frameworks
            ),
            languages=self._unique(
                languages
            ),
            databases=self._unique(
                databases
            ),
            cloud=self._unique(
                cloud
            ),
            other_skills=self._unique(
                other
            ),
            total_skills=len(matches),
            source_text_length=len(source_text),
        )

    @staticmethod
    def _empty_result() -> SkillExtractionResult:
        """Return an empty extraction result."""

        return SkillExtractionResult(
            skills=[],
            technical_skills=[],
            soft_skills=[],
            tools=[],
            frameworks=[],
            languages=[],
            databases=[],
            cloud=[],
            other_skills=[],
            total_skills=0,
            source_text_length=0,
        )

    @staticmethod
    def _unique(
        values: Iterable[str],
    ) -> list[str]:
        """Return unique values while preserving order."""

        result: list[str] = []
        seen: set[str] = set()

        for value in values:
            key = value.lower()

            if key in seen:
                continue

            seen.add(key)
            result.append(value)

        return result

    # -----------------------------------------------------------------------
    # Text normalization
    # -----------------------------------------------------------------------

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text before matching."""

        text = text.replace(
            "\u2013",
            "-",
        )

        text = text.replace(
            "\u2014",
            "-",
        )

        text = text.replace(
            "\u00a0",
            " ",
        )

        # Normalize common PDF artifacts.
        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        return text.strip().lower()


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------

def extract_skills(
    text: str,
) -> SkillExtractionResult:
    """
    Convenience function for extracting skills.

    Example:
        result = extract_skills(resume_text)
    """

    extractor = SkillExtractor()

    return extractor.extract(text)


def extract_skill_names(
    text: str,
) -> list[str]:
    """Convenience function returning only skill names."""

    extractor = SkillExtractor()

    return extractor.extract_skill_names(text)