import { ChevronDown, ChevronRight } from 'lucide-react'
import { useEffect, useMemo, useRef, useState } from 'react'
import {
  formatDuration,
  type TraceRecord,
  type TraceRecordKind,
  type TraceTurn,
  turnSummary,
} from '../../ledger'
import { KIND_LABELS } from './labels'
import { prefixOffsets, VIRTUALIZE_THRESHOLD, virtualWindow } from './virtual-rows'

type FoldState = { defaultCollapsed: boolean; overrides: Set<string> }

type Props = {
  turns: readonly TraceTurn[]
  visibleRecordIds: ReadonlySet<string> | null
  focusRecordIds: ReadonlySet<string> | null
  selectedRecordId: string
  turnFold: FoldState
  callFold: FoldState
  onSelectRecord: (record: TraceRecord) => void
  onToggleTurn: (turnRecordId: string) => void
  onToggleCall: (ownerRecordId: string) => void
  scrollTargetTurnId: string
}

const KIND_CLASS: Record<TraceRecordKind, string> = {
  user: 'text-ink-strong',
  route: 'text-brand',
  message: 'text-brand',
  tool: 'text-warning',
  subtool: 'text-brand',
  output: 'text-brand',
}

type LedgerRow =
  | { type: 'turn'; key: string; turn: TraceTurn; collapsed: boolean }
  | { type: 'record'; key: string; record: TraceRecord; ownerCollapsed: boolean }

function rowHeight(row: LedgerRow): number {
  if (row.type === 'turn') return 36
  return 30
}

