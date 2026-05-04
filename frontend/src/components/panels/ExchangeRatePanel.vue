<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import draggable from 'vuedraggable'
import { useRatesStore } from '@/stores/rates'
import { formatExchangeRate, formatCurrency, formatRelativeTime } from '@/utils/formatting'
import type { ExchangeRate } from '@/types'

const emit = defineEmits<{
  baseCurrencyChange: [currency: string]
  quoteSelect: [currency: string]
}>()

const ratesStore = useRatesStore()

const STORAGE_KEY_ORDER = 'exchangeRateOrder'
const STORAGE_KEY_TARGETS = 'exchangeRateTargets'

const selectedBase = ref('USD')
const amountInput = ref<number>(1)
const targetSearch = ref('')
const showTargetDropdown = ref(false)

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

const savedTargetCurrencies = localStorage.getItem(STORAGE_KEY_TARGETS)
const selectedTargets = ref<string[]>(savedTargetCurrencies ? JSON.parse(savedTargetCurrencies) : [])

const allQuoteRates = computed(() => {
  const baseRates = ratesStore.exchangeRates.filter(
    rate => rate.base_currency === selectedBase.value
  )
  return baseRates.sort((a, b) => {
    if (a.target_currency < b.target_currency) return -1
    if (a.target_currency > b.target_currency) return 1
    return 0
  })
})

const displayRates = ref<ExchangeRate[]>([])

const quoteRates = computed(() => {
  if (selectedTargets.value.length === 0) {
    return displayRates.value.length > 0 ? displayRates.value : allQuoteRates.value
  }
  const source = displayRates.value.length > 0 ? displayRates.value : allQuoteRates.value
  return source.filter((r: ExchangeRate) => selectedTargets.value.includes(r.target_currency))
})

const searchResults = computed(() => {
  if (!targetSearch.value) return availableCurrencies.value.filter(c => !selectedTargets.value.includes(c))
  const query = targetSearch.value.toLowerCase()
  return availableCurrencies.value.filter(c =>
    !selectedTargets.value.includes(c) &&
    (c.toLowerCase().includes(query) || currencyNames[c]?.toLowerCase().includes(query))
  )
})

const addTargetCurrency = (currency: string) => {
  if (!selectedTargets.value.includes(currency)) {
    selectedTargets.value.push(currency)
    saveTargetCurrencies()
  }
  targetSearch.value = ''
  showTargetDropdown.value = false
}

const removeTargetCurrency = (currency: string) => {
  selectedTargets.value = selectedTargets.value.filter(c => c !== currency)
  saveTargetCurrencies()
}

const clearTargetFilter = () => {
  selectedTargets.value = []
  saveTargetCurrencies()
}

const saveTargetCurrencies = () => {
  localStorage.setItem(STORAGE_KEY_TARGETS, JSON.stringify(selectedTargets.value))
}

const saveDisplayOrder = () => {
  localStorage.setItem(STORAGE_KEY_ORDER, JSON.stringify(displayRates.value.map(r => r.target_currency)))
}

const restoreDisplayOrder = () => {
  const order = localStorage.getItem(STORAGE_KEY_ORDER)
  if (!order) {
    displayRates.value = [...allQuoteRates.value]
    return
  }
  const orderList: string[] = JSON.parse(order)
  const rateMap = new Map(allQuoteRates.value.map(r => [r.target_currency, r]))
  const ordered = orderList
    .filter(code => rateMap.has(code))
    .map(code => rateMap.get(code)!)
  const remaining = allQuoteRates.value.filter(r => !orderList.includes(r.target_currency))
  displayRates.value = [...ordered, ...remaining]
}

const handleDragEnd = () => {
  saveDisplayOrder()
}

const fetchData = async () => {
  await ratesStore.fetchLatestExchangeRates(selectedBase.value)
  emit('baseCurrencyChange', selectedBase.value)
  restoreDisplayOrder()
}

const handleQuoteClick = (targetCurrency: string) => {
  emit('quoteSelect', targetCurrency)
}

const closeDropdown = () => {
  showTargetDropdown.value = false
}

onMounted(async () => {
  await fetchData()
})

watch(selectedBase, async () => {
  await fetchData()
})

watch(allQuoteRates, () => {
  restoreDisplayOrder()
}, { deep: true })
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

    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Target Currencies
      </label>
      <div class="relative">
        <div class="flex flex-wrap gap-2 mb-2" v-if="selectedTargets.length > 0">
          <span
            v-for="currency in selectedTargets"
            :key="currency"
            class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
          >
            {{ currency }} - {{ currencyNames[currency] }}
            <button
              @click="removeTargetCurrency(currency)"
              class="ml-1.5 inline-flex items-center justify-center w-4 h-4 rounded-full text-blue-400 hover:text-blue-600 hover:bg-blue-200 focus:outline-none"
            >
              &times;
            </button>
          </span>
          <button
            @click="clearTargetFilter"
            class="px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
          >
            Show all
          </button>
        </div>
        <div class="relative">
          <input
            v-model="targetSearch"
            @focus="showTargetDropdown = true"
            @keydown.escape="closeDropdown"
            type="text"
            placeholder="Search currencies to filter..."
            class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
          />
          <div
            v-if="showTargetDropdown && searchResults.length > 0"
            class="absolute z-10 mt-1 w-full bg-white shadow-lg rounded-md border border-gray-200 max-h-48 overflow-y-auto"
          >
            <button
              v-for="currency in searchResults"
              :key="currency"
              @click="addTargetCurrency(currency)"
              class="block w-full text-left px-4 py-2 text-sm hover:bg-blue-50 transition-colors"
            >
              <span class="font-medium">{{ currency }}</span>
              <span class="text-gray-500 ml-2">{{ currencyNames[currency] }}</span>
            </button>
          </div>
          <div
            v-if="showTargetDropdown && searchResults.length === 0 && targetSearch"
            class="absolute z-10 mt-1 w-full bg-white shadow-lg rounded-md border border-gray-200 p-4 text-sm text-gray-500"
          >
            No currencies found
          </div>
        </div>
      </div>
    </div>

    <div v-if="ratesStore.loading && allQuoteRates.length === 0" class="animate-pulse">
      <div class="h-64 bg-gray-200 rounded"></div>
    </div>

    <div v-else-if="quoteRates.length > 0" class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-8"></th>
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
        <draggable
          v-model="displayRates"
          tag="tbody"
          item-key="target_currency"
          handle=".drag-handle"
          @end="handleDragEnd"
          class="bg-white divide-y divide-gray-200"
        >
          <template #item="{ element: rate }">
            <tr
              v-show="selectedTargets.length === 0 || selectedTargets.includes(rate.target_currency)"
              class="hover:bg-gray-50 cursor-pointer transition-colors"
              @click="handleQuoteClick(rate.target_currency)"
            >
              <td class="px-4 py-4 whitespace-nowrap">
                <span class="drag-handle cursor-grab active:cursor-grabbing text-gray-400 hover:text-gray-600">&#9776;</span>
              </td>
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
          </template>
        </draggable>
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