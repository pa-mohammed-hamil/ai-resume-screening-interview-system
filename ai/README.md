# AI Module

The `ai/` module contains the core Artificial Intelligence and Natural Language Processing components of the **AI Resume Screening & Interview System**.

It is responsible for transforming raw resumes and job descriptions into structured information, matching candidates to jobs, scoring candidates, ranking candidates, optimizing resumes, and evaluating fairness.

---

## 1. Module Architecture

```text
ai/
│
├── README.md
│
├── resume_parser/
│   ├── __init__.py
│   ├── parser.py
│   ├── pdf_parser.py
│   ├── docx_parser.py
│   └── text_cleaner.py
│
├── information_extraction/
│   ├── __init__.py
│   ├── extractor.py
│   ├── entity_extractor.py
│   ├── education_extractor.py
│   ├── experience_extractor.py
│   └── contact_extractor.py
│
├── skill_intelligence/
│   ├── __init__.py
│   ├── skill_extractor.py
│   ├── skill_normalizer.py
│   ├── skill_taxonomy.py
│   └── skill_gap.py
│
├── jd_analysis/
│   ├── __init__.py
│   ├── jd_parser.py
│   ├── requirement_extractor.py
│   ├── responsibility_extractor.py
│   └── jd_scorer.py
│
├── matching/
│   ├── __init__.py
│   ├── resume_job_matcher.py
│   ├── semantic_matcher.py
│   └── keyword_matcher.py
│
├── scoring/
│   ├── __init__.py
│   ├── ats_scorer.py
│   ├── skill_scorer.py
│   ├── experience_scorer.py
│   └── education_scorer.py
│
├── ranking/
│   ├── __init__.py
│   ├── candidate_ranker.py
│   ├── ranking_features.py
│   └── ranking_explainer.py
│
├── resume_optimizer/
│   ├── __init__.py
│   ├── optimizer.py
│   ├── keyword_optimizer.py
│   ├── content_optimizer.py
│   └── suggestions.py
│
└── fairness/
    ├── __init__.py
    ├── bias_detector.py
    ├── fairness_metrics.py
    └── fairness_report.py
```

---

# 2. AI Pipeline

The primary AI pipeline is:

```text
Resume PDF / DOCX
       │
       ▼
┌──────────────────────┐
│   Resume Parser      │
│ PDF / DOCX / Text    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    Text Cleaner      │
└──────────┬───────────┘
           │
           ▼
┌────────────────────────────┐
│ Information Extraction     │
│                            │
│ • Contact                  │
│ • Education                │
│ • Experience               │
│ • Entities                 │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ Skill Intelligence         │
│                            │
│ • Skill extraction         │
│ • Normalization            │
│ • Taxonomy                 │
│ • Skill gap                │
└────────────┬───────────────┘
             │
             ▼
      Structured Resume
             │
             ▼
┌────────────────────────────┐
│ Job Description Analysis   │
│                            │
│ • Requirements             │
│ • Responsibilities         │
│ • JD score                 │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ Resume ↔ Job Matching      │
│                            │
│ • Keyword matching         │
│ • Semantic matching        │
│ • Hybrid matching          │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ Candidate Scoring          │
│                            │
│ • ATS score                │
│ • Skill score              │
│ • Experience score         │
│ • Education score          │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ Candidate Ranking          │
│                            │
│ • Ranking features         │
│ • Candidate rank           │
│ • Explanation              │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ Fairness Evaluation        │
│                            │
│ • Bias detection           │
│ • Fairness metrics         │
│ • Fairness report          │
└────────────────────────────┘
```

---

# 3. Resume Parser

Location:

```text
ai/resume_parser/
```

The resume parser converts uploaded documents into clean text.

### `parser.py`

Main parser/orchestrator.

Responsibilities:

* Detect file type.
* Select the appropriate parser.
* Parse PDF/DOCX/text.
* Normalize parser output.
* Return structured parsing results.

Example:

```python
from ai.resume_parser.parser import ResumeParser

parser = ResumeParser()

result = parser.parse(
    "resume.pdf"
)

print(result)
```

### `pdf_parser.py`

Responsible for extracting text from PDF resumes.

Typical responsibilities:

* PDF text extraction.
* Page processing.
* Metadata handling.
* Basic layout preservation.

### `docx_parser.py`

Responsible for extracting text from Microsoft Word documents.

Handles:

* Paragraphs.
* Tables.
* Headings.
* Basic document structure.

### `text_cleaner.py`

Normalizes extracted resume text.

Operations include:

* Whitespace normalization.
* Duplicate line removal.
* Unicode normalization.
* Broken line cleanup.
* Header/footer cleanup.
* Special-character normalization.

