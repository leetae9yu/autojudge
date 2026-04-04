<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <v-app>
    <v-main class="app-main">
      <v-container fluid class="app-shell">
        <RouterView />
      </v-container>
    </v-main>
  </v-app>
</template>
