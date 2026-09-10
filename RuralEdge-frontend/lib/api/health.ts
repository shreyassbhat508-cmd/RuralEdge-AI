import { apiClient } from './client'
import { HealthResponse } from './types'

export async function getHealth(): Promise<HealthResponse> {
  return apiClient<HealthResponse>('/api/health')
}
