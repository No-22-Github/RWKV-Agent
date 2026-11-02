import { useEffect, useMemo, useRef, useState } from 'react'
import { ChevronRight, FolderPlus, MoreHorizontal, PenLine, Pin, Plus, Settings, SquarePen, Trash2 } from 'lucide-react'
import type { ConversationSummary, WorkspaceItem } from '../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/models'
import ConfirmDialog from './ConfirmDialog'
import Wordmark from './Wordmark'

type Props = {
  conversations: ConversationSummary[]
  workspaces: WorkspaceItem[]
  activeId: string
  busy: boolean
  open: boolean
  onCloseSidebar: () => void
  onNewChat: () => void
  onChooseWorkspace: () => void
  onOpenSettings: () => void
  /* 打开某个工作区里的对话；id 为空是在那个工作区新建对话。 */
  onOpen: (workspace: WorkspaceItem, id: string) => void
  onDelete: (id: string) => void
  onRename: (id: string, title: string) => Promise<void>
  onTogglePin: (id: string, pinned: boolean) => Promise<void>
  onRemoveWorkspace: (path: string, deleteConversations: boolean) => void
}

/* 每组先露这么多条，多的折进「显示全部」。 */
const GROUP_PREVIEW = 6
const COLLAPSED_KEY = 'rwkv-sidebar-collapsed'

function loadCollapsed(): Set<string> {
  try { return new Set(JSON.parse(window.localStorage.getItem(COLLAPSED_KEY) || '[]') as string[]) } catch { return new Set() }
}
function storeCollapsed(value: Set<string>) {
  try { window.localStorage.setItem(COLLAPSED_KEY, JSON.stringify([...value])) } catch { /* 记不住只是下次重新展开 */ }
}

/*
 * 侧栏按工作区分组列出对话（同 Claude 桌面版的项目分组）：组标题点一下折叠，悬停露出「在这里新建对话」与「…」。
 * 点别的工作区里的对话会直接切到那个工作区再打开，远端连接跟着带过去。
 * 组的顺序在一次运行里固定：后端按最近使用排序，点哪组那组就跑到最上面，列表会在手底下乱跳；
 * 所以只在第一次见到时按后端顺序排，之后新出现的工作区插在最前面，其余不动。
 */
