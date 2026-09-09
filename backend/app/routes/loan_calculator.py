import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from app.schemas.loan_calculator import (
    LoanCalculatorRequest,
    LoanCalculatorResponse,
    SchemeLoanCalculatorRequest,
    SchemeLoanCalculatorResponse,
)
from app.services.loan_calculator_service import calculate_loan, calculate_scheme_loan

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/loan-calculator", tags=["Loan Calculator"])


@router.post("", response_model=LoanCalculatorResponse)
def calculate_loan_endpoint(request: LoanCalculatorRequest):
    """
    POST /api/loan-calculator
    Calculates estimated loan financial structure (margin, loan amount, interest, total repayment, approx EMI).
    """
    try:
        response = calculate_loan(request)
        return response
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as e:
        logger.error(f"Unexpected error in POST /api/loan-calculator: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )


@router.post("/scheme/{scheme_id}", response_model=SchemeLoanCalculatorResponse)
def calculate_scheme_loan_endpoint(scheme_id: UUID, request: SchemeLoanCalculatorRequest):
    """
    POST /api/loan-calculator/scheme/{scheme_id}
    Calculates estimated loan financial structure using scheme benefit data retrieved from Supabase.
    """
    try:
        response = calculate_scheme_loan(str(scheme_id), request)
        return response
    except KeyError as ke:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ke).strip("'\""),
        )
    except ValueError as ve:
        err_msg = str(ve)
        if "No benefit information available" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=err_msg,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg,
        )
    except HTTPException:
        raise
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to fetch scheme or benefit data from database.",
        )
    except Exception as e:
        logger.error(f"Unexpected error in POST /api/loan-calculator/scheme/{scheme_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )
