"""
User Management Routes

This module contains user registration, authentication, and profile management endpoints.
"""

from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from config.settings import settings

from .. import crud, schemas
from ..auth import (authenticate_user, create_access_token, create_user_token,
                    get_current_admin_user, get_current_user, verify_token)
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=["User Management"],
    responses={404: {"description": "User not found"}},
)


@router.post(
    "/register",
    response_model=schemas.AuthResponse,
    summary="Register new user",
    description="Create a new user account with email and password. Returns JWT token for immediate authentication.",
    status_code=201,
)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user and return JWT token."""
    # Check if user already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    created_user = crud.create_user(db=db, user=user)

    # Create secure access token using user ID instead of email
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_user_token(
        user_id=created_user.id, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": created_user,
    }


@router.post(
    "/login",
    response_model=schemas.AuthResponse,
    summary="User login",
    description="Authenticate user with email and password. Returns JWT token for API access.",
)
async def login_user(
    user_credentials: schemas.UserLogin, db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token."""
    user = authenticate_user(user_credentials.email, user_credentials.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # Create secure access token using user ID instead of email
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_user_token(
        user_id=user.id, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user,
    }


@router.post(
    "/logout",
    summary="User logout",
    description="Logout user and revoke JWT token.",
    status_code=200,
)
async def logout_user(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Logout user and blacklist their token."""
    try:
        # Get token from request
        from fastapi import Request
        request = Request()
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
            # Decode token to get JTI
            payload = verify_token(token)
            if payload:
                jti = payload.get("jti")
                exp_timestamp = payload.get("exp")
                
                if jti and exp_timestamp:
                    # Convert timestamp to datetime
                    from datetime import datetime
                    expires_at = datetime.fromtimestamp(exp_timestamp)
                    
                    # Blacklist the token
                    from ..crud import blacklist_token
                    blacklist_token(db, jti=jti, user_id=current_user.id, expires_at=expires_at)
                    
                    return {"message": "Successfully logged out", "token_revoked": True}
        
        return {"message": "Successfully logged out", "token_revoked": False}
        
    except Exception as e:
        print(f"Logout error: {e}")
        return {"message": "Successfully logged out", "token_revoked": False}


@router.get(
    "/me",
    response_model=schemas.UserResponse,
    summary="Get current user profile",
    description="Get profile information for the currently authenticated user",
)
async def get_current_user_profile(
    current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user profile."""
    # Get correction count for current user
    from ..crud import get_user_with_correction_count

    user, correction_count = get_user_with_correction_count(db, current_user.id)
    user.total_corrections = correction_count
    return user


@router.get(
    "/{user_id}",
    response_model=schemas.UserResponse,
    summary="Get user by ID",
    description="Retrieve user information by user ID (admin only)",
)
async def get_user(
    user_id: int,
    current_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get user by ID (admin only)."""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Get correction count
    user, correction_count = crud.get_user_with_correction_count(db, user_id)
    user.total_corrections = correction_count
    return user


@router.put(
    "/me",
    response_model=schemas.UserResponse,
    summary="Update current user profile",
    description="Update profile information for the currently authenticated user",
)
async def update_current_user(
    user_update: schemas.UserUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user profile."""
    # Prevent role escalation - regular users cannot change their role
    update_data = user_update.dict(exclude_unset=True)
    if "role" in update_data:
        del update_data["role"]  # Remove role from update data

    # Create a new update object without role
    safe_update = schemas.UserUpdate(**update_data)

    db_user = crud.update_user(db, user_id=current_user.id, user_update=safe_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put(
    "/{user_id}",
    response_model=schemas.UserResponse,
    summary="Update user by ID",
    description="Update user information by user ID (admin only)",
)
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    current_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Update user information (admin only)."""
    db_user = crud.update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put(
    "/me/change-password",
    summary="Change current user password",
    description="Change password for the currently authenticated user",
)
async def change_current_user_password(
    password_change: schemas.UserPasswordChange,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change current user password."""
    success = crud.change_user_password(
        db,
        user_id=current_user.id,
        current_password=password_change.current_password,
        new_password=password_change.new_password,
    )
    if not success:
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    return {"message": "Password changed successfully"}


@router.put(
    "/{user_id}/change-password",
    summary="Change user password by ID",
    description="Change password for a specific user (admin only)",
)
async def change_user_password(
    user_id: int,
    password_change: schemas.UserPasswordChange,
    current_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Change user password (admin only)."""
    success = crud.change_user_password(
        db,
        user_id=user_id,
        current_password=password_change.current_password,
        new_password=password_change.new_password,
    )
    if not success:
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    return {"message": "Password changed successfully"}


@router.delete(
    "/{user_id}",
    summary="Delete user",
    description="Delete user account and all associated data (admin only)",
)
async def delete_user(
    user_id: int,
    current_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Delete user account (admin only)."""
    success = crud.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@router.get(
    "/",
    response_model=schemas.UserList,
    summary="List users",
    description="Get paginated list of all users (admin only)",
)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get paginated list of users (admin only)."""
    skip = (page - 1) * per_page
    users = crud.get_users(db, skip=skip, limit=per_page)
    total = crud.get_user_count(db)

    return {"users": users, "total": total, "page": page, "per_page": per_page}
