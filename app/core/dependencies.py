"""
FastAPI application dependencies.

Provides reusable dependencies for:
- Database sessions
- JWT authentication
- Current user
- Active user validation
- Role-based authorization
- Pagination
- Common request validation
"""

from typing import AsyncGenerator, Callable, Optional

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    InvalidTokenError,
    PermissionDeniedError,
    UserNotFoundError,
)
from app.core.logging import get_logger
from app.core.security import decode_access_token
from app.database.session import AsyncSessionLocal
from app.database.repositories.user_repository import UserRepository


# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# HTTP Bearer Authentication
# ---------------------------------------------------------------------------

security = HTTPBearer(
    auto_error=True,
)


# ---------------------------------------------------------------------------
# Database Dependency
# ---------------------------------------------------------------------------

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an asynchronous database session.

    The session is automatically closed after the request.
    """

    async with AsyncSessionLocal() as session:
        try:
            yield session

        except Exception:
            await session.rollback()
            raise

        finally:
            await session.close()


# ---------------------------------------------------------------------------
# User Repository Dependency
# ---------------------------------------------------------------------------

def get_user_repository(
    db: AsyncSession = Depends(get_db),
) -> UserRepository:
    """
    Create a UserRepository using the current database session.
    """

    return UserRepository(db)


# ---------------------------------------------------------------------------
# Current User ID
# ---------------------------------------------------------------------------

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
) -> str:
    """
    Extract and validate the current user's ID from the JWT.

    Returns:
        User ID stored in the token's `sub` claim.
    """

    token = credentials.credentials

    try:
        payload = decode_access_token(token)

    except HTTPException:
        raise

    except Exception as exc:
        logger.warning(
            "Unable to decode authentication token: %s",
            exc,
        )

        raise InvalidTokenError()

    user_id = payload.get("sub")

    if not user_id:
        raise InvalidTokenError(
            message="Authentication token does not contain a user ID."
        )

    return str(user_id)


# ---------------------------------------------------------------------------
# Current User
# ---------------------------------------------------------------------------

async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    user_repository: UserRepository = Depends(
        get_user_repository
    ),
):
    """
    Retrieve the authenticated user from the database.
    """

    user = await user_repository.get_by_id(user_id)

    if user is None:
        logger.warning(
            "Authenticated user not found: %s",
            user_id,
        )

        raise UserNotFoundError()

    return user


# ---------------------------------------------------------------------------
# Active User
# ---------------------------------------------------------------------------

async def get_current_active_user(
    current_user=Depends(get_current_user),
):
    """
    Ensure the authenticated user is active.
    """

    is_active = getattr(
        current_user,
        "is_active",
        True,
    )

    if not is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive.",
        )

    return current_user


# ---------------------------------------------------------------------------
# Current Admin
# ---------------------------------------------------------------------------

async def get_current_admin(
    current_user=Depends(get_current_active_user),
):
    """
    Ensure the current user has an admin role.
    """

    role = getattr(
        current_user,
        "role",
        None,
    )

    if role != "admin":
        logger.warning(
            "Admin access denied for user: %s",
            getattr(current_user, "id", "unknown"),
        )

        raise PermissionDeniedError(
            message="Administrator access is required."
        )

    return current_user


# ---------------------------------------------------------------------------
# Role-Based Authorization
# ---------------------------------------------------------------------------

def require_role(
    *allowed_roles: str,
) -> Callable:
    """
    Create a dependency that requires one of the supplied roles.

    Example:

        @router.get(
            "/admin",
            dependencies=[Depends(require_role("admin"))],
        )
        async def admin_endpoint():
            ...
    """

    async def role_dependency(
        current_user=Depends(
            get_current_active_user
        ),
    ):
        role = getattr(
            current_user,
            "role",
            None,
        )

        if role not in allowed_roles:
            logger.warning(
                "Role access denied. "
                "Required=%s, actual=%s, user=%s",
                allowed_roles,
                role,
                getattr(
                    current_user,
                    "id",
                    "unknown",
                ),
            )

            raise PermissionDeniedError(
                message=(
                    "You do not have permission "
                    "to access this resource."
                ),
                details={
                    "required_roles": list(
                        allowed_roles
                    )
                },
            )

        return current_user

    return role_dependency


# ---------------------------------------------------------------------------
# Recruiter Dependency
# ---------------------------------------------------------------------------

async def get_current_recruiter(
    current_user=Depends(
        get_current_active_user
    ),
):
    """
    Ensure the current user is a recruiter.
    """

    allowed_roles = {
        "recruiter",
        "admin",
    }

    role = getattr(
        current_user,
        "role",
        None,
    )

    if role not in allowed_roles:
        raise PermissionDeniedError(
            message="Recruiter access is required."
        )

    return current_user


# ---------------------------------------------------------------------------
# Candidate Dependency
# ---------------------------------------------------------------------------

async def get_current_candidate(
    current_user=Depends(
        get_current_active_user
    ),
):
    """
    Ensure the current user is a candidate.
    """

    allowed_roles = {
        "candidate",
        "admin",
    }

    role = getattr(
        current_user,
        "role",
        None,
    )

    if role not in allowed_roles:
        raise PermissionDeniedError(
            message="Candidate access is required."
        )

    return current_user


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

async def pagination_params(
    page: int = Query(
        default=1,
        ge=1,
        description="Page number.",
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of records per page.",
    ),
) -> dict:
    """
    Provide standardized pagination parameters.
    """

    offset = (page - 1) * page_size

    return {
        "page": page,
        "page_size": page_size,
        "offset": offset,
        "limit": page_size,
    }


# ---------------------------------------------------------------------------
# Optional Authentication
# ---------------------------------------------------------------------------

optional_security = HTTPBearer(
    auto_error=False,
)


async def get_optional_user_id(
    credentials: Optional[
        HTTPAuthorizationCredentials
    ] = Depends(optional_security),
) -> Optional[str]:
    """
    Return the authenticated user ID when a token is supplied.

    Unlike get_current_user_id(), this dependency does not
    require authentication.
    """

    if credentials is None:
        return None

    try:
        payload = decode_access_token(
            credentials.credentials
        )

        user_id = payload.get("sub")

        if not user_id:
            return None

        return str(user_id)

    except Exception:
        return None


# ---------------------------------------------------------------------------
# Request Configuration
# ---------------------------------------------------------------------------

def get_app_settings():
    """
    Provide application settings through FastAPI dependency injection.
    """

    return settings
