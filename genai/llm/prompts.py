# Project scaffold file
"""
Prompt templates for the AI Resume Screening & Interview System.

This module keeps LLM prompts centralized so that:
- prompts are reusable across agents/services
- prompt changes do not require business-logic changes
- outputs can be requested in predictable JSON formats
- recruiter/interview/resume workflows remain consistent
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


# ============================================================================
# Prompt Configuration
# ============================================================================


@dataclass(frozen=True)
class PromptConfig:
    """Global prompt configuration."""

    system_name: str = (
        "AI Resume Screening and Interview System"
    )

    language: str = "English"

    max_resume_length: int = 20000
    max_job_description_length: int = 15000


DEFAULT_CONFIG = PromptConfig()


# ============================================================================
# Base System Prompts
# ============================================================================


RECRUITER_SYSTEM_PROMPT = """
You are an expert AI recruiting assistant.

Your responsibilities include:
- analyzing resumes
- analyzing job descriptions
- matching candidates to jobs
- identifying relevant skills
- evaluating interview responses
- generating recruiter recommendations
- explaining scores clearly

Rules:
1. Base conclusions only on the information provided.
2. Never invent candidate qualifications.
3. Distinguish facts from reasonable inferences.
4. Do not use protected characteristics for hiring decisions.
5. Do not make discriminatory recommendations.
6. Prefer job-relevant evidence.
7. Be concise, objective, and explainable.
8. When information is missing, explicitly say so.
""".strip()


INTERVIEW_SYSTEM_PROMPT = """
You are an AI interviewer conducting a structured professional interview.

Your responsibilities include:
- asking relevant questions
- adapting question difficulty
- evaluating candidate answers
- identifying technical strengths and weaknesses
- evaluating communication quality
- providing constructive feedback

Rules:
1. Ask one primary question at a time.
2. Stay relevant to the candidate's role.
3. Do not ask discriminatory or inappropriate questions.
4. Do not evaluate protected characteristics.
5. Evaluate answers using job-relevant evidence.
6. Do not invent candidate statements.
7. Keep interview progression natural.
8. Explain evaluation criteria when requested.
""".strip()


ANALYTICS_SYSTEM_PROMPT = """
You are an AI recruiting analytics assistant.

Analyze recruiting data using objective evidence.

Focus on:
- candidate pipeline metrics
- hiring funnel performance
- interview performance
- skill distributions
- time-to-hire
- candidate quality
- ranking consistency
- fairness indicators

Never infer protected characteristics unless explicitly provided
for authorized fairness auditing, and never use such characteristics
to make hiring decisions.
""".strip()


# ============================================================================
# Resume Prompts
# ============================================================================


def resume_extraction_prompt(
    resume_text: str,
) -> str:
    """
    Extract structured information from a resume.
    """

    return f"""
Extract structured information from the resume below.

Return JSON with this structure:

{{
    "name": "",
    "email": "",
    "phone": "",
    "location": "",
    "summary": "",
    "skills": [],
    "education": [],
    "experience": [],
    "certifications": [],
    "projects": [],
    "achievements": [],
    "languages": []
}}

For experience, include:
- company
- job_title
- start_date
- end_date
- duration
- responsibilities
- technologies

For education, include:
- institution
- degree
- field
- start_date
- end_date

Do not invent information.

Resume:
---
{resume_text[:DEFAULT_CONFIG.max_resume_length]}
---
""".strip()


def resume_analysis_prompt(
    resume_text: str,
    target_role: Optional[str] = None,
) -> str:
    """
    Analyze the quality and relevance of a resume.
    """

    role_text = (
        target_role
        if target_role
        else "the candidate's apparent professional role"
    )

    return f"""
Analyze the following resume for the role:

Target role:
{role_text}

Evaluate:

1. Professional summary
2. Technical skills
3. Relevant experience
4. Education
5. Projects
6. Certifications
7. Achievements
8. Resume clarity
9. Missing information
10. Potential ATS issues

Return JSON:

{{
    "overall_score": 0,
    "strengths": [],
    "weaknesses": [],
    "technical_skills": [],
    "relevant_experience": [],
    "missing_information": [],
    "ats_issues": [],
    "recommendations": []
}}

