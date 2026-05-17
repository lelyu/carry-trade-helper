<script setup lang="ts">
import { onMounted } from 'vue'
import { useRatesStore } from '@/stores/rates'
import TabBar from '@/components/TabBar.vue'
import AppFooter from '@/components/common/AppFooter.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'

const store = useRatesStore()

const formatDate = (dateStr: string | null) => {
  if (!dateStr) return ''
  try {
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  } catch {
    return dateStr
  }
}

onMounted(() => {
  store.fetchLatestExchangeRates()
  store.fetchLatestInterestRates()
  store.fetchSupportedCurrencies()
})
</script>

<template>
  <div class="h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
    <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shrink-0">
      <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <h1 class="text-lg font-bold text-gray-900 dark:text-gray-100">Carry Trade Helper</h1>
        <div class="flex items-center gap-2">
          <ThemeToggle />
        </div>
      </div>
    </header>

    <main class="flex-1 overflow-y-auto max-w-7xl mx-auto w-full px-4 py-6 pb-20 md:pb-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 md:h-full">
        <router-link to="/exchange" class="block">
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-5 hover:shadow-md transition-shadow cursor-pointer">
            <div class="flex items-center justify-between mb-3">
              <h2 class="text-base font-semibold text-gray-900 dark:text-gray-100">Exchange Rates</h2>
              <span v-if="store.exchangeAsOf" class="text-xs text-gray-400 dark:text-gray-500">
                {{ formatDate(store.exchangeAsOf) }}
              </span>
            </div>
            <div v-if="store.exchangeLoading" class="space-y-2">
              <div v-for="i in 3" :key="i" class="h-6 bg-gray-100 dark:bg-gray-700 rounded animate-pulse" />
            </div>
            <div v-else-if="store.exchangeError" class="text-red-600 dark:text-red-400 text-sm">{{ store.exchangeError }}</div>
            <div v-else class="space-y-1.5">
              <div v-for="rate in store.exchangeRates.slice(0, 5)" :key="rate.target_currency" class="flex justify-between text-sm">
                <span class="text-gray-600 dark:text-gray-400">{{ rate.target_currency }}</span>
                <span class="font-mono text-gray-900 dark:text-gray-100">{{ rate.rate.toFixed(rate.rate < 10 ? 4 : 2) }}</span>
              </div>
              <div v-if="store.exchangeRates.length > 5" class="text-blue-600 dark:text-blue-400 text-xs pt-1">View all &rarr;</div>
            </div>
          </div>
        </router-link>

        <router-link to="/interest" class="block">
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-5 hover:shadow-md transition-shadow cursor-pointer">
            <div class="flex items-center justify-between mb-3">
              <h2 class="text-base font-semibold text-gray-900 dark:text-gray-100">Interest Rates</h2>
              <span v-if="store.interestAsOf" class="text-xs text-gray-400 dark:text-gray-500">
                {{ formatDate(store.interestAsOf) }}
              </span>
            </div>
            <div v-if="store.interestLoading" class="space-y-2">
              <div v-for="i in 3" :key="i" class="h-6 bg-gray-100 dark:bg-gray-700 rounded animate-pulse" />
            </div>
            <div v-else-if="store.interestError" class="text-red-600 dark:text-red-400 text-sm">{{ store.interestError }}</div>
            <div v-else class="space-y-1.5">
              <div v-for="rate in store.interestRates.slice(0, 5)" :key="rate.country_code" class="flex justify-between text-sm">
                <span class="text-gray-600 dark:text-gray-400">{{ rate.country_name }}</span>
                <span class="font-mono text-gray-900 dark:text-gray-100">{{ rate.rate.toFixed(2) }}%</span>
              </div>
              <div v-if="store.interestRates.length > 5" class="text-blue-600 dark:text-blue-400 text-xs pt-1">View all &rarr;</div>
            </div>
          </div>
        </router-link>
      </div>
    </main>

    <AppFooter />
    <TabBar />
  </div>
</template>