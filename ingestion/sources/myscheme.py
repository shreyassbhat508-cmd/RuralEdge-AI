"""MyScheme source module for the RuralEdge Government Data Ingestion Pipeline.

Implements the MyScheme-specific source interface.
"""

from typing import Any, Dict
import requests
from config import setup_logging
from sources.base import BaseSource, SourceError

logger = setup_logging("sources.myscheme")


class MySchemeSource(BaseSource):
    """Source handler for the MyScheme government portal (https://www.myscheme.gov.in)."""

    def __init__(self) -> None:
        super().__init__(source_name="MyScheme")

    def check_availability(self, timeout: int = 5) -> Dict[str, Any]:
        """Performs a safe, lightweight availability check against the source URL.

        Args:
            timeout (int): Request timeout in seconds.

        Returns:
            Dict[str, Any]: Reachability status and response metadata.
        """
        if not self.base_url:
            raise SourceError("Cannot check availability: Source record not loaded or base_url is missing.")

        logger.info("Performing lightweight availability check for MyScheme at %s...", self.base_url)
        headers = {
            "User-Agent": "RuralEdge-Ingestion-Pipeline/1.0 (Government Data Indexing)"
        }
        try:
            response = requests.head(self.base_url, headers=headers, timeout=timeout, allow_redirects=True)
            # Fallback to GET if HEAD request is rejected or disallowed
            if response.status_code in (405, 403, 501):
                response = requests.get(self.base_url, headers=headers, timeout=timeout, stream=True)

            is_reachable = response.status_code < 400
            logger.info(
                "MyScheme availability check result: HTTP %d (Reachable: %s)",
                response.status_code,
                is_reachable,
            )
            return {
                "url": self.base_url,
                "status_code": response.status_code,
                "is_reachable": is_reachable,
                "checked_at_status": "OK" if is_reachable else "HTTP_ERROR",
            }
        except requests.RequestException as req_err:
            logger.warning(
                "Availability check warning for MyScheme (%s): %s",
                self.base_url,
                str(req_err),
            )
            return {
                "url": self.base_url,
                "status_code": None,
                "is_reachable": False,
                "error": str(req_err),
                "checked_at_status": "CONNECTION_FAILED",
            }

    def fetch(self, **kwargs: Any) -> Dict[str, Any]:
        """Phase 2 fetch interface: performs source availability and configuration check.

        In Phase 3, this will be expanded to crawl and extract scheme document URLs.
        For Phase 2, no large-scale scraping or crawling is performed.

        Returns:
            Dict[str, Any]: Fetch result dictionary containing source status and check summary.
        """
        logger.info("Executing Phase 2 controlled fetch check for MyScheme...")
        availability = self.check_availability()
        return {
            "source_name": self.source_name,
            "source_id": self.source_id,
            "base_url": self.base_url,
            "organization": self.organization,
            "availability": availability,
            "phase": "phase_2_source_management",
        }
