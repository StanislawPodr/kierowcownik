export interface ExamAttempt {
  id: number
  category: string
  score: number
  max_score: number
  passed: boolean
  percent: number
  created_at: string
}

export interface ExamAttemptPayload {
  category: string
  score: number
  max_score: number
  passed: boolean
}

export interface ExamAttemptStats {
  total_attempts: number
  passed_count: number
  pass_rate: number
  avg_score: number
  avg_percent: number
  last_attempt: ExamAttempt | null
}
