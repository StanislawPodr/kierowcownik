import {Categories} from "../utils/categories";

export async function fetchCategories(): Promise<Categories[]> {
    const res = await fetch(`/api/questions/categories`)
    if (!res.ok) throw new Error('Błąd pobierania danych')
    const data = await res.json()
    return data.categories
}