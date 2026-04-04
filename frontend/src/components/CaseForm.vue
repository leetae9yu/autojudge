<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { computed } from 'vue'

import { type CaseRecord, useCaseStore } from '../stores/case'

const emit = defineEmits<{
  submitted: [createdCase: CaseRecord]
}>()

const caseStore = useCaseStore()
const { caseTypeOptions } = caseStore
const { canSubmit, form, isSubmitting, submitError, validationErrors } = storeToRefs(caseStore)

const evidenceModel = computed<string[]>({
  get: () => form.value.evidence,
  set: value => caseStore.setEvidence(value),
})

const evidenceCountLabel = computed(() => {
  const count = evidenceModel.value.length

  return count > 0 ? `증거 ${count}건 정리됨` : '증거를 입력하고 Enter로 추가하세요'
})

async function submit() {
  const createdCase = await caseStore.createCase()

  if (createdCase) {
    emit('submitted', createdCase)
  }
}

void [caseTypeOptions, canSubmit, isSubmitting, submitError, validationErrors, evidenceCountLabel, submit]
</script>

<template>
  <v-card class="case-form-card" elevation="0">
    <v-form class="case-form" @submit.prevent="submit">
      <div class="case-form__header">
        <div>
          <p class="case-form__eyebrow">Case intake</p>
          <h2 class="case-form__title">사건의 논점을 빠짐없이 구조화하세요.</h2>
        </div>
        <p class="case-form__summary">
          핵심 사실, 주장, 증거를 분리해 입력하면 이후 시나리오 생성과 What-If 비교가 더 정확해집니다.
        </p>
      </div>

      <div class="case-form__grid">
        <section class="case-form__section">
          <div class="case-form__section-heading">
            <span class="case-form__index">01</span>
            <div>
              <h3>사건 기본 정보</h3>
              <p>분쟁의 프레임과 당사자 구도를 먼저 고정합니다.</p>
            </div>
          </div>

          <div class="case-form__fields case-form__fields--double">
            <v-select
              v-model="form.case_type"
              :items="caseTypeOptions"
              :disabled="isSubmitting"
              :error-messages="validationErrors.case_type"
              class="case-form__field"
              density="comfortable"
              hide-details="auto"
              label="사건 유형"
              placeholder="유형을 선택해 주세요"
              variant="outlined"
            />

            <v-text-field
              v-model="form.parties"
              :disabled="isSubmitting"
              :error-messages="validationErrors.parties"
              class="case-form__field"
              density="comfortable"
              hide-details="auto"
              label="당사자 관계"
              placeholder="예: 원고 A / 피고 B"
              variant="outlined"
            />
          </div>
        </section>

        <section class="case-form__section">
          <div class="case-form__section-heading">
            <span class="case-form__index">02</span>
            <div>
              <h3>사실관계</h3>
              <p>시간순 사실과 발생 경위를 자세히 적어 주세요.</p>
            </div>
          </div>

          <v-textarea
            v-model="form.facts"
            :disabled="isSubmitting"
            :error-messages="validationErrors.facts"
            auto-grow
            class="case-form__field"
            density="comfortable"
            hide-details="auto"
            label="사실관계"
            placeholder="계약 체결, 이행 지연, 손해 발생 등 사건의 흐름을 구체적으로 입력해 주세요"
            rows="5"
            variant="outlined"
          />
        </section>

        <section class="case-form__section">
          <div class="case-form__section-heading">
            <span class="case-form__index">03</span>
            <div>
              <h3>주장 및 항변</h3>
              <p>원고의 주장과 피고의 반론을 함께 정리해 두면 해석 폭이 넓어집니다.</p>
            </div>
          </div>

          <v-textarea
            v-model="form.claims"
            :disabled="isSubmitting"
            :error-messages="validationErrors.claims"
            auto-grow
            class="case-form__field"
            density="comfortable"
            hide-details="auto"
            label="주장 / 항변"
            placeholder="원고의 청구 취지와 피고의 항변, 쟁점이 되는 법적 포인트를 함께 적어 주세요"
            rows="5"
            variant="outlined"
          />
        </section>

        <section class="case-form__section case-form__section--evidence">
          <div class="case-form__section-heading">
            <span class="case-form__index">04</span>
            <div>
              <h3>증거 목록</h3>
              <p>증거를 칩 형태로 추가해 사건의 입증 가능성을 함께 기록합니다.</p>
            </div>
          </div>

          <v-combobox
            v-model="evidenceModel"
            :disabled="isSubmitting"
            :error-messages="validationErrors.evidence"
            chips
            class="case-form__field"
            clearable
            closable-chips
            density="comfortable"
            hide-details="auto"
            hint="예: 문자 메시지 캡처, 계약서 원본, 입금 내역"
            label="증거 목록"
            multiple
            persistent-hint
            placeholder="증거를 입력하고 Enter를 눌러 추가하세요"
            variant="outlined"
          />

          <div class="case-form__evidence-footer">
            <span class="case-form__evidence-count">{{ evidenceCountLabel }}</span>
            <span class="case-form__evidence-tip">최소 1개 이상의 증거가 필요합니다.</span>
          </div>
        </section>
      </div>

      <v-alert
        v-if="submitError"
        class="case-form__alert"
        density="comfortable"
        type="error"
        variant="tonal"
      >
        {{ submitError }}
      </v-alert>

      <div class="case-form__actions">
        <p class="case-form__note">모든 필드는 필수입니다. 제출 후 결과 페이지로 이동합니다.</p>
        <v-btn
          :class="{ 'case-form__submit--ready': canSubmit }"
          :disabled="isSubmitting"
          :loading="isSubmitting"
          class="case-form__submit"
          size="large"
          type="submit"
        >
          사건 등록 후 시뮬레이션 시작
        </v-btn>
      </div>
    </v-form>
  </v-card>
