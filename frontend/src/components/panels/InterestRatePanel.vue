<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRatesStore } from '@/stores/rates'
import { formatRelativeTime } from '@/utils/formatting'

const ratesStore = useRatesStore()

const currencyInfo: Record<string, { country: string; name: string; code: string }> = {
  USD: { country: 'USA', name: 'US Dollar', code: 'USD' },
  EUR: { country: 'EU', name: 'Euro', code: 'EUR' },
  GBP: { country: 'UK', name: 'British Pound', code: 'GBP' },
  JPY: { country: 'Japan', name: 'Japanese Yen', code: 'JPY' },
  CHF: { country: 'Switzerland', name: 'Swiss Franc', code: 'CHF' },
  AUD: { country: 'Australia', name: 'Australian Dollar', code: 'AUD' },
  CAD: { country: 'Canada', name: 'Canadian Dollar', code: 'CAD' },
  NZD: { country: 'New Zealand', name: 'New Zealand Dollar', code: 'NZD' },
  CNY: { country: 'China', name: 'Chinese Yuan', code: 'CNY' },
  HKD: { country: 'Hong Kong', name: 'Hong Kong Dollar', code: 'HKD' }
}

const selectedCurrencies = ref<string[]>(['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD'])

const availableCurrencies = computed(() => {
  return Object.keys(currencyInfo).sort()
})

const filteredRates = computed(() => {
  return ratesStore.interestRates
    .filter(rate => selectedCurrencies.value.includes(rate.currency_code))
    .sort((a, b) => {
      if (a.currency_code < b.currency_code) return -1
      if (a.currency_code > b.currency_code) return 1
      return 0
    })
})

const toggleCurrency = async (currency: string) => {
  const index = selectedCurrencies.value.indexOf(currency)
  if (index > -1) {
    if (selectedCurrencies.value.length > 1) {
      selectedCurrencies.value.splice(index, 1)
    }
  } else {
    selectedCurrencies.value.push(currency)
  }
}

const fetchRates = async () => {
  const countries = selectedCurrencies.value
    .map(c => currencyInfo[c]?.country || c)
    .filter(Boolean)
    .join(',')
  
  await ratesStore.fetchLatestInterestRates(countries)
}

onMounted(async () => {
  await fetchRates()
})

watch(selectedCurrencies, async () => {
  await fetchRates()
}, { deep: true })
</script>

<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h2 class="text-xl font-semibold mb-4">Interest Rates</h2>
    
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Filter by Currency
      </label>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="currency in availableCurrencies"
          :key="currency"
          @click="toggleCurrency(currency)"
          :class="[
            'px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
            selectedCurrencies.includes(currency)
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          ]"
        >
          {{ currency }}
        </button>
      </div>
    </div>

    <div v-if="ratesStore.loading && filteredRates.length === 0" class="animate-pulse">
      <div class="h-48 bg-gray-200 rounded"></div>
    </div>

    <div v-else-if="filteredRates.length > 0" class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Currency
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Country
            </th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Interest Rate
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Last Updated
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr
            v-for="rate in filteredRates"
            :key="rate.currency_code"
            class="hover:bg-gray-50 transition-colors"
          >
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="text-sm font-medium text-gray-900">
                  {{ rate.currency_code }}
                </div>
                <div class="text-sm text-gray-500 ml-2">
                  {{ currencyInfo[rate.currency_code]?.name || rate.currency_code }}
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ rate.country_code }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right">
              <span class="text-sm font-medium text-gray-900">
                {{ Number(rate.rate).toFixed(2) }}%
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatRelativeTime(rate.created_at) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="text-center text-gray-500 py-12">
      No interest rates available
    </div>

    <div v-if="ratesStore.error" class="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-red-800">{{ ratesStore.error }}</p>
    </div>
  </div>
</template>