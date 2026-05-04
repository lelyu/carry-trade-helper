import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ExchangeRate, InterestRate } from '@/types'
import { exchangeRatesApi, interestRatesApi } from '@/services/api'

export const useRatesStore = defineStore('rates', () => {
  const exchangeRates = ref<ExchangeRate[]>([])
  const interestRates = ref<InterestRate[]>([])
  const historicalExchangeRates = ref<ExchangeRate[]>([])
  const historicalInterestRates = ref<InterestRate[]>([])
  const supportedCurrencies = ref<Record<string, string>>({})
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

  const fetchHistoricalExchangeRates = async (
    base: string,
    target: string,
    from: string,
    to: string
  ) => {
    loading.value = true
    error.value = null
    try {
      const response = await exchangeRatesApi.getHistorical(base, target, from, to)
      historicalExchangeRates.value = response.rates
    } catch (err) {
      error.value = 'Failed to fetch historical exchange rates'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  const fetchHistoricalInterestRates = async (
    countries: string,
    from: string,
    to: string
  ) => {
    loading.value = true
    error.value = null
    try {
      const response = await interestRatesApi.getHistorical(countries, from, to)
      historicalInterestRates.value = response.rates
      return response.rates
    } catch (err) {
      error.value = 'Failed to fetch historical interest rates'
      console.error(err)
      return []
    } finally {
      loading.value = false
    }
  }

  const fetchSupportedCurrencies = async () => {
    try {
      const response = await exchangeRatesApi.getCurrencies()
      supportedCurrencies.value = response.currencies
    } catch (err) {
      console.error('Failed to fetch supported currencies', err)
    }
  }

  return {
    exchangeRates,
    interestRates,
    historicalExchangeRates,
    historicalInterestRates,
    supportedCurrencies,
    loading,
    error,
    fetchLatestExchangeRates,
    fetchLatestInterestRates,
    fetchHistoricalExchangeRates,
    fetchHistoricalInterestRates,
    fetchSupportedCurrencies
  }
})