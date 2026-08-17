export type ThemeMode = 'light' | 'dark'

const STORAGE_KEY = 'rwkv-theme-mode'

function getThemeStorage(): Storage | undefined {
  if (typeof window === 'undefined') return undefined
  try {
    const storage = window.localStorage
    return typeof storage?.getItem === 'function' && typeof storage.setItem === 'function' ? storage : undefined
  } catch {
    return undefined
  }
}

function getStoredTheme(): string | null {
  try {
    return getThemeStorage()?.getItem(STORAGE_KEY) ?? null
  } catch {
    return null
  }
}

function storeTheme(theme: ThemeMode): void {
  try {
    getThemeStorage()?.setItem(STORAGE_KEY, theme)
  } catch {
    return
  }
}

export function getInitialTheme(): ThemeMode {
  if (typeof window === 'undefined') return 'light'
  const saved = getStoredTheme()
  if (saved === 'light' || saved === 'dark') return saved
  return typeof window.matchMedia === 'function' && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export function applyTheme(theme: ThemeMode): void {
  document.documentElement.setAttribute('data-theme', theme)
  document.documentElement.style.colorScheme = theme
}

export function setTheme(theme: ThemeMode): ThemeMode {
  applyTheme(theme)
  storeTheme(theme)
  return theme
}

export function toggleTheme(current: ThemeMode): ThemeMode {
  return setTheme(current === 'dark' ? 'light' : 'dark')
}
