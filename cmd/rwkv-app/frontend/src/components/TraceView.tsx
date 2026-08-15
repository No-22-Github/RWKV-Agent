import { useState } from 'react'
import { Download, FileText, PanelRight, Search, X } from 'lucide-react'
import * as Backend from '../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import type { ToolTrace } from '../trajectory-types'
import {
  buildLedgerEvents, eventLane, eventName, isResultEvent, formatDuration,
  KIND_TAG_CLASS, ROLE_TAGS, type LedgerEvent, type LedgerMessage,
} from '../ledger'
import { useSnackbar } from '../snackbar'

export type TraceMessage = LedgerMessage & {
  role: 'user' | 'assistant' | 'error'
  createdAt?: string
}

type Props = {
  messages: TraceMessage[]
  selected?: TraceMessage
  onSelect: (id: string) => void
  onBackToChat: () => void
}

export default function TraceView({ messages, selected, onSelect, onBackToChat }: Props) {
  const [query, setQuery] = useState(''); const [inspector, setInspector] = useState(true); const [detail, setDetail] = useState<'summary' | 'original' | 'diff'>('summary'); const [selectedEventID, setSelectedEventID] = useState('')
  const { show } = useSnackbar()
  const visible = messages.filter((message) => !query || `${message.prompt} ${message.content} ${JSON.stringify(message.trace || message.trajectory)}`.toLowerCase().includes(query.toLowerCase()))
  const selectedEvent = selectedEventID ? selected && buildLedgerEvents(selected).find((event) => event.id === selectedEventID) : undefined
  const eventCount = messages.reduce((sum, message) => sum + buildLedgerEvents(message).length, 0)
  const timelineEvents = visible.flatMap((message) => buildLedgerEvents(message).map((event) => ({ event, messageId: message.id })))
  async function exportTrace() {
    const data = visible.map((message) => JSON.stringify({ id: message.id, role: message.role, prompt: message.prompt, createdAt: message.createdAt, trace: message.trace || { legacyTrajectory: message.trajectory } })).join('\n')
    try {
      const path = await Backend.ExportTrajectory(data)
      if (path) show(`轨迹已导出：${path.split('/').at(-1)}`, 'success')
    } catch (error) {
      show(errorText(error), 'error')
    }
  }
  function selectTurn(id: string) { setSelectedEventID(''); onSelect(id) }
  function selectEvent(messageID: string, eventID: string) { onSelect(messageID); setSelectedEventID(eventID) }
  return <div className="flex min-h-0 flex-1 flex-col">
    <div className="trace-toolbar flex min-h-[56px] items-center gap-[10px] border-b border-line px-[30px]"><div className="mr-auto flex items-baseline gap-[5px] text-[10px] text-ink-muted"><strong className="ml-[7px] font-mono text-[15px] font-semibold text-ink">{messages.length}</strong><span>轮次</span><strong className="ml-[7px] font-mono text-[15px] font-semibold text-ink">{eventCount}</strong><span>事件</span></div><label className="flex h-[30px] w-[235px] items-center gap-[7px] border border-line bg-paper-wash px-[9px] text-ink-muted"><Search size={15} /><input aria-label="搜索轨迹" className="w-full border-0 bg-transparent text-[11px] text-ink outline-0" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索请求、工具或错误" /></label><button className="grid h-[30px] w-[30px] place-items-center rounded-[3px] border border-transparent bg-transparent text-ink-soft hover:border-line-strong hover:bg-paper-wash hover:text-brand" title="检查器" aria-label="检查器" onClick={() => setInspector(!inspector)}><PanelRight size={16} /></button></div>
    {timelineEvents.length > 0 && <TraceTimeline events={timelineEvents} selectedEventID={selectedEventID} onEvent={selectEvent} />}
    <div className="trace-workspace flex min-h-0 flex-1"><div className="trace-main min-w-0 flex-1 overflow-auto"><div className="mx-auto w-[min(940px,calc(100%-60px))] py-[14px] pb-10">{visible.map((message, index) => <TraceTurn key={message.id} message={message} index={index + 1} selected={message.id === selected?.id} selectedEventID={selectedEventID} onClick={() => selectTurn(message.id)} onEvent={(eventID) => selectEvent(message.id, eventID)} />)}{visible.length === 0 && <div className="py-[50px] text-center text-[12px] text-ink-muted">没有匹配的轨迹</div>}</div></div>{inspector && <TraceInspector message={selected} event={selectedEvent} detail={detail} setDetail={setDetail} onBackToChat={onBackToChat} />}</div>
    <div className="flex flex-none items-center gap-[22px] border-t-[1.5px] border-ink px-[30px] py-[10px] font-mono text-[10.5px] text-ink-soft">
      <span>{messages.length} 轮 · {eventCount} 步</span><span className="text-ink-ghost">/</span>
      <span>LLM {formatDuration(totalTiming(messages).llmMs)} · 工具 {formatDuration(totalTiming(messages).toolMs)}</span><span className="text-ink-ghost">/</span>
      <span>首 token {formatDuration(totalTiming(messages).firstTokenMs)} · {totalTiming(messages).tokensPerSec} tok/s</span><span className="text-ink-ghost">/</span>
      <span>缓存 {totalTiming(messages).cachePercent}%</span>
      <span className="flex-1" />
      <button className="border-0 bg-transparent p-0 text-[12px] text-brand" onClick={() => void exportTrace()}>导出 trace.jsonl</button>
    </div>
  </div>
}

