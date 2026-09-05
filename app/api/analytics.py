from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.services.analytics_service import (
    get_dashboard_stats,
    get_resume_stats,
    get_candidate_stats,
    get_interview_stats,
)

router = APIRouter()


@router.get("/dashboard")
def dashboard(
    current_user=Depends(get_current_user),
):
    """Get overall recruiter dashboard analytics."""

    return {
        "success": True,
        "data": get_dashboard_stats(
            user_id=current_user.id
        ),
    }


@router.get("/resumes")
def resume_analytics(
    current_user=Depends(get_current_user),
):
    """Get resume processing and ATS analytics."""

    return {
        "success": True,
        "data": get_resume_stats(
            user_id=current_user.id
        ),
    }


@router.get("/candidates")
def candidate_analytics(
    current_user=Depends(get_current_user),
):
    """Get candidate analytics."""

    return {
        "success": True,
        "data": get_candidate_stats(
            user_id=current_user.id
        ),
    }


@router.get("/interviews")
def interview_analytics(
    current_user=Depends(get_current_user),
):
    """Get interview analytics."""

    return {
        "success": True,
        "data": get_interview_stats(
            user_id=current_user.id
        ),
    }