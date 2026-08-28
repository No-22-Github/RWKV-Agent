import type { Result } from '../bindings/github.com/no22/RWKV-Agent/api/models'
import type { ToolTrace } from './trajectory-types'

export type LedgerEvent = {
  id: string
  order: number
  kind: 'input' | 'route' | 'model' | 'tool' | 'retry' | 'subagent' | 'output'
  title: string
  summary: string
  state: 'idle' | 'running' | 'completed' | 'failed'
  request?: unknown
  result?: unknown
  timing?: unknown
  raw?: unknown
}

export type LedgerMessage = {
  id: string
  role: string
  content: string
  prompt?: string
  trajectory?: ToolTrace[]
  trace?: Result
}

export const ROLE_TAGS: Record<LedgerEvent['kind'], { tag: string; cls: string }> = {
  input: { tag: 'USER', cls: 'user' }, route: { tag: 'ROUTE', cls: 'route' }, model: { tag: 'MODEL', cls: 'model' },
  tool: { tag: 'TOOL', cls: 'tool' }, retry: { tag: 'RETRY', cls: 'tool' }, subagent: { tag: 'AGENT', cls: 'model' }, output: { tag: 'SUBMIT', cls: 'submit' },
}

export const KIND_TAG_CLASS: Record<string, string> = {
  user: 'text-ink-strong',
  route: 'text-brand',
  model: 'text-brand',
  agent: 'text-brand',
  tool: 'text-warning',
  retry: 'text-warning',
  submit: 'text-brand',
}

export const EVENT_TITLE_PREFIX = /^(用户输入|路由请求|路由响应|模型请求|模型响应|协议修复|工具调用|工具结果|工具重试|最终回复)\s*·?\s*/

export function eventLane(kind: LedgerEvent['kind']) {
  if (kind === 'tool' || kind === 'retry' || kind === 'subagent') return 2
  if (kind === 'model' || kind === 'output') return 1
  return 0
}

export function eventName(event: LedgerEvent) {
  return event.title.replace(EVENT_TITLE_PREFIX, '').trim()
}

export function isResultEvent(event: LedgerEvent) {
  return /响应|结果|回复/.test(event.title)
}

