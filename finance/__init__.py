"""RuralEdge Finance Engine Package.

Modular, deterministic financial calculation engine for rural business projects.

Legacy (F1/F2) exports
----------------------
FinanceInput, FinanceResult, FinanceValidationError, validate_finance_input,
calculate_financials, calculate_cumulative_cash_flow.

4-Step Architecture exports
----------------------------
Models:
    ProjectInput, SchemeFinance, ProjectRequirement,
    SchemeFinancingResult, FinancialAssessment.

Functions:
    calculate_project_requirement  — Step 1: project cost and loan requirement.
    apply_scheme_financing         — Step 2: scheme loan cap enforcement.
    calculate_financial_assessment — Full 4-step pipeline entry point.

Shared:
    FinanceValidationError         — raised by all validators.
"""

from finance.models import (
    FinanceInput,
    FinanceResult,
    FinancialAssessment,
    MORATORIUM_REPAYMENT_NOTE,
    ProjectInput,
    ProjectRequirement,
    SchemeFinance,
    SchemeFinancingResult,
)
from finance.validators import (
    FinanceValidationError,
    validate_finance_input,
    validate_project_input,
    validate_scheme_finance,
)
from finance.calculator import (
    calculate_financials,
    calculate_cumulative_cash_flow,
    calculate_project_requirement,
    apply_scheme_financing,
    calculate_financial_assessment,
)

__all__ = [
    # Legacy F1/F2
    "FinanceInput",
    "FinanceResult",
    "FinanceValidationError",
    "validate_finance_input",
    "calculate_financials",
    "calculate_cumulative_cash_flow",
    # 4-Step Architecture — Models
    "ProjectInput",
    "SchemeFinance",
    "ProjectRequirement",
    "SchemeFinancingResult",
    "FinancialAssessment",
    "MORATORIUM_REPAYMENT_NOTE",
    # 4-Step Architecture — Validators
    "validate_project_input",
    "validate_scheme_finance",
    # 4-Step Architecture — Functions
    "calculate_project_requirement",
    "apply_scheme_financing",
    "calculate_financial_assessment",
]
