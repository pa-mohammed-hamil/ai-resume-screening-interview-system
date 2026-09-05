# Project scaffold file
"""
============================================================
AI Resume Screening & Interview System
Create Admin User
File: scripts/create_admin.py
============================================================

Usage:

    python scripts/create_admin.py

Or inside Docker:

    docker compose exec backend python scripts/create_admin.py

The script reads the following environment variables:

    DATABASE_URL
    ADMIN_EMAIL
    ADMIN_PASSWORD
    ADMIN_FIRST_NAME
    ADMIN_LAST_NAME

Example:

    ADMIN_EMAIL=admin@example.com
    ADMIN_PASSWORD=ChangeMe123!
    ADMIN_FIRST_NAME=System
    ADMIN_LAST_NAME=Administrator
"""

from __future__ import annotations

import getpass
import os
import sys
from pathlib import Path
from typing import Optional


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")
    load_dotenv(PROJECT_ROOT / "backend" / ".env")

except ImportError:
    # python-dotenv is optional.
    # Environment variables can still be supplied directly.
    pass


# ============================================================
# DATABASE IMPORTS
# ============================================================

try:
    from sqlalchemy import select

    from backend.app.database.session import SessionLocal
    from backend.app.models.user import User

except ImportError:
    try:
        from sqlalchemy import select

        from app.database.session import SessionLocal
        from app.models.user import User

    except ImportError as exc:
        print(
            "\nERROR: Unable to import the application database modules."
        )
        print(
            "Run this script from the project root or inside the backend container."
        )
        print(f"\nImport error: {exc}\n")
        sys.exit(1)


# ============================================================
# PASSWORD HASHING
# ============================================================

try:
    from passlib.context import CryptContext

    pwd_context = CryptContext(
        schemes=["bcrypt"],
        deprecated="auto",
    )

    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)

except ImportError:
    try:
        from pwdlib import PasswordHash

        password_hash = PasswordHash.recommended()

        def hash_password(password: str) -> str:
            """Hash a password using pwdlib."""
            return password_hash.hash(password)

    except ImportError as exc:
        print(
            "\nERROR: No supported password hashing library was found."
        )
        print(
            "Install passlib[bcrypt] or pwdlib in backend/requirements.txt."
        )
        print(f"\nImport error: {exc}\n")
        sys.exit(1)


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_ADMIN_EMAIL = "admin@example.com"
DEFAULT_FIRST_NAME = "System"
DEFAULT_LAST_NAME = "Administrator"


# ============================================================
# INPUT HELPERS
# ============================================================

def get_admin_email() -> str:
    """Get and validate the administrator email address."""

    email = os.getenv("ADMIN_EMAIL", "").strip()

    if not email:
        email = input(
            f"Admin email [{DEFAULT_ADMIN_EMAIL}]: "
        ).strip()

    if not email:
        email = DEFAULT_ADMIN_EMAIL

    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError(
            "Please provide a valid email address."
        )

    return email.lower()


def get_admin_password() -> str:
    """Get the administrator password securely."""

    password = os.getenv("ADMIN_PASSWORD", "")

    if password:
        print("Using ADMIN_PASSWORD from environment.")

    else:
        password = getpass.getpass(
            "Admin password: "
        )

    if len(password) < 8:
        raise ValueError(
            "Admin password must contain at least 8 characters."
        )

    confirmation = getpass.getpass(
        "Confirm admin password: "
    )

    if password != confirmation:
        raise ValueError(
            "Passwords do not match."
        )

    return password


def get_optional_value(
    environment_name: str,
    prompt: str,
    default: str,
) -> str:
    """Read an optional string from environment or terminal."""

    value = os.getenv(environment_name, "").strip()

    if value:
        return value

    value = input(
        f"{prompt} [{default}]: "
    ).strip()

    return value or default


# ============================================================
# MODEL HELPERS
# ============================================================

def set_if_attribute(
    user: User,
    attribute: str,
    value,
) -> None:
    """
    Set a model attribute only when that attribute exists.

    This keeps the script compatible with slightly different
    User model implementations.
    """

    if hasattr(user, attribute):
        setattr(user, attribute, value)


def find_existing_user(
    db,
    email: str,
) -> Optional[User]:
    """Find an existing user by email."""

    try:
        statement = select(User).where(
            User.email == email
        )

        return db.execute(statement).scalar_one_or_none()

    except AttributeError:
        return (
            db.query(User)
            .filter(User.email == email)
            .first()
        )