export default function Sidebar({ conversations, workspaces, activeId, busy, open, onCloseSidebar, onNewChat, onChooseWorkspace, onOpenSettings, onOpen, onDelete, onRename, onTogglePin, onRemoveWorkspace }: Props) {
  const [menu, setMenu] = useState<{ id: string; up: boolean } | null>(null)
  const [renaming, setRenaming] = useState<string | null>(null)
  const [renameValue, setRenameValue] = useState('')
  const [deleteTarget, setDeleteTarget] = useState<ConversationSummary | null>(null)
  const [removeTarget, setRemoveTarget] = useState<WorkspaceItem | null>(null)
  const [collapsed, setCollapsed] = useState(loadCollapsed)
  const [expanded, setExpanded] = useState<Set<string>>(() => new Set())
  const order = useRef<string[]>([])

  const groups = useMemo(() => {
    const known = new Set(order.current)
    const fresh = workspaces.map((workspace) => workspace.path).filter((path) => !known.has(path))
    const present = new Set(workspaces.map((workspace) => workspace.path))
    order.current = [...fresh, ...order.current.filter((path) => present.has(path))]
    const byPath = new Map(workspaces.map((workspace) => [workspace.path, workspace]))
    const active = workspaces.find((workspace) => workspace.active)
    return order.current.map((path) => {
      const workspace = byPath.get(path)!
      // 旧数据里没有工作区字段的对话只可能来自当前工作区（以前只列当前工作区）。
      const items = conversations.filter((conversation) => conversation.workspace ? conversation.workspace === path : workspace === active)
      return { workspace, items }
    })
  }, [workspaces, conversations])

  // 点击侧栏空白处或按 Esc 时收起菜单/重命名（HIG：菜单可经外部交互关闭）。
  useEffect(() => {
    if (!menu && !renaming) return
    function onPointerDown(event: PointerEvent) {
      // 「…」按钮自己负责开合；这里也关的话，按下关、松开又开，菜单会闪一下又弹出来。
      if (event.target instanceof Element && event.target.closest('[data-sidebar-menu],.sidebar-menu-trigger,input[aria-label="重命名会话"]')) return
      setMenu(null); setRenaming(null)
    }
    function onKeyDown(event: globalThis.KeyboardEvent) {
      if (event.key === 'Escape') { setMenu(null); setRenaming(null) }
    }
    document.addEventListener('pointerdown', onPointerDown)
    document.addEventListener('keydown', onKeyDown)
    return () => { document.removeEventListener('pointerdown', onPointerDown); document.removeEventListener('keydown', onKeyDown) }
  }, [menu, renaming])

  // 列表视口下方放不下菜单（约 128px 高）时向上弹出，避免末行菜单被裁剪。
  function toggleMenu(id: string, event: React.MouseEvent<HTMLButtonElement>) {
    if (menu?.id === id) { setMenu(null); return }
    const list = event.currentTarget.closest('[data-sidebar-scroll]')
    const up = list ? list.getBoundingClientRect().bottom - event.currentTarget.getBoundingClientRect().bottom < 132 : false
    setMenu({ id, up })
  }
  function toggleCollapsed(path: string) {
    setCollapsed((current) => {
      const next = new Set(current)
      if (next.has(path)) next.delete(path); else next.add(path)
      storeCollapsed(next)
      return next
    })
  }
  function toggleExpanded(path: string) {
    setExpanded((current) => { const next = new Set(current); if (next.has(path)) next.delete(path); else next.add(path); return next })
  }
  function startRename(conversation: ConversationSummary) {
    setMenu(null); setRenaming(conversation.id); setRenameValue(conversation.title || '')
  }
  function commitRename(id: string) {
    const title = renameValue.trim()
    setRenaming(null)
    if (title) void onRename(id, title)
  }

  return <>
    {open && <div className="sidebar-scrim fixed inset-0 z-[40] bg-overlay lg:hidden" onClick={onCloseSidebar} />}
    <aside data-open={open} className={`compact:w-[208px] compact:basis-[208px] max-lg:data-[open=true]:shadow-[0_12px_40px_rgba(60,50,35,.2)] [--wails-draggable:drag] [&_button]:[--wails-draggable:no-drag] [&_input]:[--wails-draggable:no-drag] wails-mac:pt-[52px] fixed inset-y-0 left-0 z-[50] flex h-full w-(--sidebar-w) flex-none flex-col border-r border-line bg-paper-sidebar py-[18px] text-ink transition-transform duration-200 motion-reduce:transition-none lg:relative lg:translate-x-0 ${open ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
      {/* macOS 隐藏了标题栏，红绿灯浮在左上角（中线距顶约 26px、右缘 79px）：字标紧跟在红绿灯右边（隔 12px，和红绿灯彼此的间距相当）、同一中线，像窗口标题一样和它们连成一组，
          下面的内容随之上移；其他平台照常放在侧栏左上角。 */}
      <div className="flex items-center px-[18px] pb-[18px] text-md font-semibold wails-mac:absolute wails-mac:left-[91px] wails-mac:top-0 wails-mac:h-[52px] wails-mac:p-0"><Wordmark /></div>
      <button className="mx-[18px] mb-[10px] flex h-8 items-center justify-center gap-2 rounded-md border border-line bg-paper-wash px-[10px] text-sm font-medium text-ink shadow-hair transition-colors hover:bg-surface-active" onClick={onNewChat} disabled={busy}><SquarePen size={16} />新的对话 <kbd className="ml-[2px] font-mono text-2xs text-ink-muted">⌘N</kbd></button>

      <div className="flex h-[30px] flex-none items-center justify-between pl-[18px] pr-[10px]">
        <span className="text-2xs font-medium text-ink-muted">工作区</span>
        <button className="grid h-[24px] w-[24px] place-items-center rounded-md border-0 bg-transparent text-ink-muted transition-colors hover:bg-surface-active hover:text-ink" onClick={onChooseWorkspace} disabled={busy} aria-label="打开工作区" title="打开工作区…"><FolderPlus size={15} /></button>
      </div>

      <nav data-sidebar-scroll aria-label="对话" className="min-h-0 flex-1 overflow-y-auto pb-[8px]">
        {groups.map(({ workspace, items }) => {
          const isCollapsed = collapsed.has(workspace.path)
          const showAll = expanded.has(workspace.path)
          const visible = showAll ? items : items.slice(0, GROUP_PREVIEW)
          const menuId = `ws:${workspace.path}`
          return <section key={workspace.path} className="mb-[12px]" aria-label={workspace.name}>
            <div className="group/workspace relative mx-[10px] flex items-center rounded-md">
              <button
                className={`flex h-[30px] min-w-0 flex-1 items-center gap-[6px] rounded-md border-0 bg-transparent px-[8px] text-left text-sm transition-colors group-hover/workspace:pr-[60px] group-focus-within/workspace:pr-[60px] hover:bg-surface-active ${workspace.active ? 'font-semibold text-ink' : workspace.available ? 'font-medium text-ink-soft' : 'text-ink-muted'}`}
                aria-expanded={!isCollapsed}
                title={workspace.available ? workspace.path : `${workspace.path}（目录已不存在）`}
                onClick={() => toggleCollapsed(workspace.path)}
              >
                <span className="truncate">{workspace.name}</span>
                <ChevronRight size={13} className={`flex-none text-ink-ghost transition-transform duration-150 motion-reduce:transition-none ${isCollapsed ? '' : 'rotate-90'}`} />
              </button>
              <span className="invisible absolute right-[4px] top-1/2 flex -translate-y-1/2 items-center group-hover/workspace:visible group-focus-within/workspace:visible has-[[aria-expanded=true]]:visible">
                <button className="grid h-[24px] w-[24px] place-items-center rounded-md border-0 bg-transparent text-ink-muted hover:text-ink" aria-label={`在“${workspace.name}”里新建对话`} title="新建对话" disabled={busy || !workspace.available} onClick={() => onOpen(workspace, '')}><Plus size={15} /></button>
                {/* 当前打开的工作区不能移除，也就不给「…」。 */}
                {!workspace.active && <button className="sidebar-menu-trigger grid h-[24px] w-[24px] place-items-center rounded-md border-0 bg-transparent text-ink-muted hover:text-ink" aria-label={`工作区“${workspace.name}”的更多操作`} aria-haspopup="menu" aria-expanded={menu?.id === menuId} onClick={(event) => toggleMenu(menuId, event)}><MoreHorizontal size={15} /></button>}
              </span>
              {menu?.id === menuId && (
                <div data-sidebar-menu className={`absolute right-2 z-[5] flex min-w-[148px] flex-col rounded-lg border border-line bg-paper-wash p-1 shadow-pop ${menu.up ? 'bottom-[30px]' : 'top-[30px]'}`} role="menu" aria-label="工作区操作">
                  <button role="menuitem" className="flex items-center gap-[7px] rounded-sm border-0 bg-transparent px-[8px] py-[6px] text-left text-sm text-danger hover:bg-surface-active" onClick={() => { setMenu(null); setRemoveTarget(workspace) }}><Trash2 size={14} />从列表移除</button>
                </div>
              )}
            </div>

            {!isCollapsed && <>
              {items.length === 0 && <div className="mx-[10px] px-[8px] py-[5px] text-sm text-ink-ghost">暂无对话</div>}
              {visible.map((conversation) => {
                const title = conversation.title || '未命名会话'
                const active = conversation.id === activeId
                return <div key={conversation.id} data-active={active} className={`group/conversation relative mx-[10px] flex items-center rounded-md transition-colors ${active ? 'bg-surface-active text-ink' : 'bg-transparent text-ink-soft hover:bg-surface-active hover:text-ink'}`}>
                  {renaming === conversation.id
                    ? <div className="flex min-w-0 flex-1 p-[3px_4px]"><input autoFocus aria-label="重命名会话" className="h-[26px] min-w-0 flex-1 rounded-md border border-line-strong bg-paper px-[6px] text-sm text-ink outline-none focus:border-brand" value={renameValue} onChange={(event) => setRenameValue(event.target.value)} onBlur={() => commitRename(conversation.id)} onKeyDown={(event) => { if (event.key === 'Enter') commitRename(conversation.id); if (event.key === 'Escape') setRenaming(null) }} /></div>
                    : <button className="flex h-[32px] min-w-0 flex-1 items-center gap-[5px] border-0 bg-transparent px-[8px] text-left text-sm text-inherit group-hover/conversation:pr-[32px] group-focus-within/conversation:pr-[32px] group-data-[active=true]/conversation:pr-[32px]" disabled={!workspace.available} onClick={() => { if (!active) onOpen(workspace, conversation.id) }} title={title}>
                        {conversation.pinned && <Pin size={11} className="flex-none text-ink-muted" aria-label="已置顶" />}
                        <span className="min-w-0 truncate">{title}</span>
                      </button>}
                  <button className="sidebar-menu-trigger invisible absolute right-[4px] top-1/2 grid h-[24px] w-[24px] -translate-y-1/2 place-items-center rounded-md border-0 bg-transparent text-ink-muted hover:text-ink group-hover/conversation:visible group-focus-within/conversation:visible group-data-[active=true]/conversation:visible aria-expanded:visible" aria-label={`会话“${title}”的更多操作`} aria-haspopup="menu" aria-expanded={menu?.id === conversation.id} onClick={(event) => toggleMenu(conversation.id, event)}><MoreHorizontal size={15} /></button>
                  {menu?.id === conversation.id && (
                    <div data-sidebar-menu className={`absolute right-2 z-[5] flex min-w-[128px] flex-col rounded-lg border border-line bg-paper-wash p-1 shadow-pop ${menu.up ? 'bottom-[30px]' : 'top-[30px]'}`} role="menu" aria-label="会话操作">
                      <button role="menuitem" className="flex items-center gap-[7px] rounded-sm border-0 bg-transparent px-[8px] py-[6px] text-left text-sm text-ink hover:bg-surface-active" onClick={() => { setMenu(null); void onTogglePin(conversation.id, !conversation.pinned) }}><Pin size={14} />{conversation.pinned ? '取消置顶' : '置顶'}</button>
                      <button role="menuitem" className="flex items-center gap-[7px] rounded-sm border-0 bg-transparent px-[8px] py-[6px] text-left text-sm text-ink hover:bg-surface-active" onClick={() => startRename(conversation)}><PenLine size={14} />重命名</button>
                      <button role="menuitem" className="flex items-center gap-[7px] rounded-sm border-0 bg-transparent px-[8px] py-[6px] text-left text-sm text-danger hover:bg-surface-active" onClick={() => { setMenu(null); setDeleteTarget(conversation) }}><Trash2 size={14} />删除会话</button>
                    </div>
                  )}
                </div>
              })}
              {items.length > GROUP_PREVIEW && <button className="mx-[10px] flex h-[28px] items-center rounded-md border-0 bg-transparent px-[8px] text-2xs text-ink-muted transition-colors hover:text-ink" onClick={() => toggleExpanded(workspace.path)}>{showAll ? '收起' : `显示全部（${items.length}）`}</button>}
            </>}
          </section>
        })}
      </nav>

      <ConfirmDialog open={deleteTarget !== null} title="删除会话" body={deleteTarget ? `将删除“${deleteTarget.title || '未命名会话'}”及其全部消息，此操作无法撤销。` : ''} onClose={() => setDeleteTarget(null)} actions={[{ label: '取消', onClick: () => setDeleteTarget(null) }, { label: '删除', variant: 'danger', onClick: () => { const target = deleteTarget; setDeleteTarget(null); if (target) onDelete(target.id) } }]} />
      <ConfirmDialog open={removeTarget !== null} title="移除工作区" body={removeTarget ? `将把“${removeTarget.name}”从侧栏移除，磁盘上的文件不受影响。这个工作区的对话记录可以保留（重新打开该目录时还在），也可以一并删除。` : ''} onClose={() => setRemoveTarget(null)} actions={[{ label: '取消', onClick: () => setRemoveTarget(null) }, { label: '移除并删除对话', variant: 'danger', onClick: () => { const target = removeTarget; setRemoveTarget(null); if (target) onRemoveWorkspace(target.path, true) } }, { label: '移除', variant: 'primary', onClick: () => { const target = removeTarget; setRemoveTarget(null); if (target) onRemoveWorkspace(target.path, false) } }]} />
      <button className="mt-[6px] flex items-center gap-[9px] border-0 border-t border-line bg-transparent px-[18px] pb-0 pt-3 text-left text-sm text-ink-soft transition-colors hover:text-ink" onClick={onOpenSettings} aria-label="设置"><Settings size={16} /><span className="flex-1">设置</span><kbd className="ml-[2px] font-mono text-2xs text-ink-muted">⌘,</kbd></button>
    </aside>
  </>
}

