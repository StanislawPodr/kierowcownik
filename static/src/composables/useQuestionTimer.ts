import { onUnmounted, ref } from 'vue'

export type TimerPhase = 'reading' | 'answering' | 'done'

export function useQuestionTimer() {
  const phase = ref<TimerPhase>('reading')
  const secondsLeft = ref(0)
  let intervalId: ReturnType<typeof setInterval> | null = null

  function clearTimer() {
    if (intervalId !== null) {
      clearInterval(intervalId)
      intervalId = null
    }
  }

  function tick(onEnd: () => void) {
    if (secondsLeft.value <= 1) {
      clearTimer()
      onEnd()
      return
    }
    secondsLeft.value -= 1
  }

  function startReading(seconds: number, onReadingEnd: () => void) {
    clearTimer()
    phase.value = 'reading'
    secondsLeft.value = seconds
    intervalId = setInterval(() => tick(onReadingEnd), 1000)
  }

  function startAnswering(seconds: number, onAnswerEnd: () => void) {
    clearTimer()
    phase.value = 'answering'
    secondsLeft.value = seconds
    intervalId = setInterval(() => tick(onAnswerEnd), 1000)
  }

  function finish() {
    clearTimer()
    phase.value = 'done'
    secondsLeft.value = 0
  }

  onUnmounted(clearTimer)

  return { phase, secondsLeft, startReading, startAnswering, finish, clearTimer }
}
