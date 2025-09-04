"""
Database Models

This module contains SQLAlchemy models for the Grammar Correction API.
"""

import uuid
from datetime import datetime

from sqlalchemy import (Column, DateTime, ForeignKey, Index, Integer, String,
                        Text, func)
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    """User model for authentication and user management."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(
        String(36),
        unique=True,
        index=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
    )
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user", nullable=False)  # "admin" or "user"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    corrections = relationship("GrammarCorrection", back_populates="user")
    blacklisted_tokens = relationship("TokenBlacklist", back_populates="user")

    __table_args__ = (
        Index("idx_user_email", "email"),
        Index("idx_user_uuid", "uuid"),
        Index("idx_user_created_at", "created_at"),
        Index("idx_user_role", "role"),
    )


class GrammarCorrection(Base):
    """Grammar correction model for storing correction history."""

    __tablename__ = "grammar_corrections"

    id = Column(Integer, primary_key=True, index=True)
    original_text = Column(Text, nullable=False)
    corrected_text = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="corrections")

    __table_args__ = (
        Index("idx_correction_user_id", "user_id"),
        Index("idx_correction_created_at", "created_at"),
        Index("idx_correction_text", "original_text", "corrected_text"),
    )


class TokenBlacklist(Base):
    """Model for tracking revoked JWT tokens."""
    __tablename__ = "token_blacklist"
    
    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(255), unique=True, index=True, nullable=False)  # JWT ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    revoked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="blacklisted_tokens")
    
    __table_args__ = (
        Index('idx_token_blacklist_jti', 'jti'),
        Index('idx_token_blacklist_user_id', 'user_id'),
        Index('idx_token_blacklist_expires_at', 'expires_at'),
    )
