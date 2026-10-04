import { useEffect, useRef, useState } from 'react'
import { Events } from '@wailsio/runtime'
import { Check, RefreshCw, RotateCcw, Trash2, Upload } from 'lucide-react'
import type { ProviderManager } from '../../state/providerManager'
import type { StateEntry, StateListing } from '../../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/models'
import * as Backend from '../../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import ConfirmDialog from '../ConfirmDialog'
import { Field, GroupTitle } from './ui'

type Props = { manager: ProviderManager }

type PendingDelete = { entry: StateEntry; serverSide: boolean }

// 与后端 StateUploadProgress 对应（事件载荷不进绑定生成）。
type StateUploadProgress = { path: string; sent: number; total: number }

/*
 * 连接档案的 State 分组（仅 RWKV Lightning CUDA）。State 存在部署进程的临时目录里：
 * 整台部署共享、服务端重启即清空。所以这里同时展示服务器列表与本机上传记录，
 * 当前选中的 State 不在服务器上时给出一键重传。
 */
export default function StateSection({ manager }: Props) {
  const [listing, setListing] = useState<StateListing | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [uploading, setUploading] = useState<{ name: string; percent: number } | null>(null)
  const [manualPath, setManualPath] = useState<string | null>(null)
  const [pendingDelete, setPendingDelete] = useState<PendingDelete | null>(null)
  const requestRef = useRef(0)

  const config = manager.draftConfigValue
  const endpointReady = manager.remoteEndpoint.trim() !== '' && !manager.draftErrors.endpoint
  // 只有影响连通性的字段变化才重新拉列表，改采样或选 State 不触发。
  const connectionKey = JSON.stringify([manager.remoteEndpoint.trim(), manager.apiKey.trim(), manager.headers.map((row) => [row.name.trim(), row.value.trim()])])

  async function refresh() {
    if (!endpointReady) return
    const request = ++requestRef.current
    setLoading(true)
    setError('')
    try {
      const value = await Backend.ListStates(config)
      if (request === requestRef.current) setListing(value)
    } catch (reason) {
      if (request === requestRef.current) { setListing(null); setError(errorText(reason)) }
    } finally {
      if (request === requestRef.current) setLoading(false)
    }
  }

  useEffect(() => {
    setListing(null)
    if (!endpointReady) return
    const timer = setTimeout(() => { void refresh() }, 500)
    return () => clearTimeout(timer)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [connectionKey, endpointReady])

  useEffect(() => {
    const off = Events.On('state:upload-progress', (event) => {
      const value = event.data as StateUploadProgress
      setUploading({ name: baseName(value.path), percent: value.total > 0 ? Math.round((value.sent * 100) / value.total) : 0 })
    })
    return () => { off() }
  }, [])

  async function upload(path: string, replacing?: string) {
    const trimmed = path.trim()
    if (!trimmed) return
    setUploading({ name: baseName(trimmed), percent: 0 })
    setError('')
    setNotice('')
    try {
      const entry = await Backend.UploadState(config, trimmed)
      if (replacing) {
        // 旧 id 已随服务端重启失效，只清本机记录，不再请求服务器。
        await Backend.DeleteState(config, replacing, false).catch(() => undefined)
      }
      if (!replacing || manager.stateId === replacing) manager.setStateId(entry.id)
      setManualPath(null)
      setNotice(replacing ? `已重新上传，新 State：${entry.id}` : `上传完成并已选用：${entry.id}`)
      await refresh()
    } catch (reason) {
      setError(errorText(reason))
    } finally {
      setUploading(null)
    }
  }

  async function chooseAndUpload() {
    try {
      const path = await Backend.ChooseStateFile()
      if (path) await upload(path)
    } catch {
      // 浏览器模式没有原生文件对话框：退回手填路径（服务进程与文件在同一台机器上）。
      setManualPath((current) => current ?? '')
    }
  }

  async function confirmDelete() {
    if (!pendingDelete) return
    const { entry, serverSide } = pendingDelete
    setPendingDelete(null)
    setError('')
    try {
      await Backend.DeleteState(config, entry.id, serverSide)
      if (serverSide && manager.stateId === entry.id) manager.setStateId('')
      setNotice(serverSide ? `已从服务器删除 ${entry.id}` : `已忘记 ${entry.id} 的本机记录`)
      await refresh()
    } catch (reason) {
      setError(errorText(reason))
    }
  }

  const states = listing?.states || []
  const missing = listing?.missing || []
  const current = manager.stateId.trim()
  const currentOnServer = states.some((entry) => entry.id === current)
  const currentMissing = Boolean(listing) && current !== '' && !currentOnServer
  const currentRecord = missing.find((entry) => entry.id === current)
  const busy = loading || uploading !== null

  return (
    <section className="pb-[24px]">
      <GroupTitle title="State" hint="仅 CUDA 协议 · 整台部署共享 · 服务端重启后清空" />

      <label className="mt-[8px] flex flex-col gap-[6px] text-xs text-ink-muted">
        当前 State
        <select
          aria-label="当前 State"
          className="h-[40px] border border-line bg-paper-wash px-[10px] text-base text-ink outline-0 focus:border-brand"
          value={current}
          onChange={(event) => manager.setStateId(event.target.value)}
        >
          <option value="">零状态（不使用 State）</option>
          {states.map((entry) => <option key={entry.id} value={entry.id}>{stateLabel(entry)}</option>)}
          {current !== '' && !currentOnServer && <option value={current}>{currentRecord ? stateLabel(currentRecord) : current}{listing ? '（服务器上已不存在）' : ''}</option>}
        </select>
      </label>

      {currentMissing && (
        <div role="alert" className="mt-[10px] border-l-2 border-warning bg-paper-soft px-[10px] py-[8px] text-xs leading-[1.65] text-ink-soft">
          <p className="m-0">State <span className="font-mono">{current}</span> 已不在服务器上，通常是服务端重启清空了上传目录。连接时会被拒绝。</p>
          <div className="mt-[7px] flex flex-wrap gap-[8px]">
            {currentRecord?.localAvailable && currentRecord.localPath && (
              <button className="flex h-[28px] items-center gap-[5px] border-0 bg-brand px-[10px] text-xs text-white disabled:opacity-60" disabled={busy} onClick={() => void upload(currentRecord.localPath!, current)}>
                <RotateCcw size={12} />重新上传 {baseName(currentRecord.localPath)}
              </button>
            )}
            <button className="h-[28px] border border-line bg-transparent px-[10px] text-xs text-ink" onClick={() => manager.setStateId('')}>改回零状态</button>
          </div>
          {currentRecord && !currentRecord.localAvailable && currentRecord.localPath && <p className="mb-0 mt-[6px] text-ink-muted">本机记录的文件已找不到：<span className="font-mono">{currentRecord.localPath}</span></p>}
        </div>
      )}

      <div className="mt-[12px] flex items-center gap-[8px]">
        <button className="flex h-[32px] items-center gap-[6px] border border-line bg-paper-wash px-[11px] text-sm text-ink disabled:opacity-50" disabled={!endpointReady || busy} onClick={() => void chooseAndUpload()}>
          <Upload size={14} />上传 .pth…
        </button>
        <button className="flex h-[32px] items-center gap-[6px] border-0 bg-transparent px-[6px] text-sm text-brand disabled:opacity-50" disabled={!endpointReady || busy} onClick={() => void refresh()} aria-label="刷新 State 列表">
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />刷新
        </button>
        <span role="status" aria-live="polite" className="min-w-0 flex-1 truncate text-right text-xs text-ink-muted">
          {!endpointReady ? '先填写 API 地址' : uploading ? `正在上传 ${uploading.name} · ${uploading.percent}%` : loading ? '正在读取服务器列表…' : listing ? `服务器上共 ${states.length} 个 State` : ''}
        </span>
      </div>
      {uploading && (
        <div className="mt-[6px] h-[3px] w-full bg-line-soft"><div className="h-full bg-brand transition-[width] duration-200" style={{ width: `${uploading.percent}%` }} /></div>
      )}

      {manualPath !== null && (
        <div className="mt-[6px] flex items-end gap-[8px]">
          <div className="flex-1"><Field label="State 文件路径（服务进程所在机器上的绝对路径）" value={manualPath} onChange={setManualPath} placeholder="/path/to/state.pth" /></div>
          <button className="mb-[6px] h-[40px] border-0 bg-brand px-[14px] text-sm text-white disabled:opacity-50" disabled={!manualPath.trim() || busy} onClick={() => void upload(manualPath)}>上传</button>
        </div>
      )}

      {error && <p role="alert" className="mb-0 mt-[8px] text-xs leading-[1.6] text-danger">{error}</p>}
      {notice && !error && <p className="mb-0 mt-[8px] text-xs text-brand">{notice}</p>}

      {states.length > 0 && (
        <ul aria-label="服务器上的 State" className="m-0 mt-[12px] list-none border-t border-line-soft p-0">
          {states.map((entry) => {
            const selected = entry.id === current
            return (
              <li key={entry.id} className={`flex items-center gap-[10px] border-b border-line-soft px-[4px] py-[9px] ${selected ? 'bg-brand-wash' : ''}`}>
                <div className="flex min-w-0 flex-1 flex-col gap-[2px]">
                  <span className="flex min-w-0 items-baseline gap-[8px]">
                    <span className="truncate text-sm font-medium text-ink">{entry.filename || '（无文件名）'}</span>
                    {entry.id !== entry.filename && <span className="flex-none font-mono text-2xs text-ink-muted">{entry.id}</span>}
                  </span>
                  <span className="truncate text-2xs text-ink-muted" title={entry.localPath || undefined}>
                    {formatBytes(entry.sizeBytes)} · {entry.tensorCount} tensors · {formatTime(entry.created)}{entry.localPath ? ` · 本机上传：${entry.localPath}` : ''}
                  </span>
                </div>
                {selected ? (
                  <span className="flex flex-none items-center gap-[4px] text-xs text-brand"><Check size={12} />使用中</span>
                ) : (
                  <button className="flex-none border-0 bg-transparent px-[6px] text-xs text-brand" onClick={() => manager.setStateId(entry.id)}>使用</button>
                )}
                <button className="grid h-[28px] w-[28px] flex-none place-items-center border-0 bg-transparent text-ink-muted hover:text-danger" aria-label={`删除 State ${entry.id}`} title="从服务器删除" onClick={() => setPendingDelete({ entry, serverSide: true })}><Trash2 size={14} /></button>
              </li>
            )
          })}
        </ul>
      )}

      {missing.length > 0 && (
        <details className="mt-[12px] text-xs text-ink-muted">
          <summary className="cursor-pointer select-none">本机上传过、服务器上已不存在（{missing.length}）</summary>
          <ul className="m-0 mt-[6px] list-none p-0">
            {missing.map((entry) => (
              <li key={entry.id} className="flex items-center gap-[10px] border-b border-line-soft px-[4px] py-[7px]">
                <span className="min-w-0 flex-1 truncate" title={entry.localPath || undefined}>
                  <span className="font-mono">{entry.id}</span> · {entry.filename}{entry.localAvailable ? '' : ' · 本地文件已不存在'}
                </span>
                {entry.localAvailable && entry.localPath && (
                  <button className="flex-none border-0 bg-transparent px-[6px] text-xs text-brand disabled:opacity-50" disabled={busy} onClick={() => void upload(entry.localPath!, entry.id)}>重新上传</button>
                )}
                <button className="flex-none border-0 bg-transparent px-[6px] text-xs text-ink-muted" onClick={() => setPendingDelete({ entry, serverSide: false })}>忘记</button>
              </li>
            ))}
          </ul>
        </details>
      )}

      <ConfirmDialog
        open={pendingDelete !== null}
        title={pendingDelete?.serverSide ? '从服务器删除这个 State？' : '忘记这条本机记录？'}
        body={pendingDelete?.serverSide
          ? `${pendingDelete.entry.filename || pendingDelete.entry.id}（${pendingDelete.entry.id}）会从整台部署上删除，正在使用它的其他人和其他连接也会受影响，无法撤销。`
          : '只删除本机的上传记录，不影响服务器。'}
        actions={[
          { label: '取消', onClick: () => setPendingDelete(null) },
          { label: pendingDelete?.serverSide ? '删除' : '忘记', variant: 'danger', onClick: () => void confirmDelete() },
        ]}
        onClose={() => setPendingDelete(null)}
      />
    </section>
  )
}

/* 部分部署直接用文件名当 state_id，两者相同时只显示一次。 */
function stateLabel(entry: StateEntry): string {
  if (!entry.filename || entry.filename === entry.id) return entry.id
  return `${entry.filename} · ${entry.id}`
}

function baseName(path: string): string {
  const index = Math.max(path.lastIndexOf('/'), path.lastIndexOf('\\'))
  return index >= 0 ? path.slice(index + 1) : path
}

function formatBytes(value: number): string {
  if (value >= 1 << 30) return `${(value / (1 << 30)).toFixed(1)} GB`
  if (value >= 1 << 20) return `${(value / (1 << 20)).toFixed(1)} MB`
  if (value >= 1 << 10) return `${(value / (1 << 10)).toFixed(1)} KB`
  return `${value} B`
}

function formatTime(seconds: number): string {
  if (!seconds) return '时间未知'
  return new Date(seconds * 1000).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

function errorText(error: unknown): string {
  return error instanceof Error ? error.message : String(error)
}
