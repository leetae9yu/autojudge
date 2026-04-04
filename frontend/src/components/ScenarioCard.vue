<script setup lang="ts">
import { computed, ref } from 'vue'

import type { ScenarioCardItem } from '../types/scenario'

const props = defineProps<{
  scenario: ScenarioCardItem
}>()

const emit = defineEmits<(event: 'what-if', scenarioId: string) => void>()

const isAuthorityOpen = ref(false)

const probabilityMeta = computed(() => {
  if (props.scenario.probability === 'high') {
    return {
      label: '가능성 높음',
      className: 'scenario-card__probability--high',
    }
  }

  if (props.scenario.probability === 'medium') {
    return {
      label: '가능성 중간',
      className: 'scenario-card__probability--medium',
    }
  }

  return {
    label: '가능성 낮음',
    className: 'scenario-card__probability--low',
  }
})

void [emit, isAuthorityOpen, probabilityMeta]
</script>

<template>
  <v-card class="scenario-card" elevation="0">
    <div class="scenario-card__header">
      <p class="scenario-card__eyebrow">Scenario {{ scenario.id }}</p>
      <div class="scenario-card__title-row">
        <h2 class="scenario-card__title">{{ scenario.title }}</h2>
        <span class="scenario-card__probability" :class="probabilityMeta.className">
          {{ probabilityMeta.label }}
        </span>
      </div>
    </div>

    <section class="scenario-card__section">
      <p class="scenario-card__section-label">법적 해석</p>
      <p class="scenario-card__interpretation">{{ scenario.interpretation }}</p>
    </section>

    <section class="scenario-card__section">
      <div class="scenario-card__section-heading">
        <p class="scenario-card__section-label">근거</p>
        <button class="scenario-card__link" type="button" @click="isAuthorityOpen = true">
          관련 법령·판례 보기
        </button>
      </div>

      <div class="scenario-card__chip-wrap">
        <button
          v-for="authority in scenario.basis"
          :key="authority.id"
          class="scenario-card__chip"
          type="button"
          @click="isAuthorityOpen = true"
        >
          <span class="scenario-card__chip-type">{{ authority.type }}</span>
          <span>{{ authority.citation }}</span>
        </button>
      </div>
    </section>

    <section class="scenario-card__section">
      <p class="scenario-card__section-label">핵심 변수</p>
      <ul class="scenario-card__factor-list">
        <li v-for="factor in scenario.keyFactors" :key="factor">{{ factor }}</li>
      </ul>
    </section>

    <div class="scenario-card__actions">
      <button class="scenario-card__button scenario-card__button--secondary" type="button" @click="isAuthorityOpen = true">
        상세 근거
      </button>
      <v-btn class="scenario-card__button scenario-card__button--primary" size="large" @click="emit('what-if', scenario.id)">
        What-If
      </v-btn>
    </div>
  </v-card>

  <div v-if="isAuthorityOpen" class="scenario-card__dialog-backdrop" @click.self="isAuthorityOpen = false">
    <section class="scenario-card__dialog" role="dialog" aria-modal="true">
      <div class="scenario-card__dialog-header">
        <div>
          <p class="scenario-card__section-label">관련 법령·판례</p>
          <h3 class="scenario-card__dialog-title">{{ scenario.title }}</h3>
        </div>
        <button class="scenario-card__close" type="button" @click="isAuthorityOpen = false">
          닫기
        </button>
      </div>

      <div class="scenario-card__authority-list">
        <article v-for="authority in scenario.basis" :key="authority.id" class="scenario-card__authority-item">
          <div class="scenario-card__authority-meta">
            <span class="scenario-card__chip-type">{{ authority.type }}</span>
            <strong>{{ authority.citation }}</strong>
          </div>
          <p class="scenario-card__authority-label">{{ authority.label }}</p>
          <p class="scenario-card__authority-summary">{{ authority.summary }}</p>
        </article>
      </div>
    </section>
  </div>
</template>

<style scoped>
.scenario-card {
  display: grid;
  gap: var(--space-5);
  height: 100%;
  padding: var(--space-5);
  border: var(--border-thin) solid var(--color-border);
  border-radius: var(--radius-lg);
  background:
    linear-gradient(160deg, rgba(255, 255, 255, 0.42), transparent 45%),
    var(--color-surface);
  box-shadow: var(--shadow-soft);
  backdrop-filter: blur(16px);
}

.scenario-card__header,
.scenario-card__section,
.scenario-card__actions {
  display: grid;
  gap: var(--space-3);
}

