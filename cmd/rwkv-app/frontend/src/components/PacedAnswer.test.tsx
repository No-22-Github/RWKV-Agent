import { act, cleanup, render } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import PacedAnswer from './PacedAnswer'

afterEach(() => {
  cleanup()
  vi.useRealTimers()
})

describe('PacedAnswer', () => {
  it('reveals streamed text at a steady pace and finishes it after the run settles', () => {
    vi.useFakeTimers({ toFake: ['requestAnimationFrame', 'cancelAnimationFrame', 'performance'] })
    const text = '杭'.repeat(90)
    const { container, rerender } = render(<PacedAnswer text={text} live />)

    act(() => { vi.advanceTimersByTime(1000) })
    const shownAfterOneSecond = container.textContent?.length || 0
    // 90 字的积压按 max(45, 90/2.5) 字/秒放：一秒后只显示约一半，而不是瞬间追上。
    expect(shownAfterOneSecond).toBeGreaterThan(30)
    expect(shownAfterOneSecond).toBeLessThan(60)

    rerender(<PacedAnswer text={text} live={false} />)
    expect(container.textContent?.length).toBe(shownAfterOneSecond)
    act(() => { vi.advanceTimersByTime(3000) })
    expect(container.textContent).toBe(text)
    expect(container.querySelector('.stream-tok')).toBeNull()
  })
})
