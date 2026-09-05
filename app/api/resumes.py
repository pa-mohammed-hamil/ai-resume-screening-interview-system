"""
Resumes API endpoints (Mock Implementation)
Provides resume upload, parsing, and analysis without database/file storage for demo purposes
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.core.config import settings
from app.services.resume_service import ResumeProcessingService

router = APIRouter()


# Mock resume storage (in-memory for demo)
MOCK_RESUMES = {
    1: {
        "id": 1,
        "candidate_id": 1,
        "candidate_name": "John Smith",
        "filename": "john_smith_resume.pdf",
        "file_type": "application/pdf",
        "file_size": 245678,
        "file_url": "/storage/resumes/john_smith_resume.pdf",
        "status": "parsed",
        "parsed_data": {
            "personal_info": {
                "name": "John Smith",
                "email": "john.smith@email.com",
                "phone": "+1-555-0101",
                "location": "San Francisco, CA",
                "linkedin": "linkedin.com/in/johnsmith",
                "github": "github.com/johnsmith",
            },
            "summary": "Senior Software Engineer with 8+ years of experience in Python, FastAPI, and cloud technologies. Proven track record of building scalable backend systems.",
            "experience": [
                {
                    "title": "Senior Software Engineer",
                    "company": "Tech Corp",
                    "location": "San Francisco, CA",
                    "start_date": "2020-01",
                    "end_date": "Present",
                    "duration": "4 years",
                    "description": "Led backend development team, architected microservices, mentored junior developers"
                },
                {
                    "title": "Software Engineer",
                    "company": "StartupXYZ",
                    "location": "San Francisco, CA",
                    "start_date": "2016-06",
                    "end_date": "2019-12",
                    "duration": "3.5 years",
                    "description": "Developed REST APIs, implemented CI/CD pipelines, optimized database queries"
                }
            ],
            "education": [
                {
                    "degree": "BS Computer Science",
                    "school": "Stanford University",
                    "location": "Stanford, CA",
                    "graduation_year": "2016",
                    "gpa": "3.8"
                }
            ],
            "skills": {
                "programming_languages": ["Python", "JavaScript", "Go", "SQL"],
                "frameworks": ["FastAPI", "Django", "React", "Flask"],
                "tools": ["Docker", "Kubernetes", "AWS", "PostgreSQL", "Redis"],
                "soft_skills": ["Leadership", "Communication", "Problem Solving"]
            },
            "certifications": [
                "AWS Certified Solutions Architect",
                "Certified Kubernetes Administrator"
            ],
            "projects": [
                {
                    "name": "E-commerce Platform",
                    "description": "Built scalable microservices handling 1M+ requests/day",
                    "technologies": ["Python", "FastAPI", "PostgreSQL", "Redis"]
                }
            ]
        },
        "ai_analysis": {
            "overall_quality_score": 92,
            "experience_score": 95,
            "skills_score": 90,
            "education_score": 88,
            "formatting_score": 94,
            "key_strengths": [
                "Extensive Python experience",
                "Strong backend architecture skills",
                "Cloud platform expertise",
                "Leadership experience"
            ],
            "areas_for_improvement": [
                "Could mention more specific project metrics",
                "Add more certifications"
            ],
            "recommended_roles": [
                "Senior Backend Engineer",
                "Staff Software Engineer",
                "Tech Lead",
                "Solutions Architect"
            ],
            "salary_estimate": {
                "min": 140000,
                "max": 180000,
                "currency": "USD"
            }
        },
        "match_jobs": [
            {"job_id": 1, "job_title": "Senior Python Developer", "match_score": 92.5}
        ],
        "created_at": "2026-08-25T09:30:00",
        "updated_at": "2026-08-25T09:35:00",
    },
    2: {
        "id": 2,
        "candidate_id": 2,
        "candidate_name": "Sarah Johnson",
        "filename": "sarah_johnson_resume.pdf",
        "file_type": "application/pdf",
        "file_size": 198432,
        "file_url": "/storage/resumes/sarah_johnson_resume.pdf",
        "status": "parsed",
        "parsed_data": {
            "personal_info": {
                "name": "Sarah Johnson",
                "email": "sarah.j@email.com",
                "phone": "+1-555-0102",
                "location": "Remote",
                "linkedin": "linkedin.com/in/sarahjohnson",
                "github": "github.com/sarahj",
            },
            "summary": "Frontend Developer specializing in React and modern JavaScript. 5 years of experience building responsive web applications.",
            "experience": [
                {
                    "title": "Frontend Developer",
                    "company": "WebTech Inc",
                    "location": "Remote",
                    "start_date": "2019-03",
                    "end_date": "Present",
                    "duration": "5 years",
                    "description": "Built React applications, optimized performance, collaborated with design team"
                }
            ],
            "education": [
                {
                    "degree": "BS Software Engineering",
                    "school": "MIT",
                    "location": "Cambridge, MA",
                    "graduation_year": "2019",
                    "gpa": "3.9"
                }
            ],
            "skills": {
                "programming_languages": ["JavaScript", "TypeScript", "HTML", "CSS"],
                "frameworks": ["React", "Next.js", "Redux", "Tailwind CSS"],
                "tools": ["Git", "Webpack", "Jest", "Figma"],
                "soft_skills": ["Design sense", "Collaboration", "Attention to detail"]
            },
            "certifications": [],
            "projects": []
        },
        "ai_analysis": {
            "overall_quality_score": 85,
            "experience_score": 82,
            "skills_score": 88,
            "education_score": 92,
            "formatting_score": 86,
            "key_strengths": [
                "Strong React expertise",
                "Modern frontend stack",
                "Top university education"
            ],
            "areas_for_improvement": [
                "Add more projects",
                "Include certifications",
                "Diversify technology stack"
            ],
            "recommended_roles": [
                "Frontend Developer",
                "React Developer",
                "UI Engineer"
            ],
            "salary_estimate": {
                "min": 100000,
                "max": 130000,
                "currency": "USD"
            }
        },
        "match_jobs": [
            {"job_id": 2, "job_title": "Frontend React Developer", "match_score": 88.0}
        ],
        "created_at": "2026-08-26T11:00:00",
        "updated_at": "2026-08-26T11:05:00",
    },
}

NEXT_RESUME_ID = 3


# Allowed file types
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


# Request/Response Models
class ResumeUpdate(BaseModel):
    status: Optional[str] = None


class MatchJobsRequest(BaseModel):
    job_ids: List[int]


# ============================================================================
# Upload Resume
# ============================================================================

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and parse a resume file with full AI pipeline.
    
    Pipeline:
    1. Save file to storage
    2. Parse PDF/DOCX to extract text
    3. Clean and normalize text
    4. Extract structured information (contact, experience, education, skills)
    5. Perform AI analysis
    6. Calculate scores
    7. Return results
    """
    global NEXT_RESUME_ID
    
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume filename is required",
        )
    
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only PDF, DOC, and DOCX files are supported. Got: {file.content_type}",
        )
    
    # Save file to storage
    storage_path = Path(settings.RESUME_STORAGE_PATH)
    storage_path.mkdir(parents=True, exist_ok=True)
    
    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = storage_path / safe_filename
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        file_size = len(content)
        
        # Process resume through AI pipeline
        processing_result = await ResumeProcessingService.process_resume(file_path)
        
        # Create new resume record
        resume_id = NEXT_RESUME_ID
        NEXT_RESUME_ID += 1
        
        now = datetime.now().isoformat()
        
        # Extract candidate name from AI analysis
        candidate_name = "New Candidate"
        if processing_result.get("ai_analysis", {}).get("contact", {}).get("name"):
            candidate_name = processing_result["ai_analysis"]["contact"]["name"]
        
        new_resume = {
            "id": resume_id,
            "candidate_id": None,
            "candidate_name": candidate_name,
            "filename": file.filename,
            "file_type": file.content_type,
            "file_size": file_size,
            "file_url": f"/storage/resumes/{safe_filename}",
            "status": processing_result["status"],
            "parsed_data": processing_result.get("parsed_data", {}),
            "ai_analysis": processing_result.get("ai_analysis", {}),
            "scores": processing_result.get("scores", {}),
            "match_jobs": [],
            "errors": processing_result.get("errors", []),
            "created_at": now,
            "updated_at": now,
        }
        
        # Store resume
        MOCK_RESUMES[resume_id] = new_resume
        
        return {
            "success": True,
            "message": f"Resume uploaded and processed successfully! Score: {processing_result.get('scores', {}).get('overall', 0)}/100",
            "data": new_resume,
        }
        
    except Exception as e:
        # Clean up file if processing failed
        if file_path.exists():
            file_path.unlink()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process resume: {str(e)}"
        )


