<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { submitExamAttempt } from '../api/examAttempts'
import { fetchWordExam } from '../api/questions'
import ExamResult from '../components/ExamResult.vue'
import QuestionCard from '../components/QuestionCard.vue'
import { useUserProgress } from '../composables/useUserProgress'
import { calculateScore } from '../utils/examScore'
import type { AnswerChoice, Question } from '../utils/question'
import {useRoute} from "vue-router";

type Screen = 'loading' | 'exam' | 'result' | 'error'

const screen = ref<Screen>('loading')
const errorMsg = ref('')
const questions = ref<Question[]>([])
const answers = ref<(AnswerChoice | null)[]>([])
const index = ref(0)
const route = useRoute()
const { isMarked, toggleMarked, markAsWrong, removeFromWrong, markAsSeen, saveProgress } = useUserProgress()

const result = computed(() =>
  screen.value === 'result' ? calculateScore(questions.value, answers.value) : null,
)

async function startExam() {
  screen.value = 'loading'
  errorMsg.value = ''
  try {
    const data = await fetchWordExam(route.params.cat)
    if (!data.questions.length) throw new Error('Brak pytań w bazie')
    questions.value = data.questions
    answers.value = data.questions.map(() => null)
    index.value = 0
    screen.value = 'exam'
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Błąd'
    screen.value = 'error'
  }
}

function onNext() {
  if (index.value >= questions.value.length - 1) {
    finishExam()
    return
  }
  index.value += 1
}

async function finishExam() {
  questions.value.forEach((q, i) => {
    const ans = answers.value[i]
    if (ans !== null) {
      markAsSeen(q.id)
      const correct = String(ans).toUpperCase() === String(q.correct_answer).trim().toUpperCase()
      if (correct) {
        removeFromWrong(q.id)
      } else {
        markAsWrong(q.id)
      }
    }
  })

  await saveProgress()

  const examResult = calculateScore(questions.value, answers.value)
  if (localStorage.getItem('access_token')) {
    submitExamAttempt({
      category: String(route.params.cat),
      score: examResult.score,
      max_score: examResult.maxScore,
      passed: examResult.passed,
    }).catch(() => {})
  }

  screen.value = 'result'
}

function setAnswer(value: AnswerChoice) {
  answers.value[index.value] = value
}

onMounted(() => {
  startExam()
})
</script>

<template>
  <p v-if="screen === 'loading'" class="status">Ładowanie pytań…</p>

  <section v-else-if="screen === 'error'" class="screen">
    <p class="error">{{ errorMsg }}</p>
    <div class="actions" style="justify-content: flex-start">
      <button type="button" @click="startExam">Spróbuj ponownie</button>
      <router-link to="/" class="menu-back">Wróć do menu</router-link>
    </div>
  </section>

  <ExamResult
    v-else-if="screen === 'result' && result"
    :result="result"
    :questions="questions"
    :answers="answers"
    @restart="startExam"
  />

  <QuestionCard
    v-else-if="screen === 'exam'"
    :key="questions[index].id"
    :question="questions[index]"
    :index="index"
    :total="questions.length"
    :model-value="answers[index]"
    :marked="isMarked(questions[index].id)"
    @toggle-marked="toggleMarked"
    @update:model-value="setAnswer"
    @next="onNext"
  />
</template>
