/**
 * RuralEdge API Client
 * Typed functions for communicating with the FastAPI backend.
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ---------------------------------------------------------------------------
// TypeScript Interfaces matching FastAPI Schemas
// ---------------------------------------------------------------------------

export interface LocationInput {
  state: string;
  district: string;
  village?: string | null;
}

export interface BusinessAnalyzeRequest {
  location: LocationInput;
  business_category: string;
  margin_capital: number;
  project_cost: number;
}

export interface CompetitorDetail {
  name: string;
  category?: string | null;
  address?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  distance_km?: number | null;
  rating?: number | null;
  user_ratings_total?: number | null;
  source?: string;
}

export interface MarketInfo {
  status: 'success' | 'unavailable' | string;
  source: string;
  radius_km: number;
  competitor_count: number | null;
  competitors: CompetitorDetail[];
  market_reach_score: number | null;
  competition_score: number | null;
  message?: string | null;
}

export interface OpportunityComponents {
  market: number;
  competition: number;
  financial: number;
  location: number;
  affordability: number;
}

export interface OpportunityInfo {
  score: number;
  level: string;
  components: OpportunityComponents;
  reasons: string[];
}

export interface FinanceInfo {
  project_cost: number;
  own_contribution: number;
  loan_amount: number;
  monthly_revenue: number;
  monthly_operating_cost: number;
  monthly_profit: number;
  profit_margin: number;
  emi: number;
  total_interest: number;
  break_even?: number | null;
  payback_months?: number | null;
  is_estimate: boolean;
  calculation_note: string;
}

export interface SchemeInfo {
  status: 'matched' | 'no_match' | 'pending' | 'error' | string;
  recommended_scheme: string | null;
  match_score: number;
  reasons: string[];
}

export interface SwotAnalysis {
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
}

export interface BusinessInfo {
  category: string;
  location: {
    state: string;
    district: string;
    village?: string | null;
  };
}

export interface BusinessAnalyzeResponse {
  business: BusinessInfo;
  market: MarketInfo;
  opportunity: OpportunityInfo;
  finance: FinanceInfo;
  scheme: SchemeInfo;
  swot: SwotAnalysis;
}

export interface HealthResponse {
  status: 'ok' | 'degraded';
  service: string;
  database: 'connected' | 'unavailable';
}

export interface SchemeResponse {
  id: string;
  name: string;
  short_name?: string | null;
  description?: string | null;
  ministry?: string | null;
  department?: string | null;
  scheme_type?: string | null;
  state?: string | null;
  status?: string | null;
  target_beneficiaries?: string[] | null;
  funding_pattern?: string | null;
  launch_date?: string | null;
  nodal_agency?: string | null;
  application_process?: string | null;
  website_url?: string | null;
  helpline?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface PaginatedSchemeResponse {
  items: SchemeResponse[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface SchemeEligibilityRecord {
  id: string;
  scheme_id: string;
  criteria_name: string;
  criteria_value: string;
  is_mandatory?: boolean;
}

export interface SchemeBenefitRecord {
  id: string;
  scheme_id: string;
  benefit_type: string;
  description: string;
  subsidy_percentage?: number | null;
  max_amount?: number | null;
}

export interface SchemeDetailsResponse {
  scheme: SchemeResponse;
  eligibility: SchemeEligibilityRecord[];
  benefits: SchemeBenefitRecord[];
  source?: {
    id: string;
    title: string;
    url?: string | null;
  } | null;
}

export interface SchemeQueryParams {
  state?: string;
  ministry?: string;
  department?: string;
  scheme_type?: string;
  status?: string;
  sort_by?: 'name' | 'launch_date' | 'created_at';
  sort_order?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}

export interface RecommendationRequest {
  state?: string | null;
  district?: string | null;
  gender?: string | null;
  caste_category?: string | null;
  occupation?: string | null;
  annual_income?: number | null;
  landholding_acres?: number | null;
  is_differently_abled?: boolean | null;
  minority_status?: boolean | null;
}

export interface SchemeRecommendation {
  scheme: SchemeResponse;
  match_score: number;
  match_reasons: string[];
  is_eligible: boolean;
  missing_criteria?: string[];
}

export interface LoanCalculatorRequest {
  project_cost: number;
  margin_percentage: number;
  annual_interest_rate: number;
  repayment_period_months: number;
  moratorium_months: number;
}

export interface LoanCalculatorResponse {
  project_cost: number;
  margin_percentage: number;
  margin_amount: number;
  loan_amount: number;
  annual_interest_rate: number;
  repayment_period_months: number;
  moratorium_months: number;
  total_interest: number;
  total_repayment: number;
  approx_monthly_payment: number;
  is_estimate: boolean;
  calculation_note: string;
}

export interface SchemeLoanCalculatorRequest {
  project_cost: number;
  margin_percentage?: number | null;
}

export interface SchemeLoanCalculatorResponse {
  scheme_id: string;
  scheme_name: string;
  project_cost: number;
  margin_percentage?: number | null;
  margin_amount?: number | null;
  subsidy_percentage?: number | null;
  subsidy_amount?: number | null;
  maximum_amount?: number | null;
  interest_rate?: number | null;
  loan_amount: number;
  repayment_period_months?: number | null;
  moratorium_months?: number | null;
  total_interest?: number | null;
  total_repayment?: number | null;
  approx_monthly_payment?: number | null;
  warnings: string[];
  is_estimate: boolean;
  calculation_note: string;
}

export interface AIChatRequest {
  message: string;
  scheme_id?: string | null;
  user_context?: RecommendationRequest | null;
  language?: string | null;
}

export interface AIChatResponse {
  reply: string;
  scheme_id?: string | null;
  sources: string[];
  disclaimer: string;
}

// ---------------------------------------------------------------------------
// Helper Request Function
// ---------------------------------------------------------------------------

async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const defaultHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const res = await fetch(url, config);

    if (!res.ok) {
      let errorMessage = `API request failed with status ${res.status}`;
      try {
        const errorData = await res.json();
        if (errorData?.error?.message) {
          errorMessage = errorData.error.message;
        } else if (errorData?.detail) {
          errorMessage = typeof errorData.detail === 'string'
            ? errorData.detail
            : JSON.stringify(errorData.detail);
        }
      } catch {
        // use default error message if response is not json
      }
      throw new Error(errorMessage);
    }

    return (await res.json()) as T;
  } catch (err: unknown) {
    if (err instanceof Error) {
      throw err;
    }
    throw new Error('Unknown network or server error occurred');
  }
}

// ---------------------------------------------------------------------------
// API Client Functions
// ---------------------------------------------------------------------------

/**
 * Health check endpoint.
 * GET /api/health
 */