</template>

<style scoped>
.case-form-card {
  border: var(--border-thin) solid var(--color-border);
  border-radius: var(--radius-lg);
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.48), transparent 45%),
    var(--color-surface);
  box-shadow: var(--shadow-strong);
  backdrop-filter: blur(20px);
}

.case-form {
  display: grid;
  gap: var(--space-6);
  padding: var(--space-6);
}

.case-form__header {
  display: grid;
  gap: var(--space-4);
  padding-bottom: var(--space-5);
  border-bottom: var(--border-thin) solid var(--color-border);
}

.case-form__eyebrow {
  font-size: 0.875rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-highlight);
}

.case-form__title {
  font-family: var(--font-display);
  font-size: clamp(2rem, 4vw, 3rem);
  line-height: var(--line-height-tight);
  color: var(--color-heading);
}

.case-form__summary {
  max-width: 38rem;
  font-size: 1rem;
  color: var(--color-text-muted);
}

.case-form__grid {
  display: grid;
  gap: var(--space-5);
}

.case-form__section {
  display: grid;
  gap: var(--space-4);
  padding: var(--space-5);
  border: var(--border-thin) solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-strong);
  box-shadow: var(--shadow-soft);
}

.case-form__section-heading {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: var(--space-3);
  align-items: start;
}

.case-form__section-heading h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-heading);
}

.case-form__section-heading p {
  color: var(--color-text-muted);
}

.case-form__index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2.5rem;
  min-height: 2.5rem;
  padding-inline: var(--space-3);
  border-radius: var(--radius-pill);
  background: var(--color-accent-soft);
  color: var(--color-accent);
  font-size: 0.875rem;
  font-weight: 700;
}

.case-form__fields {
  display: grid;
  gap: var(--space-4);
}

.case-form__evidence-footer,
.case-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  align-items: center;
  justify-content: space-between;
}

.case-form__evidence-count,
.case-form__note {
  color: var(--color-heading);
  font-weight: 600;
}

.case-form__evidence-tip {
  color: var(--color-text-muted);
}

.case-form__alert {
  border-radius: var(--radius-md);
}

.case-form__submit {
  min-width: 16rem;
  border-radius: var(--radius-pill);
  background: linear-gradient(135deg, var(--color-heading), var(--color-accent));
  color: #ffffff;
  box-shadow: var(--shadow-soft);
  opacity: 0.8;
  transition:
    opacity 180ms ease,
    transform 180ms ease;
}

.case-form__submit--ready {
  opacity: 1;
}

.case-form__submit:hover {
  transform: translateY(calc(var(--space-1) * -1));
}

.case-form__submit :deep(.v-btn__content) {
  font-weight: 700;
  letter-spacing: 0.01em;
}

.case-form__field :deep(.v-field) {
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.45);
  box-shadow: inset 0 0 0 var(--border-thin) transparent;
}

.case-form__field :deep(.v-field__outline) {
  color: var(--color-border-strong);
}

.case-form__field :deep(.v-label),
.case-form__field :deep(.v-input__details),
.case-form__field :deep(.v-field__input) {
  color: var(--color-text);
}

.case-form__field :deep(.v-chip) {
  border-radius: var(--radius-pill);
  background: var(--color-accent-soft);
  color: var(--color-accent);
}

@media (min-width: 960px) {
  .case-form {
    padding: var(--space-7);
  }

  .case-form__header {
    grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr);
    align-items: end;
  }

  .case-form__fields--double {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 599px) {
  .case-form {
    padding: var(--space-4);
  }

  .case-form__section {
    padding: var(--space-4);
  }

  .case-form__submit {
    width: 100%;
  }
}
</style>
