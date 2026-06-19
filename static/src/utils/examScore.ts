import type { AnswerChoice, Question } from './question'

export const EXAM_MAX_POINTS = 74
export const PASS_THRESHOLD = 68

export interface ExamScore {
  score: number
  maxScore: number
  passed: boolean
  percent: number
  passPercent: number
}

export function calculateScore(
  questions: Question[],
  answers: (AnswerChoice | null)[],
): ExamScore {
  let score = 0
  let maxScore = 0
  for (let i = 0; i < questions.length; i++) {
    if (answers[i] !== null && answers[i] === questions[i].correct_answer) {
      score += questions[i].number_of_points
    }
    maxScore += questions[i].number_of_points
  }
  return {
    score,
    maxScore,
    passed: score >= PASS_THRESHOLD,
    percent: Math.round((score / EXAM_MAX_POINTS) * 100),
    passPercent: Math.round((PASS_THRESHOLD / EXAM_MAX_POINTS) * 100),
  }
}
