import { useEffect, useMemo, useState } from 'react'
import { Trash2 } from 'lucide-react'
import * as Backend from '../../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import type { AppBootstrap, ConversationSummary } from '../../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/models'
import ConfirmDialog from '../ConfirmDialog'
import { Select } from './Select'
import { Button, Notice, Row, Section, Segmented, SettingsPane, Toggle } from './ui'

type Age = '7' | '30' | '90' | 'all'

const AGE_OPTIONS: { value: Age; label: string }[] = [
  { value: '7', label: '7 天前' },
  { value: '30', label: '30 天前' },
  { value: '90', label: '90 天前' },
  { value: 'all', label: '全部' },
]
const DAY_MS = 24 * 60 * 60 * 1000
const ALL_WORKSPACES = ''

/*
 * 对话记录：按「范围 + 早于多久」一次清掉陈旧对话。
 * 列的是磁盘上的全部对话，包括已经从侧栏移除的工作区里留下的；置顶默认不动。
 * 命中的对话先全部列出、默认全选，可以逐条取消，删之前看得见删的是什么。
 */
export default function ConversationsSection({ onChanged }: { onChanged: (value: AppBootstrap) => void }) {
  const [all, setAll] = useState<ConversationSummary[] | null>(null)
  const [error, setError] = useState('')
  const [workspace, setWorkspace] = useState(ALL_WORKSPACES)
  const [age, setAge] = useState<Age>('30')
  const [keepPinned, setKeepPinned] = useState(true)
  const [excluded, setExcluded] = useState<Set<string>>(() => new Set())
  const [confirming, setConfirming] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [done, setDone] = useState('')

  useEffect(() => {
    Backend.ListAllConversations().then((value) => setAll(value || [])).catch((reason) => setError(String(reason?.message ?? reason)))
  }, [])

  const workspaceOptions = useMemo(() => {
    const counts = new Map<string, number>()
    for (const conversation of all || []) counts.set(conversation.workspace, (counts.get(conversation.workspace) || 0) + 1)
    return [
      { value: ALL_WORKSPACES, label: `全部工作区（${all?.length ?? 0}）` },
      ...[...counts].sort((a, b) => b[1] - a[1]).map(([path, count]) => ({ value: path, label: `${baseName(path)}（${count}）`, hint: path })),
    ]
  }, [all])

  const matched = useMemo(() => {
    const cutoff = age === 'all' ? Infinity : Date.now() - Number(age) * DAY_MS
    return (all || []).filter((conversation) =>
      (workspace === ALL_WORKSPACES || conversation.workspace === workspace)
      && !(keepPinned && conversation.pinned)
      && new Date(conversation.updatedAt).getTime() < cutoff)
  }, [all, workspace, age, keepPinned])
  const selected = matched.filter((conversation) => !excluded.has(conversation.id))

  function toggle(id: string) {
    setExcluded((current) => { const next = new Set(current); if (next.has(id)) next.delete(id); else next.add(id); return next })
  }
  function toggleAll() {
    setExcluded(selected.length === matched.length ? new Set(matched.map((conversation) => conversation.id)) : new Set())
  }
  async function deleteSelected() {
    setConfirming(false)
    setDeleting(true)
    const ids = selected.map((conversation) => conversation.id)
    try {
      const value = await Backend.DeleteConversations(ids)
      onChanged(value)
      setAll((current) => (current || []).filter((conversation) => !ids.includes(conversation.id)))
      setExcluded(new Set())
      setDone(`已删除 ${ids.length} 条对话。`)
    } catch (reason) {
      setError(String((reason as Error)?.message ?? reason))
    } finally {
      setDeleting(false)
    }
  }

  return (
    <SettingsPane>
      <Section title="清理对话">
        {done && <Notice>{done}</Notice>}
        {error && <Notice tone="warning">{error}</Notice>}
        <Row label="范围" description="包括已从侧栏移除的工作区里留下的对话">
          <Select label="清理范围" className="w-[260px]" value={workspace} onChange={setWorkspace} options={workspaceOptions} />
        </Row>
        <Row label="最后更新早于">
          <Segmented label="最后更新早于" value={age} onChange={setAge} options={AGE_OPTIONS} />
        </Row>
        <Toggle label="保留置顶对话" checked={keepPinned} onChange={setKeepPinned} />
      </Section>

      <Section
        title={all === null ? '读取中…' : `符合条件 ${matched.length} 条，已选 ${selected.length} 条`}
        action={<Button size="sm" variant="danger" icon={<Trash2 size={13} />} disabled={selected.length === 0 || deleting} onClick={() => { setDone(''); setConfirming(true) }}>{deleting ? '删除中…' : '删除所选'}</Button>}
      >
        {all !== null && matched.length === 0 && <p className="m-0 py-[14px] text-sm text-ink-muted">没有符合条件的对话。</p>}
        {matched.length > 0 && (
          <div className="mt-[8px] overflow-hidden rounded-lg border border-line">
            <label className="flex h-[36px] cursor-pointer items-center gap-[10px] border-b border-line bg-paper-soft px-[12px] text-sm text-ink-soft">
              <input type="checkbox" aria-label="全选" className="accent-brand" checked={selected.length === matched.length} ref={(element) => { if (element) element.indeterminate = selected.length > 0 && selected.length < matched.length }} onChange={toggleAll} />
              全选
            </label>
            <ul role="list" aria-label="将删除的对话" className="m-0 max-h-[360px] list-none overflow-y-auto p-0">
              {matched.map((conversation) => (
                <li key={conversation.id} className="border-b border-line-soft last:border-b-0">
                  <label className="flex min-h-[40px] cursor-pointer items-center gap-[10px] px-[12px] py-[6px] hover:bg-surface-active">
                    <input type="checkbox" aria-label={conversation.title || '未命名会话'} className="flex-none accent-brand" checked={!excluded.has(conversation.id)} onChange={() => toggle(conversation.id)} />
                    <span className="min-w-0 flex-1 truncate text-sm text-ink" title={conversation.title}>{conversation.title || '未命名会话'}</span>
                    {workspace === ALL_WORKSPACES && <span className="max-w-[140px] flex-none truncate text-2xs text-ink-muted" title={conversation.workspace}>{baseName(conversation.workspace)}</span>}
                    <span className="w-[64px] flex-none text-right text-2xs tabular-nums text-ink-muted">{relativeTime(conversation.updatedAt)}</span>
                  </label>
                </li>
              ))}
            </ul>
          </div>
        )}
      </Section>

      <ConfirmDialog
        open={confirming}
        title="删除对话"
        body={`将删除所选的 ${selected.length} 条对话及其全部消息，此操作无法撤销。`}
        actions={[
          { label: '取消', onClick: () => setConfirming(false) },
          { label: `删除 ${selected.length} 条`, variant: 'danger', onClick: () => void deleteSelected() },
        ]}
        onClose={() => setConfirming(false)}
      />
    </SettingsPane>
  )
}

function baseName(path: string) {
  return path.split(/[\\/]/).filter(Boolean).at(-1) || path || '未知工作区'
}

function relativeTime(value: string) {
  const elapsed = Math.max(0, Date.now() - new Date(value).getTime())
  if (!Number.isFinite(elapsed)) return ''
  const days = Math.floor(elapsed / DAY_MS)
  if (days >= 1) return `${days} 天前`
  const hours = Math.floor(elapsed / (60 * 60 * 1000))
  return hours >= 1 ? `${hours} 小时前` : '刚刚'
}
