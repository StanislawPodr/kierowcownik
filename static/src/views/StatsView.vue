<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { fetchCategories } from '../api/categories'
import { fetchExamHistory, fetchExamStats } from '../api/examAttempts'
import ExamScoreChart from '../components/ExamScoreChart.vue'
import type { Categories } from '../utils/categories'
import type { ExamAttempt, ExamAttemptStats } from '../utils/examAttempts'

const loading = ref(true)
const errorMsg = ref('')
const stats = ref<ExamAttemptStats | null>(null)
const history = ref<ExamAttempt[]>([])
const isLoggedIn = ref(false)
const categories = ref<Categories[]>([])
const selectedCategory = ref('')
const categoryOpen = ref(false)

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString('pl-PL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function loadData() {
  if (!selectedCategory.value) return
  loading.value = true
  errorMsg.value = ''
  try {
    const cat = selectedCategory.value
    const [statsData, historyData] = await Promise.all([
      fetchExamStats(cat),
      fetchExamHistory(cat),
    ])
    stats.value = statsData
    history.value = historyData
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Błąd'
  } finally {
    loading.value = false
  }
}

function selectCategory(symbol: string) {
  selectedCategory.value = symbol
  categoryOpen.value = false
  loadData()
}

onMounted(async () => {
  if (!localStorage.getItem('access_token')) {
    loading.value = false
    return
  }

  isLoggedIn.value = true
  try {
    categories.value = await fetchCategories()
    if (categories.value.length > 0) {
      selectedCategory.value = categories.value[0].symbol
      await loadData()
    } else {
      loading.value = false
    }
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Błąd'
    loading.value = false
  }
})
</script>

<template>
  <section class="screen screen--stats">
    <p v-if="loading && !stats" class="status">Ładowanie…</p>

    <template v-else-if="!isLoggedIn">
      <h1 class="stats-title">Statystyki</h1>
      <p class="stats-hint">Zaloguj się, aby zobaczyć historię egzaminów.</p>
      <div class="actions">
        <router-link to="/logowanie" class="menu-back stats-login-link">Logowanie</router-link>
        <router-link to="/" class="menu-back">Wróć do menu</router-link>
      </div>
    </template>

    <template v-else-if="errorMsg">
      <h1 class="stats-title">Statystyki</h1>
      <p class="error">{{ errorMsg }}</p>
      <div class="actions">
        <router-link to="/" class="menu-back">Wróć do menu</router-link>
      </div>
    </template>

    <template v-else>
      <header class="stats-top">
        <h1 class="stats-title">Statystyki</h1>
        <div v-if="categories.length" class="stats-cat-picker">
          <button
            type="button"
            class="stats-cat-btn"
            @click="categoryOpen = !categoryOpen"
          >
            Kat. {{ selectedCategory }}
            <span class="stats-cat-chevron">{{ categoryOpen ? '▲' : '▼' }}</span>
          </button>
          <ul v-if="categoryOpen" class="stats-cat-menu">
            <li
              v-for="cat in categories"
              :key="cat.id"
              class="stats-cat-option"
              :class="{ active: cat.symbol === selectedCategory }"
              @click="selectCategory(cat.symbol)"
            >
              {{ cat.symbol }}
            </li>
          </ul>
        </div>
      </header>

      <div v-if="stats" class="stats-summary">
        <div class="stats-summary-item">
          <span class="stats-summary-value">{{ stats.total_attempts }}</span>
          <span class="stats-summary-label">testów</span>
        </div>
        <div class="stats-summary-item">
          <span class="stats-summary-value">{{ stats.avg_percent }}%</span>
          <span class="stats-summary-label">śr. wynik</span>
        </div>
        <div class="stats-summary-item">
          <span class="stats-summary-value">{{ stats.pass_rate }}%</span>
          <span class="stats-summary-label">% zdanych</span>
        </div>
        <div class="stats-summary-item">
          <span class="stats-summary-value">{{ stats.passed_count }}</span>
          <span class="stats-summary-label">zdanych</span>
        </div>
      </div>

      <section class="stats-section">
        <h2 class="stats-section-title">Historia</h2>
        <p v-if="history.length === 0" class="stats-hint">Brak zapisanych egzaminów w tej kategorii.</p>
        <ul v-else class="stats-match-list">
          <li
            v-for="item in history"
            :key="item.id"
            class="stats-match"
            :class="item.passed ? 'stats-match--pass' : 'stats-match--fail'"
          >
            <span class="stats-match-bar" aria-hidden="true" />
            <span class="stats-match-date">{{ formatDate(item.created_at) }}</span>
            <span class="stats-match-cat">{{ item.category }}</span>
            <span class="stats-match-score">{{ item.percent }}%</span>
            <span class="stats-match-result">
              {{ item.passed ? 'Zdany' : 'Niezdany' }}
            </span>
          </li>
        </ul>
      </section>

      <section class="stats-section">
        <h2 class="stats-section-title">Wykres wyników</h2>
        <ExamScoreChart :attempts="history" />
      </section>

      <div class="actions">
        <router-link to="/" class="menu-back">Wróć do menu</router-link>
      </div>
    </template>
  </section>
</template>
