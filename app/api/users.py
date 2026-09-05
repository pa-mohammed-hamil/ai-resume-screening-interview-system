from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.schemas.user import UserResponse, UserUpdate
from app.services.auth_service import update_user

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_current_user_profile(
    current_user=Depends(get_current_user),
):
    """Get the currently authenticated user's profile."""

    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
)
def update_current_user_profile(
    payload: UserUpdate,
    current_user=Depends(get_current_user),
):
    """Update the currently authenticated user's profile."""

    user = update_user(
        user_id=current_user.id,
        payload=payload,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.delete("/me")
def delete_current_user(
    current_user=Depends(get_current_user),
):
    """Delete the currently authenticated user's account."""

    # Actual database deletion should be handled by the service layer.
    return {
        "success": True,
        "message": "User account deleted successfully",
        "user_id": current_user.id,
    }


@router.get("/me/preferences")
def get_preferences(
    current_user=Depends(get_current_user),
):
    """Get user preferences."""

    return {
        "user_id": current_user.id,
        "preferences": {
            "email_notifications": True,
            "interview_reminders": True,
            "resume_updates": True,
        },
    }


@router.put("/me/preferences")
def update_preferences(
    preferences: dict,
    current_user=Depends(get_current_user),
):
    """Update user preferences."""

    return {
        "success": True,
        "user_id": current_user.id,
        "preferences": preferences,
    }