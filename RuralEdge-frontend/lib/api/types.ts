export interface ApiErrorDetail {
  field?: string
  message: string
  type?: string
}

export interface ApiErrorPayload {
  success: false
  error: {
    code: string
    message: string
    details?: ApiErrorDetail[]
  }
}

export class ApiError extends Error {
  code: string
  status: number
  details?: ApiErrorDetail[]

  constructor(message: string, code = 'API_ERROR', status = 500, details?: ApiErrorDetail[]) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
    this.details = details
  }
}

export interface HealthResponse {
  status: string
  service: string
  database: string
}

export interface SchemeResponse {
  id: string
  source_id?: string | null
  name: string
  short_name?: string | null
  ministry?: string | null
  department?: string | null
  description?: string | null
  scheme_type?: string | null
  official_url?: string | null
  application_url?: string | null
  launch_date?: string | null
  status?: string | null
  target_beneficiaries?: any
  states?: any
  metadata?: Record<string, any> | null
  created_at?: string | null
  updated_at?: string | null
}

export interface PaginatedSchemeResponse {
  items: SchemeResponse[]
  page: number
  limit: number
  total: number
  total_pages: number
}

export interface EligibilityResponse {
  id: string
  scheme_id: string
  min_age?: number | null
  max_age?: number | null
  gender?: string | null
  caste_category?: string | null
  max_income?: number | null
  occupation?: string | null
  education?: string | null
  disability_status?: boolean | null
  land_required?: boolean | null
  business_exists?: boolean | null
  details?: Record<string, any> | null
  created_at?: string | null
}

export interface BenefitResponse {
  id: string
  scheme_id: string
  financial_benefit_amount?: number | null
  subsidy_percentage?: number | null
  interest_rate?: number | null
  repayment_period_months?: number | null
  moratorium_months?: number | null
  maximum_amount?: number | null
  details?: Record<string, any> | null
  created_at?: string | null
}

export interface SchemeDetailsResponse {
  scheme: SchemeResponse
  eligibility: EligibilityResponse[]
  benefits: BenefitResponse[]
  source?: any
}

export interface SchemeFilterParams {
  state?: string
  ministry?: string
  department?: string
  scheme_type?: string
  status?: string
  sort_by?: 'name' | 'launch_date' | 'created_at'
  sort_order?: 'asc' | 'desc'
  page?: number
  limit?: number
}

export interface SchemeSearchParams {
  query?: string
  state?: string
  scheme_type?: string
  status?: string
  ministry?: string
}

export interface RecommendationRequest {
  state?: string
  district?: string
  age?: number
  gender?: string
  occupation?: string
  annual_income?: number
  caste_category?: string
  education?: string
  disability?: boolean
  land_owned?: boolean
  business_exists?: boolean
}

export interface SchemeRecommendation {
  scheme: SchemeResponse
  eligibility: EligibilityResponse[]
  benefits: BenefitResponse[]
  match_reasons: string[]
  match_score: number
  warnings: string[]
}

export interface LoanCalculatorRequest {
  project_cost: number
  margin_percentage: number
  annual_interest_rate: number
  repayment_period_months: number
  moratorium_months: number
}

export interface LoanCalculatorResponse {
  project_cost: number
  margin_percentage: number
  margin_amount: number
  loan_amount: number
  annual_interest_rate: number
  repayment_period_months: number
  moratorium_months: number
  total_interest: number
  total_repayment: number
  approx_monthly_payment: number
  is_estimate: boolean
  calculation_note: string
}

export interface SchemeLoanCalculatorRequest {
  project_cost: number
  margin_percentage?: number
}

export interface SchemeLoanCalculatorResponse {
  scheme_id: string
  scheme_name: string
  project_cost: number
  margin_percentage?: number | null
  margin_amount?: number | null
  subsidy_percentage?: number | null
  subsidy_amount?: number | null
  maximum_amount?: number | null
  interest_rate?: number | null
  loan_amount: number
  repayment_period_months?: number | null
  moratorium_months?: number | null
  total_interest?: number | null
  total_repayment?: number | null
  approx_monthly_payment?: number | null
  warnings: string[]
  is_estimate: boolean
  calculation_note: string
}

export interface LocationResponse {
  id: string
  state?: string | null
  district?: string | null
  taluk?: string | null
  village?: string | null
  pincode?: string | null
  latitude?: number | null
  longitude?: number | null
  metadata?: Record<string, any> | null
  created_at?: string | null
}

export interface LocationQueryParams {
  state?: string
  district?: string
  taluk?: string
  village?: string
  pincode?: string
}

export interface AIChatRequest {
  message: string
  scheme_id?: string
  user_context?: RecommendationRequest
  language?: string
}

export interface AIChatResponse {
  reply: string
  scheme_id?: string | null
  sources: string[]
  disclaimer: string
}

export interface BusinessAnalyzeRequest {
  location: {
    state?: string
    district?: string
    village?: string
  }
  business_category: string
  margin_capital: number
  project_cost: number
}

export interface BusinessAnalyzeResponse {
  business: Record<string, any>
  market: Record<string, any>
  opportunity: Record<string, any>
  finance: Record<string, any>
  scheme: Record<string, any>
  swot: Record<string, any>
}
