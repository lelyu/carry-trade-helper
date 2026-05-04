<script setup lang="ts">
import { onMounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import ChatPanel from '@/components/chat/ChatPanel.vue'

const chatStore = useChatStore()

onMounted(async () => {
  if (chatStore.messages.length === 0) {
    await chatStore.fetchHistory()
  }
})
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold text-gray-900 mb-6">AI Trading Assistant</h1>
    <p class="text-gray-600 mb-6">
      Ask questions about carry trades, interest rates, and market analysis. Powered by AI with real-time data.
    </p>

    <div class="bg-white rounded-lg shadow-md h-[600px] flex flex-col">
      <ChatPanel />
    </div>
  </div>
</template>