/* 轨迹台账：轮次 → 分组 → 记录三层，双层折叠 + 搜索过滤 + 时间轴联动降透明 + 虚拟滚动。 */
export default function TraceLedger({
  turns, visibleRecordIds, focusRecordIds, selectedRecordId,
  turnFold, callFold, onSelectRecord, onToggleTurn, onToggleCall,
  scrollTargetTurnId,
}: Props) {
  const rows = useMemo<LedgerRow[]>(() => {
    const built: LedgerRow[] = []
    for (const turn of turns) {
      const turnCollapsed = turnFold.overrides.has(turn.turnRecordId)
        ? !turnFold.defaultCollapsed
        : turnFold.defaultCollapsed
      const visibleRecords = visibleRecordIds === null
        ? turn.records
        : turn.records.filter((record) => visibleRecordIds.has(record.recordId))
      built.push({ type: 'turn', key: turn.turnRecordId, turn, collapsed: turnCollapsed })
      if (turnCollapsed || visibleRecords.length === 0) continue
      for (const record of visibleRecords) {
        const ownerCollapsed = visibleRecordIds === null
          && (record.kind === 'tool' || record.kind === 'subtool') && record.ownerRecordId
          ? (callFold.overrides.has(record.ownerRecordId)
            ? !callFold.defaultCollapsed
            : callFold.defaultCollapsed)
          : false
        if (ownerCollapsed) continue
        built.push({ type: 'record', key: record.recordId, record, ownerCollapsed })
      }
    }
    return built
  }, [turns, visibleRecordIds, turnFold, callFold])

  const callOwners = useMemo(() => {
    const owners = new Set<string>()
    for (const turn of turns) {
      for (const record of turn.records) {
        if ((record.kind === 'tool' || record.kind === 'subtool') && record.ownerRecordId) {
          owners.add(record.ownerRecordId)
        }
      }
    }
    return owners
  }, [turns])

  const isCallCollapsed = (ownerRecordId: string) =>
    callFold.overrides.has(ownerRecordId) ? !callFold.defaultCollapsed : callFold.defaultCollapsed

  const scrollRef = useRef<HTMLDivElement>(null)
  const [scrollTop, setScrollTop] = useState(0)
  const [viewportHeight, setViewportHeight] = useState(600)
  const virtualize = rows.length > VIRTUALIZE_THRESHOLD
  const offsets = useMemo(
    () => prefixOffsets(rows.length, (index) => rowHeight(rows[index])),
    [rows],
  )
  const virtualWin = virtualize
    ? virtualWindow(rows.length, offsets, scrollTop, viewportHeight)
    : { start: 0, end: rows.length, padTop: 0, padBottom: 0 }
  const slice = rows.slice(virtualWin.start, virtualWin.end)

  useEffect(() => {
    const node = scrollRef.current
    if (!node || typeof ResizeObserver === 'undefined') return
    const observer = new ResizeObserver(() => setViewportHeight(node.clientHeight))
    observer.observe(node)
    setViewportHeight(node.clientHeight)
    return () => observer.disconnect()
  }, [])

  // 从聊天页锚定到目标轮次：滚到对应轮次头。
  useEffect(() => {
    if (!scrollTargetTurnId) return
    const node = scrollRef.current?.querySelector(`[data-turn-row="${scrollTargetTurnId}"]`)
    node?.scrollIntoView({ block: 'start' })
  }, [scrollTargetTurnId])

  return (
    <div
      ref={scrollRef}
      className="min-h-0 flex-1 overflow-auto"
      onScroll={(event) => setScrollTop(event.currentTarget.scrollTop)}
    >
      <div style={{ paddingTop: virtualWin.padTop, paddingBottom: virtualWin.padBottom }}>
        {slice.map((row) => {
          if (row.type === 'turn') {
            const collapsed = row.collapsed
            return (
              <button
                key={row.key}
                data-turn-row={row.turn.turnRecordId}
                className="sticky top-0 z-[1] flex w-full items-center gap-[10px] border-0 border-b border-line bg-paper-soft px-[30px] py-[7px] text-left"
                onClick={() => onToggleTurn(row.turn.turnRecordId)}
                aria-expanded={!collapsed}
              >
                {collapsed
                  ? <ChevronRight size={13} className="flex-none text-ink-ghost" />
                  : <ChevronDown size={13} className="flex-none text-ink-ghost" />}
                <span className="font-serif text-sm font-semibold text-ink">TURN {row.turn.turn}</span>
                <span className="truncate text-xs text-ink-muted">{turnSummary(row.turn)}</span>
                {row.turn.header.durationMs > 0 && (
                  <span className="ml-auto flex-none font-mono text-2xs text-ink-ghost">{formatDuration(row.turn.header.durationMs)}</span>
                )}
                {row.turn.header.isError && <span className="flex-none font-mono text-2xs text-danger">失败</span>}
              </button>
            )
          }
          const record = row.record
          const dimmed = focusRecordIds !== null && !focusRecordIds.has(record.recordId)
          return (
            <div
              key={row.key}
              data-record-row={record.recordId}
              className={`flex items-center gap-[6px] border-b border-line-soft px-[30px] py-[5px] ${record.recordId === selectedRecordId ? 'bg-brand-wash' : ''}`}
              style={dimmed ? { opacity: 0.35 } : undefined}
            >
              <button
                className="grid min-w-0 flex-1 grid-cols-[46px_54px_minmax(0,1fr)_auto] items-center gap-[10px] border-0 bg-transparent p-0 text-left hover:bg-paper-soft"
                onClick={() => onSelectRecord(record)}
                aria-pressed={record.recordId === selectedRecordId}
                title={record.text}
              >
                <span className="text-right font-mono text-2xs text-ink-ghost">#{record.index}</span>
                <span className={`text-left font-mono text-2xs font-medium tracking-[.1em] ${KIND_CLASS[record.kind]}`}>{KIND_LABELS[record.kind]}</span>
                <span className="flex min-w-0 items-baseline gap-[7px] overflow-hidden">
                  <span className="max-w-[38%] flex-none truncate font-mono text-xs text-ink">{record.title}</span>
                  <span className={`min-w-0 flex-1 truncate font-mono text-xs ${record.isError ? 'text-danger' : 'text-ink-soft'}`}>{record.text}</span>
                </span>
                <span className="flex flex-none items-center gap-[8px] font-mono text-2xs text-ink-ghost">
                  {record.tokens && <span>{record.tokens.input.toLocaleString('zh-CN')}→{record.tokens.output.toLocaleString('zh-CN')}</span>}
                  {record.timeMs ? <span>{formatDuration(record.timeMs)}</span> : null}
                  {record.detail.protocolRepaired && <span className="text-warning" title={record.detail.protocolError}>已修复</span>}
                </span>
              </button>
              {record.kind === 'message' && callOwners.has(record.recordId) && (
                <button
                  aria-label={isCallCollapsed(record.recordId) ? `展开 ${record.title} 的调用` : `折叠 ${record.title} 的调用`}
                  aria-expanded={!isCallCollapsed(record.recordId)}
                  className="grid h-[22px] w-[22px] flex-none place-items-center border-0 bg-transparent p-0 text-ink-ghost hover:text-ink"
                  onClick={() => onToggleCall(record.recordId)}
                >{isCallCollapsed(record.recordId)
                  ? <ChevronRight size={13} />
                  : <ChevronDown size={13} />}</button>
              )}
            </div>
          )
        })}
        {rows.length === 0 && (
          <div className="py-[50px] text-center text-xs text-ink-muted">没有匹配的轨迹记录</div>
        )}
      </div>
    </div>
  )
}
