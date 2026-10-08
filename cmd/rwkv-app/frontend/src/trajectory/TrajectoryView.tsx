/*
 * Trajectory view host for RWKV-Agent: toolbar, overview timeline and ledger
 * from deepseek-harness ui-trajectory (MIT, see ./LICENSE.deepseek-harness),
 * fed by rwkv-adapter instead of DSH's session projection. Fold, timeline
 * range, search and selection state follow DSH's TrajectoryView one-for-one.
 */
import { useCallback, useEffect, useMemo, useState } from 'react'
import { Download } from 'lucide-react'
import { TrajectoryTable } from './TrajectoryTable.tsx'
import { TrajectoryToolbar } from './TrajectoryToolbar.tsx'
import { TrajectoryTimeline } from './TrajectoryTimeline.tsx'
import { trajectoryTimelineFocusIndexes, type TrajectoryTimelineMode, type TrajectoryTimeRange } from './timeline.ts'
import { trajectoryRecordId } from './trajectory-record.ts'
import { TrajectorySearchIndex } from './trajectory-search-index.ts'
import { createTrajectoryTranslate } from './locales.ts'
import { buildTrajectoryModel, type AdapterMessage, type LiveTurn } from './rwkv-adapter.ts'
import css from './views.module.css'
import './tokens.css'

const EMPTY_TURN_IDS: ReadonlySet<number> = new Set()
const EMPTY_RECORD_IDS: ReadonlySet<string> = new Set()
const SEARCH_DEBOUNCE_MS = 200
const DURATION_STORAGE_KEY = 'rwkv.trajectory.actualDuration'

export type TrajectoryViewProps = {
  messages: readonly AdapterMessage[]
  /** The turn still running, rebuilt from live agent events; null when idle. */
  live: LiveTurn | null
  /** Conversation message to bring into view when the tab opens (from the chat's 查看轨迹). */
  focusMessageId?: string
  /** Export the conversation's traces (trace.jsonl). */
  onExport?: () => void
}

const t = createTrajectoryTranslate('zh')

