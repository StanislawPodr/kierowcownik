<script setup lang="ts">
import { computed } from 'vue'
import { EXAM_MAX_POINTS, PASS_THRESHOLD } from '../utils/examScore'
import type { ExamAttempt } from '../utils/examAttempts'

const props = defineProps<{
  attempts: ExamAttempt[]
}>()

const PAD = { top: 16, right: 16, bottom: 28, left: 40 }
const W = 480
const H = 220
const Y_MIN = 0
const Y_MAX = 100
const PASS_PERCENT = Math.round((PASS_THRESHOLD / EXAM_MAX_POINTS) * 100)

const chronological = computed(() =>
  [...props.attempts].sort(
    (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
  ),
)

const innerW = W - PAD.left - PAD.right
const innerH = H - PAD.top - PAD.bottom

function yAt(percent: number): number {
  const t = (percent - Y_MIN) / (Y_MAX - Y_MIN)
  return PAD.top + innerH * (1 - t)
}

const yTicks = [0, 25, 50, 75, 100]

const bars = computed(() => {
  const items = chronological.value
  const count = items.length
  if (count === 0) return []

  const slotW = innerW / count
  const barW = Math.min(slotW * 0.65, 28)

  return items.map((a, i) => {
    const pct = Math.min(Y_MAX, Math.max(Y_MIN, a.percent))
    const x = PAD.left + i * slotW + (slotW - barW) / 2
    const y = yAt(pct)
    const barH = PAD.top + innerH - y
    return {
      x,
      y,
      width: barW,
      height: barH,
      passed: a.passed,
      percent: a.percent,
      label: i + 1,
    }
  })
})

const passLineY = computed(() => yAt(PASS_PERCENT))
</script>

<template>
  <div v-if="attempts.length === 0" class="chart-empty">Za mało danych do wykresu.</div>
  <svg
    v-else
    class="score-chart"
    :viewBox="`0 0 ${W} ${H}`"
    role="img"
    aria-label="Wykres wyników egzaminów w procentach"
  >
    <line
      v-for="tick in yTicks"
      :key="tick"
      :x1="PAD.left"
      :y1="yAt(tick)"
      :x2="W - PAD.right"
      :y2="yAt(tick)"
      class="chart-grid"
    />
    <text
      v-for="tick in yTicks"
      :key="'lbl-' + tick"
      :x="PAD.left - 6"
      :y="yAt(tick) + 4"
      class="chart-tick-label"
      text-anchor="end"
    >
      {{ tick }}%
    </text>

    <line
      :x1="PAD.left"
      :y1="passLineY"
      :x2="W - PAD.right"
      :y2="passLineY"
      class="chart-pass-line"
    />
    <text :x="W - PAD.right" :y="passLineY - 4" class="chart-pass-label" text-anchor="end">
      próg {{ PASS_PERCENT }}%
    </text>

    <rect
      v-for="(bar, i) in bars"
      :key="i"
      :x="bar.x"
      :y="bar.y"
      :width="bar.width"
      :height="bar.height"
      rx="2"
      :class="bar.passed ? 'chart-bar--pass' : 'chart-bar--fail'"
    >
      <title>Egzamin {{ bar.label }}: {{ bar.percent }}%</title>
    </rect>
  </svg>
</template>

<style scoped>
.score-chart {
  width: 100%;
  max-width: 520px;
  height: auto;
  display: block;
}

.chart-grid {
  stroke: #e8e8e8;
  stroke-width: 1;
}

.chart-tick-label {
  font-size: 10px;
  fill: #666;
}

.chart-pass-line {
  stroke: #2e7d32;
  stroke-width: 1.5;
  stroke-dasharray: 4 3;
  opacity: 0.85;
}

.chart-pass-label {
  font-size: 9px;
  fill: #2e7d32;
}

.chart-bar--pass {
  fill: #2e7d32;
}

.chart-bar--fail {
  fill: #c62828;
}

.chart-empty {
  color: #666;
  font-size: 0.9rem;
  padding: 24px 0;
  text-align: center;
}
</style>