---

# 4. Information Extraction

Location:

```text
ai/information_extraction/
```

This layer transforms unstructured resume text into structured candidate information.

## `extractor.py`

Central extraction orchestrator.

Example:

```python
from ai.information_extraction.extractor import ResumeInformationExtractor

extractor = ResumeInformationExtractor()

result = extractor.extract(
    resume_text
)
```

Expected output:

```json
{
  "contact": {},
  "education": [],
  "experience": [],
  "entities": []
}
```

## `contact_extractor.py`

Extracts:

* Name
* Email
* Phone
* Location
* LinkedIn
* GitHub
* Portfolio
* Website

## `education_extractor.py`

Extracts:

* Institution
* Degree
* Field of study
* Start date
* End date
* GPA
* Percentage
* Grade

## `experience_extractor.py`

Extracts:

* Company
* Job title
* Employment dates
* Responsibilities
* Achievements
* Technologies
* Experience duration

## `entity_extractor.py`

Extracts important entities such as:

* Organizations
* Technologies
* Tools
* Job titles
* Locations
* Certifications
* Projects

---

# 5. Skill Intelligence

Location:

```text
ai/skill_intelligence/
```

This module converts raw skill mentions into normalized skills.

## `skill_extractor.py`

Identifies skills from:

* Resume text
* Experience descriptions
* Projects
* Job descriptions
* Certifications

Example:

```text
Python
Python programming
Python 3
Py
```

can be identified as variations of the same underlying skill.

## `skill_normalizer.py`

Normalizes skill names.

Example:

```text
"JS"                → "JavaScript"
"React.js"           → "React"
"Postgre SQL"        → "PostgreSQL"
"ML"                 → "Machine Learning"
"Amazon Web Services"→ "AWS"
```

## `skill_taxonomy.py`

Defines the skill hierarchy.

Example:

```text
Programming
├── Python
├── Java
├── JavaScript
└── C++

Web Development
├── React
├── Angular
├── Vue
├── HTML
└── CSS

Cloud
├── AWS
├── Azure
└── GCP

AI / ML
├── Machine Learning
├── Deep Learning
├── NLP
├── Computer Vision
└── Generative AI
```

## `skill_gap.py`

Compares candidate skills against job requirements.

Example:

```json
{
  "matched_skills": [
    "Python",
    "FastAPI",
    "PostgreSQL"
  ],
  "missing_skills": [
    "AWS",
    "Docker"
  ],
  "match_percentage": 75
}
```

---

# 6. Job Description Analysis

Location:

```text
ai/jd_analysis/
```

This module analyzes job descriptions before matching candidates.

## `jd_parser.py`

Extracts and cleans raw job-description text.

## `requirement_extractor.py`

Identifies:

* Required skills
* Preferred skills
* Education requirements
* Experience requirements
* Certifications
* Domain knowledge

Example:

```text
Required:
Python
FastAPI
PostgreSQL

Preferred:
AWS
Docker
Kubernetes
```

## `responsibility_extractor.py`

Identifies responsibilities such as:

```text
Develop REST APIs
Build ML pipelines
Deploy applications
Collaborate with engineering teams
```

## `jd_scorer.py`

Produces a quality/structure score for the job description.

Potential dimensions:

```text
Skill clarity
Experience clarity
Education clarity
Responsibility clarity
Requirement completeness
```

---

# 7. Resume-Job Matching

Location:

```text
ai/matching/
```

The matching system combines multiple signals.

## Keyword Matching

Implemented in:

```text
keyword_matcher.py
```

Matches explicit terms.

Example:

```text
Resume:
Python, FastAPI, Docker

JD:
Python, FastAPI, Docker, AWS
```

Keyword match:

```text
3 / 4 = 75%
```

## Semantic Matching

Implemented in:

```text
semantic_matcher.py
```

Uses semantic representations to identify conceptually similar skills and experience.

For example:

```text
"REST API development"
```

can be semantically related to:

```text
"FastAPI backend development"
```

## Hybrid Matching

Implemented in:

```text
resume_job_matcher.py
```

Combines:

```text
Keyword similarity
        +
Semantic similarity
        +
Skill overlap
        +
Experience compatibility
        +
Education compatibility
```

Example conceptual formula:

```text
Match Score =
    0.35 × Semantic Score
  + 0.30 × Skill Score
  + 0.20 × Keyword Score
  + 0.10 × Experience Score
  + 0.05 × Education Score
```

The weights should be configurable rather than hard-coded when used in production.

---

# 8. Candidate Scoring

Location:

