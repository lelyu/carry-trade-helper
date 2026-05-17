<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import IconExchange from '@/components/icons/IconExchange.vue'
import IconInterest from '@/components/icons/IconInterest.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'

const route = useRoute()

const activeTab = computed(() => {
  if (route.path.startsWith('/interest')) return 'interest'
  if (route.path.startsWith('/exchange')) return 'exchange'
  return null
})
</script>

<template>
  <nav class="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 z-50 md:hidden safe-area-bottom">
    <div class="flex items-center justify-around h-14">
      <router-link
        to="/exchange"
        class="flex flex-col items-center justify-center w-full h-full space-y-0.5"
        :class="activeTab === 'exchange' ? 'text-blue-600 dark:text-blue-400' : 'text-gray-400 dark:text-gray-500'"
      >
        <IconExchange class="w-5 h-5" />
        <span class="text-[10px] font-medium">Rates</span>
      </router-link>
      <router-link
        to="/interest"
        class="flex flex-col items-center justify-center w-full h-full space-y-0.5"
        :class="activeTab === 'interest' ? 'text-blue-600 dark:text-blue-400' : 'text-gray-400 dark:text-gray-500'"
      >
        <IconInterest class="w-5 h-5" />
        <span class="text-[10px] font-medium">Interest</span>
      </router-link>
    </div>
  </nav>

  <nav class="hidden md:flex fixed top-0 left-0 right-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 z-40">
    <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between w-full">
      <div class="flex items-center gap-6">
        <router-link to="/" class="text-lg font-bold text-gray-900 dark:text-gray-100">Carry Trade Helper</router-link>
        <div class="flex items-center gap-1">
          <router-link
            to="/exchange"
            class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
            :class="activeTab === 'exchange'
              ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
              : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'"
          >
            Exchange Rates
          </router-link>
          <router-link
            to="/interest"
            class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
            :class="activeTab === 'interest'
              ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
              : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'"
          >
            Interest Rates
          </router-link>
        </div>
      </div>
      <ThemeToggle />
    </div>
  </nav>
</template>

<style scoped>
.safe-area-bottom {
  padding-bottom: env(safe-area-inset-bottom, 0px);
}
</style>