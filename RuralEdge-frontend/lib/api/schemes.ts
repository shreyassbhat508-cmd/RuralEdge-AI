import { apiClient } from './client'
import {
  BenefitResponse,
  EligibilityResponse,
  PaginatedSchemeResponse,
  RecommendationRequest,
  SchemeDetailsResponse,
  SchemeFilterParams,
  SchemeResponse,
  SchemeSearchParams,
} from './types'

export async function getSchemes(params?: SchemeFilterParams): Promise<PaginatedSchemeResponse> {
  return apiClient<PaginatedSchemeResponse>('/api/schemes', { params: params as any })
}

export async function searchSchemes(params?: SchemeSearchParams): Promise<SchemeResponse[]> {
  return apiClient<SchemeResponse[]>('/api/schemes/search', { params: params as any })
}

export async function getSchemeById(id: string): Promise<SchemeResponse> {
  return apiClient<SchemeResponse>(`/api/schemes/${id}`)
}

export async function getSchemeDetails(id: string): Promise<SchemeDetailsResponse> {
  return apiClient<SchemeDetailsResponse>(`/api/schemes/${id}/details`)
}

export async function getSchemeEligibility(id: string): Promise<EligibilityResponse[]> {
  return apiClient<EligibilityResponse[]>(`/api/schemes/${id}/eligibility`)
}

export async function getSchemeBenefits(id: string): Promise<BenefitResponse[]> {
  return apiClient<BenefitResponse[]>(`/api/schemes/${id}/benefits`)
}

export async function checkSchemeEligibility(
  id: string,
  request: RecommendationRequest
): Promise<{ scheme: SchemeResponse; eligible: boolean; reasons: string[]; warnings: string[] }> {
  return apiClient(`/api/schemes/${id}/eligibility-check`, {
    method: 'POST',
    body: JSON.stringify(request),
  })
}