# ============================================================================
# List Resumes
# ============================================================================

@router.get("/")
def list_resumes(
    status: Optional[str] = None,
    candidate_id: Optional[int] = None,
):
    """
    Get all resumes with optional filters.
    
    This is a mock implementation that returns in-memory resumes.
    In production, this would query a database.
    """
    
    # Get all resumes
    resumes = list(MOCK_RESUMES.values())
    
    # Apply filters
    if status:
        resumes = [r for r in resumes if r["status"] == status]
    
    if candidate_id:
        resumes = [r for r in resumes if r["candidate_id"] == candidate_id]
    
    # Sort by created date (newest first)
    resumes = sorted(resumes, key=lambda x: x["created_at"], reverse=True)
    
    return {
        "success": True,
        "count": len(resumes),
        "data": resumes,
    }


# ============================================================================
# Get Resume by ID
# ============================================================================

@router.get("/{resume_id}")
def get_resume(resume_id: int):
    """
    Get detailed resume information.
    
    This is a mock implementation that retrieves from in-memory storage.
    In production, this would query a database.
    """
    
    # Check if resume exists
    if resume_id not in MOCK_RESUMES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found",
        )
    
    resume = MOCK_RESUMES[resume_id]
    
    return {
        "success": True,
        "data": resume,
    }


