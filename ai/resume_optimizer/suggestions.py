"""
optimizer.py

Main Resume Optimization Orchestrator.

This module coordinates the different resume optimization and
scoring components into one unified pipeline.

Pipeline:

    Resume
       |
       +--> Keyword Analysis
       |
       +--> Content Analysis
       |
       +--> Skill Analysis
       |
       +--> ATS Analysis
       |
       +--> Education Analysis
       |
       +--> Experience Analysis
       |
       v
    Unified Optimization Report

IMPORTANT:
This module never invents candidate experience, skills,
education, metrics, certifications, or achievements.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


# ============================================================
# Optional Component Imports
# ============================================================

try:
    from ai.resume_optimizer.keyword_optimizer import (
        KeywordOptimizer,
    )
except ImportError:
    KeywordOptimizer = None


try:
    from ai.resume_optimizer.content_optimizer import (
        ContentOptimizer,
    )
except ImportError:
    ContentOptimizer = None


try:
    from ai.scoring.ats_scorer import (
        ATSScorer,
    )
except ImportError:
    ATSScorer = None


try:
    from ai.scoring.education_scorer import (
        EducationScorer,
    )
except ImportError:
    EducationScorer = None


try:
    from ai.scoring.experience_scorer import (
        ExperienceScorer,
    )
except ImportError:
    ExperienceScorer = None


try:
    from ai.scoring.skill_scorer import (
        SkillScorer,
    )
except ImportError:
    SkillScorer = None


# ============================================================
# Data Models
# ============================================================

@dataclass
class OptimizationSummary:
    """
    High-level resume optimization summary.
    """

    overall_score: float

    ats_score: float
    keyword_score: float
    content_score: float
    skill_score: float
    education_score: float
    experience_score: float

    strengths: List[str] = field(
        default_factory=list
    )

    weaknesses: List[str] = field(
        default_factory=list
    )

    priority_actions: List[str] = field(
        default_factory=list
    )


@dataclass
class ResumeOptimizationResult:
    """
    Complete result returned by the optimizer.
    """

    summary: OptimizationSummary

    keyword_analysis: Dict[str, Any]

    content_analysis: Dict[str, Any]

    skill_analysis: Dict[str, Any]

    education_analysis: Dict[str, Any]

    experience_analysis: Dict[str, Any]

    ats_analysis: Dict[str, Any]

    optimized_bullets: List[Dict[str, Any]]

    recommendations: List[str]

    warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:

        return {
            "summary": asdict(
                self.summary
            ),
            "keyword_analysis": (
                self.keyword_analysis
            ),
            "content_analysis": (
                self.content_analysis
            ),
            "skill_analysis": (
                self.skill_analysis
            ),
            "education_analysis": (
                self.education_analysis
            ),
            "experience_analysis": (
                self.experience_analysis
            ),
            "ats_analysis": (
                self.ats_analysis
            ),
            "optimized_bullets": (
                self.optimized_bullets
            ),
            "recommendations": (
                self.recommendations
            ),
            "warnings": (
                self.warnings
            ),
        }


# ============================================================
# Resume Optimizer
# ============================================================

class ResumeOptimizer:
    """
    Main orchestration engine.

    Combines:

        KeywordOptimizer
        ContentOptimizer
        SkillScorer
        EducationScorer
        ExperienceScorer
        ATSScorer

    Default score distribution:

        ATS          30%
        Keywords     20%
        Content      15%
        Skills       15%
        Experience   10%
        Education    10%

    Total = 100%
    """

    DEFAULT_WEIGHTS = {
        "ats": 0.30,
        "keyword": 0.20,
        "content": 0.15,
        "skill": 0.15,
        "experience": 0.10,
        "education": 0.10,
    }

    # ========================================================
    # Initialization
    # ========================================================

    def __init__(
        self,
        weights: Optional[
            Dict[str, float]
        ] = None,
    ):

        self.weights = (
            weights
            or self.DEFAULT_WEIGHTS.copy()
        )

        self._validate_weights()

        self.keyword_optimizer = (
            KeywordOptimizer()
            if KeywordOptimizer
            else None
        )

        self.content_optimizer = (
            ContentOptimizer()
            if ContentOptimizer
            else None
        )

        self.skill_scorer = (
            SkillScorer()
            if SkillScorer
            else None
        )

        self.education_scorer = (
            EducationScorer()
            if EducationScorer
            else None
        )

        self.experience_scorer = (
            ExperienceScorer()
            if ExperienceScorer
            else None
        )

        self.ats_scorer = (
            ATSScorer()
            if ATSScorer
            else None
        )

    # ========================================================
    # Validation
    # ========================================================

    def _validate_weights(self) -> None:

        required = set(
            self.DEFAULT_WEIGHTS.keys()
        )

        provided = set(
            self.weights.keys()
        )

        if required != provided:

            raise ValueError(
                "Optimizer weights must contain exactly: "
                f"{sorted(required)}"
            )

        total = sum(
            self.weights.values()
        )

        if abs(total - 1.0) > 0.001:

            raise ValueError(
                "Optimizer weights must sum to 1.0."
            )

        for key, value in (
            self.weights.items()
        ):

            if value < 0:

                raise ValueError(
                    f"Weight cannot be negative: {key}"
                )

    # ========================================================
    # Generic Result Conversion
    # ========================================================

    @staticmethod
    def result_to_dict(
        result: Any,
    ) -> Dict[str, Any]:

        if result is None:
            return {}

        if isinstance(result, dict):
            return result

        if hasattr(result, "to_dict"):

            try:
                return result.to_dict()

            except Exception:
                pass

        if hasattr(result, "__dataclass_fields__"):

            return asdict(result)

        if hasattr(result, "__dict__"):

            return dict(
                result.__dict__
            )

        return {
            "result": result
        }

    # ========================================================
    # Extract Score
    # ========================================================

    @staticmethod
    def extract_score(
        data: Dict[str, Any],
        possible_keys: List[str],
    ) -> float:

        for key in possible_keys:

            value = data.get(key)

            if value is None:
                continue

            try:

                score = float(value)

                return max(
                    0.0,
                    min(
                        100.0,
                        score,
                    ),
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

        return 0.0

    # ========================================================
    # Keyword Analysis
    # ========================================================

    def analyze_keywords(
        self,
        resume_text: str,
        job_description: str,
    ) -> Dict[str, Any]:

        if not self.keyword_optimizer:

            return {
                "available": False,
                "error": (
                    "KeywordOptimizer is not available."
                ),
            }

        try:

            result = (
                self.keyword_optimizer.optimize(
                    resume_text=resume_text,
                    job_description=job_description,
                )
            )

            data = self.result_to_dict(
                result
            )

            data["available"] = True

            return data

        except Exception as exc:

            return {
                "available": False,
                "error": str(exc),
            }

    # ========================================================
    # Content Analysis
    # ========================================================

    def analyze_content(
        self,
        resume_text: str,
        job_description: str,
    ) -> Dict[str, Any]:

        if not self.content_optimizer:

            return {
                "available": False,
                "error": (
                    "ContentOptimizer is not available."
                ),
            }

        try:

            result = (
                self.content_optimizer.optimize(
                    resume_text=resume_text,
                    job_description=job_description,
                )
            )

            data = self.result_to_dict(
                result
            )

            data["available"] = True

            return data

        except Exception as exc:

            return {
                "available": False,
                "error": str(exc),
            }

    # ========================================================
    # Skill Analysis
    # ========================================================

    def analyze_skills(
        self,
        resume_text: str,
        job_description: str,
    ) -> Dict[str, Any]:

        if not self.skill_scorer:

            return {
                "available": False,
                "error": (
                    "SkillScorer is not available."
                ),
            }

        try:

            # Support common scorer APIs.
            if hasattr(
                self.skill_scorer,
                "score",
            ):

                result = (
                    self.skill_scorer.score(
                        resume_text,
                        job_description,
                    )
                )

            elif hasattr(
                self.skill_scorer,
                "calculate",
            ):

                result = (
                    self.skill_scorer.calculate(
                        resume_text,
                        job_description,
                    )
                )

            elif hasattr(
                self.skill_scorer,
                "evaluate",
            ):

                result = (
                    self.skill_scorer.evaluate(
                        resume_text,
                        job_description,
                    )
                )

            else:

                return {
                    "available": False,
                    "error": (
                        "SkillScorer does not expose "
                        "a supported scoring method."
                    ),
                }

            data = self.result_to_dict(
                result
            )

            data["available"] = True

            return data

        except Exception as exc:

            return {
                "available": False,
                "error": str(exc),
            }

    # ========================================================
    # Education Analysis
    # ========================================================

    def analyze_education(
        self,
        resume_text: str,
        job_description: str,
    ) -> Dict[str, Any]:

        if not self.education_scorer:

            return {
                "available": False,
                "error": (
                    "EducationScorer is not available."
                ),
            }

        try:

            if hasattr(
                self.education_scorer,
                "score",
            ):

                result = (
                    self.education_scorer.score(
                        resume_text,
                        job_description,
                    )
                )

            elif hasattr(
                self.education_scorer,
                "calculate",
            ):

                result = (
                    self.education_scorer.calculate(
                        resume_text,
                        job_description,
                    )
                )

            elif hasattr(
                self.education_scorer,
                "evaluate",
            ):

                result = (
                    self.education_scorer.evaluate(
                        resume_text,
                        job_description,
                    )
                )

            else:

                return {
                    "available": False,
                    "error": (
                        "EducationScorer does not expose "
                        "a supported scoring method."
                    ),
                }

            data = self.result_to_dict(
                result
            )

            data["available"] = True

            return data

        except Exception as exc:

            return {
                "available": False,
                "error": str(exc),
            }

    # ========================================================
    # Experience Analysis
    # ========================================================

    def analyze_experience(
        self,
        resume_text: str,
        job_description: str,
    ) -> Dict[str, Any]:

        if not self.experience_scorer:

            return {
                "available": False,
                "error": (
                    "ExperienceScorer is not available."
                ),
            }

        try:

            if hasattr(
                self.experience_scorer,
                "score",
            ):

                result = (
                    self.experience_scorer.score(
                        resume_text,
                        job_description,
                    )
                )

            elif hasattr(
                self.experience_scorer,
                "calculate",
            ):

                result = (
                    self.experience_scorer.calculate(
                        resume_text,
                        job_description,
                    )
                )

            elif hasattr(
                self.experience_scorer,
                "evaluate",
            ):

                result = (
                    self.experience_scorer.evaluate(
                        resume_text,
                        job_description,
                    )
                )

            else:

                return {
                    "available": False,
                    "error": (
                        "ExperienceScorer does not expose "
                        "a supported scoring method."
                    ),
                }

            data = self.result_to_dict(
                result
            )

            data["available"] = True

            return data

        except Exception as exc:

            return {
                "available": False,
                "error": str(exc),
            }

    # ========================================================
    # ATS Analysis
    # ========================================================

    def analyze_ats(
        self,
        resume_text: str,
        job_description: str,
    ) -> Dict[str, Any]:

        if not self.ats_scorer:

            return {
                "available": False,
                "error": (
                    "ATSScorer is not available."
                ),
            }

        try:

            if hasattr(
                self.ats_scorer,
                "score",
            ):

                result = (
                    self.ats_scorer.score(
                        resume_text,
                        job_description,
                    )
                )

            elif hasattr(
                self.ats_scorer,
                "calculate",
            ):

                result = (
                    self.ats_scorer.calculate(
                        resume_text,
                        job_description,
                    )
                )

            elif hasattr(
                self.ats_scorer,
                "evaluate",
            ):

                result = (
                    self.ats_scorer.evaluate(
                        resume_text,
                        job_description,
                    )
                )

            else:

                return {
                    "available": False,
                    "error": (
                        "ATSScorer does not expose "
                        "a supported scoring method."
                    ),
                }

            data = self.result_to_dict(
                result
            )

            data["available"] = True

            return data

        except Exception as exc:

            return {
                "available": False,
                "error": str(exc),
            }

    # ========================================================
    # Overall Score
    # ========================================================

    def calculate_overall_score(
        self,
        ats_score: float,
        keyword_score: float,
        content_score: float,
        skill_score: float,
        experience_score: float,
        education_score: float,
    ) -> float:

        score = (
            ats_score *
            self.weights["ats"]

            +

            keyword_score *
            self.weights["keyword"]

            +

            content_score *
            self.weights["content"]

            +

            skill_score *
            self.weights["skill"]

            +

            experience_score *
            self.weights["experience"]

            +

            education_score *
            self.weights["education"]
        )

        return round(
            max(
                0.0,
                min(100.0, score),
            ),
            2,
        )

    # ========================================================
    # Strength Detection
    # ========================================================

    def identify_strengths(
        self,
        scores: Dict[str, float],
    ) -> List[str]:

        strengths = []

        labels = {
            "ats": "ATS compatibility",
            "keyword": "job keyword alignment",
            "content": "resume content quality",
            "skill": "technical skill alignment",
            "experience": "professional experience",
            "education": "education alignment",
        }

        for category, score in scores.items():

            if score >= 85:

                strengths.append(
                    f"Strong {labels[category]} "
                    f"({score:.1f}/100)."
                )

            elif score >= 75:

                strengths.append(
                    f"Good {labels[category]} "
                    f"({score:.1f}/100)."
                )

        return strengths

    # ========================================================
    # Weakness Detection
    # ========================================================

    def identify_weaknesses(
        self,
        scores: Dict[str, float],
    ) -> List[str]:

        weaknesses = []

        labels = {
            "ats": "ATS compatibility",
            "keyword": "keyword alignment",
            "content": "content quality",
            "skill": "skill alignment",
            "experience": "experience alignment",
            "education": "education alignment",
        }

        for category, score in sorted(
            scores.items(),
            key=lambda item: item[1],
        ):

            if score < 50:

                weaknesses.append(
                    f"Weak {labels[category]} "
                    f"({score:.1f}/100)."
                )

            elif score < 70:

                weaknesses.append(
                    f"{labels[category].capitalize()} "
                    f"could be improved "
                    f"({score:.1f}/100)."
                )

        return weaknesses

    # ========================================================
    # Priority Actions
    # ========================================================

    def generate_priority_actions(
        self,
        scores: Dict[str, float],
        keyword_data: Dict[str, Any],
        content_data: Dict[str, Any],
    ) -> List[str]:

        actions = []

        # Missing keywords.
        missing_keywords = (
            keyword_data.get(
                "missing_keywords_list",
                keyword_data.get(
                    "missing_keywords",
                    [],
                ),
            )
        )

        if missing_keywords:

            if isinstance(
                missing_keywords,
                list,
            ):

                preview = ", ".join(
                    missing_keywords[:8]
                )

                actions.append(
                    "Add truthful, job-relevant keywords "
                    f"where appropriate: {preview}."
                )

        # Content.
        if scores["content"] < 70:

            actions.append(
                "Improve resume bullets with strong action "
                "verbs and measurable outcomes."
            )

        # Skills.
        if scores["skill"] < 70:

            actions.append(
                "Strengthen alignment between the candidate's "
                "verified skills and the target job requirements."
            )

        # Experience.
        if scores["experience"] < 70:

            actions.append(
                "Emphasize experience that directly demonstrates "
                "the responsibilities required by the target role."
            )

        # Education.
        if scores["education"] < 70:

            actions.append(
                "Clearly present the candidate's relevant degree, "
                "field of study, and education details."
            )

        # ATS.
        if scores["ats"] < 70:

            actions.append(
                "Improve ATS compatibility through clear sections, "
                "consistent formatting, relevant keywords, and "
                "complete resume information."
            )

        # Avoid duplicate recommendations.
        unique = []

        for action in actions:

            if action not in unique:
                unique.append(action)

        return unique[:10]

    # ========================================================
    # Collect Recommendations
    # ========================================================

    def collect_recommendations(
        self,
        keyword_data: Dict[str, Any],
        content_data: Dict[str, Any],
        skill_data: Dict[str, Any],
        education_data: Dict[str, Any],
        experience_data: Dict[str, Any],
        ats_data: Dict[str, Any],
    ) -> List[str]:

        recommendations = []

        datasets = [
            keyword_data,
            content_data,
            skill_data,
            education_data,
            experience_data,
            ats_data,
        ]

        for data in datasets:

            if not isinstance(
                data,
                dict,
            ):
                continue

            values = data.get(
                "recommendations",
                [],
            )

            if not isinstance(
                values,
                list,
            ):
                continue

            for recommendation in values:

                if (
                    isinstance(
                        recommendation,
                        str,
                    )
                    and recommendation.strip()
                    and recommendation
                    not in recommendations
                ):

                    recommendations.append(
                        recommendation.strip()
                    )

        return recommendations[:20]

    # ========================================================
    # Collect Warnings
    # ========================================================

    def collect_warnings(
        self,
        keyword_data: Dict[str, Any],
        content_data: Dict[str, Any],
        skill_data: Dict[str, Any],
        education_data: Dict[str, Any],
        experience_data: Dict[str, Any],
        ats_data: Dict[str, Any],
    ) -> List[str]:

        warnings = []

        datasets = {
            "keyword": keyword_data,
            "content": content_data,
            "skill": skill_data,
            "education": education_data,
            "experience": experience_data,
            "ats": ats_data,
        }

        for name, data in datasets.items():

            if not isinstance(
                data,
                dict,
            ):
                continue

            if data.get(
                "available",
                True,
            ) is False:

                error = data.get(
                    "error",
                    "Unknown error",
                )

                warnings.append(
                    f"{name.capitalize()} analysis unavailable: "
                    f"{error}"
                )

        # Keyword stuffing warning.
        if keyword_data.get(
            "stuffing_detected",
            False,
        ):

            warnings.append(
                "Potential keyword stuffing detected. "
                "Use keywords naturally and only where relevant."
            )

        return warnings

    # ========================================================
    # Optimized Bullets
    # ========================================================

    @staticmethod
    def extract_optimized_bullets(
        content_data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        bullets = content_data.get(
            "optimized_bullets",
            [],
        )

        if not isinstance(
            bullets,
            list,
        ):
            return []

        result = []

        for bullet in bullets:

            if isinstance(
                bullet,
                dict,
            ):

                result.append(
                    bullet
                )

        return result

    # ========================================================
    # Main Pipeline
    # ========================================================

    def optimize(
        self,
        resume_text: str,
        job_description: str,
    ) -> ResumeOptimizationResult:

        if not isinstance(
            resume_text,
            str,
        ):

            raise TypeError(
                "resume_text must be a string."
            )

        if not isinstance(
            job_description,
            str,
        ):

            raise TypeError(
                "job_description must be a string."
            )

        if not resume_text.strip():

            raise ValueError(
                "Resume text cannot be empty."
            )

        if not job_description.strip():

            raise ValueError(
                "Job description cannot be empty."
            )

        # ----------------------------------------------------
        # Run analysis modules
        # ----------------------------------------------------

        keyword_data = (
            self.analyze_keywords(
                resume_text,
                job_description,
            )
        )

        content_data = (
            self.analyze_content(
                resume_text,
                job_description,
            )
        )

        skill_data = (
            self.analyze_skills(
                resume_text,
                job_description,
            )
        )

        education_data = (
            self.analyze_education(
                resume_text,
                job_description,
            )
        )

        experience_data = (
            self.analyze_experience(
                resume_text,
                job_description,
            )
        )

        ats_data = (
            self.analyze_ats(
                resume_text,
                job_description,
            )
        )

        # ----------------------------------------------------
        # Extract scores
        # ----------------------------------------------------

        ats_score = self.extract_score(
            ats_data,
            [
                "total_score",
                "ats_score",
                "score",
                "overall_score",
            ],
        )

        keyword_score = self.extract_score(
            keyword_data,
            [
                "keyword_score",
                "total_score",
                "score",
                "overall_score",
            ],
        )

        content_score = self.extract_score(
            content_data,
            [
                "overall_score",
                "content_score",
                "score",
                "total_score",
            ],
        )

        skill_score = self.extract_score(
            skill_data,
            [
                "skill_score",
                "total_score",
                "score",
                "overall_score",
            ],
        )

        education_score = self.extract_score(
            education_data,
            [
                "total_score",
                "education_score",
                "score",
                "overall_score",
            ],
        )

        experience_score = self.extract_score(
            experience_data,
            [
                "total_score",
                "experience_score",
                "score",
                "overall_score",
            ],
        )

        scores = {
            "ats": ats_score,
            "keyword": keyword_score,
            "content": content_score,
            "skill": skill_score,
            "experience": experience_score,
            "education": education_score,
        }

        # ----------------------------------------------------
        # Overall score
        # ----------------------------------------------------

        overall_score = (
            self.calculate_overall_score(
                ats_score=ats_score,
                keyword_score=keyword_score,
                content_score=content_score,
                skill_score=skill_score,
                experience_score=experience_score,
                education_score=education_score,
            )
        )

        # ----------------------------------------------------
        # Strengths / weaknesses
        # ----------------------------------------------------

        strengths = (
            self.identify_strengths(
                scores
            )
        )

        weaknesses = (
            self.identify_weaknesses(
                scores
            )
        )

        priority_actions = (
            self.generate_priority_actions(
                scores=scores,
                keyword_data=keyword_data,
                content_data=content_data,
            )
        )

        # ----------------------------------------------------
        # Recommendations
        # ----------------------------------------------------

        recommendations = (
            self.collect_recommendations(
                keyword_data=keyword_data,
                content_data=content_data,
                skill_data=skill_data,
                education_data=education_data,
                experience_data=experience_data,
                ats_data=ats_data,
            )
        )

        # Add priority actions first.
        combined_recommendations = []

        for recommendation in (
            priority_actions +
            recommendations
        ):

            if recommendation not in (
                combined_recommendations
            ):

                combined_recommendations.append(
                    recommendation
                )

        # ----------------------------------------------------
        # Warnings
        # ----------------------------------------------------

        warnings = (
            self.collect_warnings(
                keyword_data=keyword_data,
                content_data=content_data,
                skill_data=skill_data,
                education_data=education_data,
                experience_data=experience_data,
                ats_data=ats_data,
            )
        )

        # ----------------------------------------------------
        # Optimized bullets
        # ----------------------------------------------------

        optimized_bullets = (
            self.extract_optimized_bullets(
                content_data
            )
        )

        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        summary = OptimizationSummary(
            overall_score=overall_score,

            ats_score=ats_score,

            keyword_score=keyword_score,

            content_score=content_score,

            skill_score=skill_score,

            education_score=education_score,

            experience_score=experience_score,

            strengths=strengths,

            weaknesses=weaknesses,

            priority_actions=priority_actions,
        )

        return ResumeOptimizationResult(
            summary=summary,

            keyword_analysis=keyword_data,

            content_analysis=content_data,

            skill_analysis=skill_data,

            education_analysis=education_data,

            experience_analysis=experience_data,

            ats_analysis=ats_data,

            optimized_bullets=optimized_bullets,

            recommendations=(
                combined_recommendations[:20]
            ),

            warnings=warnings,
        )


# ============================================================
# Convenience Function
# ============================================================

def optimize_resume(
    resume_text: str,
    job_description: str,
) -> Dict[str, Any]:

    """
    Convenience API for the application/backend layer.
    """

    optimizer = ResumeOptimizer()

    result = optimizer.optimize(
        resume_text=resume_text,
        job_description=job_description,
    )

    return result.to_dict()


# ============================================================
# Score Label
# ============================================================

def get_score_label(
    score: float,
) -> str:

    if score >= 90:
        return "Excellent"

    if score >= 80:
        return "Very Good"

    if score >= 70:
        return "Good"

    if score >= 60:
        return "Needs Improvement"

    if score >= 50:
        return "Weak"

    return "Poor"


# ============================================================
# Example
# ============================================================

if __name__ == "__main__":

    resume = """
    JOHN DOE

    Professional Summary

    Software Engineer with 4 years of experience
    developing backend applications using Python,
    FastAPI, SQL and AWS.

    Skills

    Python
    FastAPI
    SQL
    PostgreSQL
    Docker
    AWS
    Git
    Machine Learning

    Experience

    Software Engineer
    ABC Technologies

    - Developed REST APIs using Python and FastAPI.
    - Optimized PostgreSQL database queries.
    - Deployed backend services using Docker and AWS.
    - Collaborated with engineering teams.
    - Improved application performance by 30%.

    Education

    B.Tech in Computer Science
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
    - AWS
    - REST API

    Preferred:

    - PyTorch
    - Kubernetes
    - Generative AI
    - NLP

    Experience with scalable backend systems,
    cloud deployment and CI/CD.
    """

    optimizer = ResumeOptimizer()

    result = optimizer.optimize(
        resume_text=resume,
        job_description=job_description,
    )

    summary = result.summary

    print("=" * 75)
    print("AI RESUME OPTIMIZATION REPORT")
    print("=" * 75)

    print(
        f"\nOverall Score: "
        f"{summary.overall_score}/100 "
        f"({get_score_label(summary.overall_score)})"
    )

    print("\n" + "-" * 75)
    print("SCORE BREAKDOWN")
    print("-" * 75)

    scores = {
        "ATS": summary.ats_score,
        "Keywords": summary.keyword_score,
        "Content": summary.content_score,
        "Skills": summary.skill_score,
        "Experience": summary.experience_score,
        "Education": summary.education_score,
    }

    for name, score in scores.items():

        print(
            f"{name:<15}: "
            f"{score:>6.2f}/100 "
            f"({get_score_label(score)})"
        )

    print("\n" + "-" * 75)
    print("STRENGTHS")
    print("-" * 75)

    if summary.strengths:

        for strength in summary.strengths:
            print(f"  ✓ {strength}")

    else:

        print("  No major strengths detected.")

    print("\n" + "-" * 75)
    print("WEAKNESSES")
    print("-" * 75)

    if summary.weaknesses:

        for weakness in summary.weaknesses:
            print(f"  ⚠ {weakness}")

    else:

        print("  No major weaknesses detected.")

    print("\n" + "-" * 75)
    print("PRIORITY ACTIONS")
    print("-" * 75)

    if summary.priority_actions:

        for action in (
            summary.priority_actions
        ):

            print(f"  → {action}")

    else:

        print(
            "  No immediate actions required."
        )

    print("\n" + "-" * 75)
    print("MISSING KEYWORDS")
    print("-" * 75)

    missing = (
        result.keyword_analysis.get(
            "missing_keywords_list",
            [],
        )
    )

    if missing:

        for keyword in missing:
            print(f"  ✗ {keyword}")

    else:

        print(
            "  No missing keywords detected."
        )

    print("\n" + "-" * 75)
    print("OPTIMIZED BULLETS")
    print("-" * 75)

    if result.optimized_bullets:

        for index, bullet in enumerate(
            result.optimized_bullets,
            start=1,
        ):

            print(
                f"\n[{index}] Original:"
            )

            print(
                f"    {bullet.get('original', '')}"
            )

            print(
                "    Optimized:"
            )

            print(
                f"    {bullet.get('optimized', '')}"
            )

    else:

        print(
            "  No bullet optimizations available."
        )

    print("\n" + "-" * 75)
    print("RECOMMENDATIONS")
    print("-" * 75)

    for recommendation in (
        result.recommendations
    ):

        print(
            f"  → {recommendation}"
        )

    print("\n" + "-" * 75)
    print("WARNINGS")
    print("-" * 75)

    if result.warnings:

        for warning in result.warnings:
            print(f"  ⚠ {warning}")

    else:

        print(
            "  No warnings."
        )

    print("\n" + "=" * 75)
    print("OPTIMIZATION COMPLETE")
    print("=" * 75)