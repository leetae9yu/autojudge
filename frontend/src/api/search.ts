import { apiClient } from './client'

export interface SearchRequest {
  case_id: string
  top_k?: number
}

export interface SearchResultItem {
  id?: string
  title?: string
  citation?: string
  summary?: string
  score?: number
}

export interface SearchResponse {
  query: string
  laws: SearchResultItem[]
  precedents: SearchResultItem[]
}

export async function searchCase(request: SearchRequest): Promise<SearchResponse> {
  const response = await apiClient.post<SearchResponse>('/api/search', request)
  return response.data
}
