import { useEffect, useRef, useState } from 'react'
import {
  CheckCircle2,
  ChevronDown,
  ExternalLink,
  LoaderCircle,
  RefreshCw,
  Users,
  Wrench,
  XCircle,
} from 'lucide-react'

export type ToolRetryTrace = {
  attempt: number
  maxAttempts: number
  statusCode?: number
  delayMs: number
}

export type SubagentStep = {
  step: number
  tool: string
  arguments?: string
  status: 'running' | 'completed' | 'failed'
  error?: string
  retries?: ToolRetryTrace[]
}

export type SubagentTrace = {
  index: number
  task: string
  status: 'running' | 'completed' | 'failed'
  error?: string
  route?: string
  bundles?: string[]
  durationMs?: number
  output?: string
  sources?: string[]
  steps?: SubagentStep[]
}

export type ToolTrace = {
  step: number
  tool: string
  arguments?: string
  status: 'running' | 'completed' | 'failed'
  error?: string
  retries?: ToolRetryTrace[]
  subagents?: SubagentTrace[]
}

type ToolTrajectoryProps = {
  calls: ToolTrace[]
  done: boolean
  status?: string
}

export default function ToolTrajectory({ calls, done, status }: ToolTrajectoryProps) {
  const [expanded, setExpanded] = useState(false)
  const [animationKey, setAnimationKey] = useState(0)
  const toolFailures = calls.filter((call) => call.status === 'failed').length
  const subagentFailures = calls.reduce(
    (count, call) => count + (call.subagents?.filter((child) => child.status === 'failed').length || 0),
    0,
  )
  const failures = toolFailures + subagentFailures
  const subagentCount = calls.reduce((count, call) => count + (call.subagents?.length || 0), 0)
  const summary = toolFailures > 0
    ? `完成 ${calls.length} 次工具调用，${toolFailures} 次失败`
    : subagentFailures > 0
      ? `已完成 ${calls.length} 次工具调用，${subagentFailures} 个子 Agent 失败`
    : `已完成 ${calls.length} 次工具调用`
  const latest = done ? summary : status || 'Agent 正在工作…'
  const [current, setCurrent] = useState(latest)
  const [outgoing, setOutgoing] = useState<string | null>(null)
  const previous = useRef(latest)
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const bodyOpen = !done || expanded

  useEffect(() => {
    if (latest === previous.current) return
    if (timer.current) clearTimeout(timer.current)
    setOutgoing(previous.current)
    setCurrent(latest)
    previous.current = latest
    timer.current = setTimeout(() => setOutgoing(null), 350)
    return () => {
      if (timer.current) clearTimeout(timer.current)
    }
  }, [latest])

  function toggle() {
    if (!done || calls.length === 0) return
    setExpanded((value) => {
      if (!value) setAnimationKey((key) => key + 1)
      return !value
    })
  }

  return (
    <div className={`tool-trajectory${failures > 0 ? ' has-failures' : ''}`}>
      <div className="trajectory-stage" aria-live="polite">
        <div className={outgoing ? 'trajectory-track sliding' : 'trajectory-track'}>
          {outgoing && <TrajectoryPill text={outgoing} />}
          <button
            type="button"
            className={`trajectory-pill${done ? ' done' : ''}`}
            onClick={toggle}
            disabled={!done || calls.length === 0}
            aria-expanded={done ? expanded : undefined}
          >
            {done
              ? failures > 0 ? <XCircle size={15} /> : <CheckCircle2 size={15} />
              : <LoaderCircle className="spin" size={15} />}
            <span>{current}{done && subagentCount > 0 ? ` · ${subagentCount} 个子 Agent` : ''}</span>
            {done && calls.length > 0 && <ChevronDown className={expanded ? 'open' : ''} size={15} />}
          </button>
        </div>
      </div>

      {calls.length > 0 && (
        <div className={`trajectory-body${bodyOpen ? ' open' : ''}`}>
          <ol className="trajectory-list" key={animationKey}>
            {calls.map((call, index) => (
              <li
                className={`trajectory-item ${call.status}`}
                style={{ animationDelay: `${index * 35}ms` }}
                key={`${call.step}-${call.tool}-${index}`}
              >
                <div className="trajectory-call">
                  <StatusIcon status={call.status} tool />
                  <div className="trajectory-call-copy">
                    <span className="trajectory-tool">
                      {call.tool}
                      {!!call.subagents?.length && <span className="trajectory-agent-count"> · {call.subagents.length} 个子 Agent</span>}
                    </span>
                    <span className="trajectory-step">步骤 {call.step} · {statusText(call.status)}</span>
                    {call.error && <span className="trajectory-error">{call.error}</span>}
                    {!!call.retries?.length && <RetryList values={call.retries} />}
                  </div>
                </div>
                {!!call.subagents?.length && <SubagentList values={call.subagents} live={!done} />}
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  )
}

function SubagentList({ values, live }: { values: SubagentTrace[]; live: boolean }) {
  return (
    <div className="subagent-list">
      {values.map((child) => (
        <details className={`subagent-trace ${child.status}`} key={`${child.index}-${child.task}`} open={live}>
          <summary>
            <StatusIcon status={child.status} />
            <span className="subagent-title">Agent {child.index}</span>
            <span className="subagent-task">{child.task}</span>
            {child.durationMs !== undefined && child.durationMs > 0 && (
              <span className="subagent-duration">{formatDuration(child.durationMs)}</span>
            )}
            <ChevronDown className="subagent-chevron" size={14} />
          </summary>
          <div className="subagent-body">
            {(child.route || child.bundles?.length) && (
              <div className="subagent-route">
                {child.route && <span>route: {child.route}</span>}
                {!!child.bundles?.length && <span>bundles: {child.bundles.join(', ')}</span>}
              </div>
            )}
            {!!child.steps?.length && (
              <ol className="subagent-steps">
                {child.steps.map((step, index) => (
                  <li className={step.status} key={`${step.step}-${step.tool}-${index}`}>
                    <StatusIcon status={step.status} tool />
                    <div>
                      <span className="trajectory-tool">{step.tool}</span>
                      {step.arguments && <code>{formatArguments(step.arguments)}</code>}
                      {step.error && <span className="trajectory-error">{step.error}</span>}
                      {!!step.retries?.length && <RetryList values={step.retries} />}
                    </div>
                  </li>
                ))}
              </ol>
            )}
            {child.error && <div className="subagent-error">{child.error}</div>}
            {child.output && (
              <div className="subagent-output">
                <span>输出</span>
                <p>{child.output}</p>
              </div>
            )}
            {!!child.sources?.length && (
              <div className="subagent-sources">
                <span>来源</span>
                {child.sources.map((source) => (
                  <a href={source} target="_blank" rel="noreferrer" key={source}>
                    <ExternalLink size={12} />
                    <span>{source}</span>
                  </a>
                ))}
              </div>
            )}
          </div>
        </details>
      ))}
    </div>
  )
}

function RetryList({ values }: { values: ToolRetryTrace[] }) {
  return (
    <div className="trajectory-retries">
      {values.map((retry, index) => (
        <div className="trajectory-retry" key={`${retry.attempt}-${retry.statusCode || 0}-${index}`}>
          <RefreshCw size={11} />
          <span>
            尝试 {retry.attempt}/{retry.maxAttempts}
            {retry.statusCode ? ` · HTTP ${retry.statusCode}` : ' · 网络错误'}
            {` · ${formatRetryDelay(retry.delayMs)}后重试`}
          </span>
        </div>
      ))}
    </div>
  )
}

function StatusIcon({ status, tool = false }: { status: ToolTrace['status']; tool?: boolean }) {
  if (status === 'running') return <LoaderCircle className="spin" size={13} />
  if (status === 'failed') return <XCircle size={13} />
  return tool ? <Wrench size={13} /> : <Users size={13} />
}

function statusText(status: ToolTrace['status']) {
  if (status === 'running') return '进行中'
  if (status === 'failed') return '失败'
  return '已完成'
}

function formatDuration(durationMs: number) {
  return `${(durationMs / 1000).toFixed(1)} 秒`
}

function formatRetryDelay(delayMs: number) {
  if (delayMs < 1000) return `${delayMs} 毫秒`
  return `${(delayMs / 1000).toFixed(delayMs % 1000 === 0 ? 0 : 1)} 秒`
}

function formatArguments(value: string) {
  try {
    return JSON.stringify(JSON.parse(value))
  } catch {
    return value
  }
}

function TrajectoryPill({ text }: { text: string }) {
  return (
    <div className="trajectory-pill">
      <LoaderCircle className="spin" size={15} />
      <span>{text}</span>
    </div>
  )
}
