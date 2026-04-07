export interface User {
  id: string
  email: string
  is_verified: boolean
  created_at: string
  last_login: string | null
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}