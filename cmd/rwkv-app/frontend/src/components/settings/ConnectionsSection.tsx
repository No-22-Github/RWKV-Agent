import { useState } from 'react'
import { ChevronRight, Plus } from 'lucide-react'
import { Provider } from '../../../bindings/github.com/no22/RWKV-Agent/api/models'
import { SavedProvider } from '../../../bindings/github.com/no22/RWKV-Agent/internal/appstorage/models'
import { kindOf, type ProviderKind, type ProviderManager } from '../../state/providerManager'
import ConfirmDialog from '../ConfirmDialog'
import { hostOf } from '../../endpoint'
import ProviderEditor from './ProviderEditor'
import { Button, Notice, RunningBadge, Section, SettingsPane } from './ui'
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
  | { kind: 'back' }
  | { kind: 'delete'; id: string }
  | null

/*
 * 档案管理分两层：先是整页宽的列表，点一行进入详情（manager.settingsDetail），详情页头的「‹」回到列表。
 * 只列一类档案（远端连接或本地模型）。点列表行只是打开详情，没有任何副作用；切换远端连接在对话页的模型标签里做。
 * 离开详情（返回、换档案、新建）前先把草稿落盘，落不了盘的经确认框。
 */
export default function ConnectionsSection({ kind, manager, ready, onDeleteProvider }: Props) {
  const listed = manager.providers.filter((provider) => kindOf(provider.config) === kind)
  const local = kind === 'local'
  const [confirm, setConfirm] = useState<PendingConfirm>(null)

  function go(next: Exclude<PendingConfirm, null | { kind: 'delete' }>) {
    if (next.kind === 'switch') manager.selectProvider(next.id)
    else if (next.kind === 'new') manager.startNewDraft(kind)
    manager.setSettingsDetail(next.kind !== 'back')
  }

  /* 离开当前草稿：能自动保存的直接落盘后离开；新建未建档、校验不过或保存失败才问。 */
  async function leaveDraft(next: Exclude<PendingConfirm, null | { kind: 'delete' }>) {
    if (manager.draftDirty && !(await manager.flushDraft())) {
      setConfirm(next)
      return
    }
    go(next)
  }
  function requestEdit(id: string) {
    if (id === manager.editingProviderId) manager.setSettingsDetail(true)
    else void leaveDraft({ kind: 'switch', id })
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
    go(pending)
  }

  const deleteTarget = confirm?.kind === 'delete' ? manager.providers.find((provider) => provider.id === confirm.id) : undefined
  const creating = manager.editingProviderId === ''

  function draftAsProvider(saved: SavedProvider): SavedProvider {
    return new SavedProvider({ ...saved, label: manager.draftLabel.trim() || derivedProviderLabel(manager.draftConfigValue), config: manager.draftConfigValue })
  }

  return (
    <div className="flex min-h-0 min-w-0 flex-1">
      {manager.settingsDetail ? (
        <ProviderEditor
          manager={manager}
          ready={ready}
          backLabel={local ? '本地模型' : '远端连接'}
          onBack={() => void leaveDraft({ kind: 'back' })}
          onTestRemote={() => void manager.testRemote()}
          onSave={() => void manager.saveProviderDraft()}
          onSaveAndUse={() => void manager.saveAndUseProviderDraft()}
          onUnload={() => void manager.unloadModel()}
          onRequestDelete={() => { if (manager.editingProviderId) setConfirm({ kind: 'delete', id: manager.editingProviderId }) }}
        />
      ) : (
        <SettingsPane>
          {manager.settingsMessage && <Notice>{manager.settingsMessage}</Notice>}
          <Section
            title={local ? '本地模型' : '远端连接'}
            action={<Button size="sm" icon={<Plus size={14} />} onClick={() => void leaveDraft({ kind: 'new' })}>{local ? '添加模型' : '新建连接'}</Button>}
          >
            <div role="list" aria-label={local ? '本地模型列表' : '远端连接列表'}>
            {listed.map((provider) => (
              <ProviderRow
                key={provider.id}
                // 正在编辑的行直接显示草稿：改名、换模型后回到列表立刻看到，不等保存落盘。
                provider={provider.id === manager.editingProviderId ? draftAsProvider(provider) : provider}
                running={ready && provider.id === manager.runtimeProviderId}
                attention={provider.id === manager.editingProviderId && manager.draftDirty && (manager.saveState.kind === 'invalid' || manager.saveState.kind === 'error')}
                onEdit={() => requestEdit(provider.id)}
              />
            ))}
            </div>
            {listed.length === 0 && (
              <p className="m-0 py-[14px] text-sm text-ink-muted">{local ? '还没有本地模型。' : '还没有远端连接。'}</p>
            )}
          </Section>
        </SettingsPane>
      )}

      <ConfirmDialog
        open={confirm !== null && confirm.kind !== 'delete'}
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
        title={local ? '删除模型' : '删除连接'}
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

/* 列表行：名称 + 一行协议与地址，右侧是运行状态和进入详情的箭头。整行可点。 */
function ProviderRow({ provider, running, attention, onEdit }: {
  provider: SavedProvider
  running: boolean
  attention: boolean
  onEdit: () => void
}) {
  const isLocal = provider.config.provider === Provider.ProviderLocal
  const meta = isLocal
    ? provider.config.model.split(/[\\/]/).at(-1) || provider.config.model
    : [provider.config.provider === Provider.ProviderChatCompletions ? 'OpenAI 兼容' : provider.config.provider === Provider.ProviderRWKVLightningPython ? 'Lightning Python' : 'Lightning CUDA', hostOf(provider.config.endpoint)].filter(Boolean).join(' · ')
  const name = provider.label || provider.config.model || '未命名连接'
  // 自动命名的连接名里已经带了主机名，副标题只留协议，不把同一个地址念两遍。
  const host = hostOf(provider.config.endpoint)
  const subtitle = !isLocal && host && name.includes(host) ? meta.replace(` · ${host}`, '') : meta
  return (
    <div role="listitem" className="border-b border-line-soft last:border-b-0">
    <button
      className="group flex min-h-[56px] w-full items-center gap-[16px] border-0 bg-transparent px-0 py-[10px] text-left"
      onClick={onEdit}
      title={name}
    >
      <span className="flex min-w-0 flex-1 flex-col gap-[2px]">
        <span className="flex min-w-0 items-center gap-[6px]">
          <span className="min-w-0 truncate text-base text-ink group-hover:underline group-hover:decoration-line-strong group-hover:underline-offset-[3px]">{name}</span>
          {attention && <span className="h-[6px] w-[6px] flex-none rounded-full bg-warning" title="有未保存更改" />}
        </span>
        <span className="truncate text-sm text-ink-muted">{subtitle}</span>
      </span>
      {running && <RunningBadge>{isLocal ? '已加载' : '运行中'}</RunningBadge>}
      <ChevronRight size={15} className="flex-none text-ink-ghost transition-colors group-hover:text-ink-muted" />
    </button>
    </div>
  )
}
