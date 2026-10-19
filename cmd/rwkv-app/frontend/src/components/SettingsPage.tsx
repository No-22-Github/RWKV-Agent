import { useEffect, useRef, useState, type ReactNode } from 'react'
import { Bot, Cloud, Cpu, Palette, Settings2, X } from 'lucide-react'
import type { Status } from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import { type ProviderManager, type SettingsSection } from '../state/providerManager'
import type { ThemePreference } from '../theme'
import ConfirmDialog, { type ConfirmAction } from './ConfirmDialog'
import ConnectionsSection from './settings/ConnectionsSection'
import GeneralSection, { AppearanceSection } from './settings/GeneralSection'
import GlobalAgentSection from './settings/GlobalAgentSection'
import type { AgentSettingsState } from '../state/agentSettings'


type Props = {
  manager: ProviderManager
  agent: AgentSettingsState
  status: Status
  ready: boolean
  onChooseWorkspace: () => void | Promise<void>
  themePreference: ThemePreference
  onThemeChange: (preference: ThemePreference) => void
  onDeleteProvider: (id: string) => void
}

const NAV_ITEMS: { id: SettingsSection; icon: ReactNode }[] = [
  { id: '远端连接', icon: <Cloud size={15} /> },
  { id: '本地推理', icon: <Cpu size={15} /> },
  { id: 'Agent', icon: <Bot size={15} /> },
  { id: '外观', icon: <Palette size={15} /> },
  { id: '通用', icon: <Settings2 size={15} /> },
]

/*
 * 设置弹窗：浮在对话上方的卡片，背后的对话保持可见，进出都不丢上下文。
 * 关闭方式：右上 ✕、Esc、点卡片外、再按 ⌘,。脏表单时关闭走确认框，不再阻断或静默丢失。
 * 远端连接与本地推理分开：本地模型有加载与释放的代价，远端只是换个地址，两者不混在一个列表里。
 * 连接、生成参数与 Agent 编辑的都是同一份档案，所以收在同一个详情下的三个标签里。
 */
