import type { Result } from '../bindings/github.com/no22/RWKV-Agent/api/models'
import type { SubagentTrace, ToolRetryTrace, ToolTrace } from './trajectory-types'

/*
 * 轨迹台账的 record 模型（对齐 deepseek-harness ui-trajectory 的结构）：
 * 一次模型请求+响应合并为一条 message 记录，一次工具调用+结果+重试合并为一条 tool 记录，
 * 协议修复/no_tool 决策并入 message 的状态与详情，不再平铺成对事件。
 */

export type TraceRecordKind = 'user' | 'route' | 'message' | 'tool' | 'subtool' | 'output'
export type TraceRecordState = 'idle' | 'running' | 'completed' | 'failed'

/** 按 kind 动态展示的详情字段；未设置的字段不渲染对应 tab。 */
export type TraceRecordDetail = {
  // user / message / route：请求侧
  prompt?: string
  promptBytes?: number
  promptTruncated?: boolean
  toolsOffered?: string[]
  stops?: string[]
  maxOutputTokens?: number
  // message：决策与响应
  stage?: string
  actionType?: string
  finishReason?: string
  modelOutput?: string
  /** <think>…</think> 内的思考文本；未闭合时为全部输出。 */
  thinking?: string
  modelError?: string
  noToolRationale?: string
  noToolAnswer?: string
  protocolError?: string
  protocolRepaired?: boolean
  stageViolation?: boolean
  modelDurationMs?: number
  startedAtMs?: number
  // tool
  toolName?: string
  arguments?: string
  result?: string
  executed?: boolean
  evidence?: boolean
  rejected?: string
  unavailable?: boolean
  toolDurationMs?: number
  retries?: ToolRetryTrace[]
  // subtool
  subagentIndex?: number
  task?: string
  /** 子 Agent 步骤链（结构化最小类型，兼容绑定层与历史轨迹两种来源）。 */
  subSteps?: Array<{ step: number; tool?: string; arguments?: string; status: string; error?: string }>
  status?: string
  // route
  route?: string
  bundles?: string[]
  attempt?: number
  failedClosed?: boolean
  // output / 通用
  output?: string
  originalOutput?: string
  answerContractRepaired?: boolean
  forcedAnswerReason?: string
  answerViolations?: string[]
  error?: string
  sources?: string[]
  legacySubagents?: SubagentTrace[]
}

export interface TraceRecord {
  /** 全局 1-based 序号，台账上显示为 #N。 */
  index: number
  recordId: string
  kind: TraceRecordKind
  state: TraceRecordState
  title: string
  /** 单行摘要；CSS ellipsis 截断。 */
  text: string
  isError: boolean
  timeMs: number | null
  /** 墙钟开始时刻（epoch ms）；旧轨迹无此字段。 */
  startedAtMs?: number | null
  lane: 0 | 1 | 2
  tokens?: { input: number; output: number; cacheRead?: number; reasoning?: number }
  turn: number
  turnRecordId: string
  groupTitle: string
  /** tool/subtool 专属：同一步 message 记录的 recordId，折叠决策归属它。 */
  ownerRecordId?: string
  detail: TraceRecordDetail
}

export interface TraceGroup {
  title: string
  records: TraceRecord[]
}

export interface TraceTurnHeader {
  steps: number
  tools: number
  subagents: number
  durationMs: number
  isError: boolean
  route?: string
}

export interface TraceTurn {
  turn: number
  turnRecordId: string
  header: TraceTurnHeader
  groups: TraceGroup[]
  /** 展示顺序的扁平记录（groups 的串联）。 */
  records: TraceRecord[]
}

export type LedgerMessage = {
  id: string
  role: string
  content: string
  prompt?: string
  trajectory?: ToolTrace[]
  trace?: Result
}

export function recordLane(kind: TraceRecordKind): 0 | 1 | 2 {
  if (kind === 'tool' || kind === 'subtool') return 2
  if (kind === 'user') return 0
  return 1
}

export function buildTraceTurns(messages: readonly LedgerMessage[]): TraceTurn[] {
  let index = 0
  return messages.map((message, turn) => buildTraceTurn(message, turn + 1, () => ++index))
}

