import { describe, expect, it } from 'vitest'
import { Result, Step, Usage } from '../bindings/github.com/no22/RWKV-Agent/api/models'
import { buildTraceTurns, flattenTraceRecords } from './ledger'

describe('trajectory record ledger', () => {
  it('merges the no-tool decision into the message record instead of a separate event', () => {
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

    const turns = buildTraceTurns([{ id: 'turn-1', role: 'assistant', content: trace.output, trace }])
    const records = flattenTraceRecords(turns)

    expect(records.map((record) => record.kind)).toEqual(['message', 'output'])
    const message = records[0]
    expect(message.detail.noToolRationale).toBe('No lookup is needed.')
    expect(message.detail.noToolAnswer).toBe('Candidate answer.')
    expect(message.text).toContain('No lookup is needed.')
  })

  it('keeps a rejected answer-stage no_tool visible via repair fields without a hard failure', () => {
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

    const records = flattenTraceRecords(buildTraceTurns([{ id: 'turn-2', role: 'assistant', content: trace.output, trace }]))
    const message = records.find((record) => record.kind === 'message')

    expect(message?.detail.protocolError).toBe('no_tool action is forbidden during answer')
    expect(message?.detail.stageViolation).toBe(true)
    expect(message?.isError).toBe(false)
  })

  it('merges tool call, result and retries into a single tool record with subtool records', () => {
    const trace = new Result({
      output: 'Answer with evidence.',
      steps: [
        new Step({
          number: 3,
          stage: 'decision',
          actionType: 'tool',
          modelOutput: 'call web_search',
          tool: 'web_search',
          toolArguments: '{"query":"rwkv"}',
          toolResult: '10 results',
          toolExecuted: true,
          toolDurationMs: 220,
          toolRetries: [
            { attempt: 1, maxAttempts: 3, delayMs: 500 },
            { attempt: 2, maxAttempts: 3, delayMs: 900 },
          ],
          usage: { promptTokens: 1200, completionTokens: 80 },
          subagents: [
            { index: 1, task: '子任务 A', status: 'completed', output: 'A 完成', durationMs: 800 },
            { index: 2, task: '子任务 B', status: 'failed', error: '超时', durationMs: 900 },
          ],
        }),
      ],
      duration: 0,
      durationMs: 1500,
    })

    const [turn] = buildTraceTurns([{ id: 'turn-3', role: 'assistant', content: trace.output, prompt: '查一下 rwkv', trace }])
    const records = turn.records

    expect(records.map((record) => `${record.index}:${record.kind}`)).toEqual([
      '1:user', '2:message', '3:tool', '4:subtool', '5:subtool', '6:output',
    ])
    expect(turn.groups.map((group) => group.title)).toEqual(['输入', 'Step 3', '输出'])

    const tool = records[2]
    expect(tool.title).toBe('web_search')
    expect(tool.detail.arguments).toBe('{"query":"rwkv"}')
    expect(tool.detail.result).toBe('10 results')
    expect(tool.detail.retries).toHaveLength(2)
    expect(tool.timeMs).toBe(220)
    expect(records[4].isError).toBe(true)
    expect(records[2].tokens).toBeUndefined()
    expect(records[1].tokens).toEqual({ input: 1200, output: 80 })
  })

  it('keeps each route attempt as one merged route record', () => {
    const trace = new Result({
      output: 'ok',
      route: 'tools',
      routeSteps: [
        { attempt: 1, route: 'tools', bundles: ['web'], durationMs: 40 },
        { attempt: 2, route: 'tools', protocolError: 'bad router output', failedClosed: true, durationMs: 60 },
      ] as never,
      steps: [],
      duration: 0,
      durationMs: 100,
    })

    const [turn] = buildTraceTurns([{ id: 'turn-4', role: 'assistant', content: 'ok', trace }])
    const routeRecords = turn.records.filter((record) => record.kind === 'route')

    expect(routeRecords).toHaveLength(2)
    expect(routeRecords[0].groupTitle).toBe('路由')
    expect(routeRecords[0].text).toBe('tools · web')
    expect(routeRecords[1].isError).toBe(true)
    expect(turn.groups[0].title).toBe('路由')
  })

  it('attaches the real output/originalOutput pair when the answer contract was repaired', () => {
    const trace = new Result({
      output: 'Repaired answer.',
      originalOutput: 'Unparseable answer.',
      answerContractRepaired: true,
      forcedAnswerReason: 'missing terminal tag',
      steps: [],
      duration: 0,
      durationMs: 5,
    })

    const records = flattenTraceRecords(buildTraceTurns([{ id: 'turn-5', role: 'assistant', content: trace.output, trace }]))
    const output = records.find((record) => record.kind === 'output')

    expect(output?.detail.answerContractRepaired).toBe(true)
    expect(output?.detail.originalOutput).toBe('Unparseable answer.')
    expect(output?.detail.forcedAnswerReason).toBe('missing terminal tag')
  })

  it('renders legacy tool-only trajectories as tool records without a message record', () => {
    const [turn] = buildTraceTurns([{
      id: 'turn-6',
      role: 'assistant',
      content: '历史回答',
      trajectory: [
        { step: 1, tool: 'web_fetch', status: 'completed', arguments: '{"url":"https://x"}' },
        { step: 2, tool: 'web_search', status: 'failed', error: '429' },
      ],
    }])
    const records = turn.records

    expect(records.map((record) => record.kind)).toEqual(['tool', 'tool', 'output'])
    expect(records[0].detail.toolName).toBe('web_fetch')
    expect(records[1].isError).toBe(true)
  })
})

