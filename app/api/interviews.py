"""
Interviews API endpoints (Mock Implementation)
Provides interview scheduling and management without database for demo purposes
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter()


# Mock interview storage (in-memory for demo)
MOCK_INTERVIEWS = {
    1: {
        "id": 1,
        "candidate_id": 1,
        "candidate_name": "John Smith",
        "job_id": 1,
        "job_title": "Senior Python Developer",
        "interview_type": "technical",
        "status": "completed",
        "scheduled_date": "2026-08-28T14:00:00",
        "duration_minutes": 60,
        "interviewer": "Sarah Chen",
        "location": "Zoom",
        "meeting_link": "https://zoom.us/j/123456789",
        "questions": [
            {
                "id": 1,
                "question": "Explain the difference between list and tuple in Python",
                "answer": "Lists are mutable, tuples are immutable...",
                "score": 9,
                "notes": "Excellent answer with examples"
            },
            {
                "id": 2,
                "question": "How do you handle exceptions in Python?",
                "answer": "Using try-except blocks...",
                "score": 8,
                "notes": "Good understanding of error handling"
            },
            {
                "id": 3,
                "question": "Explain async/await in Python",
                "answer": "Async programming allows concurrent execution...",
                "score": 10,
                "notes": "Perfect explanation with practical examples"
            }
        ],
        "overall_score": 90,
        "technical_score": 92,
        "communication_score": 88,
        "problem_solving_score": 91,
        "feedback": "Strong technical skills, excellent communication",
        "recommendation": "Strongly recommend for next round",
        "notes": "Candidate showed deep Python knowledge",
        "created_at": "2026-08-27T10:00:00",
        "updated_at": "2026-08-28T15:30:00",
    },
    2: {
        "id": 2,
        "candidate_id": 2,
        "candidate_name": "Sarah Johnson",
        "job_id": 2,
        "job_title": "Frontend React Developer",
        "interview_type": "technical",
        "status": "scheduled",
        "scheduled_date": "2026-09-05T10:00:00",
        "duration_minutes": 45,
        "interviewer": "Mike Rodriguez",
        "location": "Google Meet",
        "meeting_link": "https://meet.google.com/abc-defg-hij",
        "questions": [],
        "overall_score": 0,
        "technical_score": 0,
        "communication_score": 0,
        "problem_solving_score": 0,
        "feedback": "",
        "recommendation": "",
        "notes": "Frontend technical interview - React focus",
        "created_at": "2026-09-01T09:00:00",
        "updated_at": "2026-09-01T09:00:00",
    },
    3: {
        "id": 3,
        "candidate_id": 3,
        "candidate_name": "Michael Chen",
        "job_id": 1,
        "job_title": "Senior Python Developer",
        "interview_type": "behavioral",
        "status": "in_progress",
        "scheduled_date": "2026-09-02T15:00:00",
        "duration_minutes": 30,
        "interviewer": "Lisa Wong",
        "location": "Office - Room 301",
        "meeting_link": "",
        "questions": [
            {
                "id": 1,
                "question": "Tell me about a time you faced a difficult challenge",
                "answer": "In my previous role...",
                "score": 8,
                "notes": "Good self-awareness"
            }
        ],
        "overall_score": 0,
        "technical_score": 0,
        "communication_score": 85,
        "problem_solving_score": 0,
        "feedback": "In progress",
        "recommendation": "",
        "notes": "Behavioral round focusing on soft skills",
        "created_at": "2026-09-02T10:00:00",
        "updated_at": "2026-09-02T15:15:00",
    },
}

NEXT_INTERVIEW_ID = 4


# Request/Response Models
class InterviewCreate(BaseModel):
    candidate_id: int
    job_id: int
    interview_type: str  # technical, behavioral, cultural, final
    scheduled_date: str
    duration_minutes: int
    interviewer: str
    location: str
    meeting_link: Optional[str] = None
    notes: Optional[str] = None


class InterviewUpdate(BaseModel):
    status: Optional[str] = None
    scheduled_date: Optional[str] = None
    interviewer: Optional[str] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    notes: Optional[str] = None


class QuestionResponse(BaseModel):
    question_id: int
    answer: str
    score: Optional[int] = None
    notes: Optional[str] = None


class InterviewFeedback(BaseModel):
    overall_score: int
    technical_score: Optional[int] = None
    communication_score: Optional[int] = None
    problem_solving_score: Optional[int] = None
    feedback: str
    recommendation: str


# ============================================================================
# List Interviews
# ============================================================================

@router.get("/")
def list_interviews(
    status: Optional[str] = None,
    candidate_id: Optional[int] = None,
    job_id: Optional[int] = None,
):
    """
    Get all interviews with optional filters.
    
    This is a mock implementation that returns in-memory interviews.
    In production, this would query a database.
    """
    
    # Get all interviews
    interviews = list(MOCK_INTERVIEWS.values())
    
    # Apply filters
    if status:
        interviews = [i for i in interviews if i["status"] == status]
    
    if candidate_id:
        interviews = [i for i in interviews if i["candidate_id"] == candidate_id]
    
    if job_id:
        interviews = [i for i in interviews if i["job_id"] == job_id]
    
    # Sort by scheduled date (newest first)
    interviews = sorted(interviews, key=lambda x: x["scheduled_date"], reverse=True)
    
    return {
        "success": True,
        "count": len(interviews),
        "data": interviews,
    }


# ============================================================================
# Get Interview by ID
# ============================================================================

@router.get("/{interview_id}")
def get_interview(interview_id: int):
    """
    Get detailed interview information.
    
    This is a mock implementation that retrieves from in-memory storage.
    In production, this would query a database.
    """
    
    # Check if interview exists
    if interview_id not in MOCK_INTERVIEWS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with ID {interview_id} not found",
        )
    
    interview = MOCK_INTERVIEWS[interview_id]
    
    return {
        "success": True,
        "data": interview,
    }


# ============================================================================
# Create Interview
# ============================================================================

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_interview(payload: InterviewCreate):
    """
    Schedule a new interview.
    
    This is a mock implementation that stores in memory.
    In production, this would save to a database.
    """
    global NEXT_INTERVIEW_ID
    
    # Create new interview
    interview_id = NEXT_INTERVIEW_ID
    NEXT_INTERVIEW_ID += 1
    
    now = datetime.now().isoformat()
    
    new_interview = {
        "id": interview_id,
        "candidate_id": payload.candidate_id,
        "candidate_name": f"Candidate {payload.candidate_id}",
        "job_id": payload.job_id,
        "job_title": f"Job {payload.job_id}",
        "interview_type": payload.interview_type,
        "status": "scheduled",
        "scheduled_date": payload.scheduled_date,
        "duration_minutes": payload.duration_minutes,
        "interviewer": payload.interviewer,
        "location": payload.location,
        "meeting_link": payload.meeting_link,
        "questions": [],
        "overall_score": 0,
        "technical_score": 0,
        "communication_score": 0,
        "problem_solving_score": 0,
        "feedback": "",
        "recommendation": "",
        "notes": payload.notes or "",
        "created_at": now,
        "updated_at": now,
    }
    
    # Store interview
    MOCK_INTERVIEWS[interview_id] = new_interview
    
    return {
        "success": True,
        "message": "Interview scheduled successfully",
        "data": new_interview,
    }


# ============================================================================
# Update Interview
# ============================================================================

@router.put("/{interview_id}")
def update_interview(interview_id: int, payload: InterviewUpdate):
    """
    Update interview details.
    
    This is a mock implementation that updates in-memory storage.
    In production, this would update a database.
    """
    
    # Check if interview exists
    if interview_id not in MOCK_INTERVIEWS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with ID {interview_id} not found",
        )
    
    interview = MOCK_INTERVIEWS[interview_id]
    
    # Update fields that were provided
    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        interview[field] = value
    
    # Update timestamp
    interview["updated_at"] = datetime.now().isoformat()
    
    return {
        "success": True,
        "message": "Interview updated successfully",
        "data": interview,
    }


# ============================================================================
# Delete Interview
# ============================================================================

@router.delete("/{interview_id}")
def delete_interview(interview_id: int):
    """
    Cancel/delete an interview.
    
    This is a mock implementation that removes from in-memory storage.
    In production, this would delete from a database or mark as cancelled.
    """
    
    # Check if interview exists
    if interview_id not in MOCK_INTERVIEWS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with ID {interview_id} not found",
        )
    
    # Delete interview
    deleted_interview = MOCK_INTERVIEWS.pop(interview_id)
    
    return {
        "success": True,
        "message": "Interview cancelled successfully",
        "data": deleted_interview,
    }


# ============================================================================
# Start Interview
# ============================================================================

@router.post("/{interview_id}/start")
def start_interview(interview_id: int):
    """
    Start an interview session.
    
    This is a mock implementation that updates status.
    In production, this would initialize interview session.
    """
    
    # Check if interview exists
    if interview_id not in MOCK_INTERVIEWS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with ID {interview_id} not found",
        )
    
    interview = MOCK_INTERVIEWS[interview_id]
    
    # Update status
    interview["status"] = "in_progress"
    interview["updated_at"] = datetime.now().isoformat()
    
    # Generate sample questions based on type
    if interview["interview_type"] == "technical":
        interview["questions"] = [
            {
                "id": 1,
                "question": "Explain your approach to solving complex problems",
                "answer": "",
                "score": 0,
                "notes": ""
            },
            {
                "id": 2,
                "question": "Describe your experience with our tech stack",
                "answer": "",
                "score": 0,
                "notes": ""
            },
        ]
    elif interview["interview_type"] == "behavioral":
        interview["questions"] = [
            {
                "id": 1,
                "question": "Tell me about a time you worked in a team",
                "answer": "",
                "score": 0,
                "notes": ""
            },
            {
                "id": 2,
                "question": "How do you handle conflicts at work?",
                "answer": "",
                "score": 0,
                "notes": ""
            },
        ]
    
    return {
        "success": True,
        "message": "Interview started",
        "data": interview,
    }


# ============================================================================
# Submit Answer
# ============================================================================

@router.post("/{interview_id}/answer")
def submit_answer(interview_id: int, payload: QuestionResponse):
    """
    Submit an answer to an interview question.
    
    This is a mock implementation that stores the answer.
    In production, this would save to database and possibly use AI for evaluation.
    """
    
    # Check if interview exists
    if interview_id not in MOCK_INTERVIEWS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with ID {interview_id} not found",
        )
    
    interview = MOCK_INTERVIEWS[interview_id]
    
    # Find and update question
    question_found = False
    for question in interview["questions"]:
        if question["id"] == payload.question_id:
            question["answer"] = payload.answer
            if payload.score is not None:
                question["score"] = payload.score
            if payload.notes:
                question["notes"] = payload.notes
            question_found = True
            break
    
    if not question_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question {payload.question_id} not found in this interview",
        )
    
    interview["updated_at"] = datetime.now().isoformat()
    
    return {
        "success": True,
        "message": "Answer submitted successfully",
        "data": interview,
    }


# ============================================================================
# Complete Interview with Feedback
# ============================================================================

@router.post("/{interview_id}/complete")
def complete_interview(interview_id: int, payload: InterviewFeedback):
    """
    Complete interview and submit feedback.
    
    This is a mock implementation that updates interview status.
    In production, this would finalize interview and notify stakeholders.
    """
    
    # Check if interview exists
    if interview_id not in MOCK_INTERVIEWS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with ID {interview_id} not found",
        )
    
    interview = MOCK_INTERVIEWS[interview_id]
    
    # Update interview with feedback
    interview["status"] = "completed"
    interview["overall_score"] = payload.overall_score
    if payload.technical_score is not None:
        interview["technical_score"] = payload.technical_score
    if payload.communication_score is not None:
        interview["communication_score"] = payload.communication_score
    if payload.problem_solving_score is not None:
        interview["problem_solving_score"] = payload.problem_solving_score
    interview["feedback"] = payload.feedback
    interview["recommendation"] = payload.recommendation
    interview["updated_at"] = datetime.now().isoformat()
    
    return {
        "success": True,
        "message": "Interview completed successfully",
        "data": interview,
    }


# ============================================================================
# Generate Interview Report
# ============================================================================

@router.get("/{interview_id}/report")
def generate_report(interview_id: int):
    """
    Generate comprehensive interview report.
    
    This is a mock implementation that returns formatted report.
    In production, this would generate PDF report.
    """
    
    # Check if interview exists
    if interview_id not in MOCK_INTERVIEWS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with ID {interview_id} not found",
        )
    
    interview = MOCK_INTERVIEWS[interview_id]
    
    # Generate report
    report = {
        "interview_id": interview_id,
        "candidate": {
            "id": interview["candidate_id"],
            "name": interview["candidate_name"],
        },
        "job": {
            "id": interview["job_id"],
            "title": interview["job_title"],
        },
        "interview_details": {
            "type": interview["interview_type"],
            "date": interview["scheduled_date"],
            "duration": interview["duration_minutes"],
            "interviewer": interview["interviewer"],
            "location": interview["location"],
        },
        "scores": {
            "overall": interview["overall_score"],
            "technical": interview["technical_score"],
            "communication": interview["communication_score"],
            "problem_solving": interview["problem_solving_score"],
        },
        "questions_answered": len([q for q in interview["questions"] if q["answer"]]),
        "total_questions": len(interview["questions"]),
        "feedback": interview["feedback"],
        "recommendation": interview["recommendation"],
        "strengths": [
            "Strong technical knowledge",
            "Excellent communication skills",
            "Good problem-solving approach"
        ] if interview["overall_score"] > 80 else [
            "Adequate technical knowledge",
            "Room for improvement in communication"
        ],
        "areas_for_improvement": [
            "More experience with advanced topics",
            "Could be more concise in explanations"
        ] if interview["overall_score"] < 90 else [
            "None significant"
        ],
        "generated_at": datetime.now().isoformat(),
        "report_url": f"/storage/reports/interview_{interview_id}_report.pdf",
    }
    
    return {
        "success": True,
        "data": report,
    }


# ============================================================================
# Get Interview Statistics
# ============================================================================

@router.get("/stats/summary")
def get_interview_stats():
    """
    Get overall interview statistics.
    
    This is a mock implementation that returns simulated statistics.
    In production, this would aggregate real data from database.
    """
    
    interviews = list(MOCK_INTERVIEWS.values())
    
    stats = {
        "total_interviews": len(interviews),
        "by_status": {
            "scheduled": len([i for i in interviews if i["status"] == "scheduled"]),
            "in_progress": len([i for i in interviews if i["status"] == "in_progress"]),
            "completed": len([i for i in interviews if i["status"] == "completed"]),
            "cancelled": 0,
        },
        "by_type": {
            "technical": len([i for i in interviews if i["interview_type"] == "technical"]),
            "behavioral": len([i for i in interviews if i["interview_type"] == "behavioral"]),
            "cultural": 0,
            "final": 0,
        },
        "avg_score": sum(i["overall_score"] for i in interviews if i["overall_score"] > 0) / max(1, len([i for i in interviews if i["overall_score"] > 0])),
        "upcoming_this_week": len([i for i in interviews if i["status"] == "scheduled"]),
        "generated_at": datetime.now().isoformat(),
    }
    
    return {
        "success": True,
        "data": stats,
    }
