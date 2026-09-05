# Project scaffold file
"""
Skill Taxonomy
--------------
Centralized skill taxonomy for the AI Resume Screening &
Interview System.

Location:
    ai/skill_intelligence/skill_taxonomy.py

Responsibilities:
    - Store canonical skills
    - Store aliases
    - Organize skills into categories
    - Define related skills
    - Define parent/child relationships
    - Provide taxonomy lookup utilities
    - Support skill normalization
    - Support skill-gap analysis
    - Support JD matching and candidate ranking

Architecture:

    skill_taxonomy.py
           |
           ├── skill_extractor.py
           |
           ├── skill_normalizer.py
           |
           ├── skill_gap.py
           |
           ├── jd_analysis/
           |
           ├── matching/
           |
           ├── scoring/
           |
           └── ranking/
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable


# ============================================================================
# Skill Categories
# ============================================================================


class SkillCategory(str, Enum):
    """High-level skill categories."""

    PROGRAMMING_LANGUAGE = "programming_language"
    FRAMEWORK = "framework"
    RUNTIME = "runtime"

    DATABASE = "database"
    CLOUD = "cloud"
    DEVOPS = "devops"

    AI = "ai"
    MACHINE_LEARNING = "machine_learning"
    ML_FRAMEWORK = "machine_learning_framework"
    AI_TOOL = "ai_tool"

    DATA_SCIENCE = "data_science"
    DATA_VISUALIZATION = "data_visualization"
    DATA_ENGINEERING = "data_engineering"

    API = "api"
    ARCHITECTURE = "architecture"

    VERSION_CONTROL = "version_control"
    TESTING = "testing"

    SECURITY = "security"
    SYSTEM_DESIGN = "system_design"

    SOFT_SKILL = "soft_skill"

    TOOL = "tool"
    OTHER = "other"


# ============================================================================
# Skill Definition
# ============================================================================


@dataclass(frozen=True)
class SkillDefinition:
    """Defines one canonical skill."""

    name: str
    category: SkillCategory

    aliases: tuple[str, ...] = ()

    parent: str | None = None

    related_skills: tuple[str, ...] = ()

    description: str = ""

    # Importance from 1-5.
    importance: int = 3

    # Used by matching/scoring.
    is_technical: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert skill definition to dictionary."""

        return {
            "name": self.name,
            "category": self.category.value,
            "aliases": list(self.aliases),
            "parent": self.parent,
            "related_skills": list(
                self.related_skills
            ),
            "description": self.description,
            "importance": self.importance,
            "is_technical": self.is_technical,
        }


# ============================================================================
# Programming Languages
# ============================================================================


