import { apiClient } from './client'
import {
  LoanCalculatorRequest,
  LoanCalculatorResponse,
  SchemeLoanCalculatorRequest,
  SchemeLoanCalculatorResponse,
} from './types'

export async function calculateLoan(
  request: LoanCalculatorRequest
): Promise<LoanCalculatorResponse> {
  return apiClient<LoanCalculatorResponse>('/api/loan-calculator', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

export async function calculateSchemeLoan(
  schemeId: string,
  request: SchemeLoanCalculatorRequest
): Promise<SchemeLoanLoanCalculatorResponse> {
  return apiClient<SchemeLoanCalculatorResponse>(`/api/loan-calculator/scheme/${schemeId}`, {
    method: 'POST',
    body: JSON.stringify(request),
  })
}
