<script setup lang="ts">
import type { ExamScore } from '../utils/examScore'

defineProps<{
  result: ExamScore
}>()

const emit = defineEmits<{
  restart: []
}>()
</script>

<template>
  <section class="screen">
    <h1>Podsumowanie egzaminu</h1>
    <p :class="result.passed ? 'result-pass' : 'result-fail'">
      {{ result.passed ? 'Egzamin zdany' : 'Egzamin niezdany' }}
    </p>
    <div class="result-percent">{{ result.percent }}%</div>
    <p class="result-detail">{{ result.score }} / {{ result.maxScore }} pkt</p>
    <p class="result-detail">Próg zaliczenia: 68 pkt ({{ result.passPercent }}%)</p>
    <div class="actions">
      <button type="button" class="primary" @click="emit('restart')">Rozpocznij ponownie</button>
      <router-link to="/" class="menu-back">Wróć do menu</router-link>
    </div>
  </section>
</template>
