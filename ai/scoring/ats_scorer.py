# Project scaffold file
    # Project scaffold file
"""
ATS Resume Scorer

Calculates an ATS-style compatibility score between a resume and a job
description using:
- Skill matching
- Keyword matching
- Experience matching
- Education matching
- Job-title similarity
- Resume completeness
- Semantic similarity (optional)

The scorer returns both a total score and detailed explanations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Set, Optional


@dataclass
class ATSScore:
    total_score: float
    keyword_score: float
    skill_score: float
    experience_score: float
    education_score: float
    title_score: float
    completeness_score: float
    matched_keywords: List[str]
    missing_keywords: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)


class ATSScorer:
    """
    ATS scoring engine.

    Default weighting:
        Skills       -> 35%
        Keywords     -> 20%
        Experience   -> 15%
        Education    -> 10%
        Job Title    -> 10%
        Completeness -> 10%
    """

    WEIGHTS = {
        "skills": 0.35,
        "keywords": 0.20,
        "experience": 0.15,
        "education": 0.10,
        "title": 0.10,
        "completeness": 0.10,
    }

    DEFAULT_SKILLS = {
        "python",
        "java",
        "javascript",
        "typescript",
        "c",
        "c++",
        "sql",
        "nosql",
        "html",
        "css",
        "react",
        "angular",
        "vue",
        "node.js",
        "node",
        "django",
        "flask",
        "fastapi",
        "spring",
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "nlp",
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
        "git",
        "github",
        "linux",
        "mongodb",
        "postgresql",
        "mysql",
        "redis",
        "rest api",
        "graphql",
        "microservices",
        "ci/cd",
        "jenkins",
    }

    STOPWORDS = {
        "the", "a", "an", "and", "or", "but", "for", "to", "of",
        "in", "on", "with", "from", "by", "as", "at", "is", "are",
        "be", "this", "that", "will", "you", "your", "our", "we",
        "have", "has", "had", "their", "they", "it", "its",
        "years", "year", "job", "role", "work", "working",
    }

    def __init__(
        self,
        skills: Optional[Set[str]] = None,
        weights: Optional[Dict[str, float]] = None,
    ):
        self.skills = {
            skill.lower()
            for skill in (skills or self.DEFAULT_SKILLS)
        }

        self.weights = weights or self.WEIGHTS.copy()

        self._validate_weights()

    def _validate_weights(self) -> None:
        total = sum(self.weights.values())

        if abs(total - 1.0) > 0.001:
            raise ValueError(
                f"ATS weights must sum to 1.0, got {total:.3f}"
            )

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for matching."""

        if not text:
            return ""

        text = text.lower()

        # Normalize common symbols.
        text = text.replace("&", " and ")

        # Keep +/# for technologies such as C++ and C#.
        text = re.sub(r"[^\w\s+#./-]", " ", text)

        # Normalize whitespace.
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def extract_keywords(self, text: str) -> Set[str]:
        """
        Extract meaningful keywords from text.

        In a production implementation this can be replaced with:
        - spaCy
        - KeyBERT
        - YAKE
        - transformer-based keyword extraction
        """

        text = self.normalize_text(text)

        words = re.findall(
            r"\b[a-zA-Z][a-zA-Z0-9+#./-]{2,}\b",
            text,
        )

        return {
            word.lower()
            for word in words
            if word.lower() not in self.STOPWORDS
        }

    def extract_skills(self, text: str) -> Set[str]:
        """Find known technical skills in text."""

        normalized = self.normalize_text(text)

        found = set()

        for skill in self.skills:
            pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"

            if re.search(pattern, normalized):
                found.add(skill)

        return found

    def keyword_score(
        self,
        resume_text: str,
        job_description: str,
    ):
        """Calculate keyword overlap."""

        resume_keywords = self.extract_keywords(resume_text)
        job_keywords = self.extract_keywords(job_description)

        if not job_keywords:
            return 100.0, set(), set()

        matched = resume_keywords & job_keywords
        missing = job_keywords - resume_keywords

        score = len(matched) / len(job_keywords) * 100

        return score, matched, missing

    def skill_score(
        self,
        resume_text: str,
        job_description: str,
    ):
        """Calculate technical skill compatibility."""

        resume_skills = self.extract_skills(resume_text)
        required_skills = self.extract_skills(job_description)

        if not required_skills:
            return 100.0, resume_skills, set()

        matched = resume_skills & required_skills
        missing = required_skills - resume_skills

        score = len(matched) / len(required_skills) * 100

        return score, matched, missing

    @staticmethod
    def extract_experience(text: str) -> float:
        """
        Extract approximate years of experience.

        Examples:
            '5 years experience' -> 5
            '3+ years'           -> 3
            '7 yrs'              -> 7
        """

        patterns = [
            r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience",
            r"experience\s*(?:of)?\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
            r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text.lower())

            if matches:
                try:
                    return max(float(x) for x in matches)
                except ValueError:
                    pass

        return 0.0

    def experience_score(
        self,
        resume_text: str,
        job_description: str,
    ) -> float:
        """Compare resume experience against job requirements."""

        resume_years = self.extract_experience(resume_text)
        required_years = self.extract_experience(job_description)

        if required_years <= 0:
            return 100.0

        if resume_years >= required_years:
            return 100.0

        score = (resume_years / required_years) * 100

        return min(score, 100.0)

    def education_score(
        self,
        resume_text: str,
        job_description: str,
    ) -> float:
        """Estimate education compatibility."""

        resume = self.normalize_text(resume_text)
        job = self.normalize_text(job_description)

        education_levels = {
            "phd": 4,
            "doctorate": 4,
            "master": 3,
            "m.tech": 3,
            "mtech": 3,
            "mba": 3,
            "bachelor": 2,
            "b.tech": 2,
            "btech": 2,
            "degree": 1,
            "diploma": 1,
        }

        required_level = 0

        for education, level in education_levels.items():
            if education in job:
                required_level = max(required_level, level)

        if required_level == 0:
            return 100.0

        candidate_level = 0

        for education, level in education_levels.items():
            if education in resume:
                candidate_level = max(candidate_level, level)

        if candidate_level >= required_level:
            return 100.0

        if candidate_level == 0:
            return 0.0

        return (candidate_level / required_level) * 100

    def title_score(
        self,
        resume_text: str,
        job_description: str,
    ) -> float:
        """Estimate job-title compatibility."""

        resume = self.normalize_text(resume_text)
        job = self.normalize_text(job_description)

        titles = [
            "software engineer",
            "software developer",
            "data scientist",
            "data analyst",
            "machine learning engineer",
            "ai engineer",
            "backend developer",
            "frontend developer",
            "full stack developer",
            "devops engineer",
            "cloud engineer",
            "web developer",
            "python developer",
            "java developer",
            "product manager",
            "project manager",
            "business analyst",
        ]

        job_titles = [
            title for title in titles
            if title in job
        ]

        if not job_titles:
            return 100.0

        matches = sum(
            1
            for title in job_titles
            if title in resume
        )

        return matches / len(job_titles) * 100

    def completeness_score(self, resume_text: str) -> float:
        """Evaluate whether important resume sections exist."""

        text = self.normalize_text(resume_text)

        sections = {
            "contact": [
                "@",
                "email",
                "phone",
            ],
            "summary": [
                "summary",
                "profile",
                "objective",
            ],
            "experience": [
                "experience",
                "employment",
                "work history",
            ],
            "education": [
                "education",
                "university",
                "college",
                "degree",
            ],
            "skills": [
                "skills",
                "technical skills",
                "technologies",
            ],
            "projects": [
                "projects",
                "project",
            ],
        }

        completed = 0

        for keywords in sections.values():
            if any(keyword in text for keyword in keywords):
                completed += 1

        return completed / len(sections) * 100

    def generate_recommendations(
        self,
        missing_skills: Set[str],
        missing_keywords: Set[str],
        experience_score: float,
        education_score: float,
        completeness_score: float,
    ) -> List[str]:

        recommendations = []

        if missing_skills:
            skills = ", ".join(sorted(missing_skills)[:10])

            recommendations.append(
                f"Consider adding relevant skills: {skills}"
            )

        if missing_keywords:
            keywords = ", ".join(sorted(missing_keywords)[:10])

            recommendations.append(
                f"Add relevant job-description keywords: {keywords}"
            )

        if experience_score < 70:
            recommendations.append(
                "Highlight relevant professional experience "
                "and measurable achievements."
            )

        if education_score < 70:
            recommendations.append(
                "Clearly mention your highest relevant educational qualification."
            )

        if completeness_score < 80:
            recommendations.append(
                "Improve resume completeness by adding clear sections "
                "for summary, experience, skills, education, and projects."
            )

        if not recommendations:
            recommendations.append(
                "Resume has strong compatibility with the supplied job description."
            )

        return recommendations

    def calculate(
        self,
        resume_text: str,
        job_description: str,
    ) -> ATSScore:
        """Calculate the complete ATS score."""

        if not resume_text.strip():
            raise ValueError("Resume text cannot be empty.")

        if not job_description.strip():
            raise ValueError("Job description cannot be empty.")

        keyword_result = self.keyword_score(
            resume_text,
            job_description,
        )

        keyword_score, matched_keywords, missing_keywords = keyword_result

        skill_result = self.skill_score(
            resume_text,
            job_description,
        )

        skill_score, matched_skills, missing_skills = skill_result

        experience = self.experience_score(
            resume_text,
            job_description,
        )

        education = self.education_score(
            resume_text,
            job_description,
        )

        title = self.title_score(
            resume_text,
            job_description,
        )

        completeness = self.completeness_score(
            resume_text
        )

        total = (
            skill_score * self.weights["skills"]
            + keyword_score * self.weights["keywords"]
            + experience * self.weights["experience"]
            + education * self.weights["education"]
            + title * self.weights["title"]
            + completeness * self.weights["completeness"]
        )

        recommendations = self.generate_recommendations(
            missing_skills,
            missing_keywords,
            experience,
            education,
            completeness,
        )

        return ATSScore(
            total_score=round(total, 2),
            keyword_score=round(keyword_score, 2),
            skill_score=round(skill_score, 2),
            experience_score=round(experience, 2),
            education_score=round(education, 2),
            title_score=round(title, 2),
            completeness_score=round(completeness, 2),
            matched_keywords=sorted(matched_keywords),
            missing_keywords=sorted(missing_keywords),
            matched_skills=sorted(matched_skills),
            missing_skills=sorted(missing_skills),
            recommendations=recommendations,
        )