export default function TrajectoryView({ messages, live, focusMessageId, onExport }: TrajectoryViewProps) {
  const model = useMemo(() => buildTrajectoryModel(messages, live, t), [messages, live])
  const turns = model.turns

  const [collapsedTurns, setCollapsedTurns] = useState<ReadonlySet<number>>(EMPTY_TURN_IDS)
  const [collapsedAssistants, setCollapsedAssistants] = useState<ReadonlySet<string>>(EMPTY_RECORD_IDS)
  const [timelineSelection, setTimelineSelection] = useState<TrajectoryTimeRange | null>(null)
  const [actualDuration, setActualDurationState] = useState(() => readStoredDuration())
  const [actualTime, setActualTime] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [appliedQuery, setAppliedQuery] = useState('')
  const [searchIndex] = useState(() => new TrajectorySearchIndex())
  const [selectedTimelineIndex, setSelectedTimelineIndex] = useState<number | null>(null)
  const [timelineRecordSelection, setTimelineRecordSelection] = useState<{ readonly index: number } | null>(null)
  const [timelineRecordFocus, setTimelineRecordFocus] = useState<{ readonly index: number } | null>(null)

  const setActualDuration = (value: boolean) => {
    setActualDurationState(value)
    try { localStorage.setItem(DURATION_STORAGE_KEY, value ? '1' : '0') } catch { /* private mode */ }
  }

  useEffect(() => {
    const timer = setTimeout(() => setAppliedQuery(searchQuery), SEARCH_DEBOUNCE_MS)
    return () => clearTimeout(timer)
  }, [searchQuery])

  // Opening from a chat turn's 查看轨迹 focuses that turn's first record.
  useEffect(() => {
    if (!focusMessageId) return
    const turn = [...model.messageIds].find(([, id]) => id === focusMessageId)?.[0]
    const first = turns.find(candidate => candidate.turn === turn)?.groups[0]?.cells[0]
    if (first !== undefined) setTimelineRecordFocus({ index: first.index })
    // Only on a new focus request, not on every live update.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [focusMessageId])

  const timelineMode: TrajectoryTimelineMode = actualDuration
    ? actualTime ? 'actual' : 'duration'
    : actualTime ? 'time' : 'sequence'

  // The index is incremental: update() reports whether anything changed, which keys the search memo.
  const searchRevision = useMemo(() => searchIndex.update([turns]), [searchIndex, turns])
  const searchMatchRecordIds = useMemo(
    () => searchIndex.search(appliedQuery),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [searchIndex, searchRevision, turns, appliedQuery],
  )
  const searchMatchIndexes = useMemo(() => {
    if (searchMatchRecordIds === null) return null
    const indexes = new Set<number>()
    for (const turn of turns) {
      for (const group of turn.groups) {
        for (const cell of group.cells) {
          if (searchMatchRecordIds.has(trajectoryRecordId(cell))) indexes.add(cell.index)
        }
      }
    }
    return indexes
  }, [turns, searchMatchRecordIds])

  const timelineFocusIndexes = useMemo(
    () => timelineSelection === null ? null : trajectoryTimelineFocusIndexes(turns, timelineSelection, timelineMode),
    [timelineMode, timelineSelection, turns],
  )
  const handleRecordSelect = useCallback((index: number) => {
    if (timelineFocusIndexes !== null && !timelineFocusIndexes.has(index)) setTimelineSelection(null)
  }, [timelineFocusIndexes])
  const handleTimelineRecordSelect = useCallback((index: number) => {
    setTimelineSelection(null)
    setTimelineRecordSelection({ index })
    setSelectedTimelineIndex(index)
  }, [])
  const handleTimelineRecordFocus = useCallback((index: number) => {
    setTimelineRecordFocus({ index })
  }, [])

  const collapsibleTurnIds = useMemo(
    () => turns
      .filter(turn => turn.turn !== null && turn.groups.reduce(
        (count, group) => count + group.cells.filter(cell => cell.requestOnly !== true && cell.kind !== 'system').length, 0,
      ) > 1)
      .flatMap(turn => turn.turn === null ? [] : [turn.turn]),
    [turns],
  )
  const allTurnsCollapsed = collapsibleTurnIds.length > 0 && collapsibleTurnIds.every(turn => collapsedTurns.has(turn))
  const collapsibleAssistantIds = useMemo(() => {
    const ids: string[] = []
    for (const turn of turns) {
      const cells = turn.groups.flatMap(group => group.cells)
      for (let i = 0; i < cells.length; i++) {
        const cell = cells[i]
        if (cell?.kind !== 'message') continue
        const next = cells[i + 1]
        if (next?.kind === 'tool' || next?.kind === 'subtool') ids.push(trajectoryRecordId(cell))
      }
    }
    return ids
  }, [turns])
  const allAssistantsCollapsed = collapsibleAssistantIds.length > 0 && collapsibleAssistantIds.every(id => collapsedAssistants.has(id))

  return (
    <div className={`${css.root} trajectory-root`}>
      <TrajectoryToolbar
        actualDuration={actualDuration}
        onActualDurationChange={(next) => { setActualDuration(next); setTimelineSelection(null) }}
        actualTime={actualTime}
        onActualTimeChange={(next) => { setActualTime(next); setTimelineSelection(null) }}
        allTurnsCollapsed={allTurnsCollapsed}
        onToggleAllTurns={() => setCollapsedTurns(current => setAll(current, collapsibleTurnIds, !allTurnsCollapsed))}
        allAssistantsCollapsed={allAssistantsCollapsed}
        onToggleAllAssistants={() => setCollapsedAssistants(current => setAll(current, collapsibleAssistantIds, !allAssistantsCollapsed))}
        searchQuery={searchQuery}
        onSearchQueryChange={setSearchQuery}
        extra={onExport && (
          <button type="button" className="trajectory-toolbar-extra" title="导出 trace.jsonl" onClick={onExport}>
            <Download size={12} strokeWidth={1.5} aria-hidden="true" />导出
          </button>
        )}
        t={t}
      />
      <TrajectoryTimeline
        t={t}
        turns={turns}
        mode={timelineMode}
        range={timelineSelection}
        selectedIndex={selectedTimelineIndex}
        searchMatchIndexes={searchMatchIndexes}
        onRangeChange={setTimelineSelection}
        onRecordSelect={handleTimelineRecordSelect}
        onRecordFocus={handleTimelineRecordFocus}
      />
      <div className={css.ledger}>
        <TrajectoryTable
          t={t}
          renderImages={() => null}
          requestNumbers={model.requests}
          turns={turns}
          timelineFocusIndexes={timelineFocusIndexes}
          searchMatchIndexes={searchMatchIndexes}
          onSelectedIndexChange={setSelectedTimelineIndex}
          onRecordSelect={handleRecordSelect}
          recordSelection={timelineRecordSelection}
          recordFocus={timelineRecordFocus}
          onClearSelection={() => { setTimelineSelection(null) }}
          collapsedTurns={collapsedTurns}
          onToggleTurn={(turn) => setCollapsedTurns(current => toggleIn(current, turn))}
          collapsedAssistants={collapsedAssistants}
          onToggleAssistant={(id) => setCollapsedAssistants(current => toggleIn(current, id))}
        />
      </div>
    </div>
  )
}

function toggleIn<T>(current: ReadonlySet<T>, value: T): ReadonlySet<T> {
  const next = new Set(current)
  if (next.has(value)) next.delete(value)
  else next.add(value)
  return next
}

function setAll<T>(current: ReadonlySet<T>, values: readonly T[], on: boolean): ReadonlySet<T> {
  const next = new Set(current)
  for (const value of values) {
    if (on) next.add(value)
    else next.delete(value)
  }
  return next
}

function readStoredDuration(): boolean {
  try { return localStorage.getItem(DURATION_STORAGE_KEY) === '1' } catch { return false }
}
