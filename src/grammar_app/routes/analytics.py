"""
Analytics Routes

This module contains statistics and reporting endpoints.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..auth import get_current_admin_user, get_current_user
from ..database import get_db

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/stats",
    response_model=schemas.DatabaseStats,
    summary="Get database statistics",
    description="Get comprehensive statistics about the database (admin only)",
)
async def get_database_stats(
    current_user=Depends(get_current_admin_user), db: Session = Depends(get_db)
):
    """Get database statistics (admin only)."""
    return crud.get_database_stats(db)


@router.get(
    "/my-stats",
    summary="Get current user statistics",
    description="Get statistics for the currently authenticated user",
)
async def get_my_stats(
    current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get statistics for the current user."""
    correction_count = crud.get_correction_count_by_user(db, current_user.id)

    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "total_corrections": correction_count,
        "member_since": current_user.created_at,
    }


@router.get(
    "/my-corrections",
    response_model=List[schemas.GrammarCorrectionResponse],
    summary="Get current user corrections",
    description="Get all corrections made by the currently authenticated user",
)
async def get_my_corrections(
    limit: int = Query(50, ge=1, le=100, description="Number of corrections"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get corrections for the current user."""
    return crud.get_user_corrections(db, user_id=current_user.id, limit=limit)


@router.get(
    "/my-correction-count",
    summary="Get current user correction count",
    description="Get the total number of corrections made by the current user",
)
async def get_my_correction_count(
    current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get correction count for the current user."""
    count = crud.get_correction_count_by_user(db, user_id=current_user.id)
    return {"user_id": current_user.id, "total_corrections": count}


# Admin-only endpoints for accessing any user's data using UUIDs
@router.get(
    "/admin/users/{user_uuid}/corrections",
    response_model=List[schemas.GrammarCorrectionResponse],
    summary="Get any user corrections (admin only)",
    description="Get all corrections made by a specific user (admin only)",
)
async def get_any_user_corrections_admin(
    user_uuid: str,
    limit: int = Query(50, ge=1, le=100, description="Number of corrections"),
    current_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get corrections by user UUID (admin only)."""
    # Get user by UUID
    user = crud.get_user_by_uuid(db, user_uuid=user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.get_user_corrections(db, user_id=user.id, limit=limit)


@router.get(
    "/admin/users/{user_uuid}/correction-count",
    summary="Get any user correction count (admin only)",
    description="Get the total number of corrections made by a user (admin only)",
)
async def get_any_user_correction_count_admin(
    user_uuid: str,
    current_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get correction count for a specific user (admin only)."""
    # Get user by UUID
    user = crud.get_user_by_uuid(db, user_uuid=user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    count = crud.get_correction_count_by_user(db, user_id=user.id)
    return {"user_uuid": user_uuid, "total_corrections": count}