```text
ai/scoring/
```

## `ats_scorer.py`

Calculates an ATS-oriented resume score.

Possible dimensions:

```text
Keyword coverage
Skill coverage
Formatting quality
Section completeness
Experience relevance
Education relevance
```

Example:

```json
{
  "ats_score": 84,
  "keyword_score": 88,
  "skill_score": 90,
  "experience_score": 80,
  "education_score": 78
}
```

## `skill_scorer.py`

Measures how well candidate skills satisfy job requirements.

## `experience_scorer.py`

Evaluates:

* Years of experience
* Relevant experience
* Job-title alignment
* Responsibility alignment
* Industry/domain alignment

## `education_scorer.py`

Evaluates:

* Degree compatibility
* Field compatibility
* Education level
* Required qualifications

---

# 9. Candidate Ranking

Location:

```text
ai/ranking/
```

The ranking system orders candidates for a particular job.

## `ranking_features.py`

Creates features such as:

```text
skill_match
semantic_match
keyword_match
experience_match
education_match
ats_score
```

## `candidate_ranker.py`

Produces the candidate ranking.

Example:

```text
1. Candidate A — 91.4
2. Candidate B — 87.9
3. Candidate C — 82.6
4. Candidate D — 77.1
```

## `ranking_explainer.py`

Provides human-readable explanations.

Example:

```text
Candidate A ranked #1 because:

+ Strong Python experience
+ 92% required-skill coverage
+ 5 years relevant experience
+ Strong semantic alignment

Missing:
- Kubernetes
```

The explanation layer is important because recruiters should be able to understand why a candidate received a particular score.

---

# 10. Resume Optimizer

Location:

```text
ai/resume_optimizer/
```

The optimizer recommends improvements to a resume for a target job.

## `optimizer.py`

Main optimization orchestrator.

## `keyword_optimizer.py`

Finds relevant keywords missing from the resume.

Example:

```text
Missing keywords:

AWS
Docker
Kubernetes
CI/CD
```

## `content_optimizer.py`

Suggests improvements to:

* Professional summary
* Experience bullets
* Project descriptions
* Skills section

## `suggestions.py`

Produces actionable recommendations.

Example:

```json
{
  "priority": "high",
  "section": "experience",
  "suggestion": "Add measurable outcomes to project descriptions."
}
```

---

# 11. Fairness

Location:

```text
ai/fairness/
```

The fairness module helps identify potentially problematic patterns in candidate scoring and ranking.

## `bias_detector.py`

Detects potentially sensitive or problematic signals.

The ranking system should avoid using protected characteristics such as:

* Gender
* Race/ethnicity
* Religion
* Age
* Disability
* Other legally protected characteristics

The system should also avoid indirect proxy features where appropriate.

## `fairness_metrics.py`

Provides statistical fairness measurements.

Possible metrics include:

```text
Selection rate
Selection-rate ratio
False-positive rate
False-negative rate
Group-level score distributions
```

## `fairness_report.py`

Generates a structured fairness report.

Example:

```json
{
  "status": "review_required",
  "metrics": {},
  "potential_issues": [],
  "recommendations": []
}
```

Fairness analysis should be treated as a decision-support mechanism rather than proof that an automated hiring system is legally or ethically compliant.

---

# 12. AI Data Flow

```text
                    ┌──────────────────┐
                    │ Resume / JD File │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Document Parser  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Text Cleaner     │
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
    ┌──────────────────┐          ┌──────────────────┐
    │ Resume Extraction│          │ JD Analysis      │
    └────────┬─────────┘          └────────┬─────────┘
             │                             │
             ▼                             ▼
    ┌──────────────────┐          ┌──────────────────┐
    │ Skill Intelligence│         │ Requirements     │
    └────────┬─────────┘          └────────┬─────────┘
             │                             │
             └──────────────┬──────────────┘
                            ▼
                   ┌──────────────────┐
                   │ Matching Engine  │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │ Scoring Engine   │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │ Ranking Engine   │
                   └────────┬─────────┘
                            │
                   ┌────────┴────────┐
                   ▼                 ▼
          ┌────────────────┐  ┌────────────────┐
          │ Explanation    │  │ Fairness Check │
          └────────────────┘  └────────────────┘
```

---

# 13. Example End-to-End Usage

