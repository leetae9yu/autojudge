import { apiClient } from './client'
import type { CaseInput, CaseRecord } from './cases'

export interface WhatIfChanges {
  facts?: string | null
  evidence?: string[] | null
  claims?: string | null
}

export interface WhatIfRequest {
  original_scenario_id: string
  changes: WhatIfChanges
}

export interface FieldDifference {
  field: 'facts' | 'evidence' | 'claims'
  original: string | string[]
  modified: string | string[]
}

export interface WhatIfComparison {
  original_case: CaseRecord & { input_data: CaseInput }
  modified_case: CaseRecord & { input_data: CaseInput }
  differences: FieldDifference[]
  summary: string
}

export interface WhatIfResponse {
  id: string
  created_at: string
  original_scenario_id: string
  disclaimer: string
  comparison: WhatIfComparison
}

export async function createWhatIf(request: WhatIfRequest): Promise<WhatIfResponse> {
  const response = await apiClient.post<WhatIfResponse>('/api/whatif', request)
  return response.data
}

export async function getWhatIf(scenarioId: string): Promise<WhatIfResponse> {
  const response = await apiClient.get<WhatIfResponse>(`/api/whatif/${scenarioId}`)
  return response.data
}
