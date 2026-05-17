<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRatesStore } from '@/stores/rates'
import TrendIndicator from '@/components/TrendIndicator.vue'
import TabBar from '@/components/TabBar.vue'

const store = useRatesStore()
const search = ref('')

const filteredRates = computed(() => {
  if (!search.value) return store.interestRates
  const q = search.value.toLowerCase()
  return store.interestRates.filter(r =>
    r.country_code.toLowerCase().includes(q) ||
    r.country_name.toLowerCase().includes(q) ||
    r.currency_code.toLowerCase().includes(q)
  )
})

const formatDate = (dateStr: string | null) => {
  if (!dateStr) return ''
  try {
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  } catch {
    return dateStr
  }
}

onMounted(() => {
  if (store.interestRates.length === 0) {
    store.fetchLatestInterestRates()
  }
})
</script>

<template>
  <div class="h-screen flex flex-col bg-gray-50">
    <header class="bg-white border-b border-gray-200 shrink-0 z-40">
      <div class="px-4 py-3">
        <div class="flex items-center justify-between mb-3">
          <router-link to="/" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M15 18l-6-6 6-6" />
            </svg>
          </router-link>
          <h1 class="text-lg font-semibold text-gray-900">Interest Rates</h1>
          <div class="w-5" />
        </div>
        <div v-if="store.interestAsOf" class="text-xs text-gray-400 text-center mb-2">
          Rates as of {{ formatDate(store.interestAsOf) }}
        </div>
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" />
          </svg>
          <input
            v-model="search"
            type="text"
            placeholder="Search countries..."
            class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>
    </header>

    <main class="flex-1 overflow-y-auto px-4 pt-3 pb-20 md:pb-6">
      <div v-if="store.interestLoading" class="space-y-2 mt-2">
        <div v-for="i in 8" :key="i" class="bg-white rounded-lg p-4 animate-pulse">
          <div class="h-5 bg-gray-100 rounded w-2/3" />
        </div>
      </div>

      <div v-else-if="store.interestError" class="mt-4 p-4 bg-red-50 rounded-lg text-red-700 text-sm">
        {{ store.interestError }}
      </div>

      <div v-else class="space-y-1.5">
        <router-link
          v-for="rate in filteredRates"
          :key="rate.country_code"
          :to="`/interest/${rate.country_code}`"
          class="block bg-white rounded-lg px-4 py-3 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center justify-between">
            <div>
              <div class="font-semibold text-gray-900">{{ rate.country_name }}</div>
              <div class="text-xs text-gray-400">{{ rate.country_code }} &middot; {{ rate.currency_code }}</div>
            </div>
            <div class="text-right">
              <div class="font-mono text-gray-900 font-semibold">
                {{ rate.rate.toFixed(2) }}%
              </div>
              <div class="flex items-center justify-end gap-1">
                <TrendIndicator :value="rate.trend_7d" />
                <span v-if="rate.date" class="text-[10px] text-gray-400">{{ formatDate(rate.date) }}</span>
              </div>
            </div>
          </div>
        </router-link>
      </div>
    </main>

    <TabBar />
  </div>
</template>