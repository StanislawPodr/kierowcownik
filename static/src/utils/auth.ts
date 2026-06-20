export interface RegisterPayload {
  username: string
  password?: string
  password_confirm?: string
}

export interface RegisterResponse {
  id: number
  username: string
}

export interface LoginPayload {
  username: string
  password?: string
}

export interface LoginResponse {
  access: string
  refresh: string
}

