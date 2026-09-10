import { ApiError, ApiErrorPayload } from './types'

const rawApiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
export const API_BASE_URL = rawApiUrl.replace(/\/+$/, '')

interface FetchOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined | null>
}

export async function apiClient<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
  const { params, headers, ...customConfig } = options

  // Normalize endpoint string
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
  let url = `${API_BASE_URL}${cleanEndpoint}`

  // Append query params if present
  if (params) {
    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        searchParams.append(key, String(val))
      }
    })
    const queryString = searchParams.toString()
    if (queryString) {
      url += `?${queryString}`
    }
  }

  const config: RequestInit = {
    method: options.method || 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    ...customConfig,
  }

  let response: Response
  try {
    response = await fetch(url, config)
  } catch (err: any) {
    throw new ApiError(
      'Network error. Please check backend connection and server availability.',
      'NETWORK_ERROR',
      0
    )
  }

  let data: any
  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('application/json')) {
    try {
      data = await response.json()
    } catch {
      data = null
    }
  } else {
    data = await response.text()
  }

  if (!response.ok) {
    if (data && typeof data === 'object' && data.success === false && data.error) {
      const errorPayload = data as ApiErrorPayload
      throw new ApiError(
        errorPayload.error.message || 'API request failed',
        errorPayload.error.code || `HTTP_${response.status}`,
        response.status,
        errorPayload.error.details
      )
    }

    const message =
      typeof data === 'string' && data
        ? data
        : data?.detail || `HTTP Error ${response.status}: ${response.statusText}`

    throw new ApiError(message, `HTTP_${response.status}`, response.status)
  }

  return data as T
}
