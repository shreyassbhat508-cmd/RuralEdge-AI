"""Scheme Extractor module for the RuralEdge Government Data Ingestion Pipeline.

Provides deterministic Python parsing using BeautifulSoup and pattern matching
to extract structured scheme, eligibility, and benefit records from raw or cleaned HTML scheme documents.
Strictly avoids fabrication: unextracted or absent fields evaluate to None.
"""

import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from config import setup_logging
from processors.html_cleaner import HTMLCleaner

logger = setup_logging("processors.scheme_extractor")


@dataclass
class SchemeData:
    """Structured representation of a government scheme matching database columns."""
    name: str
    short_name: Optional[str] = None
    ministry: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None
    scheme_type: Optional[str] = None
    official_url: Optional[str] = None
    application_url: Optional[str] = None
    launch_date: Optional[str] = None
    status: Optional[str] = "active"
    target_beneficiaries: Optional[List[str]] = None
    states: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converts SchemeData to a dictionary suitable for database insertion."""
        d = asdict(self)
        return d


@dataclass
class EligibilityData:
    """Structured representation of scheme eligibility criteria matching database columns."""
    category: Optional[str] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    income_min: Optional[float] = None
    income_max: Optional[float] = None
    education: Optional[str] = None
    location_requirement: Optional[str] = None
    caste_category: Optional[str] = None
    disability_required: Optional[bool] = None
    land_required: Optional[bool] = None
    business_required: Optional[bool] = None
    other_conditions: Optional[str] = None
    eligibility_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converts EligibilityData to a dictionary suitable for database insertion."""
        return asdict(self)


