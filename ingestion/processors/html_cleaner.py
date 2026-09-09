"""HTML Cleaner module for the RuralEdge Government Data Ingestion Pipeline.

Strips non-content HTML tags (scripts, styles, nav, headers, footers),
normalizes whitespace, preserves meaningful structural breaks, and produces clean text for extraction.
"""

import re
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from config import setup_logging

logger = setup_logging("processors.html_cleaner")


class HTMLCleaner:
    """Cleans raw HTML government document content into structured clean text using BeautifulSoup."""

    # Tags to completely remove along with their content
    TAGS_TO_REMOVE = [
        "script",
        "style",
        "nav",
        "header",
        "footer",
        "iframe",
        "noscript",
        "svg",
        "form",
        "button",
        "aside",
    ]

    # Block level tags that represent structural text breaks
    BLOCK_TAGS = [
        "p", "h1", "h2", "h3", "h4", "h5", "h6",
        "li", "tr", "div", "section", "article", "blockquote", "dt", "dd"
    ]

    def __init__(self, raw_html: str) -> None:
        """Initializes the cleaner with raw HTML string.

        Args:
            raw_html (str): The unparsed HTML content.
        """
        self.raw_html: str = raw_html or ""

    def clean(self) -> str:
        """Cleans the raw HTML and returns normalized text content.

        Returns:
            str: Cleaned, whitespace-normalized plain text representation of the HTML document.
        """
        if not self.raw_html.strip():
            return ""

        soup = BeautifulSoup(self.raw_html, "html.parser")

        # Decompose non-content tags
        for tag in soup(self.TAGS_TO_REMOVE):
            tag.decompose()

        # Add newline placeholders around block tags to preserve text boundaries
        for tag_name in self.BLOCK_TAGS:
            for tag in soup.find_all(tag_name):
                tag.insert_before("\n")
                tag.insert_after("\n")

        # Extract text
        raw_text = soup.get_text(separator=" ")

        # Normalize whitespace (multiple spaces/tabs to single space, clean empty lines)
        lines = [line.strip() for line in raw_text.splitlines()]
        # Remove consecutive empty lines
        cleaned_lines = []
        prev_empty = False
        for line in lines:
            # Replace multiple internal spaces/tabs with single space
            line = re.sub(r"[ \t]+", " ", line)
            if line:
                cleaned_lines.append(line)
                prev_empty = False
            elif not prev_empty:
                cleaned_lines.append("")
                prev_empty = True

        cleaned_text = "\n".join(cleaned_lines).strip()
        logger.info(
            "HTML cleaned: reduced from %d raw bytes to %d clean characters.",
            len(self.raw_html),
            len(cleaned_text),
        )
        return cleaned_text

    def parse_soup(self) -> BeautifulSoup:
        """Returns a cleaned BeautifulSoup tree with scripts and navigation elements removed.

        Returns:
            BeautifulSoup: Cleaned DOM tree.
        """
        soup = BeautifulSoup(self.raw_html, "html.parser")
        for tag in soup(self.TAGS_TO_REMOVE):
            tag.decompose()
        return soup


def clean_html(raw_html: str) -> str:
    """Convenience function to clean raw HTML into plain text.

    Args:
        raw_html (str): Raw HTML string.

    Returns:
        str: Clean text representation.
    """
    cleaner = HTMLCleaner(raw_html)
    return cleaner.clean()
