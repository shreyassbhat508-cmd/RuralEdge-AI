"""Validators module for the RuralEdge Finance Engine.

Provides deterministic input validation and custom validation exception handling.

validate_finance_input  — Legacy F1/F2 validator. Preserved unchanged.
validate_project_input  — 4-step architecture: validates ProjectInput cost components.
validate_scheme_finance — 4-step architecture: validates SchemeFinance terms.
"""

from typing import List
from finance.models import FinanceInput, ProjectInput, SchemeFinance


class FinanceValidationError(Exception):
    """Exception raised when finance inputs fail business and numerical validation rules."""

    def __init__(self, errors: List[str]) -> None:
        self.errors: List[str] = errors
        message = f"Finance Validation Error(s): {'; '.join(errors)}"
        super().__init__(message)


# ---------------------------------------------------------------------------
# Legacy F1 / F2 validator — DO NOT MODIFY
# ---------------------------------------------------------------------------

def validate_finance_input(input_data: FinanceInput) -> bool:
    """Validates FinanceInput against numerical constraints and financial sanity rules.

    Args:
        input_data (FinanceInput): The input parameters to validate.

    Returns:
        bool: True if input data is valid.

    Raises:
        FinanceValidationError: If one or more validation rules are violated.
    """
    errors: List[str] = []

    # 1. Non-negative checks for all monetary and quantitative inputs
    if input_data.total_project_cost < 0:
        errors.append(f"total_project_cost cannot be negative (got {input_data.total_project_cost}).")

    if input_data.own_contribution < 0:
        errors.append(f"own_contribution cannot be negative (got {input_data.own_contribution}).")

    if input_data.loan_amount < 0:
        errors.append(f"loan_amount cannot be negative (got {input_data.loan_amount}).")

    if input_data.annual_interest_rate < 0:
        errors.append(f"annual_interest_rate cannot be negative (got {input_data.annual_interest_rate}).")

    if input_data.loan_tenure_months < 0:
        errors.append(f"loan_tenure_months cannot be negative (got {input_data.loan_tenure_months}).")

    if input_data.monthly_revenue < 0:
        errors.append(f"monthly_revenue cannot be negative (got {input_data.monthly_revenue}).")

    if input_data.monthly_operating_cost < 0:
        errors.append(f"monthly_operating_cost cannot be negative (got {input_data.monthly_operating_cost}).")

    if input_data.monthly_fixed_cost < 0:
        errors.append(f"monthly_fixed_cost cannot be negative (got {input_data.monthly_fixed_cost}).")

    if input_data.working_capital < 0:
        errors.append(f"working_capital cannot be negative (got {input_data.working_capital}).")

    # 2. Capital funding constraint check
    total_funding = input_data.own_contribution + input_data.loan_amount
    if total_funding > input_data.total_project_cost:
        errors.append(
            f"Capital funding surplus rejected: own_contribution ({input_data.own_contribution}) + "
            f"loan_amount ({input_data.loan_amount}) = {total_funding} exceeds "
            f"total_project_cost ({input_data.total_project_cost})."
        )

    # 3. Loan parameters validity check
    if input_data.loan_amount > 0:
        if input_data.loan_tenure_months <= 0:
            errors.append(
                f"Invalid loan tenure: loan_amount is {input_data.loan_amount}, but "
                f"loan_tenure_months is {input_data.loan_tenure_months} (must be > 0)."
            )

    if errors:
        raise FinanceValidationError(errors)

    return True


# ---------------------------------------------------------------------------
# 4-Step Architecture validators
# ---------------------------------------------------------------------------

def validate_project_input(project_input: ProjectInput) -> bool:
    """Validates ProjectInput for the 4-step assessment pipeline.

    All cost components and operational parameters must be non-negative.
    The engine deliberately does NOT require own_contribution <= project_cost —
    a surplus own contribution is a valid scenario handled by calculate_project_requirement.

    Args:
        project_input: The ProjectInput DTO to validate.

    Returns:
        True if valid.

    Raises:
        FinanceValidationError: If any field violates non-negativity constraints.
    """
    errors: List[str] = []

    non_negative_fields = [
        ("fixed_asset_cost",               project_input.fixed_asset_cost),
        ("setup_cost",                      project_input.setup_cost),
        ("initial_inventory_cost",          project_input.initial_inventory_cost),
        ("initial_working_capital",         project_input.initial_working_capital),
        ("own_contribution",                project_input.own_contribution),
        ("expected_monthly_revenue",        project_input.expected_monthly_revenue),
        ("expected_monthly_operating_cost", project_input.expected_monthly_operating_cost),
        ("expected_monthly_fixed_cost",     project_input.expected_monthly_fixed_cost),
    ]

    for field_name, value in non_negative_fields:
        if value < 0:
            errors.append(f"{field_name} cannot be negative (got {value}).")

    if errors:
        raise FinanceValidationError(errors)

    return True


def validate_scheme_finance(scheme: SchemeFinance) -> bool:
    """Validates SchemeFinance parameters.

    Args:
        scheme: The SchemeFinance DTO to validate.

    Returns:
        True if valid.

    Raises:
        FinanceValidationError: If any scheme parameter violates constraints.
    """
    errors: List[str] = []

    if scheme.maximum_loan_amount < 0:
        errors.append(f"maximum_loan_amount cannot be negative (got {scheme.maximum_loan_amount}).")

    if scheme.interest_rate < 0:
        errors.append(f"interest_rate cannot be negative (got {scheme.interest_rate}).")

    if scheme.tenure_months < 0:
        errors.append(f"tenure_months cannot be negative (got {scheme.tenure_months}).")

    if scheme.moratorium_months < 0:
        errors.append(f"moratorium_months cannot be negative (got {scheme.moratorium_months}).")

    if errors:
        raise FinanceValidationError(errors)

    return True