function buildTraceTurn(message: LedgerMessage, turn: number, nextIndex: () => number): TraceTurn {
  const turnRecordId = `turn:${message.id}`
  const trace = message.trace
  const records: TraceRecord[] = []

  function add(groupTitle: string, record: Omit<TraceRecord, 'index' | 'turn' | 'turnRecordId' | 'groupTitle' | 'lane'>) {
    records.push({ ...record, lane: recordLane(record.kind), index: nextIndex(), turn, turnRecordId, groupTitle })
  }

  if (message.prompt) {
    add('输入', {
      recordId: `${message.id}:user`, kind: 'user', state: 'completed',
      title: '用户输入', text: shortValue(message.prompt), isError: false, timeMs: null,
      startedAtMs: trace?.startedAtMs || null,
      detail: { prompt: message.prompt },
    })
  }

  trace?.routeSteps?.forEach((route, routeIndex) => {
    const attempt = route.attempt || routeIndex + 1
    const error = route.protocolError || (route.failedClosed ? '路由失败关闭' : '') || ''
    add('路由', {
      recordId: `${message.id}:route:${attempt}`, kind: 'route',
      state: error ? 'failed' : 'completed',
      title: `路由 · Attempt ${attempt}`,
      text: error || [route.route, ...(route.bundles || [])].filter(Boolean).join(' · ') || '无可用响应',
      isError: Boolean(error), timeMs: route.durationMs ?? null,
      startedAtMs: route.startedAtMs || null,
      detail: {
        prompt: route.request?.prompt, promptBytes: route.request?.bytes, promptTruncated: route.request?.truncated,
        route: route.route, bundles: route.bundles, attempt, failedClosed: route.failedClosed,
        protocolError: route.protocolError, modelOutput: route.modelOutput, modelDurationMs: route.durationMs,
        startedAtMs: route.startedAtMs,
      },
    })
  })

  trace?.steps.forEach((step) => {
    const noTool = step.actionType === 'no_tool'
    const modelError = step.modelError || ''
    const stageRejected = noTool && Boolean(step.protocolError || step.stageViolation) && !step.protocolRepaired
    const { thinking, rest } = splitModelOutput(step.modelOutput)
    const summary = modelError
      || (noTool ? step.noToolRationale || step.noToolAnswer || '模型决定直接回答' : '')
      || summaryLine(rest)
      || (thinking ? `（仅思考）${summaryLine(thinking)}` : '')
      || step.actionType || '空响应'
    add(`Step ${step.number}`, {
      recordId: `${message.id}:s${step.number}:message`, kind: 'message',
      state: modelError ? 'failed' : 'completed',
      title: `Step ${step.number} · 决策`,
      text: shortValue(summary),
      isError: Boolean(modelError),
      timeMs: step.modelDurationMs ?? null,
      startedAtMs: step.startedAtMs || null,
      tokens: usageTokens(step.usage),
      detail: {
        prompt: step.request?.prompt, promptBytes: step.request?.bytes, promptTruncated: step.request?.truncated,
        toolsOffered: step.request?.toolsOffered, stops: step.request?.stops, maxOutputTokens: step.request?.maxOutputTokens,
        stage: step.stage, actionType: step.actionType, finishReason: step.finishReason,
        modelOutput: step.modelOutput, thinking: thinking || undefined, modelError: step.modelError || undefined,
        noToolRationale: step.noToolRationale, noToolAnswer: step.noToolAnswer,
        protocolError: step.protocolError, protocolRepaired: step.protocolRepaired, stageViolation: step.stageViolation,
        modelDurationMs: step.modelDurationMs, startedAtMs: step.startedAtMs,
      },
    })
    if (step.tool) {
      const rejected = step.toolRejected || ''
      const failed = Boolean(step.toolError || rejected)
      add(`Step ${step.number}`, {
        recordId: `${message.id}:s${step.number}:tool`, kind: 'tool',
        ownerRecordId: `${message.id}:s${step.number}:message`,
        state: failed ? 'failed' : 'completed',
        title: step.tool,
        text: shortValue(step.toolError || rejected || step.toolResult || step.toolArguments || '无参数'),
        isError: failed,
        timeMs: step.toolDurationMs ?? null,
        startedAtMs: step.toolStartedAtMs || null,
        detail: {
          toolName: step.tool, arguments: step.toolArguments, result: step.toolResult,
          startedAtMs: step.toolStartedAtMs,
          executed: step.toolExecuted, evidence: step.toolEvidence, rejected: step.toolRejected || undefined,
          unavailable: step.toolUnavailable, error: step.toolError || undefined,
          toolDurationMs: step.toolDurationMs, retries: step.toolRetries,
        },
      })
    }
    step.subagents?.forEach((child) => {
      const failed = child.status === 'failed'
      add(`Step ${step.number}`, {
        recordId: `${message.id}:s${step.number}:a${child.index}`, kind: 'subtool',
        ownerRecordId: `${message.id}:s${step.number}:message`,
        state: child.status === 'running' ? 'running' : failed ? 'failed' : 'completed',
        title: `子 Agent ${child.index}`,
        text: shortValue(child.error || child.output || child.task || child.status),
        isError: failed,
        timeMs: child.durationMs ?? null,
        startedAtMs: child.startedAtMs || null,
        detail: {
          subagentIndex: child.index, task: child.task, status: child.status, startedAtMs: child.startedAtMs,
          route: child.route, bundles: child.bundles, output: child.output, sources: child.sources,
          error: child.error || undefined,
          subSteps: child.steps?.map((childStep) => ({
            step: childStep.number, tool: childStep.tool, arguments: childStep.arguments,
            status: childStep.status, error: childStep.error,
          })),
          toolDurationMs: child.durationMs,
        },
      })
    })
  })

  if (!trace && message.trajectory?.length) {
    // 历史轨迹：只有工具摘要，合并为 tool 记录，排在最终回复之前。
    message.trajectory.forEach((item, itemIndex) => {
      const failed = item.status === 'failed'
      add(`Step ${item.step}`, {
        recordId: `${message.id}:legacy:${item.step}:${itemIndex}`, kind: 'tool',
        state: item.status === 'running' ? 'running' : failed ? 'failed' : 'completed',
        title: item.tool,
        text: shortValue(item.error || item.arguments || item.status),
        isError: failed, timeMs: null,
        detail: { toolName: item.tool, arguments: item.arguments, error: item.error, retries: item.retries, legacySubagents: item.subagents },
      })
    })
  }

  const repaired = trace?.answerContractRepaired === true
  if (trace?.error || message.role === 'error') {
    add('输出', {
      recordId: `${message.id}:output`, kind: 'output', state: 'failed',
      title: '运行失败', text: shortValue(trace?.error || message.content), isError: true,
      timeMs: null, startedAtMs: trace?.startedAtMs || null,
      detail: {
        error: trace?.error || message.content, output: trace?.output, originalOutput: trace?.originalOutput,
        answerContractRepaired: repaired, forcedAnswerReason: trace?.forcedAnswerReason, answerViolations: trace?.answerViolations,
      },
    })
  } else {
    add('输出', {
      recordId: `${message.id}:output`, kind: 'output', state: 'completed',
      title: '最终回复', text: shortValue(trace?.output || message.content), isError: false,
      timeMs: null, startedAtMs: trace?.startedAtMs || null,
      detail: {
        output: trace?.output || message.content, originalOutput: trace?.originalOutput,
        answerContractRepaired: repaired, forcedAnswerReason: trace?.forcedAnswerReason, answerViolations: trace?.answerViolations,
      },
    })
  }

  return {
    turn,
    turnRecordId,
    header: {
      steps: trace?.steps.length || message.trajectory?.length || 0,
      tools: records.filter((record) => record.kind === 'tool').length,
      subagents: records.filter((record) => record.kind === 'subtool').length,
      durationMs: trace?.durationMs ?? 0,
      isError: message.role === 'error' || Boolean(trace?.error),
      route: trace?.route,
    },
    groups: groupConsecutive(records),
    records,
  }
}

