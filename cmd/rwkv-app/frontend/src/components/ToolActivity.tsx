import { useState } from 'react'
import {
  ChevronDown, ChevronRight, FilePen, FileText, FolderTree, Globe, Loader2, Network,
  Search, Terminal, Wrench, X, type LucideIcon,
} from 'lucide-react'
import PixelLoader from './PixelLoader'
import { isKnownTool, toolRunning, toolSummary, toolVerb } from '../i18n/toolLabels'
import type { Step } from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { SubagentTrace, ToolTrace } from '../trajectory-types'

/*
 * 对话区的工具调用卡片（参照 Claude 网页版）：
 * - 收起时一行摘要：运行中显示最新一次调用，结束后按工具汇总，连续同名调用记 ×N。
 * - 展开后一行一个调用组；连续调用同一工具合并成一行并刷新为最新一次的参数。
 * - 每行再展开看参数、结果、错误；子 Agent 也作为 spawn_agents 行的详情。
 */

export type ToolCall = {
  id: string
  tool: string
  arguments?: string
  result?: string
  error?: string
  status: 'running' | 'completed' | 'failed'
  durationMs?: number
  subagents?: SubagentTrace[]
}

type CallGroup = { id: string; tool: string; calls: ToolCall[] }

/** 落定的回合：优先用完整 trace（含结果），否则退回历史轨迹摘要。 */
export function callsFromSteps(steps: readonly Step[]): ToolCall[] {
  return steps.filter((step) => step.tool).map((step) => {
    const error = step.toolError || step.toolRejected || ''
    return {
      id: `s${step.number}`, tool: step.tool || '', arguments: step.toolArguments,
      result: step.toolResult, error: error || undefined,
      status: error ? 'failed' : 'completed', durationMs: step.toolDurationMs,
      subagents: step.subagents?.map((child) => ({
        index: child.index, task: child.task, status: child.status as SubagentTrace['status'],
        error: child.error, durationMs: child.durationMs, output: child.output,
        steps: child.steps?.map((childStep) => ({ step: childStep.number, tool: childStep.tool, arguments: childStep.arguments, status: childStep.status as 'completed' | 'failed', error: childStep.error })),
      })),
    }
  })
}

export function callsFromTrajectory(trajectory: readonly ToolTrace[]): ToolCall[] {
  return trajectory.map((item, index) => ({
    id: `t${item.step}:${index}`, tool: item.tool, arguments: item.arguments, error: item.error,
    status: item.status, subagents: item.subagents,
  }))
}

type LiveEvent = {
  kind: string; step?: number; parentStep?: number; tool?: string; arguments?: string
  subagentIndex?: number; subagentTask?: string; durationMs?: number; error?: string
}

/** 运行中的回合：由 agent:event 流拼出调用列表；子 Agent 事件挂到父步骤的 spawn 调用下。 */
export function callsFromEvents(events: readonly LiveEvent[]): ToolCall[] {
  const calls: ToolCall[] = []
  const byStep = new Map<number, ToolCall>()
  for (const event of events) {
    if (event.subagentIndex) {
      const parent = byStep.get(event.parentStep || 0)
      if (!parent) continue
      const agents = parent.subagents ||= []
      let agent = agents.find((item) => item.index === event.subagentIndex)
      if (!agent) {
        agent = { index: event.subagentIndex, task: event.subagentTask || '', status: 'running', steps: [] }
        agents.push(agent)
      }
      if (event.kind === 'subagent_done') {
        agent.status = event.error ? 'failed' : 'completed'
        agent.error = event.error
        agent.durationMs = event.durationMs
      } else if (event.kind === 'tool_start' && event.tool) {
        agent.steps = [...(agent.steps || []), { step: event.step || 0, tool: event.tool, arguments: event.arguments, status: 'running' }]
      } else if (event.kind === 'tool_done') {
        const last = [...(agent.steps || [])].reverse().find((item) => item.step === event.step)
        if (last) { last.status = event.error ? 'failed' : 'completed'; last.error = event.error }
      }
      continue
    }
    if (event.kind === 'tool_start' && event.tool) {
      const call: ToolCall = { id: `live${event.step || calls.length}`, tool: event.tool, arguments: event.arguments, status: 'running' }
      calls.push(call)
      byStep.set(event.step || 0, call)
    } else if (event.kind === 'tool_done') {
      const call = byStep.get(event.step || 0)
      if (!call) continue
      call.status = event.error ? 'failed' : 'completed'
      call.error = event.error
      call.durationMs = event.durationMs
    }
  }
  return calls
}

function groupCalls(calls: readonly ToolCall[]): CallGroup[] {
  const groups: CallGroup[] = []
  for (const call of calls) {
    const last = groups.at(-1)
    if (last && last.tool === call.tool) last.calls.push(call)
    else groups.push({ id: call.id, tool: call.tool, calls: [call] })
  }
  return groups
}

