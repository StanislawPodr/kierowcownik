export interface Question {
  id: number
  question_number: number
  question_text: string
  is_basic: boolean
  answer_A: string
  answer_B: string
  answer_C: string
  correct_answer: string
  media_url: string
  url_type: '' | 'P' | 'V'
  number_of_points: number
}

export type AnswerChoice = 'A' | 'B' | 'C' | 'T' | 'F'

export function isAbc(question: Question): boolean {
  return [question.answer_A, question.answer_B, question.answer_C].some(
    (t) => String(t || '').trim() !== '',
  )
}

export function typeLabel(question: Question): string {
  return question.is_basic ? 'Podstawowe' : 'Specjalistyczne'
}

export function getBasicTiming() {
  return { reading: 20, answer: 15 }
}

export function getSpecialistTiming() {
  return { total: 50 }
}
