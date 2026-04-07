<script setup lang="ts">
import { ref, computed } from 'vue'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()

const inputMessage = ref('')
const loading = computed(() => chatStore.loading)
const error = computed(() => chatStore.error)
const messages = computed(() => chatStore.messages)

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return
  
  const message = inputMessage.value
  inputMessage.value = ''
  
  await chatStore.sendMessage(message)
}
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold text-gray-900 mb-6">AI Trading Assistant</h1>
    <p class="text-gray-600 mb-6">
      Ask questions about carry trades, interest rates, and market analysis. Powered by AI with real-time data.
    </p>
    
    <div class="bg-white rounded-lg shadow-md mb-6 h-96 overflow-y-auto p-4">
      <div v-if="messages.length === 0" class="text-center text-gray-500 mt-32">
        <p>Start a conversation with the AI assistant</p>
        <p class="text-sm mt-2">Try asking: "What are the best carry trade opportunities today?"</p>
      </div>
      
      <div v-else class="space-y-4">
        <div 
          v-for="message in messages" 
          :key="message.id"
          :class="[
            'flex',
            message.role === 'user' ? 'justify-end' : 'justify-start'
          ]"
        >
          <div 
            :class="[
              'rounded-lg px-4 py-2 max-w-3xl',
              message.role === 'user' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-900'
            ]"
          >
            <p class="whitespace-pre-wrap">{{ message.content }}</p>
            <p class="text-xs mt-1 opacity-75">
              {{ new Date(message.created_at).toLocaleTimeString() }}
            </p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="bg-white rounded-lg shadow-md p-4">
      <form @submit.prevent="sendMessage" class="flex space-x-4">
        <input
          v-model="inputMessage"
          type="text"
          placeholder="Type your message..."
          :disabled="loading"
          class="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
        <button
          type="submit"
          :disabled="loading || !inputMessage.trim()"
          class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ loading ? 'Sending...' : 'Send' }}
        </button>
      </form>
    </div>
    
    <div v-if="error" class="mt-4 p-4 bg-red-50 text-red-800 rounded">
      {{ error }}
    </div>
  </div>
</template>