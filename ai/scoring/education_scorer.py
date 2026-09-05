"""
education_scorer.py

Education compatibility scoring for an AI Resume Screening System.

Features:
- Detects degree level
- Detects degree fields/specializations
- Handles equivalent degree names
- Detects required education from job descriptions
- Scores degree-level compatibility
- Scores field/specialization compatibility
- Produces explainable scoring details
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional


@dataclass
class Education:
    degree_level: str
    degree_name: str
    field: Optional[str]
    institution: Optional[str] = None
    year: Optional[int] = None


@dataclass
class EducationScore:
    total_score: float
    degree_score: float
    field_score: float
    requirement_score: float

    candidate_degree: Optional[str]
    candidate_field: Optional[str]

    required_degree: Optional[str]
    required_field: Optional[str]

    matched_requirements: List[str]
    missing_requirements: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)


class EducationScorer:
    """
    Education scoring engine.

    Score weighting:

        Degree level   -> 50%
        Field match    -> 30%
        Requirements   -> 20%

    Final score is between 0 and 100.
    """

    DEGREE_LEVELS = {
        "high_school": 1,
        "diploma": 2,
        "associate": 3,
        "bachelor": 4,
        "master": 5,
        "mba": 5,
        "mtech": 5,
        "ms": 5,
        "phd": 6,
        "doctorate": 6,
    }

    DEGREE_ALIASES = {
        "bachelor": [
            "bachelor",
            "bachelors",
            "bachelor's",
            "b.tech",
            "btech",
            "b.e",
            "be",
            "b.sc",
            "bsc",
            "bca",
            "bba",
            "undergraduate",
        ],
        "master": [
            "master",
            "masters",
            "master's",
            "m.sc",
            "msc",
            "mca",
            "ma",
            "m.com",
            "mcom",
            "postgraduate",
        ],
        "mba": [
            "mba",
            "master of business administration",
        ],
        "mtech": [
            "m.tech",
            "mtech",
            "master of technology",
        ],
        "ms": [
            "ms",
            "m.s",
            "master of science",
        ],
        "phd": [
            "phd",
            "ph.d",
            "doctorate",
            "doctoral",
            "doctor of philosophy",
        ],
        "diploma": [
            "diploma",
            "polytechnic",
        ],
        "associate": [
            "associate degree",
            "associate's degree",
        ],
        "high_school": [
            "high school",
            "secondary school",
            "12th",
            "higher secondary",
        ],
    }

    FIELD_ALIASES = {
        "computer science": [
            "computer science",
            "cs",
            "computer engineering",
            "computer technology",
        ],
        "information technology": [
            "information technology",
            "information systems",
            "it",
        ],
        "software engineering": [
            "software engineering",
            "software development",
        ],
        "data science": [
            "data science",
            "data analytics",
        ],
        "artificial intelligence": [
            "artificial intelligence",
            "artificial intelligence and machine learning",
            "ai",
        ],
        "machine learning": [
            "machine learning",
            "ml",
        ],
        "electronics": [
            "electronics",
            "electronics engineering",
            "ece",
        ],
        "electrical engineering": [
            "electrical engineering",
            "eee",
        ],
        "mechanical engineering": [
            "mechanical engineering",
            "mechanical",
        ],
        "civil engineering": [
            "civil engineering",
            "civil",
        ],
        "business administration": [
            "business administration",
            "business management",
            "management",
        ],
        "finance": [
            "finance",
            "financial management",
        ],
        "marketing": [
            "marketing",
            "digital marketing",
        ],
    }

    def __init__(
        self,
        degree_weight: float = 0.50,
        field_weight: float = 0.30,
        requirement_weight: float = 0.20,
    ):
        self.weights = {
            "degree": degree_weight,
            "field": field_weight,
            "requirement": requirement_weight,
        }

        self._validate_weights()

    def _validate_weights(self) -> None:
        total = sum(self.weights.values())

        if abs(total - 1.0) > 0.001:
            raise ValueError(
                "Education scorer weights must sum to 1.0"
            )

    @staticmethod
    def normalize(text: str) -> str:
        """Normalize text before matching."""

        if not text:
            return ""

        text = text.lower()

        text = text.replace("&", " and ")

        text = re.sub(
            r"[^a-zA-Z0-9+#.\s'-]",
            " ",
            text,
        )

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # ---------------------------------------------------------
    # Degree Detection
    # ---------------------------------------------------------

    def detect_degree_level(
        self,
        text: str,
    ) -> Optional[str]:
        """
        Detect the highest education level present in text.
        """

        normalized = self.normalize(text)

        detected = []

        for level, aliases in self.DEGREE_ALIASES.items():

            for alias in aliases:

                alias_normalized = self.normalize(alias)

                if alias_normalized in normalized:
                    detected.append(level)
                    break

        if not detected:
            return None

        return max(
            detected,
            key=lambda x: self.DEGREE_LEVELS[x],
        )

    def detect_degree_name(
        self,
        text: str,
    ) -> Optional[str]:
        """Return a human-readable degree name."""

        normalized = self.normalize(text)

        degree_patterns = [
            r"(b\.?tech|btech)",
            r"(b\.?e\.?)",
            r"(b\.?sc|bsc)",
            r"(b\.?ca|bca)",
            r"(b\.?ba|bba)",
            r"(m\.?tech|mtech)",
            r"(m\.?sc|msc)",
            r"(m\.?ca|mca)",
            r"(mba)",
            r"(m\.?s\.?)",
            r"(ph\.?d)",
            r"(bachelor(?:'s)? degree)",
            r"(master(?:'s)? degree)",
            r"(associate degree)",
            r"(diploma)",
        ]

        for pattern in degree_patterns:

            match = re.search(
                pattern,
                normalized,
                flags=re.IGNORECASE,
            )

            if match:
                return match.group(1)

        level = self.detect_degree_level(text)

        return level

    # ---------------------------------------------------------
    # Field Detection
    # ---------------------------------------------------------

    def detect_field(
        self,
        text: str,
    ) -> Optional[str]:
        """Detect specialization/major."""

        normalized = self.normalize(text)

        detected = []

        for field, aliases in self.FIELD_ALIASES.items():

            for alias in aliases:

                alias_normalized = self.normalize(alias)

                pattern = (
                    rf"(?<![a-z])"
                    rf"{re.escape(alias_normalized)}"
                    rf"(?![a-z])"
                )

                if re.search(pattern, normalized):
                    detected.append(field)
                    break

        if not detected:
            return None

        # Prefer more specific fields.
        priority = {
            "artificial intelligence": 10,
            "machine learning": 9,
            "data science": 8,
            "computer science": 7,
            "software engineering": 6,
            "information technology": 5,
        }

        return max(
            detected,
            key=lambda x: priority.get(x, 1),
        )

    # ---------------------------------------------------------
    # Education Extraction
    # ---------------------------------------------------------

    def extract_education(
        self,
        text: str,
    ) -> Education:

        degree_level = self.detect_degree_level(text)

        degree_name = self.detect_degree_name(text)

        field = self.detect_field(text)

        year = None

        years = re.findall(
            r"\b(19\d{2}|20\d{2})\b",
            text,
        )

        if years:
            year = max(int(y) for y in years)

        institution = self.extract_institution(text)

        return Education(
            degree_level=degree_level or "unknown",
            degree_name=degree_name or "unknown",
            field=field,
            institution=institution,
            year=year,
        )

    def extract_institution(
        self,
        text: str,
    ) -> Optional[str]:
        """
        Basic institution extraction.

        A production system can replace this with NER.
        """

        patterns = [
            r"(?:university|college|institute)\s+of\s+[A-Za-z ]+",
            r"[A-Za-z ]+\s+(?:university|college|institute)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            if match:
                return match.group(0).strip()

        return None

    # ---------------------------------------------------------
    # Required Education Detection
    # ---------------------------------------------------------

    def extract_required_education(
        self,
        job_description: str,
    ) -> Education:

        degree_level = self.detect_degree_level(
            job_description
        )

        degree_name = self.detect_degree_name(
            job_description
        )

        field = self.detect_field(
            job_description
        )

        return Education(
            degree_level=degree_level or "unknown",
            degree_name=degree_name or "unknown",
            field=field,
        )

    # ---------------------------------------------------------
    # Degree Score
    # ---------------------------------------------------------

    def calculate_degree_score(
        self,
        candidate: Education,
        required: Education,
    ) -> float:

        candidate_level = self.DEGREE_LEVELS.get(
            candidate.degree_level,
            0,
        )

        required_level = self.DEGREE_LEVELS.get(
            required.degree_level,
            0,
        )

        # No explicit degree requirement.
        if required_level == 0:
            return 100.0

        # Candidate exceeds requirement.
        if candidate_level >= required_level:
            return 100.0

        if candidate_level == 0:
            return 0.0

        # Partial credit.
        score = (
            candidate_level /
            required_level
        ) * 100

        return round(score, 2)

    # ---------------------------------------------------------
    # Field Score
    # ---------------------------------------------------------

    def calculate_field_score(
        self,
        candidate: Education,
        required: Education,
    ) -> float:

        # No required field.
        if not required.field:
            return 100.0

        # Candidate has no detected field.
        if not candidate.field:
            return 0.0

        if candidate.field == required.field:
            return 100.0

        # Related technical fields.
        related_fields = {
            "computer science": {
                "information technology",
                "software engineering",
                "data science",
                "artificial intelligence",
                "machine learning",
            },
            "information technology": {
                "computer science",
                "software engineering",
                "data science",
            },
            "software engineering": {
                "computer science",
                "information technology",
            },
            "data science": {
                "computer science",
                "artificial intelligence",
                "machine learning",
                "information technology",
            },
            "artificial intelligence": {
                "computer science",
                "machine learning",
                "data science",
            },
            "machine learning": {
                "artificial intelligence",
                "computer science",
                "data science",
            },
        }

        related = related_fields.get(
            required.field,
            set(),
        )

        if candidate.field in related:
            return 75.0

        return 0.0

    # ---------------------------------------------------------
    # Requirement Score
    # ---------------------------------------------------------

    def calculate_requirement_score(
        self,
        resume_text: str,
        job_description: str,
    ) -> float:

        resume = self.normalize(resume_text)
        job = self.normalize(job_description)

        requirements = []

        requirement_patterns = [
            r"degree",
            r"bachelor",
            r"master",
            r"phd",
            r"doctorate",
            r"diploma",
            r"computer science",
            r"information technology",
            r"engineering",
            r"data science",
            r"artificial intelligence",
            r"machine learning",
            r"relevant field",
        ]

        for pattern in requirement_patterns:

            if re.search(pattern, job):
                requirements.append(pattern)

        if not requirements:
            return 100.0

        matched = 0

        for requirement in requirements:

            if re.search(
                requirement,
                resume,
            ):
                matched += 1

        return round(
            matched / len(requirements) * 100,
            2,
        )

    # ---------------------------------------------------------
    # Recommendations
    # ---------------------------------------------------------

    def generate_recommendations(
        self,
        candidate: Education,
        required: Education,
        degree_score: float,
        field_score: float,
    ) -> List[str]:

        recommendations = []

        if degree_score < 100:

            if candidate.degree_level == "unknown":
                recommendations.append(
                    "Clearly mention your highest educational qualification."
                )

            else:
                recommendations.append(
                    "Highlight any higher or equivalent educational "
                    "qualification relevant to the position."
                )

        if field_score < 100:

            if required.field and not candidate.field:
                recommendations.append(
                    f"Clearly specify your major or specialization. "
                    f"The role prefers {required.field}."
                )

            elif required.field:
                recommendations.append(
                    f"Emphasize coursework or projects related to "
                    f"{required.field}."
                )

        if not recommendations:
            recommendations.append(
                "Education appears well aligned with the job requirements."
            )

        return recommendations

    # ---------------------------------------------------------
    # Main Scoring Function
    # ---------------------------------------------------------

    def calculate(
        self,
        resume_text: str,
        job_description: str,
    ) -> EducationScore:

        if not resume_text.strip():
            raise ValueError(
                "Resume text cannot be empty."
            )

        if not job_description.strip():
            raise ValueError(
                "Job description cannot be empty."
            )

        candidate = self.extract_education(
            resume_text
        )

        required = self.extract_required_education(
            job_description
        )

        degree_score = self.calculate_degree_score(
            candidate,
            required,
        )

        field_score = self.calculate_field_score(
            candidate,
            required,
        )

        requirement_score = self.calculate_requirement_score(
            resume_text,
            job_description,
        )

        total_score = (
            degree_score *
            self.weights["degree"]
            +
            field_score *
            self.weights["field"]
            +
            requirement_score *
            self.weights["requirement"]
        )

        matched = []
        missing = []

        if degree_score >= 100:
            matched.append(
                f"Degree requirement satisfied: "
                f"{candidate.degree_level}"
            )
        else:
            missing.append(
                f"Required degree: {required.degree_level}"
            )

        if field_score >= 100:
            matched.append(
                f"Field requirement satisfied: "
                f"{candidate.field}"
            )
        elif required.field:
            missing.append(
                f"Preferred field: {required.field}"
            )

        recommendations = self.generate_recommendations(
            candidate,
            required,
            degree_score,
            field_score,
        )

        return EducationScore(
            total_score=round(total_score, 2),
            degree_score=round(degree_score, 2),
            field_score=round(field_score, 2),
            requirement_score=round(
                requirement_score,
                2,
            ),
            candidate_degree=candidate.degree_name,
            candidate_field=candidate.field,
            required_degree=required.degree_name,
            required_field=required.field,
            matched_requirements=matched,
            missing_requirements=missing,
            recommendations=recommendations,
        )


# ============================================================
# Example
# ============================================================

if __name__ == "__main__":

    resume = """
    John Doe

    Education:
    Bachelor of Technology in Computer Science
    ABC University
    2022

    Skills:
    Python, Machine Learning, SQL
    """

    job_description = """
    Machine Learning Engineer

    Requirements:
    Bachelor's degree in Computer Science,
    Artificial Intelligence, Data Science,
    or a related field.

    3+ years of experience with Python
    and machine learning.
    """

    scorer = EducationScorer()

    result = scorer.calculate(
        resume_text=resume,
        job_description=job_description,
    )

    print("=" * 60)
    print("EDUCATION SCORE")
    print("=" * 60)

    print(f"Overall Score : {result.total_score}%")
    print(f"Degree Score  : {result.degree_score}%")
    print(f"Field Score   : {result.field_score}%")
    print(
        f"Requirement   : {result.requirement_score}%"
    )

    print("\nCandidate Education:")
    print(
        f"  Degree: {result.candidate_degree}"
    )
    print(
        f"  Field : {result.candidate_field}"
    )

    print("\nJob Requirement:")
    print(
        f"  Degree: {result.required_degree}"
    )
    print(
        f"  Field : {result.required_field}"
    )

    print("\nMatched Requirements:")

    for item in result.matched_requirements:
        print(f"  ✓ {item}")

    print("\nMissing Requirements:")

    for item in result.missing_requirements:
        print(f"  ✗ {item}")

    print("\nRecommendations:")

    for item in result.recommendations:
        print(f"  → {item}")