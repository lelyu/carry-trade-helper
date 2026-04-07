<template>
  <div class="max-w-6xl mx-auto">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Carry Trade Dashboard</h1>
      <p class="mt-2 text-gray-600">Monitor exchange rates and interest rates for carry trade opportunities</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold mb-4">Exchange Rates</h2>
        <button 
          @click="fetchExchangeRates"
          :disabled="ratesStore.loading"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50 mb-4"
        >
          {{ ratesStore.loading ? 'Loading...' : 'Fetch Latest Rates' }}
        </button>
        
        <div v-if="ratesStore.exchangeRates.length > 0" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Currency Pair</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rate</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="rate in ratesStore.exchangeRates" :key="rate.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {{ rate.base_currency }}/{{ rate.target_currency }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ parseFloat(String(rate.rate)).toFixed(4) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ new Date(rate.date).toLocaleDateString() }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div v-else-if="ratesStore.error" class="mt-4 p-4 bg-red-50 text-red-700 rounded">
          {{ ratesStore.error }}
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold mb-4">Interest Rates</h2>
        <button 
          @click="fetchInterestRates"
          :disabled="ratesStore.loading"
          class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition disabled:opacity-50 mb-4"
        >
          {{ ratesStore.loading ? 'Loading...' : 'Fetch Latest Rates' }}
        </button>
        
        <div v-if="ratesStore.interestRates.length > 0" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Country</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rate</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="rate in ratesStore.interestRates" :key="rate.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {{ rate.country_code }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ parseFloat(String(rate.rate)).toFixed(2) }}%
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ rate.rate_type || 'Policy Rate' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div v-else-if="ratesStore.error" class="mt-4 p-4 bg-red-50 text-red-700 rounded">
          {{ ratesStore.error }}
        </div>
      </div>
    </div>

    <div v-if="ratesStore.interestRates.length > 0" class="mb-8">
      <InterestRateChart 
        :data="interestChartData" 
        title="Interest Rates by Country" 
      />
    </div>

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
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRatesStore } from '@/stores/rates'
import InterestRateChart from '@/components/charts/InterestRateChart.vue'

const ratesStore = useRatesStore()

const fetchExchangeRates = () => {
  ratesStore.fetchLatestExchangeRates('USD')
}

const fetchInterestRates = () => {
  ratesStore.fetchLatestInterestRates()
}

const interestChartData = computed(() => {
  return ratesStore.interestRates.map(rate => ({
    country: rate.country_code,
    rate: parseFloat(String(rate.rate))
  }))
})
</script>