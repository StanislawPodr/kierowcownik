import type { Question } from '../utils/question'

export async function fetchWordExam(): Promise<{ questions: Question[] }> {
  const res = await fetch('/api/questions/exam/word/')
  if (!res.ok) throw new Error('Błąd pobierania danych')
  return res.json()
}
