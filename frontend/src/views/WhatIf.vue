<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { getCase } from '@/api/cases'
import { createWhatIf } from '@/api/whatif'
import type { WhatIfChanges } from '@/api/whatif'

type EditableField = 'facts' | 'evidence' | 'claims'

type CaseInput = {
  case_type: string
  parties: string
  facts: string
  claims: string
  evidence: string[]
}

type CaseRecord = {
  id: string
  created_at: string
  input_data: CaseInput
}

type FieldDifference = {
  field: EditableField
  original: string | string[]
  modified: string | string[]
}

type WhatIfResponse = {
  id: string
  original_scenario_id: string
  created_at: string
  comparison: {
    original_case: CaseRecord
    modified_case: CaseRecord
    differences: FieldDifference[]
    summary: string
  }
}

const fieldOptions: Array<{ label: string; value: EditableField; subtitle: string }> = [
  {
    label: '사실관계 수정',
    value: 'facts',
    subtitle: '사건의 전제 사실을 다시 설정합니다.',
  },
  {
    label: '증거 추가/삭제',
    value: 'evidence',
    subtitle: '입증 자료를 추가하거나 제거합니다.',
  },
  {
    label: '주장 변경',
    value: 'claims',
    subtitle: '당사자의 핵심 주장을 수정합니다.',
  },
]

const fieldLabels: Record<EditableField, string> = {
  facts: '사실관계',
  evidence: '증거',
  claims: '주장',
}

const route = useRoute()

const loading = ref(false)
const generating = ref(false)
const errorMessage = ref('')
const originalCase = ref<CaseRecord | null>(null)
const whatIfResult = ref<WhatIfResponse | null>(null)

const primaryField = ref<EditableField>('facts')
const enableSecondaryField = ref(false)
const secondaryField = ref<EditableField | null>(null)

const formState = reactive({
  facts: '',
  evidenceText: '',
  claims: '',
})

const routeId = computed(() => {
  const rawId = route.params.id
  return typeof rawId === 'string' ? rawId : ''
})

const availableSecondaryOptions = computed(() =>
  fieldOptions.filter(option => option.value !== primaryField.value),
)

const selectedFields = computed<EditableField[]>(() => {
  const fields: EditableField[] = [primaryField.value]

  if (
    enableSecondaryField.value &&
    secondaryField.value &&
    secondaryField.value !== primaryField.value
  ) {
    fields.push(secondaryField.value)
  }

  return fields
})

const selectedFieldSet = computed(() => new Set(selectedFields.value))

const originalInput = computed(() => originalCase.value?.input_data ?? null)

const evidenceDraft = computed(() =>
  formState.evidenceText
    .split('\n')
    .map(entry => entry.trim())
    .filter(Boolean),
)

const changedFields = computed<EditableField[]>(() => {
  if (!originalInput.value) {
    return []
  }

  const changes: EditableField[] = []

  if (
    selectedFieldSet.value.has('facts') &&
    formState.facts.trim() !== originalInput.value.facts.trim()
  ) {
    changes.push('facts')
  }

  if (
    selectedFieldSet.value.has('evidence') &&
    JSON.stringify(evidenceDraft.value) !== JSON.stringify(originalInput.value.evidence)
  ) {
    changes.push('evidence')
  }

  if (
    selectedFieldSet.value.has('claims') &&
    formState.claims.trim() !== originalInput.value.claims.trim()
  ) {
    changes.push('claims')
  }

  return changes
})

const canGenerate = computed(
  () => Boolean(originalCase.value) && changedFields.value.length >= 1 && changedFields.value.length <= 2,
)

const summaryItems = computed(() => {
  if (!originalInput.value) {
    return []
  }

  return [
    { label: '사건 유형', value: originalInput.value.case_type },
    { label: '당사자', value: originalInput.value.parties },
    { label: '증거 수', value: `${originalInput.value.evidence.length}건` },
    { label: 'What-If 한도', value: '최대 2개 변수' },
  ]
})

const diffFieldSet = computed(
  () => new Set<EditableField>(whatIfResult.value?.comparison.differences.map(diff => diff.field) ?? []),
)

