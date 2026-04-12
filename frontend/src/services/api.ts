import axios from 'axios'
import type { User, AuthResponse, DeviceInfo, SessionsResponse } from '@/types'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const authStore = useAuthStore()
      const refreshed = await authStore.attemptRefresh()

      if (refreshed) {
        originalRequest.headers.Authorization = `Bearer ${authStore.accessToken}`
        return api(originalRequest)
      }
    }

    return Promise.reject(error)
  }
)

export const authApi = {
  requestMagicLink: async (email: string) => {
    const response = await api.post('/auth/request-magic-link', { email })
    return response.data
  },

  verifyMagicLink: async (token: string, deviceInfo?: DeviceInfo): Promise<AuthResponse> => {
    const response = await api.post('/auth/verify-magic-link', {
      token,
      device_info: deviceInfo,
    })
    return response.data
  },

  refreshToken: async (refreshToken: string): Promise<AuthResponse> => {
    const response = await api.post('/auth/refresh', { refresh_token: refreshToken })
    return response.data
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me')
    return response.data
  },

  logout: async (refreshToken: string) => {
    await api.post('/auth/logout', { refresh_token: refreshToken })
  },

  logoutAll: async () => {
    await api.post('/auth/logout-all')
  },

  getSessions: async (): Promise<SessionsResponse> => {
    const response = await api.get('/auth/sessions')
    return response.data
  },

  revokeSession: async (sessionId: string) => {
    await api.post('/auth/revoke-session', { session_id: sessionId })
  },
}

export const exchangeRatesApi = {
  getLatest: async (base: string = 'USD', quotes?: string) => {
    const params = new URLSearchParams({ base })
    if (quotes) params.append('quotes', quotes)
    const response = await api.get('/api/exchange-rates/latest', { params })
    return response.data
  },

  getHistorical: async (base: string, target: string, from: string, to: string) => {
    const response = await api.get('/api/exchange-rates/historical', {
      params: { base, quotes: target, from: from, to: to }
    })
    return response.data
  },

  getCurrencies: async () => {
    const response = await api.get('/api/exchange-rates/currencies')
    return response.data
  },
}

export const interestRatesApi = {
  getLatest: async (countries?: string) => {
    const params = countries ? { countries } : {}
    const response = await api.get('/api/interest-rates/latest', { params })
    return response.data
  },

  getHistorical: async (countries: string, from: string, to: string) => {
    const response = await api.get('/api/interest-rates/historical', {
      params: { countries, from_date: from, to_date: to }
    })
    return response.data
  },
}

export const preferencesApi = {
  get: async () => {
    const response = await api.get('/api/preferences')
    return response.data
  },

  create: async (data: any) => {
    const response = await api.post('/api/preferences', data)
    return response.data
  },

  update: async (data: any) => {
    const response = await api.put('/api/preferences', data)
    return response.data
  },
}

export const chatApi = {
  sendMessage: async (content: string) => {
    const response = await api.post('/api/chat/message', { content })
    return response.data
  },

  getHistory: async (limit: number = 50, offset: number = 0) => {
    const response = await api.get('/api/chat/history', {
      params: { limit, offset }
    })
    return response.data
  },
}

export default api