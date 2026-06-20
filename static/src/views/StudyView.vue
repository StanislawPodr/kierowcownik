<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  fetchCategoryMeta,
  fetchSequentialQuestion,
  type CategoryMeta,
} from '../api/questions'
import StudyQuestionCard from '../components/StudyQuestionCard.vue'
import { useMarkedQuestions } from '../composables/useMarkedQuestions'
import type { Question } from '../utils/question'

type Screen = 'loading' | 'ready' | 'empty' | 'error'
type TypeFilter = 'all' | 'basic' | 'specialist'
type MarkedFilter = 'all' | 'markedOnly'

const route = useRoute()
const cat = computed(() => String(route.params.cat))

const screen = ref<Screen>('loading')
const errorMsg = ref('')
const meta = ref<CategoryMeta | null>(null)
const currentQuestion = ref<Question | null>(null)
const offset = ref(0)
const total = ref(0)

const typeFilter = ref<TypeFilter>('all')
const markedFilter = ref<MarkedFilter>('all')
const pointsFilter = ref<number | 'all'>('all')

const { marked, isMarked, toggle } = useMarkedQuestions(cat.value)

const markedCount = computed(() => marked.value.size)

function buildFilters() {
  const filters: { type?: 'basic' | 'specialist'; points?: number; ids?: number[] } = {}
  if (typeFilter.value !== 'all') filters.type = typeFilter.value
  if (pointsFilter.value !== 'all') filters.points = pointsFilter.value
  if (markedFilter.value === 'markedOnly') filters.ids = Array.from(marked.value)
  return filters
}


async function loadAt(targetOffset: number) {
  screen.value = 'loading'
  errorMsg.value = ''


  if (markedFilter.value === 'markedOnly' && marked.value.size === 0) {
    total.value = 0
    currentQuestion.value = null
    offset.value = 0
    screen.value = 'empty'
    return
  }

  try {
    const res = await fetchSequentialQuestion(cat.value, Math.max(0, targetOffset), buildFilters())
    total.value = res.total

    if (res.total === 0) {
      currentQuestion.value = null
      offset.value = 0
      screen.value = 'empty'
      return
    }

    if (res.question === null) {
      await loadAt(res.total - 1)
      return
    }

    currentQuestion.value = res.question
    offset.value = res.offset
    screen.value = 'ready'
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Błąd'
    screen.value = 'error'
  }
}

async function loadMeta() {
  try {
    meta.value = await fetchCategoryMeta(cat.value)
  } catch {
    meta.value = null
  }
}

function goPrev() {
  if (offset.value > 0) loadAt(offset.value - 1)
}

function goNext() {
  if (offset.value < total.value - 1) loadAt(offset.value + 1)
}

watch([typeFilter, pointsFilter, markedFilter], () => {
  loadAt(0)
})

function onToggleMarked(id: number) {
  toggle(id)
  if (markedFilter.value === 'markedOnly') {
    loadAt(offset.value)
  }
}

onMounted(() => {
  loadMeta()
  loadAt(0)
})
</script>

