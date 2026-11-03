import { useEffect, useRef, useState, type ForwardRefExoticComponent, type HTMLAttributes, type RefAttributes } from 'react'
import { CloudSunIcon } from './icons/animated/cloud-sun'
import { FileFetchIcon } from './icons/animated/file-fetch'
import { EarthIcon } from './icons/animated/earth'
import { FilePenLineIcon } from './icons/animated/file-pen-line'
import { FileTextIcon } from './icons/animated/file-text'
import { FolderTreeIcon } from './icons/animated/folder-tree'
import { SearchIcon } from './icons/animated/search'
import { TerminalIcon } from './icons/animated/terminal'
import { UsersIcon } from './icons/animated/users'
import { CalculatorIcon, ClockIcon, DatabaseIcon, PackageOpenIcon } from './icons/animated/compute'
import { WrenchIcon } from './icons/animated/wrench'

type IconHandle = { startAnimation: () => void; stopAnimation: () => void }
type AnimatedIcon = ForwardRefExoticComponent<HTMLAttributes<HTMLDivElement> & { size?: number } & RefAttributes<IconHandle>>

// lucide-animated 的动画都只播一遍（约 0.5–1 秒）；运行中按这个间隔重播，读起来是「还在干活」而不是一直抖。
// 1.2 秒实测太赶；「还在跑」主要由标题文字和右侧实时计时表达，图标留出呼吸的停顿。
const REPLAY_MS = 2000

// 每个图标放完一遍要多久（取各段 delay + duration 的最大值）。搜索、抓网页常常几百毫秒就跑完，
// 不等这一遍放完就停，动画只露个开头；所以停之前先把这一遍放完，标题行也挂到这一遍结束。
// 按图标各算各的，不拿最慢那个统一卡：快图标不该多挂。改了图标动画要同步这里。
const PASS_MS = new Map<AnimatedIcon, number>([
  [UsersIcon, 600],
  [CalculatorIcon, 900], [ClockIcon, 900], [DatabaseIcon, 900], [PackageOpenIcon, 900],
  [TerminalIcon, 800],
  [SearchIcon, 1000], [CloudSunIcon, 1000], [FilePenLineIcon, 1000],
  [FileFetchIcon, 1050], [WrenchIcon, 1050],
  [EarthIcon, 1200],
  [FileTextIcon, 1400],
  [FolderTreeIcon, 1500],
])

/** 这个工具的图标放完一遍的毫秒数。 */
export function animationPassMs(tool: string): number {
  return PASS_MS.get(animatedToolIcon(tool)) ?? 1000
}

/** 工具名 → 动画图标；工具行图标的唯一分类规则（按工具名关键词匹配）。 */
export function animatedToolIcon(tool: string): AnimatedIcon {
  const name = tool.toLowerCase()
  if (name === 'spawn_agents') return UsersIcon
  if (name === 'load_tools') return PackageOpenIcon
  if (/calculator|calculate/.test(name)) return CalculatorIcon
  if (/(?:^|_)(?:datetime|time|date)(?:_|$)/.test(name)) return ClockIcon
  if (/data_query|json_query|database|sql/.test(name)) return DatabaseIcon
  if (/weather|forecast/.test(name)) return CloudSunIcon
  if (/search|grep|find/.test(name)) return SearchIcon
  if (/fetch/.test(name)) return FileFetchIcon
  if (/web|url|browse/.test(name)) return EarthIcon
  if (/list|tree|dir/.test(name)) return FolderTreeIcon
  if (/write|edit|create|patch|replace|append/.test(name)) return FilePenLineIcon
  if (/read|open|cat|view/.test(name)) return FileTextIcon
  if (/script|shell|bash|exec|run|command/.test(name)) return TerminalIcon
  return WrenchIcon
}

function prefersReducedMotion() {
  return typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches === true
}

/*
 * 工具行前的图标：调用运行中时循环播放动画，结束后回到静态。图标经 ref 受控，
 * 所以悬停不会触发动画——历史里已完成的调用保持安静。
 */
export default function AnimatedToolIcon({ tool, running, size = 15, className }: { tool: string; running: boolean; size?: number; className?: string }) {
  const Icon = animatedToolIcon(tool)
  const handle = useRef<IconHandle>(null)
  const lastStart = useRef(0)

  useEffect(() => {
    const icon = handle.current
    if (!icon) return
    if (!running || prefersReducedMotion()) {
      // 正在放的这一遍先放完再停，别在半路弹回静态。
      const remaining = lastStart.current + (PASS_MS.get(Icon) ?? 1000) - Date.now()
      if (remaining <= 0 || prefersReducedMotion()) {
        icon.stopAnimation()
        return
      }
      const timer = setTimeout(() => handle.current?.stopAnimation(), remaining)
      return () => clearTimeout(timer)
    }
    const play = () => { lastStart.current = Date.now(); handle.current?.startAnimation() }
    play()
    const timer = setInterval(play, REPLAY_MS)
    return () => clearInterval(timer)
  }, [running, Icon])

  return <Icon ref={handle} size={size} className={className} aria-hidden data-running={running || undefined} />
}

/**
 * 标题行正在执行的工具：工具一结束图标就换成 R 点阵，快工具的动画来不及放。
 * 这里让出现过的工具挂到它的图标放完第一遍为止，期间换成新工具就立刻跟上新的。
 * 整轮结束不归这里管：调用方只在 running 时显示它。
 */
export function useHeldTool(tool: string | undefined): string | undefined {
  const [held, setHeld] = useState<{ tool: string; since: number } | undefined>(tool ? { tool, since: Date.now() } : undefined)
  const current = tool ? (held?.tool === tool ? held : { tool, since: Date.now() }) : held
  if (current !== held) setHeld(current)
  useEffect(() => {
    if (tool || !held) return
    const timer = setTimeout(() => setHeld(undefined), Math.max(0, held.since + animationPassMs(held.tool) - Date.now()))
    return () => clearTimeout(timer)
  }, [tool, held])
  return current?.tool
}