.scenario-card__eyebrow,
.scenario-card__section-label {
  font-size: 0.875rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.scenario-card__eyebrow {
  color: var(--color-highlight);
}

.scenario-card__section-label {
  color: var(--color-text-muted);
}

.scenario-card__title-row,
.scenario-card__section-heading,
.scenario-card__actions,
.scenario-card__dialog-header,
.scenario-card__authority-meta {
  display: flex;
  gap: var(--space-3);
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
}

.scenario-card__title {
  font-family: var(--font-display);
  font-size: clamp(1.5rem, 3vw, 2rem);
  line-height: var(--line-height-tight);
  color: var(--color-heading);
  max-width: 20rem;
}

.scenario-card__probability {
  padding: 0.625rem 0.875rem;
  border-radius: var(--radius-pill);
  border: var(--border-thin) solid transparent;
  font-size: 0.875rem;
  font-weight: 700;
  white-space: nowrap;
}

.scenario-card__probability--high {
  color: var(--color-success);
  background: color-mix(in srgb, var(--color-success) 12%, var(--color-surface-strong));
  border-color: color-mix(in srgb, var(--color-success) 24%, transparent);
}

.scenario-card__probability--medium {
  color: var(--color-warning);
  background: color-mix(in srgb, var(--color-warning) 12%, var(--color-surface-strong));
  border-color: color-mix(in srgb, var(--color-warning) 24%, transparent);
}

.scenario-card__probability--low {
  color: var(--color-danger);
  background: color-mix(in srgb, var(--color-danger) 12%, var(--color-surface-strong));
  border-color: color-mix(in srgb, var(--color-danger) 24%, transparent);
}

.scenario-card__interpretation {
  color: var(--color-heading);
  font-size: 1rem;
}

.scenario-card__link,
.scenario-card__chip,
.scenario-card__close,
.scenario-card__button--secondary {
  border: none;
  background: transparent;
  cursor: pointer;
  color: inherit;
}

.scenario-card__link,
.scenario-card__close {
  color: var(--color-accent);
  font-weight: 700;
}

.scenario-card__chip-wrap,
.scenario-card__factor-list,
.scenario-card__authority-list {
  display: grid;
  gap: var(--space-3);
}

.scenario-card__chip-wrap {
  display: flex;
  flex-wrap: wrap;
}

.scenario-card__chip {
  display: inline-flex;
  gap: var(--space-2);
  align-items: center;
  padding: 0.625rem 0.875rem;
  border: var(--border-thin) solid var(--color-border);
  border-radius: var(--radius-pill);
  background: var(--color-surface-strong);
  transition:
    transform 180ms ease,
    border-color 180ms ease,
    box-shadow 180ms ease;
}

.scenario-card__chip:hover,
.scenario-card__button--secondary:hover,
.scenario-card__close:hover,
.scenario-card__link:hover {
  transform: translateY(-2px);
}

.scenario-card__chip:hover {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-soft);
}

.scenario-card__chip-type {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 3rem;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-pill);
  background: var(--color-accent-soft);
  color: var(--color-accent);
  font-size: 0.75rem;
  font-weight: 700;
}

.scenario-card__factor-list {
  padding-left: 1.25rem;
}

.scenario-card__factor-list li::marker {
  color: var(--color-highlight);
}

.scenario-card__actions {
  margin-top: auto;
}

.scenario-card__button {
  min-width: 8.5rem;
  border-radius: var(--radius-pill);
}

.scenario-card__button--secondary {
  padding: 0.875rem 1.125rem;
  border: var(--border-thin) solid var(--color-border-strong);
  border-radius: var(--radius-pill);
  font-weight: 700;
}

.scenario-card__button--primary {
  background: linear-gradient(135deg, var(--color-accent), var(--color-highlight));
  color: var(--color-surface-strong);
}

.scenario-card__dialog-backdrop {
  position: fixed;
  inset: 0;
  z-index: 20;
  display: grid;
  place-items: center;
  padding: var(--space-4);
  background: rgba(10, 14, 18, 0.56);
  backdrop-filter: blur(6px);
}

.scenario-card__dialog {
  width: min(100%, 42rem);
  display: grid;
  gap: var(--space-4);
  padding: var(--space-5);
  border: var(--border-thin) solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-surface-strong);
  box-shadow: var(--shadow-strong);
}

.scenario-card__dialog-title {
  font-family: var(--font-display);
  font-size: clamp(1.5rem, 2.5vw, 2rem);
  line-height: var(--line-height-tight);
  color: var(--color-heading);
}

.scenario-card__authority-item {
  display: grid;
  gap: var(--space-2);
  padding: var(--space-4);
  border: var(--border-thin) solid var(--color-border);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.42);
}

.scenario-card__authority-label {
  color: var(--color-heading);
  font-weight: 700;
}

.scenario-card__authority-summary {
  color: var(--color-text-muted);
}

@media (max-width: 599px) {
  .scenario-card {
    padding: var(--space-4);
  }

  .scenario-card__button,
  .scenario-card__button--secondary {
    width: 100%;
  }
}
</style>
