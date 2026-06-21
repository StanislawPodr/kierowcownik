<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { useQuestionTimer } from '../composables/useQuestionTimer'
import { mediaUrl } from '../utils/mediaUrl'
import {
  getBasicTiming,
  getSpecialistTiming,
  isAbc,
  type AnswerChoice,
  type Question,
  typeLabel,
} from '../utils/question'

const props = defineProps<{
  question: Question
  index: number
  total: number
  modelValue: AnswerChoice | null
  marked: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: AnswerChoice]
  next: []
  toggleMarked: [id: number]
}>()

const mediaError = ref(false)
const answerCountdownStarted = ref(false)
const videoRef = ref<HTMLVideoElement | null>(null)
const videoFinished = ref(false)
let lastVideoTime = 0

const { phase, secondsLeft, startReading, startAnswering, finish, clearTimer } =
  useQuestionTimer()

const abc = computed(() => isAbc(props.question))
const src = computed(() => mediaUrl(props.question))
const hasMedia = computed(() => props.question.media_url.trim() !== '')
const isVideo = computed(() => props.question.url_type === 'V')

const showMedia = computed(() => {
  if (!hasMedia.value) return false
  if (props.question.is_basic && phase.value === 'reading') return false
  return !mediaError.value
})

const hideMediaForReading = computed(
  () => props.question.is_basic && phase.value === 'reading' && hasMedia.value,
)

const readingMediaHint = computed(() => {
  if (props.question.url_type === 'V') {
    return 'Po upływie czasu zostanie wyświetlony film.'
  }
  if (props.question.url_type === 'P') {
    return 'Po upływie czasu zostanie wyświetlone zdjęcie.'
  }
  return 'Po upływie czasu zostanie wyświetlony materiał.'
})

const waitingForVideoEnd = computed(
  () =>
    props.question.is_basic &&
    isVideo.value &&
    phase.value === 'answering' &&
    !answerCountdownStarted.value,
)

const canAnswer = computed(() => phase.value === 'answering')
const canGoNext = computed(() => phase.value === 'answering')

const phaseText = computed(() => {
  if (props.question.is_basic) {
    if (phase.value === 'reading') return 'Czas na zapoznanie się z treścią'
    if (waitingForVideoEnd.value) {
      return 'Zapoznaj się z materiałem video'
    }
    return 'Czas na udzielenie odpowiedzi'
  }
  return 'Czas na pytanie'
})

const abcOptions = computed(() =>
  [
    { key: 'A' as const, text: props.question.answer_A },
    { key: 'B' as const, text: props.question.answer_B },
    { key: 'C' as const, text: props.question.answer_C },
  ].filter((o) => String(o.text || '').trim() !== ''),
)

function resetVideoState() {
  videoFinished.value = false
  lastVideoTime = 0
}

function tryAutoplay() {
  const el = videoRef.value
  if (!el || videoFinished.value) return
  el.play().catch(() => {})
}

function onVideoPause() {
  const el = videoRef.value
  if (!el || videoFinished.value || el.ended) return
  el.play().catch(() => {})
}

function onVideoPlay() {
  const el = videoRef.value
  if (!el || !videoFinished.value) return
  el.pause()
  if (Number.isFinite(el.duration)) {
    el.currentTime = el.duration
  }
}

function onVideoSeeking() {
  const el = videoRef.value
  if (!el || videoFinished.value) return
  if (el.currentTime < lastVideoTime - 0.25) {
    el.currentTime = lastVideoTime
  }
}

function onVideoTimeUpdate() {
  const el = videoRef.value
  if (!el || videoFinished.value) return
  if (el.currentTime > lastVideoTime) {
    lastVideoTime = el.currentTime
  }
}

function startAnswerCountdown() {
  if (answerCountdownStarted.value) return
  answerCountdownStarted.value = true
  startAnswering(getBasicTiming().answer, () => goNext())
}

function startBasicAnswerPhase() {
  clearTimer()
  phase.value = 'answering'
  answerCountdownStarted.value = false

  if (isVideo.value && hasMedia.value && !mediaError.value) {
    secondsLeft.value = 0
    return
  }

  startAnswerCountdown()
}

function onVideoEnded() {
  videoFinished.value = true
  if (waitingForVideoEnd.value) {
    startAnswerCountdown()
  }
}

function onVideoError() {
  mediaError.value = true
  if (phase.value === 'answering' && !answerCountdownStarted.value) {
    startAnswerCountdown()
  }
}