Use a 0-100 score.

Resume:
---
{resume_text[:DEFAULT_CONFIG.max_resume_length]}
---
""".strip()


def resume_ats_prompt(
    resume_text: str,
    job_description: str,
) -> str:
    """
    Evaluate resume ATS compatibility against a JD.
    """

    return f"""
Evaluate this resume against the job description for ATS compatibility.

Analyze:

- keyword coverage
- required skills
- preferred skills
- job-title alignment
- experience alignment
- education alignment
- missing keywords
- irrelevant keywords
- formatting risks
- measurable achievements

Return JSON:

{{
    "ats_score": 0,
    "matched_keywords": [],
    "missing_keywords": [],
    "required_skills_matched": [],
    "required_skills_missing": [],
    "experience_match": 0,
    "education_match": 0,
    "formatting_issues": [],
    "recommendations": []
}}

Do not recommend adding skills that the candidate does not possess.

JOB DESCRIPTION:
---
{job_description[:DEFAULT_CONFIG.max_job_description_length]}
---

RESUME:
---
{resume_text[:DEFAULT_CONFIG.max_resume_length]}
---
""".strip()


# ============================================================================
# Job Description Prompts
# ============================================================================


def jd_analysis_prompt(
    job_description: str,
) -> str:
    """
    Analyze a job description.
    """

    return f"""
Analyze the following job description.

Extract:

- job title
- seniority
- required skills
- preferred skills
- years of experience
- education requirements
- certifications
- responsibilities
- technical requirements
- soft skills
- keywords
- measurable requirements

Return JSON:

{{
    "job_title": "",
    "seniority": "",
    "required_skills": [],
    "preferred_skills": [],
    "years_of_experience": null,
    "education_requirements": [],
    "certifications": [],
    "responsibilities": [],
    "technical_requirements": [],
    "soft_skills": [],
    "keywords": [],
    "requirements": []
}}

Do not infer requirements that are not reasonably supported
by the job description.

Job description:
---
{job_description[:DEFAULT_CONFIG.max_job_description_length]}
---
""".strip()


def jd_requirements_prompt(
    job_description: str,
) -> str:
    """
    Extract must-have and nice-to-have requirements.
    """

    return f"""
Identify the requirements in this job description.

Separate them into:

1. Must-have requirements
2. Nice-to-have requirements
3. Responsibilities
4. Technical skills
5. Soft skills
6. Experience requirements
7. Education requirements

Return JSON:

{{
    "must_have": [],
    "nice_to_have": [],
    "responsibilities": [],
    "technical_skills": [],
    "soft_skills": [],
    "experience_requirements": [],
    "education_requirements": []
}}

Job description:
---
{job_description[:DEFAULT_CONFIG.max_job_description_length]}
---
""".strip()


# ============================================================================
# Matching Prompts
# ============================================================================


def candidate_matching_prompt(
    resume_text: str,
    job_description: str,
) -> str:
    """
    Match a candidate against a job.
    """

    return f"""
Compare the candidate resume against the job description.

Evaluate only job-relevant evidence.

Analyze:

- skills match
- experience match
- education match
- responsibility match
- keyword match
- semantic relevance
- missing requirements
- strengths
- concerns

Return JSON:

{{
    "match_score": 0,
    "skills_match": 0,
    "experience_match": 0,
    "education_match": 0,
    "responsibility_match": 0,
    "matched_skills": [],
    "missing_skills": [],
    "strengths": [],
    "concerns": [],
    "explanation": ""
}}

Scores must be between 0 and 100.

JOB DESCRIPTION:
---
{job_description}
---

RESUME:
---
{resume_text}
---
""".strip()


def semantic_matching_prompt(
    candidate_profile: str,
    job_profile: str,
) -> str:
    """
    Perform semantic candidate/job matching.
    """

    return f"""
Determine the semantic similarity between the candidate profile
and the job profile.

Focus on:
- technical capabilities
- professional experience
- responsibilities
- domain relevance
- seniority
- transferable skills

Return JSON:

{{
    "semantic_score": 0,
    "strong_matches": [],
    "partial_matches": [],
    "weak_matches": [],
    "explanation": ""
}}

Candidate:
---
{candidate_profile}
---