@dataclass
class BenefitData:
    """Structured representation of scheme benefits matching database columns."""
    benefit_type: Optional[str] = None
    amount: Optional[float] = None
    interest_rate: Optional[float] = None
    subsidy_percentage: Optional[float] = None
    maximum_amount: Optional[float] = None
    repayment_period_months: Optional[int] = None
    moratorium_months: Optional[int] = None
    description: Optional[str] = None
    benefit_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converts BenefitData to a dictionary suitable for database insertion."""
        return asdict(self)


@dataclass
class ExtractedSchemeRecord:
    """Complete extracted record container."""
    scheme: SchemeData
    eligibility: EligibilityData
    benefits: BenefitData

    def to_dict(self) -> Dict[str, Any]:
        """Converts ExtractedSchemeRecord to dictionary format."""
        return {
            "scheme": self.scheme.to_dict(),
            "eligibility": self.eligibility.to_dict(),
            "benefits": self.benefits.to_dict(),
        }


class SchemeExtractor:
    """Deterministic parser for extracting structured government scheme data from HTML documents."""

    def __init__(self, raw_html: str, document_url: Optional[str] = None) -> None:
        """Initializes the extractor with raw HTML and document URL context.

        Args:
            raw_html (str): The raw HTML content of the scheme page.
            document_url (Optional[str]): Source document URL.
        """
        self.raw_html: str = raw_html or ""
        self.document_url: Optional[str] = document_url
        self.cleaner = HTMLCleaner(self.raw_html)
        self.clean_text: str = self.cleaner.clean()
        self.soup: BeautifulSoup = self.cleaner.parse_soup()

    def extract_scheme(self) -> ExtractedSchemeRecord:
        """Executes deterministic parsing and returns structured scheme record.

        Returns:
            ExtractedSchemeRecord: The extracted scheme, eligibility, and benefit details.
        """
        logger.info("Extracting scheme details from HTML document...")

        scheme_data = self._extract_scheme_data()
        eligibility_data = self._extract_eligibility_data()
        benefit_data = self._extract_benefit_data()

        return ExtractedSchemeRecord(
            scheme=scheme_data,
            eligibility=eligibility_data,
            benefits=benefit_data,
        )

    def _extract_scheme_data(self) -> SchemeData:
        """Extracts primary scheme metadata."""
        # Extract scheme name from h1 tag or title tag or .scheme-title element
        name = None

        h1 = self.soup.find("h1")
        if h1 and h1.get_text().strip():
            name = h1.get_text().strip()

        if not name:
            title_elem = self.soup.find("title")
            if title_elem and title_elem.get_text().strip():
                # Title often contains extra branding like "PM Kisan | myScheme"
                raw_title = title_elem.get_text().strip()
                name = raw_title.split("|")[0].split("-")[0].strip()

        if not name:
            # Look for elements with class containing 'scheme-title' or 'heading'
            scheme_title_elem = self.soup.select_one(".scheme-name, .scheme-title, #scheme-title")
            if scheme_title_elem:
                name = scheme_title_elem.get_text().strip()

        if not name:
            name = "Unnamed Scheme"

        # Short name extraction (e.g. PM-KISAN in parentheses or short name field)
        short_name = None
        short_match = re.search(r"\(([^)]+)\)", name)
        if short_match:
            candidate = short_match.group(1).strip()
            if len(candidate) <= 20 and candidate.isupper():
                short_name = candidate

        # Ministry extraction
        ministry = None
        ministry_elem = self.soup.find(text=re.compile(r"Ministry", re.IGNORECASE))
        if ministry_elem:
            parent = ministry_elem.parent
            if parent:
                parent_text = parent.get_text().strip()
                m_match = re.search(r"Ministry\s+of\s+[A-Za-z\s,&]+", parent_text, re.IGNORECASE)
                if m_match:
                    ministry = m_match.group(0).strip()

        # Department extraction
        department = None
        dept_elem = self.soup.find(text=re.compile(r"Department", re.IGNORECASE))
        if dept_elem:
            parent = dept_elem.parent
            if parent:
                parent_text = parent.get_text().strip()
                d_match = re.search(r"Department\s+of\s+[A-Za-z\s,&]+", parent_text, re.IGNORECASE)
                if d_match:
                    department = d_match.group(0).strip()

        # Description extraction
        description = None
        desc_heading = self.soup.find(["h2", "h3", "h4"], text=re.compile(r"Details|Overview|Description|About", re.IGNORECASE))
        if desc_heading:
            next_p = desc_heading.find_next_sibling(["p", "div"])
            if next_p:
                description = next_p.get_text().strip()

        if not description:
            # Fallback to first major paragraph
            first_p = self.soup.find("p")
            if first_p and len(first_p.get_text().strip()) > 30:
                description = first_p.get_text().strip()

        # Scheme type extraction
        scheme_type = None
        if re.search(r"Central\s+Sector|Centrally\s+Sponsored", self.clean_text, re.IGNORECASE):
            scheme_type = "Central"
        elif re.search(r"State\s+Scheme", self.clean_text, re.IGNORECASE):
            scheme_type = "State"

        # Official and application URLs
        official_url = self.document_url
        application_url = None
        apply_link = self.soup.find("a", text=re.compile(r"Apply|Official\s+Website|Portal", re.IGNORECASE))
        if apply_link and apply_link.get("href"):
            href = apply_link.get("href").strip()
            if href.startswith("http"):
                application_url = href

        # Target beneficiaries extraction
        target_beneficiaries = None
        beneficiary_matches = re.findall(
            r"(Farmers|Women|Students|Youth|Senior Citizens|Artisans|Workers|Entrepreneurs)",
            self.clean_text,
            re.IGNORECASE,
        )
        if beneficiary_matches:
            target_beneficiaries = list(set([b.capitalize() for b in beneficiary_matches]))

        # States extraction
        states = None
        state_match = re.search(r"State:\s*([A-Za-z\s,]+)", self.clean_text, re.IGNORECASE)
        if state_match:
            raw_states = state_match.group(1).strip().split(",")
            states = [s.strip() for s in raw_states if s.strip()]

        # Launch date extraction (must be valid YYYY-MM-DD for DB DATE column)
        launch_date = None
        date_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", self.clean_text)
        if date_match:
            candidate_date = date_match.group(1).strip()
            # Verify ISO date formatting
            try:
                datetime.strptime(candidate_date, "%Y-%m-%d")
                launch_date = candidate_date
            except ValueError:
                launch_date = None

        metadata = {
            "extraction_method": "deterministic_bs4",
            "source_document_url": self.document_url,
            "raw_text_length": len(self.clean_text),
        }

        return SchemeData(
            name=name,
            short_name=short_name,
            ministry=ministry,
            department=department,
            description=description,
            scheme_type=scheme_type,
            official_url=official_url,
            application_url=application_url,
            launch_date=launch_date,
            status="active",
            target_beneficiaries=target_beneficiaries,
            states=states,
            metadata=metadata,
        )

    def _extract_eligibility_data(self) -> EligibilityData:
        """Extracts eligibility rules from document text."""
        min_age = None
        max_age = None
        gender = None
        occupation = None
        income_max = None
        land_required = None

        # Age extraction patterns (e.g., "18 to 40 years", "Age: 18-60", "Minimum age 21")
        age_range_match = re.search(r"(\d{1,2})\s*(?:to|-|–)\s*(\d{1,2})\s*years", self.clean_text, re.IGNORECASE)
        if age_range_match:
            min_age = int(age_range_match.group(1))
            max_age = int(age_range_match.group(2))
        else:
            min_age_match = re.search(r"min(?:imum)?\s*age\s*(?:is|:)?\s*(\d{1,2})", self.clean_text, re.IGNORECASE)
            if min_age_match:
                min_age = int(min_age_match.group(1))
            max_age_match = re.search(r"max(?:imum)?\s*age\s*(?:is|:)?\s*(\d{1,2})", self.clean_text, re.IGNORECASE)
            if max_age_match:
                max_age = int(max_age_match.group(1))

        # Gender extraction
        if re.search(r"female|women|pregnant\s+women|mother|woman", self.clean_text, re.IGNORECASE):
            gender = "Female"
        elif re.search(r"male\s+only", self.clean_text, re.IGNORECASE):
            gender = "Male"
        elif re.search(r"all\s+genders|male\s+and\s+female", self.clean_text, re.IGNORECASE):
            gender = "All"

        # Occupation extraction
        occ_match = re.search(r"(Farmer|Student|Artisan|Weaver|Worker|Small\s+Merchant|Vendor|Pregnant\s+Women|Individual)", self.clean_text, re.IGNORECASE)
        if occ_match:
            occupation = occ_match.group(1).title()

        # Income max extraction (e.g. "income below Rs. 2,50,000", "income less than 2.5 lakh")
        inc_match = re.search(r"income\s+(?:less\s+than|below|under|up\s+to|max(?:imum)?)\s*(?:Rs\.?|INR|₹)?\s*([\d,]+)", self.clean_text, re.IGNORECASE)
        if inc_match:
            raw_inc = inc_match.group(1).replace(",", "")
            if raw_inc.isdigit():
                income_max = float(raw_inc)

        # Land requirement
        if re.search(r"landholding|cultivable\s+land|land\s+owner", self.clean_text, re.IGNORECASE):
            land_required = True

        # Extract list of conditions under Eligibility section
        other_conditions_list = []
        eligibility_heading = self.soup.find(["h2", "h3", "h4"], text=re.compile(r"Eligibility", re.IGNORECASE))
        if eligibility_heading:
            section = eligibility_heading.find_next_sibling(["ul", "ol", "div"])
            if section:
                lis = section.find_all("li")
                if lis:
                    other_conditions_list = [li.get_text().strip() for li in lis if li.get_text().strip()]

        other_conditions = "\n".join(other_conditions_list) if other_conditions_list else None

        eligibility_extra = {}
        if other_conditions_list:
            eligibility_extra["extracted_criteria_list"] = other_conditions_list

        return EligibilityData(
            category=None,
            min_age=min_age,
            max_age=max_age,
            gender=gender,
            occupation=occupation,
            income_min=None,
            income_max=income_max,
            education=None,
            location_requirement=None,
            caste_category=None,
            disability_required=None,
            land_required=land_required,
            business_required=None,
            other_conditions=other_conditions,
            eligibility_data=eligibility_extra,
        )

    def _extract_benefit_data(self) -> BenefitData:
        """Extracts benefit rules and financial amounts from document text."""
        benefit_type = None
        amount = None
        interest_rate = None
        subsidy_percentage = None
        maximum_amount = None
        description = None

        # Benefit type
        if re.search(r"Direct\s+Benefit\s+Transfer|DBT|Cash\s+Transfer|Cash\s+Assistance", self.clean_text, re.IGNORECASE):
            benefit_type = "Direct Benefit Transfer (DBT)"
        elif re.search(r"Subsidy", self.clean_text, re.IGNORECASE):
            benefit_type = "Subsidy"
        elif re.search(r"Loan|Credit", self.clean_text, re.IGNORECASE):
            benefit_type = "Loan / Credit"

        # Financial amount extraction (e.g. "₹1,400", "Rs. 6000", "Rs. 6,000 per year", "Rs 6000/-")
        amt_match = re.search(r"(?:Rs\.?|INR|₹)\s*([\d,]+)(?:\s*(?:per|/\-|year|annum))?", self.clean_text, re.IGNORECASE)
        if amt_match:
            raw_amt = amt_match.group(1).replace(",", "")
            if raw_amt.isdigit():
                amount = float(raw_amt)

        # Subsidy percentage (e.g. "50% subsidy", "subsidy of 60%")
        sub_match = re.search(r"(\d{1,2}(?:\.\d+)?)\s*%\s*subsidy|subsidy\s+of\s+(\d{1,2}(?:\.\d+)?)\s*%", self.clean_text, re.IGNORECASE)
        if sub_match:
            raw_sub = sub_match.group(1) or sub_match.group(2)
            if raw_sub:
                subsidy_percentage = float(raw_sub)

        # Interest rate (e.g. "interest rate of 4%", "4% per annum")
        int_match = re.search(r"(\d{1,2}(?:\.\d+)?)\s*%\s*(?:interest|p\.a\.|per\s+annum)", self.clean_text, re.IGNORECASE)
        if int_match:
            interest_rate = float(int_match.group(1))

        # Extract benefit section text
        benefit_heading = self.soup.find(["h2", "h3", "h4"], text=re.compile(r"Benefits|Financial\s+Assistance", re.IGNORECASE))
        if benefit_heading:
            next_sec = benefit_heading.find_next_sibling(["p", "ul", "ol", "div"])
            if next_sec:
                description = next_sec.get_text().strip()

        benefit_extra = {}
        if description:
            benefit_extra["extracted_benefit_text"] = description

        return BenefitData(
            benefit_type=benefit_type,
            amount=amount,
            interest_rate=interest_rate,
            subsidy_percentage=subsidy_percentage,
            maximum_amount=maximum_amount,
            repayment_period_months=None,
            moratorium_months=None,
            description=description,
            benefit_data=benefit_extra,
        )


def extract_scheme_from_html(raw_html: str, document_url: Optional[str] = None) -> ExtractedSchemeRecord:
    """Convenience function for extracting structured scheme records from HTML.

    Args:
        raw_html (str): Raw HTML content.
        document_url (Optional[str]): Document URL.

    Returns:
        ExtractedSchemeRecord: Extracted data container.
    """
    extractor = SchemeExtractor(raw_html=raw_html, document_url=document_url)
    return extractor.extract_scheme()