PROGRAMMING_LANGUAGES = (
    SkillDefinition(
        name="python",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=("py", "python3"),
        importance=5,
    ),

    SkillDefinition(
        name="java",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=(
            "java8",
            "java11",
            "java17",
            "java21",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="javascript",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=(
            "js",
            "ecmascript",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="typescript",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=("ts",),
        importance=5,
    ),

    SkillDefinition(
        name="c",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=(),
        importance=4,
    ),

    SkillDefinition(
        name="c++",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=(
            "cpp",
            "cplusplus",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="c#",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=(
            "csharp",
            "c sharp",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="go",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=("golang",),
        importance=4,
    ),

    SkillDefinition(
        name="rust",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=(),
        importance=4,
    ),

    SkillDefinition(
        name="php",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=(),
        importance=3,
    ),

    SkillDefinition(
        name="ruby",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=(),
        importance=3,
    ),

    SkillDefinition(
        name="kotlin",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=(),
        importance=4,
    ),

    SkillDefinition(
        name="swift",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        aliases=(),
        importance=4,
    ),
)


# ============================================================================
# Frontend Frameworks
# ============================================================================


FRONTEND_FRAMEWORKS = (
    SkillDefinition(
        name="react",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "reactjs",
            "react.js",
        ),
        related_skills=(
            "javascript",
            "typescript",
            "next.js",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="angular",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "angularjs",
            "angular.js",
        ),
        related_skills=(
            "typescript",
            "javascript",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="vue",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "vuejs",
            "vue.js",
        ),
        related_skills=(
            "javascript",
            "typescript",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="next.js",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "nextjs",
            "next",
        ),
        related_skills=(
            "react",
            "javascript",
            "typescript",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="svelte",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "sveltejs",
        ),
        related_skills=(
            "javascript",
            "typescript",
        ),
        importance=3,
    ),
)


# ============================================================================
# Backend Frameworks
# ============================================================================


BACKEND_FRAMEWORKS = (
    SkillDefinition(
        name="fastapi",
        category=SkillCategory.FRAMEWORK,
        aliases=(),
        related_skills=(
            "python",
            "rest api",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="django",
        category=SkillCategory.FRAMEWORK,
        aliases=(),
        related_skills=(
            "python",
            "rest api",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="flask",
        category=SkillCategory.FRAMEWORK,
        aliases=(),
        related_skills=(
            "python",
            "rest api",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="express",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "expressjs",
            "express.js",
        ),
        related_skills=(
            "node.js",
            "javascript",
            "rest api",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="spring",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "spring framework",
        ),
        related_skills=(
            "java",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="spring boot",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "springboot",
            "spring boot framework",
        ),
        parent="spring",
        related_skills=(
            "java",
            "rest api",
            "microservices",
        ),
        importance=5,
    ),

    SkillDefinition(
        name=".net",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "dotnet",
            "dot net",
        ),
        related_skills=(
            "c#",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="asp.net",
        category=SkillCategory.FRAMEWORK,
        aliases=(
            "aspnet",
            "asp.net core",
            "aspnet core",
        ),
        parent=".net",
        related_skills=(
            "c#",
        ),
        importance=4,
    ),
)


# ============================================================================
# Runtime
# ============================================================================


RUNTIMES = (
    SkillDefinition(
        name="node.js",
        category=SkillCategory.RUNTIME,
        aliases=(
            "nodejs",
            "node",
        ),
        related_skills=(
            "javascript",
            "typescript",
            "express",
        ),
        importance=5,
    ),
)


# ============================================================================
# AI / Machine Learning
# ============================================================================


AI_SKILLS = (
    SkillDefinition(
        name="artificial intelligence",
        category=SkillCategory.AI,
        aliases=(
            "ai",
            "artificial intelligence",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="generative ai",
        category=SkillCategory.AI,
        aliases=(
            "genai",
            "gen ai",
            "generative artificial intelligence",
        ),
        related_skills=(
            "large language models",
            "natural language processing",
            "rag",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="large language models",
        category=SkillCategory.AI,
        aliases=(
            "llm",
            "llms",
            "large language model",
        ),
        parent="generative ai",
        related_skills=(
            "natural language processing",
            "generative ai",
            "rag",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="natural language processing",
        category=SkillCategory.AI,
        aliases=(
            "nlp",
            "natural language processing",
        ),
        related_skills=(
            "machine learning",
            "deep learning",
            "large language models",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="computer vision",
        category=SkillCategory.AI,
        aliases=(
            "cv",
            "computer-vision",
        ),
        related_skills=(
            "deep learning",
            "machine learning",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="machine learning",
        category=SkillCategory.MACHINE_LEARNING,
        aliases=(
            "ml",
            "machine-learning",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="deep learning",
        category=SkillCategory.MACHINE_LEARNING,
        aliases=(
            "dl",
            "deep-learning",
        ),
        parent="machine learning",
        related_skills=(
            "pytorch",
            "tensorflow",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="reinforcement learning",
        category=SkillCategory.MACHINE_LEARNING,
        aliases=(
            "rl",
        ),
        parent="machine learning",
        importance=4,
    ),
)


# ============================================================================
# ML Frameworks
# ============================================================================


ML_FRAMEWORKS = (
    SkillDefinition(
        name="pytorch",
        category=SkillCategory.ML_FRAMEWORK,
        aliases=(
            "torch",
        ),
        related_skills=(
            "deep learning",
            "python",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="tensorflow",
        category=SkillCategory.ML_FRAMEWORK,
        aliases=(
            "tf",
        ),
        related_skills=(
            "deep learning",
            "python",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="scikit-learn",
        category=SkillCategory.ML_FRAMEWORK,
        aliases=(
            "sklearn",
            "scikit learn",
            "scikit_learn",
        ),
        related_skills=(
            "machine learning",
            "python",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="keras",
        category=SkillCategory.ML_FRAMEWORK,
        aliases=(),
        related_skills=(
            "tensorflow",
            "deep learning",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="xgboost",
        category=SkillCategory.ML_FRAMEWORK,
        aliases=(),
        related_skills=(
            "machine learning",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="lightgbm",
        category=SkillCategory.ML_FRAMEWORK,
        aliases=(),
        related_skills=(
            "machine learning",
        ),
        importance=4,
    ),
)


# ============================================================================
# GenAI / RAG
# ============================================================================


GENAI_SKILLS = (
    SkillDefinition(
        name="rag",
        category=SkillCategory.AI,
        aliases=(
            "retrieval augmented generation",
            "retrieval-augmented generation",
        ),
        related_skills=(
            "generative ai",
            "large language models",
            "vector database",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="prompt engineering",
        category=SkillCategory.AI,
        aliases=(
            "prompt design",
            "prompt engineering",
        ),
        related_skills=(
            "generative ai",
            "large language models",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="vector database",
        category=SkillCategory.DATABASE,
        aliases=(
            "vector db",
            "vector databases",
        ),
        related_skills=(
            "rag",
            "embeddings",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="embeddings",
        category=SkillCategory.AI,
        aliases=(
            "text embeddings",
            "vector embeddings",
        ),
        related_skills=(
            "rag",
            "vector database",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="langchain",
        category=SkillCategory.AI_TOOL,
        aliases=(
            "lang chain",
        ),
        related_skills=(
            "rag",
            "generative ai",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="llamaindex",
        category=SkillCategory.AI_TOOL,
        aliases=(
            "llama index",
        ),
        related_skills=(
            "rag",
            "generative ai",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="hugging face",
        category=SkillCategory.AI_TOOL,
        aliases=(
            "huggingface",
            "hugging face transformers",
        ),
        importance=4,
    ),
)


# ============================================================================
# Data Science
# ============================================================================


DATA_SCIENCE_SKILLS = (
    SkillDefinition(
        name="pandas",
        category=SkillCategory.DATA_SCIENCE,
        aliases=(),
        related_skills=(
            "python",
            "numpy",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="numpy",
        category=SkillCategory.DATA_SCIENCE,
        aliases=(),
        related_skills=(
            "python",
            "pandas",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="scipy",
        category=SkillCategory.DATA_SCIENCE,
        aliases=(),
        related_skills=(
            "python",
            "numpy",
        ),
        importance=3,
    ),

    SkillDefinition(
        name="matplotlib",
        category=SkillCategory.DATA_VISUALIZATION,
        aliases=(),
        related_skills=(
            "python",
            "pandas",
        ),
        importance=3,
    ),

    SkillDefinition(
        name="seaborn",
        category=SkillCategory.DATA_VISUALIZATION,
        aliases=(),
        related_skills=(
            "python",
            "matplotlib",
        ),
        importance=3,
    ),

    SkillDefinition(
        name="jupyter",
        category=SkillCategory.DATA_SCIENCE,
        aliases=(
            "jupyter notebook",
            "jupyter notebooks",
        ),
        importance=3,
    ),
)


# ============================================================================
# Databases
# ============================================================================


DATABASES = (
    SkillDefinition(
        name="postgresql",
        category=SkillCategory.DATABASE,
        aliases=(
            "postgres",
            "postgre",
            "postgre sql",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="mysql",
        category=SkillCategory.DATABASE,
        aliases=(),
        importance=4,
    ),

    SkillDefinition(
        name="mongodb",
        category=SkillCategory.DATABASE,
        aliases=(
            "mongo",
            "mongo db",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="redis",
        category=SkillCategory.DATABASE,
        aliases=(),
        importance=4,
    ),

    SkillDefinition(
        name="sqlite",
        category=SkillCategory.DATABASE,
        aliases=(),
        importance=3,
    ),

    SkillDefinition(
        name="oracle",
        category=SkillCategory.DATABASE,
        aliases=(
            "oracle db",
            "oracle database",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="microsoft sql server",
        category=SkillCategory.DATABASE,
        aliases=(
            "sql server",
            "mssql",
            "ms sql server",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="elasticsearch",
        category=SkillCategory.DATABASE,
        aliases=(
            "elastic search",
            "elastic",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="dynamodb",
        category=SkillCategory.DATABASE,
        aliases=(
            "dynamo db",
            "amazon dynamodb",
        ),
        importance=4,
    ),
)


# ============================================================================
# Cloud
# ============================================================================


CLOUD_SKILLS = (
    SkillDefinition(
        name="aws",
        category=SkillCategory.CLOUD,
        aliases=(
            "amazon web services",
            "amazon aws",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="azure",
        category=SkillCategory.CLOUD,
        aliases=(
            "microsoft azure",
            "ms azure",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="google cloud",
        category=SkillCategory.CLOUD,
        aliases=(
            "gcp",
            "google cloud platform",
        ),
        importance=5,
    ),
)


# ============================================================================
# DevOps
# ============================================================================


DEVOPS_SKILLS = (
    SkillDefinition(
        name="docker",
        category=SkillCategory.DEVOPS,
        aliases=(
            "docker containers",
            "containerization",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="kubernetes",
        category=SkillCategory.DEVOPS,
        aliases=(
            "k8s",
            "kube",
        ),
        related_skills=(
            "docker",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="terraform",
        category=SkillCategory.DEVOPS,
        aliases=(),
        importance=4,
    ),

    SkillDefinition(
        name="jenkins",
        category=SkillCategory.DEVOPS,
        aliases=(),
        importance=4,
    ),

    SkillDefinition(
        name="github actions",
        category=SkillCategory.DEVOPS,
        aliases=(
            "github action",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="gitlab ci",
        category=SkillCategory.DEVOPS,
        aliases=(
            "gitlab ci/cd",
            "gitlab cicd",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="ci/cd",
        category=SkillCategory.DEVOPS,
        aliases=(
            "cicd",
            "continuous integration",
            "continuous delivery",
            "continuous deployment",
        ),
        importance=4,
    ),
)


# ============================================================================
# API / Architecture
# ============================================================================


API_SKILLS = (
    SkillDefinition(
        name="rest api",
        category=SkillCategory.API,
        aliases=(
            "rest apis",
            "restful api",
            "restful apis",
            "rest",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="graphql",
        category=SkillCategory.API,
        aliases=(),
        importance=4,
    ),

    SkillDefinition(
        name="websocket",
        category=SkillCategory.API,
        aliases=(
            "websockets",
            "web socket",
        ),
        importance=3,
    ),

    SkillDefinition(
        name="microservices",
        category=SkillCategory.ARCHITECTURE,
        aliases=(
            "microservice",
            "microservice architecture",
        ),
        importance=5,
    ),

    SkillDefinition(
        name="system design",
        category=SkillCategory.SYSTEM_DESIGN,
        aliases=(
            "system architecture",
            "software architecture",
        ),
        importance=5,
    ),
)


# ============================================================================
# Version Control
# ============================================================================


VERSION_CONTROL = (
    SkillDefinition(
        name="git",
        category=SkillCategory.VERSION_CONTROL,
        aliases=(),
        importance=5,
    ),

    SkillDefinition(
        name="github",
        category=SkillCategory.VERSION_CONTROL,
        aliases=(),
        importance=4,
    ),

    SkillDefinition(
        name="gitlab",
        category=SkillCategory.VERSION_CONTROL,
        aliases=(),
        importance=4,
    ),

    SkillDefinition(
        name="bitbucket",
        category=SkillCategory.VERSION_CONTROL,
        aliases=(),
        importance=3,
    ),
)


# ============================================================================
# Testing
# ============================================================================


TESTING_SKILLS = (
    SkillDefinition(
        name="pytest",
        category=SkillCategory.TESTING,
        aliases=(),
        related_skills=(
            "python",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="unittest",
        category=SkillCategory.TESTING,
        aliases=(
            "python unittest",
        ),
        related_skills=(
            "python",
        ),
        importance=3,
    ),

    SkillDefinition(
        name="jest",
        category=SkillCategory.TESTING,
        aliases=(),
        related_skills=(
            "javascript",
            "typescript",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="selenium",
        category=SkillCategory.TESTING,
        aliases=(),
        importance=4,
    ),

    SkillDefinition(
        name="cypress",
        category=SkillCategory.TESTING,
        aliases=(),
        importance=4,
    ),
)


# ============================================================================
# Security
# ============================================================================


SECURITY_SKILLS = (
    SkillDefinition(
        name="oauth",
        category=SkillCategory.SECURITY,
        aliases=(
            "oauth2",
            "oauth 2.0",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="jwt",
        category=SkillCategory.SECURITY,
        aliases=(
            "json web token",
            "json web tokens",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="authentication",
        category=SkillCategory.SECURITY,
        aliases=(
            "user authentication",
        ),
        importance=4,
    ),

    SkillDefinition(
        name="authorization",
        category=SkillCategory.SECURITY,
        aliases=(
            "access control",
        ),
        importance=4,
    ),
)


# ============================================================================
# Soft Skills
# ============================================================================


SOFT_SKILLS = (
    SkillDefinition(
        name="communication",
        category=SkillCategory.SOFT_SKILL,
        aliases=(
            "communication skills",
            "verbal communication",
            "written communication",
        ),
        importance=3,
        is_technical=False,
    ),

    SkillDefinition(
        name="leadership",
        category=SkillCategory.SOFT_SKILL,
        aliases=(
            "leadership skills",
        ),
        importance=3,
        is_technical=False,
    ),

    SkillDefinition(
        name="teamwork",
        category=SkillCategory.SOFT_SKILL,
        aliases=(
            "team work",
            "team player",
            "collaboration",
            "collaborative skills",
        ),
        importance=3,
        is_technical=False,
    ),

    SkillDefinition(
        name="problem solving",
        category=SkillCategory.SOFT_SKILL,
        aliases=(
            "problem-solving",
            "problem solving skills",
        ),
        importance=3,
        is_technical=False,
    ),

    SkillDefinition(
        name="time management",
        category=SkillCategory.SOFT_SKILL,
        aliases=(
            "time-management",
        ),
        importance=2,
        is_technical=False,
    ),

    SkillDefinition(
        name="adaptability",
        category=SkillCategory.SOFT_SKILL,
        aliases=(
            "adaptable",
        ),
        importance=2,
        is_technical=False,
    ),

    SkillDefinition(
        name="critical thinking",
        category=SkillCategory.SOFT_SKILL,
        aliases=(),
        importance=3,
        is_technical=False,
    ),
)


# ============================================================================
# Complete Taxonomy
# ============================================================================


ALL_SKILLS: tuple[SkillDefinition, ...] = (
    PROGRAMMING_LANGUAGES
    + FRONTEND_FRAMEWORKS
    + BACKEND_FRAMEWORKS
    + RUNTIMES
    + AI_SKILLS
    + ML_FRAMEWORKS
    + GENAI_SKILLS
    + DATA_SCIENCE_SKILLS
    + DATABASES
    + CLOUD_SKILLS
    + DEVOPS_SKILLS
    + API_SKILLS
    + VERSION_CONTROL
    + TESTING_SKILLS
    + SECURITY_SKILLS
    + SOFT_SKILLS
)


# ============================================================================
# Taxonomy Index
# ============================================================================


def _normalize_key(value: str) -> str:
    """Normalize a lookup key."""

    return (
        value
        .strip()
        .lower()
        .replace("_", " ")
    )


SKILL_INDEX: dict[str, SkillDefinition] = {
    _normalize_key(skill.name): skill
    for skill in ALL_SKILLS
}


ALIAS_INDEX: dict[str, str] = {}

for skill in ALL_SKILLS:
    canonical = skill.name

    for alias in skill.aliases:
        ALIAS_INDEX[
            _normalize_key(alias)
        ] = canonical


# ============================================================================
# Lookup Functions
# ============================================================================


def get_skill(
    skill_name: str,
) -> SkillDefinition | None:
    """
    Get a skill definition by canonical name
    or alias.
    """

    if not skill_name:
        return None

    key = _normalize_key(
        skill_name
    )

    skill = SKILL_INDEX.get(key)

    if skill:
        return skill

    canonical = ALIAS_INDEX.get(key)

    if canonical:
        return SKILL_INDEX.get(
            _normalize_key(canonical)
        )

    return None


def get_canonical_name(
    skill_name: str,
) -> str | None:
    """Return canonical skill name."""

    skill = get_skill(skill_name)

    if skill is None:
        return None

    return skill.name


def is_known_skill(
    skill_name: str,
) -> bool:
    """Check whether skill exists in taxonomy."""

    return get_skill(skill_name) is not None


# ============================================================================
# Category Functions
# ============================================================================


def get_skill_category(
    skill_name: str,
) -> SkillCategory | None:
    """Return category of a skill."""

    skill = get_skill(skill_name)

    if skill is None:
        return None

    return skill.category


def get_skills_by_category(
    category: SkillCategory | str,
) -> list[SkillDefinition]:
    """Return all skills in a category."""

    if isinstance(
        category,
        str,
    ):
        try:
            category = SkillCategory(
                category
            )
        except ValueError:
            return []

    return [
        skill
        for skill in ALL_SKILLS
        if skill.category == category
    ]


def get_category_names() -> list[str]:
    """Return available taxonomy categories."""

    return sorted(
        {
            skill.category.value
            for skill in ALL_SKILLS
        }
    )


# ============================================================================
# Alias Functions
# ============================================================================


def get_aliases(
    skill_name: str,
) -> list[str]:
    """Return aliases for a skill."""

    skill = get_skill(skill_name)

    if skill is None:
        return []

    return list(skill.aliases)


def resolve_alias(
    alias: str,
) -> str | None:
    """Resolve alias to canonical skill."""

    if not alias:
        return None

    return ALIAS_INDEX.get(
        _normalize_key(alias)
    )


# ============================================================================
# Relationship Functions
# ============================================================================


def get_parent(
    skill_name: str,
) -> str | None:
    """Return parent skill."""

    skill = get_skill(skill_name)

    if skill is None:
        return None

    return skill.parent


def get_related_skills(
    skill_name: str,
) -> list[str]:
    """Return related skills."""

    skill = get_skill(skill_name)

    if skill is None:
        return []

    return list(
        skill.related_skills
    )


def get_children(
    skill_name: str,
) -> list[str]:
    """Return direct child skills."""

    canonical = get_canonical_name(
        skill_name
    )

    if canonical is None:
        return []

    return [
        skill.name
        for skill in ALL_SKILLS
        if skill.parent == canonical
    ]


# ============================================================================
# Matching Utilities
# ============================================================================


def canonicalize_skills(
    skills: Iterable[str],
) -> list[str]:
    """
    Convert skills to canonical names.

    Unknown skills are ignored.
    Duplicates are removed.
    """

    result: list[str] = []
    seen: set[str] = set()

    for skill in skills:
        canonical = get_canonical_name(
            skill
        )

        if canonical is None:
            continue

        if canonical in seen:
            continue

        seen.add(canonical)
        result.append(canonical)

    return result


def find_matching_skills(
    candidate_skills: Iterable[str],
    required_skills: Iterable[str],
) -> list[str]:
    """Find normalized skills shared by candidate and job."""

    candidate = set(
        canonicalize_skills(
            candidate_skills
        )
    )

    required = canonicalize_skills(
        required_skills
    )

    return [
        skill
        for skill in required
        if skill in candidate
    ]


def find_missing_skills(
    candidate_skills: Iterable[str],
    required_skills: Iterable[str],
) -> list[str]:
    """Find required skills missing from candidate."""

    candidate = set(
        canonicalize_skills(
            candidate_skills
        )
    )

    required = canonicalize_skills(
        required_skills
    )

    return [
        skill
        for skill in required
        if skill not in candidate
    ]


# ============================================================================
# Similarity / Relationship
# ============================================================================


def are_equivalent(
    skill_a: str,
    skill_b: str,
) -> bool:
    """Check whether two skill names are equivalent."""

    canonical_a = get_canonical_name(
        skill_a
    )

    canonical_b = get_canonical_name(
        skill_b
    )

    if (
        canonical_a is None
        or canonical_b is None
    ):
        return False

    return canonical_a == canonical_b


def are_related(
    skill_a: str,
    skill_b: str,
) -> bool:
    """Check whether two skills are related."""

    canonical_a = get_canonical_name(
        skill_a
    )

    canonical_b = get_canonical_name(
        skill_b
    )

    if (
        canonical_a is None
        or canonical_b is None
    ):
        return False

    definition = get_skill(
        canonical_a
    )

    if definition is None:
        return False

    if canonical_b in (
        definition.related_skills
    ):
        return True

    if definition.parent == canonical_b:
        return True

    return canonical_a in (
        get_related_skills(
            canonical_b
        )
    )


# ============================================================================
# Importance
# ============================================================================


def get_skill_importance(
    skill_name: str,
) -> int:
    """
    Return skill importance from 1 to 5.

    Unknown skills receive the default value 1.
    """

    skill = get_skill(skill_name)

    if skill is None:
        return 1

    return skill.importance


# ============================================================================
# Technical / Soft Skill Utilities
# ============================================================================


def is_technical_skill(
    skill_name: str,
) -> bool:
    """Check whether skill is technical."""

    skill = get_skill(skill_name)

    if skill is None:
        return False

    return skill.is_technical


def is_soft_skill(
    skill_name: str,
) -> bool:
    """Check whether skill is a soft skill."""

    skill = get_skill(skill_name)

    if skill is None:
        return False

    return (
        skill.category
        == SkillCategory.SOFT_SKILL
    )


# ============================================================================
# Export Utilities
# ============================================================================


def taxonomy_as_dict() -> dict[str, dict[str, Any]]:
    """Return the complete taxonomy as a dictionary."""

    return {
        skill.name: skill.to_dict()
        for skill in ALL_SKILLS
    }


def taxonomy_size() -> int:
    """Return number of canonical skills."""

    return len(ALL_SKILLS)


def validate_taxonomy() -> list[str]:
    """
    Validate taxonomy consistency.

    Returns a list of validation errors.
    """

    errors: list[str] = []

    canonical_names = [
        skill.name
        for skill in ALL_SKILLS
    ]

    if len(canonical_names) != len(
        set(canonical_names)
    ):
        errors.append(
            "Duplicate canonical skill names found."
        )

    for skill in ALL_SKILLS:

        if not skill.name.strip():
            errors.append(
                "Found skill with empty name."
            )

        if skill.parent:
            if not is_known_skill(
                skill.parent
            ):
                errors.append(
                    f"{skill.name}: "
                    f"unknown parent "
                    f"{skill.parent}"
                )

        for related in (
            skill.related_skills
        ):
            if not is_known_skill(
                related
            ):
                errors.append(
                    f"{skill.name}: "
                    f"unknown related skill "
                    f"{related}"
                )

    return errors


# ============================================================================
# Public exports
# ============================================================================


__all__ = [
    "SkillCategory",
    "SkillDefinition",
    "ALL_SKILLS",
    "SKILL_INDEX",
    "ALIAS_INDEX",
    "get_skill",
    "get_canonical_name",
    "is_known_skill",
    "get_skill_category",
    "get_skills_by_category",
    "get_category_names",
    "get_aliases",
    "resolve_alias",
    "get_parent",
    "get_children",
    "get_related_skills",
    "canonicalize_skills",
    "find_matching_skills",
    "find_missing_skills",
    "are_equivalent",
    "are_related",
    "get_skill_importance",
    "is_technical_skill",
    "is_soft_skill",
    "taxonomy_as_dict",
    "taxonomy_size",
    "validate_taxonomy",
]