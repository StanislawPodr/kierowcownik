<script setup lang="ts">
import { computed, ref } from 'vue'
import { mediaUrl } from '../utils/mediaUrl'
import {
  isAbc,
  type AnswerChoice,
  type Question,
  typeLabel,
} from '../utils/question'

const props = defineProps<{
  question: Question
  index: number
  userAnswer: AnswerChoice | null
}>()

const mediaError = ref(false)

const abc = computed(() => isAbc(props.question))
const src = computed(() => mediaUrl(props.question))
const hasMedia = computed(() => props.question.media_url.trim() !== '')

const abcOptions = computed(() =>
  [
    { key: 'A' as const, text: props.question.answer_A },
    { key: 'B' as const, text: props.question.answer_B },
    { key: 'C' as const, text: props.question.answer_C },
  ].filter((o) => String(o.text || '').trim() !== ''),
)

function optionClass(key: AnswerChoice): string {
  const isCorrect = key === props.question.correct_answer
  const isUser = key === props.userAnswer
  if (isCorrect) return 'review-answer--correct'
  if (isUser && !isCorrect) return 'review-answer--wrong'
  return ''
}
</script>

<template>
  <article class="review-card">
    <div class="meta">
      <span>Pytanie {{ index + 1 }}</span>
      <span>{{ typeLabel(question) }}</span>
      <span>{{ question.number_of_points }} pkt</span>
    </div>

    <div class="media-box media-box--review">
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
        :src="src"
        controls
        playsinline
        preload="auto"
        @error="mediaError = true"
      />
    </div>

    <p class="question-text">{{ question.question_text }}</p>

    <div v-if="userAnswer === null" class="review-unanswered">Nie udzielono odpowiedzi</div>

    <div v-if="!abc" class="answers answers--row">
      <div class="review-answer review-answer--tf" :class="optionClass('T')">TAK</div>
      <div class="review-answer review-answer--tf" :class="optionClass('N')">NIE</div>
    </div>

    <div v-else class="answers">
      <div
        v-for="opt in abcOptions"
        :key="opt.key"
        class="review-answer answer-abc"
        :class="optionClass(opt.key)"
      >
        <span class="label">{{ opt.key }}</span>
        <span>{{ opt.text }}</span>
      </div>
    </div>
  </article>
</template>
