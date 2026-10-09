import { afterEach, expect, it, vi } from 'vitest'
import { Clipboard } from '@wailsio/runtime'
import { writeClipboard } from './clipboard'
vi.mock('@wailsio/runtime', () => ({ Clipboard: { SetText: vi.fn() } }))
afterEach(() => {
  vi.resetAllMocks()
  Object.defineProperty(navigator, 'clipboard', { configurable: true, value: undefined })
})
it('writes exact text through the browser', async () => {
  const writeText = vi.fn().mockResolvedValue(undefined)
  Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText } })
  expect(await writeClipboard('中文\nmessage')).toBe(true)
  expect(writeText).toHaveBeenCalledWith('中文\nmessage')
  expect(Clipboard.SetText).not.toHaveBeenCalled()
})
it('uses native clipboard when browser API is missing', async () => {
  vi.mocked(Clipboard.SetText).mockResolvedValue(undefined)
  expect(await writeClipboard('用户消息')).toBe(true)
  expect(Clipboard.SetText).toHaveBeenCalledWith('用户消息')
})
it('uses native clipboard when browser write is rejected', async () => {
  Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: vi.fn().mockRejectedValue(new Error('denied')) } })
  vi.mocked(Clipboard.SetText).mockResolvedValue(undefined)
  expect(await writeClipboard('回答')).toBe(true)
  expect(Clipboard.SetText).toHaveBeenCalledWith('回答')
})
it('reports failure when host cannot write', async () => {
  vi.mocked(Clipboard.SetText).mockRejectedValue(new Error('unavailable'))
  expect(await writeClipboard('message')).toBe(false)
  expect(document.querySelector('textarea')).toBeNull()
})
