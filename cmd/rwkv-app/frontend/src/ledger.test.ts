import { describe, expect, it, vi } from 'vitest'
import { Result, Step, Usage } from '../bindings/github.com/no22/RWKV-Agent/api/models'
import { splitModelOutput, traceStats } from './ledger'

vi.mock('@wailsio/runtime', () => ({
  Create: {
    Array: (create: (value: unknown) => unknown) => (values?: unknown[]) => values == null ? values : values.map(create),
    Map: () => (value: unknown) => value,
    Nullable: (create: (value: unknown) => unknown) => (value: unknown) => value == null ? value : create(value),
    Any: (value: unknown) => value,
  },
}))

describe('splitModelOutput', () => {
  it('splits a closed think block into thinking and the following action', () => {
    const { thinking, rest } = splitModelOutput('<think>\n用户想要搜索 Windows 11 的版本号。\n</think>\n<tool_call>{"name":"web_search","arguments":{"query":"win11"}}</tool_call>')
    expect(thinking).toBe('用户想要搜索 Windows 11 的版本号。')
    expect(rest).toBe('<tool_call>{"name":"web_search","arguments":{"query":"win11"}}</tool_call>')
  })

  it('treats an unclosed think block as pure thinking', () => {
    expect(splitModelOutput('<think>只想到了一半，没有结论')).toEqual({ thinking: '只想到了一半，没有结论', rest: '' })
  })

  it('leaves outputs without a think block untouched', () => {
    expect(splitModelOutput('<tool_call>{"name":"read_file"}</tool_call>')).toEqual({ thinking: '', rest: '<tool_call>{"name":"read_file"}</tool_call>' })
    expect(splitModelOutput(undefined)).toEqual({ thinking: '', rest: '' })
  })

  it('drops the fast-thinking framing ">" before a protocol action', () => {
    // 快思考预填把 think 闭合符扣在 prompt 末尾，模型首字节是补位的 ">"。
    const { thinking, rest } = splitModelOutput('>\n<tool_call>{"name":"web_search","arguments":{"query":"win10"}}</tool_call>')
    expect(thinking).toBe('')
    expect(rest).toBe('<tool_call>{"name":"web_search","arguments":{"query":"win10"}}</tool_call>')
  })

  it('unwraps the full-thinking framing ">" so the model think block still splits', () => {
    const { thinking, rest } = splitModelOutput('><think>需要先搜索。</think><tool_call>{"name":"web_search"}</tool_call>')
    expect(thinking).toBe('需要先搜索。')
    expect(rest).toBe('<tool_call>{"name":"web_search"}</tool_call>')
  })

  it('keeps a leading ">" that is ordinary Markdown quoting, not framing', () => {
    expect(splitModelOutput('> 引用的内容')).toEqual({ thinking: '', rest: '> 引用的内容' })
  })
})

describe('traceStats', () => {
  it('sums prompt and completion tokens across steps', () => {
    const trace = new Result({
      output: 'ok',
      steps: [
        new Step({ number: 1, stage: 'decision', usage: new Usage({ promptTokens: 100, completionTokens: 20 }) }),
        new Step({ number: 2, stage: 'answer' }),
        new Step({ number: 3, stage: 'answer', usage: new Usage({ promptTokens: 30, completionTokens: 5 }) }),
      ],
      duration: 0,
      durationMs: 1234,
    })
    expect(traceStats(trace)).toEqual({ durationMs: 1234, tokens: 155 })
  })
})