function beginTimers() {
  mediaError.value = false
  answerCountdownStarted.value = false
  resetVideoState()

  if (props.question.is_basic) {
    startReading(getBasicTiming().reading, () => startBasicAnswerPhase())
    return
  }

  startAnswering(getSpecialistTiming().total, () => goNext())
}

function pick(value: AnswerChoice) {
  if (!canAnswer.value) return
  emit('update:modelValue', value)
}

function skipReading() {
  if (phase.value !== 'reading' || !props.question.is_basic) return
  startBasicAnswerPhase()
}

function goNext() {
  finish()
  answerCountdownStarted.value = false
  emit('next')
}

watch(
  () => props.question.id,
  () => beginTimers(),
  { immediate: true },
)

watch(
  [() => props.question.id, hideMediaForReading, () => mediaError.value],
  () => {
    if (hideMediaForReading.value || !isVideo.value || !hasMedia.value || mediaError.value) {
      return
    }
    nextTick(() => tryAutoplay())
  },
  { immediate: true },
)
</script>

<template>
  <article class="screen screen--question">
    <div class="meta">
      <span>Pytanie {{ index + 1 }} / {{ total }}</span>
      <span>{{ typeLabel(question) }}</span>
      <span>{{ question.number_of_points }} pkt</span>
    </div>

    <div class="timer-bar">
      <span>{{ phaseText }}</span>
      <div>
        <strong v-if="answerCountdownStarted || !waitingForVideoEnd">{{ secondsLeft }} s</strong>
        <strong v-else>—</strong>
        <button
          v-if="question.is_basic && phase === 'reading'"
          type="button"
          style="margin-left: 12px"
          @click="skipReading"
        >
          Kliknij, aby wyświetlić multimedia przed czasem
        </button>
      </div>
    </div>

    <div class="media-box">
      <p v-if="!hasMedia" class="media-placeholder">Brak multimediów do pytania</p>
      <p v-else-if="hideMediaForReading" class="media-placeholder">
        {{ readingMediaHint }}
      </p>
      <p v-else-if="mediaError" class="media-error">Nie udało się załadować pliku</p>
      <img
        v-else-if="question.url_type === 'P'"
        :src="src"
        alt=""
        @error="mediaError = true"
      />
      <video
        v-else-if="question.url_type === 'V'"
        ref="videoRef"
        :class="{ 'video-finished': videoFinished }"
        :src="src"
        playsinline
        preload="auto"
        disablePictureInPicture
        controlsList="nodownload noplaybackrate nofullscreen noremoteplayback"
        @loadeddata="tryAutoplay"
        @play="onVideoPlay"
        @pause="onVideoPause"
        @seeking="onVideoSeeking"
        @timeupdate="onVideoTimeUpdate"
        @ended="onVideoEnded"
        @error="onVideoError"
        @contextmenu.prevent
      />
    </div>

    <footer class="question-footer">
      <p class="question-text">{{ question.question_text }}</p>

      <div v-if="!abc" class="answers answers--row">
        <button
          type="button"
          :class="{ selected: modelValue === 'T' }"
          :disabled="!canAnswer"
          @click="pick('T')"
        >
          TAK
        </button>
        <button
          type="button"
          :class="{ selected: modelValue === 'N' }"
          :disabled="!canAnswer"
          @click="pick('N')"
        >
          NIE
        </button>
      </div>

      <div v-else class="answers">
        <button
          v-for="opt in abcOptions"
          :key="opt.key"
          type="button"
          class="answer-abc"
          :class="{ selected: modelValue === opt.key }"
          :disabled="!canAnswer"
          @click="pick(opt.key)"
        >
          <span class="label">{{ opt.key }}</span>
          <span>{{ opt.text }}</span>
        </button>
      </div>

      <div class="actions">
        <button
          type="button"
          class="mark-toggle"
          :class="{ 'mark-toggle--active': marked }"
          @click="emit('toggleMarked', question.id)"
        >
          {{ marked ? 'Usuń z listy do nauki' : 'Oznacz jako wymagające nauki' }}
        </button>
        <button type="button" class="primary" :disabled="!canGoNext" @click="goNext">Przejdź do następnego pytania</button>
      </div>
    </footer>
  </article>
</template>

<style scoped>
.mark-toggle {
  border: 2px solid #e53935;
  background: transparent;
  color: #e53935;
  border-radius: 8px;
  padding: 10px 18px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.mark-toggle:hover {
  background-color: #e53935;
  color: #fff;
}

.mark-toggle--active {
  background-color: #e53935;
  color: #fff;
}
</style>