const secondaryPlaceholder = computed(
  () => availableSecondaryOptions.value[0]?.value ?? null,
)

watch(primaryField, nextField => {
  if (secondaryField.value === nextField) {
    secondaryField.value = secondaryPlaceholder.value
  }
})

watch(enableSecondaryField, isEnabled => {
  if (!isEnabled) {
    secondaryField.value = null
    return
  }

  secondaryField.value ??= secondaryPlaceholder.value
})

watch(
  routeId,
  async id => {
    whatIfResult.value = null
    errorMessage.value = ''

    if (!id) {
      originalCase.value = null
      return
    }

    loading.value = true

    try {
      const response = await getCase(id)
      originalCase.value = response
      hydrateForm(response.input_data)
    } catch (error) {
      originalCase.value = null
      errorMessage.value = readErrorMessage(error, '원본 시나리오를 불러오지 못했습니다.')
    } finally {
      loading.value = false
    }
  },
  { immediate: true },
)

async function generateScenario() {
  if (!originalCase.value) {
    return
  }

  const changes = buildChangesPayload()
  if (Object.keys(changes).length === 0) {
    errorMessage.value = '변경 사항을 1개 이상 입력해 주세요.'
    return
  }

  generating.value = true
  errorMessage.value = ''

  try {
    const response = await createWhatIf({
      original_scenario_id: originalCase.value.id,
      changes,
    })

    whatIfResult.value = response
  } catch (error) {
    errorMessage.value = readErrorMessage(error, '새 시나리오를 생성하지 못했습니다.')
  } finally {
    generating.value = false
  }
}

function hydrateForm(input: CaseInput) {
  formState.facts = input.facts
  formState.evidenceText = input.evidence.join('\n')
  formState.claims = input.claims
}

function buildChangesPayload() {
  if (!originalInput.value) {
    return {}
  }

  const changes: WhatIfChanges = {}

  if (changedFields.value.includes('facts')) {
    changes.facts = formState.facts.trim()
  }

  if (changedFields.value.includes('evidence')) {
    changes.evidence = evidenceDraft.value
  }

  if (changedFields.value.includes('claims')) {
    changes.claims = formState.claims.trim()
  }

  return changes
}

function renderFieldValue(value: string | string[]) {
  if (Array.isArray(value)) {
    return value.length > 0 ? value.join('\n') : '입력된 내용이 없습니다.'
  }

  return value || '입력된 내용이 없습니다.'
}

function isChanged(field: EditableField) {
  return diffFieldSet.value.has(field)
}

function readErrorMessage(error: unknown, fallback: string) {
  return error instanceof Error ? error.message : fallback
}
</script>

