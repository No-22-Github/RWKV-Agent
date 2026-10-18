/* 实际渲染用的配色。 */
export type ThemeMode = 'light' | 'dark'
/* 用户的选择：跟随系统或固定一种。没存过时默认跟随系统。 */
export type ThemePreference = 'system' | ThemeMode

const STORAGE_KEY = 'rwkv-theme-mode'
const DARK_QUERY = '(prefers-color-scheme: dark)'

function getThemeStorage(): Storage | undefined {
  if (typeof window === 'undefined') return undefined
  try {
    const storage = window.localStorage
    return typeof storage?.getItem === 'function' && typeof storage.setItem === 'function' ? storage : undefined
  } catch {
    return undefined
  }
}

function getStoredPreference(): string | null {
  try {
    return getThemeStorage()?.getItem(STORAGE_KEY) ?? null
  } catch {
    return null
  }
}

function storePreference(preference: ThemePreference): void {
  try {
    getThemeStorage()?.setItem(STORAGE_KEY, preference)
  } catch {
    return
  }
}

function systemTheme(): ThemeMode {
  return typeof window !== 'undefined' && typeof window.matchMedia === 'function' && window.matchMedia(DARK_QUERY).matches ? 'dark' : 'light'
}

export function getThemePreference(): ThemePreference {
  const saved = getStoredPreference()
  return saved === 'light' || saved === 'dark' ? saved : 'system'
}

export function resolveTheme(preference: ThemePreference): ThemeMode {
  return preference === 'system' ? systemTheme() : preference
}

export function applyTheme(theme: ThemeMode): void {
  document.documentElement.setAttribute('data-theme', theme)
  document.documentElement.style.colorScheme = theme
}

/* 存下选择并立即应用，返回实际生效的配色。 */
export function setThemePreference(preference: ThemePreference): ThemeMode {
  storePreference(preference)
  const theme = resolveTheme(preference)
  applyTheme(theme)
  return theme
}

/* 系统明暗切换时回调；返回取消订阅函数。没有 matchMedia 的环境什么也不做。 */
export function watchSystemTheme(onChange: (theme: ThemeMode) => void): () => void {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return () => {}
  const query = window.matchMedia(DARK_QUERY)
  const listener = (event: MediaQueryListEvent) => onChange(event.matches ? 'dark' : 'light')
  query.addEventListener?.('change', listener)
  return () => query.removeEventListener?.('change', listener)
}
