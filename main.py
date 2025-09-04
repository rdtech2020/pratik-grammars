#!/usr/bin/env python3
"""
Main Application Entry Point

This is the main entry point for Pratik's Grammar Correction API.
It initializes the FastAPI application and starts the server.
"""

import uvicorn
from src.grammar_app.main import app
from config.settings import settings

if __name__ == "__main__":
    """Start the FastAPI server."""
    uvicorn.run(
        "src.grammar_app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        workers=settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower()
    )
