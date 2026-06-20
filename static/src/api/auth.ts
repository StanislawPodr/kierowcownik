import { RegisterPayload, RegisterResponse, LoginPayload, LoginResponse } from '../utils/auth'

export async function registerUser(payload: RegisterPayload): Promise<RegisterResponse> {
  const res = await fetch('/api/auth/register/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    // Django REST Framework validation errors are typically dictionaries of arrays
    throw errorData
  }

  return res.json()
}

export async function loginUser(payload: LoginPayload): Promise<LoginResponse> {
  const res = await fetch('/api/auth/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw errorData
  }

  return res.json()
}