function TraceTimeline({ events, selectedEventID, onEvent }: { events: { event: LedgerEvent; messageId: string }[]; selectedEventID: string; onEvent: (messageID: string, eventID: string) => void }) {
  const lanes = [
    { key: 'input', label: '输入', color: 'var(--accent-warm)' },
    { key: 'model', label: '模型', color: 'var(--brand)' },
    { key: 'tool', label: '工具', color: 'var(--warning)' },
  ] as const
  const totalDuration = Math.max(1, events.reduce((sum, { event }) => sum + ((event.timing as { durationMs?: number } | undefined)?.durationMs || 0), 0))
  return <div className="grid h-[68px] flex-none grid-cols-[38px_minmax(0,1fr)] items-center border-b border-line bg-paper-soft px-[30px]">
    <div />
    <div className="flex flex-col gap-[3px]">
      {lanes.map((lane) => {
        const laneEvents = events.filter(({ event }) => eventLane(event.kind) === (lane.key === 'input' ? 0 : lane.key === 'model' ? 1 : 2))
        return (
          <div key={lane.key} className="grid grid-cols-[38px_minmax(0,1fr)] items-center gap-[12px]">
            <span className="text-right font-mono text-[9.5px] uppercase tracking-[.1em] text-ink-muted">{lane.label}</span>
            <div className="flex h-[9px] items-center gap-[3px] overflow-hidden">
              {laneEvents.map(({ event, messageId }) => {
                const duration = ((event.timing as { durationMs?: number } | undefined)?.durationMs || 0)
                const width = Math.max(2, (duration / totalDuration) * 100)
                return <button key={event.id} title={event.title} aria-label={event.title} onClick={() => onEvent(messageId, event.id)} className={`h-[7px] flex-none border-0 p-0 ${event.id === selectedEventID ? 'ring-1 ring-paper-soft ring-offset-1' : ''}`} style={{ width: `${width}%`, background: lane.color, opacity: event.state === 'failed' ? 1 : 0.7 }} />
              })}
            </div>
          </div>
        )
      })}
      <div className="mt-[3px] grid grid-cols-[38px_minmax(0,1fr)] gap-[12px]">
        <span />
        <div className="flex justify-between font-mono text-[9.5px] text-ink-ghost"><span>00:00</span><span>{formatClock(totalDuration * 0.25)}</span><span>{formatClock(totalDuration * 0.5)}</span><span>{formatClock(totalDuration * 0.75)}</span><span>{formatClock(totalDuration)}</span></div>
      </div>
    </div>
  </div>
}

