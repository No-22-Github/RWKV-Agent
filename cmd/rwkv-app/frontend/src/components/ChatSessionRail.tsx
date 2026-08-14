import { useEffect, useState } from 'react'
import { Folder, MessageSquare, MessagesSquare, MoreVertical, SquarePen, Trash2 } from 'lucide-react'

type ConversationSummary = { id: string; title: string; updatedAt: string }
type WorkspaceItem = { name: string; path: string; active: boolean; available: boolean }

type Props = {
  conversations: ConversationSummary[]
  workspaces: WorkspaceItem[]
  activeId: string
  busy?: boolean
  onOpen: (id: string) => void
  onDelete: (id: string) => void
  onNewChat: () => void
  onOpenWorkspace: (path: string) => void
}

/** 二级会话栏（EvoOne 风）：始终展开 296px，内容错峰滑入；每项的删除菜单用 clip-path 揭示动画。 */
export default function ChatSessionRail({
  conversations, workspaces, activeId, busy, onOpen, onDelete, onNewChat, onOpenWorkspace,
}: Props) {
  const [openMenu, setOpenMenu] = useState<string | null>(null)

  useEffect(() => {
    function close() { setOpenMenu(null) }
    window.addEventListener('pointerdown', close)
    return () => window.removeEventListener('pointerdown', close)
  }, [])

  return (
    <aside className="chat-session-rail chat-session-rail--open">
      <div className="chat-session-rail-header">
        <span className="chat-session-rail-title">对话</span>
        <button
          type="button"
          className="chat-session-rail-header-action"
          title="新会话"
          onClick={onNewChat}
          disabled={busy}
        >
          <SquarePen size={20} />
        </button>
      </div>

      {workspaces.length > 0 && (
        <div className="rail-section">
          <div className="rail-section-title">工作区</div>
          {workspaces.map((ws) => (
            <button
              type="button"
              key={ws.path}
              className={`rail-workspace${ws.active ? ' rail-workspace--active' : ''}`}
              onClick={() => onOpenWorkspace(ws.path)}
              disabled={!ws.available || busy}
              title={ws.path}
            >
              <Folder size={18} />
              <span>{ws.name}</span>
            </button>
          ))}
        </div>
      )}

      <div className="chat-session-rail-list">
        {conversations.length === 0 && (
          <div className="chat-session-rail-empty">
            <MessagesSquare size={28} />
            <span>暂无历史对话</span>
          </div>
        )}
        {conversations.map((c) => (
          <div
            key={c.id}
            className={`chat-session-rail-item${c.id === activeId ? ' chat-session-rail-item--active' : ''}${openMenu === c.id ? ' chat-session-rail-item--menu-open' : ''}`}
            onClick={() => onOpen(c.id)}
            title={c.title || '未命名会话'}
          >
            <MessageSquare className="chat-session-rail-item-icon" size={20} />
            <div className="chat-session-rail-item-content">
              <div className="chat-session-rail-item-head">
                <div className="chat-session-rail-item-label">{c.title || '未命名会话'}</div>
                <div className="chat-session-rail-item-time">{relativeTime(c.updatedAt)}</div>
              </div>
            </div>
            <div className="chat-session-rail-item-actions" onClick={(e) => e.stopPropagation()}>
              <button
                type="button"
                className="chat-session-rail-item-menu-trigger"
                title="更多操作"
                aria-label="更多操作"
                aria-expanded={openMenu === c.id}
                onClick={(e) => { e.stopPropagation(); setOpenMenu((prev) => (prev === c.id ? null : c.id)) }}
              >
                <MoreVertical size={18} />
              </button>
              <div className={`chat-session-rail-item-menu${openMenu === c.id ? ' chat-session-rail-item-menu--open' : ''}`}>
                <button
                  type="button"
                  className="chat-session-rail-item-menu-item"
                  tabIndex={openMenu === c.id ? 0 : -1}
                  onClick={(e) => { e.stopPropagation(); setOpenMenu(null); onDelete(c.id) }}
                >
                  <Trash2 size={18} />
                  <span>删除会话</span>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="chat-session-rail-spacer" />
    </aside>
  )
}

function relativeTime(value: string) {
  const timestamp = new Date(value).getTime()
  if (!Number.isFinite(timestamp)) return ''
  const elapsed = Math.max(0, Math.floor((Date.now() - timestamp) / 1000))
  if (elapsed < 60) return '刚刚'
  const minutes = Math.floor(elapsed / 60)
  if (minutes < 60) return `${minutes} 分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours} 小时前`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days} 天前`
  return new Intl.DateTimeFormat('zh-CN', { month: 'numeric', day: 'numeric' }).format(timestamp)
}
