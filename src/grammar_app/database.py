"""
Database Configuration

This module handles database connection and session management.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import settings

from .base import Base

# Use database URL from settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Create database engine with SQLite
# check_same_thread=False is only needed for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session factory - each request gets its own session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get DB session
def get_db():
    """
    Database session dependency.

    Provides a database session for each request and ensures proper cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
