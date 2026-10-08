/*
 * RWKV-Agent trace → DSH trajectory model. Each conversation message becomes a
 * turn; routing attempts and harness steps become groups, and every model call
 * (route or step) is one numbered request. Harness-only facts (stage, protocol
 * repair, no_tool rationale, answer-contract repair) ride on `cell.harness`.
 */
import type { Result, Step } from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { ToolTrace } from '../trajectory-types'
import { splitModelOutput } from '../ledger'
import { resultText } from '../components/ToolActivity'
import type { TrajectoryGroupModel, TrajectoryTurnModel } from './layout.ts'
import type { TrajectoryTranslate } from './locales.ts'
import type { TrajectoryHarnessFact, TrajectoryCellProps } from './trajectory-record.ts'
import type { TrajectoryRequestNumber, TrajectoryUsage } from './TrajectoryTable.tsx'
// Live turn construction lives in its own file; it only calls back into helpers at run time.
import { buildLiveTurn } from './rwkv-adapter-live.ts'

export type AdapterMessage = {
  id: string
  role: string
  content: string
  prompt?: string
  createdAt?: string
  trajectory?: ToolTrace[]
  trace?: Result
}

/** One agent:event as the app receives it, stamped with its arrival time. */
export type LiveEvent = {
  kind: string; at: number; step?: number; parentStep?: number; tool?: string; arguments?: string
  route?: string; bundles?: string[]; subagentIndex?: number; subagentTask?: string
  durationMs?: number; attempt?: number; maxAttempts?: number; statusCode?: number; delayMs?: number; error?: string
}

/** The turn still running: its prompt plus the events received so far. */
export type LiveTurn = { id: string; prompt: string; startedAt: number; events: readonly LiveEvent[] }

export type TrajectoryModel = {
  turns: TrajectoryTurnModel[]
  requests: TrajectoryRequestNumber[]
  /** Conversation message id for each turn number (1-based). */
  messageIds: Map<number, string>
}

type Group = { title: string; cells: TrajectoryCellProps[] }

class Builder {
  index = 0
  requestNumber = 0
  cumulative: TrajectoryUsage | undefined
  previousPrompt: string | undefined
  readonly turns: TrajectoryTurnModel[] = []
  readonly requests: TrajectoryRequestNumber[] = []
  readonly messageIds = new Map<number, string>()

  constructor(readonly t: TrajectoryTranslate) {}

  next() { return ++this.index }

  request(turn: number, step: number, group: string, fields: {
    status: 'complete' | 'running' | 'error'
    startedAt?: number | null
    durationMs?: number | null
    error?: string
    usage?: TrajectoryUsage
    prompt?: { prompt: string; bytes?: number; truncated?: boolean; toolsOffered?: string[]; stops?: string[]; maxOutputTokens?: number } | null
  }) {
    if (fields.usage !== undefined) this.cumulative = addUsage(this.cumulative, fields.usage)
    const prompt = fields.prompt
    const startedAt = finite(fields.startedAt)
    this.requests.push({
      turn, step, group,
      number: ++this.requestNumber,
      status: fields.status,
      ...(startedAt === null ? {} : {
        startedAt,
        completedAt: finite(fields.durationMs) === null ? null : startedAt + (fields.durationMs as number),
      }),
      ...(fields.error ? { error: fields.error } : {}),
      ...(prompt && (prompt.maxOutputTokens !== undefined || prompt.stops?.length)
        ? { requestConfig: { ...(prompt.maxOutputTokens !== undefined ? { maxTokens: prompt.maxOutputTokens } : {}), ...(prompt.stops?.length ? { stop: prompt.stops } : {}) } }
        : {}),
      ...(fields.usage === undefined ? {} : { usage: fields.usage }),
      ...(this.cumulative === undefined ? {} : { cumulativeUsage: this.cumulative }),
      ...(prompt?.prompt
        ? {
          prompt: {
            text: prompt.prompt,
            ...(prompt.bytes ? { bytes: prompt.bytes } : {}),
            ...(prompt.truncated ? { truncated: true } : {}),
            ...(this.previousPrompt === undefined ? {} : { previous: this.previousPrompt }),
            ...(prompt.toolsOffered ? { toolsOffered: prompt.toolsOffered } : {}),
          },
        }
        : {}),
    })
    if (prompt?.prompt) this.previousPrompt = prompt.prompt
  }
}

export function buildTrajectoryModel(
  messages: readonly AdapterMessage[],
  live: LiveTurn | null,
  t: TrajectoryTranslate,
): TrajectoryModel {
  const builder = new Builder(t)
  messages.forEach((message, position) => buildMessageTurn(builder, message, position + 1))
  if (live !== null) buildLiveTurn(builder, live, messages.length + 1)
  return { turns: builder.turns, requests: builder.requests, messageIds: builder.messageIds }
}

