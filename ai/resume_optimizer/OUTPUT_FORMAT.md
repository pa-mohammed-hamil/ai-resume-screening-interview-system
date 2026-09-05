# Resume Optimizer Output Format

## Overview

The Resume Optimizer returns a structured `ResumeOptimizationResult` object that can be converted to a dictionary using the `to_dict()` method.

## Output Structure

```python
{
    "summary": {
        "overall_score": float,       # 0-100 weighted score
        "ats_score": float,           # 0-100
        "keyword_score": float,       # 0-100
        "content_score": float,       # 0-100
        "skill_score": float,         # 0-100
        "education_score": float,     # 0-100
        "experience_score": float,    # 0-100
        "strengths": List[str],       # List of identified strengths
        "weaknesses": List[str],      # List of identified weaknesses
        "priority_actions": List[str] # Top priority improvements
    },
    "keyword_analysis": Dict[str, Any],      # From KeywordOptimizer
    "content_analysis": Dict[str, Any],      # From ContentOptimizer
    "skill_analysis": Dict[str, Any],        # From SkillScorer
    "education_analysis": Dict[str, Any],    # From EducationScorer
    "experience_analysis": Dict[str, Any],   # From ExperienceScorer
    "ats_analysis": Dict[str, Any],          # From ATSScorer
    "optimized_bullets": List[Dict[str, Any]], # Improved bullet points
    "recommendations": List[str],            # Combined recommendations (max 20)
    "warnings": List[str]                    # Any warnings or errors
}
```

## Default Score Weights

The overall score is calculated using weighted components:

```python
DEFAULT_WEIGHTS = {
    "ats": 0.30,        # 30% - ATS compatibility
    "keyword": 0.20,    # 20% - Job keyword alignment
    "content": 0.15,    # 15% - Resume content quality
    "skill": 0.15,      # 15% - Technical skill alignment
    "experience": 0.10, # 10% - Professional experience
    "education": 0.10,  # 10% - Education alignment
}
```

**Total**: 100%

## Score Interpretation

### Overall Score Ranges
- **85-100**: Excellent - Strong match across all categories
- **75-84**: Good - Solid resume with minor improvements needed
- **50-74**: Average - Several areas need improvement
- **0-49**: Weak - Significant improvements required

### Category-Specific Scores
Each component score (ATS, keyword, content, skill, experience, education) is rated 0-100:
- **85+**: Strong performance
- **75-84**: Good performance
- **50-74**: Needs improvement
- **<50**: Weak, requires significant work

## Detailed Sections

### 1. Summary Section

```python
{
    "overall_score": 78.5,
    "ats_score": 82.0,
    "keyword_score": 75.0,
    "content_score": 80.0,
    "skill_score": 85.0,
    "education_score": 70.0,
    "experience_score": 78.0,
    "strengths": [
        "Strong technical skill alignment (85.0/100).",
        "Good ATS compatibility (82.0/100)."
    ],
    "weaknesses": [
        "Education alignment could be improved (70.0/100)."
    ],
    "priority_actions": [
        "Add truthful, job-relevant keywords where appropriate: Python, AWS, Docker.",
        "Clearly present the candidate's relevant degree, field of study, and education details."
    ]
}
```

### 2. Keyword Analysis

Contains:
- `keyword_score`: Overall keyword matching score
- `missing_keywords`: Keywords from job description not in resume
- `matched_keywords`: Keywords found in both resume and JD
- `keyword_density`: Keyword usage metrics
- `stuffing_detected`: Boolean flag for keyword stuffing
- `recommendations`: Keyword-specific suggestions

### 3. Content Analysis

Contains:
- `overall_score` or `content_score`: Content quality score
- `optimized_bullets`: List of improved bullet points
- `action_verb_usage`: Metrics on action verb usage
- `quantifiable_achievements`: Metrics/numbers found
- `recommendations`: Content improvement suggestions

### 4. Skill Analysis

Contains:
- `skill_score` or `total_score`: Skill matching score
- `matched_skills`: Skills present in both resume and JD
- `missing_skills`: Required skills not in resume
- `skill_overlap_percentage`: % of required skills present
- `recommendations`: Skill-related suggestions

### 5. Education Analysis

