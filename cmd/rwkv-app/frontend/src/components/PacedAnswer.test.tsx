import { act, cleanup, render } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import PacedAnswer from './PacedAnswer'

afterEach(() => {
  cleanup()
  vi.useRealTimers()
})

describe('PacedAnswer', () => {
  it('shows restored progress statically and animates only what comes after it', () => {
    vi.useFakeTimers({ toFake: ['requestAnimationFrame', 'cancelAnimationFrame', 'performance'] })
    const text = '杭'.repeat(90)
    const { container } = render(<PacedAnswer text={text} live initialShown={40} />)

    // 恢复的部分整段都已读过：直接按普通文本显示，不拆字、不淡入。
    expect(container.textContent).toHaveLength(40)
    expect(container.querySelector('.stream-tok')).toBeNull()
    expect(container.querySelector('.stream-static')).not.toBeNull()

    act(() => { vi.advanceTimersByTime(300) })
    expect(container.querySelectorAll('.stream-tok-static')).toHaveLength(40)
    expect(container.querySelectorAll('.stream-tok').length).toBeGreaterThan(0)
  })

  it('reveals streamed text at a steady pace and finishes it after the run settles', () => {
    vi.useFakeTimers({ toFake: ['requestAnimationFrame', 'cancelAnimationFrame', 'performance'] })
    const text = '杭'.repeat(90)
    const settled = vi.fn()
    const { container, rerender } = render(<PacedAnswer text={text} live onSettled={settled} />)

    act(() => { vi.advanceTimersByTime(1000) })
    const shownAfterOneSecond = container.textContent?.length || 0
    // 90 字的积压按 max(45, 90/2.5) 字/秒放：一秒后只显示约一半，而不是瞬间追上。
    expect(shownAfterOneSecond).toBeGreaterThan(30)
    expect(shownAfterOneSecond).toBeLessThan(60)

    rerender(<PacedAnswer text={text} live={false} onSettled={settled} />)
    expect(settled).not.toHaveBeenCalledWith(text)
    expect(container.textContent?.length).toBe(shownAfterOneSecond)
    act(() => { vi.advanceTimersByTime(600) })
    expect(container.textContent).toBe(text)
    expect(settled).toHaveBeenCalledWith(text)
    expect(container.querySelector('.stream-tok')).toBeNull()
  })
  it('finishes a large backlog within the short catch-up window without revealing it all at once', () => {
    vi.useFakeTimers({ toFake: ['requestAnimationFrame', 'cancelAnimationFrame', 'performance'] })
    const text = '杭'.repeat(600)
    const { container, rerender } = render(<PacedAnswer text={text} live />)
    act(() => { vi.advanceTimersByTime(300) })
    const before = container.textContent!.length
    rerender(<PacedAnswer text={text} live={false} />)
    expect(container.textContent).toHaveLength(before)
    act(() => { vi.advanceTimersByTime(200) })
    expect(container.textContent!.length).toBeGreaterThan(before + 80)
    expect(container.textContent!.length).toBeLessThan(text.length)
    act(() => { vi.advanceTimersByTime(650) })
    expect(container.textContent).toBe(text)
    expect(container.querySelector('.stream-tok')).toBeNull()
  })

})