function groupConsecutive(records: readonly TraceRecord[]): TraceGroup[] {
  const groups: TraceGroup[] = []
  for (const record of records) {
    const last = groups.at(-1)
    if (last && last.title === record.groupTitle) last.records.push(record)
    else groups.push({ title: record.groupTitle, records: [record] })
  }
  return groups
}

export function flattenTraceRecords(turns: readonly TraceTurn[]): TraceRecord[] {
  return turns.flatMap((turn) => turn.records)
}

export function turnSummary(turn: TraceTurn): string {
  const parts = [`${turn.header.steps} 步`]
  if (turn.header.tools > 0) parts.push(`${turn.header.tools} 次工具`)
  if (turn.header.subagents > 0) parts.push(`${turn.header.subagents} 路子 Agent`)
  if (turn.header.route) parts.push(`路由 ${turn.header.route}`)
  return parts.join(' · ')
}

function usageTokens(usage?: {
  promptTokens?: number; completionTokens?: number
  cacheReadTokens?: number; reasoningTokens?: number
}) {
  if (!usage) return undefined
  const input = usage.promptTokens ?? 0
  const output = usage.completionTokens ?? 0
  const cacheRead = usage.cacheReadTokens || 0
  const reasoning = usage.reasoningTokens || 0
  if (input === 0 && output === 0 && cacheRead === 0 && reasoning === 0) return undefined
  return { input, output, cacheRead: cacheRead || undefined, reasoning: reasoning || undefined }
}