function buildMessageTurn(builder: Builder, message: AdapterMessage, turn: number) {
  const { t } = builder
  const trace = message.trace
  const groups: Group[] = []
  builder.messageIds.set(turn, message.id)
  const startedAt = finite(trace?.startedAtMs) ?? parseTime(message.createdAt)

  if (message.prompt) groups.push({ title: t('group.message'), cells: [userCell(builder, message.prompt, startedAt)] })

  trace?.routeSteps?.forEach((route, position) => {
    const attempt = route.attempt || position + 1
    const title = t('group.route', { attempt })
    const error = route.protocolError || (route.failedClosed ? '路由失败关闭' : '')
    builder.request(turn, -attempt, title, {
      status: error ? 'error' : 'complete', startedAt: route.startedAtMs, durationMs: route.durationMs,
      error: error || undefined, prompt: route.request,
    })
    groups.push({
      title,
      cells: [{
        index: builder.next(),
        recordId: `route\u0000${message.id}\u0000${attempt}`,
        kind: 'message',
        text: error || [route.route, ...(route.bundles || [])].filter(Boolean).join(' · ') || t('record.noContent'),
        ...(route.modelOutput ? { outputDetail: route.modelOutput } : {}),
        ...(error ? { isError: true } : {}),
        timeSeconds: seconds(route.durationMs),
        startedAt: finite(route.startedAtMs),
        harness: facts([
          ['路由', route.route], ['能力组', route.bundles?.join(' · ')],
          ['协议错误', route.protocolError, 'error'], ['失败关闭', route.failedClosed ? '是' : undefined, 'error'],
        ]),
      }],
    })
  })

  const steps = trace?.steps ?? []
  steps.forEach((step, position) => {
    const title = t('group.step', { step: step.number })
    const usage = stepUsage(step)
    builder.request(turn, step.number, title, {
      status: step.modelError ? 'error' : 'complete', startedAt: step.startedAtMs, durationMs: step.modelDurationMs,
      error: step.modelError || undefined, usage, prompt: step.request,
    })
    const cells = [stepMessageCell(builder, message, step, usage, position === steps.length - 1)]
    if (step.tool) cells.push(stepToolCell(builder, message, step))
    for (const child of step.subagents ?? []) cells.push(...subagentCells(builder, message, step, child))
    groups.push({ title, cells })
  })

  if (!trace && message.trajectory?.length) {
    for (const call of message.trajectory) {
      const failed = call.status === 'failed'
      groups.push({
        title: t('group.step', { step: call.step }),
        cells: [{
          index: builder.next(), kind: 'tool', callId: `${message.id}\u0000legacy\u0000${call.step}`,
          toolName: call.tool, text: call.tool,
          ...(call.arguments ? { previewMarkdown: call.arguments, inputDetail: call.arguments } : {}),
          outputDetail: call.error || t('record.noOutput'),
          ...(failed ? { isError: true, result: call.error || 'error' } : { result: t('record.noOutput') }),
          timeSeconds: null, startedAt: null,
        }, ...(call.subagents ?? []).map((child): TrajectoryCellProps => ({
          index: builder.next(), kind: 'subtool', callId: `${message.id}\u0000legacy\u0000${call.step}\u0000a${child.index}`,
          toolName: `子 Agent ${child.index}`, text: `子 Agent ${child.index}`, previewMarkdown: child.task, inputDetail: child.task,
          outputDetail: child.error || child.output || t('record.noOutput'),
          ...(child.status === 'failed' ? { isError: true, result: child.error || 'error' } : child.output ? { result: '', resultPreviewMarkdown: child.output } : {}),
          timeSeconds: seconds(child.durationMs), startedAt: null,
          harness: facts([['路由', child.route], ['能力组', child.bundles?.join(' · ')], ['子步骤', child.steps?.map(item => item.tool).join(' → ')], ['来源', child.sources?.join('\n')]]),
        }))],
      })
    }
  }

  const failure = trace?.error || (message.role === 'error' ? message.content : '')
  if (failure) {
    groups.push({
      title: t('group.answer'),
      cells: [{
        index: builder.next(), recordId: `error\u0000${message.id}`, kind: 'message',
        text: failure, outputDetail: failure, isError: true, timeSeconds: null, startedAt: null,
      }],
    })
  } else if (!trace && message.content) {
    groups.push({
      title: t('group.answer'),
      cells: [{ index: builder.next(), recordId: `answer\u0000${message.id}`, kind: 'message', text: '', previewMarkdown: message.content, outputDetail: message.content, timeSeconds: null, startedAt: null }],
    })
  }

  builder.turns.push({ turn, groups: groups.map(toGroupModel) })
}

