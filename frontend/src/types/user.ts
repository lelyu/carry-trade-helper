export interface User {
  id: string
  email: string
  is_verified: boolean
  created_at: string
  last_login: string | null
}

export interface DeviceInfo {
  user_agent: string | null
  platform: string | null
  language: string | null
  screen_resolution: string | null
  timezone: string | null
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface Session {
  id: string
  device_info: Record<string, unknown> | null
  ip_address: string | null
  user_agent: string | null
  created_at: string
  last_used_at: string | null
  expires_at: string
  is_current: boolean
}

export interface SessionsResponse {
  sessions: Session[]
  current_session_id: string | null
}