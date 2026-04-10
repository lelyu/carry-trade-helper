import type { DeviceInfo } from '@/types'

export function useDeviceInfo() {
  const getDeviceInfo = (): DeviceInfo => {
    return {
      user_agent: navigator.userAgent,
      platform: navigator.platform,
      language: navigator.language,
      screen_resolution: `${screen.width}x${screen.height}`,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    }
  }

  return {
    getDeviceInfo,
  }
}