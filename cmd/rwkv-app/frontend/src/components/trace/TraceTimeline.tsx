import { useMemo, useRef, useState } from 'react'
import { formatDuration, formatStartedAt, recordLane, type TraceRecord } from '../../ledger'
import type { TraceTimelineMode } from './TraceToolbar'

type TimeRange = { start: number; end: number }

type Props = {
  records: readonly TraceRecord[]
  mode: TraceTimelineMode
  searchMatches: ReadonlySet<string> | null
  focusRecordIds: ReadonlySet<string> | null
  selectedRecordId: string
  onSelectRecord: (record: TraceRecord) => void
  onRangeChange: (range: TimeRange | null) => void
}

type Span = { record: TraceRecord; start: number; end: number; lane: 0 | 1 | 2 }

const WALL_MODES: TraceTimelineMode[] = ['actual']

const LANE_LABELS = ['输入', '模型', '工具'] as const
const LANE_COUNT = 3

export function computeTraceSpans(records: readonly TraceRecord[], mode: TraceTimelineMode): { spans: Span[]; domain: number; origin: number } {
  if (WALL_MODES.includes(mode)) {
    const timed = records.filter((record) => typeof record.startedAtMs === 'number')
    const first = timed.length > 0 ? timed[0].startedAtMs ?? null : null
    return buildWallSpans(timed, mode, first)
  }
  if (mode === 'duration') {
    let cursor = 0
    const spans = records.map((record) => {
      const duration = record.timeMs ?? 0
      const span = { record, start: cursor, end: cursor + duration, lane: recordLane(record.kind) }
      cursor += duration
      return span
    })
    return { spans, domain: Math.max(1, cursor), origin: 0 }
  }
  return {
    spans: records.map((record, index) => ({ record, start: index, end: index + 1, lane: recordLane(record.kind) })),
    domain: Math.max(1, records.length),
    origin: 0,
  }
}

function buildWallSpans(
  timed: readonly TraceRecord[],
  mode: TraceTimelineMode,
  originValue: number | null,
): { spans: Span[]; domain: number; origin: number } {
  const origin = originValue ?? 0
  const spans = timed.map((record) => {
    const start = (record.startedAtMs ?? 0) - origin
    const end = start + (record.timeMs ?? 0)
    return { record, start, end, lane: recordLane(record.kind) }
  })
  const maxEnd = spans.reduce((best, span) => Math.max(best, span.end), 1)
  return { spans, domain: Math.max(1, maxEnd), origin }
}

