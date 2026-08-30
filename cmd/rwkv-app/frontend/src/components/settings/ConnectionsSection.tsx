import { useState } from 'react'
import { MoreHorizontal, Plus, Trash2 } from 'lucide-react'
import { Provider } from '../../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { SavedProvider } from '../../../bindings/github.com/no22/RWKV-Agent/internal/appstorage/models'
import type { ProviderManager } from '../../state/providerManager'
import ConfirmDialog from '../ConfirmDialog'
import ProviderEditor from './ProviderEditor'

type Props = {
  manager: ProviderManager
  ready: boolean
  onActivateProvider: (id: string) => void
  onDeleteProvider: (id: string) => void
}

type PendingConfirm =
  | { kind: 'switch'; id: string }
  | { kind: 'new' }
  | { kind: 'delete'; id: string }
  | null

/* 连接管理：左列表 + 右编辑器的主从式布局。脏表单的切换/新建/删除都经确认框。 */
export default function ConnectionsSection({ manager, ready, onActivateProvider, onDeleteProvider }: Props) {
  const [menuForID, setMenuForID] = useState('')
  const [confirm, setConfirm] = useState<PendingConfirm>(null)

  function requestEdit(id: string) {
    setMenuForID('')
    if (id === manager.editingProviderId) return
    if (manager.draftDirty) setConfirm({ kind: 'switch', id })
    else manager.selectProvider(id)
  }
  function requestNew() {
    setMenuForID('')
    if (manager.draftDirty) setConfirm({ kind: 'new' })
    else manager.startNewDraft()
  }
  function requestDelete(id: string) {
    setMenuForID('')
    setConfirm({ kind: 'delete', id })
  }

  async function resolveConfirm(action: 'save' | 'discard' | 'cancel') {
    const pending = confirm
    setConfirm(null)
    if (!pending || pending.kind === 'delete' || action === 'cancel') return
    if (action === 'save') {
      if (!(await manager.saveProviderDraft())) return
    } else {
      manager.discardDraft()
    }
    if (pending.kind === 'switch') manager.selectProvider(pending.id)
    else manager.startNewDraft()
  }

  const deleteTarget = confirm?.kind === 'delete' ? manager.providers.find((provider) => provider.id === confirm.id) : undefined

  return (
    <div className="flex min-h-0 flex-1">
      <aside className="flex w-[232px] flex-none flex-col border-r border-line bg-paper-sidebar">
        <div className="flex items-center justify-between px-[14px] pb-[6px] pt-[14px]">
          <span className="font-mono text-2xs font-medium uppercase tracking-[.14em] text-ink-muted">已保存连接</span>
          <span className="font-mono text-2xs text-ink-ghost">{manager.providers.length}</span>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto px-[10px] pb-[8px]">
          {manager.providers.map((provider) => (
            <ProviderRow
              key={provider.id}
              provider={provider}
              running={ready && provider.id === manager.runtimeProviderId}
              selected={provider.id === manager.editingProviderId}
              dirty={provider.id === manager.editingProviderId && manager.draftDirty}
              menuOpen={menuForID === provider.id}
              onToggleMenu={() => setMenuForID(menuForID === provider.id ? '' : provider.id)}
              onCloseMenu={() => setMenuForID('')}
              onEdit={() => requestEdit(provider.id)}
              onUse={() => { setMenuForID(''); onActivateProvider(provider.id) }}
              onDelete={() => requestDelete(provider.id)}
            />
          ))}
          {manager.providers.length === 0 && (
            <p className="px-[6px] py-[8px] text-xs leading-[1.65] text-ink-muted">还没有保存的连接。在右侧填写并保存即可。</p>
          )}
        </div>
        <button className="mx-[10px] mb-[12px] mt-[6px] flex h-[32px] flex-none items-center justify-center gap-[6px] border-[1.5px] border-ink bg-transparent text-sm font-medium text-ink" onClick={requestNew}>
          <Plus size={14} />新建连接
        </button>
      </aside>

      <ProviderEditor
        manager={manager}
        ready={ready}
        onTestRemote={() => void manager.testRemote()}
        onSave={() => void manager.saveProviderDraft()}
        onSaveAndUse={() => void manager.saveAndUseProviderDraft()}
        onRequestDelete={() => { if (manager.editingProviderId) requestDelete(manager.editingProviderId) }}
      />

      <ConfirmDialog
        open={confirm?.kind === 'switch' || confirm?.kind === 'new'}
        title="有未保存的更改"
        body="当前连接档案的更改还没有保存。要如何处理？"
        actions={[
          { label: '保存', variant: 'primary', onClick: () => void resolveConfirm('save') },
          { label: '放弃更改', onClick: () => void resolveConfirm('discard') },
          { label: '取消', onClick: () => void resolveConfirm('cancel') },
        ]}
        onClose={() => setConfirm(null)}
      />
      <ConfirmDialog
        open={confirm?.kind === 'delete'}
        title="删除连接"
        body={deleteTarget ? `将删除「${deleteTarget.label || deleteTarget.config.model || '未命名连接'}」，此操作不可撤销。` : '将删除该连接，此操作不可撤销。'}
        actions={[
          { label: '删除', variant: 'danger', onClick: () => { const pending = confirm; setConfirm(null); if (pending?.kind === 'delete') onDeleteProvider(pending.id) } },
          { label: '取消', onClick: () => setConfirm(null) },
        ]}
        onClose={() => setConfirm(null)}
      />
    </div>
  )
}

