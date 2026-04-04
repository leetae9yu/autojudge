<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import ScenarioCard from '../components/ScenarioCard.vue'
import type { ScenarioCardItem } from '../types/scenario'
import { getCase } from '@/api/cases'
import { createScenarios, type ScenarioItem } from '@/api/scenarios'

const props = withDefaults(
  defineProps<{
    id?: string
  }>(),
  {
    id: 'case-sample-001',
  },
)

const router = useRouter()
const loading = ref(false)
const errorMessage = ref('')
const scenarioResults = ref<ScenarioCardItem[]>([])

watch(
  () => props.id,
  async id => {
    errorMessage.value = ''
    scenarioResults.value = []

    if (!id) {
      return
    }

    loading.value = true

    try {
      const caseRecord = await getCase(id)
      const result = await createScenarios({ case_id: caseRecord.id, count: 3 })
      scenarioResults.value = result.scenarios.map((scenario, index) => toScenarioCardItem(scenario, index))
    } catch (error) {
      errorMessage.value = error instanceof Error ? error.message : '시나리오를 불러오지 못했습니다.'
    } finally {
      loading.value = false
    }
  },
  { immediate: true },
)

async function moveToWhatIf(scenarioId: string) {
  await router.push({
    name: 'whatif',
    params: { id: props.id },
    query: { scenario: scenarioId },
  })
}

function toScenarioCardItem(scenario: ScenarioItem, index: number): ScenarioCardItem {
  return {
    id: String(index + 1).padStart(2, '0'),
    title: scenario.title,
    interpretation: scenario.interpretation,
    probability: scenario.probability,
    keyFactors: scenario.key_factors,
    basis: scenario.basis.map((citation, citationIndex) => parseAuthority(citation, citationIndex)),
  }
}

function parseAuthority(citation: string, index: number): ScenarioCardItem['basis'][number] {
  const match = citation.match(/^\[(?<type>[^\]]+)\]\s*(?<identifier>.+?)\s*-\s*(?<title>.+)$/)
  const type: ScenarioCardItem['basis'][number]['type'] =
    match?.groups?.type === '판례' ? '판례' : '법령'
  const identifier = match?.groups?.identifier?.trim() || citation
  const title = match?.groups?.title?.trim() || citation

  return {
    id: `${index}-${citation}`,
    type,
    label: title,
    citation: identifier,
    summary: citation,
  }
}
</script>

<template>
  <section class="scenario-result-page page-shell">
    <v-alert v-if="errorMessage" class="scenario-result-page__disclaimer" density="comfortable" type="error" variant="tonal">
      {{ errorMessage }}
    </v-alert>

    <v-skeleton-loader v-if="loading" type="article, article, article" />

    <template v-else>
      <v-alert class="scenario-result-page__disclaimer" density="comfortable" type="warning" variant="tonal">
        본 서비스는 법률 자문을 제공하지 않습니다. 생성된 시나리오는 참고용이며, 실제 법적 결정은
        반드시 변호사와 상담하십시오.
      </v-alert>

      <div class="scenario-result-page__hero">
        <div class="scenario-result-page__copy">
          <p class="scenario-result-page__eyebrow">AutoJudge scenario briefing</p>
          <h1 class="scenario-result-page__title">현재 입력 사건에 대한 가능한 법적 해석 Top 3</h1>
          <p class="scenario-result-page__description">
            동일한 사실관계도 증거의 밀도와 책임 제한 요소에 따라 다른 결론으로 읽힐 수 있습니다.
            아래 카드는 현재 사건 ID {{ props.id }} 기준으로 정리한 우선 시나리오입니다.
          </p>
        </div>
      </div>

      <div class="scenario-result-page__summary-grid">
        <article class="scenario-result-page__summary-card">
          <span>사건 ID</span>
          <strong>{{ props.id }}</strong>
        </article>
        <article class="scenario-result-page__summary-card">
          <span>출력 형식</span>
          <strong>Top3 legal interpretations</strong>
        </article>
        <article class="scenario-result-page__summary-card">
          <span>근거 원칙</span>
          <strong>{{ scenarioResults.length > 0 ? '법령·판례 인용 기반' : '시나리오 생성 대기 중' }}</strong>
        </article>
      </div>

      <div class="scenario-result-page__grid">
        <ScenarioCard
          v-for="scenario in scenarioResults"
          :key="scenario.id"
          :scenario="scenario"
          @what-if="moveToWhatIf"
        />
      </div>
    </template>
  </section>
</template>

<style scoped>
.scenario-result-page {
  display: grid;
  gap: var(--space-6);
}

.scenario-result-page__hero {
  display: grid;
  gap: var(--space-5);
}

.scenario-result-page__copy {
  display: grid;
  gap: var(--space-4);
}

.scenario-result-page__eyebrow {
  font-size: 0.875rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--color-accent);
}

.scenario-result-page__title {
  max-width: 56rem;
  font-family: var(--font-display);
  font-size: clamp(2.75rem, 6vw, 5rem);
  line-height: var(--line-height-tight);
  color: var(--color-heading);
}

.scenario-result-page__description {
  max-width: 44rem;
  font-size: 1.0625rem;
  color: var(--color-text-muted);
}

.scenario-result-page__disclaimer {
  border: var(--border-thin) solid color-mix(in srgb, var(--color-warning) 28%, transparent);
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--color-warning) 12%, var(--color-surface));
  box-shadow: var(--shadow-soft);
}

.scenario-result-page__summary-grid {
  display: grid;
  gap: var(--space-3);
}

.scenario-result-page__summary-card {
  display: grid;
  gap: var(--space-1);
  padding: var(--space-4);
  border: var(--border-thin) solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  box-shadow: var(--shadow-soft);
}

.scenario-result-page__summary-card span {
  font-size: 0.875rem;
  color: var(--color-text-muted);
}

.scenario-result-page__summary-card strong {
  color: var(--color-heading);
  font-size: 1rem;
}

.scenario-result-page__grid {
  display: grid;
  gap: var(--space-4);
}

@media (min-width: 960px) {
  .scenario-result-page__hero {
    grid-template-columns: minmax(0, 1.8fr) minmax(0, 1fr);
    align-items: end;
  }

  .scenario-result-page__summary-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .scenario-result-page__grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    align-items: stretch;
  }
}
</style>
