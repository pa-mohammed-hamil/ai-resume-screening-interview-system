"""
Candidates API endpoints (Mock Implementation)
Provides candidate management and screening without database for demo purposes
"""

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

router = APIRouter()


# Mock candidate storage (in-memory for demo)
MOCK_CANDIDATES = {
    1: {
        "id": 1,
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith@email.com",
        "phone": "+1-555-0101",
        "location": "San Francisco, CA",
        "current_title": "Senior Software Engineer",
        "experience_years": 8,
        "skills": ["Python", "FastAPI", "PostgreSQL", "AWS", "Docker", "React"],
        "education": "BS Computer Science, Stanford University",
        "linkedin": "linkedin.com/in/johnsmith",
        "github": "github.com/johnsmith",
        "resume_url": "/storage/resumes/john_smith_resume.pdf",
        "status": "screening",
        "applied_jobs": [1],  # Applied to Senior Python Developer
        "match_score": 92.5,
        "technical_score": 95,
        "experience_score": 90,
        "culture_fit_score": 88,
        "availability": "2 weeks",
        "expected_salary": 150000,
        "notes": "Excellent technical background, strong Python skills",
        "created_at": "2026-08-25T10:00:00",
        "updated_at": "2026-08-25T10:00:00",
    },
    2: {
        "id": 2,
        "first_name": "Sarah",
        "last_name": "Johnson",
        "email": "sarah.j@email.com",
        "phone": "+1-555-0102",
        "location": "Remote",
        "current_title": "Frontend Developer",
        "experience_years": 5,
        "skills": ["React", "TypeScript", "CSS", "JavaScript", "Redux", "Next.js"],
        "education": "BS Software Engineering, MIT",
        "linkedin": "linkedin.com/in/sarahjohnson",
        "github": "github.com/sarahj",
        "resume_url": "/storage/resumes/sarah_johnson_resume.pdf",
        "status": "shortlisted",
        "applied_jobs": [2],  # Applied to Frontend React Developer
        "match_score": 88.0,
        "technical_score": 92,
        "experience_score": 85,
        "culture_fit_score": 90,
        "availability": "Immediate",
        "expected_salary": 120000,
        "notes": "Great UI/UX skills, portfolio looks impressive",
        "created_at": "2026-08-26T14:30:00",
        "updated_at": "2026-08-27T09:15:00",
    },
    3: {
        "id": 3,
        "first_name": "Michael",
        "last_name": "Chen",
        "email": "mchen@email.com",
        "phone": "+1-555-0103",
        "location": "Austin, TX",
        "current_title": "DevOps Engineer",
        "experience_years": 6,
        "skills": ["Kubernetes", "Docker", "AWS", "Terraform", "Python", "Jenkins"],
        "education": "MS Computer Science, UC Berkeley",
        "linkedin": "linkedin.com/in/michaelchen",
        "github": "github.com/mchen",
        "resume_url": "/storage/resumes/michael_chen_resume.pdf",
        "status": "interviewed",
        "applied_jobs": [1],  # Applied to Senior Python Developer
        "match_score": 85.5,
        "technical_score": 88,
        "experience_score": 87,
        "culture_fit_score": 82,
        "availability": "1 month",
        "expected_salary": 140000,
        "notes": "Strong DevOps background, good communication",
        "created_at": "2026-08-27T11:20:00",
        "updated_at": "2026-08-28T16:45:00",
    },
    4: {
        "id": 4,
        "first_name": "Emily",
        "last_name": "Davis",
        "email": "emily.davis@email.com",
        "phone": "+1-555-0104",
        "location": "New York, NY",
        "current_title": "Full Stack Developer",
        "experience_years": 4,
        "skills": ["React", "Node.js", "MongoDB", "GraphQL", "TypeScript", "AWS"],
        "education": "BS Computer Science, NYU",
        "linkedin": "linkedin.com/in/emilydavis",
        "github": "github.com/emilyd",
        "resume_url": "/storage/resumes/emily_davis_resume.pdf",
        "status": "screening",
        "applied_jobs": [2],  # Applied to Frontend React Developer
        "match_score": 82.0,
        "technical_score": 85,
        "experience_score": 80,
        "culture_fit_score": 81,
        "availability": "2 weeks",
        "expected_salary": 110000,
        "notes": "Versatile full-stack developer, good potential",
        "created_at": "2026-08-28T09:00:00",
        "updated_at": "2026-08-28T09:00:00",
    },
    5: {
        "id": 5,
        "first_name": "David",
        "last_name": "Martinez",
        "email": "d.martinez@email.com",
        "phone": "+1-555-0105",
        "location": "Seattle, WA",
        "current_title": "Machine Learning Engineer",
        "experience_years": 7,
        "skills": ["Python", "TensorFlow", "PyTorch", "AWS", "Docker", "SQL"],
        "education": "PhD Machine Learning, Stanford",
        "linkedin": "linkedin.com/in/davidmartinez",
        "github": "github.com/dmartinez",
        "resume_url": "/storage/resumes/david_martinez_resume.pdf",
        "status": "offer",
        "applied_jobs": [1],  # Applied to Senior Python Developer
        "match_score": 94.0,
        "technical_score": 98,
        "experience_score": 92,
        "culture_fit_score": 91,
        "availability": "1 month",
        "expected_salary": 180000,
        "notes": "Outstanding ML background, PhD from Stanford",
        "created_at": "2026-08-24T08:30:00",
        "updated_at": "2026-08-30T14:20:00",
    },
}

