import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, expect, it, vi } from 'vitest'
import { useConversationScroll } from './useConversationScroll'

let resize: () => void
function Fixture({ reset = 0 }: { reset?: number }) {
  const state = useConversationScroll(false, reset)
  return <><div data-testid="scroll" ref={state.scrollRef}><div ref={state.contentRef} /></div>{state.showScrollButton && <button onClick={state.scrollToBottom}>回到底部</button>}</>
}
function setup() {
  vi.useFakeTimers()
  vi.stubGlobal('ResizeObserver', class {
    constructor(callback: () => void) { resize = callback }
    observe() {} disconnect() {}
  })
  const view = render(<Fixture />)
  const node = screen.getByTestId('scroll')
  Object.defineProperty(node, 'clientHeight', { value: 500 })
  let height = 2000
  Object.defineProperty(node, 'scrollHeight', { get: () => height })
  const flush = () => act(() => { vi.advanceTimersByTime(20) })
  const grow = (next: number) => { height = next; act(() => resize()); flush() }
  flush()
  fireEvent.scroll(node)
  return { node, view, flush, grow }
}
afterEach(() => { cleanup(); vi.useRealTimers(); vi.unstubAllGlobals() })

it('cancels a queued follow before the upward wheel produces a scroll event', () => {
  const { node, flush, grow } = setup()
  expect(node.scrollTop).toBe(1500)
  act(() => resize())
  fireEvent.wheel(node, { cancelable: false, deltaY: -1 })
  flush()
  grow(2100)
  expect(node.scrollTop).toBe(1500)
  expect(screen.getByRole('button')).toBeInTheDocument()
  // A delayed programmatic event must not restore following.
  fireEvent.scroll(node)
  grow(2200)
  expect(node.scrollTop).toBe(1500)
  fireEvent.click(screen.getByRole('button'))
  expect(node.scrollTop).toBe(1700)
  grow(2300)
  expect(node.scrollTop).toBe(1800)
})

it('follows actual layout growth and shrinkage, but preserves the paused position', () => {
  const { node, grow, view, flush } = setup()
  grow(2400)
  expect(node.scrollTop).toBe(1900)
  fireEvent.scroll(node)
  grow(1800)
  fireEvent.scroll(node)
  grow(2100)
  expect(node.scrollTop).toBe(1600)
  fireEvent.wheel(node, { cancelable: false, deltaY: -200 })
  node.scrollTop = 1000
  fireEvent.scroll(node)
  grow(2300)
  expect(node.scrollTop).toBe(1000)
  view.rerender(<Fixture reset={1} />)
  flush()
  expect(node.scrollTop).toBe(1800)
})

it('resumes only when downward user scrolling reaches the bottom', () => {
  const { node, grow } = setup()
  fireEvent.wheel(node, { cancelable: false, deltaY: -10 })
  node.scrollTop = 1490
  fireEvent.scroll(node)
  grow(2010)
  expect(node.scrollTop).toBe(1490)
  fireEvent.wheel(node, { cancelable: false, deltaY: 50 })
  node.scrollTop = 1510
  fireEvent.scroll(node)
  grow(2100)
  expect(node.scrollTop).toBe(1600)
})

it('adds only a short wheel ease and cancels momentum on return to bottom', () => {
  const { node, flush } = setup()
  fireEvent.wheel(node, { deltaY: -100 })
  expect(node.scrollTop).toBe(1500)
  flush()
  expect(node.scrollTop).toBeGreaterThan(1400)
  expect(node.scrollTop).toBeLessThan(1500)
  act(() => { vi.advanceTimersByTime(100) })
  expect(node.scrollTop).toBe(1400)
  fireEvent.wheel(node, { deltaY: -100 })
  flush()
  fireEvent.click(screen.getByRole('button'))
  act(() => { vi.advanceTimersByTime(100) })
  expect(node.scrollTop).toBe(1500)
})

it('drops the old wheel target immediately when direction reverses', () => {
  const { node, flush } = setup()
  fireEvent.wheel(node, { deltaY: -200 })
  flush()
  const position = node.scrollTop
  fireEvent.wheel(node, { deltaY: 30 })
  flush()
  expect(node.scrollTop).toBeGreaterThan(position)
  act(() => { vi.advanceTimersByTime(100) })
  expect(node.scrollTop).toBeCloseTo(position + 30)
})
