import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { FoldVertical, PanelRight, Search, UnfoldVertical } from 'lucide-react'

export type TraceTimelineMode = 'sequence' | 'duration' | 'actual'

type Props = {
  mode: TraceTimelineMode
  onModeChange: (mode: TraceTimelineMode) => void
  /** 轨迹带墙钟开始时间时才提供墙钟投影。 */
  hasWallClock: boolean
  allTurnsCollapsed: boolean
  onToggleAllTurns: () => void
  allCallsExpanded: boolean
  onToggleAllCalls: () => void
  searchQuery: string
  onSearchQueryChange: (query: string) => void
  matchCount: number | null
  inspectorOpen: boolean
  onToggleInspector: () => void
}

// 稳定引用：避免 effect 依赖每次渲染重建的数组。
const MODES_SHORT: TraceTimelineMode[] = ['sequence', 'duration']
const MODES_ALL: TraceTimelineMode[] = ['sequence', 'duration', 'actual']

/* 轨迹工具栏：时间轴投影（滑动指示条）、双层折叠全开全关、搜索。 */
export default function TraceToolbar({
  mode, onModeChange, hasWallClock, allTurnsCollapsed, onToggleAllTurns,
  allCallsExpanded, onToggleAllCalls, searchQuery, onSearchQueryChange,
  matchCount, inspectorOpen, onToggleInspector,
}: Props) {
  const groupRef = useRef<HTMLDivElement>(null)
  const [thumb, setThumb] = useState({ left: 0, width: 0, ready: false })

  const modes = hasWallClock ? MODES_ALL : MODES_SHORT

  // 滑动指示条：测量当前激活分段的位置与宽度，切换时用 transform 过渡。
  useLayoutEffect(() => {
    const group = groupRef.current
    if (!group) return
    const index = modes.indexOf(mode)
    const buttons = group.querySelectorAll('button[data-mode]')
    const active = buttons[index] as HTMLElement | undefined
    if (active) setThumb({ left: active.offsetLeft, width: active.offsetWidth, ready: true })
  }, [mode, hasWallClock, modes])

  useEffect(() => {
    const group = groupRef.current
    if (!group || typeof ResizeObserver === 'undefined') return
    const observer = new ResizeObserver(() => {
      const index = modes.indexOf(mode)
      const active = group.querySelectorAll('button[data-mode]')[index] as HTMLElement | undefined
      if (active) setThumb((current) => ({ ...current, left: active.offsetLeft, width: active.offsetWidth }))
    })
    observer.observe(group)
    return () => observer.disconnect()
  }, [mode, modes])

  return (
    <div className="flex min-h-[48px] flex-none items-center gap-[14px] border-b border-line px-[30px]" role="toolbar" aria-label="轨迹工具栏">
      <div ref={groupRef} className="relative flex border border-line bg-paper-soft p-[2px]">
        {thumb.ready && (
          <span
            aria-hidden
            className="absolute bottom-[2px] top-[2px] bg-paper shadow-sm transition-[transform,width] duration-[180ms] ease-[cubic-bezier(.2,0,0,1)] motion-reduce:transition-none"
            style={{ transform: `translateX(${thumb.left}px)`, width: thumb.width }}
          />
        )}
        {modes.map((value) => (
          <button
            key={value}
            data-mode={value}
            aria-pressed={mode === value}
            className={`relative z-[1] flex h-[26px] items-center border-0 px-[9px] text-xs transition-colors duration-[160ms] ease-[cubic-bezier(.2,0,0,1)] motion-reduce:transition-none ${mode === value ? 'bg-transparent font-medium text-brand' : 'bg-transparent text-ink-muted hover:text-ink'}`}
            onClick={() => onModeChange(value)}
            title={value === 'sequence' ? '每个操作等宽排列' : value === 'duration' ? '按记录耗时绘制（压缩空闲）' : '真实耗时按真实时刻摆放（完整甘特图）'}
          >{value === 'sequence' ? '时序' : value === 'duration' ? '时长' : '墙钟'}</button>
        ))}
      </div>
      <span className="h-[16px] w-px flex-none bg-line" />
      <button
        aria-pressed={allTurnsCollapsed}
        className="flex h-[26px] items-center gap-[5px] border-0 bg-transparent px-[4px] text-xs text-ink-soft hover:text-brand"
        onClick={onToggleAllTurns}
        title={allTurnsCollapsed ? '展开所有轮次' : '折叠所有轮次'}
      >
        {allTurnsCollapsed ? <UnfoldVertical size={13} /> : <FoldVertical size={13} />}
        轮次
      </button>
      <button
        aria-pressed={allCallsExpanded}
        className="flex h-[26px] items-center gap-[5px] border-0 bg-transparent px-[4px] text-xs text-ink-soft hover:text-brand"
        onClick={onToggleAllCalls}
        title={allCallsExpanded ? '折叠所有调用' : '展开所有调用'}
      >
        {allCallsExpanded ? <FoldVertical size={13} /> : <UnfoldVertical size={13} />}
        调用
      </button>
      {matchCount !== null && (
        <span className="text-xs text-brand">{matchCount} 条命中</span>
      )}
      <label className="ml-auto flex h-[28px] w-[235px] items-center gap-[7px] border border-line bg-paper-wash px-[9px] text-ink-muted">
        <Search size={14} />
        <input
          type="search"
          aria-label="搜索轨迹"
          className="w-full border-0 bg-transparent text-xs text-ink outline-0"
          value={searchQuery}
          onChange={(event) => onSearchQueryChange(event.target.value)}
          placeholder="搜索请求、工具或结果"
        />
      </label>
      <button
        aria-label="检查器"
        aria-pressed={inspectorOpen}
        className={`grid h-[28px] w-[28px] place-items-center rounded-[3px] border bg-transparent ${inspectorOpen ? 'border-line-strong text-brand' : 'border-transparent text-ink-soft hover:border-line hover:text-brand'}`}
        onClick={onToggleInspector}
      ><PanelRight size={15} /></button>
    </div>
  )
}