<template>
  <div class="study-view">
    <header class="study-header">
      <h1>Tryb nauki — {{ cat }}</h1>
      <router-link to="/" class="menu-back">Wróć do menu</router-link>
    </header>

    <div class="filters">
      <div class="filter-group">
        <span class="filter-label">Rodzaj:</span>
        <button type="button" class="filter-btn" :class="{ active: typeFilter === 'all' }" @click="typeFilter = 'all'">
          Wszystkie
        </button>
        <button type="button" class="filter-btn" :class="{ active: typeFilter === 'basic' }" @click="typeFilter = 'basic'">
          Podstawowe{{ meta ? ` (${meta.basic_count})` : '' }}
        </button>
        <button type="button" class="filter-btn" :class="{ active: typeFilter === 'specialist' }" @click="typeFilter = 'specialist'">
          Specjalistyczne{{ meta ? ` (${meta.specialist_count})` : '' }}
        </button>
      </div>

      <div class="filter-group" v-if="meta && meta.points.length">
        <span class="filter-label">Punkty:</span>
        <button type="button" class="filter-btn" :class="{ active: pointsFilter === 'all' }" @click="pointsFilter = 'all'">
          Wszystkie
        </button>
        <button
          v-for="p in meta.points"
          :key="p"
          type="button"
          class="filter-btn"
          :class="{ active: pointsFilter === p }"
          @click="pointsFilter = p"
        >
          {{ p }} pkt
        </button>
      </div>

      <div class="filter-group">
        <span class="filter-label">Status:</span>
        <button type="button" class="filter-btn" :class="{ active: markedFilter === 'all' }" @click="markedFilter = 'all'">
          Wszystkie
        </button>
        <button
          type="button"
          class="filter-btn filter-btn--marked"
          :class="{ active: markedFilter === 'markedOnly' }"
          @click="markedFilter = 'markedOnly'"
        >
          Wymagające nauki ({{ markedCount }})
        </button>
      </div>
    </div>

    <p v-if="screen === 'loading'" class="status">Ładowanie pytania…</p>

    <section v-else-if="screen === 'error'" class="screen">
      <p class="error">{{ errorMsg }}</p>
      <div class="actions" style="justify-content: flex-start">
        <button type="button" @click="loadAt(offset)">Spróbuj ponownie</button>
        <router-link to="/" class="menu-back">Wróć do menu</router-link>
      </div>
    </section>

    <p v-else-if="screen === 'empty'" class="status">
      Brak pytań spełniających wybrane filtry.
    </p>

    <template v-else-if="currentQuestion">
      <p class="results-count">Pytanie {{ offset + 1 }} z {{ total }}</p>

      <StudyQuestionCard
        :key="currentQuestion.id"
        :question="currentQuestion"
        :index="offset"
        :total="total"
        :marked="isMarked(currentQuestion.id)"
        @toggle-marked="onToggleMarked"
      />

      <div class="nav-bar">
        <button type="button" class="nav-btn" :disabled="offset === 0" @click="goPrev">
          ← Poprzednie
        </button>
        <span class="nav-position">{{ offset + 1 }} / {{ total }}</span>
        <button type="button" class="nav-btn" :disabled="offset >= total - 1" @click="goNext">
          Następne →
        </button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.study-view {
  min-height: 100vh;
  width: 100%;
  padding: 2rem;
  box-sizing: border-box;
  font-family: Arial, sans-serif;
}
 
.study-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
 
.study-header h1 {
  color: #000000;
  font-size: 2.2rem;
  margin: 0;
}
 
.menu-back {
  color: #fff;
  background-color: #b71c1c;
  text-decoration: none;
  padding: 10px 18px;
  border-radius: 8px;
  font-weight: bold;
}
 
.filters {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  background-color: rgba(255, 255, 255, 0.92);
  border-radius: 10px;
  padding: 1rem 1.25rem;
  margin-bottom: 1.25rem;
  max-width: 900px;
}
 
.filter-group {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}
 
.filter-label {
  font-weight: bold;
  margin-right: 0.5rem;
  color: #333;
}
 
.filter-btn {
  border: 2px solid #b71c1c;
  background-color: transparent;
  color: #b71c1c;
  border-radius: 16px;
  padding: 6px 14px;
  font-weight: bold;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.15s ease, color 0.15s ease;
}
 
.filter-btn:hover {
  background-color: #f0d4d4;
}
 
.filter-btn.active {
  background-color: #e53935;
  color: #fff;
  border-color: #e53935;
}
 
.filter-btn--marked.active {
  background-color: #b71c1c;
  border-color: #b71c1c;
}
 
.results-count {
  color: #333;
  margin-bottom: 1rem;
}
 
.nav-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 1.5rem;
  max-width: 900px;
}
 
.nav-btn {
  background-color: #e53935;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 14px 28px;
  font-weight: bold;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background-color 0.15s ease, transform 0.1s ease;
}
 
.nav-btn:hover:not(:disabled) {
  background-color: #b71c1c;
}
 
.nav-btn:active:not(:disabled) {
  transform: translateY(2px);
}
 
.nav-btn:disabled {
  background-color: #9e9e9e;
  cursor: not-allowed;
  opacity: 0.6;
}
 
.nav-position {
  color: #333;
  font-weight: bold;
  font-size: 1.1rem;
  min-width: 80px;
  text-align: center;
}

</style>