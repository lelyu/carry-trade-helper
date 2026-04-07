<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRatesStore } from '@/stores/rates'
import ExchangeRateChart from '@/components/charts/ExchangeRateChart.vue'
import InterestRateChart from '@/components/charts/InterestRateChart.vue'

const ratesStore = useRatesStore()

// Component title
const title = 'Carry Trade Analysis'

// Supported currencies with metadata
const currencyInfo: Record<string, { country: string; name: string }> = {
  USD: { country: 'USA', name: 'US Dollar' },
  EUR: { country: 'EU', name: 'Euro' },
  GBP: { country: 'UK', name: 'British Pound' },
  JPY: { country: 'Japan', name: 'Japanese Yen' },
  CHF: { country: 'Switzerland', name: 'Swiss Franc' },
  AUD: { country: 'Australia', name: 'Australian Dollar' },
  CAD: { country: 'Canada', name: 'Canadian Dollar' },
  NZD: { country: 'New Zealand', name: 'New Zealand Dollar' },
  CNY: { country: 'China', name: 'Chinese Yuan' },
  HKD: { country: 'Hong Kong', name: 'Hong Kong Dollar' }
}

const currencies = Object.keys(currencyInfo)

// Currency selection
const selectedBase = ref('USD')
const selectedTarget = ref('EUR')

// Computed: Current exchange rate
const currentRate = computed(() => {
  const rate = ratesStore.exchangeRates.find(
    r => r.base_currency === selectedBase.value && 
         r.target_currency === selectedTarget.value
  )
  return rate ? parseFloat(String(rate.rate)) : null
})

// Computed: Last updated
const lastUpdated = computed(() => {
  const rate = ratesStore.exchangeRates.find(
    r => r.base_currency === selectedBase.value && 
         r.target_currency === selectedTarget.value
  )
  return rate ? new Date(rate.created_at) : null
})

// Computed: Base currency interest rate
const baseInterestRate = computed(() => {
  const rate = ratesStore.interestRates.find(
    r => r.currency_code === selectedBase.value
  )
  return rate ? parseFloat(String(rate.rate)) : null
})

// Computed: Target currency interest rate
const targetInterestRate = computed(() => {
  const rate = ratesStore.interestRates.find(
    r => r.currency_code === selectedTarget.value
  )
  return rate ? parseFloat(String(rate.rate)) : null
})

// Computed: Interest rate differential
const interestDifferential = computed(() => {
  if (baseInterestRate.value !== null && targetInterestRate.value !== null) {
    return baseInterestRate.value - targetInterestRate.value
  }
  return null
})

// Computed: Carry trade assessment
const carryTradeAssessment = computed(() => {
  if (interestDifferential.value === null) return null
  
  if (interestDifferential.value > 0.5) {
    return { 
      status: 'favorable', 
      color: 'text-green-600', 
      bgColor: 'bg-green-50 border-green-200',
      label: 'Favorable for Carry Trade',
      description: `Long ${selectedBase.value}/Short ${selectedTarget.value} earns positive carry of ${interestDifferential.value.toFixed(2)}%`
    }
  } else if (interestDifferential.value < -0.5) {
    return { 
      status: 'unfavorable', 
      color: 'text-red-600',
      bgColor: 'bg-red-50 border-red-200',
      label: 'Unfavorable for Carry Trade',
      description: `Interest rate differential is ${interestDifferential.value.toFixed(2)}%. Consider ${selectedTarget.value}/${selectedBase.value} instead.`
    }
  } else {
    return { 
      status: 'marginal', 
      color: 'text-gray-600',
      bgColor: 'bg-gray-50 border-gray-200',
      label: 'Marginal Opportunity',
      description: 'Interest rate differential is minimal. Limited carry opportunity.'
    }
  }
})

// Computed: Exchange rate chart data (last 90 days)
const exchangeRateChartData = computed(() => {
  const ninetyDaysAgo = new Date()
  ninetyDaysAgo.setDate(ninetyDaysAgo.getDate() - 90)
  
  return ratesStore.historicalExchangeRates
    .filter(r => 
      r.base_currency === selectedBase.value && 
      r.target_currency === selectedTarget.value &&
      new Date(r.date) >= ninetyDaysAgo
    )
    .map(rate => ({
      date: new Date(rate.date),
      rate: parseFloat(String(rate.rate))
    }))
    .sort((a, b) => a.date.getTime() - b.date.getTime())
})

