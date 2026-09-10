import { apiClient } from './client'
import { AIChatRequest, AIChatResponse } from './types'

export async function sendAiMessage(request: AIChatRequest): Promise<AIChatResponse> {
  return apiClient<AIChatResponse>('/api/ai/chat', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}
