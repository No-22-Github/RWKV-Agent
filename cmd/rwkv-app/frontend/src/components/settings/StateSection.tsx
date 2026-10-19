import { useEffect, useRef, useState } from 'react'
import { Events } from '@wailsio/runtime'
import { RotateCcw } from 'lucide-react'
import type { ProviderManager } from '../../state/providerManager'
import type { StateEntry, StateListing } from '../../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/models'
import * as Backend from '../../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import ConfirmDialog from '../ConfirmDialog'
import { Button } from './ui'
import { MissingCurrent, ServerFiles } from './ServerFiles'
import { baseName, pickLocalFile, stageBrowserFile, type PickedFile } from '../../localFile'

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

  /* source 是本机路径（桌面版、重新上传）或浏览器选的文件（网页版）。 */
  async function upload(source: string | PickedFile, replacing?: string) {
    const picked: PickedFile = typeof source === 'string' ? { kind: 'path', path: source.trim(), name: baseName(source.trim()) } : source
    if (picked.kind === 'path' && !picked.path) return
    setUploading({ name: picked.name, percent: 0 })
    setError('')
    setNotice('')
    try {
      const entry = picked.kind === 'path'
        ? await Backend.UploadState(config, picked.path)
        : await Backend.UploadBrowserState(config, await stageBrowserFile(picked.file))
      if (replacing) {
        // 旧 id 已随服务端重启失效，只清本机记录，不再请求服务器。
        await Backend.DeleteState(config, replacing, false).catch(() => undefined)
      }
      if (!replacing || manager.stateId === replacing) manager.setStateId(entry.id)
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
      const picked = await pickLocalFile(manager.browserUploads, Backend.ChooseStateFile)
      if (picked) await upload(picked)
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
    <div>
      <ServerFiles
        noun="State"
        items={states.map((entry) => ({
          id: entry.id,
          title: entry.filename || entry.id,
          meta: [formatBytes(entry.sizeBytes), formatTime(entry.created), entry.id !== entry.filename ? entry.id : ''].filter(Boolean).join(' · '),
          metaTitle: entry.localPath ? `本机上传：${entry.localPath}` : undefined,
        }))}
        missing={missing.map((entry) => ({ id: entry.id, title: entry.filename || entry.id, canReupload: Boolean(entry.localAvailable && entry.localPath) }))}
        current={current}
        selectable={manager.draftIsRunning}
        alert={currentMissing && (
          <MissingCurrent actions={<>
            {currentRecord?.localAvailable && currentRecord.localPath && (
              <Button variant="primary" size="sm" icon={<RotateCcw size={12} />} disabled={busy} onClick={() => void upload(currentRecord.localPath!, current)}>重新上传 {baseName(currentRecord.localPath)}</Button>
            )}
            <Button size="sm" onClick={() => manager.setStateId('')}>改回零状态</Button>
          </>}>正在用的 State 已不在服务器上（服务端重启会清空），连接时会被拒绝。</MissingCurrent>
        )}
        onUse={manager.setStateId}
        onDelete={(id) => { const entry = states.find((item) => item.id === id); if (entry) setPendingDelete({ entry, serverSide: true }) }}
        onReupload={(id) => { const entry = missing.find((item) => item.id === id); if (entry?.localPath) void upload(entry.localPath, entry.id) }}
        onForget={(id) => { const entry = missing.find((item) => item.id === id); if (entry) setPendingDelete({ entry, serverSide: false }) }}
        upload={{ ready: endpointReady, busy, loading, uploading, error, notice, onUpload: () => void chooseAndUpload(), onRefresh: () => void refresh() }}
      />

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
    </div>
  )
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