# ============================================================
# ADMIN CREATION
# ============================================================

def create_admin() -> None:
    """Create or update the administrator account."""

    print()
    print("=" * 60)
    print("AI Resume Screening & Interview System")
    print("Administrator Account Setup")
    print("=" * 60)
    print()

    email = get_admin_email()

    first_name = get_optional_value(
        "ADMIN_FIRST_NAME",
        "Admin first name",
        DEFAULT_FIRST_NAME,
    )

    last_name = get_optional_value(
        "ADMIN_LAST_NAME",
        "Admin last name",
        DEFAULT_LAST_NAME,
    )

    password = get_admin_password()

    db = SessionLocal()

    try:
        existing_user = find_existing_user(
            db,
            email,
        )

        # ----------------------------------------------------
        # EXISTING USER
        # ----------------------------------------------------

        if existing_user is not None:

            print()
            print(
                f"User already exists: {email}"
            )

            make_admin = input(
                "Promote this user to admin? [y/N]: "
            ).strip().lower()

            if make_admin not in {"y", "yes"}:
                print()
                print("No changes made.")
                return

            # Update password.
            hashed_password = hash_password(
                password
            )

            if hasattr(existing_user, "hashed_password"):
                existing_user.hashed_password = (
                    hashed_password
                )

            elif hasattr(existing_user, "password_hash"):
                existing_user.password_hash = (
                    hashed_password
                )

            elif hasattr(existing_user, "password"):
                existing_user.password = (
                    hashed_password
                )

            # Update profile.
            set_if_attribute(
                existing_user,
                "first_name",
                first_name,
            )

            set_if_attribute(
                existing_user,
                "last_name",
                last_name,
            )

            # Promote to admin.
            if hasattr(existing_user, "role"):
                existing_user.role = "admin"

            if hasattr(existing_user, "is_admin"):
                existing_user.is_admin = True

            if hasattr(existing_user, "is_active"):
                existing_user.is_active = True

            db.commit()
            db.refresh(existing_user)

            print()
            print("=" * 60)
            print("ADMIN USER UPDATED SUCCESSFULLY")
            print("=" * 60)
            print()
            print(f"Email : {email}")
            print("Role  : admin")
            print("Status: active")
            print()

            return

        # ----------------------------------------------------
        # CREATE NEW USER
        # ----------------------------------------------------

        hashed_password = hash_password(
            password
        )

        user_kwargs = {}

        # Required/common fields.
        if hasattr(User, "email"):
            user_kwargs["email"] = email

        # Password field.
        if hasattr(User, "hashed_password"):
            user_kwargs["hashed_password"] = (
                hashed_password
            )

        elif hasattr(User, "password_hash"):
            user_kwargs["password_hash"] = (
                hashed_password
            )

        elif hasattr(User, "password"):
            user_kwargs["password"] = (
                hashed_password
            )

        # Profile fields.
        if hasattr(User, "first_name"):
            user_kwargs["first_name"] = first_name

        if hasattr(User, "last_name"):
            user_kwargs["last_name"] = last_name

        # Role.
        if hasattr(User, "role"):
            user_kwargs["role"] = "admin"

        # Status.
        if hasattr(User, "is_admin"):
            user_kwargs["is_admin"] = True

        if hasattr(User, "is_active"):
            user_kwargs["is_active"] = True

        user = User(**user_kwargs)

        db.add(user)
        db.commit()
        db.refresh(user)

        print()
        print("=" * 60)
        print("ADMIN USER CREATED SUCCESSFULLY")
        print("=" * 60)
        print()
        print(f"Email : {email}")
        print(f"Name  : {first_name} {last_name}")
        print("Role  : admin")
        print("Status: active")
        print()
        print(
            "You can now sign in through the application."
        )
        print()

    except ValueError:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()

        print()
        print("=" * 60)
        print("FAILED TO CREATE ADMIN USER")
        print("=" * 60)
        print()
        print(f"Error: {exc}")
        print()

        raise

    finally:
        db.close()


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """Application entry point."""

    try:
        create_admin()

        return 0

    except KeyboardInterrupt:
        print()
        print("Operation cancelled.")
        return 130

    except ValueError as exc:
        print()
        print(f"ERROR: {exc}")
        return 1

    except Exception:
        return 1


if __name__ == "__main__":
    raise SystemExit(main())