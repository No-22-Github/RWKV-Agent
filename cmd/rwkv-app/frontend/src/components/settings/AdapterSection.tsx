import { useEffect, useRef, useState } from 'react'
import { Events } from '@wailsio/runtime'
import { RotateCcw } from 'lucide-react'
import type { ProviderManager } from '../../state/providerManager'
import type { AdapterEntry, AdapterListing } from '../../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/models'
import * as Backend from '../../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import ConfirmDialog from '../ConfirmDialog'
import { Button, TextInput } from './ui'
import { MissingCurrent, ServerFiles } from './ServerFiles'
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
    <div>
      <ServerFiles
        noun="适配器"
        items={adapters.map((entry) => ({
          id: entry.id,
          title: entry.id,
          meta: [entry.version ? shortVersion(entry.version) : '', entry.rank ? `rank ${entry.rank}` : '', entry.alpha ? `alpha ${entry.alpha}` : '', entry.versions > 1 ? `${entry.versions} 个版本` : '', entry.localPath ? baseName(entry.localPath) : ''].filter(Boolean).join(' · '),
          metaTitle: [entry.versions > 1 ? '有多个版本时生成用最新注册的' : '', entry.localPath ? `本机上传：${entry.localPath}` : ''].filter(Boolean).join('\n') || undefined,
        }))}
        missing={missing.map((entry) => ({ id: entry.id, title: `${entry.id} · ${baseName(entry.localPath || '')}`, canReupload: Boolean(entry.localAvailable && entry.localPath) }))}
        current={current}
        selectable={manager.draftIsRunning}
        alert={currentMissing && (
          <MissingCurrent actions={<>
            {currentRecord?.localAvailable && currentRecord.localPath && (
              <Button variant="primary" size="sm" icon={<RotateCcw size={12} />} disabled={busy} onClick={() => void upload(currentRecord.id, currentRecord.localPath!)}>重新上传 {baseName(currentRecord.localPath)}</Button>
            )}
            <Button size="sm" onClick={() => manager.setAdapterId('')}>改回基模</Button>
          </>}>正在用的适配器已不在服务器上（服务端重启会清空），连接时会被拒绝。</MissingCurrent>
        )}
        onUse={manager.setAdapterId}
        onDelete={(id) => { const entry = adapters.find((item) => item.id === id); if (entry) setPendingDelete({ entry, serverSide: true }) }}
        onReupload={(id) => { const entry = missing.find((item) => item.id === id); if (entry?.localPath) void upload(entry.id, entry.localPath) }}
        onForget={(id) => { const entry = missing.find((item) => item.id === id); if (entry) setPendingDelete({ entry, serverSide: false }) }}
        upload={{ ready: endpointReady, busy, loading, uploading, error, notice, onUpload: () => void chooseFile(), onRefresh: () => void refresh() }}
      />
      {pending && !uploading && (
        <div className="mt-[10px] border-t border-line-soft pt-[10px]">
          <p className="m-0 mb-[6px] truncate text-sm text-ink-muted" title={pending.file.kind === 'path' ? pending.file.path : undefined}>{pending.file.name} · 生成时按 ID 选用，重复的 ID 会成为新版本</p>
          <div className="flex items-center gap-[8px]">
            <TextInput label="适配器 ID" className="flex-1" value={pending.id} onChange={(id) => setPending({ ...pending, id })} placeholder="r16-lr3e-5" />
            <Button variant="primary" disabled={!pending.id.trim() || busy} onClick={() => void upload(pending.id, pending.file)}>上传</Button>
            <Button variant="ghost" onClick={() => setPending(null)}>取消</Button>
          </div>
        </div>
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
    </div>
  )
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
