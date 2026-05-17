<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  value: number | null
}>()

const trendClass = computed(() => {
  if (props.value === null || props.value === undefined) return 'text-gray-400'
  if (props.value > 0) return 'text-green-600'
  if (props.value < 0) return 'text-red-600'
  return 'text-gray-400'
})

const trendIcon = computed(() => {
  if (props.value === null || props.value === undefined) return 'flat'
  if (props.value > 0) return 'up'
  if (props.value < 0) return 'down'
  return 'flat'
})

const formatted = computed(() => {
  if (props.value === null || props.value === undefined) return ''
  const abs = Math.abs(props.value)
  if (abs < 0.01) return '0.00%'
  return (props.value > 0 ? '+' : '') + props.value.toFixed(2) + '%'
})
</script>

<template>
  <span :class="trendClass" class="inline-flex items-center text-sm font-medium">
    <svg v-if="trendIcon === 'up'" class="w-4 h-4 mr-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
      <path d="M7 17l5-5 5 5" />
      <path d="M7 11l5-5 5 5" />
    </svg>
    <svg v-else-if="trendIcon === 'down'" class="w-4 h-4 mr-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
      <path d="M7 7l5 5 5-5" />
      <path d="M7 13l5 5 5-5" />
    </svg>
    <svg v-else class="w-4 h-4 mr-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
      <path d="M7 12h10" />
    </svg>
    {{ formatted }}
  </span>
</template>