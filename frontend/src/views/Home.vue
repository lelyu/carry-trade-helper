<script setup lang="ts">
import ExchangeRatePanel from '@/components/panels/ExchangeRatePanel.vue'
import InterestRatePanel from '@/components/panels/InterestRatePanel.vue'
import FloatingAiBox from '@/components/common/FloatingAiBox.vue'
</script>

<template>
  <div class="max-w-7xl mx-auto">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">
        Carry Trade Helper — Currency Converter & Interest Rates
      </h1>
      <p class="mt-3 text-gray-600 leading-relaxed">
        Convert currencies in real-time across 40+ pairs and compare central bank interest rates worldwide. Our AI-powered assistant identifies carry trade opportunities by analyzing interest rate differentials and exchange rate trends, helping you make informed trading decisions.
      </p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <ExchangeRatePanel />
      <InterestRatePanel />
    </div>

    <FloatingAiBox />
  </div>
</template>