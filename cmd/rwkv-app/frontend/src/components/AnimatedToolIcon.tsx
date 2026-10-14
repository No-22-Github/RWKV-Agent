import { useEffect, useRef, type ForwardRefExoticComponent, type HTMLAttributes, type RefAttributes } from 'react'
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

  useEffect(() => {
    const icon = handle.current
    if (!icon) return
    if (!running || prefersReducedMotion()) {
      icon.stopAnimation()
      return
    }
    icon.startAnimation()
    const timer = setInterval(() => handle.current?.startAnimation(), REPLAY_MS)
    return () => clearInterval(timer)
  }, [running, Icon])

  return <Icon ref={handle} size={size} className={className} aria-hidden data-running={running || undefined} />
}
