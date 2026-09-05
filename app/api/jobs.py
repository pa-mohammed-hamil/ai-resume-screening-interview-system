"""
Jobs API endpoints (Mock Implementation)
Provides CRUD operations for job postings without database for demo purposes
"""

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter()


# Mock job storage (in-memory for demo)
MOCK_JOBS = {
    1: {
        "id": 1,
        "title": "Senior Python Developer",
        "department": "Engineering",
        "location": "San Francisco, CA",
        "employment_type": "Full-time",
        "experience_level": "Senior",
        "description": "We are looking for an experienced Python developer to join our team...",
        "requirements": [
            "5+ years of Python experience",
            "FastAPI/Django expertise",
            "PostgreSQL knowledge",
            "AWS experience"
        ],
        "responsibilities": [
            "Design and implement backend services",
            "Mentor junior developers",
            "Review code and ensure quality"
        ],
        "skills_required": ["Python", "FastAPI", "PostgreSQL", "AWS", "Docker"],
        "salary_min": 120000,
        "salary_max": 180000,
        "status": "active",
        "created_at": "2026-08-15T10:00:00",
        "updated_at": "2026-08-15T10:00:00",
    },
    2: {
        "id": 2,
        "title": "Frontend React Developer",
        "department": "Engineering",
        "location": "Remote",
        "employment_type": "Full-time",
        "experience_level": "Mid-level",
        "description": "Join our frontend team to build amazing user experiences...",
        "requirements": [
            "3+ years of React experience",
            "TypeScript proficiency",
            "CSS expertise",
            "REST API integration"
        ],
        "responsibilities": [
            "Build responsive web applications",
            "Collaborate with designers",
            "Optimize performance"
        ],
        "skills_required": ["React", "TypeScript", "CSS", "JavaScript", "Git"],
        "salary_min": 90000,
        "salary_max": 140000,
        "status": "active",
        "created_at": "2026-08-20T14:30:00",
        "updated_at": "2026-08-20T14:30:00",
    },
}

NEXT_JOB_ID = 3


# Request/Response Models
class JobCreate(BaseModel):
    title: str
    department: str
    location: str
    employment_type: str
    experience_level: str
    description: str
    requirements: List[str]
    responsibilities: List[str]
    skills_required: List[str]
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    responsibilities: Optional[List[str]] = None
    skills_required: Optional[List[str]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    status: Optional[str] = None


# ============================================================================
# Create Job
# ============================================================================

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate):
    """
    Create a new job posting.
    
    This is a mock implementation that stores jobs in memory.
    In production, this would save to a database.
    """
    global NEXT_JOB_ID
    
    # Create new job
    job_id = NEXT_JOB_ID
    NEXT_JOB_ID += 1
    
    now = datetime.now().isoformat()
    
    new_job = {
        "id": job_id,
        "title": payload.title,
        "department": payload.department,
        "location": payload.location,
        "employment_type": payload.employment_type,
        "experience_level": payload.experience_level,
        "description": payload.description,
        "requirements": payload.requirements,
        "responsibilities": payload.responsibilities,
        "skills_required": payload.skills_required,
        "salary_min": payload.salary_min,
        "salary_max": payload.salary_max,
        "status": "active",
        "created_at": now,
        "updated_at": now,
    }
    
    # Store job
    MOCK_JOBS[job_id] = new_job
    
    return {
        "success": True,
        "message": "Job created successfully",
        "data": new_job,
    }


# ============================================================================
# List Jobs
# ============================================================================

@router.get("/")
def list_jobs(
    status: Optional[str] = None,
    department: Optional[str] = None,
    location: Optional[str] = None,
):
    """
    Get all job postings with optional filters.
    
    This is a mock implementation that returns in-memory jobs.
    In production, this would query a database.
    """
    
    # Get all jobs
    jobs = list(MOCK_JOBS.values())
    
    # Apply filters
    if status:
        jobs = [job for job in jobs if job["status"] == status]
    
    if department:
        jobs = [job for job in jobs if job["department"].lower() == department.lower()]
    
    if location:
        jobs = [job for job in jobs if location.lower() in job["location"].lower()]
    
    return {
        "success": True,
        "count": len(jobs),
        "data": jobs,
    }