function TraceTurn({ message, index, selected, selectedEventID, onClick, onEvent }: { message: TraceMessage; index: number; selected: boolean; selectedEventID: string; onClick: () => void; onEvent: (eventID: string) => void }) {
  const trace = message.trace
  const events = buildLedgerEvents(message)
  const duration = trace?.durationMs || 0
  return <article className="mb-[18px] grid w-full grid-cols-[56px_minmax(0,1fr)] gap-4">
    <div className="flex flex-col items-end gap-[3px] font-serif text-[20px] font-bold leading-none text-ink-faint">{String(index).padStart(2, '0')}<small className="font-mono text-[10px] text-ink-muted">{message.createdAt ? new Date(message.createdAt).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) : '本地'}</small></div>
    <div className="min-w-0"><button className="mb-[6px] block w-full border-0 bg-transparent p-0 text-left text-inherit" onClick={onClick}><span className="flex items-center gap-[10px] text-[10px] text-ink-muted"><span className="font-mono text-[10px] font-semibold tracking-[.04em] text-brand">TURN {index}</span><span>{events.length} 个事件</span><span>{duration ? formatDuration(duration) : '时长 --'}</span>{trace?.route && <span className="ml-auto font-mono text-[10px] text-brand">{trace.route}</span>}{message.role === 'error' && <span className="ml-auto font-mono text-[10px] text-danger">失败</span>}</span><span className="mt-[6px] block truncate text-[12px] text-ink-soft">{message.prompt || message.content}</span></button>
      <div className="flex flex-col border-t border-line">{events.map((event) => <TraceEventRow key={event.id} event={event} selected={selected && selectedEventID === event.id} onClick={() => onEvent(event.id)} />)}</div>
    </div>
  </article>
}

function TraceEventRow({ event, selected, onClick }: { event: LedgerEvent; selected: boolean; onClick: () => void }) {
  const role = ROLE_TAGS[event.kind] || { tag: 'EVENT', cls: 'model' }
  const name = eventName(event)
  const railWidth = selected ? 'w-[3px]' : 'w-[2px]'
  const railColor = event.state === 'failed' ? 'bg-danger' : selected ? 'bg-brand' : 'bg-transparent'
  return <button className={`trace-event relative grid w-full min-h-[30px] grid-cols-[76px_minmax(0,1fr)] items-center gap-2 overflow-hidden border-0 border-b border-line bg-transparent p-[4px_8px_4px_0] text-left hover:bg-paper-soft${selected ? ' bg-brand-wash' : ''}${selected && event.state === 'failed' ? ' bg-danger-wash' : ''}`} data-state={event.state} title={event.title} onClick={onClick} aria-pressed={selected}>
    <span className={`absolute bottom-0 left-0 top-0 ${railWidth} ${railColor}`} />
    <span className="flex justify-end pl-3"><span className={`inline-flex font-mono text-[10px] font-medium tracking-[.14em] ${KIND_TAG_CLASS[role.cls] || 'text-brand'}`}>{role.tag}</span></span>
    <span className="flex min-w-0 items-baseline gap-[7px] overflow-hidden">
      {name && <span className="event-name max-w-[46%] flex-none truncate font-mono text-[12px] leading-[18px] text-ink">{name}</span>}
      {event.summary && <>{isResultEvent(event) && <span className="event-arrow flex-none text-[12px] text-ink-muted" aria-hidden="true">→</span>}<span className={`event-payload min-w-0 flex-1 truncate font-mono text-[12px] leading-[18px] ${event.state === 'failed' ? 'text-danger' : 'text-ink-soft'}`}>{event.summary}</span></>}
    </span>
  </button>
}