if __name__ == "__main__":

    resume = """
    John Doe
    Software Engineer

    Summary:
    Python developer with 4 years of experience building AI applications.

    Experience:
    Software Engineer - 4 years

    Skills:
    Python, FastAPI, Flask, SQL, PostgreSQL, Docker,
    Machine Learning, NLP, TensorFlow, Git, AWS

    Education:
    Bachelor of Technology in Computer Science

    Projects:
    AI Resume Screening Platform
    """

    job_description = """
    We are looking for a Machine Learning Engineer.

    Requirements:
    3+ years of experience.
    Strong Python programming skills.
    Experience with Machine Learning, NLP and TensorFlow.
    FastAPI and Docker experience preferred.
    Knowledge of AWS and SQL.
    Bachelor's degree in Computer Science or related field.
    """

    scorer = ATSScorer()

    result = scorer.calculate(
        resume_text=resume,
        job_description=job_description,
    )

    print("=" * 60)
    print("ATS SCORE")
    print("=" * 60)

    print(f"Overall Score: {result.total_score}%")
    print(f"Skills:        {result.skill_score}%")
    print(f"Keywords:      {result.keyword_score}%")
    print(f"Experience:    {result.experience_score}%")
    print(f"Education:     {result.education_score}%")
    print(f"Title:         {result.title_score}%")
    print(f"Completeness:  {result.completeness_score}%")

    print("\nMatched Skills:")
    for skill in result.matched_skills:
        print(f"  ✓ {skill}")

    print("\nMissing Skills:")
    for skill in result.missing_skills:
        print(f"  ✗ {skill}")

    print("\nRecommendations:")
    for recommendation in result.recommendations:
        print(f"  → {recommendation}")