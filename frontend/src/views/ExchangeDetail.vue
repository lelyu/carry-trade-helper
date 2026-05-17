<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRatesStore } from '@/stores/rates'
import LineChart from '@/components/LineChart.vue'
import TrendIndicator from '@/components/TrendIndicator.vue'
import TabBar from '@/components/TabBar.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'

const props = defineProps<{ target: string }>()
const store = useRatesStore()

const CURRENCY_NAMES: Record<string, string> = {
  USD: 'US Dollar', EUR: 'Euro', GBP: 'British Pound', JPY: 'Japanese Yen',
  CHF: 'Swiss Franc', AUD: 'Australian Dollar', CAD: 'Canadian Dollar',
  NZD: 'New Zealand Dollar', CNY: 'Chinese Yuan', HKD: 'Hong Kong Dollar',
}

type Period = '7d' | '30d' | '90d' | '1y'
const selectedPeriod = ref<Period>('7d')
const chartLoading = ref(false)
const chartError = ref(false)

const chartData = ref<Array<{ date: string; rate: number }>>([])
const currentRate = computed(() =>
  store.exchangeRates.find(r => r.target_currency === props.target)
)
const trendValue = computed(() => currentRate.value?.trend_7d ?? null)

const periods: { key: Period; label: string }[] = [
  { key: '7d', label: '7D' },
  { key: '30d', label: '1M' },
  { key: '90d', label: '3M' },
  { key: '1y', label: '1Y' },
]

const periodStartDate = (period: Period): string => {
  const now = new Date()
  const days: Record<Period, number> = { '7d': 7, '30d': 30, '90d': 90, '1y': 365 }
  now.setDate(now.getDate() - days[period])
  return now.toISOString().split('T')[0]
}

const fetchHistoricalData = async (period: Period) => {
  chartLoading.value = true
  chartError.value = false
  const to = new Date().toISOString().split('T')[0]
  const from = periodStartDate(period)
  const base = store.exchangeBase || 'USD'
  const data = await store.fetchHistoricalExchangeRates(base, props.target, from, to)
  chartData.value = data.map((r: { date: string; rate: number }) => ({
    date: r.date,
    rate: Number(r.rate),
  }))
  if (chartData.value.length === 0) {
    chartError.value = true
  }
  chartLoading.value = false
}

const formatDate = (dateStr: string | null) => {
  if (!dateStr) return ''
  try {
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  } catch {
    return dateStr
  }
}

onMounted(() => {
  if (store.exchangeHistory7d && store.exchangeHistory7d[props.target] && store.exchangeHistory7d[props.target].length > 0) {
    chartData.value = store.exchangeHistory7d[props.target].map(p => ({
      date: p.date,
      rate: Number(p.rate),
    }))
  } else {
    fetchHistoricalData('7d')
  }
})

watch(selectedPeriod, (period) => {
  fetchHistoricalData(period)
})
</script>

<template>
  <div class="h-screen flex flex-col bg-gray-50 dark:bg-gray-900 md:pt-14">
    <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shrink-0 z-40">
      <div class="px-4 py-3">
        <div class="flex items-center justify-between mb-2">
          <router-link to="/exchange" class="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M15 18l-6-6 6-6" />
            </svg>
          </router-link>
          <h1 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {{ store.exchangeBase }} / {{ target }}
          </h1>
          <ThemeToggle />
        </div>
      </div>
    </header>

    <main class="flex-1 overflow-y-auto px-4 pt-4 pb-20 md:pb-6">
      <div v-if="currentRate" class="space-y-4">
        <div class="bg-white dark:bg-gray-800 rounded-lg p-5">
          <div class="text-sm text-gray-400 dark:text-gray-500">{{ CURRENCY_NAMES[target] || target }}</div>
          <div class="text-3xl font-mono font-bold text-gray-900 dark:text-gray-100 mt-1">
            {{ currentRate.rate.toFixed(currentRate.rate < 10 ? 4 : 2) }}
          </div>
          <div class="flex items-center gap-2 mt-1">
            <TrendIndicator :value="trendValue" />
            <span v-if="currentRate.date" class="text-xs text-gray-400 dark:text-gray-500">
              as of {{ formatDate(currentRate.date) }}
            </span>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-lg p-4">
          <div class="flex gap-1 mb-3">
            <button
              v-for="p in periods"
              :key="p.key"
              @click="selectedPeriod = p.key"
              class="px-3 py-1.5 text-xs font-medium rounded-md transition-colors"
              :class="selectedPeriod === p.key
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'"
            >
              {{ p.label }}
            </button>
          </div>

          <div v-if="chartData.length > 0" class="w-full">
            <LineChart :data="chartData" color="#3b82f6" :height="250" />
          </div>
          <div v-else-if="chartLoading" class="h-[250px] flex items-center justify-center text-gray-400 dark:text-gray-500 text-sm">
            Loading chart...
          </div>
          <div v-else-if="chartError" class="h-[250px] flex flex-col items-center justify-center text-gray-400 dark:text-gray-500">
            <svg class="w-8 h-8 mb-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M12 9v3.75M9 9h.01M15 9h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="text-sm">Data unavailable for this period</span>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-12 text-gray-400 dark:text-gray-500">
        Currency not found
      </div>
    </main>

    <TabBar />
  </div>
</template>