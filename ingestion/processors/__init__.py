"""Processors package for the RuralEdge Government Data Ingestion Pipeline."""

from processors.html_cleaner import HTMLCleaner, clean_html
from processors.scheme_extractor import (
    SchemeExtractor,
    extract_scheme_from_html,
    SchemeData,
    EligibilityData,
    BenefitData,
    ExtractedSchemeRecord,
)

__all__ = [
    "HTMLCleaner",
    "clean_html",
    "SchemeExtractor",
    "extract_scheme_from_html",
    "SchemeData",
    "EligibilityData",
    "BenefitData",
    "ExtractedSchemeRecord",
]
