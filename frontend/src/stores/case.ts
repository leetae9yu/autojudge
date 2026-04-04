import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { apiBaseUrl } from '../api'

export const caseTypeOptions = ['손해배상', '계약위반', '부당이득'] as const

export type CaseType = (typeof caseTypeOptions)[number]

export interface CaseDraft {
  case_type: CaseType | null
  parties: string
  facts: string
  claims: string
  evidence: string[]
}

export interface CaseValidationErrors {
  case_type: string
  parties: string
  facts: string
  claims: string
  evidence: string
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
  input_data: CasePayload
}

const emptyErrors: CaseValidationErrors = {
  case_type: '',
  parties: '',
  facts: '',
  claims: '',
  evidence: '',
}

const createEmptyForm = (): CaseDraft => ({
  case_type: null,
  parties: '',
  facts: '',
  claims: '',
  evidence: [],
})

const normalizeEvidence = (items: string[]) =>
  [...new Set(items.map(item => item.trim()).filter(Boolean))]

const buildValidationErrors = (draft: CaseDraft): CaseValidationErrors => ({
  case_type: draft.case_type ? '' : '사건 유형을 선택해 주세요.',
  parties: draft.parties.trim() ? '' : '당사자 관계를 입력해 주세요.',
  facts: draft.facts.trim() ? '' : '사실관계를 입력해 주세요.',
  claims: draft.claims.trim() ? '' : '주장/항변을 입력해 주세요.',
  evidence: normalizeEvidence(draft.evidence).length > 0 ? '' : '증거를 최소 1개 이상 추가해 주세요.',
})

const hasErrors = (errors: CaseValidationErrors) => Object.values(errors).some(Boolean)

const toPayload = (draft: CaseDraft): CasePayload => ({
  case_type: draft.case_type as CaseType,
  parties: draft.parties.trim(),
  facts: draft.facts.trim(),
  claims: draft.claims.trim(),
  evidence: normalizeEvidence(draft.evidence),
})

export const useCaseStore = defineStore('case', () => {
  const form = ref<CaseDraft>(createEmptyForm())
  const didAttemptSubmit = ref(false)
  const isSubmitting = ref(false)
  const submitError = ref('')
  const lastCreatedCase = ref<CaseRecord | null>(null)

  const validationErrors = computed(() =>
    didAttemptSubmit.value ? buildValidationErrors(form.value) : emptyErrors,
  )

  const canSubmit = computed(() => !hasErrors(buildValidationErrors(form.value)) && !isSubmitting.value)

  function setEvidence(items: string[]) {
    form.value.evidence = normalizeEvidence(items)
  }

  function resetForm() {
    form.value = createEmptyForm()
    didAttemptSubmit.value = false
    submitError.value = ''
  }

  async function createCase() {
    didAttemptSubmit.value = true
    submitError.value = ''

    const errors = buildValidationErrors(form.value)

    if (hasErrors(errors)) {
      return null
    }

    isSubmitting.value = true

    try {
      const response = await fetch(`${apiBaseUrl}/cases`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(toPayload(form.value)),
      })

      if (!response.ok) {
        let detail = '사건 등록에 실패했습니다. 잠시 후 다시 시도해 주세요.'

        try {
          const errorData = (await response.json()) as { detail?: string }

          if (typeof errorData.detail === 'string' && errorData.detail.trim()) {
            detail = errorData.detail
          }
        } catch {
          // ignore JSON parse failures and fall back to the default message
        }

        throw new Error(detail)
      }

      const createdCase = (await response.json()) as CaseRecord
      lastCreatedCase.value = createdCase

      return createdCase
    } catch (error) {
      submitError.value =
        error instanceof Error ? error.message : '사건 등록에 실패했습니다. 잠시 후 다시 시도해 주세요.'

      return null
    } finally {
      isSubmitting.value = false
    }
  }

  return {
    canSubmit,
    caseTypeOptions,
    createCase,
    form,
    isSubmitting,
    lastCreatedCase,
    resetForm,
    setEvidence,
    submitError,
    validationErrors,
  }
})
