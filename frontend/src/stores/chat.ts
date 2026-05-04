import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ChatMessage } from '@/types'
import { chatApi } from '@/services/api'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const sendMessage = async (content: string) => {
    loading.value = true
    error.value = null
    try {
      const response = await chatApi.sendMessage(content)
      messages.value.push(response)
    } catch (err) {
      error.value = 'Failed to send message'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  const fetchHistory = async (limit: number = 50) => {
    loading.value = true
    error.value = null
    try {
      const response = await chatApi.getHistory(limit)
      messages.value = response.messages
    } catch (err) {
      error.value = 'Failed to fetch chat history'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  return {
    messages,
    loading,
    error,
    sendMessage,
    fetchHistory
  }
})