function userCell(builder: Builder, prompt: string, startedAt: number | null): TrajectoryCellProps {
  return {
    index: builder.next(), kind: 'user', text: '', previewMarkdown: prompt, inputDetail: prompt,
    opensTurn: true, timeSeconds: 0, startedAt,
  }
}

function stepMessageCell(builder: Builder, message: AdapterMessage, step: Step, usage: TrajectoryUsage | undefined, last: boolean): TrajectoryCellProps {
  const { t } = builder
  const trace = message.trace
  const { thinking, rest } = splitModelOutput(step.modelOutput)
  const toolOnly = Boolean(step.tool) || (step.subagents?.length ?? 0) > 0
  const answer = last && !trace?.error ? trace?.output || '' : ''
  const preview = answer || (toolOnly ? thinking : rest || thinking)
  const startedAt = finite(step.startedAtMs)
  const duration = finite(step.modelDurationMs)
  const repaired = last && trace?.answerContractRepaired === true
  return {
    index: builder.next(),
    recordId: `assistant\u0000${message.id}\u0000${step.number}`,
    kind: 'message',
    text: step.modelError || (preview ? '' : toolOnly ? t('layout.toolCallOnly') : ''),
    ...(preview && !step.modelError ? { previewMarkdown: preview } : {}),
    ...(rest || step.modelOutput ? { outputDetail: answer || rest || step.modelOutput } : {}),
    ...(thinking ? { thinkingDetail: thinking } : {}),
    ...(step.modelError ? { isError: true } : {}),
    timeSeconds: seconds(step.modelDurationMs),
    startedAt,
    ...usageFields(usage),
    assistantMetrics: {
      timingRecorded: startedAt !== null && duration !== null,
      stepStartTime: startedAt,
      firstTokenTime: finite(step.firstTokenAtMs),
      completedTime: startedAt !== null && duration !== null ? startedAt + duration : null,
      usageProvided: usage !== undefined,
      outputTokens: usage?.output ?? null,
    },
    harness: facts([
      ['阶段', step.stage], ['动作', step.actionType], ['结束原因', step.finishReason],
      ['协议修复', step.protocolError ? `${step.protocolRepaired ? '已修复' : '未修复'} · ${step.protocolError}` : undefined, step.protocolRepaired ? 'warn' : 'error'],
      ['阶段约束', step.stageViolation ? '当前阶段不接受该动作' : undefined, 'error'],
      ['直接回答理由', step.noToolRationale], ['候选答案', step.noToolAnswer],
      ['答案契约', repaired ? `已修复 · ${trace?.forcedAnswerReason || trace?.answerViolations?.join('；') || '输出被改写以满足契约'}` : undefined, 'warn'],
      ['修复前输出', repaired ? trace?.originalOutput : undefined],
      ['模型错误', step.modelError, 'error'],
    ]),
  }
}

function stepToolCell(builder: Builder, message: AdapterMessage, step: Step): TrajectoryCellProps {
  const { t } = builder
  const error = step.toolError || step.toolRejected || ''
  const result = step.toolResult ? resultText(step.toolResult) : ''
  return {
    index: builder.next(), kind: 'tool', callId: `${message.id}\u0000${step.number}`,
    toolName: step.tool, text: step.tool || '',
    ...(step.toolArguments ? { previewMarkdown: step.toolArguments, inputDetail: step.toolArguments } : {}),
    outputDetail: error || result || t('record.noOutput'),
    ...(error ? { isError: true, result: error } : result ? { result: '', resultPreviewMarkdown: result } : { result: t('record.noOutput') }),
    timeSeconds: seconds(step.toolDurationMs),
    startedAt: finite(step.toolStartedAtMs),
    harness: facts([
      ['已执行', step.toolExecuted === undefined ? undefined : step.toolExecuted ? '是' : '否'],
      ['证据', step.toolEvidence === undefined ? undefined : step.toolEvidence ? '有效' : '无效'],
      ['工具状态', step.toolUnavailable ? '不可用' : undefined, 'error'],
      ['拒绝原因', step.toolRejected, 'error'],
      ['传输重试', step.toolRetries?.length ? step.toolRetries.map(retry => `${retry.attempt}/${retry.maxAttempts}${retry.statusCode ? ` · HTTP ${retry.statusCode}` : ''} · 等待 ${retry.delayMs} ms`).join('；') : undefined, 'warn'],
    ]),
  }
}

