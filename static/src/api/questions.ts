import type { Question } from '../utils/question'
import {RouteParamValue} from "vue-router";

export async function fetchWordExam(cat: string | RouteParamValue[]): Promise<{ questions: Question[] }> {
  const res = await fetch(`/api/questions/exam/category/${cat}`)
  if (!res.ok) throw new Error('Błąd pobierania danych')
  return res.json()
}
