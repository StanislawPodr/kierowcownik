import type { Question } from '../utils/question'
import {RouteParamValue} from "vue-router";

export async function fetchWordExam(cat: string | RouteParamValue[]): Promise<{ questions: Question[] }> {
  const res = await fetch(`/api/questions/exam/category/${cat}`)
  if (!res.ok) throw new Error('Błąd pobierania danych')
  return res.json()
}

export async function fetchCategoryQuestions(cat: string | RouteParamValue[]): Promise<Question[]> {
  const res = await fetch(`/api/questions/category/${cat}`)
  if (!res.ok) throw new Error('Błąd pobierania danych')
  return res.json()
}


export interface CategoryMeta {
  category: string
  total: number
  basic_count: number
  specialist_count: number
  points: number[]
}
 
export async function fetchCategoryMeta(cat: string | RouteParamValue[]): Promise<CategoryMeta> {
  const res = await fetch(`/api/questions/category/${cat}/meta`)
  if (!res.ok) throw new Error('Błąd pobierania metadanych kategorii')
  return res.json()
}
 
export interface SequentialFilters {
  type?: 'basic' | 'specialist'
  points?: number
  ids?: number[]
}
 
export interface SequentialQuestionResponse {
  category: string
  total: number
  offset: number
  question: Question | null
}
 
export async function fetchSequentialQuestion(
  cat: string | RouteParamValue[],
  offset: number,
  filters: SequentialFilters = {},
): Promise<SequentialQuestionResponse> {
  const params = new URLSearchParams()
  params.set('offset', String(offset))
  if (filters.type) params.set('type', filters.type)
  if (filters.points !== undefined) params.set('points', String(filters.points))
  if (filters.ids && filters.ids.length) params.set('ids', filters.ids.join(','))
 
  const res = await fetch(`/api/questions/category/${cat}/sequential?${params.toString()}`)
  if (!res.ok) throw new Error('Błąd pobierania pytania')
  return res.json()
}
