import { afterEach, describe, expect, it, vi } from 'vitest'
import { getInitialTheme, setTheme } from './theme'

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

    expect(getInitialTheme()).toBe('dark')
    expect(setTheme('light')).toBe('light')
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

    expect(getInitialTheme()).toBe('light')
    expect(() => setTheme('dark')).not.toThrow()
    expect(document.documentElement).toHaveAttribute('data-theme', 'dark')
  })
})
