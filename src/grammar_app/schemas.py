"""
Pydantic Schemas

This module contains Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


# Base schemas
class TextRequest(BaseModel):
    """Request schema for grammar correction."""

    text: str


class CorrectionResponse(BaseModel):
    """Response schema for grammar correction."""

    original: str
    corrected: str


# User schemas
class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: str
    role: str = "user"  # Default to regular user


class UserCreate(UserBase):
    """Schema for user creation."""

    password: str


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for user updates."""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None


class UserPasswordChange(BaseModel):
    """Schema for password change."""

    current_password: str
    new_password: str


class UserResponse(UserBase):
    """Schema for user responses."""

    id: int
    uuid: str
    created_at: datetime
    updated_at: datetime
    total_corrections: int = 0

    class Config:
        from_attributes = True


class UserList(BaseModel):
    """Schema for user list responses."""

    users: List[UserResponse]
    total: int
    page: int
    per_page: int


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthResponse(BaseModel):
    """Schema for authentication responses."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Schema for token data."""

    email: Optional[str] = None


# Grammar correction schemas
class GrammarCorrectionBase(BaseModel):
    """Base grammar correction schema."""

    original_text: str
    corrected_text: str


class GrammarCorrectionCreate(GrammarCorrectionBase):
    """Schema for creating grammar corrections."""

    user_id: Optional[int] = None


class GrammarCorrectionResponse(GrammarCorrectionBase):
    """Schema for grammar correction responses."""

    id: int
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GrammarCorrectionList(BaseModel):
    """Schema for grammar correction list responses."""

    corrections: List[GrammarCorrectionResponse]
    total: int
    page: int
    per_page: int


# Database operation schemas
class DatabaseStats(BaseModel):
    """Schema for database statistics."""

    total_corrections: int
    total_users: int
    corrections_today: int
    users_today: int


class SearchRequest(BaseModel):
    """Schema for search requests."""

    query: str
    page: int = 1
    per_page: int = 20
