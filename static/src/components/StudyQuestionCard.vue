<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { mediaUrl } from '../utils/mediaUrl'
import { isAbc, type AnswerChoice, type Question, typeLabel } from '../utils/question'

const props = defineProps<{
  question: Question
  index: number
  total: number
  marked: boolean
}>()

const emit = defineEmits<{
  toggleMarked: [id: number]
}>()

const mediaError = ref(false)
const selectedAnswer = ref<AnswerChoice | null>(null)
const videoRef = ref<HTMLVideoElement | null>(null)

const abc = computed(() => isAbc(props.question))
const src = computed(() => mediaUrl(props.question))
const hasMedia = computed(() => props.question.media_url.trim() !== '')
const answered = computed(() => selectedAnswer.value !== null)

const abcOptions = computed(() =>
  [
    { key: 'A' as const, text: props.question.answer_A },
    { key: 'B' as const, text: props.question.answer_B },
    { key: 'C' as const, text: props.question.answer_C },
  ].filter((o) => String(o.text || '').trim() !== ''),
)

const normalizedCorrectAnswer = computed(() =>
  String(props.question.correct_answer || '').trim().toUpperCase(),
)

const isSelectedCorrect = computed(
  () => answered.value && String(selectedAnswer.value).toUpperCase() === normalizedCorrectAnswer.value,
)

function isCorrect(key: string): boolean {
  return key.toUpperCase() === normalizedCorrectAnswer.value
}

function isWrongSelected(key: string): boolean {
  return (
    answered.value &&
    String(selectedAnswer.value).toUpperCase() === key.toUpperCase() &&
    key.toUpperCase() !== normalizedCorrectAnswer.value
  )
}


function pick(key: AnswerChoice) {
  if (answered.value) return
  selectedAnswer.value = key
}

function retry() {
  selectedAnswer.value = null
}

function tryAutoplay() {
  const el = videoRef.value
  if (!el) return
  el.play().catch(() => {
  })
}

watch(
  () => props.question.id,
  () => {
    selectedAnswer.value = null
    mediaError.value = false
    nextTick(() => tryAutoplay())
  },
  { immediate: true },
)
</script>

<template>
  <article class="screen screen--question study-card" :class="{ 'study-card--marked': marked }">
    <div class="meta">
      <span>Pytanie {{ index + 1 }} / {{ total }}</span>
      <span>{{ typeLabel(question) }}</span>
      <span>{{ question.number_of_points }} pkt</span>
      <span v-if="marked" class="badge-marked">Wymaga nauki</span>
    </div>



    <div class="media-box">
      <p v-if="!hasMedia" class="media-placeholder">Brak multimediów do pytania</p>
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
        :src="src"
        playsinline
        controls
        autoplay
        muted
        loop
        preload="auto"
        disablePictureInPicture
        controlsList="nodownload noplaybackrate"
        @loadeddata="tryAutoplay"
        @error="mediaError = true"
        @contextmenu.prevent
      />
    </div>

    <footer class="question-footer">
      <p class="question-text">{{ question.question_text }}</p>

      <div v-if="!abc" class="answers answers--row">
        <button
          type="button"
          class="study-answer"
          :class="{
            correct: answered && isCorrect('T'),
            wrong: isWrongSelected('T'),
            selected: selectedAnswer === 'T',
          }"
          :disabled="answered"
          @click="pick('T')"
        >
          TAK
        </button>
        <button
          type="button"
          class="study-answer"
          :class="{
            correct: answered && isCorrect('N'),
            wrong: isWrongSelected('N'),
            selected: selectedAnswer === 'N',
          }"
          :disabled="answered"
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
          class="answer-abc study-answer"
          :class="{
            correct: answered && isCorrect(opt.key),
            wrong: isWrongSelected(opt.key),
            selected: selectedAnswer === opt.key,
          }"
          :disabled="answered"
          @click="pick(opt.key)"
        >
          <span class="label">{{ opt.key }}</span>
          <span>{{ opt.text }}</span>
        </button>
      </div>

      <p v-if="answered" class="answer-feedback" :class="{ ok: isSelectedCorrect }">
        {{ isSelectedCorrect ? 'Poprawna odpowiedź!' : 'Niepoprawna odpowiedź — prawidłowa jest zaznaczona na zielono.' }}
      </p>

      <div class="actions">
        <button v-if="answered" type="button" class="retry-btn" @click="retry">
          Spróbuj ponownie
        </button>
        <button
          type="button"
          class="mark-toggle"
          :class="{ 'mark-toggle--active': marked }"
          @click="emit('toggleMarked', question.id)"
        >
          {{ marked ? 'Usuń z listy do nauki' : 'Oznacz jako wymagające nauki' }}
        </button>
      </div>
    </footer>
  </article>
</template>

<style scoped>
.study-card {
  position: relative;
}

.badge-marked {
  background-color: #e53935;
  color: #fff;
  padding: 2px 10px;
  border-radius: 12px;
  font-weight: bold;
  font-size: 0.85rem;
}

.study-card--marked {
  outline: 2px solid #e53935;
}

.study-answer.selected:not(.correct):not(.wrong) {
  outline: 3px solid #1565c0;
}

.study-answer.correct {
  background-color: #2e7d32 !important;
  color: #fff !important;
  border-color: #2e7d32 !important;
  font-weight: bold;
}

.study-answer.wrong {
  background-color: #c62828 !important;
  color: #fff !important;
  border-color: #c62828 !important;
  font-weight: bold;
}

.study-answer:disabled {
  cursor: default;
  opacity: 1;
}

.answer-feedback {
  margin-top: 0.75rem;
  font-weight: bold;
  color: #c62828;
}

.answer-feedback.ok {
  color: #2e7d32;
}

.retry-btn {
  border: 2px solid #1565c0;
  background: transparent;
  color: #1565c0;
  border-radius: 8px;
  padding: 10px 18px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.retry-btn:hover {
  background-color: #1565c0;
  color: #fff;
}

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