```python
from ai.resume_parser.parser import ResumeParser
from ai.information_extraction.extractor import (
    ResumeInformationExtractor,
)
from ai.skill_intelligence.skill_extractor import (
    SkillExtractor,
)
from ai.jd_analysis.jd_parser import JDParser
from ai.matching.resume_job_matcher import (
    ResumeJobMatcher,
)


# 1. Parse resume
resume_parser = ResumeParser()

resume_result = resume_parser.parse(
    "resume.pdf"
)

resume_text = resume_result["text"]


# 2. Extract resume information
information_extractor = (
    ResumeInformationExtractor()
)

resume_data = information_extractor.extract(
    resume_text
)


# 3. Extract skills
skill_extractor = SkillExtractor()

skills = skill_extractor.extract(
    resume_text
)


# 4. Parse job description
jd_parser = JDParser()

job_data = jd_parser.parse(
    job_description
)


# 5. Match resume to job
matcher = ResumeJobMatcher()

match_result = matcher.match(
    resume_data=resume_data,
    job_data=job_data,
)
```

---

# 14. Design Principles

The AI module follows these principles:

### Modular

Each AI capability is isolated into a dedicated module.

### Explainable

Scores and rankings should have understandable explanations.

### Configurable

Weights, thresholds, taxonomies, and model configuration should be configurable.

### Testable

Each AI component should have unit tests and evaluation datasets.

### Deterministic Where Possible

Rule-based extraction and normalization should produce stable results.

### Model-Agnostic

LLM and embedding providers should not be tightly coupled to the AI business logic.

### Privacy-Aware

Resume and candidate information should be handled securely and should not be logged unnecessarily.

### Fairness-Aware

Candidate ranking should be monitored for unintended bias and problematic proxy signals.

---

# 15. Testing

AI components are tested under:

```text
tests/
├── unit/
│   ├── test_resume_parser.py
│   ├── test_matching.py
│   ├── test_scoring.py
│   └── test_ranking.py
│
└── evaluation/
    ├── test_resume_accuracy.py
    ├── test_matching_accuracy.py
    ├── test_ranking_accuracy.py
    └── test_fairness.py
```

Evaluation datasets are stored under:

```text
data/evaluation/
├── test_resumes/
├── test_jobs/
└── expected_results/
```

---

# 16. Recommended Dependencies

Depending on the implementation, the AI layer may use:

```text
PyMuPDF / pdfplumber
python-docx
spaCy
scikit-learn
sentence-transformers
numpy
pandas
```

LLM and embedding dependencies should be isolated behind provider interfaces rather than imported throughout the application.

---

# 17. Production Considerations

For production deployment:

1. Store uploaded resumes outside the application source tree.
2. Validate uploaded file types and sizes.
3. Scan uploaded files for malicious content.
4. Avoid logging raw resume contents.
5. Encrypt sensitive candidate data at rest and in transit.
6. Add authentication and authorization around candidate data.
7. Version scoring and ranking algorithms.
8. Store model/version metadata with generated scores.
9. Keep audit logs for important automated decisions.
10. Monitor extraction, matching, ranking, and fairness metrics.
11. Allow recruiters to review and override automated recommendations.
12. Do not represent AI ranking as an unquestionable hiring decision.

---

# 18. Module Responsibilities

| Module                   | Primary Responsibility                    |
| ------------------------ | ----------------------------------------- |
| `resume_parser`          | Convert resume files into text            |
| `information_extraction` | Extract structured candidate information  |
| `skill_intelligence`     | Extract, normalize, and compare skills    |
| `jd_analysis`            | Analyze job descriptions                  |
| `matching`               | Match resumes against jobs                |
| `scoring`                | Calculate candidate/job scores            |
| `ranking`                | Rank and explain candidates               |
| `resume_optimizer`       | Recommend resume improvements             |
| `fairness`               | Detect and measure potential ranking bias |

---

# 19. Overall AI Architecture

```text
                         AI RESUME SYSTEM
                                │
        ┌───────────────────────┼────────────────────────┐
        │                       │                        │
        ▼                       ▼                        ▼
 Resume Processing        Job Processing          AI Intelligence
        │                       │                        │
        ▼                       ▼                        ▼
 Resume Parser             JD Parser             Skill Intelligence
        │                       │                        │
        ▼                       ▼                        ▼
 Information              Requirements             Matching
 Extraction               Extraction                   │
        │                       │                        ▼
        └───────────────┬───────┘                    Scoring
                        │                              │
                        ▼                              ▼
                 Resume ↔ Job Match              Ranking
                                                       │
                          ┌────────────────────────────┤
                          │                            │
                          ▼                            ▼
                   Explanation                  Fairness Check
                          │                            │
                          └──────────────┬─────────────┘
                                         ▼
                                Recruiter Dashboard
```

The `ai/` package is the intelligence layer between raw candidate/job documents and the backend services that expose matching, scoring, ranking, optimization, and fairness functionality to the application.