NEXT_CANDIDATE_ID = 6


# Request/Response Models
class CandidateCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    location: str
    current_title: Optional[str] = None
    experience_years: int
    skills: List[str]
    education: str
    linkedin: Optional[str] = None
    github: Optional[str] = None
    resume_url: Optional[str] = None


class CandidateUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    match_score: Optional[float] = None
    technical_score: Optional[float] = None
    experience_score: Optional[float] = None
    culture_fit_score: Optional[float] = None


class CompareRequest(BaseModel):
    candidate_ids: List[int]


# ============================================================================
# List Candidates
# ============================================================================

@router.get("/")
def list_candidates(
    status: Optional[str] = None,
    job_id: Optional[int] = None,
    min_score: Optional[float] = None,
):
    """
    Get all candidates with optional filters.
    
    This is a mock implementation that returns in-memory candidates.
    In production, this would query a database.
    """
    
    # Get all candidates
    candidates = list(MOCK_CANDIDATES.values())
    
    # Apply filters
    if status:
        candidates = [c for c in candidates if c["status"] == status]
    
    if job_id:
        candidates = [c for c in candidates if job_id in c["applied_jobs"]]
    
    if min_score:
        candidates = [c for c in candidates if c["match_score"] >= min_score]
    
    # Sort by match score (highest first)
    candidates = sorted(candidates, key=lambda x: x["match_score"], reverse=True)
    
    return {
        "success": True,
        "count": len(candidates),
        "data": candidates,
    }


# ============================================================================
# Get Candidate by ID
# ============================================================================

@router.get("/{candidate_id}")
def get_candidate(candidate_id: int):
    """
    Get detailed candidate profile.
    
    This is a mock implementation that retrieves from in-memory storage.
    In production, this would query a database.
    """
    
    # Check if candidate exists
    if candidate_id not in MOCK_CANDIDATES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID {candidate_id} not found",
        )
    
    candidate = MOCK_CANDIDATES[candidate_id]
    
    return {
        "success": True,
        "data": candidate,
    }


# ============================================================================
# Create Candidate
# ============================================================================

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_candidate(payload: CandidateCreate):
    """
    Create a new candidate profile.
    
    This is a mock implementation that stores in memory.
    In production, this would save to a database.
    """
    global NEXT_CANDIDATE_ID
    
    # Create new candidate
    candidate_id = NEXT_CANDIDATE_ID
    NEXT_CANDIDATE_ID += 1
    
    now = datetime.now().isoformat()
    
    new_candidate = {
        "id": candidate_id,
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "email": payload.email,
        "phone": payload.phone,
        "location": payload.location,
        "current_title": payload.current_title,
        "experience_years": payload.experience_years,
        "skills": payload.skills,
        "education": payload.education,
        "linkedin": payload.linkedin,
        "github": payload.github,
        "resume_url": payload.resume_url,
        "status": "screening",
        "applied_jobs": [],
        "match_score": 0.0,
        "technical_score": 0.0,
        "experience_score": 0.0,
        "culture_fit_score": 0.0,
        "availability": "Unknown",
        "expected_salary": 0,
        "notes": "",
        "created_at": now,
        "updated_at": now,
    }
    
    # Store candidate
    MOCK_CANDIDATES[candidate_id] = new_candidate
    
    return {
        "success": True,
        "message": "Candidate created successfully",
        "data": new_candidate,
    }


# ============================================================================
# Update Candidate
# ============================================================================

@router.put("/{candidate_id}")
def update_candidate(candidate_id: int, payload: CandidateUpdate):
    """
    Update candidate profile.
    
    This is a mock implementation that updates in-memory storage.
    In production, this would update a database.
    """
    
    # Check if candidate exists
    if candidate_id not in MOCK_CANDIDATES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID {candidate_id} not found",
        )
    
    candidate = MOCK_CANDIDATES[candidate_id]
    
    # Update fields that were provided
    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        candidate[field] = value
    
    # Update timestamp
    candidate["updated_at"] = datetime.now().isoformat()
    
    return {
        "success": True,
        "message": "Candidate updated successfully",
        "data": candidate,
    }


# ============================================================================
# Delete Candidate
# ============================================================================