// Computed: Interest rate comparison data
const interestRateChartData = computed(() => {
  const data = []
  
  if (baseInterestRate.value !== null) {
    data.push({
      currency: selectedBase.value,
      country: currencyInfo[selectedBase.value].country,
      rate: baseInterestRate.value
    })
  }
  
  if (targetInterestRate.value !== null) {
    data.push({
      currency: selectedTarget.value,
      country: currencyInfo[selectedTarget.value].country,
      rate: targetInterestRate.value
    })
  }
  
  return data
})

// Computed: Summary statistics
const summaryStats = computed(() => {
  if (exchangeRateChartData.value.length === 0) return null
  
  const rates = exchangeRateChartData.value.map(d => d.rate)
  const min = Math.min(...rates)
  const max = Math.max(...rates)
  const avg = rates.reduce((a, b) => a + b, 0) / rates.length
  const current = currentRate.value || 0
  
  return {
    min,
    max,
    avg,
    current,
    range: max - min,
    volatility: ((max - min) / avg * 100).toFixed(2)
  }
})

// Helper: Get date 90 days ago
const getLast90Days = () => {
  const date = new Date()
  date.setDate(date.getDate() - 90)
  return date
}

// Methods: Fetch data
const fetchAllData = async () => {
  const ninetyDaysAgo = getLast90Days()
  const today = new Date()
  
  await Promise.all([
    ratesStore.fetchLatestExchangeRates(selectedBase.value),
    ratesStore.fetchLatestInterestRates(),
    ratesStore.fetchHistoricalExchangeRates(
      selectedBase.value,
      selectedTarget.value,
      ninetyDaysAgo.toISOString().split('T')[0],
      today.toISOString().split('T')[0]
    )
  ])
}

// Manual refresh
const refreshRates = async () => {
  await fetchAllData()
}

// Lifecycle: Fetch on mount
onMounted(async () => {
  await fetchAllData()
})

// Watchers: Refetch on currency change
watch([selectedBase, selectedTarget], async () => {
  await fetchAllData()
})
</script>

