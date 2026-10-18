import { useState } from 'react'
import { MoreHorizontal, Plus, Trash2 } from 'lucide-react'
import { Provider } from '../../../bindings/github.com/no22/RWKV-Agent/api/models'
import { SavedProvider } from '../../../bindings/github.com/no22/RWKV-Agent/internal/appstorage/models'
import { kindOf, type ProviderKind, type ProviderManager } from '../../state/providerManager'
import ConfirmDialog from '../ConfirmDialog'
import { hostOf } from '../../endpoint'
import ProviderEditor from './ProviderEditor'
import { Button } from './ui'
import { derivedProviderLabel } from '../../state/draftValidation'

type Props = {
  kind: ProviderKind
  manager: ProviderManager
  ready: boolean
  onDeleteProvider: (id: string) => void
}

type PendingConfirm =
  | { kind: 'switch'; id: string }
  | { kind: 'new' }
  | { kind: 'delete'; id: string }
  | null

/*
 * 档案管理：左列表 + 右编辑器的主从式布局，只列一类档案（远端连接或本地模型）。
 * 点列表行只是打开详情，没有任何副作用；切换远端连接在对话页的模型标签里做。
 * 脏表单的切换/新建/删除都经确认框。
 */
export default function ConnectionsSection({ kind, manager, ready, onDeleteProvider }: Props) {
  const listed = manager.providers.filter((provider) => kindOf(provider.config) === kind)
  const local = kind === 'local'
  const [menuForID, setMenuForID] = useState('')
  const [confirm, setConfirm] = useState<PendingConfirm>(null)

  /* 离开当前草稿：能自动保存的直接落盘后离开；新建未建档、校验不过或保存失败才问。 */
  async function leaveDraft(next: Exclude<PendingConfirm, null>) {
    if (manager.draftDirty && !(await manager.flushDraft())) {
      setConfirm(next)
      return
    }
    if (next.kind === 'switch') manager.selectProvider(next.id)
    else if (next.kind === 'new') manager.startNewDraft(kind)
  }
  function requestEdit(id: string) {
    setMenuForID('')
    if (id === manager.editingProviderId) return
    void leaveDraft({ kind: 'switch', id })
  }
  function requestNew() {
    setMenuForID('')
    void leaveDraft({ kind: 'new' })
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
    else manager.startNewDraft(kind)
  }

  const deleteTarget = confirm?.kind === 'delete' ? manager.providers.find((provider) => provider.id === confirm.id) : undefined
  const creating = manager.editingProviderId === ''

  function draftAsProvider(saved: SavedProvider): SavedProvider {
    return new SavedProvider({ ...saved, label: manager.draftLabel.trim() || derivedProviderLabel(manager.draftConfigValue), config: manager.draftConfigValue })
  }

  return (
    <div className="flex min-h-0 flex-1">
      <aside className="flex w-[232px] flex-none flex-col border-r border-line bg-paper-sidebar">
        <div className="flex items-center justify-between gap-[6px] py-[10px] pl-[14px] pr-[8px]">
          <span className="font-mono text-2xs font-medium text-ink-muted">{local ? '本地模型' : '已保存连接'} <span className="text-ink-ghost">{listed.length}</span></span>
          <Button variant="ghost" size="sm" icon={<Plus size={13} />} onClick={requestNew}>{local ? '添加模型' : '新建连接'}</Button>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto px-[10px] pb-[8px]">
          {manager.editingProviderId === '' && (
            <div className="mb-[4px] flex items-center gap-[9px] rounded-lg border border-dashed border-line-strong bg-surface-active px-[8px] py-[7px]" aria-current="true">
              <span className="h-[7px] w-[7px] flex-none" />
              <span className="min-w-0 flex-1">
                <span className="block truncate text-base font-medium text-ink">{manager.draftLabel.trim() || (local ? '新本地模型' : '新连接')}</span>
                <span className="mt-[2px] block truncate font-mono text-2xs text-ink-muted">未保存 · 填写后点右上「保存」</span>
              </span>
            </div>
          )}
          {listed.map((provider) => (
            <ProviderRow
              key={provider.id}
              // 正在编辑的行直接显示草稿：改名、换模型时列表同步变化，不等保存落盘。
              provider={provider.id === manager.editingProviderId ? draftAsProvider(provider) : provider}
              running={ready && provider.id === manager.runtimeProviderId}
              selected={provider.id === manager.editingProviderId}
              dirty={provider.id === manager.editingProviderId && manager.draftDirty && (manager.saveState.kind === 'invalid' || manager.saveState.kind === 'error')}
              menuOpen={menuForID === provider.id}
              onToggleMenu={() => setMenuForID(menuForID === provider.id ? '' : provider.id)}
              onCloseMenu={() => setMenuForID('')}
              onEdit={() => requestEdit(provider.id)}
              onDelete={() => requestDelete(provider.id)}
            />
          ))}
          {listed.length === 0 && (
            <p className="px-[6px] py-[8px] text-xs leading-[1.65] text-ink-muted">{local ? '还没有本地模型。在右侧填写模型文件路径并保存，需要时再加载。' : '还没有保存的连接。在右侧填写并保存即可。'}</p>
          )}
        </div>
      </aside>

      <ProviderEditor
        manager={manager}
        ready={ready}
        onTestRemote={() => void manager.testRemote()}
        onSave={() => void manager.saveProviderDraft()}
        onSaveAndUse={() => void manager.saveAndUseProviderDraft()}
        onUnload={() => void manager.unloadModel()}
        onRequestDelete={() => { if (manager.editingProviderId) requestDelete(manager.editingProviderId) }}
      />

      <ConfirmDialog
        open={confirm?.kind === 'switch' || confirm?.kind === 'new'}
        title="有未保存的更改"
        body={`${manager.draftBlockReason || '当前连接档案的更改还没有保存。'}要如何处理？`}
        actions={[
          // 已有档案走到这里说明自动保存失败，再点"保存"也一样失败，只给放弃/取消。
          ...(creating ? [{ label: '保存', variant: 'primary' as const, onClick: () => void resolveConfirm('save') }] : []),
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

function ProviderRow({ provider, running, selected, dirty, menuOpen, onToggleMenu, onCloseMenu, onEdit, onDelete }: {
  provider: SavedProvider
  running: boolean
  selected: boolean
  dirty: boolean
  menuOpen: boolean
  onToggleMenu: () => void
  onCloseMenu: () => void
  onEdit: () => void
  onDelete: () => void
}) {
  const meta = provider.config.provider === Provider.ProviderLocal
    ? `本地模型 · ${provider.config.model.split(/[\\/]/).at(-1) || provider.config.model}`
    : [provider.config.provider === Provider.ProviderChatCompletions ? 'OpenAI 兼容' : provider.config.provider === Provider.ProviderRWKVLightningPython ? 'Lightning Python' : 'Lightning CUDA', hostOf(provider.config.endpoint)].filter(Boolean).join(' · ')
  return (
    <div className={`group relative mb-[4px] flex items-stretch rounded-lg border px-[8px] py-[7px] transition-colors ${selected ? 'border-line-strong bg-surface-active' : 'border-transparent hover:bg-surface-active'}`}>
      <button className="flex min-w-0 flex-1 items-center gap-[9px] border-0 bg-transparent p-0 text-left" onClick={onEdit} title={provider.label || provider.config.model || '未命名连接'}>
        <span className={`h-[7px] w-[7px] flex-none rounded-full ${running ? 'bg-brand-bright' : 'bg-transparent'}`} title={running ? '运行中' : undefined} />
        <span className="min-w-0 flex-1">
          <span className="flex items-center gap-[6px]">
            <span className="min-w-0 truncate text-base font-medium text-ink">{provider.label || provider.config.model || '未命名连接'}</span>
            {dirty && <span className="h-[5px] w-[5px] flex-none rounded-full bg-warning" title="有未保存更改" />}
          </span>
          <span className="mt-[2px] block truncate font-mono text-2xs text-ink-muted">{meta}</span>
          {running && <span className="mt-[1px] block text-2xs text-brand">{provider.config.provider === Provider.ProviderLocal ? '已加载' : '运行中'}</span>}
        </span>
      </button>
      {/* 行上只留「⋯」（删除）：悬停时不再挤掉名称，也没有一碰就切换模型的按钮。 */}
      <div className="flex flex-none items-center">
        <button className="grid h-[24px] w-[24px] place-items-center border-0 bg-transparent text-ink-muted opacity-0 transition-opacity hover:text-ink focus-visible:opacity-100 group-hover:opacity-100" aria-label={`更多操作 ${provider.label || ''}`} onClick={onToggleMenu}><MoreHorizontal size={14} /></button>
      </div>
      {menuOpen && (
        <>
          <div className="fixed inset-0 z-[10]" onClick={onCloseMenu} aria-hidden="true" />
          <div role="menu" className="absolute right-[6px] top-[30px] z-[20] flex min-w-[140px] flex-col rounded-lg border border-line-strong bg-paper-wash p-[4px] shadow-pop">
            <button role="menuitem" className="flex items-center gap-[7px] rounded-md border-0 bg-transparent px-[8px] py-[6px] text-left text-xs text-danger hover:bg-danger-wash" onClick={onDelete}><Trash2 size={13} />删除连接</button>
          </div>
        </>
      )}
    </div>
  )
}

