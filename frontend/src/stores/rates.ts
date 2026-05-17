import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ExchangeRateItem, InterestRateItem, ExchangeRateListResponse, InterestRateListResponse } from '@/types'
import { exchangeRatesApi, interestRatesApi } from '@/services/api'

export const useRatesStore = defineStore('rates', () => {
  const exchangeRates = ref<ExchangeRateItem[]>([])
  const interestRates = ref<InterestRateItem[]>([])
  const exchangeBase = ref('USD')
  const exchangeAsOf = ref<string | null>(null)
  const interestAsOf = ref<string | null>(null)
  const exchangeHistory7d = ref<Record<string, Array<{ date: string; rate: string }>> | null>(null)
  const interestHistory7d = ref<Record<string, Array<{ date: string; rate: string }>> | null>(null)
  const supportedCurrencies = ref<Record<string, string>>({})
  const exchangeLoading = ref(false)
  const interestLoading = ref(false)
  const exchangeError = ref<string | null>(null)
  const interestError = ref<string | null>(null)
  const exchangeStale = ref(false)
  const interestStale = ref(false)

  const fetchLatestExchangeRates = async (base: string = 'USD') => {
    exchangeLoading.value = true
    exchangeError.value = null
    try {
      const response: ExchangeRateListResponse = await exchangeRatesApi.getLatest(base)
      exchangeRates.value = response.rates
      exchangeAsOf.value = response.as_of
      exchangeHistory7d.value = response.history_7d
      exchangeBase.value = base
    } catch (err) {
      exchangeError.value = 'Failed to fetch exchange rates'
      console.error(err)
    } finally {
      exchangeLoading.value = false
    }
  }

  const fetchLatestInterestRates = async () => {
    interestLoading.value = true
    interestError.value = null
    try {
      const response: InterestRateListResponse = await interestRatesApi.getLatest()
      interestRates.value = response.rates
      interestAsOf.value = response.as_of
      interestHistory7d.value = response.history_7d
    } catch (err) {
      interestError.value = 'Failed to fetch interest rates'
      console.error(err)
    } finally {
      interestLoading.value = false
    }
  }

  const fetchHistoricalExchangeRates = async (base: string, target: string, from: string, to: string) => {
    try {
      const response = await exchangeRatesApi.getHistorical(base, target, from, to)
      return response.rates
    } catch (err) {
      console.error(err)
      return []
    }
  }

  const fetchHistoricalInterestRates = async (country: string, from: string, to: string) => {
    try {
      const response = await interestRatesApi.getHistorical(country, from, to)
      return response.rates
    } catch (err) {
      console.error(err)
      return []
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
    exchangeBase,
    exchangeAsOf,
    interestAsOf,
    exchangeHistory7d,
    interestHistory7d,
    supportedCurrencies,
    exchangeLoading,
    interestLoading,
    exchangeError,
    interestError,
    exchangeStale,
    interestStale,
    fetchLatestExchangeRates,
    fetchLatestInterestRates,
    fetchHistoricalExchangeRates,
    fetchHistoricalInterestRates,
    fetchSupportedCurrencies,
  }
})