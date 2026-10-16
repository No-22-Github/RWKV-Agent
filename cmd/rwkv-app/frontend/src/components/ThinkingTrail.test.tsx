import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Step } from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import ThinkingTrail, { LiveThought, stepThoughts } from './ThinkingTrail'

const steps = [
  new Step({ number: 1, stage: 'decision', modelOutput: '>The user wants the weather.</think>\n<tool_call>{"name":"get_weather"}' }),
  new Step({ number: 2, stage: 'decision', modelOutput: '合肥明天雷阵雨。' }),
]

describe('ThinkingTrail', () => {
  it('lists only the steps that thought', () => {
    expect(stepThoughts(steps)).toEqual([{ step: 1, text: 'The user wants the weather.' }])
  })

  it('stays collapsed until opened', () => {
    render(<ThinkingTrail steps={steps} />)
    expect(screen.queryByText('The user wants the weather.')).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /思考过程 · 1 段/ }))
    expect(screen.getByText('The user wants the weather.')).toBeInTheDocument()
  })

  it('renders nothing live before the model thinks', () => {
    const { container } = render(<LiveThought text="  " />)
    expect(container).toBeEmptyDOMElement()
  })
})
