# Project scaffold file
"""
keyword_optimizer.py

ATS keyword optimization engine for an AI Resume Screening System.

Features:
- Extract keywords from job descriptions
- Extract keywords from resumes
- Normalize keyword aliases
- Detect matched and missing keywords
- Classify keywords by category
- Calculate keyword coverage
- Calculate keyword relevance
- Detect keyword stuffing
- Recommend safe keyword placement
- Suggest where missing keywords can naturally appear
- Produce explainable optimization reports

IMPORTANT:
This module does not invent candidate experience.
A missing keyword should only be added when it truthfully
represents the candidate's skills, experience, education,
projects, or certifications.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Set, Tuple


# ============================================================
# Data Models
# ============================================================

@dataclass
class KeywordMatch:
    """
    Represents a keyword found in the resume.
    """

    keyword: str
    category: str
    occurrences: int
    placement: str
    relevance: float


@dataclass
class KeywordSuggestion:
    """
    Represents one keyword optimization suggestion.
    """

    keyword: str
    category: str
    priority: str
    suggested_section: str
    reason: str


@dataclass
class KeywordOptimizationResult:
    """
    Complete keyword optimization report.
    """

    keyword_score: float
    coverage_score: float
    relevance_score: float
    distribution_score: float
    stuffing_score: float

    total_keywords: int
    matched_keywords: int
    missing_keywords: int

    matched_keywords_list: List[str]
    missing_keywords_list: List[str]

    keyword_matches: List[KeywordMatch]
    suggestions: List[KeywordSuggestion]

    keyword_frequency: Dict[str, int]
    categories: Dict[str, List[str]]

    stuffing_detected: bool
    recommendations: List[str]

    def to_dict(self) -> Dict:
        return {
            "keyword_score": self.keyword_score,
            "coverage_score": self.coverage_score,
            "relevance_score": self.relevance_score,
            "distribution_score": self.distribution_score,
            "stuffing_score": self.stuffing_score,
            "total_keywords": self.total_keywords,
            "matched_keywords": self.matched_keywords,
            "missing_keywords": self.missing_keywords,
            "matched_keywords_list": self.matched_keywords_list,
            "missing_keywords_list": self.missing_keywords_list,
            "keyword_matches": [
                asdict(item)
                for item in self.keyword_matches
            ],
            "suggestions": [
                asdict(item)
                for item in self.suggestions
            ],
            "keyword_frequency": self.keyword_frequency,
            "categories": self.categories,
            "stuffing_detected": self.stuffing_detected,
            "recommendations": self.recommendations,
        }


# ============================================================
# Keyword Optimizer
# ============================================================

class KeywordOptimizer:
    """
    Explainable ATS keyword optimization engine.

    Overall keyword score:

        Coverage       -> 40%
        Relevance      -> 25%
        Distribution   -> 20%
        Anti-stuffing  -> 15%

    Final score: 0-100
    """

    WEIGHTS = {
        "coverage": 0.40,
        "relevance": 0.25,
        "distribution": 0.20,
        "stuffing": 0.15,
    }

    # ========================================================
    # Technical Keywords
    # ========================================================

    TECHNICAL_KEYWORDS = {
        # Programming
        "python",
        "java",
        "javascript",
        "typescript",
        "c",
        "c++",
        "c#",
        "go",
        "golang",
        "rust",
        "php",
        "ruby",
        "kotlin",
        "swift",

        # Frontend
        "html",
        "css",
        "sass",
        "bootstrap",
        "tailwind",
        "react",
        "react.js",
        "reactjs",
        "angular",
        "vue",
        "vue.js",
        "next.js",
        "nextjs",

        # Backend
        "node",
        "node.js",
        "nodejs",
        "express",
        "express.js",
        "django",
        "flask",
        "fastapi",
        "spring",
        "spring boot",
        ".net",
        "asp.net",

        # Database
        "sql",
        "mysql",
        "postgresql",
        "postgres",
        "oracle",
        "mongodb",
        "mongo",
        "redis",
        "sqlite",
        "elasticsearch",

        # AI / ML
        "artificial intelligence",
        "ai",
        "machine learning",
        "ml",
        "deep learning",
        "natural language processing",
        "nlp",
        "computer vision",
        "generative ai",
        "genai",
        "large language model",
        "large language models",
        "llm",
        "llms",
        "transformers",
        "rag",
        "retrieval augmented generation",

        # ML Frameworks
        "tensorflow",
        "pytorch",
        "keras",
        "scikit-learn",
        "sklearn",
        "xgboost",
        "lightgbm",

        # Data
        "pandas",
        "numpy",
        "scipy",
        "matplotlib",
        "seaborn",
        "spark",
        "pyspark",
        "hadoop",
        "airflow",

        # Cloud
        "aws",
        "amazon web services",
        "azure",
        "microsoft azure",
        "gcp",
        "google cloud",
        "ec2",
        "s3",
        "lambda",

        # DevOps
        "docker",
        "kubernetes",
        "terraform",
        "ansible",
        "jenkins",
        "github actions",
        "gitlab ci",
        "ci/cd",

        # Version control
        "git",
        "github",
        "gitlab",
        "bitbucket",

        # API / Architecture
        "rest api",
        "restful api",
        "graphql",
        "grpc",
        "microservices",
        "distributed systems",
        "system design",

        # Messaging
        "kafka",
        "apache kafka",
        "rabbitmq",

        # Analytics
        "power bi",
        "tableau",
        "excel",

        # Security
        "cybersecurity",
        "information security",
        "oauth",
        "jwt",
        "authentication",
        "authorization",
    }

    # ========================================================
    # Professional Keywords
    # ========================================================

    PROFESSIONAL_KEYWORDS = {
        "software development",
        "software engineering",
        "web development",
        "backend development",
        "frontend development",
        "full stack development",
        "api development",
        "data analysis",
        "data engineering",
        "data science",
        "cloud computing",
        "cloud architecture",
        "devops",
        "test automation",
        "quality assurance",
        "agile",
        "scrum",
        "project management",
        "product management",
        "stakeholder management",
        "technical documentation",
        "code review",
        "debugging",
        "performance optimization",
        "scalability",
        "deployment",
        "automation",
        "continuous integration",
        "continuous deployment",
    }

    # ========================================================
    # Soft Skills
    # ========================================================

    SOFT_SKILLS = {
        "communication",
        "leadership",
        "teamwork",
        "collaboration",
        "problem solving",
        "problem-solving",
        "critical thinking",
        "analytical thinking",
        "time management",
        "adaptability",
        "creativity",
        "decision making",
        "decision-making",
        "mentoring",
        "negotiation",
        "presentation",
        "organization",
        "attention to detail",
        "interpersonal skills",
    }

    # ========================================================
    # Keyword Aliases
    # ========================================================

    ALIASES = {
        "react.js": "react",
        "reactjs": "react",

        "vue.js": "vue",
        "vuejs": "vue",

        "next.js": "nextjs",

        "node.js": "node",
        "nodejs": "node",

        "express.js": "express",
        "expressjs": "express",

        "golang": "go",

        "postgres": "postgresql",
        "mongo": "mongodb",

        "sklearn": "scikit-learn",

        "ai": "artificial intelligence",
        "ml": "machine learning",

        "genai": "generative ai",

        "llm": "large language model",
        "llms": "large language model",

        "amazon web services": "aws",
        "microsoft azure": "azure",
        "google cloud": "gcp",

        "restful api": "rest api",

        "problem-solving": "problem solving",
        "decision-making": "decision making",

        "continuous integration": "ci/cd",
        "continuous deployment": "ci/cd",
    }

    # ========================================================
    # Keyword Categories
    # ========================================================

    CATEGORY_MAP = {
        "programming": {
            "python",
            "java",
            "javascript",
            "typescript",
            "c",
            "c++",
            "c#",
            "go",
            "rust",
            "php",
            "ruby",
            "kotlin",
            "swift",
        },

        "frontend": {
            "html",
            "css",
            "sass",
            "bootstrap",
            "tailwind",
            "react",
            "angular",
            "vue",
            "nextjs",
        },

        "backend": {
            "node",
            "express",
            "django",
            "flask",
            "fastapi",
            "spring",
            "spring boot",
            ".net",
            "asp.net",
        },

        "database": {
            "sql",
            "mysql",
            "postgresql",
            "oracle",
            "mongodb",
            "redis",
            "sqlite",
            "elasticsearch",
        },

        "ai_ml": {
            "artificial intelligence",
            "machine learning",
            "deep learning",
            "natural language processing",
            "computer vision",
            "generative ai",
            "large language model",
            "transformers",
            "rag",
            "retrieval augmented generation",
            "tensorflow",
            "pytorch",
            "keras",
            "scikit-learn",
            "xgboost",
            "lightgbm",
        },

        "data": {
            "pandas",
            "numpy",
            "scipy",
            "matplotlib",
            "seaborn",
            "spark",
            "pyspark",
            "hadoop",
            "airflow",
            "data analysis",
            "data engineering",
            "data science",
        },

        "cloud": {
            "aws",
            "azure",
            "gcp",
            "ec2",
            "s3",
            "lambda",
            "cloud computing",
            "cloud architecture",
        },

        "devops": {
            "docker",
            "kubernetes",
            "terraform",
            "ansible",
            "jenkins",
            "github actions",
            "gitlab ci",
            "ci/cd",
            "devops",
            "deployment",
            "automation",
        },

        "architecture": {
            "rest api",
            "graphql",
            "grpc",
            "microservices",
            "distributed systems",
            "system design",
            "scalability",
        },

        "analytics": {
            "power bi",
            "tableau",
            "excel",
        },

        "soft_skills": SOFT_SKILLS,
    }

    # ========================================================
    # Resume Sections
    # ========================================================

    SECTIONS = {
        "summary": [
            "summary",
            "professional summary",
            "profile",
            "objective",
        ],

        "skills": [
            "skills",
            "technical skills",
            "core skills",
            "key skills",
            "technologies",
        ],

        "experience": [
            "experience",
            "work experience",
            "professional experience",
            "employment",
        ],

        "projects": [
            "projects",
            "personal projects",
            "academic projects",
        ],

        "education": [
            "education",
            "academic background",
        ],

        "certifications": [
            "certifications",
            "certificates",
        ],
    }

    # ========================================================
    # Initialization
    # ========================================================

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
    ):

        self.weights = (
            weights or self.WEIGHTS.copy()
        )

        self._validate_weights()

    def _validate_weights(self) -> None:

        if abs(
            sum(self.weights.values()) - 1.0
        ) > 0.001:

            raise ValueError(
                "Keyword optimizer weights must sum to 1.0."
            )

    # ========================================================
    # Normalization
    # ========================================================

    @staticmethod
    def normalize(
        text: str,
    ) -> str:

        if not text:
            return ""

        text = text.lower()

        text = text.replace(
            "–",
            "-",
        )

        text = text.replace(
            "—",
            "-",
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    # ========================================================
    # Canonical Keyword
    # ========================================================

    def canonicalize(
        self,
        keyword: str,
    ) -> str:

        keyword = self.normalize(
            keyword
        )

        return self.ALIASES.get(
            keyword,
            keyword,
        )

    # ========================================================
    # Category
    # ========================================================

    def get_category(
        self,
        keyword: str,
    ) -> str:

        keyword = self.canonicalize(
            keyword
        )

        for category, keywords in (
            self.CATEGORY_MAP.items()
        ):

            normalized = {
                self.canonicalize(k)
                for k in keywords
            }

            if keyword in normalized:
                return category

        if keyword in {
            self.canonicalize(k)
            for k in self.TECHNICAL_KEYWORDS
        }:
            return "technical"

        if keyword in {
            self.canonicalize(k)
            for k in self.PROFESSIONAL_KEYWORDS
        }:
            return "professional"

        if keyword in {
            self.canonicalize(k)
            for k in self.SOFT_SKILLS
        }:
            return "soft_skills"

        return "other"

    # ========================================================
    # Extract Known Keywords
    # ========================================================

    def extract_known_keywords(
        self,
        text: str,
    ) -> Set[str]:

        normalized = self.normalize(
            text
        )

        all_keywords = (
            self.TECHNICAL_KEYWORDS
            |
            self.PROFESSIONAL_KEYWORDS
            |
            self.SOFT_SKILLS
        )

        found = set()

        for keyword in all_keywords:

            keyword_normalized = (
                self.normalize(keyword)
            )

            pattern = re.compile(
                rf"(?<![a-zA-Z0-9])"
                rf"{re.escape(keyword_normalized)}"
                rf"(?![a-zA-Z0-9])",
                flags=re.IGNORECASE,
            )

            if pattern.search(
                normalized
            ):

                found.add(
                    self.canonicalize(keyword)
                )

        return found

    # ========================================================
    # Extract JD Keywords
    # ========================================================

    def extract_job_keywords(
        self,
        job_description: str,
    ) -> Set[str]:

        return self.extract_known_keywords(
            job_description
        )

    # ========================================================
    # Extract Resume Keywords
    # ========================================================

    def extract_resume_keywords(
        self,
        resume_text: str,
    ) -> Set[str]:

        return self.extract_known_keywords(
            resume_text
        )

    # ========================================================
    # Keyword Frequency
    # ========================================================

    def keyword_frequency(
        self,
        text: str,
        keywords: Set[str],
    ) -> Dict[str, int]:

        normalized = self.normalize(
            text
        )

        frequencies = {}

        for keyword in keywords:

            canonical = self.canonicalize(
                keyword
            )

            # Include aliases in the search.
            variants = {
                canonical,
                keyword,
            }

            for alias, target in (
                self.ALIASES.items()
            ):

                if target == canonical:
                    variants.add(alias)

            count = 0

            for variant in variants:

                pattern = re.compile(
                    rf"(?<![a-zA-Z0-9])"
                    rf"{re.escape(variant)}"
                    rf"(?![a-zA-Z0-9])",
                    flags=re.IGNORECASE,
                )

                count += len(
                    pattern.findall(
                        normalized
                    )
                )

            frequencies[canonical] = count

        return frequencies

    # ========================================================
    # Keyword Coverage
    # ========================================================

    def calculate_coverage(
        self,
        job_keywords: Set[str],
        resume_keywords: Set[str],
    ) -> Tuple[
        float,
        Set[str],
        Set[str],
    ]:

        job_keywords = {
            self.canonicalize(k)
            for k in job_keywords
        }

        resume_keywords = {
            self.canonicalize(k)
            for k in resume_keywords
        }

        matched = (
            job_keywords &
            resume_keywords
        )

        missing = (
            job_keywords -
            resume_keywords
        )

        if not job_keywords:
            return 100.0, matched, missing

        score = (
            len(matched) /
            len(job_keywords)
        ) * 100

        return (
            round(score, 2),
            matched,
            missing,
        )

    # ========================================================
    # Relevance Score
    # ========================================================

    def calculate_relevance(
        self,
        matched_keywords: Set[str],
        job_keywords: Set[str],
    ) -> float:

        if not job_keywords:
            return 100.0

        score = 0.0

        for keyword in matched_keywords:

            category = self.get_category(
                keyword
            )

            if category in {
                "programming",
                "backend",
                "frontend",
                "ai_ml",
                "database",
                "cloud",
                "devops",
                "architecture",
            }:

                score += 1.0

            elif category in {
                "data",
                "analytics",
                "professional",
            }:

                score += 0.9

            elif category == "soft_skills":

                score += 0.6

            else:

                score += 0.5

        return round(
            score /
            len(job_keywords)
            * 100,
            2,
        )

    # ========================================================
    # Section Detection
    # ========================================================

    def detect_sections(
        self,
        resume_text: str,
    ) -> Dict[str, Tuple[int, int]]:

        lines = resume_text.splitlines()

        sections = {}

        current_section = None
        current_start = 0

        position = 0

        for line in lines:

            normalized = self.normalize(
                line
            ).strip(" :-")

            detected = None

            for section, headings in (
                self.SECTIONS.items()
            ):

                if normalized in {
                    self.normalize(h)
                    for h in headings
                }:

                    detected = section
                    break

            if detected:

                if current_section is not None:

                    sections[
                        current_section
                    ] = (
                        current_start,
                        position,
                    )

                current_section = detected
                current_start = position

            position += len(line) + 1

        if current_section is not None:

            sections[
                current_section
            ] = (
                current_start,
                len(resume_text),
            )

        return sections

    # ========================================================
    # Keyword Placement
    # ========================================================

    def find_keyword_placement(
        self,
        resume_text: str,
        keyword: str,
    ) -> str:

        sections = self.detect_sections(
            resume_text
        )

        normalized = self.normalize(
            resume_text
        )

        keyword = self.canonicalize(
            keyword
        )

        variants = {
            keyword
        }

        for alias, target in (
            self.ALIASES.items()
        ):

            if target == keyword:
                variants.add(alias)

        # Search section-by-section.
        for section, (
            start,
            end,
        ) in sections.items():

            content = self.normalize(
                resume_text[start:end]
            )

            for variant in variants:

                if re.search(
                    rf"(?<![a-zA-Z0-9])"
                    rf"{re.escape(variant)}"
                    rf"(?![a-zA-Z0-9])",
                    content,
                    flags=re.IGNORECASE,
                ):

                    return section

        # Fallback.
        for variant in variants:

            if variant in normalized:
                return "other"

        return "missing"

    # ========================================================
    # Distribution Score
    # ========================================================

    def calculate_distribution_score(
        self,
        resume_text: str,
        matched_keywords: Set[str],
    ) -> float:

        if not matched_keywords:
            return 0.0

        sections = self.detect_sections(
            resume_text
        )

        if not sections:
            return 50.0

        useful_sections = {
            "summary",
            "skills",
            "experience",
            "projects",
            "education",
        }

        detected = 0

        for keyword in matched_keywords:

            placement = (
                self.find_keyword_placement(
                    resume_text,
                    keyword,
                )
            )

            if placement in useful_sections:
                detected += 1

        return round(
            detected /
            len(matched_keywords)
            * 100,
            2,
        )

    # ========================================================
    # Keyword Stuffing Detection
    # ========================================================

    def detect_keyword_stuffing(
        self,
        resume_text: str,
        keywords: Set[str],
    ) -> Tuple[bool, float]:

        frequencies = self.keyword_frequency(
            resume_text,
            keywords,
        )

        words = re.findall(
            r"\b\w+\b",
            resume_text.lower(),
        )

        word_count = len(words)

        if word_count == 0:
            return False, 100.0

        total_keyword_occurrences = sum(
            frequencies.values()
        )

        density = (
            total_keyword_occurrences /
            word_count
        )

        # Excessive keyword density.
        if density >= 0.15:

            return True, 20.0

        if density >= 0.10:

            return True, 45.0

        if density >= 0.07:

            return True, 70.0

        return False, 100.0

    # ========================================================
    # Keyword Match Objects
    # ========================================================

    def build_keyword_matches(
        self,
        resume_text: str,
        matched_keywords: Set[str],
    ) -> List[KeywordMatch]:

        frequencies = self.keyword_frequency(
            resume_text,
            matched_keywords,
        )

        results = []

        for keyword in sorted(
            matched_keywords
        ):

            frequency = frequencies.get(
                keyword,
                0,
            )

            placement = (
                self.find_keyword_placement(
                    resume_text,
                    keyword,
                )
            )

            if frequency >= 1:

                relevance = min(
                    100.0,
                    70.0 +
                    frequency * 5,
                )

            else:

                relevance = 0.0

            results.append(
                KeywordMatch(
                    keyword=keyword,
                    category=self.get_category(
                        keyword
                    ),
                    occurrences=frequency,
                    placement=placement,
                    relevance=round(
                        relevance,
                        2,
                    ),
                )
            )

        return results

    # ========================================================
    # Suggestions
    # ========================================================

    def generate_suggestions(
        self,
        missing_keywords: Set[str],
        resume_text: str,
    ) -> List[KeywordSuggestion]:

        suggestions = []

        for keyword in sorted(
            missing_keywords
        ):

            category = self.get_category(
                keyword
            )

            if category in {
                "programming",
                "frontend",
                "backend",
                "database",
                "ai_ml",
                "data",
                "cloud",
                "devops",
                "architecture",
            }:

                section = "skills"

                reason = (
                    "Add this keyword to the Skills section "
                    "if it accurately represents your capabilities; "
                    "also mention it in relevant experience or "
                    "project bullets when supported."
                )

                priority = "high"

            elif category == "soft_skills":

                section = "experience"

                reason = (
                    "Demonstrate this skill through a concrete "
                    "experience or achievement rather than "
                    "listing it without evidence."
                )

                priority = "low"

            else:

                section = "experience"

                reason = (
                    "Mention this keyword in relevant experience, "
                    "projects, or summary content when truthful."
                )

                priority = "medium"

            suggestions.append(
                KeywordSuggestion(
                    keyword=keyword,
                    category=category,
                    priority=priority,
                    suggested_section=section,
                    reason=reason,
                )
            )

        return suggestions

    # ========================================================
    # Recommendations
    # ========================================================

    def generate_recommendations(
        self,
        coverage_score: float,
        relevance_score: float,
        distribution_score: float,
        stuffing_detected: bool,
        missing_keywords: Set[str],
    ) -> List[str]:

        recommendations = []

        if coverage_score < 70:

            recommendations.append(
                "Increase relevant keyword coverage by "
                "naturally reflecting job requirements that "
                "you genuinely meet."
            )

        if relevance_score < 70:

            recommendations.append(
                "Prioritize technical and role-specific keywords "
                "over generic buzzwords."
            )

        if distribution_score < 70:

            recommendations.append(
                "Distribute important keywords naturally across "
                "the Summary, Skills, Experience, and Projects "
                "sections where appropriate."
            )

        if stuffing_detected:

            recommendations.append(
                "Reduce repeated keyword usage. ATS optimization "
                "should focus on relevance and evidence rather "
                "than keyword repetition."
            )

        if missing_keywords:

            recommendations.append(
                "Only add missing keywords when they accurately "
                "describe your actual skills, experience, projects, "
                "education, or certifications."
            )

        if not recommendations:

            recommendations.append(
                "Keyword alignment is strong. Keep keyword usage "
                "natural and evidence-based."
            )

        return recommendations

    # ========================================================
    # Main Optimization
    # ========================================================

    def optimize(
        self,
        resume_text: str,
        job_description: str,
    ) -> KeywordOptimizationResult:

        if not resume_text.strip():

            raise ValueError(
                "Resume text cannot be empty."
            )

        if not job_description.strip():

            raise ValueError(
                "Job description cannot be empty."
            )

        # Extract keywords.
        job_keywords = (
            self.extract_job_keywords(
                job_description
            )
        )

        resume_keywords = (
            self.extract_resume_keywords(
                resume_text
            )
        )

        # Coverage.
        (
            coverage_score,
            matched_keywords,
            missing_keywords,
        ) = self.calculate_coverage(
            job_keywords,
            resume_keywords,
        )

        # Relevance.
        relevance_score = (
            self.calculate_relevance(
                matched_keywords,
                job_keywords,
            )
        )

        # Distribution.
        distribution_score = (
            self.calculate_distribution_score(
                resume_text,
                matched_keywords,
            )
        )

        # Keyword stuffing.
        (
            stuffing_detected,
            stuffing_score,
        ) = self.detect_keyword_stuffing(
            resume_text,
            resume_keywords,
        )

        # Keyword match details.
        keyword_matches = (
            self.build_keyword_matches(
                resume_text,
                matched_keywords,
            )
        )

        # Frequency.
        keyword_frequency = (
            self.keyword_frequency(
                resume_text,
                resume_keywords,
            )
        )

        # Suggestions.
        suggestions = (
            self.generate_suggestions(
                missing_keywords,
                resume_text,
            )
        )

        # Overall keyword score.
        total_score = (
            coverage_score *
            self.weights["coverage"]
            +
            relevance_score *
            self.weights["relevance"]
            +
            distribution_score *
            self.weights["distribution"]
            +
            stuffing_score *
            self.weights["stuffing"]
        )

        # Category grouping.
        categories = {}

        for keyword in sorted(
            resume_keywords
        ):

            category = self.get_category(
                keyword
            )

            categories.setdefault(
                category,
                [],
            ).append(keyword)

        recommendations = (
            self.generate_recommendations(
                coverage_score=coverage_score,
                relevance_score=relevance_score,
                distribution_score=distribution_score,
                stuffing_detected=stuffing_detected,
                missing_keywords=missing_keywords,
            )
        )

        return KeywordOptimizationResult(
            keyword_score=round(
                total_score,
                2,
            ),

            coverage_score=coverage_score,

            relevance_score=relevance_score,

            distribution_score=distribution_score,

            stuffing_score=stuffing_score,

            total_keywords=len(
                job_keywords
            ),

            matched_keywords=len(
                matched_keywords
            ),

            missing_keywords=len(
                missing_keywords
            ),

            matched_keywords_list=sorted(
                matched_keywords
            ),

            missing_keywords_list=sorted(
                missing_keywords
            ),

            keyword_matches=keyword_matches,

            suggestions=suggestions,

            keyword_frequency=keyword_frequency,

            categories=categories,

            stuffing_detected=stuffing_detected,

            recommendations=recommendations,
        )


# ============================================================
# Helper Function
# ============================================================

def optimize_resume_keywords(
    resume_text: str,
    job_description: str,
) -> Dict:

    optimizer = KeywordOptimizer()

    result = optimizer.optimize(
        resume_text=resume_text,
        job_description=job_description,
    )

    return result.to_dict()


# ============================================================
# Example
# ============================================================

if __name__ == "__main__":

    resume = """
    JOHN DOE

    Professional Summary

    Software Engineer with 4 years of experience
    developing backend applications using Python,
    FastAPI and SQL.

    Skills

    Python
    FastAPI
    SQL
    PostgreSQL
    Docker
    Git
    AWS

    Experience

    Software Engineer
    ABC Technologies

    - Developed REST API services using Python and FastAPI.
    - Optimized PostgreSQL database queries.
    - Deployed applications using Docker and AWS.
    - Collaborated with engineering teams to deliver
      scalable backend systems.

    Projects

    AI Resume Screening System
    - Built a machine learning application using Python.
    """

    job_description = """
    Machine Learning Engineer

    Requirements:

    - Python
    - Machine Learning
    - Deep Learning
    - FastAPI
    - SQL
    - PostgreSQL
    - Docker
    - REST API
    - AWS

    Preferred:

    - PyTorch
    - Kubernetes
    - Generative AI
    - NLP

    Experience with scalable backend systems,
    cloud deployment and CI/CD is preferred.
    """

    optimizer = KeywordOptimizer()

    result = optimizer.optimize(
        resume_text=resume,
        job_description=job_description,
    )

    print("=" * 70)
    print("KEYWORD OPTIMIZATION REPORT")
    print("=" * 70)

    print(
        f"\nKeyword Score       : "
        f"{result.keyword_score}%"
    )

    print(
        f"Coverage Score      : "
        f"{result.coverage_score}%"
    )

    print(
        f"Relevance Score     : "
        f"{result.relevance_score}%"
    )

    print(
        f"Distribution Score  : "
        f"{result.distribution_score}%"
    )

    print(
        f"Anti-Stuffing Score : "
        f"{result.stuffing_score}%"
    )

    print(
        f"\nJob Keywords        : "
        f"{result.total_keywords}"
    )

    print(
        f"Matched Keywords    : "
        f"{result.matched_keywords}"
    )

    print(
        f"Missing Keywords    : "
        f"{result.missing_keywords}"
    )

    print("\n" + "=" * 70)
    print("MATCHED KEYWORDS")
    print("=" * 70)

    for keyword in result.matched_keywords_list:
        print(f"  ✓ {keyword}")

    print("\n" + "=" * 70)
    print("MISSING KEYWORDS")
    print("=" * 70)

    for keyword in result.missing_keywords_list:
        print(f"  ✗ {keyword}")

    print("\n" + "=" * 70)
    print("KEYWORD DETAILS")
    print("=" * 70)

    for match in result.keyword_matches:

        print(
            f"\n{match.keyword}"
        )

        print(
            f"  Category    : "
            f"{match.category}"
        )

        print(
            f"  Occurrences : "
            f"{match.occurrences}"
        )

        print(
            f"  Placement   : "
            f"{match.placement}"
        )

        print(
            f"  Relevance   : "
            f"{match.relevance}%"
        )

    print("\n" + "=" * 70)
    print("SUGGESTIONS")
    print("=" * 70)

    for suggestion in result.suggestions:

        print(
            f"\n[{suggestion.priority.upper()}] "
            f"{suggestion.keyword}"
        )

        print(
            f"  Category : "
            f"{suggestion.category}"
        )

        print(
            f"  Section  : "
            f"{suggestion.suggested_section}"
        )

        print(
            f"  Reason   : "
            f"{suggestion.reason}"
        )

    print("\n" + "=" * 70)
    print("KEYWORD FREQUENCY")
    print("=" * 70)

    for keyword, count in sorted(
        result.keyword_frequency.items()
    ):

        print(
            f"  {keyword:35} {count}"
        )

    print("\n" + "=" * 70)
    print("CATEGORIES")
    print("=" * 70)

    for category, keywords in (
        result.categories.items()
    ):

        print(
            f"\n{category.upper()}:"
        )

        for keyword in keywords:
            print(f"  • {keyword}")

    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)

    for recommendation in result.recommendations:
        print(
            f"  → {recommendation}"
        )

    print("\n" + "=" * 70)

    print(
        "Keyword stuffing detected: "
        f"{result.stuffing_detected}"
    )