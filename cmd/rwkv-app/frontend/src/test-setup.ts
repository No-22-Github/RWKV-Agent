import '@testing-library/jest-dom/vitest'
import { vi } from 'vitest'

Element.prototype.scrollIntoView = () => undefined

Object.defineProperty(window, 'matchMedia', {
  configurable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(() => false),
  })),
})

// jsdom 没有 Canvas：像素动画只占位不绘制，免得每次挂载都打一条 Not implemented。
HTMLCanvasElement.prototype.getContext = (() => null) as typeof HTMLCanvasElement.prototype.getContext
