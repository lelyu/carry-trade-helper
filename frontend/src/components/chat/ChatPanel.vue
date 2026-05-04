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

const handleSuggestedPrompt = async (prompt: string) => {
  inputMessage.value = prompt
  await sendMessage()
}

defineExpose({ handleSuggestedPrompt })
</script>

<template>
  <div class="flex flex-col h-full">
    <div class="flex-1 overflow-y-auto p-4 space-y-4" ref="messageContainer">
      <div v-if="messages.length === 0" class="text-center text-gray-500 mt-8">
        <p>Start a conversation with the AI assistant</p>
        <p class="text-sm mt-2">Try asking about carry trade opportunities</p>
      </div>

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
            'rounded-lg px-4 py-2 max-w-[85%]',
            message.role === 'user'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-900'
          ]"
        >
          <p class="whitespace-pre-wrap text-sm">{{ message.content }}</p>
          <p class="text-xs mt-1 opacity-75">
            {{ new Date(message.created_at).toLocaleTimeString() }}
          </p>
        </div>
      </div>
    </div>

    <div v-if="error" class="px-4 py-2">
      <p class="text-sm text-red-600">{{ error }}</p>
    </div>

    <div class="border-t p-4">
      <form @submit.prevent="sendMessage" class="flex space-x-2">
        <input
          v-model="inputMessage"
          type="text"
          placeholder="Ask about carry trades, rates, or currencies..."
          :disabled="loading"
          class="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
        />
        <button
          type="submit"
          :disabled="loading || !inputMessage.trim()"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
        >
          {{ loading ? 'Sending...' : 'Send' }}
        </button>
      </form>
    </div>
  </div>
</template>