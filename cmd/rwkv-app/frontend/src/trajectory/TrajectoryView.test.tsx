import { act, cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { Result } from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import TrajectoryView from './TrajectoryView'
import type { AdapterMessage } from './rwkv-adapter'

const started = Date.UTC(2026, 9, 8, 10, 0, 0)

function readmeTurn(): AdapterMessage {
  return {
    id: 'm1',
    role: 'assistant',
    content: '已完成读取。',
    prompt: '读取 README',
    trace: new Result({
      output: '已完成读取。',
      startedAtMs: started,
      durationMs: 1300,
      routeSteps: [{ attempt: 1, request: { prompt: '路由提示', bytes: 12 }, route: 'inspect', bundles: ['workspace'], startedAtMs: started + 5, durationMs: 30 }],
      steps: [
        {
          number: 1, stage: 'model', actionType: 'tool_call', startedAtMs: started + 40, modelDurationMs: 500, firstTokenAtMs: started + 240,
          request: { prompt: '系统\nUser: 读取 README\nAssistant:', bytes: 40, toolsOffered: ['read_file', 'list_files'], maxOutputTokens: 1024 },
          modelOutput: '<tool_call>{"name":"read_file","arguments":{"path":"README.md"}}</tool_call>',
          usage: { promptTokens: 120, completionTokens: 20 },
          tool: 'read_file', toolArguments: '{"path":"README.md"}', toolStartedAtMs: started + 545, toolDurationMs: 300,
          toolResult: '{"ok":true,"tool":"read_file","result":{"path":"README.md","content":"# RWKV Agent\\n本地优先"}}', toolExecuted: true,
        },
        {
          number: 2, stage: 'answer', actionType: 'answer', startedAtMs: started + 860, modelDurationMs: 400,
          request: { prompt: '系统\nUser: 读取 README\nAssistant: <tool_call>…\nTool: …\nAssistant:', bytes: 70 },
          modelOutput: '<answer>已完成读取。</answer>', usage: { promptTokens: 200, completionTokens: 10 },
          protocolError: 'missing </answer>', protocolRepaired: true,
        },
      ],
    }),
  }
}

describe('TrajectoryView', () => {
  afterEach(() => cleanup())

  it('lays out a turn as user, route, steps and tool rows with numbered requests', () => {
    render(<TrajectoryView messages={[readmeTurn()]} live={null} />)
    const ledger = screen.getByRole('table')
    expect(within(ledger).getByText('读取 README')).toBeInTheDocument()
    expect(within(ledger).getByText(/inspect · workspace/)).toBeInTheDocument()
    expect(within(ledger).getAllByText('read_file').length).toBeGreaterThan(0)
    // 工具行在同一行里给出参数 → 结果，结果剥掉外壳只留正文
    expect(within(ledger).getByText(/本地优先/)).toBeInTheDocument()
    expect(within(ledger).getByText('已完成读取。')).toBeInTheDocument()
    // 路由 + 两步 = 三次请求
    expect(screen.getByRole('button', { name: '请求 #1' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '请求 #3' })).toBeInTheDocument()
  })

  it('opens a request with its prompt, offered tools and a diff against the previous request', () => {
    render(<TrajectoryView messages={[readmeTurn()]} live={null} />)
    fireEvent.click(screen.getByRole('button', { name: '请求 #2' }))
    const inspector = screen.getByRole('complementary', { name: '事件详情' })
    expect(within(inspector).getByText('read_file, list_files')).toBeInTheDocument()
    fireEvent.click(within(inspector).getByRole('tab', { name: '提示词' }))
    expect(within(inspector).getByText(/User: 读取 README/)).toBeInTheDocument()
    fireEvent.click(within(inspector).getByRole('tab', { name: '差异' }))
    expect(within(inspector).getByText('与上一次请求相比')).toBeInTheDocument()
  })

  it('shows harness facts and assistant timing in the record inspector', () => {
    render(<TrajectoryView messages={[readmeTurn()]} live={null} />)
    fireEvent.click(screen.getByText('已完成读取。'))
    const inspector = screen.getByRole('complementary', { name: '事件详情' })
    expect(within(inspector).getByText('协议修复')).toBeInTheDocument()
    expect(within(inspector).getByText('已修复 · missing </answer>')).toBeInTheDocument()
  })

  it('filters the ledger by search', async () => {
    render(<TrajectoryView messages={[readmeTurn()]} live={null} />)
    fireEvent.change(screen.getByRole('searchbox', { name: '搜索轨迹' }), { target: { value: 'README.md' } })
    await act(async () => { await new Promise(resolve => setTimeout(resolve, 250)) })
    const ledger = screen.getByRole('table')
    expect(within(ledger).queryByText(/inspect · workspace/)).not.toBeInTheDocument()
    expect(within(ledger).getAllByText('read_file').length).toBeGreaterThan(0)
  })

  it('folds every turn into a one-line summary from the toolbar', () => {
    render(<TrajectoryView messages={[readmeTurn()]} live={null} />)
    fireEvent.click(screen.getByRole('button', { name: '收起所有轮次' }))
    expect(screen.getByRole('button', { name: '展开所有轮次' })).toBeInTheDocument()
    expect(within(screen.getByRole('table')).queryByText(/本地优先/)).not.toBeInTheDocument()
  })

  it('builds the running turn from live events and leaves open records pending', () => {
    render(<TrajectoryView messages={[]} live={{
      id: 'live', prompt: '列出 docs', startedAt: started,
      events: [
        { kind: 'model_start', step: 1, at: started + 10 },
        { kind: 'model_done', step: 1, durationMs: 200, at: started + 210 },
        { kind: 'tool_start', step: 1, tool: 'list_files', arguments: '{"path":"docs"}', at: started + 220 },
      ],
    }} />)
    const ledger = screen.getByRole('table')
    expect(within(ledger).getByText('列出 docs')).toBeInTheDocument()
    expect(within(ledger).getAllByText('list_files').length).toBeGreaterThan(0)
    expect(document.querySelector('[data-running]')).not.toBeNull()
  })
})
