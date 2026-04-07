import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ExchangeRate, InterestRate } from '@/types'
import { exchangeRatesApi, interestRatesApi } from '@/services/api'

export const useRatesStore = defineStore('rates', () => {
  const exchangeRates = ref<ExchangeRate[]>([])
  const interestRates = ref<InterestRate[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchLatestExchangeRates = async (base: string = 'USD') => {
    loading.value = true
    error.value = null
    try {
      const response = await exchangeRatesApi.getLatest(base)
      exchangeRates.value = response.rates
    } catch (err) {
      error.value = 'Failed to fetch exchange rates'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  const fetchLatestInterestRates = async (countries?: string) => {
    loading.value = true
    error.value = null
    try {
      const response = await interestRatesApi.getLatest(countries)
      interestRates.value = response.rates
    } catch (err) {
      error.value = 'Failed to fetch interest rates'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  return {
    exchangeRates,
    interestRates,
    loading,
    error,
    fetchLatestExchangeRates,
    fetchLatestInterestRates
  }
})