/** 墙钟时刻展示：HH:MM:SS.mmm（本地时区）。 */
export function formatStartedAt(ms: number) {
  const date = new Date(ms)
  const pad = (value: number, width = 2) => String(value).padStart(width, '0')
  return `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}.${pad(date.getMilliseconds(), 3)}`
}

function firstLine(text?: string) {
  if (!text) return ''
  return text.split('\n', 1)[0] || text
}

/** 拆分前导 <think> 块：闭合时返回思考与正文，未闭合时正文为空。 */
function splitThink(output?: string): { thinking: string; rest: string } {
  if (!output) return { thinking: '', rest: '' }
  const trimmed = output.trimStart()
  if (!trimmed.startsWith('<think>')) return { thinking: '', rest: output }
  const body = trimmed.slice(7)
  const close = body.indexOf('</think>')
  if (close === -1) return { thinking: body.trim(), rest: '' }
  return { thinking: body.slice(0, close).trim(), rest: body.slice(close + 8).trim() }
}

/*
 * 快思考/完整思考预填把 think 标签的收尾字节扣在 prompt 末尾（"<think></think" 缺
 * ">"，"<think" 缺 ">"），模型的首个输出字节是补位的 ">"，随后才是思考块或协议动作。
 * 它是框架字节而非内容：仅当 ">" 之后紧跟协议动作或思考块开头时才剥掉，其余场景
 * （如 Markdown 引用）原样保留。原始字节始终保留在 detail.modelOutput / 原文页签。
 */
const PROTOCOL_ACTION_OPENINGS = ['<tool_call>', '<answer>', '```json', '<think>', '{']

function stripAssistantFraming(output: string): string {
  const trimmed = output.trimStart()
  if (!trimmed.startsWith('>')) return output
  const body = trimmed.replace(/^>\s*/, '')
  return PROTOCOL_ACTION_OPENINGS.some((opening) => body.startsWith(opening)) ? body : output
}

/** 展示层统一的模型输出拆分：先剥框架字节，再拆前导 think 块。 */
export function splitModelOutput(output?: string): { thinking: string; rest: string } {
  const { thinking, rest } = splitThink(stripAssistantFraming(output ?? ''))
  return { thinking, rest }
}

/** 摘要取行：跳过代码围栏与孤立的括号行，取第一行有信息量的内容。 */
function summaryLine(text?: string) {
  if (!text) return ''
  const lines = text.split('\n').map((line) => line.trim()).filter(Boolean)
  for (const line of lines) {
    if (/^(```[a-zA-Z]*|[{}[\]])$/.test(line)) continue
    return line
  }
  return lines[0] || ''
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
