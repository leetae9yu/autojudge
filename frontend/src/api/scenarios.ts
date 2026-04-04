import { apiClient } from './client'

export interface ScenarioAuthority {
  id: string
  type: '법령' | '판례'
  label: string
  citation: string
  summary: string
}

export interface ScenarioItem {
  title: string
  interpretation: string
  basis: string[]
  probability: 'high' | 'medium' | 'low'
  key_factors: string[]
  disclaimer: string
}

export interface ScenarioGenerationRequest {
  case_id: string
  count?: number
}

export interface ScenarioGenerationResult {
  id: string
  case_id: string
  disclaimer: string
  scenarios: ScenarioItem[]
}

export async function createScenarios(request: ScenarioGenerationRequest): Promise<ScenarioGenerationResult> {
  const response = await apiClient.post<ScenarioGenerationResult>('/api/scenarios', request)
  return response.data
}

export async function getScenario(scenarioId: string): Promise<ScenarioGenerationResult> {
  const response = await apiClient.get<ScenarioGenerationResult>(`/api/scenarios/${scenarioId}`)
  return response.data
}