Job:
---
{job_profile}
---
""".strip()


# ============================================================================
# Skill Intelligence Prompts
# ============================================================================


def skill_extraction_prompt(
    text: str,
) -> str:
    """
    Extract technical and professional skills.
    """

    return f"""
Extract skills from the following text.

Categorize skills into:

- programming_languages
- frameworks
- libraries
- databases
- cloud
- devops
- tools
- methodologies
- soft_skills
- domain_skills

Return JSON:

{{
    "programming_languages": [],
    "frameworks": [],
    "libraries": [],
    "databases": [],
    "cloud": [],
    "devops": [],
    "tools": [],
    "methodologies": [],
    "soft_skills": [],
    "domain_skills": []
}}

Only include skills explicitly supported by the text.

Text:
---
{text}
---
""".strip()


def skill_gap_prompt(
    candidate_skills: List[str],
    required_skills: List[str],
) -> str:
    """
    Identify skill gaps.
    """

    return f"""
Compare candidate skills against required job skills.

Candidate skills:
{candidate_skills}

Required skills:
{required_skills}

Return JSON:

{{
    "matched_skills": [],
    "missing_skills": [],
    "partial_skills": [],
    "critical_gaps": [],
    "recommendations": []
}}

Do not assume the candidate possesses a skill
unless the evidence supports it.
""".strip()


# ============================================================================
# Candidate Ranking Prompts
# ============================================================================


def candidate_ranking_prompt(
    candidates: List[Dict[str, Any]],
    job_description: str,
) -> str:
    """
    Rank candidates using job-relevant criteria.
    """

    return f"""
Rank the following candidates for the job.

Use only job-relevant factors:

- required skills
- preferred skills
- relevant experience
- education where job-relevant
- responsibilities
- demonstrated achievements

Do not use:
- name
- gender
- age
- race
- ethnicity
- religion
- disability
- marital status
- other protected characteristics

Return JSON:

{{
    "rankings": [
        {{
            "candidate_id": "",
            "rank": 0,
            "score": 0,
            "strengths": [],
            "gaps": [],
            "explanation": ""
        }}
    ]
}}

Job:
---
{job_description}
---

Candidates:
---
{candidates}
---
""".strip()


def ranking_explanation_prompt(
    candidate_name: str,
    score: float,
    strengths: List[str],
    gaps: List[str],
) -> str:
    """
    Explain a candidate ranking.
    """

    return f"""
Explain why this candidate received the given ranking.

Candidate:
{candidate_name}

Score:
{score}

Strengths:
{strengths}

Gaps:
{gaps}

Provide an objective, recruiter-friendly explanation.

Do not reference protected characteristics.
Do not invent evidence.
""".strip()


# ============================================================================
# Interview Prompts
# ============================================================================


def interview_question_prompt(
    role: str,
    candidate_profile: str,
    difficulty: str = "medium",
    question_type: str = "technical",
) -> str:
    """
    Generate an interview question.
    """

    return f"""
Generate one {question_type} interview question for:

Role:
{role}

Difficulty:
{difficulty}

Candidate profile:
---
{candidate_profile}
---

Requirements:

- Ask exactly one primary question.
- Make it relevant to the role.
- Avoid discriminatory or personal questions.
- Prefer questions that reveal practical competence.
- Do not assume experience not present in the profile.

Return JSON:

{{
    "question": "",
    "type": "{question_type}",
    "difficulty": "{difficulty}",
    "skill_assessed": "",
    "expected_signals": []
}}
""".strip()


def behavioral_question_prompt(
    role: str,
    candidate_profile: str,
) -> str:
    """
    Generate a behavioral interview question.
    """

    return f"""
Generate one behavioral interview question for the role:

{role}

Candidate profile:
---
{candidate_profile}
---

Use a STAR-oriented question that evaluates:
- teamwork
- problem solving
- ownership
- communication
- adaptability

Return JSON:

{{
    "question": "",
    "skill_assessed": "",
    "expected_signals": []
}}
""".strip()


def adaptive_question_prompt(
    role: str,
    previous_question: str,
    previous_answer: str,
    current_difficulty: str,
) -> str:
    """
    Generate the next adaptive interview question.
    """

    return f"""