function ProviderRow({ provider, running, selected, dirty, menuOpen, onToggleMenu, onCloseMenu, onEdit, onUse, onDelete }: {
  provider: SavedProvider
  running: boolean
  selected: boolean
  dirty: boolean
  menuOpen: boolean
  onToggleMenu: () => void
  onCloseMenu: () => void
  onEdit: () => void
  onUse: () => void
  onDelete: () => void
}) {
  const meta = provider.config.provider === Provider.ProviderLocal
    ? `本地模型 · ${provider.config.model.split(/[\\/]/).at(-1) || provider.config.model}`
    : [provider.config.provider === Provider.ProviderChatCompletions ? 'OpenAI 兼容' : 'RWKV 续写', hostOf(provider.config.endpoint)].filter(Boolean).join(' · ')
  return (
    <div className={`group relative mb-[4px] flex items-stretch border px-[8px] py-[7px] ${selected ? 'border-brand bg-surface-active' : 'border-transparent hover:border-line hover:bg-paper-wash'}`}>
      <button className="flex min-w-0 flex-1 items-center gap-[9px] border-0 bg-transparent p-0 text-left" onClick={onEdit} title={provider.label || provider.config.model || '未命名连接'}>
        <span className={`h-[7px] w-[7px] flex-none rounded-full ${running ? 'bg-brand-bright' : 'bg-transparent'}`} title={running ? '运行中' : undefined} />
        <span className="min-w-0 flex-1">
          <span className="flex items-center gap-[6px]">
            <span className="min-w-0 truncate text-base font-medium text-ink">{provider.label || provider.config.model || '未命名连接'}</span>
            {dirty && <span className="h-[5px] w-[5px] flex-none rounded-full bg-warning" title="有未保存更改" />}
          </span>
          <span className="mt-[2px] block truncate font-mono text-2xs text-ink-muted">{meta}</span>
          {running && <span className="mt-[1px] block text-2xs text-brand">运行中</span>}
        </span>
      </button>
      <div className="flex flex-none items-center gap-[2px]">
        {!running && (
          <button className="h-[24px] border border-line bg-paper-wash px-[8px] text-xs text-ink-soft opacity-0 transition-opacity hover:border-brand hover:text-brand focus-visible:opacity-100 group-hover:opacity-100" onClick={onUse} title="切换为此连接">使用</button>
        )}
        <button className="grid h-[24px] w-[24px] place-items-center border-0 bg-transparent text-ink-muted opacity-0 transition-opacity hover:text-ink focus-visible:opacity-100 group-hover:opacity-100" aria-label={`更多操作 ${provider.label || ''}`} onClick={onToggleMenu}><MoreHorizontal size={14} /></button>
      </div>
      {menuOpen && (
        <>
          <div className="fixed inset-0 z-[10]" onClick={onCloseMenu} aria-hidden="true" />
          <button className="absolute right-[6px] top-[30px] z-[20] flex items-center gap-[7px] border border-line-strong bg-paper-wash px-[10px] py-[7px] text-xs text-danger shadow-[0_8px_20px_rgba(45,33,20,.12)]" onClick={onDelete}><Trash2 size={13} />删除连接</button>
        </>
      )}
    </div>
  )
}

function hostOf(endpoint?: string): string {
  const value = (endpoint || '').trim()
  if (!value) return ''
  try {
    return new URL(value).host || value
  } catch {
    return value.replace(/^https?:\/\//, '').split('/')[0]
  }
}
