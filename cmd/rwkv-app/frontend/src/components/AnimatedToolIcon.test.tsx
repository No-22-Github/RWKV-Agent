import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import ToolActivity from './ToolActivity'
import AnimatedToolIcon, { animatedToolIcon } from './AnimatedToolIcon'
import { SearchIcon } from './icons/animated/search'
import { FileFetchIcon } from './icons/animated/file-fetch'

afterEach(cleanup)

describe('tool row icons', () => {
  it('animates only rows whose call is still running', () => {
    const { container, rerender } = render(<ToolActivity running calls={[
      { id: 'a', tool: 'get_weather', arguments: '{"location":"合肥"}', status: 'completed', durationMs: 2500 },
      { id: 'b', tool: 'web_search', arguments: '{"query":"合肥 景点"}', status: 'running' },
    ]} />)
    // 收起时：标题行用正在执行的工具图标代替 R 点阵。
    expect(container.querySelectorAll('[data-running="true"]')).toHaveLength(1)
    expect(screen.queryByLabelText('Agent 运行中')).toBeNull()
    fireEvent.click(screen.getByRole('button', { expanded: false }))
    expect(container.querySelectorAll('.tool-activity-panel [data-running="true"]')).toHaveLength(1)
    // 运行中右侧是实时计时而不是转圈。
    expect(screen.getByRole('timer', { name: '运行中' })).toHaveTextContent(/^\d+\.\d s$/)

    rerender(<ToolActivity calls={[
      { id: 'a', tool: 'get_weather', arguments: '{"location":"合肥"}', status: 'completed', durationMs: 2500 },
      { id: 'b', tool: 'web_search', arguments: '{"query":"合肥 景点"}', status: 'completed', durationMs: 1900 },
    ]} />)
    expect(container.querySelectorAll('[data-running="true"]')).toHaveLength(0)
    expect(screen.queryByRole('timer')).toBeNull()
    expect(screen.getByText('1.9 s')).toBeInTheDocument()
    expect(container.querySelectorAll('.tool-activity-panel svg[viewBox="0 0 24 24"]').length).toBeGreaterThanOrEqual(2)
  })

  it('shows the R mark while the model decides between tool calls', () => {
    render(<ToolActivity running liveLabel="步骤 2 · 正在决定下一步" calls={[
      { id: 'a', tool: 'get_weather', arguments: '{"location":"合肥"}', status: 'completed', durationMs: 1400 },
    ]} />)
    expect(screen.getByLabelText('Agent 运行中')).toBeInTheDocument()
    expect(document.querySelector('[data-running="true"]')).toBeNull()
  })

  it('keeps a settled R mark on the summary row once the turn is done', () => {
    render(<ToolActivity calls={[
      { id: 'a', tool: 'get_weather', arguments: '{"location":"合肥"}', status: 'completed', durationMs: 1400 },
    ]} />)
    expect(screen.getByText('查询了天气')).toBeInTheDocument()
    expect(screen.queryByLabelText('Agent 运行中')).toBeNull()
    expect(document.querySelector('[aria-label="Agent 已完成"]')).not.toBeNull()
  })
})

const toolNames = ['list_files', 'read_file', 'read_lines', 'search_text', 'write_file', 'append_file', 'replace_lines', 'web_search', 'web_fetch', 'spawn_agents', 'calculator', 'data_query', 'get_weather', 'bash', 'datetime', 'load_tools', 'custom_tool']

it.each(toolNames)('supports running and settled icons for %s', (tool) => {
  const { container, rerender } = render(<AnimatedToolIcon tool={tool} running />)
  expect(container.querySelector('[data-running="true"] svg')).not.toBeNull()
  rerender(<AnimatedToolIcon tool={tool} running={false} />)
  expect(container.querySelector('[data-running="true"]')).toBeNull()
  expect(container.querySelector('svg')).not.toBeNull()
})

it('shows animated icons for running tools inside a subagent and settles them when the agent ends', () => {
  const calls = [{ id: 'a', tool: 'spawn_agents', status: 'running' as const, subagents: [{
    index: 1, task: 'inspect files', status: 'running' as const, steps: [
      { step: 1, tool: 'read_file', status: 'completed' as const },
      { step: 2, tool: 'bash', status: 'running' as const },
    ],
  }] }]
  const { container, rerender } = render(<ToolActivity running calls={calls} />)
  fireEvent.click(screen.getByRole('button', { expanded: false }))
  fireEvent.click(screen.getByRole('button', { expanded: false }))
  const command = screen.getByText('bash').closest('span')!
  expect(command.querySelector('[data-running="true"]')).not.toBeNull()
  expect(screen.getByText('read_file').closest('span')!.querySelector('[data-running="true"]')).toBeNull()
  rerender(<ToolActivity calls={[{ ...calls[0], status: 'completed', subagents: [{ ...calls[0].subagents[0], status: 'completed' }] }]} />)
  expect(container.querySelector('[data-running="true"]')).toBeNull()
})

it('distinguishes web search from fetching a page', () => {
  expect(animatedToolIcon('web_search')).toBe(SearchIcon)
  expect(animatedToolIcon('web_fetch')).toBe(FileFetchIcon)
})