@router.delete("/{candidate_id}")
def delete_candidate(candidate_id: int):
    """
    Delete a candidate profile.
    
    This is a mock implementation that removes from in-memory storage.
    In production, this would delete from a database.
    """
    
    # Check if candidate exists
    if candidate_id not in MOCK_CANDIDATES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID {candidate_id} not found",
        )
    
    # Delete candidate
    deleted_candidate = MOCK_CANDIDATES.pop(candidate_id)
    
    return {
        "success": True,
        "message": "Candidate deleted successfully",
        "data": deleted_candidate,
    }


# ============================================================================
# Compare Candidates
# ============================================================================

@router.post("/compare")
def compare_candidates(payload: CompareRequest):
    """
    Compare multiple candidates side-by-side.
    
    This is a mock implementation that returns simulated comparison.
    In production, this would aggregate data from database.
    """
    
    candidate_ids = payload.candidate_ids
    
    # Validation
    if len(candidate_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least two candidates are required for comparison",
        )
    
    if len(candidate_ids) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 candidates can be compared at once",
        )
    
    # Get candidates
    candidates_data = []
    for cid in candidate_ids:
        if cid not in MOCK_CANDIDATES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate with ID {cid} not found",
            )
        candidates_data.append(MOCK_CANDIDATES[cid])
    
    # Create comparison matrix
    comparison = {
        "candidates": candidates_data,
        "comparison_matrix": {
            "skills_overlap": [
                [len(set(c1["skills"]) & set(c2["skills"])) 
                 for c2 in candidates_data] 
                for c1 in candidates_data
            ],
            "score_differences": [
                [abs(c1["match_score"] - c2["match_score"]) 
                 for c2 in candidates_data] 
                for c1 in candidates_data
            ],
        },
        "summary": {
            "highest_match_score": max(c["match_score"] for c in candidates_data),
            "lowest_match_score": min(c["match_score"] for c in candidates_data),
            "avg_experience": sum(c["experience_years"] for c in candidates_data) / len(candidates_data),
            "most_common_skills": ["Python", "AWS", "Docker"],  # Mock data
        },
        "recommendation": candidates_data[0]["id"],  # Recommend first (highest score assumed)
        "generated_at": datetime.now().isoformat(),
    }
    
    return {
        "success": True,
        "data": comparison,
    }


# ============================================================================
# Rank Candidates for Job
# ============================================================================

@router.get("/ranking/{job_id}")
def rank_candidates_for_job(job_id: int):
    """
    Rank all candidates for a specific job opening.
    
    This is a mock implementation that returns simulated rankings.
    In production, this would use ML models for ranking.
    """
    
    # Get candidates who applied for this job
    candidates = [
        c for c in MOCK_CANDIDATES.values() 
        if job_id in c.get("applied_jobs", [])
    ]
    
    if not candidates:
        return {
            "success": True,
            "job_id": job_id,
            "message": "No candidates found for this job",
            "data": {
                "ranked_candidates": [],
                "total_candidates": 0,
            }
        }
    
    # Sort by match score (highest first)
    ranked = sorted(candidates, key=lambda x: x["match_score"], reverse=True)
    
    # Add rank position
    for idx, candidate in enumerate(ranked, 1):
        candidate["rank"] = idx
        candidate["percentile"] = round((1 - (idx - 1) / len(ranked)) * 100, 1)
    
    ranking_data = {
        "job_id": job_id,
        "ranked_candidates": ranked,
        "total_candidates": len(ranked),
        "avg_match_score": sum(c["match_score"] for c in ranked) / len(ranked),
        "top_3": ranked[:3] if len(ranked) >= 3 else ranked,
        "generated_at": datetime.now().isoformat(),
    }
    
    return {
        "success": True,
        "job_id": job_id,
        "data": ranking_data,
    }


# ============================================================================
# Get Candidate Statistics
# ============================================================================

@router.get("/{candidate_id}/stats")
def get_candidate_stats(candidate_id: int):
    """
    Get statistics and insights for a specific candidate.
    
    This is a mock implementation that returns simulated statistics.
    In production, this would aggregate real data.
    """
    
    # Check if candidate exists
    if candidate_id not in MOCK_CANDIDATES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID {candidate_id} not found",
        )
    
    candidate = MOCK_CANDIDATES[candidate_id]
    
    # Mock statistics
    stats = {
        "candidate_id": candidate_id,
        "name": f"{candidate['first_name']} {candidate['last_name']}",
        "jobs_applied": len(candidate["applied_jobs"]),
        "interviews_completed": 1 if candidate["status"] in ["interviewed", "offer"] else 0,
        "avg_score": round((
            candidate["match_score"] + 
            candidate["technical_score"] + 
            candidate["experience_score"] + 
            candidate["culture_fit_score"]
        ) / 4, 2),
        "skill_proficiency": {
            skill: round(85 + (i * 2.5), 1) 
            for i, skill in enumerate(candidate["skills"][:5])
        },
        "comparison_with_pool": {
            "better_than": "75% of candidates",
            "rank_in_pool": 5,
            "total_in_pool": 20,
        },
        "generated_at": datetime.now().isoformat(),
    }
    
    return {
        "success": True,
        "data": stats,
    }