<template>
  <v-sheet class="whatif-view d-flex flex-column ga-6" color="transparent">
    <section class="d-flex flex-column ga-4">
      <div class="d-flex flex-column ga-2">
        <p class="text-overline text-primary">What-If Scenario Lab</p>
        <div class="d-flex flex-column ga-2 ga-md-3">
          <h1 class="text-h4 font-weight-bold">변수를 1~2개 바꿔 새 해석 시나리오를 만듭니다.</h1>
          <p class="text-body-1 text-medium-emphasis">
            원본 사건의 핵심 요소를 유지한 채 사실관계, 증거, 주장 중 최대 두 항목만 바꿔
            비교 가능한 대안 시나리오를 생성합니다.
          </p>
        </div>
      </div>

      <v-alert
        type="info"
        variant="tonal"
        density="comfortable"
        text="MVP 제약: 한 번에 1~2개 변수만 수정할 수 있습니다."
      />
    </section>

    <v-alert v-if="errorMessage" type="error" variant="tonal" :text="errorMessage" />

    <v-skeleton-loader v-if="loading" type="article, article" />

    <template v-else-if="originalInput">
      <v-card rounded="xl" variant="outlined">
        <v-card-item>
          <template #prepend>
            <v-icon icon="mdi-file-document-edit-outline" color="primary" />
          </template>
          <v-card-title>원본 시나리오 요약</v-card-title>
          <v-card-subtitle>사건 ID {{ originalCase?.id }}</v-card-subtitle>
        </v-card-item>

        <v-card-text class="d-flex flex-column ga-4">
          <div class="d-flex flex-wrap ga-2">
            <v-chip
              v-for="item in summaryItems"
              :key="item.label"
              color="primary"
              variant="tonal"
              size="small"
            >
              {{ item.label }} · {{ item.value }}
            </v-chip>
          </div>

          <v-row>
            <v-col cols="12" md="6">
              <div class="d-flex flex-column ga-2">
                <p class="text-subtitle-2 text-medium-emphasis">핵심 사실</p>
                <p class="text-body-1 comparison-copy">{{ originalInput.facts }}</p>
              </div>
            </v-col>
            <v-col cols="12" md="6">
              <div class="d-flex flex-column ga-2">
                <p class="text-subtitle-2 text-medium-emphasis">현재 주장</p>
                <p class="text-body-1 comparison-copy">{{ originalInput.claims }}</p>
              </div>
            </v-col>
          </v-row>

          <div class="d-flex flex-column ga-2">
            <p class="text-subtitle-2 text-medium-emphasis">증거 목록</p>
            <div class="d-flex flex-wrap ga-2">
              <v-chip
                v-for="evidence in originalInput.evidence"
                :key="evidence"
                size="small"
                variant="outlined"
              >
                {{ evidence }}
              </v-chip>
              <span v-if="originalInput.evidence.length === 0" class="text-body-2 text-medium-emphasis">
                입력된 증거가 없습니다.
              </span>
            </div>
          </div>
        </v-card-text>
      </v-card>

      <v-card rounded="xl" variant="outlined">
        <v-card-item>
          <template #prepend>
            <v-icon icon="mdi-tune-variant" color="primary" />
          </template>
          <v-card-title>변수 선택 및 수정</v-card-title>
          <v-card-subtitle>라디오 버튼으로 주 변경 항목을 고르고, 필요하면 한 항목을 더 추가하세요.</v-card-subtitle>
        </v-card-item>

        <v-card-text class="d-flex flex-column ga-6">
          <div class="d-flex flex-column ga-4">
            <v-radio-group v-model="primaryField" color="primary" inline>
              <div class="d-flex flex-column ga-3">
                <v-radio
                  v-for="option in fieldOptions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </div>
            </v-radio-group>

            <div class="d-flex flex-column ga-3">
              <v-switch
                v-model="enableSecondaryField"
                color="primary"
                inset
                label="보조 변경 항목 추가"
              />

              <v-select
                v-if="enableSecondaryField"
                v-model="secondaryField"
                :items="availableSecondaryOptions"
                item-title="label"
                item-value="value"
                label="두 번째 변수 선택"
                variant="outlined"
                hide-details
              />
            </div>
          </div>

          <div class="d-flex flex-wrap ga-2">
            <v-chip
              v-for="field in selectedFields"
              :key="field"
              color="primary"
              variant="flat"
              size="small"
            >
              {{ fieldLabels[field] }}
            </v-chip>
            <v-chip color="secondary" variant="tonal" size="small">
              실제 변경 {{ changedFields.length }}/2
            </v-chip>
          </div>

          <div class="d-flex flex-column ga-4">
            <v-textarea
              v-if="selectedFieldSet.has('facts')"
              v-model="formState.facts"
              label="수정된 사실관계"
              placeholder="새로운 사실관계를 입력하세요."
              variant="outlined"
              rows="5"
              auto-grow
              counter
            />

            <v-textarea
              v-if="selectedFieldSet.has('evidence')"
              v-model="formState.evidenceText"
              label="증거 목록"
              placeholder="증거를 한 줄에 하나씩 입력하세요."
              variant="outlined"
              rows="5"
              auto-grow
              hint="줄바꿈 기준으로 증거를 추가/삭제합니다."
              persistent-hint
            />

            <v-textarea
              v-if="selectedFieldSet.has('claims')"
              v-model="formState.claims"
              label="수정된 주장"
              placeholder="새로운 주장을 입력하세요."
              variant="outlined"
              rows="5"
              auto-grow
              counter
            />
          </div>

          <div class="d-flex flex-column flex-sm-row ga-3 align-sm-center justify-space-between">
            <p class="text-body-2 text-medium-emphasis">
              선택된 항목 가운데 실제로 값이 바뀐 필드만 API에 전달됩니다.
            </p>
            <v-btn
              color="primary"
              size="large"
              :loading="generating"
              :disabled="!canGenerate"
              prepend-icon="mdi-swap-horizontal-bold"
              @click="generateScenario"
            >
              새 시나리오 생성
            </v-btn>
          </div>
        </v-card-text>
      </v-card>

      <section v-if="whatIfResult" class="d-flex flex-column ga-4">
        <v-card rounded="xl" color="primary" variant="tonal">
          <v-card-text class="d-flex flex-column ga-3">
            <div class="d-flex flex-wrap align-center ga-2">
              <p class="text-subtitle-1 font-weight-bold">차이 요약</p>
              <v-chip
                v-for="difference in whatIfResult.comparison.differences"
                :key="difference.field"
                color="primary"
                variant="flat"
                size="small"
              >
                {{ fieldLabels[difference.field] }} 변경
              </v-chip>
            </div>
            <p class="text-body-1">{{ whatIfResult.comparison.summary }}</p>
          </v-card-text>
        </v-card>

        <v-row align="stretch">
          <v-col cols="12" lg="6">
            <v-card rounded="xl" variant="outlined" class="fill-height">
              <v-card-item>
                <template #prepend>
                  <v-icon icon="mdi-file-outline" color="primary" />
                </template>
                <v-card-title>Original scenario</v-card-title>
                <v-card-subtitle>비교 기준</v-card-subtitle>
              </v-card-item>

              <v-card-text class="d-flex flex-column ga-4">
                <div class="comparison-field pa-4 rounded-lg" :class="{ 'comparison-field--changed': false }">
                  <p class="text-overline text-medium-emphasis">사건 유형</p>
                  <p class="text-body-1">{{ whatIfResult.comparison.original_case.input_data.case_type }}</p>
                </div>

                <div class="comparison-field pa-4 rounded-lg" :class="{ 'comparison-field--changed': false }">
                  <p class="text-overline text-medium-emphasis">당사자</p>
                  <p class="text-body-1 comparison-copy">
                    {{ whatIfResult.comparison.original_case.input_data.parties }}
                  </p>
                </div>

                <div
                  class="comparison-field pa-4 rounded-lg"
                  :class="{ 'comparison-field--changed': isChanged('facts') }"
                >
                  <div class="d-flex align-center justify-space-between ga-2">
                    <p class="text-overline text-medium-emphasis">사실관계</p>
                    <v-chip v-if="isChanged('facts')" size="x-small" color="primary" variant="flat">
                      변경됨
                    </v-chip>
                  </div>
                  <p class="text-body-1 comparison-copy">
                    {{ renderFieldValue(whatIfResult.comparison.original_case.input_data.facts) }}
                  </p>
                </div>

                <div
                  class="comparison-field pa-4 rounded-lg"
                  :class="{ 'comparison-field--changed': isChanged('evidence') }"
                >
                  <div class="d-flex align-center justify-space-between ga-2">
                    <p class="text-overline text-medium-emphasis">증거</p>
                    <v-chip v-if="isChanged('evidence')" size="x-small" color="primary" variant="flat">
                      변경됨
                    </v-chip>
                  </div>
                  <p class="text-body-1 comparison-copy">
                    {{ renderFieldValue(whatIfResult.comparison.original_case.input_data.evidence) }}
                  </p>
                </div>

                <div
                  class="comparison-field pa-4 rounded-lg"
                  :class="{ 'comparison-field--changed': isChanged('claims') }"
                >
                  <div class="d-flex align-center justify-space-between ga-2">
                    <p class="text-overline text-medium-emphasis">주장</p>
                    <v-chip v-if="isChanged('claims')" size="x-small" color="primary" variant="flat">
                      변경됨
                    </v-chip>
                  </div>
                  <p class="text-body-1 comparison-copy">
                    {{ renderFieldValue(whatIfResult.comparison.original_case.input_data.claims) }}
                  </p>
                </div>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" lg="6">
            <v-card rounded="xl" variant="outlined" class="fill-height">
              <v-card-item>
                <template #prepend>
                  <v-icon icon="mdi-auto-fix" color="primary" />
                </template>
                <v-card-title>Modified scenario</v-card-title>
                <v-card-subtitle>API 생성 결과</v-card-subtitle>
              </v-card-item>

              <v-card-text class="d-flex flex-column ga-4">
                <div class="comparison-field pa-4 rounded-lg">
                  <p class="text-overline text-medium-emphasis">사건 유형</p>
                  <p class="text-body-1">{{ whatIfResult.comparison.modified_case.input_data.case_type }}</p>
                </div>

                <div class="comparison-field pa-4 rounded-lg">
                  <p class="text-overline text-medium-emphasis">당사자</p>
                  <p class="text-body-1 comparison-copy">
                    {{ whatIfResult.comparison.modified_case.input_data.parties }}
                  </p>
                </div>

                <div
                  class="comparison-field pa-4 rounded-lg"
                  :class="{ 'comparison-field--changed': isChanged('facts') }"
                >
                  <div class="d-flex align-center justify-space-between ga-2">
                    <p class="text-overline text-medium-emphasis">사실관계</p>
                    <v-chip v-if="isChanged('facts')" size="x-small" color="primary" variant="flat">
                      새 해석 변수
                    </v-chip>
                  </div>
                  <p class="text-body-1 comparison-copy">
                    {{ renderFieldValue(whatIfResult.comparison.modified_case.input_data.facts) }}
                  </p>
                </div>

                <div
                  class="comparison-field pa-4 rounded-lg"
                  :class="{ 'comparison-field--changed': isChanged('evidence') }"
                >
                  <div class="d-flex align-center justify-space-between ga-2">
                    <p class="text-overline text-medium-emphasis">증거</p>
                    <v-chip v-if="isChanged('evidence')" size="x-small" color="primary" variant="flat">
                      새 해석 변수
                    </v-chip>
                  </div>
                  <p class="text-body-1 comparison-copy">
                    {{ renderFieldValue(whatIfResult.comparison.modified_case.input_data.evidence) }}
                  </p>
                </div>

                <div
                  class="comparison-field pa-4 rounded-lg"
                  :class="{ 'comparison-field--changed': isChanged('claims') }"
                >
                  <div class="d-flex align-center justify-space-between ga-2">
                    <p class="text-overline text-medium-emphasis">주장</p>
                    <v-chip v-if="isChanged('claims')" size="x-small" color="primary" variant="flat">
                      새 해석 변수
                    </v-chip>
                  </div>
                  <p class="text-body-1 comparison-copy">
                    {{ renderFieldValue(whatIfResult.comparison.modified_case.input_data.claims) }}
                  </p>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </section>
    </template>

    <v-card v-else rounded="xl" variant="outlined">
      <v-card-text class="py-10 text-center text-medium-emphasis">
        비교할 원본 시나리오를 찾지 못했습니다. 유효한 사건 ID로 다시 진입해 주세요.
      </v-card-text>
    </v-card>
  </v-sheet>
</template>

<style scoped>
.whatif-view {
  --whatif-field-border: rgba(var(--v-theme-on-surface), 0.12);
  --whatif-field-highlight-border: rgba(var(--v-theme-primary), 0.32);
  --whatif-field-highlight-bg: rgba(var(--v-theme-primary), 0.08);
}

.comparison-field {
  border: 1px solid var(--whatif-field-border);
  background: rgb(var(--v-theme-surface));
}

.comparison-field--changed {
  border-color: var(--whatif-field-highlight-border);
  background: var(--whatif-field-highlight-bg);
}

.comparison-copy {
  white-space: pre-line;
}
</style>
