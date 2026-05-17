<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import IconExchange from '@/components/icons/IconExchange.vue'
import IconInterest from '@/components/icons/IconInterest.vue'

const route = useRoute()

const activeTab = computed(() => {
  if (route.path.startsWith('/interest')) return 'interest'
  if (route.path.startsWith('/exchange')) return 'exchange'
  return null
})
</script>

<template>
  <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50 md:hidden safe-area-bottom">
    <div class="flex items-center justify-around h-14">
      <router-link
        to="/exchange"
        class="flex flex-col items-center justify-center w-full h-full space-y-0.5"
        :class="activeTab === 'exchange' ? 'text-blue-600' : 'text-gray-400'"
      >
        <IconExchange class="w-5 h-5" />
        <span class="text-[10px] font-medium">Rates</span>
      </router-link>
      <router-link
        to="/interest"
        class="flex flex-col items-center justify-center w-full h-full space-y-0.5"
        :class="activeTab === 'interest' ? 'text-blue-600' : 'text-gray-400'"
      >
        <IconInterest class="w-5 h-5" />
        <span class="text-[10px] font-medium">Interest</span>
      </router-link>
    </div>
  </nav>
</template>

<style scoped>
.safe-area-bottom {
  padding-bottom: env(safe-area-inset-bottom, 0px);
}
</style>