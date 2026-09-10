import { apiClient } from './client'
import { LocationQueryParams, LocationResponse } from './types'

export async function getLocations(
  params?: LocationQueryParams
): Promise<LocationResponse[]> {
  return apiClient<LocationResponse[]>('/api/locations', {
    params: params as any,
  })
}
