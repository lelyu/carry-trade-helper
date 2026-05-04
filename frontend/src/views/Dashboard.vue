<script setup lang="ts">
import { onMounted } from 'vue'
import { useRatesStore } from '@/stores/rates'
import { useChatStore } from '@/stores/chat'
import ExchangeRatePanel from '@/components/panels/ExchangeRatePanel.vue'
import InterestRatePanel from '@/components/panels/InterestRatePanel.vue'
import ChatPanel from '@/components/chat/ChatPanel.vue'

const ratesStore = useRatesStore()
const chatStore = useChatStore()

onMounted(async () => {
  await ratesStore.fetchLatestInterestRates()
  if (chatStore.messages.length === 0) {
    await chatStore.fetchHistory()
  }
})
</script>

<template>
  <div class="max-w-7xl mx-auto">
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
      <p class="mt-2 text-gray-600">
        Analyze exchange rates, compare interest rates, and chat with AI for trading insights.
      </p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-1">
        <ExchangeRatePanel />
      </div>

      <div class="lg:col-span-1">
        <InterestRatePanel />
      </div>

      <div class="lg:col-span-1">
        <div class="bg-white rounded-lg shadow-md flex flex-col h-[700px]">
          <div class="px-6 py-4 border-b">
            <h2 class="text-xl font-semibold text-gray-900">AI Chat</h2>
            <p class="text-sm text-gray-500 mt-1">Ask about carry trade opportunities</p>
          </div>
          <ChatPanel />
        </div>
      </div>
    </div>

    <div v-if="ratesStore.error" class="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-red-800">{{ ratesStore.error }}</p>
    </div>
  </div>
</template>