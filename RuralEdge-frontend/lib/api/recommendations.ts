import { apiClient } from './client'
import { RecommendationRequest, SchemeRecommendation } from './types'

export async function getRecommendations(
  request: RecommendationRequest
): Promise<SchemeRecommendation[]> {
  return apiClient<SchemeRecommendation[]>('/api/recommendations', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}
