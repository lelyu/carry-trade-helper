import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { authApi } from '@/services/api'
import { useDeviceInfo } from '@/composables/useDeviceInfo'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const tokenExpiry = ref<number | null>(
    localStorage.getItem('token_expiry') ? parseInt(localStorage.getItem('token_expiry')!) : null
  )
  const isRefreshing = ref(false)

  const isAuthenticated = computed(() => {
    if (!accessToken.value) return false
    if (!tokenExpiry.value) return false
    if (Date.now() > tokenExpiry.value) return false
    return true
  })

  const login = async (email: string) => {
    try {
      await authApi.requestMagicLink(email)
      return { success: true }
    } catch (error) {
      return { success: false, error }
    }
  }

  const setTokens = (response: {
    access_token: string
    refresh_token: string
    expires_in: number
    user: User
  }) => {
    accessToken.value = response.access_token
    refreshToken.value = response.refresh_token
    tokenExpiry.value = Date.now() + response.expires_in * 1000
    user.value = response.user

    localStorage.setItem('access_token', response.access_token)
    localStorage.setItem('refresh_token', response.refresh_token)
    localStorage.setItem('token_expiry', tokenExpiry.value.toString())
  }

  const verifyToken = async (magicToken: string) => {
    try {
      const { getDeviceInfo } = useDeviceInfo()
      const deviceInfo = getDeviceInfo()
      const response = await authApi.verifyMagicLink(magicToken, deviceInfo)
      setTokens(response)
      return { success: true }
    } catch (error) {
      return { success: false, error }
    }
  }

  const attemptRefresh = async (): Promise<boolean> => {
    if (!refreshToken.value || isRefreshing.value) return false

    isRefreshing.value = true
    try {
      const response = await authApi.refreshToken(refreshToken.value)
      setTokens(response)
      return true
    } catch {
      logout()
      return false
    } finally {
      isRefreshing.value = false
    }
  }

  const fetchUser = async () => {
    try {
      user.value = await authApi.getCurrentUser()
      return { success: true }
    } catch (error) {
      logout()
      return { success: false, error }
    }
  }

  const logout = async () => {
    if (refreshToken.value) {
      try {
        await authApi.logout(refreshToken.value)
      } catch {
        // Ignore logout errors
      }
    }

    user.value = null
    accessToken.value = null
    refreshToken.value = null
    tokenExpiry.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('token_expiry')
  }

  const logoutAll = async () => {
    try {
      await authApi.logoutAll()
    } catch {
      // Ignore logout errors
    } finally {
      user.value = null
      accessToken.value = null
      refreshToken.value = null
      tokenExpiry.value = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('token_expiry')
    }
  }

  return {
    user,
    accessToken,
    refreshToken,
    tokenExpiry,
    isAuthenticated,
    isRefreshing,
    login,
    setTokens,
    verifyToken,
    attemptRefresh,
    fetchUser,
    logout,
    logoutAll,
  }
})