You are conducting an adaptive interview.

Role:
{role}

Previous question:
{previous_question}

Candidate answer:
{previous_answer}

Current difficulty:
{current_difficulty}

Based on the quality of the answer:

- increase difficulty if the answer demonstrates strong competence
- maintain difficulty if the answer is adequate
- reduce difficulty if the answer demonstrates significant gaps

Generate exactly one next question.

Return JSON:

{{
    "question": "",
    "difficulty": "",
    "reason": "",
    "skill_assessed": ""
}}
""".strip()


# ============================================================================
# Interview Evaluation Prompts
# ============================================================================


def answer_evaluation_prompt(
    question: str,
    answer: str,
    expected_signals: Optional[List[str]] = None,
) -> str:
    """
    General interview answer evaluation.
    """

    signals = (
        expected_signals
        if expected_signals
        else []
    )

    return f"""
Evaluate the candidate's interview answer.

Question:
---
{question}
---

Answer:
---
{answer}
---

Expected signals:
{signals}

Evaluate:

- correctness
- relevance
- completeness
- reasoning
- evidence
- clarity

Return JSON:

{{
    "score": 0,
    "correctness": 0,
    "relevance": 0,
    "completeness": 0,
    "reasoning": 0,
    "evidence": 0,
    "strengths": [],
    "weaknesses": [],
    "feedback": ""
}}

All scores must be between 0 and 100.
""".strip()


def technical_evaluation_prompt(
    question: str,
    answer: str,
    expected_answer: Optional[str] = None,
) -> str:
    """
    Evaluate technical correctness.
    """

    expected = (
        expected_answer
        if expected_answer
        else "No reference answer provided."
    )

    return f"""
Evaluate the technical quality of this interview answer.

Question:
---
{question}
---

Candidate answer:
---
{answer}
---

Reference answer:
---
{expected}
---

Evaluate:

- technical correctness
- depth
- problem solving
- practical understanding
- accuracy
- use of appropriate terminology

Return JSON:

{{
    "technical_score": 0,
    "correct": true,
    "depth_score": 0,
    "problem_solving_score": 0,
    "strengths": [],
    "technical_gaps": [],
    "feedback": ""
}}

Do not penalize the candidate for using different terminology
when the underlying technical concept is correct.
""".strip()


def communication_evaluation_prompt(
    answer: str,
) -> str:
    """
    Evaluate communication quality.
    """

    return f"""
Evaluate the communication quality of the following interview answer.

Answer:
---
{answer}
---

Evaluate:

- clarity
- structure
- conciseness
- coherence
- relevance
- ability to explain ideas

Do not infer personality, intelligence, confidence,
or protected characteristics from speaking style.

Return JSON:

{{
    "communication_score": 0,
    "clarity": 0,
    "structure": 0,
    "conciseness": 0,
    "coherence": 0,
    "relevance": 0,
    "strengths": [],
    "improvements": [],
    "feedback": ""
}}
""".strip()


def confidence_evaluation_prompt(
    transcript: str,
) -> str:
    """
    Evaluate observable response characteristics.

    Note:
    Actual vocal confidence should preferably be calculated
    from acoustic/audio features rather than inferred from text.
    """

    return f"""
Analyze the transcript for observable response behavior.

Evaluate:

- hesitation markers
- uncertainty language
- answer completeness
- directness
- consistency

Do not diagnose personality.
Do not infer mental health.
Do not infer protected characteristics.

Return JSON:

{{
    "confidence_score": 0,
    "uncertainty_markers": [],
    "hesitation_markers": [],
    "strengths": [],
    "improvements": [],
    "explanation": ""
}}

Transcript:
---
{transcript}
---
""".strip()


# ============================================================================
# Interview Report
# ============================================================================


def interview_report_prompt(
    candidate_name: str,
    role: str,
    evaluations: List[Dict[str, Any]],
) -> str:
    """
    Generate a complete interview report.
    """

    return f"""
Generate a professional interview report.

Candidate:
{candidate_name}

Role:
{role}

Interview evaluations:
---
{evaluations}
---

Summarize:

- technical performance
- communication performance
- problem solving
- strengths
- weaknesses
- skill gaps
- hiring recommendation
- recommended next steps

