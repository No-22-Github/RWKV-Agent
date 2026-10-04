import { useEffect, useRef, useState } from 'react'
import { ArrowLeft } from 'lucide-react'
import type { Status } from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { ProviderManager } from '../state/providerManager'
import type { ThemeMode } from '../theme'
import ConfirmDialog, { type ConfirmAction } from './ConfirmDialog'
import AgentBehaviorSection from './settings/AgentBehaviorSection'
import ConnectionsSection from './settings/ConnectionsSection'
import GeneralSection from './settings/GeneralSection'
import ParametersSection from './settings/ParametersSection'

type Section = '连接' | '参数' | 'Agent' | '通用'

type Props = {
  manager: ProviderManager
  status: Status
  ready: boolean
  onChooseWorkspace: () => void | Promise<void>
  theme: ThemeMode
  onToggleTheme: () => void
  onActivateProvider: (id: string) => void
  onDeleteProvider: (id: string) => void
}

const NAV_ITEMS: Section[] = ['连接', '参数', 'Agent', '通用']

/* 连接、参数与 Agent 都在编辑同一份档案草稿：脏标记要在各分区上都可见。 */
const PROFILE_SECTIONS: Section[] = ['连接', '参数', 'Agent']

/* 设置页 shell：侧栏导航 + 内容区。脏表单时关闭/Esc 走确认框，不再阻断或静默丢失。 */
export default function SettingsPage({ manager, status, ready, onChooseWorkspace, theme, onToggleTheme, onActivateProvider, onDeleteProvider }: Props) {
  const [section, setSection] = useState<Section>('连接')
  const [confirmClose, setConfirmClose] = useState(false)

  /* 返回对话：待保存的更改先落盘再关；只有无法自动保存时才弹确认框。 */
  async function requestClose() {
    if (confirmClose) return // 确认框自己处理 Esc
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
      if (event.key !== 'Escape' || event.defaultPrevented) return
      event.preventDefault()
      void requestCloseRef.current()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [manager.settingsOpen])

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

  const runtime = manager.providers.find((provider) => provider.id === manager.runtimeProviderId)
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
    <div className="flex h-full w-full bg-paper text-ink">
      <aside className="settings-sidebar flex h-full w-(--sidebar-w) flex-none flex-col border-r border-line bg-paper-sidebar py-[18px]">
        <div className="px-[18px] pb-[18px] text-lg font-semibold">设置</div>
        <nav aria-label="设置分区" className="flex flex-col">
        {NAV_ITEMS.map((item) => (
          <button
            key={item}
            aria-current={section === item ? 'page' : undefined}
            className={`mx-[10px] flex items-center gap-[9px] rounded-md px-[10px] py-[7px] text-left text-base transition-colors ${section === item ? 'bg-surface-active font-medium text-ink' : 'text-ink-soft hover:bg-surface-active hover:text-ink'}`}
            onClick={() => setSection(item)}
          >
            {item}
            {PROFILE_SECTIONS.includes(item) && profileNeedsAttention && <span className="ml-auto h-[6px] w-[6px] rounded-full bg-warning" title={manager.draftBlockReason || '有未保存更改'} />}
          </button>
        ))}
        </nav>
        <div className="flex-1" />
        <button className="mx-[18px] mb-3 flex items-center gap-[9px] rounded-md border border-line bg-paper-wash px-3 py-2 text-base text-ink-soft shadow-hair transition-colors hover:bg-surface-active hover:text-ink" onClick={() => void requestClose()}>
          <ArrowLeft size={15} />
          返回对话
        </button>
      </aside>

      <main className="flex min-w-0 flex-1 flex-col">
        <header className="settings-header flex h-(--header-h) flex-none items-end justify-between gap-[16px] border-b border-line px-[30px] pb-[10px]">
          <span className=" text-lg font-semibold">{section}</span>
          {section === '连接' && (
            <span className="flex min-w-0 items-center gap-[7px] text-2xs text-ink-muted">
              {ready && runtime ? (
                <>
                  <span className="h-[6px] w-[6px] flex-none rounded-full bg-brand-bright" />
                  当前运行：<span className="min-w-0 truncate font-medium text-ink-soft">{runtime.label || runtime.config.model || '未命名连接'}</span>
                </>
              ) : (
                '当前没有运行连接'
              )}
            </span>
          )}
        </header>

        {section === '连接'
          ? <ConnectionsSection manager={manager} ready={ready} onActivateProvider={onActivateProvider} onDeleteProvider={onDeleteProvider} />
          : section === '参数'
            ? <ParametersSection manager={manager} />
            : section === 'Agent'
              ? <AgentBehaviorSection manager={manager} />
              : <GeneralSection status={status} onChooseWorkspace={onChooseWorkspace} theme={theme} onToggleTheme={onToggleTheme} />}
      </main>

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
