"""Base source abstraction module for the RuralEdge Government Data Ingestion Pipeline.

Defines the core interface and custom exceptions for all government sources.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from config import setup_logging

logger = setup_logging("sources.base")


class SourceError(Exception):
    """Base exception class for source-related errors."""
    pass


class SourceNotFoundError(SourceError):
    """Raised when a government source record is not found in the database."""
    pass


class InactiveSourceError(SourceError):
    """Raised when a government source is marked as inactive."""
    pass


class InvalidSourceConfigError(SourceError):
    """Raised when a government source configuration is missing or invalid."""
    pass


class BaseSource(ABC):
    """Abstract Base Class representing a modular government data source.

    Attributes:
        source_name (str): The unique name of the government source (e.g. 'MyScheme').
        _record (Optional[Dict[str, Any]]): The cached database record from 'government_sources'.
    """

    def __init__(self, source_name: str) -> None:
        if not source_name or not isinstance(source_name, str):
            raise InvalidSourceConfigError("source_name must be a non-empty string.")
        self.source_name: str = source_name.strip()
        self._record: Optional[Dict[str, Any]] = None

    def load_source_record(self, client: Any) -> Dict[str, Any]:
        """Queries the 'government_sources' table in Supabase and caches the source record.

        Args:
            client: Authenticated Supabase client instance.

        Returns:
            Dict[str, Any]: The database record for this government source.

        Raises:
            SourceNotFoundError: If no record exists for self.source_name.
            InactiveSourceError: If the source record exists but is_active is False.
            InvalidSourceConfigError: If the source record is missing critical fields (e.g. base_url).
            SourceError: For unexpected database error during lookup.
        """
        logger.info("Retrieving database record for source '%s'...", self.source_name)
        try:
            response = (
                client.table("government_sources")
                .select("*")
                .eq("name", self.source_name)
                .limit(1)
                .execute()
            )
        except Exception as e:
            logger.error("Supabase query error for source '%s': %s", self.source_name, str(e))
            raise SourceError(f"Failed to query database for source '{self.source_name}': {e}") from e

        if not response.data or len(response.data) == 0:
            logger.error("Source '%s' not found in 'government_sources' table.", self.source_name)
            raise SourceNotFoundError(
                f"Source '{self.source_name}' was not found in 'government_sources' table."
            )

        record = response.data[0]
        self._record = record

        # Validate active state
        if not record.get("is_active", False):
            logger.error("Source '%s' (ID: %s) is marked as inactive.", self.source_name, record.get("id"))
            raise InactiveSourceError(
                f"Source '{self.source_name}' is inactive (is_active=False)."
            )

        # Validate critical configuration
        base_url = record.get("base_url")
        if not base_url or not str(base_url).strip():
            logger.error("Source '%s' (ID: %s) is missing a valid 'base_url'.", self.source_name, record.get("id"))
            raise InvalidSourceConfigError(
                f"Source '{self.source_name}' record is missing a valid 'base_url'."
            )

        logger.info(
            "Successfully loaded active source '%s' (ID: %s, URL: %s)",
            self.source_name,
            record.get("id"),
            record.get("base_url"),
        )
        return record

    @property
    def record(self) -> Optional[Dict[str, Any]]:
        """Returns the cached source record dictionary."""
        return self._record

    @property
    def source_id(self) -> Optional[str]:
        """Returns the UUID of the government source if loaded."""
        return self._record.get("id") if self._record else None

    @property
    def base_url(self) -> Optional[str]:
        """Returns the base URL of the government source if loaded."""
        return self._record.get("base_url") if self._record else None

    @property
    def organization(self) -> Optional[str]:
        """Returns the organization responsible for the source."""
        return self._record.get("organization") if self._record else None

    @property
    def source_type(self) -> Optional[str]:
        """Returns the source type (e.g. portal, api, aggregator)."""
        return self._record.get("source_type") if self._record else None

    @property
    def is_active(self) -> bool:
        """Returns True if source record is loaded and active."""
        return bool(self._record and self._record.get("is_active", False))

    @abstractmethod
    def fetch(self, **kwargs: Any) -> Dict[str, Any]:
        """Abstract interface for fetching source data.

        Subclasses must implement this for source-specific fetching logic.
        For Phase 2, this must be a lightweight controlled test or status check.
        """
        pass
