export interface ExchangeRateItem {
  target_currency: string
  rate: number
  date: string
  trend_7d: number | null
}

export interface ExchangeRateListResponse {
  base: string
  as_of: string | null
  rates: ExchangeRateItem[]
  history_7d: Record<string, Array<{ date: string; rate: string }>> | null
}

export interface InterestRateItem {
  country_code: string
  currency_code: string
  country_name: string
  rate: number
  date: string | null
  trend_7d: number | null
}

export interface InterestRateListResponse {
  as_of: string | null
  rates: InterestRateItem[]
  history_7d: Record<string, Array<{ date: string; rate: string }>> | null
}