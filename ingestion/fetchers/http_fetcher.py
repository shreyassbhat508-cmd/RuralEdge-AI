"""HTTP Fetcher module for the RuralEdge Government Data Ingestion Pipeline.

Provides controlled, safe HTTP fetching for government source content.
Includes timeout handling, User-Agent identification, content-size safety limits,
and structured error reporting.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
import requests
from config import Config, setup_logging

logger = setup_logging("fetchers.http")


class FetcherError(Exception):
    """Base exception for HTTP Fetcher errors."""
    pass


class ResponseSizeExceededError(FetcherError):
    """Raised when response content size exceeds configured limit."""
    pass


class HTTPFetcher:
    """Reusable HTTP fetcher for retrieving raw government portal content safely."""

    def __init__(
        self,
        timeout: Optional[int] = None,
        user_agent: Optional[str] = None,
        max_response_size: Optional[int] = None,
    ) -> None:
        """Initializes the HTTP Fetcher.

        Args:
            timeout (Optional[int]): Request timeout in seconds. Defaults to Config.DEFAULT_REQUEST_TIMEOUT.
            user_agent (Optional[str]): HTTP User-Agent header string. Defaults to Config.USER_AGENT.
            max_response_size (Optional[int]): Maximum allowed response size in bytes. Defaults to Config.MAX_RESPONSE_SIZE.
        """
        self.timeout: int = timeout if timeout is not None else Config.DEFAULT_REQUEST_TIMEOUT
        self.user_agent: str = user_agent if user_agent is not None else Config.USER_AGENT
        self.max_response_size: int = (
            max_response_size if max_response_size is not None else Config.MAX_RESPONSE_SIZE
        )

    def fetch(self, url: str) -> Dict[str, Any]:
        """Fetches the raw content from the given URL with size limits and error handling.

        Args:
            url (str): The target URL to fetch.

        Returns:
            Dict[str, Any]: Structured fetch result containing:
                - url (str): Target URL
                - status_code (Optional[int]): HTTP response status code
                - content_type (str): MIME type / content type header
                - content (str): Raw fetched content as string
                - fetched_at (str): ISO timestamp (UTC) of when fetch completed
                - content_length (int): Byte length of fetched content
                - success (bool): True if fetch succeeded and passed limits
                - error (Optional[str]): Error message if fetch failed
        """
        fetched_at = datetime.now(timezone.utc).isoformat()
        logger.info("Initiating HTTP GET request to %s...", url)

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        try:
            # Send HTTP GET request with streaming enabled to monitor response size
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
                stream=True,
                allow_redirects=True,
            )

            status_code = response.status_code
            content_type = response.headers.get("Content-Type", "").strip()

            # Handle non-2xx HTTP status codes
            if status_code >= 400:
                logger.error("HTTP error response %d received from %s", status_code, url)
                return {
                    "url": url,
                    "status_code": status_code,
                    "content_type": content_type,
                    "content": "",
                    "fetched_at": fetched_at,
                    "content_length": 0,
                    "success": False,
                    "error": f"HTTP Error {status_code}",
                }

            # Check Content-Length header if present
            content_length_header = response.headers.get("Content-Length")
            if content_length_header and content_length_header.isdigit():
                expected_size = int(content_length_header)
                if expected_size > self.max_response_size:
                    response.close()
                    logger.error(
                        "Content-Length %d bytes exceeds configured limit of %d bytes for %s",
                        expected_size,
                        self.max_response_size,
                        url,
                    )
                    return {
                        "url": url,
                        "status_code": status_code,
                        "content_type": content_type,
                        "content": "",
                        "fetched_at": fetched_at,
                        "content_length": 0,
                        "success": False,
                        "error": (
                            f"Response size ({expected_size} bytes) exceeds limit "
                            f"of {self.max_response_size} bytes."
                        ),
                    }

            # Read response content in chunks to enforce size limit
            content_chunks = []
            downloaded_bytes = 0

            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    downloaded_bytes += len(chunk)
                    if downloaded_bytes > self.max_response_size:
                        response.close()
                        logger.error(
                            "Downloaded size (%d bytes) exceeded maximum limit of %d bytes for %s",
                            downloaded_bytes,
                            self.max_response_size,
                            url,
                        )
                        return {
                            "url": url,
                            "status_code": status_code,
                            "content_type": content_type,
                            "content": "",
                            "fetched_at": fetched_at,
                            "content_length": downloaded_bytes,
                            "success": False,
                            "error": (
                                f"Response exceeded maximum limit of {self.max_response_size} bytes."
                            ),
                        }
                    content_chunks.append(chunk)

            raw_bytes = b"".join(content_chunks)

            # Detect encoding or fallback to utf-8
            encoding = response.encoding or "utf-8"
            try:
                raw_text = raw_bytes.decode(encoding, errors="replace")
            except (UnicodeDecodeError, LookupError):
                raw_text = raw_bytes.decode("utf-8", errors="replace")

            if not raw_text.strip():
                logger.warning("Empty response content received from %s", url)
                return {
                    "url": url,
                    "status_code": status_code,
                    "content_type": content_type,
                    "content": "",
                    "fetched_at": fetched_at,
                    "content_length": 0,
                    "success": False,
                    "error": "Empty response content received.",
                }

            logger.info(
                "Successfully fetched %s (HTTP %d, %d bytes, Type: %s)",
                url,
                status_code,
                len(raw_bytes),
                content_type or "unknown",
            )

            return {
                "url": url,
                "status_code": status_code,
                "content_type": content_type,
                "content": raw_text,
                "fetched_at": fetched_at,
                "content_length": len(raw_bytes),
                "success": True,
                "error": None,
            }

        except requests.exceptions.Timeout as t_err:
            logger.error("Timeout error while fetching %s: %s", url, str(t_err))
            return {
                "url": url,
                "status_code": None,
                "content_type": "",
                "content": "",
                "fetched_at": fetched_at,
                "content_length": 0,
                "success": False,
                "error": f"Connection timed out: {t_err}",
            }

        except requests.exceptions.ConnectionError as c_err:
            logger.error("Connection error while fetching %s: %s", url, str(c_err))
            return {
                "url": url,
                "status_code": None,
                "content_type": "",
                "content": "",
                "fetched_at": fetched_at,
                "content_length": 0,
                "success": False,
                "error": f"Connection failed: {c_err}",
            }

        except requests.exceptions.RequestException as req_err:
            logger.error("HTTP request error while fetching %s: %s", url, str(req_err))
            return {
                "url": url,
                "status_code": getattr(req_err.response, "status_code", None),
                "content_type": "",
                "content": "",
                "fetched_at": fetched_at,
                "content_length": 0,
                "success": False,
                "error": f"Request exception: {req_err}",
            }

        except Exception as e:
            logger.error("Unexpected error while fetching %s: %s", url, str(e))
            return {
                "url": url,
                "status_code": None,
                "content_type": "",
                "content": "",
                "fetched_at": fetched_at,
                "content_length": 0,
                "success": False,
                "error": f"Unexpected fetch error: {e}",
            }
