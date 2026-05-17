import { ref, watch } from 'vue'

type Theme = 'light' | 'dark' | 'system'

const getStoredTheme = (): Theme => {
  if (typeof window === 'undefined') return 'system'
  const stored = localStorage.getItem('theme') as Theme | null
  if (stored) return stored
  return 'system'
}

const theme = ref<Theme>(getStoredTheme())
const resolvedTheme = ref<'light' | 'dark'>('light')

function applyTheme() {
  let effective: 'light' | 'dark'
  if (theme.value === 'system') {
    effective = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  } else {
    effective = theme.value
  }
  resolvedTheme.value = effective
  document.documentElement.classList.toggle('dark', effective === 'dark')
  document.documentElement.style.colorScheme = effective
}

function setTheme(newTheme: Theme) {
  theme.value = newTheme
  localStorage.setItem('theme', newTheme)
  applyTheme()
}

function toggleTheme() {
  if (resolvedTheme.value === 'dark') {
    setTheme('light')
  } else {
    setTheme('dark')
  }
}

if (typeof window !== 'undefined') {
  applyTheme()
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (theme.value === 'system') applyTheme()
  })
}

watch(theme, applyTheme)

export function useTheme() {
  return { theme, resolvedTheme, setTheme, toggleTheme }
}