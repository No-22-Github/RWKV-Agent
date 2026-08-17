export type ThemeMode = 'light' | 'dark'

const STORAGE_KEY = 'rwkv-theme-mode'

export function getInitialTheme(): ThemeMode {
  if (typeof window === 'undefined') return 'light'
  const saved = window.localStorage.getItem(STORAGE_KEY)
  if (saved === 'light' || saved === 'dark') return saved
  return typeof window.matchMedia === 'function' && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export function applyTheme(theme: ThemeMode): void {
  document.documentElement.setAttribute('data-theme', theme)
  document.documentElement.style.colorScheme = theme
}

export function setTheme(theme: ThemeMode): ThemeMode {
  applyTheme(theme)
  if (typeof window !== 'undefined') window.localStorage.setItem(STORAGE_KEY, theme)
  return theme
}

export function toggleTheme(current: ThemeMode): ThemeMode {
  return setTheme(current === 'dark' ? 'light' : 'dark')
}
