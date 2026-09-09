"""Configuration module for the RuralEdge Government Data Ingestion Pipeline.

Handles loading environment variables, credential validation, and logging setup.
"""

import logging
import os
import sys
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

# Base directory paths
INGESTION_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = INGESTION_DIR.parent

# Load environment variables: check ingestion/.env first, then root .env
env_file_ingestion = INGESTION_DIR / ".env"
env_file_root = PROJECT_ROOT / ".env"

if env_file_ingestion.is_file():
    load_dotenv(dotenv_path=env_file_ingestion)
elif env_file_root.is_file():
    load_dotenv(dotenv_path=env_file_root)
else:
    # Attempt general dotenv load from current working directory
    load_dotenv()

# Logging Configuration
LOG_LEVEL_STR = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)


def setup_logging(name: str = "ingestion") -> logging.Logger:
    """Configures and returns a standardized logger for ingestion pipeline components."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(LOG_LEVEL)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(LOG_LEVEL)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


logger = setup_logging("config")


class Config:
    """Ingestion pipeline configuration holder."""

    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "").strip()
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "").strip()

    # HTTP Fetcher Settings
    DEFAULT_REQUEST_TIMEOUT: int = int(os.getenv("DEFAULT_REQUEST_TIMEOUT", "15"))
    USER_AGENT: str = os.getenv(
        "USER_AGENT",
        "RuralEdge-Ingestion-Pipeline/1.0 (Government Data Indexing)",
    )
    # Maximum response size limit (Default: 10MB = 10 * 1024 * 1024 bytes)
    MAX_RESPONSE_SIZE: int = int(
        os.getenv("MAX_RESPONSE_SIZE", str(10 * 1024 * 1024))
    )

    @classmethod
    def validate(cls) -> bool:
        """Validates that all required configuration settings are present and well-formed.

        Raises:
            ValueError: If SUPABASE_URL or SUPABASE_KEY are missing or invalid.
        """
        if not cls.SUPABASE_URL:
            logger.error("SUPABASE_URL is missing. Please set it in your .env file.")
            raise ValueError(
                "Missing SUPABASE_URL environment variable. "
                "Ensure it is defined in your ingestion/.env file."
            )

        if not cls.SUPABASE_KEY:
            logger.error("SUPABASE_KEY is missing. Please set it in your .env file.")
            raise ValueError(
                "Missing SUPABASE_KEY environment variable. "
                "Ensure it is defined in your ingestion/.env file."
            )

        parsed_url = urlparse(cls.SUPABASE_URL)
        if not parsed_url.scheme or not parsed_url.netloc:
            logger.error("Invalid SUPABASE_URL format: '%s'", cls.SUPABASE_URL)
            raise ValueError(
                f"Invalid SUPABASE_URL format: '{cls.SUPABASE_URL}'. "
                "Expected format: https://<project-ref>.supabase.co"
            )

        if "your-project" in cls.SUPABASE_URL or "your-supabase" in cls.SUPABASE_KEY:
            logger.warning(
                "Placeholder credentials detected in environment variables. "
                "Please replace them with your actual Supabase project credentials."
            )

        return True

    @classmethod
    def masked_url(cls) -> str:
        """Returns the Supabase URL for safe logging."""
        return cls.SUPABASE_URL

    @classmethod
    def masked_key(cls) -> str:
        """Returns a safely masked version of the Supabase Key."""
        if not cls.SUPABASE_KEY:
            return "<NOT_SET>"
        if len(cls.SUPABASE_KEY) <= 8:
            return "****"
        return f"{cls.SUPABASE_KEY[:4]}...{cls.SUPABASE_KEY[-4:]}"
