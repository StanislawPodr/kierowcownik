import { fetchWithAuth } from './client'

export interface ProgressData {
  wrong_questions: number[]
  marked_questions: number[]
  seen_questions: number[]
}

export async function fetchUserProgress(): Promise<ProgressData> {
  const res = await fetchWithAuth('/api/questions/progress/')
  if (!res.ok) throw new Error('Błąd wczytywania postępów z serwera')
  return res.json()
}

export async function saveUserProgress(data: ProgressData): Promise<ProgressData> {
  const res = await fetchWithAuth('/api/questions/progress/', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Błąd zapisu postępów na serwerze')
  return res.json()
}