export async function healthCheck(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>('/api/health', {
    method: 'GET',
    cache: 'no-store',
  });
}

/**
 * Comprehensive business feasibility, financial, market and scheme analysis.
 * POST /api/business/analyze
 */
export async function analyzeBusiness(
  payload: BusinessAnalyzeRequest,
): Promise<BusinessAnalyzeResponse> {
  return apiFetch<BusinessAnalyzeResponse>('/api/business/analyze', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * Fetch paginated schemes list.
 * GET /api/schemes
 */
export async function getSchemes(
  params: SchemeQueryParams = {},
): Promise<PaginatedSchemeResponse> {
  const query = new URLSearchParams();
  if (params.state) query.set('state', params.state);
  if (params.ministry) query.set('ministry', params.ministry);
  if (params.department) query.set('department', params.department);
  if (params.scheme_type) query.set('scheme_type', params.scheme_type);
  if (params.status) query.set('status', params.status);
  if (params.sort_by) query.set('sort_by', params.sort_by);
  if (params.sort_order) query.set('sort_order', params.sort_order);
  if (params.page) query.set('page', params.page.toString());
  if (params.limit) query.set('limit', params.limit.toString());

  const queryString = query.toString();
  const endpoint = queryString ? `/api/schemes?${queryString}` : '/api/schemes';
  return apiFetch<PaginatedSchemeResponse>(endpoint, {
    method: 'GET',
  });
}

/**
 * Fetch a single scheme by UUID.
 * GET /api/schemes/{id}
 */
export async function getScheme(id: string): Promise<SchemeResponse> {
  return apiFetch<SchemeResponse>(`/api/schemes/${encodeURIComponent(id)}`, {
    method: 'GET',
  });
}

/**
 * Fetch complete scheme details (scheme, eligibility, benefits, source).
 * GET /api/schemes/{id}/details
 */
export async function getSchemeDetails(id: string): Promise<SchemeDetailsResponse> {
  return apiFetch<SchemeDetailsResponse>(
    `/api/schemes/${encodeURIComponent(id)}/details`,
    {
      method: 'GET',
    },
  );
}

/**
 * Get deterministic recommendations based on profile criteria.
 * POST /api/recommendations
 */
export async function getRecommendations(
  payload: RecommendationRequest,
): Promise<SchemeRecommendation[]> {
  return apiFetch<SchemeRecommendation[]>('/api/recommendations', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * Calculate loan details with reducing balance EMI.
 * POST /api/loan-calculator
 */
export async function calculateLoan(
  payload: LoanCalculatorRequest,
): Promise<LoanCalculatorResponse> {
  return apiFetch<LoanCalculatorResponse>('/api/loan-calculator', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * Calculate loan details using scheme benefit rules.
 * POST /api/loan-calculator/scheme/{scheme_id}
 */
export async function calculateSchemeLoan(
  schemeId: string,
  payload: SchemeLoanCalculatorRequest,
): Promise<SchemeLoanCalculatorResponse> {
  return apiFetch<SchemeLoanCalculatorResponse>(
    `/api/loan-calculator/scheme/${encodeURIComponent(schemeId)}`,
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
  );
}

/**
 * Grounded AI chat assistant powered by Gemini.
 * POST /api/ai/chat
 */
export async function chatWithAI(payload: AIChatRequest): Promise<AIChatResponse> {
  return apiFetch<AIChatResponse>('/api/ai/chat', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
