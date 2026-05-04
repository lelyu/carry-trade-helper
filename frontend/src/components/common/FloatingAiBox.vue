<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const isOpen = ref(false)
const inputMessage = ref('')
const boxRef = ref<HTMLElement | null>(null)

const suggestedPrompts = [
  'Analyze current carry trade opportunities',
  'Compare interest rates across currencies',
  "What's the outlook for USD/JPY?"
]

const toggleOpen = () => {
  isOpen.value = !isOpen.value
}

const navigateToChat = (prompt: string) => {
  if (authStore.isAuthenticated) {
    router.push({ name: 'Dashboard', query: { prompt: prompt } })
  } else {
    router.push({ name: 'Login', query: { redirect: '/dashboard', prompt: prompt } })
  }
  isOpen.value = false
}

const handlePromptClick = (prompt: string) => {
  navigateToChat(prompt)
}

const handleSubmit = () => {
  if (!inputMessage.value.trim()) return
  const prompt = inputMessage.value
  inputMessage.value = ''
  navigateToChat(prompt)
}

const handleClickOutside = (event: MouseEvent) => {
  if (boxRef.value && !boxRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div ref="boxRef" class="floating-ai-box fixed bottom-6 right-6 z-50">
    <div
      v-if="isOpen"
      class="mb-4 w-80 bg-white rounded-lg shadow-xl border border-gray-200 overflow-hidden"
    >
      <div class="bg-blue-600 px-4 py-3">
        <h3 class="text-white font-semibold text-sm">AI Trading Assistant</h3>
        <p class="text-blue-100 text-xs mt-0.5">Powered by AI agents</p>
      </div>

      <div class="p-4">
        <p class="text-sm text-gray-600 mb-3">
          Ask about carry trades, rates, or currencies
        </p>

        <div class="space-y-2 mb-4">
          <button
            v-for="prompt in suggestedPrompts"
            :key="prompt"
            @click="handlePromptClick(prompt)"
            class="w-full text-left px-3 py-2 text-sm rounded-md border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-colors text-gray-700"
          >
            {{ prompt }}
          </button>
        </div>

        <form @submit.prevent="handleSubmit" class="flex space-x-2">
          <input
            v-model="inputMessage"
            type="text"
            placeholder="Or type your question..."
            class="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
          />
          <button
            type="submit"
            :disabled="!inputMessage.trim()"
            class="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50 text-sm"
          >
            Go
          </button>
        </form>
      </div>
    </div>

    <button
      @click.stop="toggleOpen"
      class="w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg flex items-center justify-center transition-all hover:scale-105"
      :aria-label="isOpen ? 'Close AI assistant' : 'Open AI assistant'"
    >
      <svg v-if="!isOpen" xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
      </svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>
</template>