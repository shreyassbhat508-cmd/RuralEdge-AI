"""Scheme Validator module for the RuralEdge Government Data Ingestion Pipeline.

Validates extracted scheme, eligibility, and benefit records against business rules,
type constraints, and range bounds prior to database insertion.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import urlparse
from config import setup_logging
from processors.scheme_extractor import ExtractedSchemeRecord, SchemeData, EligibilityData, BenefitData

logger = setup_logging("validators.scheme")


@dataclass
class ValidationResult:
    """Container for validation outcomes."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """Adds an error message and marks result invalid."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Adds a non-fatal warning message."""
        self.warnings.append(message)


class SchemeValidator:
    """Validates extracted scheme, eligibility, and benefit records."""

    VALID_STATUSES = {"active", "inactive", "launched", "closed", "draft", "expired"}

    def validate(
        self,
        record: ExtractedSchemeRecord,
        source_id: Optional[str] = None,
    ) -> ValidationResult:
        """Validates the extracted scheme record.

        Args:
            record (ExtractedSchemeRecord): Extracted record containing scheme, eligibility, and benefits.
            source_id (Optional[str]): Source ID UUID if available.

        Returns:
            ValidationResult: Result object containing validity status, errors, and warnings.
        """
        result = ValidationResult(is_valid=True)

        if source_id:
            self._validate_source_id(source_id, result)

        self._validate_scheme(record.scheme, result)
        self._validate_eligibility(record.eligibility, result)
        self._validate_benefits(record.benefits, result)

        if result.is_valid:
            logger.info("Validation PASSED for scheme '%s'. Warnings: %d", record.scheme.name, len(result.warnings))
        else:
            logger.warning(
                "Validation FAILED for scheme '%s' with %d errors.",
                record.scheme.name,
                len(result.errors),
            )

        return result

    def _validate_source_id(self, source_id: str, result: ValidationResult) -> None:
        """Validates source_id presence and format."""
        if not source_id or not isinstance(source_id, str) or not source_id.strip():
            result.add_error("source_id is required and must be a non-empty string.")

    def _validate_scheme(self, scheme: SchemeData, result: ValidationResult) -> None:
        """Validates primary scheme fields."""
        # 1. Scheme name exists and non-empty
        if not scheme.name or not scheme.name.strip():
            result.add_error("Scheme name is required and cannot be empty.")
        elif scheme.name.strip() == "Unnamed Scheme":
            result.add_warning("Scheme name was defaulting to 'Unnamed Scheme'.")

        # 2. URL format validation
        if scheme.official_url:
            if not self._is_valid_url(scheme.official_url):
                result.add_error(f"Invalid official_url format: '{scheme.official_url}'")

        if scheme.application_url:
            if not self._is_valid_url(scheme.application_url):
                result.add_error(f"Invalid application_url format: '{scheme.application_url}'")

        # 3. Status validation
        if scheme.status and scheme.status.lower() not in self.VALID_STATUSES:
            result.add_warning(f"Unrecognized scheme status: '{scheme.status}'")

    def _validate_eligibility(self, eligibility: EligibilityData, result: ValidationResult) -> None:
        """Validates eligibility criteria numerical and logical rules."""
        # 1. min_age <= max_age
        if eligibility.min_age is not None:
            if eligibility.min_age < 0 or eligibility.min_age > 120:
                result.add_error(f"Invalid min_age: {eligibility.min_age}. Must be between 0 and 120.")

        if eligibility.max_age is not None:
            if eligibility.max_age < 0 or eligibility.max_age > 120:
                result.add_error(f"Invalid max_age: {eligibility.max_age}. Must be between 0 and 120.")

        if eligibility.min_age is not None and eligibility.max_age is not None:
            if eligibility.min_age > eligibility.max_age:
                result.add_error(
                    f"Invalid age range: min_age ({eligibility.min_age}) > max_age ({eligibility.max_age})."
                )

        # 2. income_min <= income_max
        if eligibility.income_min is not None and eligibility.income_min < 0:
            result.add_error(f"income_min cannot be negative: {eligibility.income_min}")

        if eligibility.income_max is not None and eligibility.income_max < 0:
            result.add_error(f"income_max cannot be negative: {eligibility.income_max}")

        if eligibility.income_min is not None and eligibility.income_max is not None:
            if eligibility.income_min > eligibility.income_max:
                result.add_error(
                    f"Invalid income range: income_min ({eligibility.income_min}) > income_max ({eligibility.income_max})."
                )

    def _validate_benefits(self, benefits: BenefitData, result: ValidationResult) -> None:
        """Validates benefit financial fields."""
        if benefits.amount is not None and benefits.amount < 0:
            result.add_error(f"Benefit amount cannot be negative: {benefits.amount}")

        if benefits.maximum_amount is not None and benefits.maximum_amount < 0:
            result.add_error(f"Benefit maximum_amount cannot be negative: {benefits.maximum_amount}")

        if benefits.subsidy_percentage is not None:
            if benefits.subsidy_percentage < 0 or benefits.subsidy_percentage > 100:
                result.add_error(
                    f"Invalid subsidy_percentage: {benefits.subsidy_percentage}. Must be between 0 and 100."
                )

        if benefits.interest_rate is not None:
            if benefits.interest_rate < 0 or benefits.interest_rate > 100:
                result.add_error(
                    f"Invalid interest_rate: {benefits.interest_rate}. Must be between 0 and 100."
                )

        if benefits.repayment_period_months is not None and benefits.repayment_period_months < 0:
            result.add_error(f"repayment_period_months cannot be negative: {benefits.repayment_period_months}")

        if benefits.moratorium_months is not None and benefits.moratorium_months < 0:
            result.add_error(f"moratorium_months cannot be negative: {benefits.moratorium_months}")

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Checks if a URL string is valid and well-formed."""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme in ("http", "https") and parsed.netloc)
        except Exception:
            return False


def validate_scheme_record(
    record: ExtractedSchemeRecord,
    source_id: Optional[str] = None,
) -> ValidationResult:
    """Convenience function to validate an extracted scheme record.

    Args:
        record (ExtractedSchemeRecord): Extracted record.
        source_id (Optional[str]): Government source UUID.

    Returns:
        ValidationResult: Validation outcome.
    """
    validator = SchemeValidator()
    return validator.validate(record=record, source_id=source_id)
