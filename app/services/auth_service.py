# Project scaffold file
# backend/app/services/auth_service.py

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User


class AuthService:
    """Authentication and authorization business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================================================================
    # User Lookup
    # ==================================================================

    async def get_user_by_id(
        self,
        user_id: int,
    ) -> Optional[User]:
        """Return a user by primary key."""

        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )

        return result.scalar_one_or_none()

    async def get_user_by_email(
        self,
        email: str,
    ) -> Optional[User]:
        """Return a user by email address."""

        normalized_email = email.strip().lower()

        result = await self.db.execute(
            select(User).where(
                User.email == normalized_email
            )
        )

        return result.scalar_one_or_none()

    # ==================================================================
    # Registration
    # ==================================================================

    async def register_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        **extra_fields: Any,
    ) -> User:
        """Create and persist a new user."""

        normalized_email = email.strip().lower()

        existing_user = await self.get_user_by_email(
            normalized_email
        )

        if existing_user:
            raise ValueError(
                "A user with this email already exists."
            )

        user_data = {
            "email": normalized_email,
            "password_hash": hash_password(password),
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
        }

        user_data.update(extra_fields)

        user = User(**user_data)

        self.db.add(user)

        await self.db.commit()
        await self.db.refresh(user)

        return user

    # ==================================================================
    # Password Authentication
    # ==================================================================

    async def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> Optional[User]:
        """
        Validate email/password credentials.

        Returns the authenticated user or None when credentials
        are invalid.
        """

        user = await self.get_user_by_email(email)

        if not user:
            return None

        password_hash = getattr(
            user,
            "password_hash",
            None,
        )

        if not password_hash:
            return None

        if not verify_password(
            password,
            password_hash,
        ):
            return None

        if hasattr(user, "is_active") and not user.is_active:
            return None

        return user

    # ==================================================================
    # Login
    # ==================================================================

    async def login(
        self,
        email: str,
        password: str,
    ) -> Optional[dict[str, Any]]:
        """
        Authenticate a user and generate JWT tokens.

        Returns None for invalid credentials.
        """

        user = await self.authenticate_user(
            email=email,
            password=password,
        )

        if not user:
            return None

        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "type": "access",
            }
        )

        refresh_token = create_refresh_token(
            data={
                "sub": str(user.id),
                "type": "refresh",
            }
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user,
        }

    # ==================================================================
    # Access Token
    # ==================================================================

    def create_user_access_token(
        self,
        user: User,
    ) -> str:
        """Create an access token for a user."""

        return create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "type": "access",
            }
        )

    # ==================================================================
    # Refresh Token
    # ==================================================================

    def create_user_refresh_token(
        self,
        user: User,
    ) -> str:
        """Create a refresh token for a user."""

        return create_refresh_token(
            data={
                "sub": str(user.id),
                "type": "refresh",
            }
        )

    async def refresh_access_token(
        self,
        refresh_token: str,
    ) -> Optional[dict[str, str]]:
        """Validate a refresh token and issue a new access token."""

        payload = self.decode_token(refresh_token)

        if not payload:
            return None

        if payload.get("type") != "refresh":
            return None

        subject = payload.get("sub")

        if not subject:
            return None

        try:
            user_id = int(subject)
        except (TypeError, ValueError):
            return None

        user = await self.get_user_by_id(user_id)

        if not user:
            return None

        if hasattr(user, "is_active") and not user.is_active:
            return None

        access_token = self.create_user_access_token(user)

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    # ==================================================================
    # Token Validation
    # ==================================================================

    def decode_token(
        self,
        token: str,
    ) -> Optional[dict[str, Any]]:
        """Decode and validate a JWT."""

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )

            return payload

        except JWTError:
            return None

    async def get_user_from_token(
        self,
        token: str,
    ) -> Optional[User]:
        """Resolve the authenticated user from a JWT."""

        payload = self.decode_token(token)

        if not payload:
            return None

        if payload.get("type") != "access":
            return None

        subject = payload.get("sub")

        if not subject:
            return None

        try:
            user_id = int(subject)
        except (TypeError, ValueError):
            return None

        user = await self.get_user_by_id(user_id)

        if not user:
            return None

        if hasattr(user, "is_active") and not user.is_active:
            return None

        return user

    # ==================================================================
    # Password Change
    # ==================================================================

    async def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ) -> bool:
        """Change the authenticated user's password."""

        password_hash = getattr(
            user,
            "password_hash",
            None,
        )

        if not password_hash:
            return False

        if not verify_password(
            current_password,
            password_hash,
        ):
            return False

        if current_password == new_password:
            raise ValueError(
                "New password must be different from the current password."
            )

        user.password_hash = hash_password(
            new_password
        )

        await self.db.commit()
        await self.db.refresh(user)

        return True

    # ==================================================================
    # Password Reset
    # ==================================================================

    def create_password_reset_token(
        self,
        user: User,
        expires_minutes: int = 30,
    ) -> str:
        """Create a short-lived password reset token."""

        now = datetime.now(timezone.utc)

        expire = now + timedelta(
            minutes=expires_minutes
        )

        payload = {
            "sub": str(user.id),
            "type": "password_reset",
            "exp": expire,
        }

        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

    async def reset_password(
        self,
        reset_token: str,
        new_password: str,
    ) -> bool:
        """Reset a user's password using a reset token."""

        payload = self.decode_token(reset_token)

        if not payload:
            return False

        if payload.get("type") != "password_reset":
            return False

        subject = payload.get("sub")

        if not subject:
            return False

        try:
            user_id = int(subject)
        except (TypeError, ValueError):
            return False

        user = await self.get_user_by_id(user_id)

        if not user:
            return False

        user.password_hash = hash_password(
            new_password
        )

        await self.db.commit()

        return True

    # ==================================================================
    # Account Status
    # ==================================================================

    async def activate_user(
        self,
        user: User,
    ) -> User:
        """Activate a user account."""

        user.is_active = True

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def deactivate_user(
        self,
        user: User,
    ) -> User:
        """Deactivate a user account."""

        user.is_active = False

        await self.db.commit()
        await self.db.refresh(user)

        return user

    # ==================================================================
    # Email Verification
    # ==================================================================

    def create_email_verification_token(
        self,
        user: User,
        expires_minutes: int = 60,
    ) -> str:
        """Create an email verification token."""

        now = datetime.now(timezone.utc)

        expire = now + timedelta(
            minutes=expires_minutes
        )

        payload = {
            "sub": str(user.id),
            "type": "email_verification",
            "exp": expire,
        }

        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

    async def verify_email(
        self,
        verification_token: str,
    ) -> bool:
        """Verify a user's email address."""

        payload = self.decode_token(
            verification_token
        )

        if not payload:
            return False

        if payload.get("type") != "email_verification":
            return False

        subject = payload.get("sub")

        if not subject:
            return False

        try:
            user_id = int(subject)
        except (TypeError, ValueError):
            return False

        user = await self.get_user_by_id(user_id)

        if not user:
            return False

        if hasattr(user, "is_verified"):
            user.is_verified = True

        await self.db.commit()

        return True

