import { ref } from 'vue'

const STORAGE_PREFIX = 'kierowcownik:marked:'

function storageKey(cat: string): string {
  return `${STORAGE_PREFIX}${cat}`
}

function readMarked(cat: string): Set<number> {
  try {
    const raw = localStorage.getItem(storageKey(cat))
    if (!raw) return new Set()
    const arr = JSON.parse(raw)
    if (!Array.isArray(arr)) return new Set()
    return new Set(arr.filter((v) => typeof v === 'number'))
  } catch {
    return new Set()
  }
}

function writeMarked(cat: string, ids: Set<number>) {
  try {
    localStorage.setItem(storageKey(cat), JSON.stringify(Array.from(ids)))
  } catch {

  }
}


export function markQuestionsAsWrong(cat: string, ids: number[]) {
  if (!ids.length) return
  const current = readMarked(cat)
  ids.forEach((id) => current.add(id))
  writeMarked(cat, current)
}


export function useMarkedQuestions(cat: string) {
  const marked = ref<Set<number>>(readMarked(cat))

  function isMarked(id: number): boolean {
    return marked.value.has(id)
  }

  function mark(id: number) {
    const next = new Set(marked.value)
    next.add(id)
    marked.value = next
    writeMarked(cat, next)
  }

  function unmark(id: number) {
    const next = new Set(marked.value)
    next.delete(id)
    marked.value = next
    writeMarked(cat, next)
  }

  function toggle(id: number) {
    if (isMarked(id)) unmark(id)
    else mark(id)
  }

  function clearAll() {
    marked.value = new Set()
    writeMarked(cat, new Set())
  }

  return { marked, isMarked, mark, unmark, toggle, clearAll }
}