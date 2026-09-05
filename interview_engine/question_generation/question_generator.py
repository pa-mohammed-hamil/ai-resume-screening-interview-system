"""
Adaptive Interview Question Generator

Location:
    interview_engine/question_generation/question_generator.py

Purpose:
    Generate interview questions based on:
    - Job description
    - Candidate resume
    - Skills
    - Experience
    - Interview type
    - Difficulty
    - Previous questions/answers

Designed to work with the AI Resume Screening & Interview System.
"""

from __future__ import annotations

import random
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Sequence


# ============================================================================
# Constants
# ============================================================================

QUESTION_TYPES = {
    "technical",
    "behavioral",
    "situational",
    "experience",
    "project",
    "skill",
    "role_specific",
    "general",
    "follow_up",
}

DIFFICULTIES = {
    "easy",
    "medium",
    "hard",
}

DEFAULT_QUESTION_COUNT = 10


# ============================================================================
# Question Templates
# ============================================================================

TECHNICAL_TEMPLATES = {
    "easy": [
        "What is {skill}, and where have you used it?",
        "What are the basic concepts you know about {skill}?",
        "How would you explain {skill} to someone who is new to it?",
        "What are some common use cases of {skill}?",
    ],
    "medium": [
        "Describe a project where you used {skill}. What was your approach?",
        "What challenges have you faced while working with {skill}?",
        "How do you troubleshoot problems related to {skill}?",
        "What are the important best practices when using {skill}?",
        "How would you optimize a solution built using {skill}?",
    ],
    "hard": [
        "What are the major performance or scalability challenges when using {skill}?",
        "How would you design a production-grade system using {skill}?",
        "Compare different approaches for solving a problem using {skill}.",
        "What are the limitations of {skill}, and how would you work around them?",
        "Describe a complex technical problem you solved using {skill}.",
    ],
}


BEHAVIORAL_TEMPLATES = [
    "Tell me about a time when you faced a difficult challenge at work.",
    "Tell me about a time when you disagreed with a teammate. How did you handle it?",
    "Describe a situation where you had to work under a tight deadline.",
    "Tell me about a mistake you made and what you learned from it.",
    "Describe a time when you had to learn a new technology quickly.",
    "Tell me about a time when you took ownership of a difficult task.",
    "Describe a situation where you received critical feedback.",
    "Tell me about a time when you improved an existing process.",
]


SITUATIONAL_TEMPLATES = [
    "What would you do if a production issue occurred just before a major release?",
    "How would you handle a disagreement with a senior engineer?",
    "What would you do if the requirements of a project were unclear?",
    "How would you prioritize multiple urgent tasks?",
    "What would you do if your solution failed during testing?",
    "How would you respond if a stakeholder rejected your proposed solution?",
]


EXPERIENCE_TEMPLATES = [
    "Walk me through your professional experience.",
    "Which project in your experience are you most proud of and why?",
    "What has been the most challenging project you have worked on?",
    "Which technical decision had the biggest impact on one of your projects?",
    "How has your previous experience prepared you for this role?",
]


PROJECT_TEMPLATES = [
    "Walk me through one of your most important projects.",
    "What problem were you trying to solve in that project?",
    "What was your specific contribution to the project?",
    "What technical challenges did you face in the project?",
    "How did you test and validate your project?",
    "If you could rebuild the project today, what would you change?",
]


GENERAL_TEMPLATES = [
    "Tell me about yourself.",
    "Why are you interested in this role?",
    "Why do you want to join our company?",
    "What are your strongest technical skills?",
    "What are your career goals?",
    "What motivates you as an engineer?",
]


