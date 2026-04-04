<script setup lang="ts">
import { RouterView } from 'vue-router'

void RouterView
</script>

<template>
  <v-app>
    <v-main class="app-main">
      <v-container fluid class="app-shell">
        <v-alert class="app-disclaimer" density="comfortable" type="warning" variant="tonal">
          본 서비스는 법률 자문을 제공하지 않습니다. 생성된 시나리오는 참고용이며, 실제 법적 결정은
          반드시 변호사와 상담하십시오.
        </v-alert>
        <RouterView />
      </v-container>
    </v-main>
  </v-app>
</template>

<style scoped>
.app-shell {
  display: grid;
  gap: var(--space-4);
}

.app-disclaimer {
  border: var(--border-thin) solid color-mix(in srgb, var(--color-warning) 32%, transparent);
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--color-warning) 14%, var(--color-surface));
  box-shadow: var(--shadow-soft);
}
</style>
