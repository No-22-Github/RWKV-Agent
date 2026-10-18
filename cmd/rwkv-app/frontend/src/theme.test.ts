import { afterEach, describe, expect, it, vi } from 'vitest'
import { getThemePreference, resolveTheme, setThemePreference, watchSystemTheme } from './theme'

const originalStorage = Object.getOwnPropertyDescriptor(window, 'localStorage')

afterEach(() => {
  if (originalStorage) {
    Object.defineProperty(window, 'localStorage', originalStorage)
  } else {
    Reflect.deleteProperty(window, 'localStorage')
  }
  document.documentElement.removeAttribute('data-theme')
  document.documentElement.style.colorScheme = ''
})

describe('theme storage', () => {
  it('reads and writes the selected theme when storage is available', () => {
    const getItem = vi.fn(() => 'dark')
    const setItem = vi.fn()
    Object.defineProperty(window, 'localStorage', {
      configurable: true,
      value: { getItem, setItem },
    })

    expect(getThemePreference()).toBe('dark')
    expect(setThemePreference('light')).toBe('light')
    expect(getItem).toHaveBeenCalledWith('rwkv-theme-mode')
    expect(setItem).toHaveBeenCalledWith('rwkv-theme-mode', 'light')
    expect(document.documentElement).toHaveAttribute('data-theme', 'light')
  })

  it('keeps theme initialization usable when storage access is denied', () => {
    Object.defineProperty(window, 'localStorage', {
      configurable: true,
      get: () => {
        throw new DOMException('denied', 'SecurityError')
      },
    })

    expect(getThemePreference()).toBe('system')
    expect(() => setThemePreference('dark')).not.toThrow()
    expect(document.documentElement).toHaveAttribute('data-theme', 'dark')
  })

  it('defaults to following the system and tracks its changes', () => {
    Object.defineProperty(window, 'localStorage', {
      configurable: true,
      value: { getItem: vi.fn(() => null), setItem: vi.fn() },
    })
    let listener: ((event: { matches: boolean }) => void) | undefined
    const matchMedia = vi.fn(() => ({
      matches: true,
      addEventListener: (_: string, fn: (event: { matches: boolean }) => void) => { listener = fn },
      removeEventListener: vi.fn(),
    }))
    const originalMatchMedia = window.matchMedia
    Object.defineProperty(window, 'matchMedia', { configurable: true, value: matchMedia })
    try {
      expect(getThemePreference()).toBe('system')
      expect(resolveTheme('system')).toBe('dark')
      expect(setThemePreference('system')).toBe('dark')
      const seen: string[] = []
      const stop = watchSystemTheme((theme) => seen.push(theme))
      listener?.({ matches: false })
      expect(seen).toEqual(['light'])
      stop()
    } finally {
      Object.defineProperty(window, 'matchMedia', { configurable: true, value: originalMatchMedia })
    }
  })
})
