"""
Application Configuration Settings

This module contains all configuration settings for the Grammar Correction API.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application Information
    APP_NAME: str = "🚀 Pratik's Grammar Correction API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Advanced AI-powered grammar correction system with user management and analytics"
    DEVELOPER_NAME: str = "Ram Dayal (Senior Software Engineer)"
    DEVELOPER_LINKEDIN: str = "https://www.linkedin.com/in/i-am-ramaji/"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    WORKERS: int = 1
    
    # Database Configuration
    DATABASE_URL: str = f"sqlite:///{PROJECT_ROOT}/data/grammar.db"
    
    # AI Model Configuration
    MODEL_NAME: str = "vennify/t5-base-grammar-correction"  # Current model
    # Alternative better models to try:
    # "microsoft/DialoGPT-medium" - Good for conversational grammar
    # "facebook/bart-large-cnn" - Good for text correction
    # "t5-base" - General purpose text-to-text
    # "google/flan-t5-base" - Better instruction following
    MODEL_DIR: str = str(PROJECT_ROOT / "models" / "grammar_correction")
    DEVICE: str = "cpu"  # "cuda" for GPU, "cpu" for CPU
    
    # Model Performance Settings
    MODEL_MAX_LENGTH: int = 512
    MODEL_TEMPERATURE: float = 0.1
    MODEL_TOP_P: float = 0.9
    MODEL_REPETITION_PENALTY: float = 1.1
    MODEL_DO_SAMPLE: bool = False  # Use greedy decoding for consistency
    
    # Fallback Settings
    USE_BASIC_RULES_FIRST: bool = True
    USE_AI_MODEL_FALLBACK: bool = True
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # Security Configuration
    SECRET_KEY: str = "drZYdjltQ4RvAjgmlLjt6cngQ-eNModC8Lj0GIDkTXPZxfkaJM0owuerLx-K0yLyKQfu7WUXEhn_atjViAn-Mg"
    ALGORITHM: str = "HS256"  # Consider RS256 for production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Reduced from 30 to 15 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # Refresh tokens for longer sessions
    
    # Security Enhancements
    JWT_ISSUER: str = "grammar-correction-api"
    JWT_AUDIENCE: str = "grammar-correction-users"
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15
    PASSWORD_MIN_LENGTH: int = 8
    REQUIRE_SPECIAL_CHARS: bool = True
    
    # CORS Configuration
    ALLOWED_ORIGINS: list = ["*"]
    ALLOWED_METHODS: list = ["*"]
    ALLOWED_HEADERS: list = ["*"]
    
    # Pagination Configuration
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # File Paths
    DATA_DIR: Path = PROJECT_ROOT / "data"
    MODELS_DIR: Path = PROJECT_ROOT / "models"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(exist_ok=True)
settings.MODELS_DIR.mkdir(exist_ok=True)
settings.LOGS_DIR.mkdir(exist_ok=True)