# ============================================================================
# Update Resume
# ============================================================================

@router.put("/{resume_id}")
def update_resume(resume_id: int, payload: ResumeUpdate):
    """
    Update resume metadata.
    
    This is a mock implementation that updates in-memory storage.
    In production, this would update a database.
    """
    
    # Check if resume exists
    if resume_id not in MOCK_RESUMES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found",
        )
    
    resume = MOCK_RESUMES[resume_id]
    
    # Update fields
    if payload.status:
        resume["status"] = payload.status
    
    resume["updated_at"] = datetime.now().isoformat()
    
    return {
        "success": True,
        "message": "Resume updated successfully",
        "data": resume,
    }


# ============================================================================
# Delete Resume
# ============================================================================

@router.delete("/{resume_id}")
def delete_resume(resume_id: int):
    """
    Delete a resume.
    
    This is a mock implementation that removes from in-memory storage.
    In production, this would delete file from storage and database record.
    """
    
    # Check if resume exists
    if resume_id not in MOCK_RESUMES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found",
        )
    
    # Delete resume
    deleted_resume = MOCK_RESUMES.pop(resume_id)
    
    return {
        "success": True,
        "message": "Resume deleted successfully",
        "data": deleted_resume,
    }


# ============================================================================
# Analyze Resume with AI
# ============================================================================

@router.post("/{resume_id}/analyze")
def analyze_resume(resume_id: int):
    """
    Run AI analysis on a resume to extract insights.
    
    This is a mock implementation that returns simulated AI analysis.
    In production, this would:
    - Use OpenAI/Anthropic to analyze resume
    - Extract skills, experience, education
    - Generate recommendations
    - Calculate quality scores
    """
    
    # Check if resume exists
    if resume_id not in MOCK_RESUMES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found",
        )
    
    resume = MOCK_RESUMES[resume_id]
    
    # Mock AI analysis (in production, would call AI service)
    ai_analysis = {
        "overall_quality_score": 87,
        "experience_score": 85,
        "skills_score": 88,
        "education_score": 86,
        "formatting_score": 89,
        "key_strengths": [
            "Well-structured resume",
            "Clear experience progression",
            "Relevant technical skills"
        ],
        "areas_for_improvement": [
            "Add more quantifiable achievements",
            "Include project links or portfolio",
            "Add professional summary"
        ],
        "recommended_roles": [
            "Software Engineer",
            "Backend Developer",
            "Full-Stack Developer"
        ],
        "salary_estimate": {
            "min": 90000,
            "max": 130000,
            "currency": "USD"
        },
        "analyzed_at": datetime.now().isoformat(),
    }
    
    # Update resume with analysis
    resume["ai_analysis"] = ai_analysis
    resume["status"] = "analyzed"
    resume["updated_at"] = datetime.now().isoformat()
    
    return {
        "success": True,
        "message": "Resume analysis completed",
        "data": ai_analysis,
    }


