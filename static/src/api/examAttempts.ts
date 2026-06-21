import { fetchWithAuth } from './client'
import type { ExamAttempt, ExamAttemptPayload, ExamAttemptStats } from '../utils/examAttempts'

export async function submitExamAttempt(payload: ExamAttemptPayload): Promise<ExamAttempt> {
  const res = await fetchWithAuth('/api/questions/exam-attempts/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error('Błąd zapisu wyniku egzaminu')
  return res.json()
}

export async function fetchExamHistory(category?: string): Promise<ExamAttempt[]> {
  const url = category
    ? `/api/questions/exam-attempts/?category=${encodeURIComponent(category)}`
    : '/api/questions/exam-attempts/'
  const res = await fetchWithAuth(url)
  if (!res.ok) throw new Error('Błąd wczytywania historii egzaminów')
  return res.json()
}

export async function fetchExamStats(category?: string): Promise<ExamAttemptStats> {
  const url = category
    ? `/api/questions/exam-attempts/stats/?category=${encodeURIComponent(category)}`
    : '/api/questions/exam-attempts/stats/'
  const res = await fetchWithAuth(url)
  if (!res.ok) throw new Error('Błąd wczytywania statystyk')
  return res.json()
}
