"""
Database Operation Routes

This module contains CRUD operations for grammar corrections with search and filtering.
"""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..auth import get_current_admin_user, get_current_user
from ..database import get_db

router = APIRouter(
    prefix="/corrections",
    tags=["Database Operations"],
    responses={404: {"description": "Correction not found"}},
)


@router.get(
    "/",
    response_model=schemas.GrammarCorrectionList,
    summary="List corrections",
    description="Get paginated list of grammar corrections. Returns user's own corrections when authenticated.",
)
async def list_corrections(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get paginated list of grammar corrections for the authenticated user."""
    skip = (page - 1) * per_page
    corrections = crud.get_user_corrections(
        db, user_id=current_user.id, skip=skip, limit=per_page
    )
    total = crud.get_correction_count_by_user(db, current_user.id)

    return {
        "corrections": corrections,
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.get(
    "/{correction_id}",
    response_model=schemas.GrammarCorrectionResponse,
    summary="Get correction by ID",
    description="Retrieve a specific grammar correction by ID (user can only access their own corrections)",
)
async def get_correction(
    correction_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get grammar correction by ID (user can only access their own corrections)."""
    correction = crud.get_correction(db, correction_id=correction_id)
    if correction is None:
        raise HTTPException(status_code=404, detail="Correction not found")

    # Ensure user can only access their own corrections
    if correction.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You can only view your own corrections",
        )

    return correction


@router.get(
    "/recent",
    response_model=List[schemas.GrammarCorrectionResponse],
    summary="Get recent corrections",
    description="Get the most recent grammar corrections for the authenticated user",
)
async def get_recent_corrections(
    limit: int = Query(10, ge=1, le=50, description="Number of recent corrections"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get recent grammar corrections for the authenticated user."""
    return crud.get_user_corrections(db, user_id=current_user.id, limit=limit)


@router.get(
    "/search",
    response_model=List[schemas.GrammarCorrectionResponse],
    summary="Search corrections",
    description="Search grammar corrections by text content (user's own corrections only)",
)
async def search_corrections(
    query: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search grammar corrections by text (user's own corrections only)."""
    skip = (page - 1) * per_page
    # Note: This would need to be updated in CRUD to filter by user_id
    corrections = crud.search_corrections(db, query=query, skip=skip, limit=per_page)

    # Filter to only user's corrections
    user_corrections = [c for c in corrections if c.user_id == current_user.id]
    return user_corrections


@router.get(
    "/date-range",
    response_model=List[schemas.GrammarCorrectionResponse],
    summary="Get corrections by date range",
    description="Get grammar corrections within a specific date range (user's own corrections only)",
)
async def get_corrections_by_date_range(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get grammar corrections within a date range (user's own corrections only)."""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
        )

    # Note: This would need to be updated in CRUD to filter by user_id
    all_corrections = crud.get_corrections_by_date_range(
        db, start_date=start, end_date=end
    )

    # Filter to only user's corrections
    user_corrections = [c for c in all_corrections if c.user_id == current_user.id]
    return user_corrections


@router.delete(
    "/{correction_id}",
    summary="Delete correction",
    description="Delete a specific grammar correction (user can only delete their own corrections)",
)
async def delete_correction(
    correction_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete grammar correction by ID (user can only delete their own corrections)."""
    correction = crud.get_correction(db, correction_id=correction_id)
    if correction is None:
        raise HTTPException(status_code=404, detail="Correction not found")

    # Ensure user can only delete their own corrections
    if correction.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You can only delete your own corrections",
        )

    success = crud.delete_correction(db, correction_id=correction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Correction not found")
    return {"message": "Correction deleted successfully"}


# Admin-only endpoints
@router.get(
    "/admin/all",
    response_model=schemas.GrammarCorrectionList,
    summary="List all corrections (admin only)",
    description="Get paginated list of all grammar corrections across all users (admin only)",
)
async def list_all_corrections_admin(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get paginated list of all grammar corrections (admin only)."""
    skip = (page - 1) * per_page
    corrections = crud.get_all_corrections(db, skip=skip, limit=per_page)
    total = crud.get_total_correction_count(db)

    return {
        "corrections": corrections,
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.get(
    "/admin/{correction_id}",
    response_model=schemas.GrammarCorrectionResponse,
    summary="Get any correction by ID (admin only)",
    description="Retrieve any grammar correction by ID (admin only)",
)
async def get_any_correction_admin(
    correction_id: int,
    current_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get any grammar correction by ID (admin only)."""
    correction = crud.get_correction(db, correction_id=correction_id)
    if correction is None:
        raise HTTPException(status_code=404, detail="Correction not found")

    return correction


@router.delete(
    "/admin/{correction_id}",
    summary="Delete any correction (admin only)",
    description="Delete any grammar correction by ID (admin only)",
)
async def delete_any_correction_admin(
    correction_id: int,
    current_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Delete any grammar correction by ID (admin only)."""
    success = crud.delete_correction(db, correction_id=correction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Correction not found")
    return {"message": "Correction deleted successfully"}


@router.get(
    "/admin/search",
    response_model=List[schemas.GrammarCorrectionResponse],
    summary="Search all corrections (admin only)",
    description="Search all grammar corrections by text content (admin only)",
)
async def search_all_corrections_admin(
    query: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user=Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Search all grammar corrections by text (admin only)."""
    skip = (page - 1) * per_page
    corrections = crud.search_corrections(db, query=query, skip=skip, limit=per_page)
    return corrections
