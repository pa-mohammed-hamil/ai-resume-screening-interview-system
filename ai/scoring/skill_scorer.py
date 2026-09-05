# Project scaffold file
"""
skill_scorer.py

Skill compatibility scoring for an AI Resume Screening System.

Features:
- Extract technical and soft skills
- Normalize skill aliases
- Detect required and preferred skills
- Calculate skill coverage
- Calculate category-wise scores
- Identify matched and missing skills
- Generate recommendations
- Produce explainable 0-100 scoring

Designed to work with:
    resume_parser
    information_extraction
    skill_intelligence
    ats_scorer
    candidate_ranking
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Set


# ============================================================
# Data Models
# ============================================================

@dataclass
class SkillMatch:
    skill: str
    category: str
    importance: str
    matched: bool
    evidence: Optional[str] = None


@dataclass
class SkillScore:
    total_score: float

    required_skill_score: float
    preferred_skill_score: float
    category_score: float

    required_skills: List[str]
    preferred_skills: List[str]

    matched_required_skills: List[str]
    missing_required_skills: List[str]

    matched_preferred_skills: List[str]
    missing_preferred_skills: List[str]

    technical_skills: List[str]
    soft_skills: List[str]

    recommendations: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================
# Skill Scorer
# ============================================================

class SkillScorer:
    """
    Calculates resume-to-job skill compatibility.

    Default weighting:

        Required skills  -> 60%
        Preferred skills -> 20%
        Skill categories -> 20%

    Final score: 0-100
    """

    WEIGHTS = {
        "required": 0.60,
        "preferred": 0.20,
        "category": 0.20,
    }

    # ========================================================
    # Technical Skills
    # ========================================================

    TECHNICAL_SKILLS = {
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

        "sql",
        "nosql",
        "mysql",
        "postgresql",
        "oracle",
        "mongodb",
        "redis",
        "elasticsearch",

        "html",
        "css",
        "sass",
        "tailwind",
        "bootstrap",

        "react",
        "react.js",
        "angular",
        "vue",
        "vue.js",
        "next.js",
        "nextjs",

        "node",
        "node.js",
        "express",
        "express.js",

        "django",
        "flask",
        "fastapi",
        "spring",
        "spring boot",

        "machine learning",
        "deep learning",
        "artificial intelligence",
        "nlp",
        "natural language processing",
        "computer vision",
        "generative ai",
        "generative artificial intelligence",
        "large language models",
        "llm",
        "transformers",

        "tensorflow",
        "pytorch",
        "keras",
        "scikit-learn",
        "sklearn",

        "pandas",
        "numpy",
        "scipy",
        "matplotlib",

        "docker",
        "kubernetes",
        "terraform",
        "ansible",

        "aws",
        "amazon web services",
        "azure",
        "microsoft azure",
        "gcp",
        "google cloud",

        "git",
        "github",
        "gitlab",
        "bitbucket",

        "linux",
        "unix",

        "rest api",
        "restful api",
        "graphql",
        "grpc",
        "microservices",

        "jenkins",
        "github actions",
        "gitlab ci",
        "ci/cd",

        "apache kafka",
        "kafka",
        "rabbitmq",

        "spark",
        "apache spark",
        "hadoop",

        "power bi",
        "tableau",
        "excel",
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
        "project management",
        "presentation",
        "negotiation",
        "conflict resolution",
        "mentoring",
        "stakeholder management",
        "attention to detail",
        "organization",
        "interpersonal skills",
        "written communication",
        "verbal communication",
    }

    # ========================================================
    # Skill Categories
    # ========================================================

    SKILL_CATEGORIES = {
        "programming": {
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
        },

        "web": {
            "html",
            "css",
            "sass",
            "react",
            "angular",
            "vue",
            "next.js",
            "nextjs",
            "node",
            "node.js",
            "express",
            "express.js",
            "django",
            "flask",
            "fastapi",
        },

        "data": {
            "sql",
            "nosql",
            "mysql",
            "postgresql",
            "oracle",
            "mongodb",
            "redis",
            "elasticsearch",
            "pandas",
            "numpy",
            "scipy",
            "excel",
        },

        "ai_ml": {
            "machine learning",
            "deep learning",
            "artificial intelligence",
            "nlp",
            "natural language processing",
            "computer vision",
            "generative ai",
            "large language models",
            "llm",
            "transformers",
            "tensorflow",
            "pytorch",
            "keras",
            "scikit-learn",
            "sklearn",
        },

        "cloud": {
            "aws",
            "amazon web services",
            "azure",
            "microsoft azure",
            "gcp",
            "google cloud",
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
            "linux",
            "git",
            "github",
            "gitlab",
        },

        "architecture": {
            "rest api",
            "restful api",
            "graphql",
            "grpc",
            "microservices",
            "apache kafka",
            "kafka",
            "rabbitmq",
            "spark",
            "apache spark",
            "hadoop",
        },

        "analytics": {
            "power bi",
            "tableau",
            "excel",
            "sql",
            "pandas",
            "numpy",
        },

        "soft_skills": SOFT_SKILLS,
    }

    # ========================================================
    # Aliases
    # ========================================================

    SKILL_ALIASES = {
        "react.js": "react",
        "reactjs": "react",

        "vue.js": "vue",
        "vuejs": "vue",

        "node.js": "node",
        "nodejs": "node",

        "next.js": "nextjs",

        "express.js": "express",
        "expressjs": "express",

        "golang": "go",

        "sklearn": "scikit-learn",

        "nlp": "natural language processing",

        "ai": "artificial intelligence",
        "ml": "machine learning",

        "genai": "generative ai",
        "gen-ai": "generative ai",

        "llms": "large language models",

        "aws cloud": "aws",
        "amazon web services": "aws",

        "microsoft azure": "azure",

        "google cloud": "gcp",

        "postgres": "postgresql",

        "mongo": "mongodb",

        "restful api": "rest api",

        "problem-solving": "problem solving",
        "decision-making": "decision making",
    }

    # ========================================================
    # Initialization
    # ========================================================

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
    ):
        self.weights = weights or self.WEIGHTS.copy()

        self._validate_weights()

    def _validate_weights(self) -> None:

        total = sum(self.weights.values())

        if abs(total - 1.0) > 0.001:
            raise ValueError(
                "Skill scorer weights must sum to 1.0"
            )

    # ========================================================
    # Text Normalization
    # ========================================================

    @staticmethod
    def normalize(text: str) -> str:

        if not text:
            return ""

        text = text.lower()

        text = text.replace("&", " and ")

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    # ========================================================
    # Canonical Skill
    # ========================================================

    def canonicalize(
        self,
        skill: str,
    ) -> str:

        skill = self.normalize(skill)

        return self.SKILL_ALIASES.get(
            skill,
            skill,
        )

    # ========================================================
    # Skill Category
    # ========================================================

    def get_category(
        self,
        skill: str,
    ) -> str:

        skill = self.canonicalize(skill)

        for category, skills in self.SKILL_CATEGORIES.items():

            canonical_skills = {
                self.canonicalize(s)
                for s in skills
            }

            if skill in canonical_skills:
                return category

        if skill in self.SOFT_SKILLS:
            return "soft_skills"

        if skill in self.TECHNICAL_SKILLS:
            return "technical"

        return "other"

    # ========================================================
    # Extract All Skills
    # ========================================================

    def extract_skills(
        self,
        text: str,
    ) -> Set[str]:

        normalized = self.normalize(text)

        found = set()

        all_skills = (
            self.TECHNICAL_SKILLS |
            self.SOFT_SKILLS
        )

        for skill in all_skills:

            normalized_skill = (
                self.normalize(skill)
            )

            pattern = (
                rf"(?<![a-z0-9])"
                rf"{re.escape(normalized_skill)}"
                rf"(?![a-z0-9])"
            )

            if re.search(
                pattern,
                normalized,
            ):
                found.add(
                    self.canonicalize(skill)
                )

        return found

    # ========================================================
    # Extract Required Skills
    # ========================================================

    def extract_required_skills(
        self,
        job_description: str,
    ) -> Set[str]:

        normalized = self.normalize(
            job_description
        )

        required = set()

        # Look for requirement sections.
        sections = re.split(
            r"\b(?:requirements?|qualifications?|must have|required skills?)\b",
            normalized,
            flags=re.IGNORECASE,
        )

        if len(sections) > 1:

            requirement_text = sections[1]

        else:

            # If no explicit section exists,
            # use the whole JD.
            requirement_text = normalized

        extracted = self.extract_skills(
            requirement_text
        )

        required.update(extracted)

        return required

    # ========================================================
    # Extract Preferred Skills
    # ========================================================

    def extract_preferred_skills(
        self,
        job_description: str,
    ) -> Set[str]:

        normalized = self.normalize(
            job_description
        )

        preferred = set()

        preferred_patterns = [
            r"preferred",
            r"nice to have",
            r"good to have",
            r"bonus",
            r"plus",
            r"desirable",
            r"preferred qualifications",
        ]

        for pattern in preferred_patterns:

            matches = re.finditer(
                pattern,
                normalized,
                flags=re.IGNORECASE,
            )

            for match in matches:

                start = match.start()

                # Take a reasonable local context.
                context = normalized[
                    start:start + 500
                ]

                preferred.update(
                    self.extract_skills(
                        context
                    )
                )

        return preferred

    # ========================================================
    # Required Skill Score
    # ========================================================

    def calculate_required_score(
        self,
        candidate_skills: Set[str],
        required_skills: Set[str],
    ):
        if not required_skills:
            return 100.0, set(), set()

        matched = (
            candidate_skills &
            required_skills
        )

        missing = (
            required_skills -
            candidate_skills
        )

        score = (
            len(matched) /
            len(required_skills) *
            100
        )

        return (
            round(score, 2),
            matched,
            missing,
        )

    # ========================================================
    # Preferred Skill Score
    # ========================================================

    def calculate_preferred_score(
        self,
        candidate_skills: Set[str],
        preferred_skills: Set[str],
    ):
        if not preferred_skills:
            return 100.0, set(), set()

        matched = (
            candidate_skills &
            preferred_skills
        )

        missing = (
            preferred_skills -
            candidate_skills
        )

        score = (
            len(matched) /
            len(preferred_skills) *
            100
        )

        return (
            round(score, 2),
            matched,
            missing,
        )

    # ========================================================
    # Category Score
    # ========================================================

    def calculate_category_score(
        self,
        candidate_skills: Set[str],
        required_skills: Set[str],
    ) -> float:

        if not required_skills:
            return 100.0

        categories = {}

        for skill in required_skills:

            category = self.get_category(
                skill
            )

            categories.setdefault(
                category,
                []
            ).append(skill)

        category_scores = []

        for category, skills in categories.items():

            if not skills:
                continue

            matched = sum(
                1
                for skill in skills
                if skill in candidate_skills
            )

            score = (
                matched /
                len(skills) *
                100
            )

            category_scores.append(
                score
            )

        if not category_scores:
            return 100.0

        return round(
            sum(category_scores) /
            len(category_scores),
            2,
        )

    # ========================================================
    # Skill Classification
    # ========================================================

    def classify_skills(
        self,
        skills: Set[str],
    ):
        technical = set()
        soft = set()

        for skill in skills:

            if (
                skill in
                {
                    self.canonicalize(s)
                    for s in self.SOFT_SKILLS
                }
            ):
                soft.add(skill)

            else:
                technical.add(skill)

        return technical, soft

    # ========================================================
    # Recommendations
    # ========================================================

    def generate_recommendations(
        self,
        missing_required: Set[str],
        missing_preferred: Set[str],
        required_score: float,
        category_score: float,
    ) -> List[str]:

        recommendations = []

        if missing_required:

            skills = ", ".join(
                sorted(
                    missing_required
                )[:10]
            )

            recommendations.append(
                "If you genuinely have these skills, "
                f"make them visible in the resume: {skills}."
            )

        if missing_preferred:

            skills = ", ".join(
                sorted(
                    missing_preferred
                )[:10]
            )

            recommendations.append(
                "Consider highlighting relevant preferred "
                f"skills when supported by your experience: {skills}."
            )

        if required_score < 60:

            recommendations.append(
                "The resume has relatively low required-skill "
                "coverage. Tailor the skills and experience "
                "sections to the target job."
            )

        if category_score < 70:

            recommendations.append(
                "Improve balance across the major skill "
                "categories required by the position."
            )

        if not recommendations:

            recommendations.append(
                "Skill profile is strongly aligned with "
                "the supplied job description."
            )

        return recommendations

    # ========================================================
    # Main Calculation
    # ========================================================

    def calculate(
        self,
        resume_text: str,
        job_description: str,
    ) -> SkillScore:

        if not resume_text.strip():
            raise ValueError(
                "Resume text cannot be empty."
            )

        if not job_description.strip():
            raise ValueError(
                "Job description cannot be empty."
            )

        # Candidate skills
        candidate_skills = (
            self.extract_skills(
                resume_text
            )
        )

        # Job skills
        required_skills = (
            self.extract_required_skills(
                job_description
            )
        )

        preferred_skills = (
            self.extract_preferred_skills(
                job_description
            )
        )

        # Prevent double counting preferred skills.
        preferred_skills -= required_skills

        # Required score
        (
            required_score,
            matched_required,
            missing_required,
        ) = self.calculate_required_score(
            candidate_skills,
            required_skills,
        )

        # Preferred score
        (
            preferred_score,
            matched_preferred,
            missing_preferred,
        ) = self.calculate_preferred_score(
            candidate_skills,
            preferred_skills,
        )

        # Category score
        category_score = (
            self.calculate_category_score(
                candidate_skills,
                required_skills,
            )
        )

        # Overall score
        total_score = (
            required_score *
            self.weights["required"]
            +
            preferred_score *
            self.weights["preferred"]
            +
            category_score *
            self.weights["category"]
        )

        # Classify candidate skills
        technical_skills, soft_skills = (
            self.classify_skills(
                candidate_skills
            )
        )

        # Recommendations
        recommendations = (
            self.generate_recommendations(
                missing_required,
                missing_preferred,
                required_score,
                category_score,
            )
        )

        return SkillScore(
            total_score=round(
                total_score,
                2,
            ),

            required_skill_score=required_score,
            preferred_skill_score=preferred_score,
            category_score=category_score,

            required_skills=sorted(
                required_skills
            ),

            preferred_skills=sorted(
                preferred_skills
            ),

            matched_required_skills=sorted(
                matched_required
            ),

            missing_required_skills=sorted(
                missing_required
            ),

            matched_preferred_skills=sorted(
                matched_preferred
            ),

            missing_preferred_skills=sorted(
                missing_preferred
            ),

            technical_skills=sorted(
                technical_skills
            ),

            soft_skills=sorted(
                soft_skills
            ),

            recommendations=recommendations,
        )


# ============================================================
# Example
# ============================================================

if __name__ == "__main__":

    resume = """
    JOHN DOE

    Skills:
    Python, FastAPI, Django, SQL, PostgreSQL,
    Machine Learning, Deep Learning, PyTorch,
    Docker, AWS, Git, React.

    Experience:
    Machine Learning Engineer with 4 years of experience.

    Developed AI applications using Python and PyTorch.
    Built REST APIs using FastAPI.
    Deployed applications using Docker and AWS.

    Strong communication and teamwork skills.
    """

    job_description = """
    Machine Learning Engineer

    Requirements:
    - 3+ years of experience
    - Python
    - Machine Learning
    - Deep Learning
    - PyTorch
    - SQL
    - FastAPI
    - Docker

    Preferred:
    - AWS
    - Kubernetes
    - React
    - Generative AI

    Strong communication and problem solving skills.
    """

    scorer = SkillScorer()

    result = scorer.calculate(
        resume_text=resume,
        job_description=job_description,
    )

    print("=" * 70)
    print("SKILL COMPATIBILITY SCORE")
    print("=" * 70)

    print(
        f"Overall Score       : "
        f"{result.total_score}%"
    )

    print(
        f"Required Skills     : "
        f"{result.required_skill_score}%"
    )

    print(
        f"Preferred Skills    : "
        f"{result.preferred_skill_score}%"
    )

    print(
        f"Category Score      : "
        f"{result.category_score}%"
    )

    print("\nRequired Skills:")

    for skill in result.required_skills:
        print(f"  • {skill}")

    print("\nMatched Required Skills:")

    for skill in result.matched_required_skills:
        print(f"  ✓ {skill}")

    print("\nMissing Required Skills:")

    for skill in result.missing_required_skills:
        print(f"  ✗ {skill}")

    print("\nPreferred Skills:")

    for skill in result.preferred_skills:
        print(f"  • {skill}")

    print("\nMatched Preferred Skills:")

    for skill in result.matched_preferred_skills:
        print(f"  ✓ {skill}")

    print("\nMissing Preferred Skills:")

    for skill in result.missing_preferred_skills:
        print(f"  ✗ {skill}")

    print("\nTechnical Skills Found:")

    for skill in result.technical_skills:
        print(f"  • {skill}")

    print("\nSoft Skills Found:")

    for skill in result.soft_skills:
        print(f"  • {skill}")

    print("\nRecommendations:")

    for recommendation in result.recommendations:
        print(f"  → {recommendation}")