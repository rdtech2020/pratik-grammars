"""
Routes package for Pratik's Grammar Correction API.

This package contains all the route handlers organized by functionality:
- grammar: Core grammar correction endpoints
- users: User management endpoints
- database: Database operations endpoints
- analytics: Statistics and analytics endpoints
- system: System information endpoints
"""

from .analytics import router as analytics_router
from .database import router as database_router
from .grammar import router as grammar_router
from .system import router as system_router
from .users import router as users_router

__all__ = [
    "grammar_router",
    "users_router",
    "database_router",
    "analytics_router",
    "system_router",
]
