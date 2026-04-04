<script setup lang="ts">
import { useRouter } from 'vue-router'

import CaseForm from '../components/CaseForm.vue'
import { type CaseRecord, useCaseStore } from '../stores/case'

const router = useRouter()
const caseStore = useCaseStore()

async function handleSubmitted(createdCase: CaseRecord) {
  await router.push({
    name: 'result',
    query: {
      caseId: createdCase.id,
    },
  })

  caseStore.resetForm()
}

void [CaseForm, handleSubmitted]
</script>

<template>
  <section class="case-input-page">
    <div class="case-input-page__hero">
      <div class="case-input-page__copy">
        <p class="case-input-page__eyebrow">AutoJudge intake console</p>
        <h1 class="case-input-page__title">민사 사건을 정제된 입력으로 바꿔 시뮬레이션의 출발점을 만듭니다.</h1>
        <p class="case-input-page__description">
          손해배상, 계약위반, 부당이득 사건을 구조화해 등록하면 이후 검색, 시나리오 생성, What-If
          분석으로 자연스럽게 이어집니다.
        </p>
      </div>

      <div class="case-input-page__meta">
        <div class="case-input-page__badge">
          <span>필수 입력</span>
          <strong>5 fields</strong>
        </div>
        <div class="case-input-page__badge">
          <span>제출 흐름</span>
          <strong>POST /api/cases</strong>
        </div>
      </div>
    </div>

    <CaseForm @submitted="handleSubmitted" />
  </section>
</template>

<style scoped>
.case-input-page {
  display: grid;
  gap: var(--space-6);
}

.case-input-page__hero {
  display: grid;
  gap: var(--space-5);
}

.case-input-page__copy {
  display: grid;
  gap: var(--space-4);
}

.case-input-page__eyebrow {
  font-size: 0.875rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--color-accent);
}

.case-input-page__title {
  max-width: 56rem;
  font-family: var(--font-display);
  font-size: clamp(2.75rem, 6vw, 5.25rem);
  line-height: var(--line-height-tight);
  color: var(--color-heading);
}

.case-input-page__description {
  max-width: 42rem;
  font-size: 1.0625rem;
  color: var(--color-text-muted);
}

.case-input-page__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
}

.case-input-page__badge {
  display: grid;
  gap: var(--space-1);
  min-width: 11rem;
  padding: var(--space-4);
  border: var(--border-thin) solid var(--color-border);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.45);
  box-shadow: var(--shadow-soft);
  backdrop-filter: blur(16px);
}

.case-input-page__badge span {
  font-size: 0.875rem;
  color: var(--color-text-muted);
}

.case-input-page__badge strong {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-heading);
}

@media (min-width: 960px) {
  .case-input-page__hero {
    grid-template-columns: minmax(0, 1.8fr) minmax(0, 0.9fr);
    align-items: end;
  }

  .case-input-page__meta {
    justify-content: end;
  }
}
</style>
