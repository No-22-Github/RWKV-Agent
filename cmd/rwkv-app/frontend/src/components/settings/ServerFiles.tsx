import { useRef, type ReactNode } from 'react'
import { Check, RefreshCw, Trash2, Upload } from 'lucide-react'
import { Button } from './ui'

export type ServerFileItem = { id: string; title: string; meta: string; metaTitle?: string }
export type MissingFileItem = { id: string; title: string; canReupload: boolean }
/* sent 是已发送字节数（来自后端进度事件），用来算上传速度。 */
export type UploadingFile = { name: string; percent: number; sent?: number }

/*
 * State 与适配器（MiSS / NoRA）共用的服务器文件面板（放在连接详情「高级」的折叠行里）：
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
  upload: { ready: boolean; busy: boolean; loading: boolean; uploading: UploadingFile | null; error: string; notice: string; onUpload: () => void; onRefresh: () => void }
}) {
  const speed = useUploadSpeed(upload.uploading)
  const status = !upload.ready ? '先填写 API 地址'
    : upload.uploading ? [`正在上传 ${upload.uploading.name}`, `${upload.uploading.percent}%`, speed].filter(Boolean).join(' · ')
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
              <Button size="sm" variant="ghost" square className="hover:text-danger" aria-label={`删除${spaced(noun)} ${entry.id}`} title="从服务器删除" onClick={() => onDelete(entry.id)}><Trash2 size={14} /></Button>
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
        <Button size="sm" variant="ghost" square disabled={!upload.ready || upload.busy} onClick={upload.onRefresh} aria-label={`刷新${spaced(noun)}列表`} title="刷新"><RefreshCw size={13} className={upload.loading ? 'animate-spin' : ''} /></Button>
        <span role="status" aria-live="polite" className={`min-w-0 flex-1 truncate text-right text-sm ${upload.error ? 'text-danger' : 'text-ink-muted'}`} title={upload.error || status || undefined}>{upload.error || status}</span>
      </div>
      {upload.uploading && (
        <div className="mt-[8px] h-[3px] w-full overflow-hidden rounded-full bg-line-soft"><div className="h-full bg-brand transition-[width] duration-200" style={{ width: `${upload.uploading.percent}%` }} /></div>
      )}
    </div>
  )
}

const SPEED_WINDOW_MS = 3000

/*
 * 上传速度：取最近 SPEED_WINDOW_MS 内的字节增量，比从头平均更跟得上网速变化。
 * 进度事件按百分比节流（每 1% 一次），所以窗口里不足半秒时先不显示，免得开头一跳一跳。
 */
function useUploadSpeed(uploading: UploadingFile | null): string {
  const samples = useRef<{ name: string; points: { at: number; sent: number }[] }>({ name: '', points: [] })
  if (!uploading || uploading.sent === undefined) {
    if (!uploading) samples.current = { name: '', points: [] }
    return ''
  }
  const now = performance.now()
  if (samples.current.name !== uploading.name) samples.current = { name: uploading.name, points: [] }
  const points = samples.current.points
  if (points.at(-1)?.sent !== uploading.sent) points.push({ at: now, sent: uploading.sent })
  while (points.length > 2 && now - points[0].at > SPEED_WINDOW_MS) points.shift()
  const first = points[0], last = points.at(-1)!
  const elapsed = last.at - first.at
  if (elapsed < 500) return ''
  return `${formatBytes(((last.sent - first.sent) * 1000) / elapsed)}/s`
}

export function formatBytes(bytes: number): string {
  if (bytes >= 1 << 30) return `${(bytes / (1 << 30)).toFixed(1)} GB`
  if (bytes >= 1 << 20) return `${(bytes / (1 << 20)).toFixed(1)} MB`
  if (bytes >= 1 << 10) return `${Math.round(bytes / (1 << 10))} KB`
  return `${Math.round(bytes)} B`
}

/* 选中的文件已不在服务器上（多半是服务端重启清空了）：一条警告 + 重新上传 / 改回不用。 */
export function MissingCurrent({ children, actions }: { children: ReactNode; actions: ReactNode }) {
  return (
    <div role="alert" className="mb-[8px] rounded-md border border-warning/40 bg-paper px-[12px] py-[8px] text-sm leading-[1.6] text-ink-soft">
      <p className="m-0">{children}</p>
      <div className="mt-[6px] flex flex-wrap gap-[8px]">{actions}</div>
    </div>
  )
}
