"""
Grammar Correction Routes

This module contains the core grammar correction API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas
from ..auth import get_current_user
from ..crud import create_correction
from ..database import get_db
from ..services import correct_grammar

router = APIRouter(
    prefix="/correct",
    tags=["Grammar Correction"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=schemas.CorrectionResponse,
    summary="Correct grammar in text",
    description="Correct grammatical errors in text using advanced T5 transformer models. Requires authentication. Automatically saves corrections to database linked to the authenticated user.",
    response_description="Grammar correction result with original and corrected text",
    status_code=200,
)
async def correct_text(
    request: schemas.TextRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Correct grammar in the provided text (authenticated users only)."""
    try:
        corrected_text = correct_grammar(request.text)

        # Save correction with user ID
        create_correction(
            db,
            original_text=request.text,
            corrected_text=corrected_text,
            user_id=current_user.id,
        )

        return {"original": request.text, "corrected": corrected_text}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Grammar correction failed: {str(e)}"
        )


@router.post(
    "/anonymous",
    response_model=schemas.CorrectionResponse,
    summary="Correct grammar in text (anonymous)",
    description="Correct grammatical errors in text without authentication. Corrections are not saved to database.",
    response_description="Grammar correction result with original and corrected text",
    status_code=200,
)
async def correct_text_anonymous(request: schemas.TextRequest):
    """Correct grammar in the provided text (anonymous users, no database storage)."""
    try:
        corrected_text = correct_grammar(request.text)
        return {"original": request.text, "corrected": corrected_text}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Grammar correction failed: {str(e)}"
        )
