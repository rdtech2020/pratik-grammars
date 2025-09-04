"""
Main FastAPI Application

This is the main entry point for Pratik's Grammar Correction API.
It initializes the FastAPI application and includes all route modules.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings

from .database import Base, engine
from .routes import (analytics_router, database_router, grammar_router,
                     system_router, users_router)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    contact={
        "name": settings.DEVELOPER_NAME,
        "url": settings.DEVELOPER_LINKEDIN,
    },
    openapi_tags=[
        {
            "name": "Grammar Correction",
            "description": "Core AI-powered grammar correction operations",
        },
        {
            "name": "User Management",
            "description": "User registration, authentication, and profile management",
        },
        {
            "name": "Database Operations",
            "description": "CRUD operations for grammar corrections with search and filtering",
        },
        {
            "name": "Analytics",
            "description": "Statistics and reporting endpoints",
        },
        {
            "name": "System",
            "description": "API information and system endpoints",
        },
    ],
    servers=[
        {
            "url": f"http://localhost:{settings.PORT}",
            "description": "Development server",
        },
        {"url": "https://api.pratik-grammars.com", "description": "Production server"},
    ],
)

# Add CORS middleware to fix Swagger UI issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

# Include all route modules
app.include_router(grammar_router)
app.include_router(users_router)
app.include_router(database_router)
app.include_router(analytics_router)
app.include_router(system_router)