/** 运行中的小号标记：单格 R 彗星，和一行小字等高。 */
export function ThinkingMark() {
  return <PixelLoader className="text-ink" layout="single" animation="comet" cell={1.7} gap={0.3} baseAlpha={0.1} label="Agent 运行中" />
}

type Props = {
  calls: readonly ToolCall[]
  running?: boolean
  /** 运行中摘要行的文字（如「步骤 3 · 正在决定下一步」）；不传则用最新调用。 */
  liveLabel?: string
}

export default function ToolActivity({ calls, running = false, liveLabel }: Props) {
  const [open, setOpen] = useState(false)
  if (calls.length === 0) return null
  const groups = groupCalls(calls)
  const failed = calls.filter((call) => call.status === 'failed').length
  const latest = groups.at(-1)!

  return <div className="tool-activity text-sm" data-testid="tool-activity">
    <button type="button" aria-expanded={open} onClick={() => setOpen((value) => !value)} className="group flex max-w-full items-center gap-[6px] border-0 bg-transparent p-0 text-left text-ink-muted transition-colors hover:text-ink">
      {running && <ThinkingMark />}
      {running
        ? <span className="shimmer-text min-w-0 truncate">{liveLabel || `${toolRunning(latest.tool)} ${primaryArg(latest.calls.at(-1)!)}`.trim()}</span>
        : <span className="min-w-0 truncate">{summarize(groups)}{failed > 0 && <span className="text-danger"> · {failed} 次失败</span>}</span>}
      {open ? <ChevronDown size={15} className="flex-none" /> : <ChevronRight size={15} className="flex-none" />}
    </button>
    {open && <div className="tool-activity-panel mt-[10px] overflow-hidden rounded-xl border border-line bg-card-bg">
      {groups.map((group) => <GroupRow key={group.id} group={group} />)}
    </div>}
  </div>
}

function GroupRow({ group }: { group: CallGroup }) {
  const [open, setOpen] = useState(false)
  const latest = group.calls.at(-1)!
  const Icon = toolIcon(group.tool)
  const verb = toolVerb(group.tool)
  const isRunning = group.calls.some((call) => call.status === 'running')
  const failed = group.calls.some((call) => call.status === 'failed')
  const duration = group.calls.reduce((sum, call) => sum + (call.durationMs || 0), 0)
  const target = primaryArg(latest)

  return <div className="border-b border-line last:border-b-0">
    <button type="button" aria-expanded={open} onClick={() => setOpen((value) => !value)} className="flex w-full min-w-0 items-center gap-[10px] border-0 bg-transparent px-[14px] py-[10px] text-left transition-colors hover:bg-surface-active">
      <Icon size={15} className="flex-none text-ink-muted" />
      <span className="flex-none text-ink-muted">{verb}</span>
      <span className="min-w-0 truncate text-ink" title={target}>{target}</span>
      {group.calls.length > 1 && <span className="flex-none rounded-md bg-surface-active px-[6px] py-[1px] font-mono text-2xs text-ink-soft">×{group.calls.length}</span>}
      <span className="flex-1" />
      {isRunning
        ? <Loader2 size={13} className="spin flex-none text-ink-muted" aria-label="运行中" />
        : <>
          {failed && <X size={13} className="flex-none text-danger" aria-label="失败" />}
          {duration > 0 && <span className="flex-none font-mono text-2xs text-ink-ghost">{formatDuration(duration)}</span>}
        </>}
      <ChevronRight size={14} className={`flex-none text-ink-ghost transition-transform duration-150 ${open ? 'rotate-90' : ''}`} />
    </button>
    {open && <div className="flex flex-col gap-[14px] border-t border-line-soft bg-paper-soft px-[14px] py-[12px]">
      {group.calls.map((call, index) => <CallDetail key={call.id} call={call} order={group.calls.length > 1 ? index + 1 : undefined} />)}
    </div>}
  </div>
}

function CallDetail({ call, order }: { call: ToolCall; order?: number }) {
  return <div className="flex min-w-0 flex-col gap-[8px]">
    {order != null && <div className="flex items-center gap-2 font-mono text-2xs text-ink-muted">
      <span>#{order}</span>
      {call.status === 'running' && <span>运行中</span>}
      {call.status === 'failed' && <span className="text-danger">失败</span>}
      {call.durationMs != null && <span className="text-ink-ghost">{formatDuration(call.durationMs)}</span>}
    </div>}
    <Block label="参数" text={prettyJSON(call.arguments) || '无参数'} />
    {call.error && <Block label="错误" text={call.error} danger />}
    {call.result != null && call.result !== '' && <Block label="结果" text={resultText(call.result)} />}
    {call.subagents?.length ? <div className="flex flex-col gap-[8px]">
      <span className="text-2xs text-ink-muted">子 Agent</span>
      {call.subagents.map((agent) => <SubagentDetail key={agent.index} agent={agent} />)}
    </div> : null}
  </div>
}