# ============================================================================
# Get Job by ID
# ============================================================================

@router.get("/{job_id}")
def get_job(job_id: int):
    """
    Get details of a specific job posting.
    
    This is a mock implementation that retrieves from in-memory storage.
    In production, this would query a database.
    """
    
    # Check if job exists
    if job_id not in MOCK_JOBS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found",
        )
    
    job = MOCK_JOBS[job_id]
    
    return {
        "success": True,
        "data": job,
    }


# ============================================================================
# Update Job
# ============================================================================

@router.put("/{job_id}")
def update_job(job_id: int, payload: JobUpdate):
    """
    Update an existing job posting.
    
    This is a mock implementation that updates in-memory storage.
    In production, this would update a database.
    """
    
    # Check if job exists
    if job_id not in MOCK_JOBS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found",
        )
    
    job = MOCK_JOBS[job_id]
    
    # Update fields that were provided
    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        job[field] = value
    
    # Update timestamp
    job["updated_at"] = datetime.now().isoformat()
    
    return {
        "success": True,
        "message": "Job updated successfully",
        "data": job,
    }


# ============================================================================
# Delete Job
# ============================================================================

@router.delete("/{job_id}")
def delete_job(job_id: int):
    """
    Delete a job posting.
    
    This is a mock implementation that removes from in-memory storage.
    In production, this would delete from a database or soft-delete.
    """
    
    # Check if job exists
    if job_id not in MOCK_JOBS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found",
        )
    
    # Delete job
    deleted_job = MOCK_JOBS.pop(job_id)
    
    return {
        "success": True,
        "message": "Job deleted successfully",
        "data": deleted_job,
    }


# ============================================================================
# Analyze Job Description (AI)
# ============================================================================

@router.post("/{job_id}/analyze")
def analyze_job_description(job_id: int):
    """
    Analyze a job description using AI to extract key information.
    
    This is a mock implementation that returns simulated AI analysis.
    In production, this would call an actual AI service.
    """
    
    # Check if job exists
    if job_id not in MOCK_JOBS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found",
        )
    
    job = MOCK_JOBS[job_id]
    
    # Mock AI analysis result
    analysis = {
        "job_id": job_id,
        "title": job["title"],
        "key_skills_extracted": job["skills_required"][:5],
        "experience_required": job["experience_level"],
        "seniority_level": job["experience_level"],
        "technical_skills": [s for s in job["skills_required"] if s in ["Python", "JavaScript", "React", "AWS", "Docker"]],
        "soft_skills": ["Communication", "Leadership", "Problem Solving"],
        "estimated_candidates_match": 127,
        "difficulty_score": 7.5,
        "competition_level": "High",
        "recommendations": [
            "Consider highlighting remote work options",
            "Salary range is competitive for the market",
            "Add more details about company culture",
        ],
        "analyzed_at": datetime.now().isoformat(),
    }
    
    return {
        "success": True,
        "message": "Job description analysis completed",
        "data": analysis,
    }


# ============================================================================
# Get Job Statistics
# ============================================================================

@router.get("/{job_id}/stats")
def get_job_stats(job_id: int):
    """
    Get statistics for a specific job posting.
    
    This is a mock implementation that returns simulated statistics.
    In production, this would aggregate real data from the database.
    """
    
    # Check if job exists
    if job_id not in MOCK_JOBS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found",
        )
    
    job = MOCK_JOBS[job_id]
    
    # Mock statistics
    stats = {
        "job_id": job_id,
        "title": job["title"],
        "total_applications": 45,
        "pending_review": 12,
        "shortlisted": 8,
        "interviewed": 3,
        "rejected": 22,
        "avg_match_score": 78.5,
        "top_matching_skills": job["skills_required"][:3],
        "application_trend": [5, 8, 12, 15, 5],  # Last 5 days
        "generated_at": datetime.now().isoformat(),
    }
    
    return {
        "success": True,
        "data": stats,
    }
