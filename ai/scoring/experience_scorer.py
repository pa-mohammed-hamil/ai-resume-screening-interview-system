"""
experience_scorer.py

Experience compatibility scoring for an AI Resume Screening System.

Features:
- Extract total years of experience
- Detect required years from a job description
- Detect job roles/titles
- Match relevant experience
- Match experience-related technologies
- Handle partial experience
- Produce explainable scoring and recommendations

Output score: 0-100
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Set


# ============================================================
# Data Models
# ============================================================

@dataclass
class ExperienceRecord:
    title: str
    company: Optional[str]
    years: float
    description: str = ""


@dataclass
class ExperienceScore:
    total_score: float

    years_score: float
    role_score: float
    relevance_score: float
    technology_score: float

    candidate_years: float
    required_years: float

    candidate_roles: List[str]
    required_roles: List[str]

    matched_roles: List[str]
    missing_roles: List[str]

    matched_technologies: List[str]
    missing_technologies: List[str]

    recommendations: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================
# Experience Scorer
# ============================================================

class ExperienceScorer:
    """
    Calculates candidate experience compatibility.

    Default weighting:

        Years of experience -> 40%
        Role similarity     -> 25%
        Experience relevance-> 20%
        Technology match    -> 15%

    Final score: 0-100
    """

    WEIGHTS = {
        "years": 0.40,
        "role": 0.25,
        "relevance": 0.20,
        "technology": 0.15,
    }

    # --------------------------------------------------------
    # Known Job Roles
    # --------------------------------------------------------

    JOB_ROLES = {
        "software engineer",
        "software developer",
        "senior software engineer",
        "junior software engineer",
        "backend developer",
        "backend engineer",
        "frontend developer",
        "frontend engineer",
        "full stack developer",
        "full stack engineer",

        "python developer",
        "java developer",
        "javascript developer",

        "data scientist",
        "data analyst",
        "data engineer",
        "machine learning engineer",
        "ml engineer",
        "ai engineer",
        "ai developer",

        "devops engineer",
        "cloud engineer",
        "site reliability engineer",
        "sre",

        "product manager",
        "project manager",
        "business analyst",

        "database administrator",
        "system administrator",

        "qa engineer",
        "test engineer",
        "automation engineer",

        "cybersecurity engineer",
        "security engineer",

        "research scientist",
        "research engineer",
    }

    # --------------------------------------------------------
    # Technology / Skill Vocabulary
    # --------------------------------------------------------

    TECHNOLOGIES = {
        "python",
        "java",
        "javascript",
        "typescript",
        "c",
        "c++",
        "c#",
        "sql",

        "react",
        "angular",
        "vue",
        "node.js",
        "node",

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

        "tensorflow",
        "pytorch",
        "scikit-learn",

        "pandas",
        "numpy",

        "docker",
        "kubernetes",

        "aws",
        "azure",
        "gcp",

        "mysql",
        "postgresql",
        "mongodb",
        "redis",

        "git",
        "github",
        "linux",

        "rest api",
        "graphql",
        "microservices",

        "jenkins",
        "ci/cd",
    }

    # --------------------------------------------------------
    # Role Aliases
    # --------------------------------------------------------

    ROLE_ALIASES = {
        "software engineer": {
            "software engineer",
            "software developer",
            "application developer",
        },

        "backend developer": {
            "backend developer",
            "backend engineer",
            "server-side developer",
        },

        "frontend developer": {
            "frontend developer",
            "frontend engineer",
            "ui developer",
            "web developer",
        },

        "full stack developer": {
            "full stack developer",
            "full-stack developer",
            "full stack engineer",
            "full-stack engineer",
        },

        "data scientist": {
            "data scientist",
            "data science",
        },

        "data analyst": {
            "data analyst",
            "business data analyst",
        },

        "data engineer": {
            "data engineer",
            "data engineering",
        },

        "machine learning engineer": {
            "machine learning engineer",
            "ml engineer",
            "machine learning developer",
        },

        "ai engineer": {
            "ai engineer",
            "artificial intelligence engineer",
            "ai developer",
        },

        "devops engineer": {
            "devops engineer",
            "devops developer",
            "devops specialist",
        },

        "cloud engineer": {
            "cloud engineer",
            "cloud developer",
            "cloud architect",
        },

        "qa engineer": {
            "qa engineer",
            "quality assurance engineer",
            "test engineer",
        },

        "product manager": {
            "product manager",
            "product owner",
        },

        "project manager": {
            "project manager",
            "program manager",
        },
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
                f"Experience weights must sum to 1.0. "
                f"Got {total:.3f}"
            )

    # ========================================================
    # Text Utilities
    # ========================================================

    @staticmethod
    def normalize(text: str) -> str:

        if not text:
            return ""

        text = text.lower()

        text = text.replace("–", "-")
        text = text.replace("—", "-")

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    # ========================================================
    # Extract Years
    # ========================================================

    def extract_years(
        self,
        text: str,
    ) -> float:
        """
        Extract years of professional experience.

        Examples:

            5 years experience
            3+ years of experience
            2 yrs experience
            4.5 years experience
        """

        if not text:
            return 0.0

        text = self.normalize(text)

        patterns = [
            r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience",

            r"experience\s*(?:of)?\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",

            r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+in",

            r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
        ]

        values = []

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            for value in matches:

                try:
                    values.append(float(value))
                except (TypeError, ValueError):
                    continue

        if not values:
            return 0.0

        return max(values)

    # ========================================================
    # Extract Date Ranges
    # ========================================================

    def extract_date_ranges(
        self,
        text: str,
    ) -> List[float]:
        """
        Estimate experience from employment date ranges.

        Example:

            Jan 2020 - Mar 2023
            2021 - Present
        """

        text = self.normalize(text)

        ranges = []

        pattern = (
            r"\b"
            r"(20\d{2}|19\d{2})"
            r"\s*[-–]\s*"
            r"(20\d{2}|19\d{2}|present|current)"
        )

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        for start, end in matches:

            start_year = int(start)

            if end.lower() in {
                "present",
                "current",
            }:
                end_year = 2026
            else:
                end_year = int(end)

            if end_year >= start_year:

                years = end_year - start_year

                if years > 0:
                    ranges.append(float(years))

        return ranges

    # ========================================================
    # Total Experience
    # ========================================================

    def calculate_total_experience(
        self,
        text: str,
    ) -> float:
        """
        Calculate total experience.

        First checks explicit statements such as
        '5 years of experience'.

        Falls back to employment date ranges.
        """

        explicit_years = self.extract_years(text)

        if explicit_years > 0:
            return explicit_years

        ranges = self.extract_date_ranges(text)

        if not ranges:
            return 0.0

        # Avoid double counting overlapping roles.
        total = sum(ranges)

        return round(total, 2)

    # ========================================================
    # Role Detection
    # ========================================================

    def extract_roles(
        self,
        text: str,
    ) -> Set[str]:

        normalized = self.normalize(text)

        roles = set()

        for role in self.JOB_ROLES:

            pattern = (
                rf"(?<![a-z])"
                rf"{re.escape(role)}"
                rf"(?![a-z])"
            )

            if re.search(
                pattern,
                normalized,
            ):
                roles.add(role)

        return roles

    # ========================================================
    # Canonical Role
    # ========================================================

    def canonical_role(
        self,
        role: str,
    ) -> str:

        role = self.normalize(role)

        for canonical, aliases in self.ROLE_ALIASES.items():

            if role in aliases:
                return canonical

        return role

    # ========================================================
    # Role Matching
    # ========================================================

    def match_roles(
        self,
        candidate_roles: Set[str],
        required_roles: Set[str],
    ):
        """
        Match candidate roles with required roles.
        """

        candidate_canonical = {
            self.canonical_role(role)
            for role in candidate_roles
        }

        required_canonical = {
            self.canonical_role(role)
            for role in required_roles
        }

        matched = (
            candidate_canonical &
            required_canonical
        )

        missing = (
            required_canonical -
            candidate_canonical
        )

        return matched, missing

    # ========================================================
    # Role Score
    # ========================================================

    def calculate_role_score(
        self,
        candidate_roles: Set[str],
        required_roles: Set[str],
    ) -> float:

        if not required_roles:
            return 100.0

        matched, _ = self.match_roles(
            candidate_roles,
            required_roles,
        )

        required_count = len(
            {
                self.canonical_role(role)
                for role in required_roles
            }
        )

        if required_count == 0:
            return 100.0

        return round(
            len(matched) /
            required_count *
            100,
            2,
        )

    # ========================================================
    # Technology Extraction
    # ========================================================

    def extract_technologies(
        self,
        text: str,
    ) -> Set[str]:

        normalized = self.normalize(text)

        technologies = set()

        for technology in self.TECHNOLOGIES:

            pattern = (
                rf"(?<![a-z0-9])"
                rf"{re.escape(technology)}"
                rf"(?![a-z0-9])"
            )

            if re.search(
                pattern,
                normalized,
            ):
                technologies.add(
                    technology
                )

        return technologies

    # ========================================================
    # Technology Matching
    # ========================================================

    def calculate_technology_score(
        self,
        resume_text: str,
        job_description: str,
    ):
        candidate_tech = self.extract_technologies(
            resume_text
        )

        required_tech = self.extract_technologies(
            job_description
        )

        if not required_tech:
            return (
                100.0,
                candidate_tech,
                set(),
            )

        matched = (
            candidate_tech &
            required_tech
        )

        missing = (
            required_tech -
            candidate_tech
        )

        score = (
            len(matched) /
            len(required_tech)
            * 100
        )

        return (
            round(score, 2),
            matched,
            missing,
        )

    # ========================================================
    # Experience Relevance
    # ========================================================

    def calculate_relevance_score(
        self,
        resume_text: str,
        job_description: str,
    ) -> float:

        resume_technologies = (
            self.extract_technologies(
                resume_text
            )
        )

        job_technologies = (
            self.extract_technologies(
                job_description
            )
        )

        resume_roles = (
            self.extract_roles(
                resume_text
            )
        )

        job_roles = (
            self.extract_roles(
                job_description
            )
        )

        signals = []

        # Role signal
        if job_roles:

            role_score = (
                self.calculate_role_score(
                    resume_roles,
                    job_roles,
                )
            )

            signals.append(
                role_score
            )

        # Technology signal
        if job_technologies:

            matched = (
                resume_technologies &
                job_technologies
            )

            tech_score = (
                len(matched) /
                len(job_technologies)
                * 100
            )

            signals.append(
                tech_score
            )

        if not signals:
            return 100.0

        return round(
            sum(signals) /
            len(signals),
            2,
        )

    # ========================================================
    # Years Score
    # ========================================================

    def calculate_years_score(
        self,
        candidate_years: float,
        required_years: float,
    ) -> float:

        if required_years <= 0:
            return 100.0

        if candidate_years >= required_years:
            return 100.0

        if candidate_years <= 0:
            return 0.0

        score = (
            candidate_years /
            required_years *
            100
        )

        return round(
            min(score, 100.0),
            2,
        )

    # ========================================================
    # Recommendations
    # ========================================================

    def generate_recommendations(
        self,
        candidate_years: float,
        required_years: float,
        years_score: float,
        role_score: float,
        relevance_score: float,
        technology_score: float,
        missing_roles: Set[str],
        missing_technologies: Set[str],
    ) -> List[str]:

        recommendations = []

        # Years
        if (
            required_years > 0
            and candidate_years < required_years
        ):
            recommendations.append(
                f"The role requests approximately "
                f"{required_years:g}+ years of experience. "
                f"Clearly highlight all relevant experience."
            )

        # Roles
        if missing_roles:
            roles = ", ".join(
                sorted(missing_roles)
            )

            recommendations.append(
                f"Highlight experience relevant to: {roles}."
            )

        # Technologies
        if missing_technologies:
            technologies = ", ".join(
                sorted(missing_technologies)[:10]
            )

            recommendations.append(
                f"If genuinely experienced, mention relevant "
                f"technologies such as: {technologies}."
            )

        # Relevance
        if relevance_score < 70:
            recommendations.append(
                "Rewrite experience bullets to emphasize "
                "achievements and responsibilities directly "
                "related to the target role."
            )

        # Quantifiable achievements
        if not re.search(
            r"\b\d+%|\b\d+\+|\$\d+|\b\d+\s*(?:users|projects|clients|teams)\b",
            self.normalize(""),
        ):
            # Do not fabricate achievements.
            recommendations.append(
                "Where truthful, add measurable outcomes "
                "to experience bullet points."
            )

        if not recommendations:
            recommendations.append(
                "Professional experience appears strongly "
                "aligned with the job requirements."
            )

        return recommendations

    # ========================================================
    # Main Calculation
    # ========================================================

    def calculate(
        self,
        resume_text: str,
        job_description: str,
    ) -> ExperienceScore:

        if not resume_text.strip():
            raise ValueError(
                "Resume text cannot be empty."
            )

        if not job_description.strip():
            raise ValueError(
                "Job description cannot be empty."
            )

        # Candidate experience
        candidate_years = (
            self.calculate_total_experience(
                resume_text
            )
        )

        # Required experience
        required_years = (
            self.extract_years(
                job_description
            )
        )

        # Roles
        candidate_roles = (
            self.extract_roles(
                resume_text
            )
        )

        required_roles = (
            self.extract_roles(
                job_description
            )
        )

        matched_roles, missing_roles = (
            self.match_roles(
                candidate_roles,
                required_roles,
            )
        )

        # Scores
        years_score = (
            self.calculate_years_score(
                candidate_years,
                required_years,
            )
        )

        role_score = (
            self.calculate_role_score(
                candidate_roles,
                required_roles,
            )
        )

        relevance_score = (
            self.calculate_relevance_score(
                resume_text,
                job_description,
            )
        )

        (
            technology_score,
            matched_technologies,
            missing_technologies,
        ) = self.calculate_technology_score(
            resume_text,
            job_description,
        )

        # Weighted total
        total_score = (
            years_score *
            self.weights["years"]
            +
            role_score *
            self.weights["role"]
            +
            relevance_score *
            self.weights["relevance"]
            +
            technology_score *
            self.weights["technology"]
        )

        recommendations = (
            self.generate_recommendations(
                candidate_years,
                required_years,
                years_score,
                role_score,
                relevance_score,
                technology_score,
                missing_roles,
                missing_technologies,
            )
        )

        return ExperienceScore(
            total_score=round(
                total_score,
                2,
            ),

            years_score=years_score,
            role_score=role_score,
            relevance_score=relevance_score,
            technology_score=technology_score,

            candidate_years=candidate_years,
            required_years=required_years,

            candidate_roles=sorted(
                candidate_roles
            ),

            required_roles=sorted(
                required_roles
            ),

            matched_roles=sorted(
                matched_roles
            ),

            missing_roles=sorted(
                missing_roles
            ),

            matched_technologies=sorted(
                matched_technologies
            ),

            missing_technologies=sorted(
                missing_technologies
            ),

            recommendations=recommendations,
        )


# ============================================================
# Example
# ============================================================

if __name__ == "__main__":

    resume = """
    JOHN DOE

    Professional Summary:
    Machine Learning Engineer with 5 years of experience
    building production AI applications.

    Experience:

    Senior Machine Learning Engineer
    ABC Technologies
    2021 - Present

    Developed machine learning systems using Python,
    PyTorch, TensorFlow and FastAPI.

    Software Engineer
    XYZ Solutions
    2019 - 2021

    Built backend services using Python, Django,
    PostgreSQL and Docker.

    Education:
    B.Tech Computer Science
    """

    job_description = """
    Machine Learning Engineer

    We are looking for a Machine Learning Engineer with
    3+ years of experience.

    Requirements:

    - Experience with machine learning
    - Python programming
    - PyTorch or TensorFlow
    - FastAPI
    - Docker
    - AWS
    - Experience building AI applications
    """

    scorer = ExperienceScorer()

    result = scorer.calculate(
        resume_text=resume,
        job_description=job_description,
    )

    print("=" * 65)
    print("EXPERIENCE COMPATIBILITY SCORE")
    print("=" * 65)

    print(
        f"Overall Score      : {result.total_score}%"
    )

    print(
        f"Years Score         : {result.years_score}%"
    )

    print(
        f"Role Score          : {result.role_score}%"
    )

    print(
        f"Relevance Score     : {result.relevance_score}%"
    )

    print(
        f"Technology Score    : {result.technology_score}%"
    )

    print("\nExperience:")

    print(
        f"  Candidate: "
        f"{result.candidate_years:g} years"
    )

    print(
        f"  Required : "
        f"{result.required_years:g} years"
    )

    print("\nMatched Roles:")

    for role in result.matched_roles:
        print(f"  ✓ {role}")

    print("\nMissing Roles:")

    for role in result.missing_roles:
        print(f"  ✗ {role}")

    print("\nMatched Technologies:")

    for technology in result.matched_technologies:
        print(f"  ✓ {technology}")

    print("\nMissing Technologies:")

    for technology in result.missing_technologies:
        print(f"  ✗ {technology}")

    print("\nRecommendations:")

    for recommendation in result.recommendations:
        print(f"  → {recommendation}")