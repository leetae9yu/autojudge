export type ScenarioProbability = 'high' | 'medium' | 'low'

export interface ScenarioAuthority {
  id: string
  type: '법령' | '판례'
  label: string
  citation: string
  summary: string
}

export interface ScenarioCardItem {
  id: string
  title: string
  interpretation: string
  probability: ScenarioProbability
  keyFactors: string[]
  basis: ScenarioAuthority[]
}
