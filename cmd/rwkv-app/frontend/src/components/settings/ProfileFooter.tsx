import { Trash2 } from 'lucide-react'
import type { ProviderManager } from '../../state/providerManager'

type Props = {
  manager: ProviderManager
  ready: boolean
  onTestRemote: () => void
  onSave: () => void
  onSaveAndUse: () => void
  /** 缺省时隐藏删除键：删除属于连接身份操作，只在连接页提供。 */
  onRequestDelete?: () => void
}

/* 档案动作栏：连接页与 Agent 页共用，底部消息与保存动作在两个分区始终可用。 */
export default function ProfileFooter({ manager, ready, onTestRemote, onSave, onSaveAndUse, onRequestDelete }: Props) {
  const isNew = manager.editingProviderId === ''
  const local = manager.settingsTab === 'local'
  // 已有档案自动保存，不再有「保存」键；主按钮只剩"让它成为运行连接"这一件事。
  const primaryLabel = isNew
    ? '保存并使用'
    : manager.draftNeedsReload
      ? '重新加载模型'
      : manager.draftIsRunning
        ? '使用中'
        : local ? '加载模型' : '使用此连接'
  const primaryDisabled = manager.settingsBusy || (manager.draftIsRunning && !manager.draftNeedsReload) || (!isNew && manager.draftError !== '')
  return (
    <>
      {manager.settingsMessage && (
        <div className="flex-none border-t border-line-soft px-[28px] py-[8px]" role="status" aria-live="polite">
          <span className="block text-xs leading-[1.6] text-ink-muted [overflow-wrap:anywhere]">{manager.settingsMessage}</span>
        </div>
      )}
      <footer className="flex flex-none items-center gap-[10px] border-t border-line bg-paper-soft px-[28px] py-[12px]">
        {onRequestDelete && (
          <button
            className="rounded-md h-[32px] border border-danger bg-transparent px-[12px] text-sm text-danger disabled:opacity-40"
            onClick={onRequestDelete}
            disabled={manager.editingProviderId === '' || manager.settingsBusy}
            aria-label="删除连接"
          ><Trash2 size={13} className="mr-[6px] inline align-[-2px]" />删除连接</button>
        )}
        <span className="flex-1" />
        {manager.settingsTab === 'remote' && (
          <button className="rounded-md h-[32px] border border-line bg-transparent px-[12px] text-sm text-ink disabled:opacity-40" onClick={onTestRemote} disabled={manager.settingsBusy}>测试连接</button>
        )}
        {isNew && (
          <button className="rounded-md h-[32px] border border-line bg-paper-wash px-[13px] text-sm font-medium text-ink shadow-hair transition-colors hover:bg-surface-active disabled:opacity-40" onClick={onSave} disabled={!manager.draftDirty || manager.settingsBusy}>{manager.settingsBusy ? '处理中…' : '保存'}</button>
        )}
        <button className="rounded-md h-[32px] border-0 bg-brand px-[15px] text-sm font-medium text-brand-fg disabled:opacity-40" onClick={onSaveAndUse} disabled={primaryDisabled} title={!isNew && manager.draftError ? manager.draftError : ready ? undefined : '当前未连接，将建立连接'}>{manager.settingsBusy ? '处理中…' : primaryLabel}</button>
      </footer>
    </>
  )
}
