import { ref } from 'vue'
import { fetchUserProgress, saveUserProgress } from '../api/progress'

export const wrongQuestions = ref<Set<number>>(new Set())
export const markedQuestions = ref<Set<number>>(new Set())
export const seenQuestions = ref<Set<number>>(new Set())
export const isLoaded = ref(false)

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'))
  if (match) return decodeURIComponent(match[2])
  return null
}

function setCookie(name: string, value: string, days = 365) {
  const date = new Date()
  date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000)
  document.cookie = `${name}=${encodeURIComponent(value)};expires=${date.toUTCString()};path=/`
}

function getUsername(): string {
  return localStorage.getItem('username') || 'guest'
}

function getWrongQuestionsCookieKey(): string {
  return `wrong_questions_${getUsername()}`
}

function getMarkedQuestionsStorageKey(): string {
  return `marked_questions_${getUsername()}`
}

function getSeenQuestionsStorageKey(): string {
  return `seen_questions_${getUsername()}`
}

function readWrongQuestionsFromCookie(): Set<number> {
  const key = getWrongQuestionsCookieKey()
  const raw = getCookie(key)
  if (!raw) return new Set()
  try {
    const arr = JSON.parse(raw)
    if (Array.isArray(arr)) {
      return new Set(arr.map(Number).filter(x => !isNaN(x)))
    }
  } catch {}
  return new Set()
}

function writeWrongQuestionsToCookie(set: Set<number>) {
  const key = getWrongQuestionsCookieKey()
  setCookie(key, JSON.stringify(Array.from(set)))
}

function readMarkedFromStorage(): Set<number> {
  const key = getMarkedQuestionsStorageKey()
  const raw = localStorage.getItem(key)
  if (!raw) return new Set()
  try {
    const arr = JSON.parse(raw)
    if (Array.isArray(arr)) {
      return new Set(arr.map(Number).filter(x => !isNaN(x)))
    }
  } catch {}
  return new Set()
}

function writeMarkedToStorage(set: Set<number>) {
  const key = getMarkedQuestionsStorageKey()
  localStorage.setItem(key, JSON.stringify(Array.from(set)))
}

function readSeenFromStorage(): Set<number> {
  const key = getSeenQuestionsStorageKey()
  const raw = localStorage.getItem(key)
  if (!raw) return new Set()
  try {
    const arr = JSON.parse(raw)
    if (Array.isArray(arr)) {
      return new Set(arr.map(Number).filter(x => !isNaN(x)))
    }
  } catch {}
  return new Set()
}

function writeSeenToStorage(set: Set<number>) {
  const key = getSeenQuestionsStorageKey()
  localStorage.setItem(key, JSON.stringify(Array.from(set)))
}

export function useUserProgress() {
  
  function initLocalState() {
    wrongQuestions.value = readWrongQuestionsFromCookie()
    markedQuestions.value = readMarkedFromStorage()
    seenQuestions.value = readSeenFromStorage()
  }

  async function loadProgress() {
    initLocalState()
    const username = localStorage.getItem('username')
    if (username) {
      try {
        const data = await fetchUserProgress()
        
        // Merge DB data with local state (avoid duplicates)
        data.wrong_questions.forEach(id => wrongQuestions.value.add(id))
        data.marked_questions.forEach(id => markedQuestions.value.add(id))
        data.seen_questions.forEach(id => seenQuestions.value.add(id))

        // Write merged back to local storages/cookies
        writeWrongQuestionsToCookie(wrongQuestions.value)
        writeMarkedToStorage(markedQuestions.value)
        writeSeenToStorage(seenQuestions.value)
        
        isLoaded.value = true
      } catch (e) {
        console.error('Failed to load progress from DB', e)
      }
    }
  }

  async function saveProgress(useKeepAlive = false) {
    const username = localStorage.getItem('username')
    if (!username) return

    const data = {
      wrong_questions: Array.from(wrongQuestions.value),
      marked_questions: Array.from(markedQuestions.value),
      seen_questions: Array.from(seenQuestions.value),
    }

    const token = localStorage.getItem('access_token')
    if (!token) return

    if (useKeepAlive) {
      try {
        const headers = {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        }
        fetch('/api/questions/progress/', {
          method: 'POST',
          headers,
          body: JSON.stringify(data),
          keepalive: true,
        })
      } catch (err) {
        console.error('Failed keepalive save', err)
      }
    } else {
      try {
        await saveUserProgress(data)
      } catch (e) {
        console.error('Failed saving progress to DB', e)
      }
    }
  }

  // Wrong Questions management
  function isWrong(id: number): boolean {
    return wrongQuestions.value.has(id)
  }

  function markAsWrong(id: number) {
    const next = new Set(wrongQuestions.value)
    next.add(id)
    wrongQuestions.value = next
    writeWrongQuestionsToCookie(next)
  }

  function removeFromWrong(id: number) {
    const next = new Set(wrongQuestions.value)
    next.delete(id)
    wrongQuestions.value = next
    writeWrongQuestionsToCookie(next)
  }

  // Marked (Wymagające nauki) management
  function isMarked(id: number): boolean {
    return markedQuestions.value.has(id)
  }

  function markAsMarked(id: number) {
    const next = new Set(markedQuestions.value)
    next.add(id)
    markedQuestions.value = next
    writeMarkedToStorage(next)
  }

  function removeFromMarked(id: number) {
    const next = new Set(markedQuestions.value)
    next.delete(id)
    markedQuestions.value = next
    writeMarkedToStorage(next)
  }

  function toggleMarked(id: number) {
    if (isMarked(id)) removeFromMarked(id)
    else markAsMarked(id)
  }

  // Seen (widziane) management
  function isSeen(id: number): boolean {
    return seenQuestions.value.has(id)
  }

  function markAsSeen(id: number) {
    const next = new Set(seenQuestions.value)
    next.add(id)
    seenQuestions.value = next
    writeSeenToStorage(next)
  }

  function removeFromSeen(id: number) {
    const next = new Set(seenQuestions.value)
    next.delete(id)
    seenQuestions.value = next
    writeSeenToStorage(next)
  }

  function clearAll() {
    wrongQuestions.value = new Set()
    markedQuestions.value = new Set()
    seenQuestions.value = new Set()
    writeWrongQuestionsToCookie(new Set())
    writeMarkedToStorage(new Set())
    writeSeenToStorage(new Set())
  }

  return {
    wrongQuestions,
    markedQuestions,
    seenQuestions,
    isLoaded,
    loadProgress,
    saveProgress,
    isWrong,
    markAsWrong,
    removeFromWrong,
    isMarked,
    markAsMarked,
    removeFromMarked,
    toggleMarked,
    isSeen,
    markAsSeen,
    removeFromSeen,
    clearAll,
  }
}

if (typeof window !== 'undefined') {
  window.addEventListener('pagehide', () => {
    const progress = useUserProgress()
    progress.saveProgress(true)
  })
}
