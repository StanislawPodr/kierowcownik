<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  fetchCategoryMeta,
  fetchSequentialQuestion,
  type CategoryMeta,
} from '../api/questions'
import StudyQuestionCard from '../components/StudyQuestionCard.vue'
import { useUserProgress } from '../composables/useUserProgress'
import type { Question } from '../utils/question'

type Screen = 'loading' | 'ready' | 'empty' | 'error'
type TypeFilter = 'all' | 'basic' | 'specialist'
type MarkedFilter = 'all' | 'markedOnly' | 'wrongOnly'

const route = useRoute()
const cat = computed(() => String(route.params.cat))

const screen = ref<Screen>('loading')
const errorMsg = ref('')
const meta = ref<CategoryMeta | null>(null)
const currentQuestion = ref<Question | null>(null)
const offset = ref(0)
const total = ref(0)
const unseenTotal = ref(0)
const nextUnseenOffset = ref<number | null>(null)

const typeFilter = ref<TypeFilter>('all')
const markedFilter = ref<MarkedFilter>('all')
const pointsFilter = ref<number | 'all'>('all')

const isSaving = ref(false)
const saveStatus = ref('')

const {
  wrongQuestions,
  markedQuestions,
  seenQuestions,
  isMarked,
  toggleMarked,
  markAsWrong,
  removeFromWrong,
  markAsSeen,
  saveProgress,
} = useUserProgress()

const isUserLoggedIn = computed(() => !!localStorage.getItem('username'))
const markedCount = computed(() => markedQuestions.value.size)
const wrongCount = computed(() => wrongQuestions.value.size)
const seenCount = computed(() => seenQuestions.value.size)

function buildFilters() {
  const filters: { type?: 'basic' | 'specialist'; points?: number; ids?: number[]; excludeIds?: number[]; statusFilter?: string } = {}
  if (typeFilter.value !== 'all') filters.type = typeFilter.value
  if (pointsFilter.value !== 'all') filters.points = pointsFilter.value
  filters.statusFilter = markedFilter.value
  
  if (markedFilter.value === 'markedOnly') {
    filters.ids = Array.from(markedQuestions.value)
  } else if (markedFilter.value === 'wrongOnly') {
    filters.ids = Array.from(wrongQuestions.value)
  } else {
    filters.excludeIds = Array.from(seenQuestions.value)
  }
  return filters
}

async function loadAt(targetOffset: number) {
  screen.value = 'loading'
  errorMsg.value = ''

  if (markedFilter.value === 'markedOnly' && markedQuestions.value.size === 0) {
    total.value = 0
    unseenTotal.value = 0
    currentQuestion.value = null
    offset.value = 0
    nextUnseenOffset.value = null
    screen.value = 'empty'
    return
  }

  if (markedFilter.value === 'wrongOnly' && wrongQuestions.value.size === 0) {
    total.value = 0
    unseenTotal.value = 0
    currentQuestion.value = null
    offset.value = 0
    nextUnseenOffset.value = null
    screen.value = 'empty'
    return
  }

  try {
    const res = await fetchSequentialQuestion(cat.value, targetOffset, buildFilters())
    total.value = res.total
    unseenTotal.value = res.unseen_total

    // If offset was auto-calculated (-1), get the resolved offset from response
    offset.value = res.offset
    nextUnseenOffset.value = res.next_unseen_offset

    if (res.question === null) {
      currentQuestion.value = null
      screen.value = 'empty'
      return
    }

    currentQuestion.value = res.question
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
  if (offset.value > 0) {
    loadAt(offset.value - 1)
  }
}

function goNext() {
  if (nextUnseenOffset.value !== null) {
    loadAt(nextUnseenOffset.value)
  } else if (offset.value < total.value - 1) {
    // Fallback normal navigation (if not in "all" mode where we skip seen)
    loadAt(offset.value + 1)
  }
}

watch([typeFilter, pointsFilter, markedFilter], () => {
  // Pass -1 to automatically find the first unseen question under new filters
  loadAt(-1)
})

function onToggleMarked(id: number) {
  toggleMarked(id)
  if (markedFilter.value === 'markedOnly') {
    loadAt(offset.value)
  }
}

function onQuestionAnswered({ id, correct }: { id: number; correct: boolean }) {
  markAsSeen(id)
  if (correct) {
    removeFromWrong(id)
  } else {
    markAsWrong(id)
  }
}

async function handleManualSave() {
  isSaving.value = true
  saveStatus.value = 'Zapisywanie...'
  try {
    await saveProgress()
    saveStatus.value = 'Zapisano pomyślnie!'
    setTimeout(() => {
      saveStatus.value = ''
    }, 3000)
  } catch (err) {
    saveStatus.value = 'Błąd zapisu.'
    setTimeout(() => {
      saveStatus.value = ''
    }, 3000)
  } finally {
    isSaving.value = false
  }
}

onMounted(() => {
  loadMeta()
  // Load first unseen question on startup
  loadAt(-1)
})
</script>

<template>
  <div class="study-view">
    <header class="study-header">
      <div class="header-left">
        <h1>Tryb nauki — {{ cat }}</h1>
        <transition name="fade">
          <span v-if="saveStatus" class="save-status-msg">{{ saveStatus }}</span>
        </transition>
      </div>
      <div class="header-actions">
        <button
          v-if="isUserLoggedIn"
          type="button"
          class="btn-save-progress"
          :disabled="isSaving"
          @click="handleManualSave"
        >
          <span v-if="isSaving" class="mini-spinner"></span>
          Zapisz postęp
        </button>
        <router-link to="/" class="menu-back">Wróć do menu</router-link>
      </div>
    </header>

    <div class="filters">
      <div class="filter-row">
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
      </div>

      <div class="filter-row filter-row--bottom">
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
          <button
            type="button"
            class="filter-btn filter-btn--wrong"
            :class="{ active: markedFilter === 'wrongOnly' }"
            @click="markedFilter = 'wrongOnly'"
          >
            Źle odpowiedziane ({{ wrongCount }})
          </button>
        </div>
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
        @answered="onQuestionAnswered"
      />

      <div class="nav-bar">
        <button type="button" class="nav-btn" :disabled="offset === 0" @click="goPrev">
          ← Poprzednie
        </button>
        <span class="nav-position">{{ offset + 1 }} / {{ total }}</span>
        <button type="button" class="nav-btn" :disabled="nextUnseenOffset === null && offset >= total - 1" @click="goNext">
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

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}
 
.study-header h1 {
  color: #000000;
  font-size: 2.2rem;
  margin: 0;
}

.save-status-msg {
  background-color: #2e7d32;
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: bold;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-save-progress {
  color: #fff;
  background-color: #1976d2;
  border: none;
  padding: 10px 18px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.2s ease;
}

.btn-save-progress:hover:not(:disabled) {
  background-color: #115293;
}

.btn-save-progress:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.mini-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
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

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.filter-row--bottom {
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid #e0e0e0;
  padding-top: 0.75rem;
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

.filter-btn--wrong {
  border-color: #e65100;
  color: #e65100;
}

.filter-btn--wrong:hover {
  background-color: #ffe0b2;
}

.filter-btn--wrong.active {
  background-color: #e65100;
  color: white;
  border-color: #e65100;
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

@keyframes spin {
  to { transform: rotate(360deg); }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