<template>
  <div class="max-w-7xl mx-auto">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900">{{ title }}</h1>
      <p class="mt-2 text-gray-600">
        Analyze currency pairs and interest rate differentials for carry trade opportunities
      </p>
    </div>

    <!-- Loading Skeleton -->
    <div v-if="ratesStore.loading && !currentRate" class="space-y-6">
      <div class="animate-pulse">
        <div class="h-48 bg-gray-200 rounded-lg"></div>
      </div>
      <div class="animate-pulse">
        <div class="h-64 bg-gray-200 rounded-lg"></div>
      </div>
      <div class="grid grid-cols-2 gap-6">
        <div class="animate-pulse">
          <div class="h-96 bg-gray-200 rounded-lg"></div>
        </div>
        <div class="animate-pulse">
          <div class="h-96 bg-gray-200 rounded-lg"></div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="space-y-6">
      <!-- Currency Selection Panel -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold mb-4">Currency Pair Selection</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Base Currency -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Base Currency (Long Position)
            </label>
            <select 
              v-model="selectedBase"
              class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option v-for="currency in currencies" :key="currency" :value="currency">
                {{ currency }} - {{ currencyInfo[currency].name }} ({{ currencyInfo[currency].country }})
              </option>
            </select>
          </div>

          <!-- Target Currency -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Target Currency (Short Position)
            </label>
            <select 
              v-model="selectedTarget"
              class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option v-for="currency in currencies" :key="currency" :value="currency">
                {{ currency }} - {{ currencyInfo[currency].name }} ({{ currencyInfo[currency].country }})
              </option>
            </select>
          </div>
        </div>

        <div class="mt-4 flex justify-end">
          <button
            @click="refreshRates"
            :disabled="ratesStore.loading"
            class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ ratesStore.loading ? 'Refreshing...' : 'Refresh Rates' }}
          </button>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="ratesStore.error" class="bg-red-50 border border-red-200 rounded-lg p-4">
        <p class="text-red-800">{{ ratesStore.error }}</p>
      </div>

      <!-- Key Metrics Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
        <!-- Exchange Rate -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <p class="text-sm text-gray-600 mb-1">Exchange Rate</p>
          <p class="text-3xl font-bold text-gray-900">
            {{ currentRate ? currentRate.toFixed(4) : '—' }}
          </p>
          <p class="text-sm text-gray-500 mt-1">
            {{ selectedBase }}/{{ selectedTarget }}
          </p>
        </div>

        <!-- Base Interest Rate -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <p class="text-sm text-gray-600 mb-1">Base Interest Rate</p>
          <p class="text-3xl font-bold text-gray-900">
            {{ baseInterestRate ? baseInterestRate.toFixed(2) + '%' : '—' }}
          </p>
          <p class="text-sm text-gray-500 mt-1">{{ currencyInfo[selectedBase]?.country }}</p>
        </div>

        <!-- Target Interest Rate -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <p class="text-sm text-gray-600 mb-1">Target Interest Rate</p>
          <p class="text-3xl font-bold text-gray-900">
            {{ targetInterestRate ? targetInterestRate.toFixed(2) + '%' : '—' }}
          </p>
          <p class="text-sm text-gray-500 mt-1">{{ currencyInfo[selectedTarget]?.country }}</p>
        </div>

        <!-- Interest Differential -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <p class="text-sm text-gray-600 mb-1">Interest Rate Spread</p>
          <p 
            class="text-3xl font-bold"
            :class="interestDifferential && interestDifferential > 0 ? 'text-green-600' : interestDifferential && interestDifferential < 0 ? 'text-red-600' : 'text-gray-900'"
          >
            {{ interestDifferential ? (interestDifferential > 0 ? '+' : '') + interestDifferential.toFixed(2) + '%' : '—' }}
          </p>
        </div>
      </div>

      <!-- Carry Trade Assessment -->
      <div 
        v-if="carryTradeAssessment" 
        :class="[carryTradeAssessment.bgColor, 'border rounded-lg shadow-md p-6']"
      >
        <h3 class="text-xl font-semibold mb-2" :class="carryTradeAssessment.color">
          {{ carryTradeAssessment.label }}
        </h3>
        <p class="text-gray-700">
          {{ carryTradeAssessment.description }}
        </p>
        <div v-if="interestDifferential !== null" class="mt-4 text-sm text-gray-600">
          <p class="mb-1">
            <strong>Interest Rate Differential:</strong> 
            {{ (interestDifferential > 0 ? '+' : '') + interestDifferential.toFixed(2) }}%
          </p>
          <p>
            <strong>Strategy:</strong> 
            <span v-if="interestDifferential > 0">
              Borrow {{ selectedTarget }} at {{ targetInterestRate?.toFixed(2) }}%, invest in {{ selectedBase }} at {{ baseInterestRate?.toFixed(2) }}% for positive carry
            </span>
            <span v-else>
              Borrow {{ selectedBase }} at {{ baseInterestRate?.toFixed(2) }}%, invest in {{ selectedTarget }} at {{ targetInterestRate?.toFixed(2) }}% for positive carry
            </span>
          </p>
        </div>
      </div>

      <!-- Summary Statistics -->
      <div v-if="summaryStats" class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-lg font-semibold mb-4">Rate Statistics (90-Day Period)</h3>
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div>
            <p class="text-sm text-gray-600">Current</p>
            <p class="text-lg font-semibold">{{ summaryStats.current.toFixed(4) }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-600">Min</p>
            <p class="text-lg font-semibold">{{ summaryStats.min.toFixed(4) }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-600">Max</p>
            <p class="text-lg font-semibold">{{ summaryStats.max.toFixed(4) }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-600">Average</p>
            <p class="text-lg font-semibold">{{ summaryStats.avg.toFixed(4) }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-600">Volatility</p>
            <p class="text-lg font-semibold">{{ summaryStats.volatility }}%</p>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Exchange Rate History Chart -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-lg font-semibold mb-4">
            {{ selectedBase }}/{{ selectedTarget }} Exchange Rate (90 Days)
          </h3>
          <ExchangeRateChart 
            v-if="exchangeRateChartData.length > 0"
            :data="exchangeRateChartData"
            :title="`${selectedBase}/${selectedTarget} Historical Rates`"
          />
          <div v-else class="text-center text-gray-500 py-12">
            No historical data available
          </div>
        </div>

        <!-- Interest Rate Comparison Chart -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-lg font-semibold mb-4">Interest Rate Comparison</h3>
          <InterestRateChart 
            v-if="interestRateChartData.length > 0"
            :data="interestRateChartData"
            title="Interest Rates by Currency"
          />
          <div v-else class="text-center text-gray-500 py-12">
            No interest rate data available
          </div>
        </div>
      </div>

      <!-- Last Updated -->
      <div v-if="lastUpdated" class="flex items-center text-sm text-gray-500">
        Last updated: {{ lastUpdated.toLocaleString() }}
      </div>
    </div>
  </div>
</template>