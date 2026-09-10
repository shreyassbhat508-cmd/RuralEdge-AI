import { apiClient } from './client'
import { BusinessAnalyzeRequest, BusinessAnalyzeResponse } from './types'

export async function analyzeBusiness(
  request: BusinessAnalyzeRequest
): Promise<BusinessAnalyzeResponse> {
  return apiClient<BusinessAnalyzeResponse>('/api/business/analyze', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}
