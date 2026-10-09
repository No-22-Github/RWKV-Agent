import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import ToolActivity from './ToolActivity'

afterEach(cleanup)

describe('tool row icons', () => {
  it('animates only rows whose call is still running', () => {
    const { container, rerender } = render(<ToolActivity running calls={[
      { id: 'a', tool: 'get_weather', arguments: '{"location":"合肥"}', status: 'completed', durationMs: 2500 },
      { id: 'b', tool: 'web_search', arguments: '{"query":"合肥 景点"}', status: 'running' },
    ]} />)
    fireEvent.click(screen.getByRole('button', { expanded: false }))
    expect(container.querySelectorAll('[data-running="true"]')).toHaveLength(1)
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
})