/* 轨迹时间轴：时序（等宽）与时长（累积瀑布）两种投影，支持拖选区间联动台账、点选记录。 */
export default function TraceTimeline({
  records, mode, searchMatches, focusRecordIds, selectedRecordId, onSelectRecord, onRangeChange,
}: Props) {
  const { spans, domain, origin } = useMemo(() => computeTraceSpans(records, mode), [records, mode])
  const trackRef = useRef<HTMLDivElement>(null)
  const [draft, setDraft] = useState<{ anchor: number; moving: number } | null>(null)
  const totalMs = useMemo(() => records.reduce((sum, record) => sum + (record.timeMs ?? 0), 0), [records])

  const boundaries = useMemo(() => {
    const marks: number[] = []
    let lastTurnId = ''
    for (const span of spans) {
      if (span.record.turnRecordId !== lastTurnId) {
        if (lastTurnId !== '') marks.push(span.start)
        lastTurnId = span.record.turnRecordId
      }
    }
    return marks
  }, [spans])

  function fractionOf(event: React.PointerEvent | React.MouseEvent): number {
    const rect = trackRef.current?.getBoundingClientRect()
    if (!rect || rect.width === 0) return 0
    return Math.min(1, Math.max(0, (event.clientX - rect.left) / rect.width))
  }

  function laneAt(event: React.PointerEvent | React.MouseEvent): 0 | 1 | 2 {
    const rect = trackRef.current?.getBoundingClientRect()
    if (!rect || rect.height === 0) return 1
    return Math.min(LANE_COUNT - 1, Math.max(0, Math.floor(((event.clientY - rect.top) / rect.height) * LANE_COUNT))) as 0 | 1 | 2
  }

  function spanAt(fraction: number, lane: 0 | 1 | 2): Span | undefined {
    const position = fraction * domain
    return spans.find((span) => span.lane === lane && span.start <= position && span.end >= position)
      ?? [...spans].reverse().find((span) => span.lane === lane && span.start <= position)
  }

  function onPointerDown(event: React.PointerEvent) {
    if (event.button !== 0) return
    event.currentTarget.setPointerCapture(event.pointerId)
    const fraction = fractionOf(event)
    setDraft({ anchor: fraction, moving: fraction })
  }
  function onPointerMove(event: React.PointerEvent) {
    if (!draft) return
    setDraft({ ...draft, moving: fractionOf(event) })
  }
  function onPointerUp(event: React.PointerEvent) {
    if (!draft) return
    const moved = Math.abs(draft.moving - draft.anchor) * (trackRef.current?.clientWidth || 0) > 3
    const range = { low: Math.min(draft.anchor, draft.moving), high: Math.max(draft.anchor, draft.moving) }
    setDraft(null)
    if (moved) {
      onRangeChange({ start: range.low * domain, end: range.high * domain })
      return
    }
    const lane = laneAt(event)
    const span = spanAt(fractionOf(event), lane)
    if (span) onSelectRecord(span.record)
  }

  const draftRange = draft
    ? { left: Math.min(draft.anchor, draft.moving), width: Math.abs(draft.moving - draft.anchor) }
    : null

  return (
    <section aria-label="轨迹时间轴" className="flex-none border-b border-line bg-paper-soft px-[30px] py-[8px]">
      <div className="grid grid-cols-[38px_minmax(0,1fr)] items-end gap-[12px]">
        <div className="flex flex-col justify-end gap-[2px] pb-[16px] text-right font-mono text-2xs uppercase tracking-[.1em] text-ink-muted">
          {LANE_LABELS.map((label) => <span key={label}>{label}</span>)}
        </div>
        <div>
          <div
            ref={trackRef}
            role="slider"
            aria-label="时间轴总览；拖选区间聚焦台账记录，双击清除"
            aria-valuetext={mode === 'sequence'
              ? `${records.length} 条记录`
              : mode === 'duration' ? formatDuration(totalMs) : formatStartedAt(origin + domain)}
            tabIndex={0}
            className="relative h-[58px] cursor-crosshair select-none"
            onPointerDown={onPointerDown}
            onPointerMove={onPointerMove}
            onPointerUp={onPointerUp}
            onDoubleClick={(event) => { event.preventDefault(); onRangeChange(null) }}
          >
            {boundaries.map((mark) => (
              <span
                key={mark}
                aria-hidden="true"
                className="absolute bottom-0 top-0 w-px bg-line-strong"
                style={{ left: `${(mark / domain) * 100}%` }}
              />
            ))}
            {spans.map((span) => {
              const widthPercent = Math.max(((span.end - span.start) / domain) * 100, 0.4)
              const searched = searchMatches === null ? undefined : searchMatches.has(span.record.recordId)
              const dimmed = focusRecordIds !== null && !focusRecordIds.has(span.record.recordId)
              return (
                <span
                  key={span.record.recordId}
                  aria-hidden="true"
                  title={`#${span.record.index} ${span.record.title} · ${span.record.timeMs ? formatDuration(span.record.timeMs) : '—'}${span.record.startedAtMs ? ` · 开始 ${formatStartedAt(span.record.startedAtMs)}` : ''}`}
                  className="absolute rounded-[1px]"
                  data-kind={span.record.kind}
                  data-search-match={searched}
                  data-selected={span.record.recordId === selectedRecordId || undefined}
                  data-dim={dimmed || undefined}
                  style={{
                    left: `${(span.start / domain) * 100}%`,
                    width: `calc(${widthPercent}% - 1px)`,
                    top: `calc(${(span.lane / LANE_COUNT) * 100}% + 2px)`,
                    height: `calc(${100 / LANE_COUNT}% - 4px)`,
                    background: span.record.isError ? 'var(--danger)' : spanKindColor(span.record.kind),
                    opacity: span.record.isError ? 0.95 : 0.72,
                  }}
                />
              )
            })}
            {draftRange && draftRange.width > 0.001 && (
              <span
                aria-hidden="true"
                className="absolute bottom-0 top-0 border-x border-brand bg-brand/15"
                style={{ left: `${draftRange.left * 100}%`, width: `${draftRange.width * 100}%` }}
              />
            )}
          </div>
          <div className="mt-[3px] flex justify-between font-mono text-2xs text-ink-ghost">
            <span>{mode === 'sequence' ? '00' : mode === 'duration' ? '00:00' : formatStartedAt(origin)}</span>
            <span>{mode === 'sequence' ? `${records.length} 条` : mode === 'duration' ? formatDuration(totalMs) : formatStartedAt(origin + domain)}</span>
          </div>
        </div>
      </div>
    </section>
  )
}

function spanKindColor(kind: TraceRecord['kind']) {
  if (kind === 'tool' || kind === 'subtool') return 'var(--warning)'
  if (kind === 'user') return 'var(--accent-warm)'
  return 'var(--brand)'
}