Contains:
- `education_score` or `total_score`: Education relevance score
- `degree_match`: Boolean or score for degree match
- `field_relevance`: Relevance of field of study
- `recommendations`: Education presentation suggestions

### 6. Experience Analysis

Contains:
- `experience_score` or `total_score`: Experience relevance score
- `years_experience`: Total years calculated
- `relevant_experience`: Job-relevant experience years
- `role_alignment`: How well experience matches role
- `recommendations`: Experience presentation suggestions

### 7. ATS Analysis

Contains:
- `ats_score` or `total_score`: ATS compatibility score
- `section_structure`: Analysis of resume sections
- `formatting_issues`: List of formatting problems
- `contact_info_present`: Boolean check
- `recommendations`: ATS improvement suggestions

### 8. Optimized Bullets

List of dictionaries containing improved bullet points:

```python
[
    {
        "original": "Worked on backend systems",
        "optimized": "Architected and deployed scalable backend microservices serving 10M+ daily requests",
        "improvement": "Added action verb and quantifiable metric",
        "score_improvement": 35
    },
    # ... more bullets
]
```

### 9. Recommendations

Combined list of actionable recommendations (max 20), prioritized:

```python
[
    "Add truthful, job-relevant keywords where appropriate: Python, AWS, Docker.",
    "Improve resume bullets with strong action verbs and measurable outcomes.",
    "Strengthen alignment between the candidate's verified skills and the target job requirements.",
    # ... more recommendations
]
```

### 10. Warnings

List of warnings or errors encountered:

```python
[
    "Potential keyword stuffing detected. Use keywords naturally and only where relevant.",
    "skill analysis unavailable: SkillScorer is not available."
]
```

## Usage Example

```python
from ai.resume_optimizer import optimize_resume

# Simple API
result_dict = optimize_resume(
    resume_text="Resume content here...",
    job_description="Job description here..."
)

# Access overall score
overall = result_dict["summary"]["overall_score"]

# Access recommendations
recommendations = result_dict["recommendations"]

# Access individual scores
ats_score = result_dict["summary"]["ats_score"]
keyword_score = result_dict["summary"]["keyword_score"]
```

## Using the ResumeOptimizer Class

```python
from ai.resume_optimizer.optimizer import ResumeOptimizer

# Create optimizer with custom weights
optimizer = ResumeOptimizer(weights={
    "ats": 0.35,
    "keyword": 0.25,
    "content": 0.15,
    "skill": 0.15,
    "experience": 0.05,
    "education": 0.05,
})

# Get result object
result = optimizer.optimize(
    resume_text="Resume content...",
    job_description="Job description..."
)

# Convert to dict
result_dict = result.to_dict()
```

## Error Handling

If a component is unavailable or fails, it returns:

```python
{
    "available": False,
    "error": "KeywordOptimizer is not available."
}
```

The optimizer continues with other available components and adds a warning to the warnings list.

## Important Notes

1. **No Fabrication**: The optimizer NEVER invents candidate experience, skills, education, metrics, certifications, or achievements
2. **Truthfulness**: All recommendations and optimized content must be grounded in actual resume information
3. **Score Scale**: All scores are 0-100 for consistency
4. **Weighted Overall**: Overall score uses weighted combination of component scores
5. **Graceful Degradation**: Missing components don't break the pipeline

## Component Availability

Each analysis section includes an `"available"` field:

```python
{
    "available": True,  # Component successfully executed
    "keyword_score": 75.0,
    # ... other data
}
```

Or if unavailable:

```python
{
    "available": False,
    "error": "KeywordOptimizer is not available."
}
```

## Output File Checklist

✅ **summary** - Always present
✅ **keyword_analysis** - Present (may be unavailable)
✅ **content_analysis** - Present (may be unavailable)
✅ **skill_analysis** - Present (may be unavailable)
✅ **education_analysis** - Present (may be unavailable)
✅ **experience_analysis** - Present (may be unavailable)
✅ **ats_analysis** - Present (may be unavailable)
✅ **optimized_bullets** - List (may be empty)
✅ **recommendations** - List (max 20 items)
✅ **warnings** - List (may be empty)

---

**Last Updated**: 2026-09-04
**File**: `ai/resume_optimizer/optimizer.py`
**Main Function**: `optimize_resume(resume_text, job_description) -> Dict[str, Any]`
