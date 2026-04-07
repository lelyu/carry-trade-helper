import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '@/types'
import { authApi } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const isAuthenticated = ref<boolean>(!!token.value)

  const login = async (email: string) => {
    try {
      await authApi.requestMagicLink(email)
      return { success: true }
    } catch (error) {
      return { success: false, error }
    }
  }

  const verifyToken = async (magicToken: string) => {
    try {
      const response = await authApi.verifyMagicLink(magicToken)
      token.value = response.access_token
      user.value = response.user
      isAuthenticated.value = true
      localStorage.setItem('token', response.access_token)
      return { success: true }
    } catch (error) {
      return { success: false, error }
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

  const logout = () => {
    user.value = null
    token.value = null
    isAuthenticated.value = false
    localStorage.removeItem('token')
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    verifyToken,
    fetchUser,
    logout
  }
})