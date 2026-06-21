<script setup lang="ts">
import { ref } from 'vue'
import { useUserProgress } from '../composables/useUserProgress'
import type { ExamScore } from '../utils/examScore'
import { getAnswerStatus, type AnswerChoice, type Question } from '../utils/question'
import QuestionReviewCard from './QuestionReviewCard.vue'

defineProps<{
  result: ExamScore
  questions: Question[]
  answers: (AnswerChoice | null)[]
}>()

const emit = defineEmits<{
  restart: []
}>()

const selectedIndex = ref<number | null>(null)
const { isMarked, toggleMarked, saveProgress } = useUserProgress()

function selectQuestion(index: number) {
  selectedIndex.value = selectedIndex.value === index ? null : index
}

async function onToggleMarked(id: number) {
  toggleMarked(id)
  await saveProgress()
}
</script>

<template>
  <section class="screen screen--result">
    <header class="result-header">
      <h1>Podsumowanie egzaminu</h1>
      <p :class="result.passed ? 'result-pass' : 'result-fail'">
        {{ result.passed ? 'Egzamin zdany' : 'Egzamin niezdany' }}
      </p>
      <div class="result-percent">{{ result.percent }}%</div>
      <p class="result-detail">{{ result.score }} / {{ result.maxScore }} pkt</p>
      <p class="result-detail">Próg zaliczenia: 68 pkt ({{ result.passPercent }}%)</p>
    </header>

    <div class="result-legend">
      <span class="result-legend-item result-legend-item--correct">Poprawna</span>
      <span class="result-legend-item result-legend-item--wrong">Błędna</span>
      <span class="result-legend-item result-legend-item--unanswered">Bez odpowiedzi</span>
    </div>

    <ul class="result-list">
      <li
        v-for="(question, i) in questions"
        :key="question.id"
        class="result-item"
        :class="[
          `result-item--${getAnswerStatus(question, answers[i])}`,
          { 'result-item--selected': selectedIndex === i, 'result-item--marked': isMarked(question.id) },
        ]"
      >
        <button type="button" class="result-item-btn" @click="selectQuestion(i)">
          <span class="result-item-num">{{ i + 1 }}.</span>
          <span class="result-item-text">{{ question.question_text }}</span>
        </button>
      </li>
    </ul>

    <QuestionReviewCard
      v-if="selectedIndex !== null"
      :question="questions[selectedIndex]"
      :index="selectedIndex"
      :user-answer="answers[selectedIndex]"
      :marked="isMarked(questions[selectedIndex].id)"
      @toggle-marked="onToggleMarked"
    />

    <div class="actions">
      <button type="button" class="primary" @click="emit('restart')">Rozpocznij ponownie</button>
      <router-link to="/" class="menu-back">Wróć do menu</router-link>
    </div>
  </section>
</template>