describe('wall-clock timestamps and usage breakdowns', () => {
  it('carries startedAt and cache/reasoning details into records', () => {
    const trace = new Result({
      output: '完成',
      startedAtMs: 1_700_000_000_000,
      steps: [
        new Step({
          number: 1,
          stage: 'tool',
          startedAtMs: 1_700_000_000_100,
          modelDurationMs: 800,
          tool: 'web_search',
          toolStartedAtMs: 1_700_000_001_000,
          toolDurationMs: 50,
          usage: new Usage({ promptTokens: 100, completionTokens: 10, cacheReadTokens: 40, reasoningTokens: 5 }),
        }),
      ],
      duration: 0,
      durationMs: 900,
    })

    const records = flattenTraceRecords(buildTraceTurns([{ id: 'wall-1', role: 'assistant', content: '完成', prompt: '搜索一下', trace }]))
    const user = records.find((record) => record.kind === 'user')
    const message = records.find((record) => record.kind === 'message')
    const tool = records.find((record) => record.kind === 'tool')

    expect(user?.startedAtMs).toBe(1_700_000_000_000)
    expect(message?.startedAtMs).toBe(1_700_000_000_100)
    expect(message?.tokens?.cacheRead).toBe(40)
    expect(message?.tokens?.reasoning).toBe(5)
    expect(tool?.startedAtMs).toBe(1_700_000_001_000)
  })

  it('keeps legacy traces without timestamps so wall-clock modes stay off', () => {
    const trace = new Result({
      output: '完成',
      steps: [new Step({ number: 1, stage: 'tool', tool: 'read_file', toolResult: 'ok' })],
      duration: 0,
      durationMs: 10,
    })
    const records = flattenTraceRecords(buildTraceTurns([{ id: 'wall-2', role: 'assistant', content: '完成', trace }]))
    expect(records.every((record) => record.startedAtMs == null)).toBe(true)
  })
})

describe('leading think block handling', () => {
  it('splits a closed think block: thinking goes to detail, summary shows the action', () => {
    const trace = new Result({
      output: 'ok',
      steps: [
        new Step({
          number: 1,
          stage: 'decision',
          modelOutput: '<think>\n用户想要搜索 Windows 11 的版本号。\n</think>\n<tool_call>{"name":"web_search","arguments":{"query":"win11"}}</tool_call>',
        }),
      ],
      duration: 0,
      durationMs: 10,
    })

    const message = flattenTraceRecords(buildTraceTurns([{ id: 'think-1', role: 'assistant', content: 'ok', trace }]))
      .find((record) => record.kind === 'message')

    expect(message?.detail.thinking).toBe('用户想要搜索 Windows 11 的版本号。')
    expect(message?.text).toContain('<tool_call>')
    expect(message?.text).not.toContain('<think>')
  })

  it('treats an unclosed think block as pure thinking and marks the summary', () => {
    const trace = new Result({
      output: '',
      steps: [
        new Step({
          number: 1,
          stage: 'decision',
          modelOutput: '<think>只想到了一半，没有结论',
        }),
      ],
      duration: 0,
      durationMs: 10,
    })

    const message = flattenTraceRecords(buildTraceTurns([{ id: 'think-2', role: 'assistant', content: '', trace }]))
      .find((record) => record.kind === 'message')

    expect(message?.detail.thinking).toBe('只想到了一半，没有结论')
    expect(message?.text).toContain('（仅思考）')
    expect(message?.text).toContain('只想到了一半')
  })

  it('leaves outputs without a think block untouched', () => {
    const trace = new Result({
      output: 'ok',
      steps: [new Step({ number: 1, stage: 'decision', modelOutput: '<tool_call>{"name":"read_file"}</tool_call>' })],
      duration: 0,
      durationMs: 10,
    })
    const message = flattenTraceRecords(buildTraceTurns([{ id: 'think-3', role: 'assistant', content: 'ok', trace }]))
      .find((record) => record.kind === 'message')
    expect(message?.detail.thinking).toBeUndefined()
    expect(message?.text).toContain('read_file')
  })
})
