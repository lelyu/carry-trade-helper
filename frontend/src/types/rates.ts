export interface ExchangeRate {
  id: string
  base_currency: string
  target_currency: string
  rate: number
  date: string
  source: string
  created_at: string
}

export interface InterestRate {
  id: string
  country_code: string
  currency_code: string
  rate: number
  rate_type: string | null
  date: string
  source: string
  created_at: string
}

export interface ExchangeRateListResponse {
  rates: ExchangeRate[]
  count: number
}

export interface InterestRateListResponse {
  rates: InterestRate[]
  count: number
}