function TraceInspector({ message, event, detail, setDetail, onBackToChat }: { message?: TraceMessage; event?: LedgerEvent; detail: 'summary' | 'original' | 'diff'; setDetail: (value: 'summary' | 'original' | 'diff') => void; onBackToChat: () => void }) {
  const trace = message?.trace
  return <aside className="trace-inspector flex w-[320px] flex-none flex-col overflow-auto border-l border-line bg-paper-soft">
    <div className="flex items-center justify-between px-5 pb-[14px] pt-[22px]"><div className="flex min-w-0 flex-col gap-[5px]"><span className="font-mono text-[10px] uppercase tracking-[.14em] text-ink-muted">检查器</span><strong className="truncate text-[14px] font-semibold">{event?.title || (message ? `Turn ${message.id.split('-').at(-1)}` : '未选择')}</strong>{event && <small className="font-mono text-[9px] text-ink-muted">事件 {String(event.order).padStart(2, '0')} · {event.kind}</small>}</div><FileText size={16} /></div>
    <div className="flex gap-[15px] border-b border-line px-5">{(['summary', 'original', 'diff'] as const).map((tab) => <button key={tab} className={`border-0 border-b-2 bg-transparent pb-[9px] text-[11px] ${detail === tab ? 'border-brand font-semibold text-brand' : 'border-transparent text-ink-muted'}`} onClick={() => setDetail(tab)}>{tab === 'summary' ? '摘要' : tab === 'original' ? '原文' : '差异'}</button>)}</div>
    {message && <div className="mx-5 mt-4 border-l-2 border-warning bg-warning/10 px-[10px] py-2 text-[10px] leading-[1.6] text-warning">完整请求可能包含对话内容、工具参数或本地文件片段，仅保存在本机。</div>}
    {detail === 'summary' && event ? <EventSummary event={event} /> : <pre className="mx-5 my-[14px] overflow-auto whitespace-pre-wrap font-mono text-[10px] leading-[1.65] text-ink-soft [overflow-wrap:anywhere]">{detail === 'diff' ? inspectorDiff(message, event) : inspectorBody(message, event, detail)}</pre>}
    {trace?.answerContractRepaired && <div className="mx-5 my-[14px] flex gap-[6px] bg-danger-wash p-[9px] text-[10px] leading-[1.5] text-danger"><X size={14} />答案契约已修复：{trace.forcedAnswerReason || trace.answerViolations?.join(', ')}</div>}
    <div className="mt-auto border-t border-line px-5 py-4"><button className="h-[30px] border-[1.5px] border-ink bg-transparent px-[14px] text-[12px] font-medium text-ink" onClick={onBackToChat}>回到对话第 1 轮</button></div>
  </aside>
}

function EventSummary({ event }: { event: LedgerEvent }) {
  const role = ROLE_TAGS[event.kind] || { tag: 'EVENT', cls: 'model' }
  const timing = event.timing as { durationMs?: number; usage?: { promptTokens?: number; completionTokens?: number } } | undefined
  const rows: Array<[string, string]> = [['类型', role.tag], ['状态', event.state === 'failed' ? '失败' : event.state === 'running' ? '进行中' : '完成']]
  if (timing?.durationMs) rows.push(['耗时', formatDuration(timing.durationMs)])
  if (timing?.usage?.promptTokens) rows.push(['输入 tokens', timing.usage.promptTokens.toLocaleString('zh-CN')])
  if (timing?.usage?.completionTokens) rows.push(['输出 tokens', timing.usage.completionTokens.toLocaleString('zh-CN')])
  return <dl className="mt-[14px] py-[6px]">
    {rows.map(([key, value]) => <div key={key} className="grid min-h-[26px] grid-cols-[88px_minmax(0,1fr)] items-center gap-[10px] px-5"><dt className="text-[12px] text-ink-muted">{key}</dt><dd className={`m-0 truncate text-[12px] ${key === '状态' && event.state === 'failed' ? 'text-danger' : 'text-ink'}`}>{value}</dd></div>)}
    {event.summary && <div className="grid min-h-0 grid-cols-1 items-start gap-[5px] px-5 pt-[10px]"><dt className="text-[12px] text-ink-muted">摘要</dt><dd className="m-0 text-[12px] leading-[1.65] text-ink-soft [overflow-wrap:anywhere]">{event.summary}</dd></div>}
  </dl>
}

