<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRatesStore } from '@/stores/rates'
import { formatExchangeRate, formatCurrency, formatRelativeTime } from '@/utils/formatting'

const emit = defineEmits<{
  baseCurrencyChange: [currency: string]
  quoteSelect: [currency: string]
}>()

const ratesStore = useRatesStore()

const selectedBase = ref('USD')
const amountInput = ref<number>(1)

const currencyNames: Record<string, string> = {
  USD: 'US Dollar',
  EUR: 'Euro',
  GBP: 'British Pound',
  JPY: 'Japanese Yen',
  CHF: 'Swiss Franc',
  AUD: 'Australian Dollar',
  CAD: 'Canadian Dollar',
  NZD: 'New Zealand Dollar',
  CNY: 'Chinese Yuan',
  HKD: 'Hong Kong Dollar'
}

const availableCurrencies = computed(() => {
  const currencies = Object.keys(currencyNames)
  return currencies.sort()
})

const quoteRates = computed(() => {
  const baseRates = ratesStore.exchangeRates.filter(
    rate => rate.base_currency === selectedBase.value
  )
  return baseRates.sort((a, b) => {
    if (a.target_currency < b.target_currency) return -1
    if (a.target_currency > b.target_currency) return 1
    return 0
  })
})

const fetchData = async () => {
  await ratesStore.fetchLatestExchangeRates(selectedBase.value)
  emit('baseCurrencyChange', selectedBase.value)
}

const handleQuoteClick = (targetCurrency: string) => {
  emit('quoteSelect', targetCurrency)
}

onMounted(async () => {
  await fetchData()
})

watch(selectedBase, async () => {
  await fetchData()
})
</script>

<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h2 class="text-xl font-semibold mb-4">Exchange Rates</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Base Currency
        </label>
        <select
          v-model="selectedBase"
          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option v-for="currency in availableCurrencies" :key="currency" :value="currency">
            {{ currency }} - {{ currencyNames[currency] }}
          </option>
        </select>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Amount
        </label>
        <input
          type="number"
          v-model.number="amountInput"
          min="0"
          step="0.01"
          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          placeholder="Enter amount"
        />
      </div>
    </div>

    <div v-if="ratesStore.loading && quoteRates.length === 0" class="animate-pulse">
      <div class="h-64 bg-gray-200 rounded"></div>
    </div>

    <div v-else-if="quoteRates.length > 0" class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Currency
            </th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Exchange Rate
            </th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Converted Amount
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Last Updated
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr
            v-for="rate in quoteRates"
            :key="rate.target_currency"
            class="hover:bg-gray-50 cursor-pointer transition-colors"
            @click="handleQuoteClick(rate.target_currency)"
          >
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="text-sm font-medium text-gray-900">
                  {{ rate.target_currency }}
                </div>
                <div class="text-sm text-gray-500 ml-2">
                  {{ currencyNames[rate.target_currency] || rate.target_currency }}
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
              {{ selectedBase }}/{{ rate.target_currency }} {{ formatExchangeRate(Number(rate.rate)) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900">
              {{ formatCurrency(Number(rate.rate) * amountInput, rate.target_currency) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatRelativeTime(rate.created_at) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="text-center text-gray-500 py-12">
      No exchange rates available
    </div>

    <div v-if="ratesStore.error" class="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-red-800">{{ ratesStore.error }}</p>
    </div>
  </div>
</template>