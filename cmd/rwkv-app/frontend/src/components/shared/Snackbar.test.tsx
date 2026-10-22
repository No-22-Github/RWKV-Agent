import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { SnackbarProvider } from '../../snackbar-context'
import { useSnackbar, type Severity, type ToastOptions } from '../../snackbar'

let show: (message: string, severity?: Severity, options?: ToastOptions) => void = () => {}
function Probe() {
  show = useSnackbar().show
  return null
}

beforeEach(() => {
  vi.useFakeTimers()
  render(<SnackbarProvider><Probe /></SnackbarProvider>)
})
afterEach(() => { cleanup(); vi.useRealTimers() })

it('replaces a loading toast in place with the result of the same key', () => {
  act(() => show('正在请求 /v1/models…', 'loading', { key: 'test' }))
  // loading 不会自己消失。
  act(() => { vi.advanceTimersByTime(20000) })
  expect(screen.getByText('正在请求 /v1/models…')).toBeInTheDocument()
  act(() => show('连接成功', 'success', { key: 'test' }))
  expect(screen.queryByText('正在请求 /v1/models…')).not.toBeInTheDocument()
  expect(screen.getAllByRole('status')).toHaveLength(1)
  act(() => { vi.advanceTimersByTime(4000) })
  act(() => { vi.advanceTimersByTime(200) })
  expect(screen.queryByText('连接成功')).not.toBeInTheDocument()
})

it('stacks at most four toasts, dropping the oldest, and does not repeat the same line', () => {
  act(() => { for (const text of ['一', '二', '三', '四', '五']) show(text) })
  act(() => show('五'))
  expect(screen.queryByText('一')).not.toBeInTheDocument()
  expect(screen.getAllByRole('status').map((item) => item.textContent)).toEqual(['二', '三', '四', '五'])
})

it('keeps an error up while hovered and closes it from its button', () => {
  act(() => show('保存失败', 'error'))
  const toast = screen.getByRole('alert')
  fireEvent.mouseEnter(toast)
  act(() => { vi.advanceTimersByTime(20000) })
  expect(screen.getByText('保存失败')).toBeInTheDocument()
  fireEvent.click(screen.getByRole('button', { name: '关闭通知' }))
  act(() => { vi.advanceTimersByTime(200) })
  expect(screen.queryByText('保存失败')).not.toBeInTheDocument()
})
