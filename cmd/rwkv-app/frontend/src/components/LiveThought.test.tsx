import { fireEvent, render, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Step } from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import { LiveThought, stepThoughts } from './LiveThought'
import ToolActivity, { callsFromSteps } from './ToolActivity'

const steps = [
  new Step({ number: 1, stage: 'decision', modelOutput: '>The user wants the weather.</think>\n<tool_call>{"name":"get_weather"}', tool: 'get_weather', toolArguments: '{"location":"合肥"}' }),
  new Step({ number: 2, stage: 'decision', modelOutput: '>I can answer now.</think>\n合肥明天雷阵雨。' }),
]

describe('thoughts in the activity card', () => {
  it('reads each step thought', () => {
    expect(stepThoughts(steps)).toEqual([{ step: 1, text: 'The user wants the weather.' }, { step: 2, text: 'I can answer now.' }])
  })

  it('interleaves thoughts with tool calls step by step', () => {
    render(<ToolActivity calls={callsFromSteps(steps)} thoughts={stepThoughts(steps)} />)
    const summary = screen.getByRole('button', { name: /思考了 2 次/ })
    fireEvent.click(summary)
    const panel = document.querySelector('.tool-activity-panel') as HTMLElement
    const rows = Array.from(panel.children).map((row) => row.getAttribute('data-testid') === 'thought-row' ? 'thought' : 'call')
    expect(rows).toEqual(['thought', 'call', 'thought'])
    const first = within(panel).getAllByTestId('thought-row')[0]
    fireEvent.click(within(first).getByRole('button'))
    expect(within(first).getAllByText('The user wants the weather.').length).toBeGreaterThan(0)
  })

  it('shows the live preview only while the card is collapsed', () => {
    const thought = { step: 1, text: 'The user wants the weather in Guangzhou and Chengdu.' }
    render(<ToolActivity calls={[]} thoughts={[thought]} running liveThought={thought.text} />)
    expect(screen.getByTestId('live-thought')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /正在思考/ }))
    expect(screen.queryByTestId('live-thought')).not.toBeInTheDocument()
  })

  it('renders nothing live before the model thinks', () => {
    const { container } = render(<LiveThought text="  " />)
    expect(container).toBeEmptyDOMElement()
  })
})
