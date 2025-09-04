import logging

from .database import Base, engine


def init_db():
    """Initialize database tables"""
    from .models import (  # Import models here to avoid circular imports
        GrammarCorrection, User)

    Base.metadata.create_all(bind=engine)
    logging.info("Database tables initialized")


# Uncomment to auto-create tables when package is imported
# init_db()

# Package-level exports
__all__ = ["engine", "Base", "init_db"]
