"""
Base Model Configuration

This module contains the SQLAlchemy Base class to avoid circular imports.
"""

from sqlalchemy.ext.declarative import declarative_base

# Base class for all models
Base = declarative_base()
