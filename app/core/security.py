"""
Security utilities for the AI Resume Screening & Interview System.

Responsibilities:
- Password hashing and verification (using bcrypt directly)
- JWT access-token generation
- JWT refresh-token generation
- JWT token decoding and validation
- Authentication helpers
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.core.config import settings
from app.core.logging import get_logger


# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Password Hashing (Using bcrypt directly to avoid passlib warnings)
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Args:
        password: User's plain-text password.

    Returns:
        Secure bcrypt password hash.
    """
    if not password:
        raise ValueError("Password cannot be empty.")
    
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a hashed password.

    Args:
        plain_password: Plain-text password to verify.
        hashed_password: Hashed password to check against.

    Returns:
        True if password matches, False otherwise.
    """
    if not plain_password or not hashed_password:
        return False
    
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        logger.exception("Password verification failed.")
        return False


# ---------------------------------------------------------------------------
# JWT Configuration
# ---------------------------------------------------------------------------

JWT_ALGORITHM = settings.ALGORITHM
JWT_SECRET_KEY = settings.SECRET_KEY


# ---------------------------------------------------------------------------
# JWT Token Creation
# ---------------------------------------------------------------------------

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the JWT token (usually {"sub": user_email})
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT access token.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(
    subject: str,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a JWT refresh token.

    Refresh tokens have a longer lifetime than access tokens.
    """
    now = datetime.now(timezone.utc)
    
    expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    payload: Dict[str, Any] = {
        "sub": str(subject),
        "type": "refresh",
        "iat": now,
        "exp": expires_at,
    }
    
    if additional_claims:
        payload.update(additional_claims)
    
    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )
    
    return token


# ---------------------------------------------------------------------------
# JWT Token Decoding
# ---------------------------------------------------------------------------

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.

    Raises:
        HTTPException: If the token is invalid or expired.

    Returns:
        JWT payload.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        
        subject = payload.get("sub")
        
        if not subject:
            logger.warning("JWT token does not contain a subject.")
            raise credentials_exception
        
        return payload
    
    except JWTError:
        logger.warning("Invalid or expired JWT token.")
        raise credentials_exception


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate an access token.
    """
    payload = decode_token(token)
    
    token_type = payload.get("type")
    
    if token_type != "access":
        logger.warning("Non-access token used as access token.")
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


def decode_refresh_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a refresh token.
    """
    payload = decode_token(token)
    
    token_type = payload.get("type")
    
    if token_type != "refresh":
        logger.warning("Non-refresh token used as refresh token.")
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


def get_user_id_from_token(token: str) -> str:
    """
    Extract the user ID from an access token.
    """
    payload = decode_access_token(token)
    
    subject = payload.get("sub")
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return str(subject)


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Return the expiration time of a JWT token.
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"verify_exp": False},
        )
        
        exp = payload.get("exp")
        
        if exp is None:
            return None
        
        return datetime.fromtimestamp(exp, tz=timezone.utc)
    
    except JWTError:
        return None


def create_token_pair(
    user_id: str,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> Dict[str, str]:
    """
    Create both access and refresh tokens.

    Returns:
        {
            "access_token": "...",
            "refresh_token": "...",
            "token_type": "bearer"
        }
    """
    access_token = create_access_token(
        data={"sub": user_id},
    )
    
    refresh_token = create_refresh_token(
        subject=user_id,
        additional_claims=additional_claims,
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def validate_password_strength(password: str) -> bool:
    """
    Validate basic password-strength requirements.

    Requirements:
    - At least 8 characters
    - At least one uppercase character
    - At least one lowercase character
    - At least one digit
    """
    if len(password) < 8:
        return False
    
    has_uppercase = any(char.isupper() for char in password)
    has_lowercase = any(char.islower() for char in password)
    has_digit = any(char.isdigit() for char in password)
    
    return has_uppercase and has_lowercase and has_digit


def validate_password_or_raise(password: str) -> None:
    """
    Validate password strength and raise an exception
    when requirements are not satisfied.
    """
    if not validate_password_strength(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Password must contain at least 8 characters, "
                "one uppercase letter, one lowercase letter, "
                "and one digit."
            ),
        )