function subagentCells(builder: Builder, message: AdapterMessage, step: Step, child: NonNullable<Step['subagents']>[number]): TrajectoryCellProps[] {
  const { t } = builder
  const failed = child.status === 'failed'
  const running = child.status === 'running'
  const out: TrajectoryCellProps[] = [{
    index: builder.next(), kind: 'subtool', callId: `${message.id}\u0000${step.number}\u0000a${child.index}`,
    toolName: `子 Agent ${child.index}`, text: `子 Agent ${child.index}`,
    previewMarkdown: child.task, inputDetail: child.task,
    ...(running ? {} : { outputDetail: child.error || child.output || t('record.noOutput') }),
    ...(failed ? { isError: true, result: child.error || 'error' } : child.output ? { result: '', resultPreviewMarkdown: child.output } : {}),
    timeSeconds: seconds(child.durationMs),
    startedAt: finite(child.startedAtMs),
    harness: facts([
      ['路由', child.route], ['能力组', child.bundles?.join(' · ')], ['来源', child.sources?.join('\n')],
    ]),
  }]
  for (const childStep of child.steps ?? []) {
    out.push({
      index: builder.next(), kind: 'subtool', callId: `${message.id}\u0000${step.number}\u0000a${child.index}\u0000${childStep.number}`,
      toolName: childStep.tool, text: childStep.tool,
      ...(childStep.arguments ? { previewMarkdown: childStep.arguments, inputDetail: childStep.arguments } : {}),
      ...(childStep.status === 'running' ? {} : { outputDetail: childStep.error || t('record.noOutput') }),
      ...(childStep.error ? { isError: true, result: childStep.error } : {}),
      timeSeconds: null, startedAt: null,
    })
  }
  return out
}

function toGroupModel(group: Group): TrajectoryGroupModel {
  const tools = new Map<string, number>()
  let duration = 0
  for (const cell of group.cells) {
    duration += cell.timeSeconds ?? 0
    if (cell.kind === 'tool' && cell.toolName) tools.set(cell.toolName, (tools.get(cell.toolName) ?? 0) + 1)
  }
  const parts = [
    ...(duration > 0 ? [`${Math.round(duration * 1000).toLocaleString()} ms`] : []),
    ...[...tools].map(([name, count]) => count > 1 ? `${name}×${count}` : name),
  ]
  return { title: group.title, ...(parts.length ? { description: parts.join(' ') } : {}), cells: group.cells }
}

function stepUsage(step: Step): TrajectoryUsage | undefined {
  const usage = step.usage
  if (!usage) return undefined
  const value: TrajectoryUsage = {
    ...(usage.promptTokens ? { input: usage.promptTokens } : {}),
    ...(usage.cacheReadTokens ? { cacheRead: usage.cacheReadTokens } : {}),
    ...(usage.cacheWriteTokens ? { cacheWrite: usage.cacheWriteTokens } : {}),
    ...(usage.completionTokens ? { output: usage.completionTokens } : {}),
    ...(usage.reasoningTokens ? { reasoning: usage.reasoningTokens } : {}),
  }
  return Object.keys(value).length === 0 ? undefined : value
}

function usageFields(usage: TrajectoryUsage | undefined): Partial<TrajectoryCellProps> {
  if (usage === undefined) return {}
  return {
    ...(usage.input !== undefined ? { input: usage.input } : {}),
    ...(usage.cacheRead !== undefined ? { cacheRead: usage.cacheRead } : {}),
    ...(usage.cacheWrite !== undefined ? { cacheWrite: usage.cacheWrite } : {}),
    ...(usage.output !== undefined ? { output: usage.output } : {}),
    ...(usage.reasoning !== undefined ? { think: usage.reasoning } : {}),
  }
}

function addUsage(total: TrajectoryUsage | undefined, usage: TrajectoryUsage): TrajectoryUsage {
  const sum = (a?: number, b?: number) => a === undefined && b === undefined ? undefined : (a ?? 0) + (b ?? 0)
  const next: TrajectoryUsage = {}
  for (const key of ['input', 'cacheRead', 'cacheWrite', 'output', 'reasoning'] as const) {
    const value = sum(total?.[key], usage[key])
    if (value !== undefined) next[key] = value
  }
  return next
}

function facts(rows: ReadonlyArray<readonly [string, string | undefined | null, ('error' | 'warn')?]>): TrajectoryHarnessFact[] | undefined {
  const out = rows.flatMap(([label, value, tone]) => value ? [{ label, value, ...(tone ? { tone } : {}) }] : [])
  return out.length ? out : undefined
}

function finite(value: number | null | undefined): number | null {
  return typeof value === 'number' && Number.isFinite(value) && value > 0 ? value : null
}

function seconds(ms: number | null | undefined): number | null {
  return typeof ms === 'number' && Number.isFinite(ms) ? Math.max(0, ms) / 1000 : null
}

function parseTime(value?: string): number | null {
  if (!value) return null
  const time = new Date(value).getTime()
  return Number.isFinite(time) && time > Date.UTC(2000, 0, 1) ? time : null
}

export { userCell, toGroupModel, finite, seconds }
export type { Builder, Group }
