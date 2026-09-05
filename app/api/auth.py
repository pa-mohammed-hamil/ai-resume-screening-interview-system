"""
Authentication API endpoints (Mock Implementation)
Provides user authentication without database for demo purposes
"""

from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.core.security import create_access_token, hash_password, verify_password

router = APIRouter()


# Mock user storage (in-memory for demo)
MOCK_USERS = {
    1: {
        "id": 1,
        "email": "demo@example.com",
        "password_hash": hash_password("demo123"),
        "first_name": "Demo",
        "last_name": "User",
        "created_at": "2026-08-15T10:00:00",
    }
}

NEXT_USER_ID = 2


# Request/Response Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ============================================================================
# Register User
# ============================================================================

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterRequest):
    """
    Register a new user.
    
    This is a mock implementation that stores users in memory.
    In production, this would save to a database.
    """
    global NEXT_USER_ID
    
    # Check if email already exists
    for user in MOCK_USERS.values():
        if user["email"] == payload.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    # Create new user
    user_id = NEXT_USER_ID
    NEXT_USER_ID += 1
    
    new_user = {
        "id": user_id,
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "created_at": datetime.now().isoformat(),
    }
    
    # Store user
    MOCK_USERS[user_id] = new_user
    
    # Create access token
    access_token = create_access_token(data={"sub": payload.email})
    
    # Return response (without password hash)
    user_response = {
        "id": new_user["id"],
        "email": new_user["email"],
        "first_name": new_user["first_name"],
        "last_name": new_user["last_name"],
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response,
    }


# ============================================================================
# Login
# ============================================================================

@router.post("/login")
def login(payload: LoginRequest):
    """
    Authenticate user and return JWT token.
    
    This is a mock implementation that checks in-memory storage.
    In production, this would query a database.
    """
    
    # Find user by email
    user = None
    for u in MOCK_USERS.values():
        if u["email"] == payload.email:
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user["email"]})
    
    # Return response (without password hash)
    user_response = {
        "id": user["id"],
        "email": user["email"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response,
    }


# ============================================================================
# Logout
# ============================================================================

@router.post("/logout")
def logout():
    """
    Logout endpoint.
    
    In a real application with refresh tokens, this would invalidate the token.
    For JWT-based auth, logout is typically handled client-side by removing the token.
    """
    return {
        "success": True,
        "message": "Logged out successfully",
    }


# ============================================================================
# Get Current User
# ============================================================================

@router.get("/me")
def get_current_user():
    """
    Get current authenticated user.
    
    This is a mock implementation that returns a demo user.
    In production, this would decode the JWT token and fetch the user.
    """
    return {
        "success": True,
        "user": {
            "id": 1,
            "email": "demo@example.com",
            "first_name": "Demo",
            "last_name": "User",
        }
    }


# ============================================================================
# List Users (Demo Only)
# ============================================================================

@router.get("/users")
def list_users():
    """
    List all users (demo endpoint).
    
    This is a mock implementation that returns all stored users.
    In production, this would be admin-only and query a database.
    """
    
    # Return users without password hashes
    users = [
        {
            "id": user["id"],
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
        }
        for user in MOCK_USERS.values()
    ]
    
    return {
        "success": True,
        "count": len(users),
        "users": users,
    }
