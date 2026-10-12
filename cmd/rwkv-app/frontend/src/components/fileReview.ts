import { structuredPatch } from 'diff'
import type { FileChange } from '../../bindings/github.com/no22/RWKV-Agent/internal/agent/tools/models'
import type { FileArtifact } from '../../bindings/github.com/no22/RWKV-Agent/internal/appstorage/models'
export type { FileArtifact }
export type FileView = 'preview' | 'code' | 'diff'
export function fileText(data = '') {
  const bytes = Uint8Array.from(atob(data), (c) => c.charCodeAt(0))
  if (bytes.includes(0)) return null
  try { return new TextDecoder('utf-8', { fatal: true }).decode(bytes) } catch { return null }
}
export function downloadFile(data: string, name: string) {
  const bytes = Uint8Array.from(atob(data), (c) => c.charCodeAt(0))
  const url = URL.createObjectURL(new Blob([bytes]))
  const a = document.createElement('a'); a.href = url; a.download = name; a.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
export function isHtml(path: string) { return /\.html?$/i.test(path) }
export function fileKind(path: string) {
  const ext = path.split('.').at(-1)?.toLowerCase() || ''
  const names: Record<string, string> = { html: '网页 · HTML', htm: '网页 · HTML', md: '文档 · Markdown', txt: '文本文件', json: '数据 · JSON', js: '代码 · JavaScript', ts: '代码 · TypeScript', tsx: '代码 · TSX', css: '样式 · CSS', py: '代码 · Python', go: '代码 · Go', svg: '图片 · SVG', png: '图片 · PNG', jpg: '图片 · JPEG', jpeg: '图片 · JPEG' }
  return names[ext] || `文件${ext ? ` · ${ext.toUpperCase()}` : ''}`
}
const cache = new WeakMap<FileChange, ReturnType<typeof computeDetails>>()
function computeDetails(change: FileChange) {
  const large = (change.before.data?.length || 0) + (change.after.data?.length || 0) > 350_000
  const before = large ? null : fileText(change.before.data), after = large ? null : fileText(change.after.data)
  const hunks = before === null || after === null ? null : structuredPatch(change.path, change.path, before, after, '', '', { context: 3 }).hunks
  let added = 0, removed = 0
  for (const hunk of hunks || []) for (const line of hunk.lines) { if (line.startsWith('+')) added++; if (line.startsWith('-')) removed++ }
  return { large, before, after, hunks, added, removed }
}
export function reviewDetails(change: FileChange) {
  let result = cache.get(change)
  if (!result) { result = computeDetails(change); cache.set(change, result) }
  return result
}
export function sameChange(a: FileChange, b: FileChange) {
  return a.path === b.path && a.before.kind === b.before.kind && a.before.data === b.before.data && (a.before.mode || 0) === (b.before.mode || 0) && a.after.kind === b.after.kind && a.after.data === b.after.data && (a.after.mode || 0) === (b.after.mode || 0)
}
export function artifactStatus(file: FileArtifact, pending: FileChange[]) {
  if (pending.some(c => sameChange(c, file.change))) return 'pending'
  return file.status === 'pending' ? 'unavailable' : file.status
}
export const statusLabel: Record<string, string> = { pending: '待确认', saved: '已保存', discarded: '已丢弃', superseded: '已更新', unavailable: '未保存' }
