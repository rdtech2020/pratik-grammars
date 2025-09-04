"""
System Routes

This module contains API information and system endpoints.
"""

from fastapi import APIRouter

from config.settings import settings

from ..services import get_model_info

router = APIRouter(
    tags=["System"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/",
    summary="API Information",
    description="Get information about the API and available endpoints",
)
async def root():
    """Get API information and available endpoints."""
    return {
        "message": "🚀 Welcome to Pratik's Grammar Correction API!",
        "developer": settings.DEVELOPER_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "endpoints": {
            "grammar_correction": "/correct",
            "user_management": "/users",
            "database_operations": "/corrections",
            "analytics": "/analytics",
            "system": "/health",
            "documentation": "/docs",
        },
    }


@router.get(
    "/health",
    summary="Health Check",
    description="Check if the API is running and healthy",
)
async def health_check():
    """Check API health status."""
    model_info = get_model_info()
    return {
        "status": "healthy",
        "model_loaded": model_info.get("model_loaded", False),
        "model_name": model_info.get("model_name", "unknown"),
        "device": model_info.get("device", "unknown"),
    }
