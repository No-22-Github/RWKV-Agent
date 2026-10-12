import { useEffect, useId, useRef, useState } from 'react'
import { AnimatePresence, motion, useReducedMotion } from 'motion/react'
import { ChevronDown, ChevronRight, FileCode2, FileText, Folder, GitCompareArrows, Globe, RotateCcw } from 'lucide-react'
import type { FileChange } from '../../bindings/github.com/no22/RWKV-Agent/internal/agent/tools/models'
import { artifactStatus, downloadFile, fileKind, isHtml, reviewDetails, sameChange, statusLabel, type FileArtifact, type FileView } from './fileReview'

export function FileIcon({ path, directory = false, size = 21 }: { path: string; directory?: boolean; size?: number }) {
  return directory ? <Folder size={size} /> : isHtml(path) ? <Globe size={size} /> : /\.(md|txt)$/i.test(path) ? <FileText size={size} /> : <FileCode2 size={size} />
}
export function ChangeStats({ change }: { change: FileChange }) {
  const details = reviewDetails(change)
  return details.hunks !== null ? <span className="inline-flex gap-1.5 whitespace-nowrap font-mono text-xs"><span className="text-green-700 dark:text-green-400">+{details.added}</span><span className="text-red-600 dark:text-red-400">-{details.removed}</span></span> : null
}
export function ChangeDiff({ change }: { change: FileChange }) {
  const details = reviewDetails(change)
  const modeChange = change.before.kind !== 'missing' && change.after.kind !== 'missing' && change.before.mode !== change.after.mode
  return <div className="min-w-0">
    {modeChange && <p className="m-0 border-b border-line px-5 py-3 text-xs text-ink-soft">权限 {(change.before.mode || 0).toString(8)} → {(change.after.mode || 0).toString(8)}</p>}
    {details.hunks === null ? <div className="flex flex-wrap items-center gap-3 p-5 text-sm text-ink-soft"><span>下载完整文件查看{details.large ? '较大文件' : '二进制文件'}的改动。</span>
      {change.before.kind === 'file' && <button className="rounded-md border border-line px-3 py-1.5" onClick={() => downloadFile(change.before.data || '', `${change.path.split('/').at(-1)}.before`)}>下载原文件</button>}
      {change.after.kind === 'file' && <button className="rounded-md border border-line px-3 py-1.5" onClick={() => downloadFile(change.after.data || '', `${change.path.split('/').at(-1)}.after`)}>下载新文件</button>}
    </div> : details.hunks.length ? <div className="overflow-x-auto pb-5 font-mono text-xs leading-6">{details.hunks.map((hunk, index) => {
      let oldLine = hunk.oldStart, newLine = hunk.newStart
      return <div key={index}>
        <div className="border-y border-line bg-paper-wash px-5 py-1 text-ink-muted">@@ -{hunk.oldStart},{hunk.oldLines} +{hunk.newStart},{hunk.newLines} @@</div>
        {hunk.lines.map((line, i) => {
          const added = line.startsWith('+'), removed = line.startsWith('-'), marker = line.startsWith('\\')
          const left = added || marker ? '' : oldLine++, right = removed || marker ? '' : newLine++
          return <div key={i} className={`flex min-w-max ${added ? 'bg-green-500/10' : removed ? 'bg-red-500/10' : ''}`}>
            <span className="w-11 select-none pr-2 text-right text-ink-muted/60">{left}</span><span className="w-11 select-none pr-3 text-right text-ink-muted/60">{right}</span>
            <span className={`whitespace-pre pr-5 ${added ? 'text-green-800 dark:text-green-300' : removed ? 'text-red-800 dark:text-red-300' : 'text-ink-soft'}`}>{line || ' '}</span>
          </div>
        })}
      </div>
    })}</div> : <p className="p-5 text-sm text-ink-muted">{change.after.kind === 'directory' || change.before.kind === 'directory' ? '目录变更，包含其子项。' : '没有文本内容差异。'}</p>}
  </div>
}
function ArtifactCard({ file, pending, onOpen }: { file: FileArtifact; pending: FileChange[]; onOpen: (file: FileArtifact, view: FileView) => void }) {
  const [menu, setMenu] = useState(false), menuRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!menu) return
    const close = (e: PointerEvent) => { if (!menuRef.current?.contains(e.target as Node)) setMenu(false) }
    const key = (e: KeyboardEvent) => { if (e.key === 'Escape') setMenu(false) }
    document.addEventListener('pointerdown', close); document.addEventListener('keydown', key)
    return () => { document.removeEventListener('pointerdown', close); document.removeEventListener('keydown', key) }
  }, [menu])
  const c = file.change, name = c.path.split('/').at(-1), state = artifactStatus(file, pending)
  const open = (view: FileView) => { setMenu(false); onOpen(file, view) }
  return <div className="flex min-w-0 items-center gap-3.5 rounded-xl border border-line bg-paper p-3.5 shadow-hair">
    <button className="flex min-w-0 flex-1 items-center gap-3.5 text-left" onClick={() => open(isHtml(c.path) ? 'preview' : 'diff')} aria-label={`打开 ${c.path}`}>
      <span className="grid h-11 w-11 flex-none place-items-center rounded-lg bg-paper-wash text-ink-soft"><FileIcon path={c.path} /></span>
      <span className="min-w-0"><span className="block truncate text-sm font-semibold text-ink" title={c.path}>{name}</span><span className="mt-1 block text-xs text-ink-muted">{fileKind(c.path)}</span></span>
    </button>
    <span className="hidden text-xs text-ink-muted sm:inline">{statusLabel[state]}</span>
    <div ref={menuRef} className="relative flex flex-none items-center rounded-lg border border-line bg-paper">
      <button className="py-1.5 pl-3 pr-2 text-sm text-ink hover:bg-paper-wash" onClick={() => open(isHtml(c.path) ? 'preview' : 'diff')}>{isHtml(c.path) ? '打开' : '查看改动'}</button>
      <button aria-label={`${c.path} 打开选项`} aria-expanded={menu} onClick={() => setMenu(!menu)} className="py-2 pl-1 pr-2 text-ink-muted"><ChevronDown size={13} /></button>
      {menu && <div className="absolute right-0 top-full z-20 mt-1 min-w-36 rounded-lg border border-line bg-paper p-1 shadow-pop">
        {isHtml(c.path) && <button className="block w-full rounded-md px-3 py-2 text-left text-sm hover:bg-paper-wash" onClick={() => open('preview')}>预览网页</button>}
        <button className="block w-full rounded-md px-3 py-2 text-left text-sm hover:bg-paper-wash" onClick={() => open('code')}>查看代码</button>
        <button className="block w-full rounded-md px-3 py-2 text-left text-sm hover:bg-paper-wash" onClick={() => open('diff')}>查看改动</button>
        <button className="block w-full rounded-md px-3 py-2 text-left text-sm hover:bg-paper-wash" onClick={() => { setMenu(false); downloadFile(c.after.data || '', name || c.path) }}>下载文件</button>
      </div>}
    </div>
  </div>
}
export default function FileChangesPanel({ changes, artifacts = [], fallbackChanges = [], disabled, onResolve, onOpen = () => {} }: { changes: FileChange[]; artifacts?: FileArtifact[]; fallbackChanges?: FileChange[]; disabled: boolean; onResolve: (changes: FileChange[], accept: boolean) => Promise<void>; onOpen?: (file: FileArtifact, view: FileView) => void }) {
  const reducedMotion = useReducedMotion(), disclosureId = useId()
  const [expanded, setExpanded] = useState(false), [resolving, setResolving] = useState(false), [allCards, setAllCards] = useState(false)
  const files: FileArtifact[] = artifacts.length ? [...artifacts, ...fallbackChanges.filter(c => !artifacts.some(f => sameChange(c, f.change))).map(change => ({ change, status: 'pending' }))] : (fallbackChanges.length ? fallbackChanges : changes).map(change => ({ change, status: 'pending' }))
  if (!files.length) return null
  const pending = files.map(f => changes.find(c => sameChange(c, f.change))).filter((c): c is FileChange => !!c)
  const cards = files.filter(f => f.change.after.kind === 'file')
  const stats = files.reduce((sum, f) => { const d = reviewDetails(f.change); return { added: sum.added + d.added, removed: sum.removed + d.removed } }, { added: 0, removed: 0 })
  const locked = disabled || resolving
  async function resolve(selected: FileChange[], accept: boolean) {
    setResolving(true)
    // 目录决策必须携带当前视图中所有子项，避免只处理父目录造成状态分叉。
    const grouped = changes.filter(c => selected.some(s => sameChange(s, c) || ((s.before.kind === 'directory' || s.after.kind === 'directory') && c.path.startsWith(s.path + '/'))))
    try { await onResolve(grouped, accept) } finally { setResolving(false) }
  }
  return <section aria-label="文件与改动" className="my-1 flex min-w-0 flex-col gap-3">
    {(allCards ? cards : cards.slice(0, 3)).map(f => <ArtifactCard key={f.change.path} file={f} pending={changes} onOpen={onOpen} />)}
    {cards.length > 3 && <button className="self-start text-xs text-ink-muted" onClick={() => setAllCards(!allCards)}>{allCards ? '收起文件' : `另有 ${cards.length - 3} 个文件`}</button>}
    <div className="rounded-xl border border-line bg-paper shadow-hair">
      <div className="flex min-h-11 flex-wrap items-center gap-3 px-3.5 py-2">
        <button aria-expanded={expanded} aria-controls={disclosureId} className="flex min-w-0 flex-1 items-center gap-2 text-left text-sm text-ink" onClick={() => setExpanded(!expanded)}>
          <ChevronRight size={14} className={`flex-none text-ink-muted transition-transform duration-300 motion-reduce:transition-none ${expanded ? 'rotate-90' : ''}`} />
          <span>{files.length} 个文件{pending.length ? '待确认' : '已更改'}</span>
          <span className="flex gap-1.5 font-mono text-xs"><span className="text-green-700 dark:text-green-400">+{stats.added}</span><span className="text-red-600 dark:text-red-400">-{stats.removed}</span></span>
        </button>
        <button className="flex flex-none items-center gap-1.5 text-xs text-ink-muted hover:text-ink" onClick={() => onOpen(files.find(f => f.change.after.kind === 'file' || f.change.before.kind === 'file') || files[0], 'diff')}><GitCompareArrows size={13} />查看改动</button>
        {pending.length > 0 && <div className="flex items-center gap-3">
          <button disabled={locked} className="flex items-center gap-1 text-xs text-ink-muted hover:text-ink disabled:opacity-40" onClick={() => void resolve(pending, false)}><RotateCcw size={13} />丢弃</button>
          <button disabled={locked} className="rounded-md bg-ink px-2.5 py-1 text-xs text-paper disabled:opacity-40" onClick={() => void resolve(pending, true)}>保存{pending.length > 1 ? '全部' : ''}</button>
        </div>}
      </div>
      <div id={disclosureId} aria-hidden={!expanded} inert={!expanded}>
        <AnimatePresence initial={false}>
          {expanded && <motion.div key="file-list" data-file-disclosure
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1, transition: reducedMotion ? { duration: 0 } : { height: { type: 'spring', duration: 0.45, bounce: 0 }, opacity: { duration: 0.28, delay: 0.08 } } }}
            exit={{ height: 0, opacity: 0, transition: reducedMotion ? { duration: 0 } : { height: { type: 'spring', duration: 0.32, bounce: 0 }, opacity: { duration: 0.14 } } }}
            className="overflow-hidden">
          <div className="border-t border-line">
        {files.map(file => {
          const c = file.change, current = pending.find(p => sameChange(p, c))
          return <div key={c.path} className="flex items-center gap-2.5 px-4 py-2.5">
            <span className="flex-none text-ink-muted"><FileIcon path={c.path} directory={c.after.kind === 'directory' || c.before.kind === 'directory'} size={15} /></span>
            <button className="min-w-0 flex-1 truncate text-left text-xs text-ink-soft hover:text-ink" title={c.path} onClick={() => onOpen(file, 'diff')}>{c.path}</button>
            <ChangeStats change={c} />
            {current ? <><button disabled={locked} aria-label={`丢弃 ${c.path}`} className="ml-2 text-xs text-ink-muted disabled:opacity-40" onClick={() => void resolve([current], false)}>丢弃</button><button disabled={locked} aria-label={`保存 ${c.path}`} className="text-xs text-ink disabled:opacity-40" onClick={() => void resolve([current], true)}>保存</button></> : <span className="ml-2 text-xs text-ink-muted">{statusLabel[artifactStatus(file, changes)]}</span>}
          </div>
        })}
        {pending.length > 0 && <p className="m-0 border-t border-line px-4 py-2 text-2xs text-ink-muted">确认后保存到工作区。关闭应用会丢弃未确认改动。</p>}
          </div>
          </motion.div>}
        </AnimatePresence>
      </div>
    </div>
  </section>
}
