"""
CRUD Operations

This module contains database operations for users and grammar corrections.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple

import bcrypt
from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

from config.settings import settings

from . import models, schemas


# Password utilities
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


# User CRUD operations
def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new regular user (non-admin)."""
    hashed_password = hash_password(user.password)
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role="user",  # Always create regular users
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_admin_user(
    db: Session, email: str, full_name: str, password: str
) -> models.User:
    """Create a new admin user (script only)."""
    hashed_password = hash_password(password)
    db_user = models.User(
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
        role="admin",  # Create admin user
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_uuid(db: Session, user_uuid: str) -> Optional[models.User]:
    """Get user by UUID."""
    return db.query(models.User).filter(models.User.uuid == user_uuid).first()


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    """Authenticate user with email and password."""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user(
    db: Session, user_id: int, user_update: schemas.UserUpdate
) -> Optional[models.User]:
    """Update user information."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user


def change_user_password(
    db: Session, user_id: int, current_password: str, new_password: str
) -> bool:
    """Change user password."""
    db_user = get_user(db, user_id)
    if not db_user:
        return False

    if not verify_password(current_password, db_user.hashed_password):
        return False

    db_user.hashed_password = hash_password(new_password)
    db_user.updated_at = datetime.utcnow()
    db.commit()
    return True


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user."""
    db_user = get_user(db, user_id)
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()
    return True


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Get list of users with pagination."""
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user_count(db: Session) -> int:
    """Get total number of users."""
    return db.query(models.User).count()


def get_user_with_correction_count(
    db: Session, user_id: int
) -> Optional[Tuple[models.User, int]]:
    """Get user with their correction count."""
    user = get_user(db, user_id)
    if not user:
        return None

    correction_count = (
        db.query(models.GrammarCorrection)
        .filter(models.GrammarCorrection.user_id == user_id)
        .count()
    )

    return user, correction_count


# Grammar correction CRUD operations
def create_correction(
    db: Session, original_text: str, corrected_text: str, user_id: Optional[int] = None
) -> models.GrammarCorrection:
    """Create a new grammar correction record."""
    db_correction = models.GrammarCorrection(
        original_text=original_text, corrected_text=corrected_text, user_id=user_id
    )
    db.add(db_correction)
    db.commit()
    db.refresh(db_correction)
    return db_correction


def get_correction(
    db: Session, correction_id: int
) -> Optional[models.GrammarCorrection]:
    """Get grammar correction by ID."""
    return (
        db.query(models.GrammarCorrection)
        .filter(models.GrammarCorrection.id == correction_id)
        .first()
    )


def get_corrections(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.GrammarCorrection]:
    """Get list of grammar corrections with pagination."""
    return (
        db.query(models.GrammarCorrection)
        .order_by(desc(models.GrammarCorrection.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def search_corrections(
    db: Session, query: str, skip: int = 0, limit: int = 100
) -> List[models.GrammarCorrection]:
    """Search grammar corrections by text."""
    return (
        db.query(models.GrammarCorrection)
        .filter(
            or_(
                models.GrammarCorrection.original_text.contains(query),
                models.GrammarCorrection.corrected_text.contains(query),
            )
        )
        .order_by(desc(models.GrammarCorrection.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_recent_corrections(
    db: Session, limit: int = 10
) -> List[models.GrammarCorrection]:
    """Get recent grammar corrections."""
    return (
        db.query(models.GrammarCorrection)
        .order_by(desc(models.GrammarCorrection.created_at))
        .limit(limit)
        .all()
    )


def get_corrections_by_date_range(
    db: Session, start_date: datetime, end_date: datetime
) -> List[models.GrammarCorrection]:
    """Get grammar corrections within a date range."""
    return (
        db.query(models.GrammarCorrection)
        .filter(
            and_(
                models.GrammarCorrection.created_at >= start_date,
                models.GrammarCorrection.created_at <= end_date,
            )
        )
        .order_by(desc(models.GrammarCorrection.created_at))
        .all()
    )


def delete_correction(db: Session, correction_id: int) -> bool:
    """Delete a grammar correction."""
    db_correction = get_correction(db, correction_id)
    if not db_correction:
        return False

    db.delete(db_correction)
    db.commit()
    return True


def get_user_corrections(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[models.GrammarCorrection]:
    """Get corrections by user ID."""
    return (
        db.query(models.GrammarCorrection)
        .filter(models.GrammarCorrection.user_id == user_id)
        .order_by(desc(models.GrammarCorrection.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_correction_count_by_user(db: Session, user_id: int) -> int:
    """Get correction count for a specific user."""
    return (
        db.query(models.GrammarCorrection)
        .filter(models.GrammarCorrection.user_id == user_id)
        .count()
    )


def get_all_corrections(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.GrammarCorrection]:
    """Get all corrections across all users (admin only)."""
    return (
        db.query(models.GrammarCorrection)
        .order_by(desc(models.GrammarCorrection.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_total_correction_count(db: Session) -> int:
    """Get total number of corrections across all users."""
    return db.query(models.GrammarCorrection).count()


# Statistics and analytics
def get_database_stats(db: Session) -> dict:
    """Get database statistics."""
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    total_corrections = db.query(models.GrammarCorrection).count()
    total_users = db.query(models.User).count()

    corrections_today = (
        db.query(models.GrammarCorrection)
        .filter(
            and_(
                models.GrammarCorrection.created_at >= today_start,
                models.GrammarCorrection.created_at <= today_end,
            )
        )
        .count()
    )

    users_today = (
        db.query(models.User)
        .filter(
            and_(
                models.User.created_at >= today_start,
                models.User.created_at <= today_end,
            )
        )
        .count()
    )

    return {
        "total_corrections": total_corrections,
        "total_users": total_users,
        "corrections_today": corrections_today,
        "users_today": users_today,
    }


def blacklist_token(db: Session, jti: str, user_id: int, expires_at: datetime) -> models.TokenBlacklist:
    """Add a token to the blacklist."""
    blacklisted_token = models.TokenBlacklist(
        jti=jti,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(blacklisted_token)
    db.commit()
    db.refresh(blacklisted_token)
    return blacklisted_token


def is_token_blacklisted(db: Session, jti: str) -> bool:
    """Check if a token is blacklisted."""
    blacklisted = db.query(models.TokenBlacklist).filter(
        models.TokenBlacklist.jti == jti
    ).first()
    return blacklisted is not None


def cleanup_expired_tokens(db: Session) -> int:
    """Remove expired tokens from blacklist."""
    now = datetime.utcnow()
    expired_tokens = db.query(models.TokenBlacklist).filter(
        models.TokenBlacklist.expires_at < now
    ).delete()
    db.commit()
    return expired_tokens
