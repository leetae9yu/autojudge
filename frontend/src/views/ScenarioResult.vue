<script setup lang="ts">
import { useRouter } from 'vue-router'

import ScenarioCard from '../components/ScenarioCard.vue'
import type { ScenarioCardItem } from '../types/scenario'

const props = withDefaults(
  defineProps<{
    id?: string
  }>(),
  {
    id: 'case-sample-001',
  },
)

const router = useRouter()

const scenarioResults: ScenarioCardItem[] = [
  {
    id: '01',
    title: '계약상 신뢰보호 위반이 중심이 되는 해석',
    interpretation:
      '계약 성립 직전의 확정적 약속, 이후 이행 거절, 상대방의 선행 지출이 함께 확인되면 신뢰이익 보호 관점에서 손해배상 책임이 폭넓게 인정될 수 있습니다.',
    probability: 'high',
    basis: [
      {
        id: 'law-390',
        type: '법령',
        label: '채무불이행 손해배상 일반 원칙',
        citation: '민법 제390조',
        summary:
          '채무자가 채무 내용에 좇은 이행을 하지 않으면 손해배상 책임이 발생한다는 기본 원칙입니다.',
      },
      {
        id: 'law-393',
        type: '법령',
        label: '손해배상 범위와 예견 가능성',
        citation: '민법 제393조',
        summary:
          '통상손해를 기본으로 하되 특별손해는 예견 가능성이 입증될 때만 포함됩니다.',
      },
      {
        id: 'prec-2013da218156',
        type: '판례',
        label: '교섭 단계 신뢰이익 보호 흐름',
        citation: '대법원 2013다218156',
        summary:
          '상대방이 정당한 신뢰를 형성한 경우 손해배상 책임이 문제될 수 있음을 보여줍니다.',
      },
    ],
    keyFactors: [
      '확정적 표현이 반복된 메시지 기록 존재',
      '상대방이 약속을 전제로 비용을 먼저 집행함',
      '변경 통지가 늦어 손해 확대를 막기 어려웠음',
    ],
  },
  {
    id: '02',
    title: '손해액 입증 부족으로 일부만 인정되는 해석',
    interpretation:
      '불이행 자체는 인정되더라도 실제 손해액과 인과관계를 뒷받침할 자료가 제한적이면 법원은 일부 항목만 받아들이고 청구 범위를 축소할 가능성이 있습니다.',
    probability: 'medium',
    basis: [
      {
        id: 'law-288',
        type: '법령',
        label: '증명책임의 기본 원칙',
        citation: '민사소송법 제288조',
        summary:
          '자신에게 유리한 사실은 당사자가 주장·입증해야 하며 손해 범위도 이에 포함됩니다.',
      },
      {
        id: 'prec-2017da242273',
        type: '판례',
        label: '손해액 증명 수준에 관한 판단',
        citation: '대법원 2017다242273',
        summary:
          '손해 발생 개연성만으로는 부족하고 항목별 입증 수준에 따라 인정 범위가 달라질 수 있음을 보여줍니다.',
      },
      {
        id: 'prec-2014da231378',
        type: '판례',
        label: '상당인과관계 심사',
        citation: '대법원 2014다231378',
        summary:
          '채무불이행과 손해 사이의 상당인과관계는 개별 사정에 따라 엄격하게 심사됩니다.',
      },
    ],
    keyFactors: [
      '영수증과 계좌기록이 일부만 확보됨',
      '손해 발생 시점과 위반 시점의 연결이 약함',
      '대체 거래 가능성에 대한 반론 여지가 존재함',
    ],
  },
  {
    id: '03',
    title: '원고 과실이 반영되어 책임이 제한되는 해석',
    interpretation:
      '상대방의 위반이 존재하더라도 원고의 대응 지연, 확인 절차 미비, 손해 확대 방지 노력 부족이 확인되면 과실상계나 책임 제한 논리가 강하게 작동할 수 있습니다.',
    probability: 'low',
    basis: [
      {
        id: 'law-396',
        type: '법령',
        label: '과실상계 규정',
        citation: '민법 제396조',
        summary:
          '채권자에게 과실이 있으면 손해배상액을 정할 때 이를 참작해 책임이 제한될 수 있습니다.',
      },
      {
        id: 'prec-2018da248855',
        type: '판례',
        label: '손해 확대 방지 의무 관련 판단',
        citation: '대법원 2018다248855',
        summary:
          '피해자가 손해 확대를 줄일 수 있었는지 여부가 배상 범위 판단에 반영될 수 있습니다.',
      },
      {
        id: 'prec-2011da101315',
        type: '판례',
        label: '상호 책임 제한 사례',
        citation: '대법원 2011다101315',
        summary:
          '계약 관계에서 양 당사자의 행위가 함께 손해를 유발한 경우 책임 비율이 조정될 수 있습니다.',
      },
    ],
    keyFactors: [
      '계약 조건 재확인 없이 선이행을 택한 정황',
      '분쟁 이후 손해 확산 방지 조치가 늦었음',
      '상대방에게 시정 기회를 충분히 주지 않았다는 반론 가능',
    ],
  },
]

async function moveToWhatIf(scenarioId: string) {
  await router.push({
    name: 'whatif',
    params: {
      id: props.id,
    },
    query: {
      scenario: scenarioId,
    },
  })
}

void [ScenarioCard, scenarioResults, moveToWhatIf]
</script>

<template>
  <section class="scenario-result-page page-shell">
    <div class="scenario-result-page__hero">
      <div class="scenario-result-page__copy">
        <p class="scenario-result-page__eyebrow">AutoJudge scenario briefing</p>
        <h1 class="scenario-result-page__title">현재 입력 사건에 대한 가능한 법적 해석 Top 3</h1>
        <p class="scenario-result-page__description">
          동일한 사실관계도 증거의 밀도와 책임 제한 요소에 따라 다른 결론으로 읽힐 수 있습니다.
          아래 카드는 현재 사건 ID {{ props.id }} 기준으로 정리한 우선 시나리오입니다.
        </p>
      </div>

      <v-alert class="scenario-result-page__disclaimer" density="comfortable" type="warning" variant="tonal">
        <template #title>법률 자문 아님</template>
        이 결과는 참고용 법적 해석 시뮬레이션입니다. 실제 소송 전략 수립이나 법률 판단은 변호사와의
        상담을 통해 진행해야 합니다.
      </v-alert>
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
        <strong>법령·판례 인용 기반</strong>
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