export function buildLedgerEvents(message: LedgerMessage): LedgerEvent[] {
  const events: LedgerEvent[] = []
  const add = (event: Omit<LedgerEvent, 'order'>) => events.push({ ...event, order: events.length + 1 })
  const trace = message.trace
  if (message.prompt) add({ id: `${message.id}:input`, kind: 'input', title: '用户输入', summary: shortValue(message.prompt), state: 'completed', request: { prompt: message.prompt }, raw: message.prompt })
  trace?.routeSteps?.forEach((route, index) => {
    const attempt = route.attempt || index + 1
    add({ id: `${message.id}:route:${attempt}:request`, kind: 'route', title: `路由请求 · Attempt ${attempt}`, summary: `${route.request?.bytes || 0} bytes`, state: 'completed', request: route.request, timing: { durationMs: route.durationMs }, raw: route })
    const error = route.protocolError || (route.failedClosed ? '路由失败关闭' : '')
    add({ id: `${message.id}:route:${attempt}:response`, kind: 'route', title: `路由响应 · ${route.route || '未决'}`, summary: error || [route.route, ...(route.bundles || [])].filter(Boolean).join(' · ') || '无可用响应', state: error ? 'failed' : 'completed', result: { modelOutput: route.modelOutput, route: route.route, bundles: route.bundles, protocolError: route.protocolError, failedClosed: route.failedClosed }, timing: { durationMs: route.durationMs }, raw: route })
  })
  trace?.steps.forEach((step) => {
    const prefix = `${message.id}:step:${step.number}`
    if (step.request) add({ id: `${prefix}:model-request`, kind: 'model', title: `模型请求 · Step ${step.number}`, summary: `${step.stage || 'decision'} · ${step.request.bytes || 0} bytes`, state: 'completed', request: step.request, timing: { durationMs: step.modelDurationMs }, raw: step })
    const modelError = step.modelError || step.protocolError
    add({ id: `${prefix}:model-response`, kind: 'model', title: `模型响应 · Step ${step.number}`, summary: shortValue(modelError || step.modelOutput || step.actionType || '空响应'), state: modelError ? 'failed' : 'completed', result: { modelOutput: step.modelOutput, finishReason: step.finishReason, actionType: step.actionType, protocolError: step.protocolError, modelError: step.modelError, usage: step.usage }, timing: { durationMs: step.modelDurationMs, usage: step.usage }, raw: step })
    if (step.actionType === 'no_tool') {
      const noToolFailure = step.protocolError || (step.stageViolation ? '当前阶段不接受 no_tool' : '')
      add({
        id: `${prefix}:no-tool`,
        kind: 'model',
        title: `无需工具 · Step ${step.number}`,
        summary: shortValue(step.noToolRationale || step.noToolAnswer || noToolFailure || '模型决定直接回答'),
        state: noToolFailure ? 'failed' : 'completed',
        result: {
          rationale: step.noToolRationale,
          candidateAnswer: step.noToolAnswer,
          accepted: !noToolFailure,
          toolExecuted: false,
          toolEvidence: false,
          error: noToolFailure || undefined,
        },
        raw: step,
      })
    }
    if (step.protocolError) add({ id: `${prefix}:protocol-retry`, kind: 'retry', title: `协议修复 · Step ${step.number}`, summary: shortValue(step.protocolError), state: step.modelError ? 'failed' : 'completed', request: { correctionFor: step.protocolError }, result: { repaired: step.protocolRepaired, stageViolation: step.stageViolation }, raw: step })
    if (step.tool) {
      add({ id: `${prefix}:tool-call`, kind: 'tool', title: `工具调用 · ${step.tool}`, summary: shortValue(step.toolArguments || '无参数'), state: step.toolError || step.toolRejected ? 'failed' : 'completed', request: { tool: step.tool, arguments: parseJSONValue(step.toolArguments) }, timing: { durationMs: step.toolDurationMs }, raw: step })
      step.toolRetries?.forEach((retry, retryIndex) => add({ id: `${prefix}:tool-retry:${retryIndex + 1}`, kind: 'retry', title: `工具重试 · ${step.tool}`, summary: `Attempt ${retry.attempt}/${retry.maxAttempts} · 等待 ${formatDuration(retry.delayMs)}`, state: 'completed', request: retry, timing: { delayMs: retry.delayMs }, raw: retry }))
      const toolFailure = step.toolError || step.toolRejected
      add({ id: `${prefix}:tool-result`, kind: 'tool', title: `工具结果 · ${step.tool}`, summary: shortValue(toolFailure || step.toolResult || (step.toolExecuted ? '执行完成' : '未执行')), state: toolFailure ? 'failed' : 'completed', result: { result: parseJSONValue(step.toolResult), error: step.toolError, rejected: step.toolRejected, executed: step.toolExecuted, evidence: step.toolEvidence, unavailable: step.toolUnavailable }, timing: { durationMs: step.toolDurationMs }, raw: step })
    }
    step.subagents?.forEach((child) => {
      const childPrefix = `${prefix}:agent:${child.index}`
      add({ id: `${childPrefix}:start`, kind: 'subagent', title: `子 Agent ${child.index} · 启动`, summary: shortValue(child.task), state: 'completed', request: { task: child.task }, raw: child })
      if (child.route) add({ id: `${childPrefix}:route`, kind: 'route', title: `子 Agent ${child.index} · 路由`, summary: [child.route, ...(child.bundles || [])].join(' · '), state: 'completed', result: { route: child.route, bundles: child.bundles }, raw: child })
      child.steps?.forEach((childStep) => {
        const childStepPrefix = `${childPrefix}:step:${childStep.number}`
        add({ id: `${childStepPrefix}:call`, kind: 'tool', title: `子 Agent ${child.index} · 调用 ${childStep.tool}`, summary: shortValue(childStep.arguments || '无参数'), state: childStep.status === 'failed' ? 'failed' : 'completed', request: { tool: childStep.tool, arguments: parseJSONValue(childStep.arguments) }, raw: childStep })
        childStep.retries?.forEach((retry, retryIndex) => add({ id: `${childStepPrefix}:retry:${retryIndex + 1}`, kind: 'retry', title: `子 Agent ${child.index} · 重试 ${childStep.tool}`, summary: `Attempt ${retry.attempt}/${retry.maxAttempts} · 等待 ${formatDuration(retry.delayMs)}`, state: 'completed', request: retry, timing: { delayMs: retry.delayMs }, raw: retry }))
        add({ id: `${childStepPrefix}:result`, kind: 'tool', title: `子 Agent ${child.index} · 工具结果`, summary: childStep.error || childStep.status, state: childStep.status === 'failed' ? 'failed' : 'completed', result: { status: childStep.status, error: childStep.error }, raw: childStep })
      })
      add({ id: `${childPrefix}:result`, kind: 'subagent', title: `子 Agent ${child.index} · ${child.status === 'failed' ? '失败' : '完成'}`, summary: shortValue(child.error || child.output || child.status), state: child.status === 'failed' ? 'failed' : 'completed', result: { status: child.status, output: child.output, error: child.error, sources: child.sources }, timing: { durationMs: child.durationMs }, raw: child })
    })
  })
  if (trace?.error || message.role === 'error') add({ id: `${message.id}:error`, kind: 'output', title: 'Agent 运行失败', summary: shortValue(trace?.error || message.content), state: 'failed', result: { error: trace?.error || message.content }, timing: { durationMs: trace?.durationMs }, raw: trace || message })
  else if (trace?.output || message.role === 'assistant') add({ id: `${message.id}:output`, kind: 'output', title: '最终回复', summary: shortValue(trace?.output || message.content), state: 'completed', result: { output: trace?.output || message.content }, timing: { durationMs: trace?.durationMs }, raw: trace || message })
  if (!trace && message.trajectory?.length) message.trajectory.forEach((item, index) => add({ id: `${message.id}:legacy:${item.step}:${index}`, kind: 'tool', title: `STEP ${item.step} · ${item.tool}`, summary: item.error || item.status, state: item.status === 'failed' ? 'failed' : 'completed', request: { tool: item.tool, arguments: item.arguments }, result: { status: item.status, error: item.error, subagents: item.subagents }, raw: item }))
  return events
}

export function parseJSONValue(value?: string) {
  if (!value) return value
  try { return JSON.parse(value) } catch { return value }
}

export function shortValue(value: unknown) {
  const text = typeof value === 'string' ? value : JSON.stringify(value)
  const compact = (text || '').replace(/\s+/g, ' ').trim()
  return compact.length > 92 ? `${compact.slice(0, 89)}...` : compact
}

export function formatDuration(value?: number) {
  if (!value) return '--'
  return value < 1000 ? `${value} ms` : `${(value / 1000).toFixed(1)} s`
}

export function traceStats(trace: Result) {
  const tokens = trace.steps.reduce((total, step) => total + (step.usage?.promptTokens || 0) + (step.usage?.completionTokens || 0), 0)
  return { durationMs: trace.durationMs, tokens }
}