Return JSON:

{{
    "candidate": "{candidate_name}",
    "role": "{role}",
    "overall_score": 0,
    "technical_score": 0,
    "communication_score": 0,
    "problem_solving_score": 0,
    "strengths": [],
    "weaknesses": [],
    "skill_gaps": [],
    "recommendation": "",
    "recommendation_reason": "",
    "next_steps": []
}}

Base the recommendation only on interview evidence.
""".strip()


# ============================================================================
# Resume Optimization
# ============================================================================


def resume_optimization_prompt(
    resume_text: str,
    job_description: str,
) -> str:
    """
    Generate resume optimization suggestions.
    """

    return f"""
Optimize the candidate's resume for the target job.

Important:
- Never fabricate experience.
- Never fabricate skills.
- Never fabricate metrics.
- Never change factual employment history.
- Only recommend improvements supported by existing evidence.

Return JSON:

{{
    "summary_suggestion": "",
    "keyword_suggestions": [],
    "skill_suggestions": [],
    "experience_improvements": [],
    "project_improvements": [],
    "formatting_suggestions": [],
    "missing_information": []
}}

Target job:
---
{job_description}
---

Resume:
---
{resume_text}
---
""".strip()


def resume_keyword_optimization_prompt(
    resume_text: str,
    target_keywords: List[str],
) -> str:
    """
    Suggest natural keyword placement.
    """

    return f"""
Review the resume for the target keywords.

Target keywords:
{target_keywords}

Resume:
---
{resume_text}
---

Identify:

- keywords already present
- keywords that could naturally be emphasized
- appropriate sections for placement
- keywords that should NOT be added because there is no evidence

Return JSON:

{{
    "existing_keywords": [],
    "recommended_keywords": [],
    "placement_suggestions": [],
    "unsupported_keywords": []
}}
""".strip()


# ============================================================================
# Recruiter Copilot
# ============================================================================


def recruiter_copilot_prompt(
    user_message: str,
    context: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Main recruiter copilot prompt.
    """

    context_text = (
        str(context)
        if context
        else "No additional context."
    )

    return f"""
You are a recruiter copilot.

Recruiter request:
---
{user_message}
---

Available context:
---
{context_text}
---

Help the recruiter with:

- candidate analysis
- job analysis
- interview planning
- candidate comparison
- sourcing strategy
- resume improvement
- recruiting analytics

Rules:
1. Use only available evidence.
2. Do not fabricate data.
3. Do not make decisions based on protected characteristics.
4. Explain recommendations.
5. Ask for missing information when necessary.

Return JSON:

{{
    "answer": "",
    "action": null,
    "recommendations": [],
    "follow_up_questions": []
}}
""".strip()


def recruiter_recommendation_prompt(
    candidate_data: Dict[str, Any],
    job_data: Dict[str, Any],
) -> str:
    """
    Generate recruiter recommendations.
    """

    return f"""
Generate recruiter recommendations based on:

Candidate:
---
{candidate_data}
---

Job:
---
{job_data}
---

Return JSON:

{{
    "recommendation": "",
    "priority": "",
    "reasons": [],
    "strengths": [],
    "risks": [],
    "next_actions": []
}}

Use only job-relevant information.
""".strip()


# ============================================================================
# Fairness Prompts
# ============================================================================


def fairness_analysis_prompt(
    ranking_data: List[Dict[str, Any]],
) -> str:
    """
    Analyze ranking behavior for potential fairness concerns.
    """

    return f"""
Analyze the candidate ranking data for potential fairness concerns.

Ranking data:
---
{ranking_data}
---

Evaluate:

- consistency
- feature relevance
- potential proxy variables
- unexplained ranking differences
- whether job-relevant criteria appear to dominate

Do not make hiring decisions.

Return JSON:

{{
    "fairness_risk": "low",
    "risk_score": 0,
    "potential_issues": [],
    "proxy_features": [],
    "recommendations": []
}}

Important:
Protected characteristics must not be used as ranking features.
""".strip()


# ============================================================================
# Analytics Prompts
# ============================================================================


