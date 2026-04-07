import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { UserPreferences, PreferencesUpdate } from '@/types'
import { preferencesApi } from '@/services/api'

export const useSettingsStore = defineStore('settings', () => {
  const preferences = ref<UserPreferences | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchPreferences = async () => {
    loading.value = true
    error.value = null
    try {
      preferences.value = await preferencesApi.get()
    } catch (err) {
      error.value = 'Failed to fetch preferences'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  const updatePreferences = async (data: PreferencesUpdate) => {
    loading.value = true
    error.value = null
    try {
      preferences.value = await preferencesApi.update(data)
      return { success: true }
    } catch (err) {
      error.value = 'Failed to update preferences'
      return { success: false, error: err }
    } finally {
      loading.value = false
    }
  }

  return {
    preferences,
    loading,
    error,
    fetchPreferences,
    updatePreferences
  }
})