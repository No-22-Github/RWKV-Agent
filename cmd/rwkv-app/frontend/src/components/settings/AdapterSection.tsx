import { useEffect, useRef, useState } from 'react'
import { Events } from '@wailsio/runtime'
import { Check, RefreshCw, RotateCcw, Trash2, Upload } from 'lucide-react'
import type { ProviderManager } from '../../state/providerManager'
import type { AdapterEntry, AdapterListing } from '../../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/models'
import * as Backend from '../../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import ConfirmDialog from '../ConfirmDialog'
import { Field, GroupTitle } from './ui'
import { Select } from './Select'
import { baseName, pickLocalFile, stageBrowserFile, type PickedFile } from '../../localFile'

type Props = { manager: ProviderManager }

type PendingDelete = { entry: AdapterEntry; serverSide: boolean }

/* 选好文件、等确认 ID 的上传。 */
type PendingUpload = { file: PickedFile; id: string }

// 与后端 AdapterUploadProgress 对应（事件载荷不进绑定生成）。
type AdapterUploadProgress = { path: string; sent: number; total: number }

/*
 * 连接档案的 MiSS 适配器分组（仅 RWKV Lightning CUDA）。适配器改的是权重，State 改的是
 * 起始上下文，两者独立、可以同时用。注册只存在部署进程的内存里：整台部署共享、
 * 服务端重启即清空，所以和 State 一样记下本机上传过的文件，失效时一键重新上传。
 */
