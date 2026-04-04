import { apiClient } from './client'

export type CaseType = '손해배상' | '계약위반' | '부당이득' | '기타'

export interface CaseInput {
  case_type: CaseType
  parties: string
  facts: string
  claims: string
  evidence: string[]
}

export interface CasePayload {
  case_type: CaseType
  parties: string
  facts: string
  claims: string
  evidence: string[]
}

export interface CaseRecord {
  id: string
  created_at: string
  disclaimer: string
  input_data: CaseInput
}

export async function createCase(payload: CasePayload): Promise<CaseRecord> {
  const response = await apiClient.post<CaseRecord>('/api/cases', payload)
  return response.data
}

export async function getCase(caseId: string): Promise<CaseRecord> {
  const response = await apiClient.get<CaseRecord>(`/api/cases/${caseId}`)
  return response.data
}
