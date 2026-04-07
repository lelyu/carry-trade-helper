export interface UserPreferences {
  id: string
  user_id: string
  currency_pairs: string[]
  email_frequency: 'hourly' | 'daily' | 'weekly'
  alert_thresholds: Record<string, any> | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface PreferencesUpdate {
  currency_pairs?: string[]
  email_frequency?: 'hourly' | 'daily' | 'weekly'
  alert_thresholds?: Record<string, any> | null
  is_active?: boolean
}