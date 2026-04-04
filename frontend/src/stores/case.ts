import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { createCase as createCaseRequest, type CasePayload, type CaseRecord, type CaseType as ApiCaseType } from '../api/cases'
import { getApiErrorMessage } from '../api/client'

export type { CasePayload, CaseRecord } from '../api/cases'

export type CaseType = '손해배상' | '계약위반' | '부당이득'

export const caseTypeOptions = ['손해배상', '계약위반', '부당이득'] as const satisfies readonly CaseType[]

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
  case_type: draft.case_type as ApiCaseType,
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
      const createdCase = await createCaseRequest(toPayload(form.value))
      lastCreatedCase.value = createdCase

      return createdCase
    } catch (error) {
      submitError.value = getApiErrorMessage(error) || '사건 등록에 실패했습니다. 잠시 후 다시 시도해 주세요.'

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