export default function AdapterSection({ manager }: Props) {
  const [listing, setListing] = useState<AdapterListing | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [uploading, setUploading] = useState<{ name: string; percent: number } | null>(null)
  const [pending, setPending] = useState<PendingUpload | null>(null)
  const [pendingDelete, setPendingDelete] = useState<PendingDelete | null>(null)
  const requestRef = useRef(0)

  const config = manager.draftConfigValue
  const endpointReady = manager.remoteEndpoint.trim() !== '' && !manager.draftErrors.endpoint
  const connectionKey = JSON.stringify([manager.remoteEndpoint.trim(), manager.apiKey.trim(), manager.headers.map((row) => [row.name.trim(), row.value.trim()])])

  async function refresh() {
    if (!endpointReady) return
    const request = ++requestRef.current
    setLoading(true)
    setError('')
    try {
      const value = await Backend.ListAdapters(config)
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
    const off = Events.On('adapter:upload-progress', (event) => {
      const value = event.data as AdapterUploadProgress
      setUploading({ name: baseName(value.path), percent: value.total > 0 ? Math.round((value.sent * 100) / value.total) : 0 })
    })
    return () => { off() }
  }, [])

  /* source 是本机路径（桌面版、重新上传）或浏览器选的文件（网页版）。 */
  async function upload(id: string, source: string | PickedFile) {
    const picked: PickedFile = typeof source === 'string' ? { kind: 'path', path: source.trim(), name: baseName(source.trim()) } : source
    const trimmedID = id.trim()
    if (!trimmedID || (picked.kind === 'path' && !picked.path)) return
    setUploading({ name: picked.name, percent: 0 })
    setError('')
    setNotice('')
    try {
      const entry = picked.kind === 'path'
        ? await Backend.UploadAdapter(config, trimmedID, picked.path)
        : await Backend.UploadBrowserAdapter(config, trimmedID, await stageBrowserFile(picked.file))
      manager.setAdapterId(entry.id)
      setPending(null)
      setNotice(`上传完成并已选用：${entry.id}${entry.version ? `（版本 ${shortVersion(entry.version)}）` : ''}`)
      await refresh()
    } catch (reason) {
      setError(errorText(reason))
    } finally {
      setUploading(null)
    }
  }

  async function chooseFile() {
    try {
      const picked = await pickLocalFile(manager.browserUploads, Backend.ChooseAdapterFile)
      if (picked) setPending({ file: picked, id: suggestID(picked.kind === 'path' ? picked.path : picked.name) })
    } catch (reason) {
      setError(errorText(reason))
    }
  }

  async function confirmDelete() {
    if (!pendingDelete) return
    const { entry, serverSide } = pendingDelete
    setPendingDelete(null)
    setError('')
    try {
      await Backend.DeleteAdapter(config, entry.id, serverSide)
      if (serverSide && manager.adapterId === entry.id) manager.setAdapterId('')
      setNotice(serverSide ? `已从服务器删除 ${entry.id}` : `已忘记 ${entry.id} 的本机记录`)
      await refresh()
    } catch (reason) {
      setError(errorText(reason))
    }
  }

  const adapters = listing?.adapters || []
  const missing = listing?.missing || []
  const current = manager.adapterId.trim()
  const currentOnServer = adapters.some((entry) => entry.id === current)
  const currentMissing = Boolean(listing) && current !== '' && !currentOnServer
  const currentRecord = missing.find((entry) => entry.id === current)
  const busy = loading || uploading !== null

  return (
    <section className="pb-[24px]">
      <GroupTitle title="MiSS 适配器" hint="仅 CUDA 协议 · 可与 State 同时使用 · 服务端重启后清空" />

      <label className="mt-[8px] flex flex-col gap-[6px] text-xs text-ink-muted">
        当前适配器
        <Select
          label="当前 MiSS 适配器"
          className="h-[40px] w-full"
          value={current}
          onChange={manager.setAdapterId}
          options={[
            { value: '', label: '基模（不使用适配器）' },
            ...adapters.map((entry) => ({ value: entry.id, label: adapterLabel(entry) })),
            ...(current !== '' && !currentOnServer ? [{ value: current, label: `${current}${listing ? '（服务器上已不存在）' : ''}` }] : []),
          ]}
        />
      </label>

      {currentMissing && (
        <div role="alert" className="mt-[10px] border-l-2 border-warning bg-paper-soft px-[10px] py-[8px] text-xs leading-[1.65] text-ink-soft">
          <p className="m-0">适配器 <span className="font-mono">{current}</span> 已不在服务器上，通常是服务端重启清空了注册。连接时会被拒绝。</p>
          <div className="mt-[7px] flex flex-wrap gap-[8px]">
            {currentRecord?.localAvailable && currentRecord.localPath && (
              <button className="rounded-md flex h-[28px] items-center gap-[5px] border-0 bg-brand px-[10px] text-xs text-brand-fg disabled:opacity-60" disabled={busy} onClick={() => void upload(currentRecord.id, currentRecord.localPath!)}>
                <RotateCcw size={12} />重新上传 {baseName(currentRecord.localPath)}
              </button>
            )}
            <button className="rounded-md h-[28px] border border-line bg-transparent px-[10px] text-xs text-ink" onClick={() => manager.setAdapterId('')}>改回基模</button>
          </div>
        </div>
      )}

      <div className="mt-[12px] flex items-center gap-[8px]">
        <button className="rounded-md flex h-[32px] items-center gap-[6px] border border-line bg-paper-wash px-[11px] text-sm text-ink disabled:opacity-50" disabled={!endpointReady || busy} onClick={() => void chooseFile()}>
          <Upload size={14} />上传 .pth…
        </button>
        <button className="flex h-[32px] items-center gap-[6px] border-0 bg-transparent px-[6px] text-sm text-brand disabled:opacity-50" disabled={!endpointReady || busy} onClick={() => void refresh()} aria-label="刷新适配器列表">
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />刷新
        </button>
        <span role="status" aria-live="polite" className="min-w-0 flex-1 truncate text-right text-xs text-ink-muted">
          {!endpointReady ? '先填写 API 地址' : uploading ? `正在上传 ${uploading.name} · ${uploading.percent}%` : loading ? '正在读取服务器列表…' : listing ? `服务器上共 ${adapters.length} 个适配器` : ''}
        </span>
      </div>
      {uploading && (
        <div className="mt-[6px] h-[3px] w-full bg-line-soft"><div className="h-full bg-brand transition-[width] duration-200" style={{ width: `${uploading.percent}%` }} /></div>
      )}

      {pending && !uploading && (
        <div className="mt-[8px] border-l-2 border-line bg-paper-soft px-[10px] pb-[6px] pt-[8px]">
          <p className="m-0 mb-[4px] truncate text-xs text-ink-soft" title={pending.file.kind === 'path' ? pending.file.path : undefined}>文件：<span className="font-mono">{pending.file.name}</span></p>
          <div className="flex items-end gap-[8px]">
            <div className="flex-1"><Field label="适配器 ID" value={pending.id} onChange={(id) => setPending({ ...pending, id })} placeholder="r16-lr3e-5" /></div>
            <button className="rounded-md mb-[6px] h-[40px] border-0 bg-brand px-[14px] text-sm text-brand-fg disabled:opacity-50" disabled={!pending.id.trim() || busy} onClick={() => void upload(pending.id, pending.file)}>上传</button>
            <button className="mb-[6px] h-[40px] border-0 bg-transparent px-[6px] text-sm text-ink-muted" onClick={() => setPending(null)}>取消</button>
          </div>
          <p className="m-0 text-2xs text-ink-muted">生成时按这个 ID 选用；用已有的 ID 上传会成为它的新版本。</p>
        </div>
      )}

      {error && <p role="alert" className="mb-0 mt-[8px] text-xs leading-[1.6] text-danger">{error}</p>}
      {notice && !error && <p className="mb-0 mt-[8px] text-xs text-brand">{notice}</p>}

      {adapters.length > 0 && (
        <ul aria-label="服务器上的 MiSS 适配器" className="m-0 mt-[12px] list-none border-t border-line-soft p-0">
          {adapters.map((entry) => {
            const selected = entry.id === current
            const origin = entry.localPath ? `本机上传：${entry.localPath}` : ''
            return (
              <li key={entry.id} className={`flex items-center gap-[10px] border-b border-line-soft px-[4px] py-[9px] ${selected ? 'bg-brand-wash' : ''}`}>
                <div className="flex min-w-0 flex-1 flex-col gap-[2px]">
                  <span className="flex min-w-0 items-baseline gap-[8px]">
                    <span className="truncate font-mono text-sm font-medium text-ink">{entry.id}</span>
                    {entry.version && <span className="flex-none font-mono text-2xs text-ink-muted" title={entry.version}>{shortVersion(entry.version)}</span>}
                  </span>
                  <span className="truncate text-2xs text-ink-muted" title={origin || undefined}>
                    {[entry.rank ? `rank ${entry.rank}` : '', entry.alpha ? `alpha ${entry.alpha}` : '', entry.versions > 1 ? `${entry.versions} 个版本，生成用最新注册的` : '', origin].filter(Boolean).join(' · ')}
                  </span>
                </div>
                {selected ? (
                  <span className="flex flex-none items-center gap-[4px] text-xs text-brand"><Check size={12} />使用中</span>
                ) : (
                  <button className="flex-none border-0 bg-transparent px-[6px] text-xs text-brand" onClick={() => manager.setAdapterId(entry.id)}>使用</button>
                )}
                <button className="grid h-[28px] w-[28px] flex-none place-items-center border-0 bg-transparent text-ink-muted hover:text-danger" aria-label={`删除适配器 ${entry.id}`} title="从服务器删除注册" onClick={() => setPendingDelete({ entry, serverSide: true })}><Trash2 size={14} /></button>
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
                  <span className="font-mono">{entry.id}</span> · {baseName(entry.localPath || '')}{entry.localAvailable ? '' : ' · 本地文件已不存在'}
                </span>
                {entry.localAvailable && entry.localPath && (
                  <button className="flex-none border-0 bg-transparent px-[6px] text-xs text-brand disabled:opacity-50" disabled={busy} onClick={() => void upload(entry.id, entry.localPath!)}>重新上传</button>
                )}
                <button className="flex-none border-0 bg-transparent px-[6px] text-xs text-ink-muted" onClick={() => setPendingDelete({ entry, serverSide: false })}>忘记</button>
              </li>
            ))}
          </ul>
        </details>
      )}

      <ConfirmDialog
        open={pendingDelete !== null}
        title={pendingDelete?.serverSide ? '从服务器删除这个适配器？' : '忘记这条本机记录？'}
        body={pendingDelete?.serverSide
          ? `${pendingDelete.entry.id} 的所有版本会从整台部署上注销，正在使用它的其他人和其他连接也会受影响。磁盘上的适配器文件不受影响。`
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

function adapterLabel(entry: AdapterEntry): string {
  return entry.version ? `${entry.id} · ${shortVersion(entry.version)}` : entry.id
}

function shortVersion(version: string): string {
  return version.slice(0, 8)
}

/*
 * 训练产物的文件名是固定的（adapter-final.pth、checkpoint-N/training.pth），能区分它们的是
 * 所在目录：r16-lr3e-5/adapter-final.pth → r16-lr3e-5，r16-lr3e-5/checkpoint-134/training.pth
 * → r16-lr3e-5-checkpoint-134。其他文件名直接去掉扩展名。
 */
export function suggestID(path: string): string {
  const parts = path.trim().split(/[\\/]+/).filter(Boolean)
  const file = parts.at(-1) || ''
  const stem = file.replace(/\.pth$/i, '')
  if (stem === 'adapter-final' || stem === 'training') {
    const parent = parts.at(-2) || ''
    if (/^checkpoint-\d+$/.test(parent) && parts.length >= 3) return `${parts.at(-3)}-${parent}`
    return parent || stem
  }
  return stem
}

function errorText(error: unknown): string {
  return error instanceof Error ? error.message : String(error)
}
