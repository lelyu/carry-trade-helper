<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h2 class="text-2xl font-bold mb-6">{{ title }}</h2>
    
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">Base Currency</label>
      <select v-model="selectedBase" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
        <option value="USD">USD</option>
        <option value="EUR">EUR</option>
        <option value="GBP">GBP</option>
      </select>
    </div>

    <button 
      @click="fetchRates"
      :disabled="loading"
      class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50"
    >
      {{ loading ? 'Loading...' : 'Fetch Latest Rates' }}
    </button>

    <div v-if="error" class="mt-4 p-4 bg-red-50 text-red-700 rounded">
      {{ error }}
    </div>

    <div v-if="exchangeRates.length > 0" class="mt-6">
      <h3 class="text-lg font-semibold mb-4">Exchange Rates (Base: {{ selectedBase }})</h3>
      <ExchangeRateChart :data="chartData" title="Exchange Rates Over Time" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRatesStore } from '@/stores/rates'
import ExchangeRateChart from '@/components/charts/ExchangeRateChart.vue'

const ratesStore = useRatesStore()

const title = 'Exchange Rates'
const selectedBase = ref('USD')
const loading = computed(() => ratesStore.loading)
const error = computed(() => ratesStore.error)
const exchangeRates = computed(() => ratesStore.exchangeRates)

const chartData = computed(() => {
  return exchangeRates.value.map(rate => ({
    date: new Date(rate.date),
    rate: parseFloat(String(rate.rate))
  }))
})

const fetchRates = async () => {
  await ratesStore.fetchLatestExchangeRates(selectedBase.value)
}
</script>