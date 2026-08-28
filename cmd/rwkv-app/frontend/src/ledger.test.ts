import { describe, expect, it } from 'vitest'
import { Result, Step } from '../bindings/github.com/no22/RWKV-Agent/api/models'
import { buildLedgerEvents } from './ledger'

describe('trajectory ledger', () => {
  it('shows model-authored no-tool rationale without presenting it as evidence', () => {
    const trace = new Result({
      output: 'Direct answer.',
      steps: [
        new Step({
          number: 1,
          stage: 'decision',
          actionType: 'no_tool',
          modelOutput: '{"name":"no_tool","arguments":{"reason":"No lookup is needed."}}',
          noToolRationale: 'No lookup is needed.',
          noToolAnswer: 'Candidate answer.',
        }),
      ],
      duration: 0,
      durationMs: 1,
    })

    const event = buildLedgerEvents({
      id: 'turn-1',
      role: 'assistant',
      content: trace.output,
      trace,
    }).find((candidate) => candidate.title === '无需工具 · Step 1')

    expect(event?.summary).toBe('No lookup is needed.')
    expect(event?.result).toEqual({
      rationale: 'No lookup is needed.',
      candidateAnswer: 'Candidate answer.',
      accepted: true,
      toolExecuted: false,
      toolEvidence: false,
      error: undefined,
    })
  })


  it('retains a rejected answer-stage no-tool message without marking it accepted', () => {
    const trace = new Result({
      output: 'Direct answer.',
      steps: [
        new Step({
          number: 2,
          stage: 'answer',
          actionType: 'no_tool',
          modelOutput: '{"name":"no_tool","arguments":{"reason":"I am done."}}',
          stageViolation: true,
          protocolError: 'no_tool action is forbidden during answer',
        }),
      ],
      duration: 0,
      durationMs: 1,
    })
    const event = buildLedgerEvents({ id: 'turn-2', role: 'assistant', content: trace.output, trace }).find(
      (candidate) => candidate.title === '无需工具 · Step 2',
    )

    expect(event?.state).toBe('failed')
    expect(event?.result).toMatchObject({ accepted: false, toolEvidence: false })
  })
})
