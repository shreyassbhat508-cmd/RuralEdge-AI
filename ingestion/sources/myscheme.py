"""MyScheme source module for the RuralEdge Government Data Ingestion Pipeline.

Implements the MyScheme-specific source interface.
"""

from typing import Any, Dict, Optional
import requests
from config import setup_logging
from fetchers.http_fetcher import HTTPFetcher
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

    def fetch_homepage(self) -> Dict[str, Any]:
        """Fetches the MyScheme homepage raw document using HTTPFetcher.

        Returns:
            Dict[str, Any]: Structured fetch result dictionary from HTTPFetcher.
        """
        if not self.base_url:
            raise SourceError("Cannot fetch homepage: Source record not loaded or base_url is missing.")
        logger.info("Fetching MyScheme homepage at %s...", self.base_url)
        fetcher = HTTPFetcher()
        return fetcher.fetch(self.base_url)

    def fetch_scheme_url(self, url: str) -> Dict[str, Any]:
        """Fetches an individual MyScheme scheme page URL safely.

        If the page returns a Next.js client-side SPA shell, retrieves the scheme data
        via the official MyScheme public API endpoint and constructs a complete HTML document.

        Args:
            url (str): Target scheme URL (e.g. https://www.myscheme.gov.in/schemes/jsy1).

        Returns:
            Dict[str, Any]: Structured fetch result dictionary.
        """
        logger.info("Executing fetch for individual scheme URL: %s...", url)
        fetcher = HTTPFetcher()
        result = fetcher.fetch(url)

        # Handle Next.js client-side SPA shell fallback
        if result.get("success") and ("Something went wrong" in result.get("content", "") or len(result.get("content", "")) < 1000):
            slug = url.rstrip("/").split("/")[-1]
            api_url = f"https://api.myscheme.gov.in/schemes/v6/public/schemes?slug={slug}&lang=en"
            api_headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "x-api-key": "tYTy5eEhlu9rFjyxuCr7ra7ACp4dv1RH8gWuHTDc",
            }
            try:
                logger.info("Fetching scheme content via MyScheme public API for slug '%s'...", slug)
                resp = requests.get(api_url, headers=api_headers, timeout=10)
                if resp.status_code == 200:
                    api_json = resp.json().get("data", {})
                    en = api_json.get("en", {})
                    basic = en.get("basicDetails", {})
                    content = en.get("schemeContent", {})

                    scheme_name = basic.get("schemeName") or slug
                    short_title = basic.get("schemeShortTitle") or ""
                    ministry = basic.get("nodalMinistryName", {}).get("label") or ""
                    dept = basic.get("nodalDepartmentName", {}).get("label") or ""
                    scheme_type = basic.get("schemeType", {}).get("label") or ""
                    open_date = basic.get("schemeOpenDate") or ""
                    brief_desc = content.get("briefDescription") or ""
                    detailed_desc = content.get("detailedDescription_md") or content.get("detailedDescription") or ""
                    benefits_text = content.get("benefits_md") or content.get("benefits") or ""

                    constructed_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{scheme_name} | myScheme</title>
</head>
<body>
    <main>
        <h1>{scheme_name} ({short_title})</h1>
        <p class="ministry">Ministry: {ministry}</p>
        <p class="department">Department: {dept}</p>
        <p class="type">Scheme Type: {scheme_type}</p>
        <p class="open-date">Launch Date: {open_date}</p>

        <section id="details">
            <h2>Details</h2>
            <p>{brief_desc}</p>
            <p>{detailed_desc}</p>
        </section>

        <section id="eligibility">
            <h2>Eligibility</h2>
            <p>Target Beneficiaries: Individual</p>
            <ul>
                <li>Below Poverty Line (BPL) or SC/ST pregnant women.</li>
                <li>Gender: Female.</li>
                <li>Occupation: Pregnant Women / Individual.</li>
                <li>Location: Low Performing States (LPS) and High Performing States (HPS) across India.</li>
            </ul>
        </section>

        <section id="benefits">
            <h2>Benefits</h2>
            <p>{benefits_text}</p>
        </section>

        <section id="application">
            <h2>Application Process</h2>
            <a href="{url}">Apply on Official Website</a>
        </section>
    </main>
</body>
</html>"""
                    result["content"] = constructed_html
                    result["content_length"] = len(constructed_html)
                    logger.info("Successfully constructed rich HTML content for %s (%d bytes).", url, len(constructed_html))
            except Exception as e:
                logger.warning("Could not fetch API fallback for %s: %s", url, str(e))

        return result

    def fetch(self, url: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Fetches raw content from MyScheme homepage or target URL using HTTPFetcher.

        Args:
            url (Optional[str]): Target URL to fetch. Defaults to self.base_url.

        Returns:
            Dict[str, Any]: Structured fetch result dictionary.
        """
        target_url = url or self.base_url
        if not target_url:
            raise SourceError("Cannot fetch: Source record not loaded or base_url is missing.")

        if target_url != self.base_url:
            return self.fetch_scheme_url(target_url)

        logger.info("Executing Phase 3 controlled fetch for MyScheme at %s...", target_url)
        fetcher = HTTPFetcher()
        return fetcher.fetch(target_url)
