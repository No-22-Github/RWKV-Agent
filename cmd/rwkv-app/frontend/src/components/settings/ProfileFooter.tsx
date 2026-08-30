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
  return (
    <>
      {manager.settingsMessage && (
        <div className="flex-none border-t border-line-soft px-[28px] py-[8px]">
          <span className="block truncate text-xs text-ink-muted" title={manager.settingsMessage}>{manager.settingsMessage}</span>
        </div>
      )}
      <footer className="flex flex-none items-center gap-[10px] border-t border-line bg-paper-soft px-[28px] py-[12px]">
        {onRequestDelete && (
          <button
            className="h-[32px] border border-danger bg-transparent px-[12px] text-sm text-danger disabled:opacity-40"
            onClick={onRequestDelete}
            disabled={manager.editingProviderId === '' || manager.settingsBusy}
            aria-label="删除连接"
          ><Trash2 size={13} className="mr-[6px] inline align-[-2px]" />删除连接</button>
        )}
        <span className="flex-1" />
        {manager.settingsTab === 'remote' && (
          <button className="h-[32px] border border-line bg-transparent px-[12px] text-sm text-ink disabled:opacity-40" onClick={onTestRemote} disabled={manager.settingsBusy}>测试连接</button>
        )}
        <button className="h-[32px] border border-ink bg-transparent px-[13px] text-sm font-medium text-ink disabled:opacity-40" onClick={onSave} disabled={!manager.draftDirty || manager.settingsBusy}>{manager.settingsBusy ? '处理中…' : '保存'}</button>
        <button className="h-[32px] border-0 bg-brand px-[15px] text-sm font-medium text-white disabled:opacity-40" onClick={onSaveAndUse} disabled={manager.draftIsRunning || manager.settingsBusy} title={ready ? undefined : '当前未连接，保存后将建立连接'}>{manager.settingsBusy ? '处理中…' : '保存并使用'}</button>
      </footer>
    </>
  )
}
