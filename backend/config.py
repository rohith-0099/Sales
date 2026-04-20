"""
Configuration module for centralized settings management.
Loads environment variables and provides typed configuration objects.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


# Load environment variables
env_file = Path(__file__).resolve().parent / ".env"
load_dotenv(env_file)


@dataclass
class FlaskConfig:
    """Flask application configuration."""
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    JSON_SORT_KEYS: bool = False


@dataclass
class UploadConfig:
    """Upload session configuration."""
    TTL_MINUTES: int = 90
    MAX_SESSIONS: int = 25
    REQUEST_TIMEOUT: int = 30  # seconds


@dataclass  
class AIConfig:
    """AI engine configuration."""
    API_KEY: str = ""
    MODEL: str = "llama-3.3-70b-versatile"
    TIMEOUT: int = 30


@dataclass
class AppConfig:
    """Main application configuration."""
    flask: FlaskConfig
    upload: UploadConfig
    ai: AIConfig
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.ai.API_KEY:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("GROQ_API_KEY not configured - AI insights will be unavailable")


def load_config() -> AppConfig:
    """Load configuration from environment variables."""
    flask_config = FlaskConfig(
        DEBUG=os.getenv("FLASK_DEBUG", "false").lower() == "true",
        HOST=os.getenv("FLASK_HOST", "0.0.0.0"),
        PORT=int(os.getenv("FLASK_PORT", 5000)),
    )
    
    upload_config = UploadConfig(
        TTL_MINUTES=int(os.getenv("UPLOAD_TTL_MINUTES", 90)),
        MAX_SESSIONS=int(os.getenv("MAX_UPLOAD_SESSIONS", 25)),
        REQUEST_TIMEOUT=int(os.getenv("REQUEST_TIMEOUT", 30)),
    )
    
    ai_config = AIConfig(
        API_KEY=os.getenv("GROQ_API_KEY", ""),
        MODEL=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        TIMEOUT=int(os.getenv("AI_TIMEOUT", 30)),
    )
    
    return AppConfig(
        flask=flask_config,
        upload=upload_config,
        ai=ai_config,
    )


# Singleton instance
_config = None


def get_config() -> AppConfig:
    """Get the application configuration."""
    global _config
    if _config is None:
        _config = load_config()
    return _config