# ============================================================================
# Match Resume with Jobs
# ============================================================================

@router.post("/{resume_id}/match")
def match_resume_with_jobs(resume_id: int, payload: MatchJobsRequest):
    """
    Match resume with job postings.
    
    This is a mock implementation that simulates ML-based matching.
    In production, this would:
    - Use embeddings to calculate similarity
    - Consider skills, experience, location
    - Rank jobs by match score
    """
    
    # Check if resume exists
    if resume_id not in MOCK_RESUMES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found",
        )
    
    resume = MOCK_RESUMES[resume_id]
    
    # Mock matching algorithm
    matches = []
    for job_id in payload.job_ids:
        # Simulate match score calculation
        match_score = round(75 + (job_id * 3.5) % 20, 1)
        matches.append({
            "job_id": job_id,
            "job_title": f"Job {job_id}",
            "match_score": match_score,
            "matching_skills": ["Python", "AWS", "Docker"],
            "missing_skills": ["Kubernetes", "GraphQL"],
            "experience_fit": "Good match",
            "salary_fit": "Within range"
        })
    
    # Sort by match score
    matches = sorted(matches, key=lambda x: x["match_score"], reverse=True)
    
    # Update resume
    resume["match_jobs"] = matches
    resume["updated_at"] = datetime.now().isoformat()
    
    return {
        "success": True,
        "message": f"Matched resume with {len(matches)} jobs",
        "data": matches,
    }


# ============================================================================
# Parse Resume (Force Re-parse)
# ============================================================================

@router.post("/{resume_id}/parse")
def parse_resume(resume_id: int):
    """
    Force re-parse a resume file.
    
    This is a mock implementation that simulates re-parsing.
    In production, this would re-extract text and data from the file.
    """
    
    # Check if resume exists
    if resume_id not in MOCK_RESUMES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found",
        )
    
    resume = MOCK_RESUMES[resume_id]
    
    # Mock parsing (in production, would call parser service)
    parsed_data = {
        "personal_info": {
            "name": resume["candidate_name"],
            "email": "candidate@email.com",
            "phone": "+1-555-0199",
            "location": "San Francisco, CA"
        },
        "summary": "Experienced professional with strong technical skills",
        "experience": [],
        "education": [],
        "skills": {
            "programming_languages": ["Python", "JavaScript"],
            "frameworks": ["FastAPI", "React"],
            "tools": ["Docker", "AWS"]
        }
    }
    
    # Update resume
    resume["parsed_data"] = parsed_data
    resume["status"] = "parsed"
    resume["updated_at"] = datetime.now().isoformat()
    
    return {
        "success": True,
        "message": "Resume parsed successfully",
        "data": parsed_data,
    }


# ============================================================================
# Get Resume Statistics
# ============================================================================

@router.get("/stats/summary")
def get_resume_stats():
    """
    Get overall resume statistics.
    
    This is a mock implementation that returns simulated statistics.
    In production, this would aggregate real data from database.
    """
    
    resumes = list(MOCK_RESUMES.values())
    
    stats = {
        "total_resumes": len(resumes),
        "by_status": {
            "parsing": len([r for r in resumes if r["status"] == "parsing"]),
            "parsed": len([r for r in resumes if r["status"] == "parsed"]),
            "analyzed": len([r for r in resumes if r["status"] == "analyzed"]),
            "failed": 0,
        },
        "avg_quality_score": sum(
            r.get("ai_analysis", {}).get("overall_quality_score", 0) 
            for r in resumes if r.get("ai_analysis")
        ) / max(1, len([r for r in resumes if r.get("ai_analysis")])),
        "file_types": {
            "pdf": len([r for r in resumes if "pdf" in r["file_type"]]),
            "doc": len([r for r in resumes if "doc" in r["file_type"]]),
            "docx": len([r for r in resumes if "docx" in r["file_type"]]),
        },
        "total_storage_mb": sum(r["file_size"] for r in resumes) / (1024 * 1024),
        "generated_at": datetime.now().isoformat(),
    }
    
    return {
        "success": True,
        "data": stats,
    }