ROLE_TEMPLATES = [
    "Why do you think you are a good fit for this role?",
    "Which responsibilities of this role are you most comfortable with?",
    "Which part of this role would require the most learning for you?",
    "How would you approach your first 30 days in this role?",
]


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class InterviewQuestion:
    """Represents a generated interview question."""

    question: str

    question_type: str = "general"

    difficulty: str = "medium"

    skill: str | None = None

    topic: str | None = None

    expected_duration_seconds: int = 90

    follow_up: bool = False

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class QuestionGenerationResult:
    """Result returned by the question generator."""

    questions: list[InterviewQuestion] = field(
        default_factory=list
    )

    candidate_skills: list[str] = field(
        default_factory=list
    )

    job_skills: list[str] = field(
        default_factory=list
    )

    difficulty: str = "medium"

    interview_type: str = "mixed"

    total_questions: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "questions": [
                question.to_dict()
                for question in self.questions
            ],
            "candidate_skills": self.candidate_skills,
            "job_skills": self.job_skills,
            "difficulty": self.difficulty,
            "interview_type": self.interview_type,
            "total_questions": self.total_questions,
        }


# ============================================================================
# Utility Functions
# ============================================================================


def normalize_text(value: Any) -> str:
    """Normalize arbitrary input into clean text."""

    if value is None:
        return ""

    text = str(value)

    text = text.replace(
        "\u00a0",
        " ",
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def normalize_skill(skill: Any) -> str:
    """Normalize a skill name."""

    value = normalize_text(
        skill
    )

    value = value.strip(
        ".,;:|/-"
    )

    return value


def unique_strings(
    values: Iterable[Any],
) -> list[str]:
    """Return unique non-empty strings."""

    result: list[str] = []
    seen: set[str] = set()

    for value in values:

        normalized = normalize_text(
            value
        )

        if not normalized:
            continue

        key = normalized.lower()

        if key in seen:
            continue

        seen.add(key)
        result.append(
            normalized
        )

    return result


# ============================================================================
# Question Generator
# ============================================================================


class QuestionGenerator:
    """
    Generate interview questions from candidate and job information.

    Example:

        generator = QuestionGenerator()

        result = generator.generate(
            resume_text=resume,
            job_description=job_description,
            candidate_skills=[
                "Python",
                "FastAPI",
                "PostgreSQL"
            ],
            job_skills=[
                "Python",
                "FastAPI",
                "Docker"
            ],
            question_count=10,
        )
    """

    def __init__(
        self,
        *,
        seed: int | None = None,
        avoid_duplicates: bool = True,
    ) -> None:

        self.random = random.Random(
            seed
        )

        self.avoid_duplicates = (
            avoid_duplicates
        )

    # ------------------------------------------------------------------
    # Skill Extraction
    # ------------------------------------------------------------------

    def extract_skills(
        self,
        data: Any,
    ) -> list[str]:
        """
        Extract skills from strings, lists, dictionaries, or objects.
        """

        if data is None:
            return []

        if isinstance(
            data,
            str,
        ):
            return self.extract_skills_from_text(
                data
            )

        if isinstance(
            data,
            dict,
        ):

            skills: list[str] = []

            for key in (
                "skills",
                "technical_skills",
                "required_skills",
                "preferred_skills",
                "skill",
            ):

                value = data.get(
                    key
                )

                if isinstance(
                    value,
                    (list, tuple, set),
                ):
                    skills.extend(
                        value
                    )

                elif isinstance(
                    value,
                    str,
                ):
                    skills.extend(
                        self.extract_skills_from_text(
                            value
                        )
                    )

            return unique_strings(
                skills
            )

        if isinstance(
            data,
            (list, tuple, set),
        ):

            result: list[str] = []

            for item in data:

                if isinstance(
                    item,
                    str,
                ):
                    result.append(
                        item
                    )

                elif isinstance(
                    item,
                    dict,
                ):
                    result.extend(
                        self.extract_skills(
                            item
                        )
                    )

            return unique_strings(
                result
            )

        return []

    def extract_skills_from_text(
        self,
        text: str,
    ) -> list[str]:
        """
        Extract common technology/skill names from text.

        This is a lightweight fallback. In production, this method
        can be replaced by ai.skill_intelligence.skill_extractor.
        """

        text = normalize_text(
            text
        )

        known_skills = [
            "Python",
            "Java",
            "JavaScript",
            "TypeScript",
            "C++",
            "C#",
            "Go",
            "Rust",
            "PHP",
            "Ruby",
            "SQL",
            "PostgreSQL",
            "MySQL",
            "MongoDB",
            "Redis",
            "FastAPI",
            "Django",
            "Flask",
            "Spring Boot",
            "React",
            "Angular",
            "Vue",
            "Node.js",
            "Express.js",
            "HTML",
            "CSS",
            "AWS",
            "Azure",
            "GCP",
            "Docker",
            "Kubernetes",
            "Terraform",
            "Git",
            "GitHub",
            "Jenkins",
            "CI/CD",
            "Machine Learning",
            "Deep Learning",
            "Artificial Intelligence",
            "Generative AI",
            "NLP",
            "Computer Vision",
            "TensorFlow",
            "PyTorch",
            "Scikit-learn",
            "Pandas",
            "NumPy",
            "LangChain",
            "REST API",
            "GraphQL",
            "Microservices",
            "Linux",
            "Agile",
            "Scrum",
        ]

        found: list[str] = []

        lower_text = text.lower()

        for skill in known_skills:

            pattern = (
                r"(?<!\w)"
                + re.escape(
                    skill.lower()
                )
                + r"(?!\w)"
            )

            if re.search(
                pattern,
                lower_text,
            ):
                found.append(
                    skill
                )

        return found

    # ------------------------------------------------------------------
    # Skill Relevance
    # ------------------------------------------------------------------

    def find_matching_skills(
        self,
        candidate_skills: Sequence[str],
        job_skills: Sequence[str],
    ) -> list[str]:
        """Find skills shared by candidate and job."""

        candidate_map = {
            skill.lower(): skill
            for skill in candidate_skills
        }

        matched: list[str] = []

        for skill in job_skills:

            key = skill.lower()

            if key in candidate_map:
                matched.append(
                    candidate_map[key]
                )

        return unique_strings(
            matched
        )

    def find_missing_skills(
        self,
        candidate_skills: Sequence[str],
        job_skills: Sequence[str],
    ) -> list[str]:
        """Find job skills missing from the candidate profile."""

        candidate_map = {
            skill.lower()
            for skill in candidate_skills
        }

        return [
            skill
            for skill in job_skills
            if skill.lower()
            not in candidate_map
        ]

    # ------------------------------------------------------------------
    # Technical Questions
    # ------------------------------------------------------------------

    def generate_technical_question(
        self,
        skill: str,
        difficulty: str = "medium",
    ) -> InterviewQuestion:
        """Generate a technical question for a skill."""

        difficulty = self.normalize_difficulty(
            difficulty
        )

        templates = TECHNICAL_TEMPLATES.get(
            difficulty,
            TECHNICAL_TEMPLATES["medium"],
        )

        template = self.random.choice(
            templates
        )

        question = template.format(
            skill=skill
        )

        duration = {
            "easy": 60,
            "medium": 90,
            "hard": 150,
        }.get(
            difficulty,
            90,
        )

        return InterviewQuestion(
            question=question,
            question_type="technical",
            difficulty=difficulty,
            skill=skill,
            topic=skill,
            expected_duration_seconds=duration,
            metadata={
                "source": "skill_based",
            },
        )

    # ------------------------------------------------------------------
    # Behavioral Questions
    # ------------------------------------------------------------------

    def generate_behavioral_question(
        self,
        difficulty: str = "medium",
    ) -> InterviewQuestion:
        """Generate a behavioral question."""

        difficulty = self.normalize_difficulty(
            difficulty
        )

        question = self.random.choice(
            BEHAVIORAL_TEMPLATES
        )

        return InterviewQuestion(
            question=question,
            question_type="behavioral",
            difficulty=difficulty,
            topic="behavior",
            expected_duration_seconds=120,
            metadata={
                "recommended_framework": "STAR",
            },
        )

    # ------------------------------------------------------------------
    # Situational Questions
    # ------------------------------------------------------------------

    def generate_situational_question(
        self,
        difficulty: str = "medium",
    ) -> InterviewQuestion:
        """Generate situational question."""

        difficulty = self.normalize_difficulty(
            difficulty
        )

        question = self.random.choice(
            SITUATIONAL_TEMPLATES
        )

        return InterviewQuestion(
            question=question,
            question_type="situational",
            difficulty=difficulty,
            topic="problem_solving",
            expected_duration_seconds=120,
        )

    # ------------------------------------------------------------------
    # Experience Questions
    # ------------------------------------------------------------------

    def generate_experience_question(
        self,
        difficulty: str = "medium",
    ) -> InterviewQuestion:
        """Generate experience-based question."""

        difficulty = self.normalize_difficulty(
            difficulty
        )

        question = self.random.choice(
            EXPERIENCE_TEMPLATES
        )

        return InterviewQuestion(
            question=question,
            question_type="experience",
            difficulty=difficulty,
            topic="experience",
            expected_duration_seconds=120,
        )

    # ------------------------------------------------------------------
    # Project Questions
    # ------------------------------------------------------------------

    def generate_project_question(
        self,
        project: str | None = None,
        difficulty: str = "medium",
    ) -> InterviewQuestion:
        """Generate project-specific question."""

        difficulty = self.normalize_difficulty(
            difficulty
        )

        if project:

            question = (
                f"Tell me about your "
                f"{project} project. "
                f"What problem did it solve "
                f"and what was your contribution?"
            )

        else:

            question = self.random.choice(
                PROJECT_TEMPLATES
            )

        return InterviewQuestion(
            question=question,
            question_type="project",
            difficulty=difficulty,
            topic="projects",
            expected_duration_seconds=150,
        )

    # ------------------------------------------------------------------
    # General Questions
    # ------------------------------------------------------------------

    def generate_general_question(
        self,
        difficulty: str = "medium",
    ) -> InterviewQuestion:
        """Generate general interview question."""

        difficulty = self.normalize_difficulty(
            difficulty
        )

        question = self.random.choice(
            GENERAL_TEMPLATES
        )

        return InterviewQuestion(
            question=question,
            question_type="general",
            difficulty=difficulty,
            topic="general",
            expected_duration_seconds=90,
        )

    # ------------------------------------------------------------------
    # Role Questions
    # ------------------------------------------------------------------

    def generate_role_question(
        self,
        difficulty: str = "medium",
    ) -> InterviewQuestion:
        """Generate role-specific question."""

        difficulty = self.normalize_difficulty(
            difficulty
        )

        question = self.random.choice(
            ROLE_TEMPLATES
        )

        return InterviewQuestion(
            question=question,
            question_type="role_specific",
            difficulty=difficulty,
            topic="role_fit",
            expected_duration_seconds=90,
        )

    # ------------------------------------------------------------------
    # Follow-up Questions
    # ------------------------------------------------------------------

    def generate_follow_up(
        self,
        previous_question: str,
        previous_answer: str,
        difficulty: str = "medium",
    ) -> InterviewQuestion:
        """
        Generate a follow-up question from the previous answer.

        This is intentionally deterministic/rule-based and can later
        be replaced by an LLM-powered follow-up generator.
        """

        difficulty = self.normalize_difficulty(
            difficulty
        )

        answer = normalize_text(
            previous_answer
        )

        if not answer:

            question = (
                "Could you provide more details "
                "about your previous answer?"
            )

        elif len(answer.split()) < 20:

            question = (
                "Can you explain that in more detail "
                "and give a specific example?"
            )

        elif any(
            word in answer.lower()
            for word in (
                "project",
                "application",
                "system",
                "platform",
            )
        ):

            question = (
                "What was your specific contribution "
                "to that project, and how did you "
                "measure the result?"
            )

        elif any(
            word in answer.lower()
            for word in (
                "challenge",
                "problem",
                "issue",
                "bug",
            )
        ):

            question = (
                "How did you investigate the problem, "
                "and what did you learn from solving it?"
            )

        else:

            question = (
                "Why did you choose that approach, "
                "and what alternatives did you consider?"
            )

        return InterviewQuestion(
            question=question,
            question_type="follow_up",
            difficulty=difficulty,
            topic="follow_up",
            expected_duration_seconds=90,
            follow_up=True,
            metadata={
                "previous_question": previous_question,
            },
        )

    # ------------------------------------------------------------------
    # Question Type Generation
    # ------------------------------------------------------------------

    def generate_by_type(
        self,
        question_type: str,
        *,
        difficulty: str = "medium",
        skill: str | None = None,
        project: str | None = None,
    ) -> InterviewQuestion:
        """Generate a question according to question type."""

        question_type = (
            normalize_text(
                question_type
            ).lower()
        )

        if question_type == "technical":

            if not skill:
                return self.generate_general_question(
                    difficulty
                )

            return self.generate_technical_question(
                skill,
                difficulty,
            )

        if question_type == "behavioral":
            return self.generate_behavioral_question(
                difficulty
            )

        if question_type == "situational":
            return self.generate_situational_question(
                difficulty
            )

        if question_type == "experience":
            return self.generate_experience_question(
                difficulty
            )

        if question_type == "project":
            return self.generate_project_question(
                project,
                difficulty,
            )

        if question_type == "role_specific":
            return self.generate_role_question(
                difficulty
            )

        return self.generate_general_question(
            difficulty
        )

    # ------------------------------------------------------------------
    # Difficulty
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_difficulty(
        difficulty: str,
    ) -> str:
        """Normalize difficulty."""

        value = normalize_text(
            difficulty
        ).lower()

        if value not in DIFFICULTIES:
            return "medium"

        return value

    def calculate_initial_difficulty(
        self,
        candidate_skills: Sequence[str],
        job_skills: Sequence[str],
    ) -> str:
        """
        Estimate initial difficulty based on candidate/job overlap.
        """

        if not job_skills:
            return "medium"

        matched = self.find_matching_skills(
            candidate_skills,
            job_skills,
        )

        ratio = (
            len(matched)
            / len(job_skills)
        )

        if ratio >= 0.75:
            return "hard"

        if ratio >= 0.40:
            return "medium"

        return "easy"

    # ------------------------------------------------------------------
    # Distribution
    # ------------------------------------------------------------------

    def build_question_distribution(
        self,
        count: int,
        interview_type: str,
    ) -> list[str]:
        """Build a question-type distribution."""

        count = max(
            1,
            count,
        )

        interview_type = (
            normalize_text(
                interview_type
            ).lower()
        )

        if interview_type == "technical":

            types = [
                "technical",
                "technical",
                "technical",
                "project",
                "situational",
            ]

        elif interview_type == "behavioral":

            types = [
                "behavioral",
                "behavioral",
                "situational",
                "experience",
                "role_specific",
            ]

        elif interview_type == "experience":

            types = [
                "experience",
                "project",
                "behavioral",
                "role_specific",
                "technical",
            ]

        else:

            types = [
                "general",
                "technical",
                "technical",
                "project",
                "behavioral",
                "situational",
                "experience",
                "role_specific",
            ]

        result: list[str] = []

        index = 0

        while len(result) < count:

            result.append(
                types[
                    index % len(types)
                ]
            )

            index += 1

        return result

    # ------------------------------------------------------------------
    # Duplicate Detection
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_question(
        question: str,
    ) -> str:
        """Normalize question for duplicate detection."""

        question = normalize_text(
            question
        ).lower()

        question = re.sub(
            r"[^\w\s]",
            "",
            question,
        )

        return question

    def remove_duplicates(
        self,
        questions: Sequence[InterviewQuestion],
    ) -> list[InterviewQuestion]:
        """Remove duplicate questions."""

        if not self.avoid_duplicates:
            return list(
                questions
            )

        result: list[
            InterviewQuestion
        ] = []

        seen: set[str] = set()

        for question in questions:

            key = self.normalize_question(
                question.question
            )

            if key in seen:
                continue

            seen.add(key)

            result.append(
                question
            )

        return result

    # ------------------------------------------------------------------
    # Generate Question Set
    # ------------------------------------------------------------------

    def generate_questions(
        self,
        *,
        candidate_skills: Sequence[str] | None = None,
        job_skills: Sequence[str] | None = None,
        question_count: int = DEFAULT_QUESTION_COUNT,
        interview_type: str = "mixed",
        difficulty: str = "medium",
        projects: Sequence[str] | None = None,
    ) -> list[InterviewQuestion]:
        """Generate a complete question set."""

        candidate_skills = unique_strings(
            candidate_skills or []
        )

        job_skills = unique_strings(
            job_skills or []
        )

        projects = unique_strings(
            projects or []
        )

        question_count = max(
            1,
            int(question_count),
        )

        difficulty = self.normalize_difficulty(
            difficulty
        )

        matched_skills = (
            self.find_matching_skills(
                candidate_skills,
                job_skills,
            )
        )

        # Prefer job-required skills that the candidate already has.
        priority_skills = (
            matched_skills
            + [
                skill
                for skill in job_skills
                if skill
                not in matched_skills
            ]
            + [
                skill
                for skill in candidate_skills
                if skill
                not in job_skills
            ]
        )

        priority_skills = unique_strings(
            priority_skills
        )

        distribution = (
            self.build_question_distribution(
                question_count,
                interview_type,
            )
        )

        questions: list[
            InterviewQuestion
        ] = []

        technical_index = 0

        project_index = 0

        for question_type in distribution:

            if question_type == "technical":

                if priority_skills:

                    skill = priority_skills[
                        technical_index
                        % len(priority_skills)
                    ]

                    technical_index += 1

                    question = (
                        self.generate_technical_question(
                            skill,
                            difficulty,
                        )
                    )

                else:

                    question = (
                        self.generate_general_question(
                            difficulty
                        )
                    )

            elif question_type == "project":

                project = None

                if projects:

                    project = projects[
                        project_index
                        % len(projects)
                    ]

                    project_index += 1

                question = (
                    self.generate_project_question(
                        project,
                        difficulty,
                    )
                )

            else:

                question = (
                    self.generate_by_type(
                        question_type,
                        difficulty=difficulty,
                    )
                )

            questions.append(
                question
            )

        questions = self.remove_duplicates(
            questions
        )

        # If duplicate removal reduced the count,
        # fill the remaining slots.
        attempts = 0

        while (
            len(questions) < question_count
            and attempts < question_count * 5
        ):

            attempts += 1

            question_type = self.random.choice(
                distribution
            )

            if question_type == "technical" and priority_skills:

                skill = self.random.choice(
                    priority_skills
                )

                question = (
                    self.generate_technical_question(
                        skill,
                        difficulty,
                    )
                )

            elif question_type == "project":

                question = (
                    self.generate_project_question(
                        None,
                        difficulty,
                    )
                )

            else:

                question = (
                    self.generate_by_type(
                        question_type,
                        difficulty=difficulty,
                    )
                )

            candidate = questions + [
                question
            ]

            deduplicated = (
                self.remove_duplicates(
                    candidate
                )
            )

            if len(deduplicated) > len(
                questions
            ):
                questions = deduplicated

        return questions[
            :question_count
        ]

    # ------------------------------------------------------------------
    # Resume + JD Generation
    # ------------------------------------------------------------------

    def generate(
        self,
        *,
        resume_text: str = "",
        job_description: str = "",
        candidate_skills: Sequence[str] | None = None,
        job_skills: Sequence[str] | None = None,
        question_count: int = DEFAULT_QUESTION_COUNT,
        interview_type: str = "mixed",
        difficulty: str | None = None,
        projects: Sequence[str] | None = None,
        candidate_data: dict[str, Any] | None = None,
        job_data: dict[str, Any] | None = None,
    ) -> QuestionGenerationResult:
        """
        Generate personalized interview questions.

        Information can come from:
            - resume_text
            - job_description
            - candidate_skills
            - job_skills
            - candidate_data
            - job_data
        """

        candidate_data = (
            candidate_data or {}
        )

        job_data = (
            job_data or {}
        )

        # --------------------------------------------------------------
        # Candidate skills
        # --------------------------------------------------------------

        candidate_skill_list = unique_strings(
            list(
                candidate_skills or []
            )
            + self.extract_skills(
                candidate_data
            )
        )

        if not candidate_skill_list:
            candidate_skill_list = (
                self.extract_skills(
                    resume_text
                )
            )

        # --------------------------------------------------------------
        # Job skills
        # --------------------------------------------------------------

        job_skill_list = unique_strings(
            list(
                job_skills or []
            )
            + self.extract_skills(
                job_data
            )
        )

        if not job_skill_list:
            job_skill_list = (
                self.extract_skills(
                    job_description
                )
            )

        # --------------------------------------------------------------
        # Projects
        # --------------------------------------------------------------

        project_list = unique_strings(
            projects or []
        )

        if not project_list:

            possible_projects = (
                candidate_data.get(
                    "projects"
                )
            )

            if isinstance(
                possible_projects,
                list,
            ):

                for project in (
                    possible_projects
                ):

                    if isinstance(
                        project,
                        str,
                    ):
                        project_list.append(
                            project
                        )

                    elif isinstance(
                        project,
                        dict,
                    ):

                        name = project.get(
                            "name"
                        )

                        if name:
                            project_list.append(
                                str(name)
                            )

        # --------------------------------------------------------------
        # Difficulty
        # --------------------------------------------------------------

        if difficulty is None:

            difficulty = (
                self.calculate_initial_difficulty(
                    candidate_skill_list,
                    job_skill_list,
                )
            )

        difficulty = (
            self.normalize_difficulty(
                difficulty
            )
        )

        # --------------------------------------------------------------
        # Generate questions
        # --------------------------------------------------------------

        questions = self.generate_questions(
            candidate_skills=candidate_skill_list,
            job_skills=job_skill_list,
            question_count=question_count,
            interview_type=interview_type,
            difficulty=difficulty,
            projects=project_list,
        )

        return QuestionGenerationResult(
            questions=questions,
            candidate_skills=candidate_skill_list,
            job_skills=job_skill_list,
            difficulty=difficulty,
            interview_type=interview_type,
            total_questions=len(
                questions
            ),
        )

    # ------------------------------------------------------------------
    # Next Question
    # ------------------------------------------------------------------

    def generate_next_question(
        self,
        *,
        previous_questions: Sequence[str] | None = None,
        previous_answers: Sequence[str] | None = None,
        candidate_skills: Sequence[str] | None = None,
        job_skills: Sequence[str] | None = None,
        current_difficulty: str = "medium",
        question_type: str = "technical",
    ) -> InterviewQuestion:
        """
        Generate the next question during an active interview.

        Avoids previously asked questions where possible.
        """

        previous_questions = list(
            previous_questions or []
        )

        previous_answers = list(
            previous_answers or []
        )

        candidate_skills = unique_strings(
            candidate_skills or []
        )

        job_skills = unique_strings(
            job_skills or []
        )

        used = {
            self.normalize_question(
                question
            )
            for question in previous_questions
        }

        skills = (
            self.find_matching_skills(
                candidate_skills,
                job_skills,
            )
            or job_skills
            or candidate_skills
        )

        attempts = 0

        while attempts < 20:

            attempts += 1

            if (
                question_type == "technical"
                and skills
            ):

                skill = self.random.choice(
                    skills
                )

                question = (
                    self.generate_technical_question(
                        skill,
                        current_difficulty,
                    )
                )

            else:

                question = (
                    self.generate_by_type(
                        question_type,
                        difficulty=current_difficulty,
                    )
                )

            key = self.normalize_question(
                question.question
            )

            if key not in used:
                return question

        return question

    # ------------------------------------------------------------------
    # Adaptive Difficulty
    # ------------------------------------------------------------------

    def adjust_difficulty(
        self,
        *,
        current_difficulty: str,
        score: float,
    ) -> str:
        """
        Adjust question difficulty based on answer score.

        Score should normally be between 0 and 100.
        """

        difficulty = (
            self.normalize_difficulty(
                current_difficulty
            )
        )

        try:
            score = float(
                score
            )
        except (
            TypeError,
            ValueError,
        ):
            return difficulty

        if score >= 85:

            if difficulty == "easy":
                return "medium"

            if difficulty == "medium":
                return "hard"

            return "hard"

        if score <= 45:

            if difficulty == "hard":
                return "medium"

            if difficulty == "medium":
                return "easy"

            return "easy"

        return difficulty

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    @staticmethod
    def questions_to_dict(
        questions: Sequence[InterviewQuestion],
    ) -> list[dict[str, Any]]:
        """Convert question objects to dictionaries."""

        return [
            question.to_dict()
            for question in questions
        ]


# ============================================================================
# Backward-Compatible Alias
# ============================================================================


InterviewQuestionGenerator = QuestionGenerator


# ============================================================================
# Convenience Functions
# ============================================================================


_default_generator: QuestionGenerator | None = None


def get_default_generator() -> QuestionGenerator:
    """Return a shared question generator."""

    global _default_generator

    if _default_generator is None:

        _default_generator = (
            QuestionGenerator()
        )

    return _default_generator


def generate_questions(
    *,
    resume_text: str = "",
    job_description: str = "",
    candidate_skills: Sequence[str] | None = None,
    job_skills: Sequence[str] | None = None,
    question_count: int = DEFAULT_QUESTION_COUNT,
    interview_type: str = "mixed",
    difficulty: str | None = None,
    projects: Sequence[str] | None = None,
    candidate_data: dict[str, Any] | None = None,
    job_data: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Generate interview questions."""

    result = get_default_generator().generate(
        resume_text=resume_text,
        job_description=job_description,
        candidate_skills=candidate_skills,
        job_skills=job_skills,
        question_count=question_count,
        interview_type=interview_type,
        difficulty=difficulty,
        projects=projects,
        candidate_data=candidate_data,
        job_data=job_data,
    )

    return [
        question.to_dict()
        for question in result.questions
    ]


def generate_next_question(
    *,
    previous_questions: Sequence[str] | None = None,
    previous_answers: Sequence[str] | None = None,
    candidate_skills: Sequence[str] | None = None,
    job_skills: Sequence[str] | None = None,
    current_difficulty: str = "medium",
    question_type: str = "technical",
) -> dict[str, Any]:
    """Generate the next interview question."""

    question = (
        get_default_generator().generate_next_question(
            previous_questions=previous_questions,
            previous_answers=previous_answers,
            candidate_skills=candidate_skills,
            job_skills=job_skills,
            current_difficulty=current_difficulty,
            question_type=question_type,
        )
    )

    return question.to_dict()


# ============================================================================
# Public API
# ============================================================================


__all__ = [
    "InterviewQuestion",
    "QuestionGenerationResult",
    "QuestionGenerator",
    "InterviewQuestionGenerator",
    "generate_questions",
    "generate_next_question",
    "get_default_generator",
]