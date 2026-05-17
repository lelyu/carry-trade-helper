const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path: string, options?: RequestInit) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(error.detail || 'Request failed')
  }
  return res.json()
}

export const exchangeRatesApi = {
  getLatest: (base: string = 'USD'): Promise<import('@/types').ExchangeRateListResponse> =>
    request(`/api/exchange-rates/latest?base=${base}`),

  getHistorical: (base: string, target: string, from: string, to: string) =>
    request(`/api/exchange-rates/historical?base=${base}&target=${target}&from=${from}&to=${to}`),

  getCurrencies: () =>
    request('/api/exchange-rates/currencies'),
}

export const interestRatesApi = {
  getLatest: (): Promise<import('@/types').InterestRateListResponse> =>
    request('/api/interest-rates/latest'),

  getHistorical: (country: string, from: string, to: string) =>
    request(`/api/interest-rates/historical?country=${country}&from=${from}&to=${to}`),
}