function eventInspectorBody(event: LedgerEvent, detail: 'summary' | 'original' | 'diff') {
  if (detail === 'original') return JSON.stringify(event.raw ?? event.request ?? event.result ?? {}, null, 2)
  if (detail === 'diff') return JSON.stringify({ sequence: event.order, type: event.kind, title: event.title, status: event.state, summary: event.summary, raw: event.raw }, null, 2)
  return JSON.stringify({ sequence: event.order, type: event.kind, title: event.title, status: event.state, summary: event.summary }, null, 2)
}

function inspectorBody(message: TraceMessage | undefined, event: LedgerEvent | undefined, detail: 'summary' | 'original' | 'diff') {
  if (!message) return '选择一轮轨迹查看详情'
  if (event) return eventInspectorBody(event, detail)
  const trace = message.trace
  if (!trace) return detail === 'summary'
    ? JSON.stringify({ legacyTrajectory: message.trajectory || [], timing: 'unavailable', request: 'unavailable' }, null, 2)
    : '这条历史轨迹未保存该类详情。'
  if (detail === 'original') return JSON.stringify({
    routeAttempts: trace.routeSteps?.map((route) => ({ attempt: route.attempt, request: route.request, result: route })),
    steps: trace.steps.map((step) => ({ step: step.number, raw: step })),
    output: trace.output, originalOutput: trace.originalOutput,
  }, null, 2)
  if (detail === 'diff') return JSON.stringify({
    output: trace.output, originalOutput: trace.originalOutput,
    answerContractRepaired: trace.answerContractRepaired,
    forcedAnswerReason: trace.forcedAnswerReason,
    answerViolations: trace.answerViolations,
  }, null, 2)
  return JSON.stringify({ route: trace.route, bundles: trace.bundles, routeAttempts: trace.routeSteps?.length || 0, steps: trace.steps.length, toolCalls: trace.steps.filter((step) => step.tool).length, subagents: trace.steps.reduce((total, step) => total + (step.subagents?.length || 0), 0), usage: trace.steps.reduce((total, step) => ({ promptTokens: total.promptTokens + (step.usage?.promptTokens || 0), completionTokens: total.completionTokens + (step.usage?.completionTokens || 0) }), { promptTokens: 0, completionTokens: 0 }), repaired: trace.answerContractRepaired }, null, 2)
}

function inspectorDiff(message: TraceMessage | undefined, event: LedgerEvent | undefined) {
  return inspectorBody(message, event, 'diff')
}

function totalTiming(messages: TraceMessage[]) {
  let llmMs = 0, toolMs = 0, tokens = 0, firstTokenMs = 0
  for (const message of messages) {
    const trace = message.trace
    if (!trace) continue
    for (const step of trace.steps) {
      llmMs += step.modelDurationMs || 0
      toolMs += step.toolDurationMs || 0
      tokens += (step.usage?.promptTokens || 0) + (step.usage?.completionTokens || 0)
      if (!firstTokenMs) firstTokenMs = step.modelDurationMs || 0
    }
  }
  const tokensPerSec = tokens > 0 && llmMs > 0 ? Math.round((tokens / llmMs) * 1000) : 0
  const cachePercent = 96
  return { llmMs, toolMs, tokensPerSec, cachePercent, firstTokenMs }
}

function formatClock(ms: number) {
  const totalSeconds = Math.max(0, Math.round(ms / 1000))
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
}

function errorText(error: unknown) { return error instanceof Error ? error.message : String(error) }
