import { describe, expect, it } from 'vitest'
import { resultText } from './ToolActivity'

describe('resultText', () => {
  it('shows the file body instead of the JSON envelope', () => {
    const raw = JSON.stringify({ ok: true, tool: 'read_file', result: { path: 'README.md', content: '# 标题\n\n正文' } })
    expect(resultText(raw)).toBe('# 标题\n\n正文')
  })
  it('falls back to pretty JSON of the unwrapped result', () => {
    const raw = JSON.stringify({ ok: true, tool: 'list_files', result: { entries: ['a', 'b'] } })
    expect(resultText(raw)).toBe(JSON.stringify({ entries: ['a', 'b'] }, null, 2))
  })
  it('keeps non-JSON results as they are', () => {
    expect(resultText('plain output')).toBe('plain output')
  })
})
