import type { ReactNode } from 'react'
import { Check, RefreshCw, Trash2, Upload } from 'lucide-react'
import { Button } from './ui'

export type ServerFileItem = { id: string; title: string; meta: string; metaTitle?: string }
export type MissingFileItem = { id: string; title: string; canReupload: boolean }

/*
 * State 与 MiSS 适配器共用的服务器文件面板（放在连接详情「高级」的折叠行里）：
 * 文件一行一个，右侧是使用/停用与删除；底部一行是上传、刷新和一句临时状态。
 * 「只对本次运行有效」这类常驻说明写在折叠行的摘要里，这里不再重复。
 *
 * 使用/停用只在这个连接正在运行时出现：选择不进档案，平时在对话页的标签里选。
 */
/* 英文名词前后留空格，中文不留："还没有 State" / "还没有适配器"。 */
function spaced(noun: string) {
  return /^[A-Za-z]/.test(noun) ? ` ${noun}` : noun
}

export function ServerFiles({ noun, items, missing, current, selectable, alert, onUse, onDelete, onReupload, onForget, upload }: {
  noun: string
  items: ServerFileItem[]
  missing: MissingFileItem[]
  current: string
  selectable: boolean
  alert?: ReactNode
  onUse: (id: string) => void
  onDelete: (id: string) => void
  onReupload: (id: string) => void
  onForget: (id: string) => void
  upload: { ready: boolean; busy: boolean; loading: boolean; uploading: { name: string; percent: number } | null; error: string; notice: string; onUpload: () => void; onRefresh: () => void }
}) {
  const status = !upload.ready ? '先填写 API 地址'
    : upload.uploading ? `正在上传 ${upload.uploading.name} · ${upload.uploading.percent}%`
      : upload.loading ? '正在读取…'
        : upload.notice
  return (
    <div>
      {alert}
      <ul aria-label={`服务器上的${spaced(noun)}`} className="m-0 list-none p-0">
        {items.map((entry) => {
          const selected = entry.id === current
          return (
            <li key={entry.id} className="flex min-h-[48px] items-center gap-[12px] border-b border-line-soft py-[8px] last:border-b-0">
              <div className="flex min-w-0 flex-1 flex-col gap-[1px]">
                <span className="flex min-w-0 items-center gap-[6px] text-base text-ink">
                  <span className="truncate">{entry.title}</span>
                  {selected && <Check size={13} className="flex-none text-ink" aria-label="使用中" />}
                </span>
                <span className="truncate text-sm text-ink-muted" title={entry.metaTitle}>{entry.meta}</span>
              </div>
              {selectable && (selected
                ? <Button size="sm" variant="ghost" onClick={() => onUse('')}>停用</Button>
                : <Button size="sm" onClick={() => onUse(entry.id)}>使用</Button>)}
              <Button size="sm" variant="ghost" className="w-[28px] px-0 hover:text-danger" aria-label={`删除${spaced(noun)} ${entry.id}`} title="从服务器删除" onClick={() => onDelete(entry.id)}><Trash2 size={14} /></Button>
            </li>
          )
        })}
        {items.length === 0 && upload.ready && !upload.loading && (
          <li className="py-[10px] text-sm text-ink-muted">服务器上还没有{spaced(noun)}</li>
        )}
      </ul>

      {missing.length > 0 && (
        <details className="mt-[4px] text-sm text-ink-muted">
          <summary className="cursor-pointer select-none py-[6px]">本机上传过、服务器上已不存在 {missing.length} 个</summary>
          <ul className="m-0 list-none p-0">
            {missing.map((entry) => (
              <li key={entry.id} className="flex items-center gap-[8px] py-[4px]">
                <span className="min-w-0 flex-1 truncate">{entry.title}{entry.canReupload ? '' : ' · 本地文件已不存在'}</span>
                {entry.canReupload && <Button size="sm" variant="ghost" disabled={upload.busy} onClick={() => onReupload(entry.id)}>重新上传</Button>}
                <Button size="sm" variant="ghost" onClick={() => onForget(entry.id)}>忘记</Button>
              </li>
            ))}
          </ul>
        </details>
      )}

      <div className="mt-[6px] flex items-center gap-[6px] border-t border-line-soft pt-[10px]">
        <Button size="sm" icon={<Upload size={13} />} disabled={!upload.ready || upload.busy} onClick={upload.onUpload}>上传 .pth…</Button>
        <Button size="sm" variant="ghost" className="w-[28px] px-0" disabled={!upload.ready || upload.busy} onClick={upload.onRefresh} aria-label={`刷新${spaced(noun)}列表`} title="刷新"><RefreshCw size={13} className={upload.loading ? 'animate-spin' : ''} /></Button>
        <span role="status" aria-live="polite" className={`min-w-0 flex-1 truncate text-right text-sm ${upload.error ? 'text-danger' : 'text-ink-muted'}`} title={upload.error || status || undefined}>{upload.error || status}</span>
      </div>
      {upload.uploading && (
        <div className="mt-[8px] h-[3px] w-full overflow-hidden rounded-full bg-line-soft"><div className="h-full bg-brand transition-[width] duration-200" style={{ width: `${upload.uploading.percent}%` }} /></div>
      )}
    </div>
  )
}

/* 选中的文件已不在服务器上（多半是服务端重启清空了）：一条警告 + 重新上传 / 改回不用。 */
export function MissingCurrent({ children, actions }: { children: ReactNode; actions: ReactNode }) {
  return (
    <div role="alert" className="mb-[8px] rounded-md border border-warning/40 bg-paper px-[10px] py-[8px] text-sm leading-[1.6] text-ink-soft">
      <p className="m-0">{children}</p>
      <div className="mt-[6px] flex flex-wrap gap-[8px]">{actions}</div>
    </div>
  )
}
