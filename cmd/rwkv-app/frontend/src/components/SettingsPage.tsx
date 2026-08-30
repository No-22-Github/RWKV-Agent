import { useEffect, useState } from 'react'
import { ArrowLeft } from 'lucide-react'
import type { Status } from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { ProviderManager } from '../state/providerManager'
import type { ThemeMode } from '../theme'
import ConfirmDialog, { type ConfirmAction } from './ConfirmDialog'
import AgentBehaviorSection from './settings/AgentBehaviorSection'
import ConnectionsSection from './settings/ConnectionsSection'
import GeneralSection from './settings/GeneralSection'

type Section = '连接' | 'Agent' | '通用'

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

const NAV_ITEMS: Section[] = ['连接', 'Agent', '通用']

/* 连接与 Agent 都在编辑同一份档案草稿：脏标记要在两个分区上都可见。 */
const PROFILE_SECTIONS: Section[] = ['连接', 'Agent']

/* 设置页 shell：侧栏导航 + 内容区。脏表单时关闭/Esc 走确认框，不再阻断或静默丢失。 */
export default function SettingsPage({ manager, status, ready, onChooseWorkspace, theme, onToggleTheme, onActivateProvider, onDeleteProvider }: Props) {
  const [section, setSection] = useState<Section>('连接')
  const [confirmClose, setConfirmClose] = useState(false)

  function requestClose() {
    if (manager.draftDirty) setConfirmClose(true)
    else manager.setSettingsOpen(false)
  }

  useEffect(() => {
    if (!manager.settingsOpen) return
    function onKeyDown(event: KeyboardEvent) {
      if (event.key !== 'Escape') return
      event.preventDefault()
      requestClose()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [manager.settingsOpen, manager.draftDirty])

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
  const closeActions: ConfirmAction[] = [
    { label: '保存并返回', variant: 'primary', onClick: () => void resolveClose('save') },
    { label: '放弃更改', onClick: () => void resolveClose('discard') },
    { label: '留在设置', onClick: () => setConfirmClose(false) },
  ]

  return (
    <div className="flex h-full w-full bg-paper text-ink">
      <aside className="settings-sidebar flex h-full w-(--sidebar-w) flex-none flex-col border-r border-line bg-paper-sidebar py-[18px]">
        <div className="px-[18px] pb-[18px] font-serif text-lg font-semibold">设置</div>
        {NAV_ITEMS.map((item) => (
          <button
            key={item}
            className={`flex items-center gap-[9px] px-[18px] py-[8px] text-left text-base ${section === item ? 'bg-surface-active font-semibold text-ink' : 'text-ink-soft'}`}
            onClick={() => setSection(item)}
          >
            <span className={`h-[14px] w-[3px] flex-none ${section === item ? 'bg-brand' : 'bg-transparent'}`} />
            {item}
            {PROFILE_SECTIONS.includes(item) && manager.draftDirty && <span className="ml-auto h-[6px] w-[6px] rounded-full bg-warning" title="有未保存更改" />}
          </button>
        ))}
        <div className="flex-1" />
        <button className="mx-[18px] mb-3 flex items-center gap-[9px] border border-line bg-transparent px-3 py-2 text-base text-ink-soft" onClick={requestClose}>
          <ArrowLeft size={15} />
          返回对话
        </button>
      </aside>

      <main className="flex min-w-0 flex-1 flex-col">
        <header className="settings-header flex h-(--header-h) flex-none items-end justify-between gap-[16px] border-b border-line px-[30px] pb-[10px]">
          <span className="font-serif text-lg font-semibold">{section}</span>
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
          : section === 'Agent'
            ? <AgentBehaviorSection manager={manager} ready={ready} />
            : <GeneralSection status={status} onChooseWorkspace={onChooseWorkspace} theme={theme} onToggleTheme={onToggleTheme} />}
      </main>

      <ConfirmDialog
        open={confirmClose}
        title="有未保存的更改"
        body="返回对话前要保存当前连接档案的更改吗？"
        actions={closeActions}
        onClose={() => setConfirmClose(false)}
      />
    </div>
  )
}
