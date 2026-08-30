import { useEffect, useMemo, useState } from 'react'
import * as Backend from '../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import {
  buildTraceTurns, flattenTraceRecords, formatDuration,
  type LedgerMessage, type TraceRecord, type TraceTurn,
} from '../ledger'
import { useSnackbar } from '../snackbar'
import RecordDetails from './trace/RecordDetails'
import TraceLedger from './trace/TraceLedger'
import TraceToolbar, { type TraceTimelineMode } from './trace/TraceToolbar'
import TraceTimeline, { computeTraceSpans } from './trace/TraceTimeline'
import { buildSearchIndex, debounce, searchRecordIds } from './trace/trace-search'

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

type FoldState = { defaultCollapsed: boolean; overrides: Set<string> }
type TimeRange = { start: number; end: number }

const SEARCH_DEBOUNCE_MS = 250

/* 轨迹视图：工具栏 + 时间轴 + 台账 + 详情面板 + 统计底栏。 */
export default function TraceView({ messages, selected, onSelect, onBackToChat }: Props) {
  const turns = useMemo<TraceTurn[]>(() => buildTraceTurns(messages), [messages])
  const records = useMemo(() => flattenTraceRecords(turns), [turns])
  const searchIndex = useMemo(() => buildSearchIndex(turns), [turns])

  const [mode, setMode] = useState<TraceTimelineMode>('sequence')
  const hasWallClock = records.length > 0 && records.every((record) => typeof record.startedAtMs === 'number' && record.startedAtMs > 0)
  // 切到无时间戳的旧轨迹时，墙钟不可用则回退为时长。
  const effectiveMode: TraceTimelineMode = mode === 'actual' && !hasWallClock ? 'duration' : mode
  const [searchQuery, setSearchQuery] = useState('')
  const [appliedQuery, setAppliedQuery] = useState('')
  const [turnFold, setTurnFold] = useState<FoldState>({ defaultCollapsed: false, overrides: new Set() })
  const [callFold, setCallFold] = useState<FoldState>({ defaultCollapsed: true, overrides: new Set() })
  const [timelineRange, setTimelineRange] = useState<TimeRange | null>(null)
  const [selectedRecordId, setSelectedRecordId] = useState('')
  const [inspectorOpen, setInspectorOpen] = useState(true)
  const [detailsWidth, setDetailsWidth] = useState(380)
  const { show } = useSnackbar()

  useEffect(() => {
    const apply = debounce((query: string) => setAppliedQuery(query), SEARCH_DEBOUNCE_MS)
    apply(searchQuery)
  }, [searchQuery])

  const searchMatches = useMemo(() => searchRecordIds(searchIndex, appliedQuery), [searchIndex, appliedQuery])
  const focusRecordIds = useMemo(() => {
    if (timelineRange === null) return null
    const { spans } = computeTraceSpans(records, effectiveMode)
    const ids = new Set<string>()
    for (const span of spans) {
      if (span.start <= timelineRange.end && span.end >= timelineRange.start) ids.add(span.record.recordId)
    }
    return ids
  }, [timelineRange, records, effectiveMode])

  const selectedRecord = records.find((record) => record.recordId === selectedRecordId) ?? null
  const selectedTurn = turns.find((turn) => turn.turnRecordId === `turn:${selected?.id}`) ?? null

  const ownerIds = useMemo(
    () => [...new Set(records.map((record) => record.ownerRecordId).filter((id): id is string => Boolean(id)))],
    [records],
  )
  const isTurnCollapsed = (turn: TraceTurn) =>
    turnFold.overrides.has(turn.turnRecordId) ? !turnFold.defaultCollapsed : turnFold.defaultCollapsed
  const isOwnerExpanded = (ownerId: string) =>
    callFold.overrides.has(ownerId) ? !callFold.defaultCollapsed : !callFold.defaultCollapsed
  const allTurnsCollapsed = turns.length > 0 && turns.filter((turn) => turn.records.length > 0).every(isTurnCollapsed)
  const allCallsExpanded = ownerIds.length > 0 && ownerIds.every(isOwnerExpanded)

  function toggleTurn(turnRecordId: string) {
    setTurnFold((current) => {
      const overrides = new Set(current.overrides)
      if (overrides.has(turnRecordId)) overrides.delete(turnRecordId)
      else overrides.add(turnRecordId)
      return { ...current, overrides }
    })
  }
  function toggleCall(ownerRecordId: string) {
    setCallFold((current) => {
      const overrides = new Set(current.overrides)
      if (overrides.has(ownerRecordId)) overrides.delete(ownerRecordId)
      else overrides.add(ownerRecordId)
      return { ...current, overrides }
    })
  }
  function toggleAllTurns() {
    setTurnFold(allTurnsCollapsed
      ? { defaultCollapsed: false, overrides: new Set() }
      : { defaultCollapsed: true, overrides: new Set() })
  }
  function toggleAllCalls() {
    setCallFold(allCallsExpanded
      ? { defaultCollapsed: true, overrides: new Set() }
      : { defaultCollapsed: false, overrides: new Set() })
  }

  function selectRecord(record: TraceRecord) {
    setSelectedRecordId(record.recordId)
    if (selected?.id !== record.turnRecordId.slice(5)) onSelect(record.turnRecordId.slice(5))
  }

  async function exportTrace() {
    const data = messages.map((message) => JSON.stringify({
      id: message.id, role: message.role, prompt: message.prompt, createdAt: message.createdAt,
      trace: message.trace || { legacyTrajectory: message.trajectory },
    })).join('\n')
    try {
      const path = await Backend.ExportTrajectory(data)
      if (path) show(`轨迹已导出：${path.split('/').at(-1)}`, 'success')
    } catch (error) {
      show(error instanceof Error ? error.message : String(error), 'error')
    }
  }

  const totalLlmMs = records.reduce((sum, record) => sum + (record.kind === 'message' || record.kind === 'route' ? record.timeMs ?? 0 : 0), 0)
  const totalToolMs = records.reduce((sum, record) => sum + (record.kind === 'tool' || record.kind === 'subtool' ? record.timeMs ?? 0 : 0), 0)
  const totalTokens = records.reduce((sum, record) => sum + (record.tokens ? record.tokens.input + record.tokens.output : 0), 0)

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <TraceToolbar
        mode={mode}
        onModeChange={(next) => { setMode(next); setTimelineRange(null) }}
        hasWallClock={hasWallClock}
        allTurnsCollapsed={allTurnsCollapsed}
        onToggleAllTurns={toggleAllTurns}
        allCallsExpanded={allCallsExpanded}
        onToggleAllCalls={toggleAllCalls}
        searchQuery={searchQuery}
        onSearchQueryChange={setSearchQuery}
        matchCount={searchMatches === null ? null : searchMatches.size}
        inspectorOpen={inspectorOpen}
        onToggleInspector={() => setInspectorOpen((open) => !open)}
      />
      <TraceTimeline
        records={records}
        mode={effectiveMode}
        searchMatches={searchMatches}
        focusRecordIds={focusRecordIds}
        selectedRecordId={selectedRecordId}
        onSelectRecord={selectRecord}
        onRangeChange={setTimelineRange}
      />
      <div className="flex min-h-0 flex-1">
        <TraceLedger
          turns={turns}
          visibleRecordIds={searchMatches}
          focusRecordIds={focusRecordIds}
          selectedRecordId={selectedRecordId}
          turnFold={turnFold}
          callFold={callFold}
          onSelectRecord={selectRecord}
          onToggleTurn={toggleTurn}
          onToggleCall={toggleCall}
          scrollTargetTurnId={selected ? `turn:${selected.id}` : ''}
        />
        {inspectorOpen && (
          <RecordDetails
            record={selectedRecord}
            turn={selectedTurn}
            width={detailsWidth}
            onWidthChange={setDetailsWidth}
            onClose={() => setInspectorOpen(false)}
          />
        )}
      </div>
      <div className="flex flex-none items-center gap-[16px] border-t-[1.5px] border-ink px-[30px] py-[10px] font-mono text-xs text-ink-soft">
        <div className="flex min-w-0 flex-1 items-center gap-[16px] overflow-hidden whitespace-nowrap">
          <span>{turns.length} 轮 · {records.length} 条</span>
          <span className="text-ink-ghost">/</span>
          <span>模型 {formatDuration(totalLlmMs || undefined)} · 工具 {formatDuration(totalToolMs || undefined)}</span>
          {totalTokens > 0 && (
            <>
              <span className="text-ink-ghost">/</span>
              <span>{totalTokens.toLocaleString('zh-CN')} tok</span>
            </>
          )}
        </div>
        <button className="flex-none border-0 bg-transparent p-0 text-sm text-brand hover:underline" onClick={onBackToChat}>返回对话</button>
        <button className="flex-none border-0 bg-transparent p-0 text-sm text-brand hover:underline" onClick={() => void exportTrace()}>导出 trace.jsonl</button>
      </div>
    </div>
  )
}
