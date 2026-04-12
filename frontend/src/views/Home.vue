<script setup lang="ts">
import { onMounted } from 'vue'
import { useRatesStore } from '@/stores/rates'
import ExchangeRatePanel from '@/components/panels/ExchangeRatePanel.vue'
import InterestRatePanel from '@/components/panels/InterestRatePanel.vue'

const ratesStore = useRatesStore()

onMounted(async () => {
  await ratesStore.fetchLatestExchangeRates('USD')
  await ratesStore.fetchLatestInterestRates()
})
</script>

<template>
  <div class="max-w-7xl mx-auto">
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900">Carry Trade Dashboard</h1>
      <p class="mt-2 text-gray-600">
        Monitor exchange rates and interest rates for carry trade opportunities
      </p>
    </div>

    <div class="space-y-6">
      <ExchangeRatePanel />
      <InterestRatePanel />
      
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold mb-4">Carry Trade Opportunities</h2>
        <p class="text-gray-600 mb-4">
          Identify potential carry trade opportunities based on interest rate differentials.
          Higher interest rate currencies can offer positive carry when paired with lower rate currencies.
        </p>
        <router-link 
          to="/chat" 
          class="inline-block px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition"
        >
          Ask AI for Analysis
        </router-link>
      </div>
    </div>
  </div>
</template>