function SubagentDetail({ agent }: { agent: SubagentTrace }) {
  return <div className="rounded-lg border border-line bg-card-bg px-[12px] py-[10px]">
    <div className="flex items-center gap-2 text-xs">
      <span className="font-mono text-2xs text-ink-muted">Agent {agent.index}</span>
      <span className="min-w-0 flex-1 truncate text-ink">{agent.task}</span>
      {agent.status === 'running' ? <Loader2 size={12} className="spin text-ink-muted" /> : agent.status === 'failed' ? <X size={12} className="text-danger" /> : null}
      {agent.durationMs != null && <span className="font-mono text-2xs text-ink-ghost">{formatDuration(agent.durationMs)}</span>}
    </div>
    {agent.steps?.length ? <div className="mt-[6px] flex flex-wrap gap-x-3 gap-y-1 font-mono text-2xs text-ink-muted">
      {agent.steps.map((step, index) => <span key={`${step.step}-${index}`} className={step.status === 'failed' ? 'text-danger' : ''}>{step.tool}</span>)}
    </div> : null}
    {(agent.error || agent.output) && <div className={`mt-[6px] text-xs leading-[1.6] ${agent.error ? 'text-danger' : 'text-ink-soft'}`}>{agent.error || agent.output}</div>}
  </div>
}

function Block({ label, text, danger }: { label: string; text: string; danger?: boolean }) {
  return <div className="flex min-w-0 flex-col gap-[4px]">
    <span className="text-2xs text-ink-muted">{label}</span>
    <pre className={`m-0 max-h-[240px] overflow-auto whitespace-pre-wrap rounded-lg border border-line bg-card-bg px-[10px] py-[8px] font-mono text-2xs leading-[1.6] [overflow-wrap:anywhere] ${danger ? 'text-danger' : 'text-ink-soft'}`}>{text}</pre>
  </div>
}

/** 工具名 → 图标；文案见 i18n/toolLabels。 */
function toolIcon(tool: string): LucideIcon {
  const name = tool.toLowerCase()
  if (name === 'spawn_agents') return Network
  if (/web|fetch|url|browse/.test(name)) return Globe
  if (/search|grep|find/.test(name)) return Search
  if (/list|tree|dir/.test(name)) return FolderTree
  if (/write|edit|create|patch|replace|append/.test(name)) return FilePen
  if (/read|open|cat|view/.test(name)) return FileText
  if (/script|shell|bash|exec|run|command/.test(name)) return Terminal
  return Wrench
}

const PRIMARY_KEYS = ['path', 'file', 'filename', 'query', 'url', 'pattern', 'command', 'script', 'dir', 'directory', 'name']

/** 一行里最能说明这次调用的参数：路径/查询/命令等；识别不了就给工具名或压缩的参数。 */
function primaryArg(call: ToolCall): string {
  const parsed = parseJSON(call.arguments)
  if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
    const record = parsed as Record<string, unknown>
    if (call.tool === 'spawn_agents' && Array.isArray(record.tasks)) return `${record.tasks.length} 个子任务`
    for (const key of PRIMARY_KEYS) {
      const value = record[key]
      if (typeof value === 'string' && value.trim()) return value.trim()
    }
    const first = Object.values(record).find((value) => typeof value === 'string' && value.trim())
    if (typeof first === 'string') return first.trim()
  }
  return isKnownTool(call.tool) ? '' : call.tool
}

function summarize(groups: readonly CallGroup[]): string {
  const counts = new Map<string, number>()
  for (const group of groups) counts.set(group.tool, (counts.get(group.tool) || 0) + group.calls.length)
  return toolSummary([...counts])
}

function parseJSON(value?: string): unknown {
  if (!value) return undefined
  try { return JSON.parse(value) } catch { return undefined }
}

function prettyJSON(value?: string) {
  if (!value) return value
  const parsed = parseJSON(value)
  return parsed === undefined || typeof parsed === 'string' ? value : JSON.stringify(parsed, null, 2)
}

const BODY_KEYS = ['content', 'text', 'output', 'stdout', 'body']

/** 结果展示：剥掉 {ok, tool, result} 外壳，有正文字段（文件内容、网页文本、命令输出）就直接显示正文。 */
export function resultText(value: string): string {
  const parsed = parseJSON(value)
  if (parsed === undefined) return value
  let inner: unknown = parsed
  if (inner && typeof inner === 'object' && !Array.isArray(inner) && 'result' in inner) inner = (inner as Record<string, unknown>).result
  if (typeof inner === 'string') return inner
  if (inner && typeof inner === 'object' && !Array.isArray(inner)) {
    const record = inner as Record<string, unknown>
    const key = BODY_KEYS.find((name) => typeof record[name] === 'string' && record[name])
    if (key) return record[key] as string
  }
  return JSON.stringify(inner, null, 2)
}

function formatDuration(durationMs: number) {
  return durationMs < 1000 ? `${durationMs} ms` : `${(durationMs / 1000).toFixed(1)} s`
}