def recruiting_analytics_prompt(
    metrics: Dict[str, Any],
) -> str:
    """
    Analyze recruiting metrics.
    """

    return f"""
Analyze these recruiting metrics.

Metrics:
---
{metrics}
---

Identify:

- important trends
- anomalies
- bottlenecks
- candidate funnel issues
- interview patterns
- actionable recommendations

Return JSON:

{{
    "summary": "",
    "key_trends": [],
    "anomalies": [],
    "bottlenecks": [],
    "recommendations": []
}}
""".strip()


# ============================================================================
# Generic Prompt Utilities
# ============================================================================


def build_system_prompt(
    domain: str = "recruiting",
) -> str:
    """
    Return an appropriate system prompt.
    """

    domain = (
        domain.lower().strip()
    )

    if domain == "interview":
        return INTERVIEW_SYSTEM_PROMPT

    if domain == "analytics":
        return ANALYTICS_SYSTEM_PROMPT

    return RECRUITER_SYSTEM_PROMPT


def build_json_instruction(
    fields: List[str],
) -> str:
    """
    Build a generic JSON output instruction.
    """

    schema = {
        field: None
        for field in fields
    }

    return f"""
Return ONLY valid JSON.

Expected fields:
{schema}
""".strip()


def truncate_text(
    text: str,
    max_length: int,
) -> str:
    """
    Safely truncate long prompt inputs.
    """

    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return (
        text[:max_length]
        + "\n\n[Content truncated]"
    )


# ============================================================================
# Prompt Registry
# ============================================================================


PROMPT_REGISTRY = {
    "resume_extraction": resume_extraction_prompt,
    "resume_analysis": resume_analysis_prompt,
    "resume_ats": resume_ats_prompt,
    "jd_analysis": jd_analysis_prompt,
    "jd_requirements": jd_requirements_prompt,
    "candidate_matching": candidate_matching_prompt,
    "semantic_matching": semantic_matching_prompt,
    "skill_extraction": skill_extraction_prompt,
    "skill_gap": skill_gap_prompt,
    "candidate_ranking": candidate_ranking_prompt,
    "ranking_explanation": ranking_explanation_prompt,
    "interview_question": interview_question_prompt,
    "behavioral_question": behavioral_question_prompt,
    "adaptive_question": adaptive_question_prompt,
    "answer_evaluation": answer_evaluation_prompt,
    "technical_evaluation": technical_evaluation_prompt,
    "communication_evaluation": communication_evaluation_prompt,
    "confidence_evaluation": confidence_evaluation_prompt,
    "interview_report": interview_report_prompt,
    "resume_optimization": resume_optimization_prompt,
    "resume_keyword_optimization": (
        resume_keyword_optimization_prompt
    ),
    "recruiter_copilot": recruiter_copilot_prompt,
    "recruiter_recommendation": (
        recruiter_recommendation_prompt
    ),
    "fairness_analysis": fairness_analysis_prompt,
    "recruiting_analytics": (
        recruiting_analytics_prompt
    ),
}


__all__ = [
    "PromptConfig",
    "DEFAULT_CONFIG",
    "RECRUITER_SYSTEM_PROMPT",
    "INTERVIEW_SYSTEM_PROMPT",
    "ANALYTICS_SYSTEM_PROMPT",
    "resume_extraction_prompt",
    "resume_analysis_prompt",
    "resume_ats_prompt",
    "jd_analysis_prompt",
    "jd_requirements_prompt",
    "candidate_matching_prompt",
    "semantic_matching_prompt",
    "skill_extraction_prompt",
    "skill_gap_prompt",
    "candidate_ranking_prompt",
    "ranking_explanation_prompt",
    "interview_question_prompt",
    "behavioral_question_prompt",
    "adaptive_question_prompt",
    "answer_evaluation_prompt",
    "technical_evaluation_prompt",
    "communication_evaluation_prompt",
    "confidence_evaluation_prompt",
    "interview_report_prompt",
    "resume_optimization_prompt",
    "resume_keyword_optimization_prompt",
    "recruiter_copilot_prompt",
    "recruiter_recommendation_prompt",
    "fairness_analysis_prompt",
    "recruiting_analytics_prompt",
    "build_system_prompt",
    "build_json_instruction",
    "truncate_text",
    "PROMPT_REGISTRY",
]