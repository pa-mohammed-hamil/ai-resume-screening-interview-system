# Project scaffold file
"""
entity_extractor.py

Entity extraction module for an AI Resume Screening System.

Extracts:
- Person names
- Email addresses
- Phone numbers
- URLs / LinkedIn / GitHub
- Locations
- Organizations
- Job titles
- Skills
- Degrees
- Certifications
- Dates
- Years
- Experience indicators

The module is intentionally designed as a lightweight,
explainable extraction layer that can later be upgraded
with spaCy, transformers, or an LLM.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional


# ============================================================
# Data Models
# ============================================================

@dataclass
class Entity:
    """
    Represents one extracted entity.
    """

    text: str
    label: str
    start: int
    end: int
    confidence: float = 1.0


@dataclass
class ExtractedEntities:
    """
    Complete collection of entities extracted from a document.
    """

    names: List[Entity]
    emails: List[Entity]
    phones: List[Entity]
    urls: List[Entity]
    locations: List[Entity]
    organizations: List[Entity]
    job_titles: List[Entity]
    skills: List[Entity]
    degrees: List[Entity]
    certifications: List[Entity]
    dates: List[Entity]
    years: List[Entity]
    experience: List[Entity]

    def to_dict(self) -> Dict:
        return {
            key: [
                asdict(entity)
                for entity in value
            ]
            for key, value in asdict(self).items()
        }


# ============================================================
# Entity Extractor
# ============================================================

class EntityExtractor:
    """
    Extracts structured entities from resumes and job descriptions.

    This is a rule-based extraction engine intended to be:
        - Fast
        - Explainable
        - Dependency-light
        - Easy to integrate

    It can later be combined with:
        spaCy NER
        BERT
        RoBERTa
        LayoutLM
        LLM-based extraction
    """

    # ========================================================
    # Skills
    # ========================================================

    SKILLS = {
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

        # Web
        "html",
        "css",
        "react",
        "react.js",
        "angular",
        "vue",
        "vue.js",
        "next.js",
        "nextjs",
        "node.js",
        "node",
        "express",
        "express.js",

        # Backend
        "django",
        "flask",
        "fastapi",
        "spring",
        "spring boot",
        "asp.net",
        ".net",

        # Database
        "sql",
        "mysql",
        "postgresql",
        "postgres",
        "oracle",
        "mongodb",
        "redis",
        "sqlite",
        "elasticsearch",

        # AI / ML
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "natural language processing",
        "nlp",
        "computer vision",
        "generative ai",
        "genai",
        "large language models",
        "llm",
        "transformers",

        # ML frameworks
        "tensorflow",
        "pytorch",
        "keras",
        "scikit-learn",
        "sklearn",

        # Data
        "pandas",
        "numpy",
        "scipy",
        "matplotlib",
        "seaborn",
        "spark",
        "pyspark",
        "hadoop",

        # Cloud
        "aws",
        "amazon web services",
        "azure",
        "google cloud",
        "gcp",

        # DevOps
        "docker",
        "kubernetes",
        "terraform",
        "ansible",
        "jenkins",
        "github actions",
        "gitlab ci",
        "ci/cd",

        # Tools
        "git",
        "github",
        "gitlab",
        "bitbucket",
        "linux",

        # APIs
        "rest api",
        "restful api",
        "graphql",
        "grpc",
        "microservices",

        # Analytics
        "power bi",
        "tableau",
        "excel",

        # Messaging
        "kafka",
        "apache kafka",
        "rabbitmq",
    }

    # ========================================================
    # Job Titles
    # ========================================================

    JOB_TITLES = {
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

        "web developer",
        "web engineer",

        "python developer",
        "java developer",

        "data scientist",
        "data analyst",
        "data engineer",

        "machine learning engineer",
        "ml engineer",
        "ai engineer",
        "artificial intelligence engineer",

        "deep learning engineer",

        "nlp engineer",
        "computer vision engineer",

        "devops engineer",
        "cloud engineer",

        "cloud architect",
        "software architect",

        "solutions architect",

        "database administrator",
        "database engineer",

        "qa engineer",
        "test engineer",
        "automation engineer",

        "product manager",
        "project manager",

        "business analyst",
        "system analyst",

        "research scientist",
        "research engineer",

        "technical lead",
        "team lead",
        "engineering manager",
    }

    # ========================================================
    # Degrees
    # ========================================================

    DEGREES = {
        "bachelor of technology",
        "bachelor of engineering",
        "bachelor of science",
        "bachelor of arts",
        "master of technology",
        "master of engineering",
        "master of science",
        "master of arts",

        "b.tech",
        "btech",
        "b.e",
        "be",
        "b.sc",
        "bsc",
        "b.a",
        "ba",

        "m.tech",
        "mtech",
        "m.e",
        "me",
        "m.sc",
        "msc",
        "m.a",
        "ma",

        "mba",
        "master of business administration",

        "phd",
        "ph.d",

        "diploma",
        "associate degree",

        "high school",
    }

    # ========================================================
    # Certifications
    # ========================================================

    CERTIFICATIONS = {
        "aws certified",
        "aws certified solutions architect",
        "aws certified developer",
        "azure fundamentals",
        "azure administrator",
        "google cloud certified",
        "gcp certification",

        "certified kubernetes administrator",
        "cka",

        "comptia",
        "comptia security+",
        "security+",

        "cisco certified",
        "ccna",
        "ccnp",

        "pmp",
        "project management professional",

        "scrum master",
        "certified scrum master",
        "csm",

        "oracle certified",

        "tensorflow developer certificate",
    }

    # ========================================================
    # Locations
    # ========================================================

    COMMON_LOCATIONS = {
        "india",
        "united states",
        "usa",
        "united kingdom",
        "uk",
        "canada",
        "australia",
        "germany",
        "france",
        "singapore",
        "uae",

        "kerala",
        "tamil nadu",
        "karnataka",
        "maharashtra",
        "telangana",
        "andhra pradesh",
        "delhi",
        "mumbai",
        "bangalore",
        "bengaluru",
        "hyderabad",
        "chennai",
        "pune",
        "kochi",
        "thrissur",
        "calicut",
        "kolkata",
        "ahmedabad",
        "noida",
        "gurgaon",
        "gurugram",
        "new delhi",
    }

    # ========================================================
    # Regex Patterns
    # ========================================================

    EMAIL_PATTERN = re.compile(
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\."
        r"[A-Za-z]{2,}\b"
    )

    PHONE_PATTERN = re.compile(
        r"(?<!\d)"
        r"(?:\+?\d{1,3}[\s.-]?)?"
        r"(?:\(?\d{2,5}\)?[\s.-]?)?"
        r"\d{3,5}[\s.-]?\d{3,5}"
        r"(?!\d)"
    )

    URL_PATTERN = re.compile(
        r"\b(?:https?://)?"
        r"(?:www\.)?"
        r"(?:linkedin\.com|github\.com|"
        r"gitlab\.com|bitbucket\.org|"
        r"[A-Za-z0-9.-]+\.[A-Za-z]{2,})"
        r"(?:/[^\s]*)?"
    )

    YEAR_PATTERN = re.compile(
        r"\b(?:19|20)\d{2}\b"
    )

    DATE_PATTERN = re.compile(
        r"\b(?:"
        r"Jan(?:uary)?|"
        r"Feb(?:ruary)?|"
        r"Mar(?:ch)?|"
        r"Apr(?:il)?|"
        r"May|"
        r"Jun(?:e)?|"
        r"Jul(?:y)?|"
        r"Aug(?:ust)?|"
        r"Sep(?:tember)?|"
        r"Oct(?:ober)?|"
        r"Nov(?:ember)?|"
        r"Dec(?:ember)?"
        r")"
        r"(?:\s+\d{4})?"
        r"\b"
        r"|"
        r"\b\d{1,2}[/-]\d{1,2}[/-](?:19|20)\d{2}\b"
    )

    EXPERIENCE_PATTERN = re.compile(
        r"\b"
        r"(?:"
        r"\d+(?:\.\d+)?\s*"
        r"(?:\+|plus)?\s*"
        r"(?:years?|yrs?)"
        r"(?:\s+of)?\s+experience"
        r"|"
        r"\d+(?:\.\d+)?\s*"
        r"(?:years?|yrs?)"
        r")"
        r"\b",
        flags=re.IGNORECASE,
    )

    # ========================================================
    # Initialization
    # ========================================================

    def __init__(
        self,
        skills: Optional[set] = None,
        job_titles: Optional[set] = None,
    ):
        self.skills = skills or self.SKILLS
        self.job_titles = (
            job_titles or self.JOB_TITLES
        )

    # ========================================================
    # Utility
    # ========================================================

    @staticmethod
    def normalize(text: str) -> str:

        text = text.lower()

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    @staticmethod
    def clean_entity_text(
        text: str,
    ) -> str:

        return text.strip(
            " \t\n\r.,;:()[]{}<>"
        )

    # ========================================================
    # Generic Phrase Extraction
    # ========================================================

    def extract_phrases(
        self,
        text: str,
        phrases: set,
        label: str,
        confidence: float = 1.0,
    ) -> List[Entity]:

        entities = []

        normalized = text.lower()

        for phrase in phrases:

            phrase_lower = phrase.lower()

            pattern = re.compile(
                rf"(?<![a-zA-Z0-9])"
                rf"{re.escape(phrase_lower)}"
                rf"(?![a-zA-Z0-9])",
                flags=re.IGNORECASE,
            )

            for match in pattern.finditer(
                normalized
            ):

                original = text[
                    match.start():match.end()
                ]

                entities.append(
                    Entity(
                        text=self.clean_entity_text(
                            original
                        ),
                        label=label,
                        start=match.start(),
                        end=match.end(),
                        confidence=confidence,
                    )
                )

        return self.remove_duplicates(
            entities
        )

    # ========================================================
    # Name Extraction
    # ========================================================

    def extract_names(
        self,
        text: str,
    ) -> List[Entity]:

        entities = []

        lines = text.splitlines()

        position = 0

        for line in lines:

            stripped = line.strip()

            if not stripped:
                position += len(line) + 1
                continue

            # Strong signals for a resume name.
            if re.match(
                r"^(name|candidate|full name)\s*:",
                stripped,
                re.IGNORECASE,
            ):

                value = re.sub(
                    r"^(name|candidate|full name)\s*:\s*",
                    "",
                    stripped,
                    flags=re.IGNORECASE,
                )

                start = text.find(
                    value,
                    position,
                )

                if start >= 0:

                    entities.append(
                        Entity(
                            text=value,
                            label="PERSON",
                            start=start,
                            end=start + len(value),
                            confidence=0.95,
                        )
                    )

            # Possible name on the first meaningful line.
            elif (
                position < 500
                and len(stripped.split()) in range(2, 5)
                and re.fullmatch(
                    r"[A-Za-z .'-]+",
                    stripped,
                )
                and not self.looks_like_heading(
                    stripped
                )
            ):

                words = stripped.split()

                if all(
                    word[0].isupper()
                    for word in words
                    if word
                ):

                    start = text.find(
                        stripped,
                        position,
                    )

                    if start >= 0:

                        entities.append(
                            Entity(
                                text=stripped,
                                label="PERSON",
                                start=start,
                                end=start + len(stripped),
                                confidence=0.70,
                            )
                        )

            position += len(line) + 1

        return self.remove_duplicates(
            entities
        )

    # ========================================================
    # Heading Detection
    # ========================================================

    @staticmethod
    def looks_like_heading(
        text: str,
    ) -> bool:

        headings = {
            "resume",
            "cv",
            "curriculum vitae",
            "skills",
            "education",
            "experience",
            "projects",
            "certifications",
            "summary",
            "profile",
            "contact",
            "objective",
            "references",
        }

        return text.lower().strip() in headings

    # ========================================================
    # Email
    # ========================================================

    def extract_emails(
        self,
        text: str,
    ) -> List[Entity]:

        entities = []

        for match in self.EMAIL_PATTERN.finditer(
            text
        ):

            entities.append(
                Entity(
                    text=match.group(),
                    label="EMAIL",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.99,
                )
            )

        return entities

    # ========================================================
    # Phone
    # ========================================================

    def extract_phones(
        self,
        text: str,
    ) -> List[Entity]:

        entities = []

        for match in self.PHONE_PATTERN.finditer(
            text
        ):

            value = self.clean_entity_text(
                match.group()
            )

            digits = re.sub(
                r"\D",
                "",
                value,
            )

            # Avoid treating years as phone numbers.
            if len(digits) < 7:
                continue

            if len(digits) > 15:
                continue

            if (
                len(digits) == 4
                and digits.startswith(
                    ("19", "20")
                )
            ):
                continue

            entities.append(
                Entity(
                    text=value,
                    label="PHONE",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.90,
                )
            )

        return self.remove_duplicates(
            entities
        )

    # ========================================================
    # URLs
    # ========================================================

    def extract_urls(
        self,
        text: str,
    ) -> List[Entity]:

        entities = []

        for match in self.URL_PATTERN.finditer(
            text
        ):

            value = match.group()

            if "@" in value:
                continue

            label = "URL"

            if "linkedin.com" in value.lower():
                label = "LINKEDIN"

            elif "github.com" in value.lower():
                label = "GITHUB"

            entities.append(
                Entity(
                    text=value,
                    label=label,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.98,
                )
            )

        return self.remove_duplicates(
            entities
        )

    # ========================================================
    # Locations
    # ========================================================

    def extract_locations(
        self,
        text: str,
    ) -> List[Entity]:

        return self.extract_phrases(
            text=text,
            phrases=self.COMMON_LOCATIONS,
            label="LOCATION",
            confidence=0.85,
        )

    # ========================================================
    # Organizations
    # ========================================================

    def extract_organizations(
        self,
        text: str,
    ) -> List[Entity]:

        entities = []

        # Company suffixes.
        pattern = re.compile(
            r"\b"
            r"[A-Z][A-Za-z0-9&.,' -]{1,60}"
            r"\s+"
            r"(?:"
            r"Inc|Ltd|Limited|LLC|LLP|"
            r"Corporation|Corp|Company|Co|"
            r"Technologies|Technology|"
            r"Solutions|Systems|"
            r"Software|Labs|Laboratories|"
            r"Consulting|Services"
            r")"
            r"\.?"
            r"\b"
        )

        for match in pattern.finditer(text):

            value = self.clean_entity_text(
                match.group()
            )

            entities.append(
                Entity(
                    text=value,
                    label="ORGANIZATION",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.82,
                )
            )

        # Common labels.
        label_pattern = re.compile(
            r"\b(?:"
            r"company|organization|employer|"
            r"worked at|working at"
            r")\s*[:\-]?\s*"
            r"([A-Z][A-Za-z0-9&.,' -]{2,60})",
            flags=re.IGNORECASE,
        )

        for match in label_pattern.finditer(
            text
        ):

            value = self.clean_entity_text(
                match.group(1)
            )

            if value:

                start = (
                    match.start(1)
                )

                entities.append(
                    Entity(
                        text=value,
                        label="ORGANIZATION",
                        start=start,
                        end=start + len(value),
                        confidence=0.70,
                    )
                )

        return self.remove_duplicates(
            entities
        )

    # ========================================================
    # Job Titles
    # ========================================================

    def extract_job_titles(
        self,
        text: str,
    ) -> List[Entity]:

        return self.extract_phrases(
            text=text,
            phrases=self.job_titles,
            label="JOB_TITLE",
            confidence=0.94,
        )

    # ========================================================
    # Skills
    # ========================================================

    def extract_skills(
        self,
        text: str,
    ) -> List[Entity]:

        return self.extract_phrases(
            text=text,
            phrases=self.skills,
            label="SKILL",
            confidence=0.95,
        )

    # ========================================================
    # Degrees
    # ========================================================

    def extract_degrees(
        self,
        text: str,
    ) -> List[Entity]:

        return self.extract_phrases(
            text=text,
            phrases=self.DEGREES,
            label="DEGREE",
            confidence=0.96,
        )

    # ========================================================
    # Certifications
    # ========================================================

    def extract_certifications(
        self,
        text: str,
    ) -> List[Entity]:

        return self.extract_phrases(
            text=text,
            phrases=self.CERTIFICATIONS,
            label="CERTIFICATION",
            confidence=0.93,
        )

    # ========================================================
    # Dates
    # ========================================================

    def extract_dates(
        self,
        text: str,
    ) -> List[Entity]:

        entities = []

        for match in self.DATE_PATTERN.finditer(
            text
        ):

            entities.append(
                Entity(
                    text=match.group(),
                    label="DATE",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.96,
                )
            )

        return entities

    # ========================================================
    # Years
    # ========================================================

    def extract_years(
        self,
        text: str,
    ) -> List[Entity]:

        entities = []

        for match in self.YEAR_PATTERN.finditer(
            text
        ):

            entities.append(
                Entity(
                    text=match.group(),
                    label="YEAR",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.98,
                )
            )

        return entities

    # ========================================================
    # Experience
    # ========================================================

    def extract_experience(
        self,
        text: str,
    ) -> List[Entity]:

        entities = []

        for match in self.EXPERIENCE_PATTERN.finditer(
            text
        ):

            entities.append(
                Entity(
                    text=match.group(),
                    label="EXPERIENCE",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.96,
                )
            )

        return entities

    # ========================================================
    # Remove Duplicate Entities
    # ========================================================

    @staticmethod
    def remove_duplicates(
        entities: List[Entity],
    ) -> List[Entity]:

        seen = set()
        result = []

        # Prefer longer entities when spans overlap.
        entities = sorted(
            entities,
            key=lambda entity: (
                entity.start,
                -(entity.end - entity.start),
            ),
        )

        for entity in entities:

            key = (
                entity.label,
                entity.start,
                entity.end,
                entity.text.lower(),
            )

            if key in seen:
                continue

            # Remove overlapping entity with same label.
            overlap = False

            for existing in result:

                if (
                    entity.label ==
                    existing.label
                    and entity.start <
                    existing.end
                    and entity.end >
                    existing.start
                ):
                    overlap = True
                    break

            if overlap:
                continue

            seen.add(key)
            result.append(entity)

        return sorted(
            result,
            key=lambda entity: entity.start,
        )

    # ========================================================
    # Extract Everything
    # ========================================================

    def extract(
        self,
        text: str,
    ) -> ExtractedEntities:

        if not text or not text.strip():
            return ExtractedEntities(
                names=[],
                emails=[],
                phones=[],
                urls=[],
                locations=[],
                organizations=[],
                job_titles=[],
                skills=[],
                degrees=[],
                certifications=[],
                dates=[],
                years=[],
                experience=[],
            )

        return ExtractedEntities(
            names=self.extract_names(text),

            emails=self.extract_emails(text),

            phones=self.extract_phones(text),

            urls=self.extract_urls(text),

            locations=self.extract_locations(text),

            organizations=self.extract_organizations(text),

            job_titles=self.extract_job_titles(text),

            skills=self.extract_skills(text),

            degrees=self.extract_degrees(text),

            certifications=self.extract_certifications(
                text
            ),

            dates=self.extract_dates(text),

            years=self.extract_years(text),

            experience=self.extract_experience(
                text
            ),
        )

    # ========================================================
    # Flat Entity List
    # ========================================================

    def extract_flat(
        self,
        text: str,
    ) -> List[Entity]:

        result = self.extract(text)

        all_entities = []

        for entities in result.to_dict().values():

            for entity_data in entities:

                all_entities.append(
                    Entity(
                        text=entity_data["text"],
                        label=entity_data["label"],
                        start=entity_data["start"],
                        end=entity_data["end"],
                        confidence=entity_data[
                            "confidence"
                        ],
                    )
                )

        return sorted(
            all_entities,
            key=lambda entity: entity.start,
        )


# ============================================================
# Helper Function
# ============================================================

def extract_resume_entities(
    resume_text: str,
) -> Dict:

    extractor = EntityExtractor()

    return extractor.extract(
        resume_text
    ).to_dict()


# ============================================================
# Example
# ============================================================

if __name__ == "__main__":

    resume = """
    JOHN DOE

    Email: john.doe@gmail.com
    Phone: +91 98765 43210

    LinkedIn: https://linkedin.com/in/johndoe
    GitHub: https://github.com/johndoe

    Location: Bangalore, India

    Professional Summary:
    Machine Learning Engineer with 4 years of experience
    building AI applications using Python, PyTorch,
    FastAPI and AWS.

    Experience:
    Machine Learning Engineer
    ABC Technologies Pvt Ltd
    2022 - Present

    Software Engineer
    XYZ Solutions Inc.
    2020 - 2022

    Education:
    B.Tech in Computer Science
    University of Technology
    2020

    Skills:
    Python, Java, SQL, PostgreSQL, FastAPI,
    React, Docker, Kubernetes, AWS,
    Machine Learning, Deep Learning,
    PyTorch, TensorFlow, Git.

    Certifications:
    AWS Certified Solutions Architect
    """

    extractor = EntityExtractor()

    result = extractor.extract(
        resume
    )

    print("=" * 70)
    print("RESUME ENTITY EXTRACTION")
    print("=" * 70)

    for category, entities in result.to_dict().items():

        print(f"\n{category.upper()}:")

        for entity in entities:

            print(
                f"  • {entity['text']}"
                f" [{entity['label']}]"
                f" ({entity['confidence']:.2f})"
            )

    print("\n" + "=" * 70)
    print("FLAT ENTITY LIST")
    print("=" * 70)

    for entity in extractor.extract_flat(
        resume
    ):

        print(
            f"{entity.label:15} | "
            f"{entity.text:40} | "
            f"{entity.confidence:.2f}"
        )