export default function SettingsPage({ manager, agent, status, ready, onChooseWorkspace, themePreference, onThemeChange, onDeleteProvider }: Props) {
  const section = manager.settingsSection
  // 切分区前草稿没法自动保存时，先问；问完再去这里。
  const [pendingSection, setPendingSection] = useState<SettingsSection | null>(null)
  const [confirmClose, setConfirmClose] = useState(false)
  const pointerOnBackdrop = useRef(false)

  /* 返回对话：待保存的更改先落盘再关；只有无法自动保存时才弹确认框。 */
  async function requestClose() {
    if (confirmClose || pendingSection) return // 确认框自己处理 Esc
    if (manager.draftDirty && !(await manager.flushDraft())) {
      setConfirmClose(true)
      return
    }
    manager.setSettingsOpen(false)
  }

  // Esc 监听只挂一次，经 ref 调最新一轮渲染的 requestClose：否则会用旧闭包里的草稿去落盘。
  const requestCloseRef = useRef(requestClose)
  requestCloseRef.current = requestClose
  useEffect(() => {
    if (!manager.settingsOpen) return
    function onKeyDown(event: KeyboardEvent) {
      // Esc 与再按一次 ⌘, 都是关闭；打开设置的 ⌘, 由 App 处理。
      const toggle = event.key === ',' && (event.metaKey || event.ctrlKey)
      if ((event.key !== 'Escape' && !toggle) || event.defaultPrevented) return
      event.preventDefault()
      void requestCloseRef.current()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [manager.settingsOpen])

  // 打开时把焦点移进卡片：背后的对话被 inert 后，键盘操作从这里开始。
  const dialogRef = useRef<HTMLDivElement>(null)
  useEffect(() => { dialogRef.current?.focus() }, [])

  /* 切分区：换到另一类档案前先把草稿落盘；新建未建档、校验不过时弹确认框。 */
  async function requestSection(next: SettingsSection) {
    if (next === section) return
    const kind = next === '远端连接' ? 'remote' : next === '本地推理' ? 'local' : null
    if (kind && kind !== manager.settingsTab && manager.draftDirty && !(await manager.flushDraft())) {
      setPendingSection(next)
      return
    }
    if (kind) {
      // 换到另一类档案从列表开始（那一类一个都没有时直接进新建草稿）；回到同一类则停在原来的列表或详情。
      const sameKind = kind === manager.settingsTab
      const target = manager.focusKind(kind)
      if (!sameKind) manager.setSettingsDetail(target === 'new')
    }
    manager.setSettingsSection(next)
  }
  async function resolveSection(action: 'save' | 'discard') {
    const next = pendingSection
    setPendingSection(null)
    if (!next) return
    if (action === 'save') {
      if (!(await manager.saveProviderDraft())) return
    } else {
      manager.discardDraft()
    }
    manager.setSettingsDetail(manager.focusKind(next === '本地推理' ? 'local' : 'remote', true) === 'new')
    manager.setSettingsSection(next)
  }

  async function resolveClose(action: 'save' | 'discard' | 'cancel') {
    setConfirmClose(false)
    if (action === 'cancel') return
    if (action === 'save') {
      if (!(await manager.saveProviderDraft())) return
    } else {
      manager.discardDraft()
    }
    manager.setSettingsOpen(false)
  }

  const draftSection: SettingsSection = manager.settingsTab === 'local' ? '本地推理' : '远端连接'
  const connectionSection = section === '远端连接' || section === '本地推理'
  const creating = manager.editingProviderId === ''
  const closeActions: ConfirmAction[] = [
    // 已有档案走到这里说明自动保存失败，只给放弃/留下；新建连接才能在这里建档。
    ...(creating ? [{ label: '保存并返回', variant: 'primary' as const, onClick: () => void resolveClose('save') }] : []),
    { label: '放弃更改', onClick: () => void resolveClose('discard') },
    { label: '留在设置', onClick: () => setConfirmClose(false) },
  ]
  // 自动保存后"未保存"只剩两种真问题：新建连接未建档、或更改无法保存。
  const profileNeedsAttention = manager.draftDirty && (creating || manager.saveState.kind === 'invalid' || manager.saveState.kind === 'error')

  return (
    <div
      className="fixed inset-0 z-[60] grid animate-fade-in place-items-center bg-overlay p-[24px] wails-mac:pt-[44px] motion-reduce:animate-none"
      // 只认按下与松开都在遮罩上的点击：在卡片里拖选文字拖到外面松手，不该关掉设置。
      onPointerDown={(event) => { pointerOnBackdrop.current = event.target === event.currentTarget }}
      onClick={(event) => { if (pointerOnBackdrop.current && event.target === event.currentTarget) void requestClose() }}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-label="设置"
        tabIndex={-1}
        className="flex h-[min(780px,100%)] w-[min(1140px,100%)] animate-sheet-in overflow-hidden rounded-xl border border-line bg-paper text-ink shadow-pop outline-0 motion-reduce:animate-none"
      >
        <aside className="flex w-[200px] flex-none flex-col border-r border-line bg-paper-sidebar px-[10px] py-[18px]">
          <div className="px-[10px] pb-[14px] text-md font-semibold text-ink">设置</div>
          <nav aria-label="设置分区" className="flex flex-col gap-[2px]">
            {NAV_ITEMS.map(({ id, icon }) => (
              <button
                key={id}
                aria-current={section === id ? 'page' : undefined}
                className={`flex h-[34px] items-center gap-[10px] rounded-md border-0 px-[10px] text-left text-base transition-colors ${section === id ? 'bg-surface-active font-medium text-ink' : 'bg-transparent text-ink-soft hover:bg-surface-active hover:text-ink'}`}
                onClick={() => void requestSection(id)}
              >
                <span className="flex-none text-ink-muted">{icon}</span>
                {id}
                {id === draftSection && profileNeedsAttention && <span className="ml-auto h-[6px] w-[6px] rounded-full bg-warning" title={manager.draftBlockReason || '有未保存更改'} />}
              </button>
            ))}
          </nav>
        </aside>

        {/* 内容区没有自己的页头：标题就是各分区的第一个 Section 或详情页的名称；关闭按钮浮在右上角。 */}
        <main className="relative flex min-w-0 flex-1 flex-col">
          <button className="absolute right-[12px] top-[12px] z-[1] grid h-[30px] w-[30px] place-items-center rounded-md border-0 bg-transparent text-ink-muted transition-colors hover:bg-surface-active hover:text-ink" aria-label="关闭设置" title="关闭（Esc）" onClick={() => void requestClose()}><X size={16} /></button>

          {connectionSection
            ? <ConnectionsSection key={section} kind={section === '本地推理' ? 'local' : 'remote'} manager={manager} ready={ready} onDeleteProvider={onDeleteProvider} />
            : section === 'Agent'
              ? <GlobalAgentSection agent={agent} />
            : section === '外观'
              ? <AppearanceSection themePreference={themePreference} onThemeChange={onThemeChange} />
              : <GeneralSection status={status} onChooseWorkspace={onChooseWorkspace} />}
        </main>
      </div>

      <ConfirmDialog
        open={pendingSection !== null}
        title="有未保存的更改"
        body={`${manager.draftBlockReason || '当前档案有未保存的更改。'}要如何处理？`}
        actions={[
          ...(manager.editingProviderId === '' ? [{ label: '保存', variant: 'primary' as const, onClick: () => void resolveSection('save') }] : []),
          { label: '放弃更改', onClick: () => void resolveSection('discard') },
          { label: '留在这里', onClick: () => setPendingSection(null) },
        ]}
        onClose={() => setPendingSection(null)}
      />
      <ConfirmDialog
        open={confirmClose}
        title="有未保存的更改"
        body={`${manager.draftBlockReason || "当前连接档案有未保存的更改。"}要如何处理？`}
        actions={closeActions}
        onClose={() => setConfirmClose(false)}
      />
    </div>
  )
}
