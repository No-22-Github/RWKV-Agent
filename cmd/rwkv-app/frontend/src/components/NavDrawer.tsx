import { useRef, useState, type ReactNode } from 'react'
import { FolderOpen, Moon, Settings, Sparkles, SquarePen, Sun } from 'lucide-react'
import { toggleDarkMode } from '../theme'

type Props = {
  dark: boolean
  onToggleDark: (next: boolean) => void
  onNewChat: () => void
  onChooseWorkspace: () => void
  onOpenSettings: () => void
  busy?: boolean
}

/**
 * MD3 导航栏（EvoOne 风）：默认 80px 图标轨道，hover 展开到 260px，
 * 展开时标签滑入、激活项药丸背景横向生长。深色切换用 View Transitions
 * 做圆形揭示动画（从按钮中心扩散）。
 */
export default function NavDrawer({ dark, onToggleDark, onNewChat, onChooseWorkspace, onOpenSettings, busy }: Props) {
  const [expanded, setExpanded] = useState(false)
  const navRef = useRef<HTMLElement>(null)
  const toggleRef = useRef<HTMLButtonElement>(null)
  const transitioningRef = useRef(false)
  const themeAnimationRef = useRef<Animation | null>(null)
  const themeSeqRef = useRef(0)

  function handleToggleDark() {
    const btn = toggleRef.current
    themeAnimationRef.current?.cancel()

    // 浏览器不擅长处理重叠的 view transition；若已有一个在进行中，退化为立即切换
    if (!btn || !document.startViewTransition || document.documentElement.matches(':active-view-transition')) {
      onToggleDark(toggleDarkMode())
      transitioningRef.current = false
      return
    }

    const rect = btn.getBoundingClientRect()
    const x = rect.left + rect.width / 2
    const y = rect.top + rect.height / 2
    const maxRadius = Math.hypot(Math.max(x, window.innerWidth - x), Math.max(y, window.innerHeight - y))

    transitioningRef.current = true
    const seq = ++themeSeqRef.current

    const transition = document.startViewTransition(() => {
      onToggleDark(toggleDarkMode())
    })

    transition.ready.then(() => {
      if (themeSeqRef.current !== seq) return
      themeAnimationRef.current?.cancel()
      themeAnimationRef.current = document.documentElement.animate(
        { clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${maxRadius}px at ${x}px ${y}px)`] },
        { duration: 500, easing: 'cubic-bezier(0.2, 0, 0, 1)', pseudoElement: '::view-transition-new(root)' },
      )
    })

    transition.finished.finally(() => {
      if (themeSeqRef.current !== seq) return
      transitioningRef.current = false
      themeAnimationRef.current = null
      const nav = navRef.current
      if (nav && !nav.matches(':hover')) setExpanded(false)
    })
  }

  const setExpandedSafe = (value: boolean) => {
    if (!transitioningRef.current) setExpanded(value)
  }

  return (
    <nav
      ref={navRef}
      className={`nav-drawer${expanded ? ' nav-drawer--expanded' : ''}`}
      onMouseEnter={() => setExpandedSafe(true)}
      onMouseLeave={() => setExpandedSafe(false)}
    >
      <div className="nav-brand">
        <div className="nav-brand-avatar"><Sparkles size={22} strokeWidth={2.2} /></div>
        <span className="nav-brand-name">rwkv</span>
      </div>

      <ul className="nav-list">
        <li><NavAction icon={<SquarePen size={22} />} label="新会话" onClick={onNewChat} disabled={busy} /></li>
        <li><NavAction icon={<FolderOpen size={22} />} label="打开工作区" onClick={onChooseWorkspace} disabled={busy} /></li>
      </ul>

      <div className="nav-spacer" />

      <div className="nav-footer">
        <NavAction icon={<Settings size={22} />} label="设置" onClick={onOpenSettings} />
        <button
          ref={toggleRef}
          className="nav-item"
          onClick={handleToggleDark}
          title={dark ? '浅色模式' : '深色模式'}
        >
          <span className="nav-pill-bg" />
          <span className="nav-icon">{dark ? <Sun size={22} /> : <Moon size={22} />}</span>
          <span className="nav-label">{dark ? '浅色模式' : '深色模式'}</span>
        </button>
      </div>
    </nav>
  )
}

function NavAction({ icon, label, onClick, disabled }: { icon: ReactNode; label: string; onClick: () => void; disabled?: boolean }) {
  return (
    <button className="nav-item" onClick={onClick} disabled={disabled} title={label}>
      <span className="nav-pill-bg" />
      <span className="nav-icon">{icon}</span>
      <span className="nav-label">{label}</span>
    </button>
  )
}
