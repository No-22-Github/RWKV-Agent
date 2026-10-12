import { useEffect, useMemo, useRef, useState } from 'react'
import { motion, useReducedMotion } from 'motion/react'
import { Check, Code2, Download, GitCompareArrows, Globe, RotateCw, X } from 'lucide-react'
import type { FileChange } from '../../bindings/github.com/no22/RWKV-Agent/internal/agent/tools/models'
import { ChangeDiff, ChangeStats, FileIcon } from './FileChangesPanel'
import { artifactStatus, downloadFile, fileText, isHtml, sameChange, statusLabel, type FileArtifact, type FileView } from './fileReview'

export default function FileReviewPane({ file, files = [], onFile, view, onView, changes, disabled, onResolve, onClose }: { file: FileArtifact; files?: FileArtifact[]; onFile?: (file: FileArtifact) => void; view: FileView; onView: (view: FileView) => void; changes: FileChange[]; disabled: boolean; onResolve: (changes: FileChange[], accept: boolean) => Promise<void>; onClose: () => void }) {
  const reducedMotion = useReducedMotion()
  const paneRef = useRef<HTMLElement>(null), closeRef = useRef<HTMLButtonElement>(null), frameRef = useRef<HTMLIFrameElement>(null)
  const onCloseRef = useRef(onClose); onCloseRef.current = onClose
  const [reload, setReload] = useState(0), [resolving, setResolving] = useState(false)
  const c = file.change, name = c.path.split('/').at(-1) || c.path, state = artifactStatus(file, changes)
  const text = useMemo(() => fileText(c.after.kind === 'missing' ? c.before.data : c.after.data), [c])
  const html = isHtml(c.path) && text !== null
  const previewDocument = useMemo(() => {
    if (text === null || !isHtml(c.path)) return ''
    // srcdoc 默认继承宿主页的 base URL；显式基址让页内锚点留在预览内。
    const doc = new DOMParser().parseFromString(text, 'text/html')
    const base = doc.createElement('base'); base.href = 'about:srcdoc'; doc.head.prepend(base)
    // iframe 的键盘事件不会冒泡到主文档；仅桥接关闭动作，不开放宿主能力。
    const escape = doc.createElement('script')
    escape.textContent = 'document.addEventListener("keydown",function(e){if(e.key==="Escape"){e.preventDefault();parent.postMessage({type:"rwkv-file-preview:escape"},"*")}},true)'
    doc.body.append(escape)
    return `<!doctype html>${doc.documentElement.outerHTML}`
  }, [text, c.path])
  useEffect(() => {
    const previousFocus = document.activeElement as HTMLElement | null
    closeRef.current?.focus({ preventScroll: true })
    const keydown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { event.preventDefault(); onCloseRef.current(); return }
      if (event.key !== 'Tab') return
      const elements = Array.from(paneRef.current?.querySelectorAll<HTMLElement>('button:not(:disabled), a[href], input:not(:disabled), textarea:not(:disabled), select:not(:disabled), iframe, [tabindex="0"]') || [])
      const first = elements[0], last = elements.at(-1)
      if (event.shiftKey && (document.activeElement === first || !paneRef.current?.contains(document.activeElement))) { event.preventDefault(); last?.focus() }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus() }
    }
    const focusin = (event: FocusEvent) => { if (paneRef.current && !paneRef.current.contains(event.target as Node)) closeRef.current?.focus({ preventScroll: true }) }
    const frameMessage = (event: MessageEvent) => {
      if (event.source === frameRef.current?.contentWindow && event.data?.type === 'rwkv-file-preview:escape') onCloseRef.current()
    }
    document.addEventListener('keydown', keydown)
    document.addEventListener('focusin', focusin)
    window.addEventListener('message', frameMessage)
    return () => {
      document.removeEventListener('keydown', keydown); document.removeEventListener('focusin', focusin); window.removeEventListener('message', frameMessage)
      if (previousFocus?.isConnected) previousFocus.focus({ preventScroll: true })
    }
  }, [])
  async function resolve(accept: boolean) { setResolving(true); try { await onResolve([c], accept) } finally { setResolving(false) } }
  const tabs: { id: FileView; label: string; icon: typeof Globe }[] = [...(html ? [{ id: 'preview' as const, label: '预览', icon: Globe }] : []), { id: 'code', label: '代码', icon: Code2 }, { id: 'diff', label: '改动', icon: GitCompareArrows }]
  const active = view === 'preview' && !html ? 'code' : view
  const imageType = ({ png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', svg: 'image/svg+xml', gif: 'image/gif', webp: 'image/webp' } as Record<string, string>)[c.path.split('.').at(-1)?.toLowerCase() || '']
  // 查看器覆盖在对话上，整个开合过程只动画 transform，不参与左侧 flex 布局。
  return <>
    <motion.div aria-hidden="true" className="fixed inset-0 z-40 bg-black/[0.08] dark:bg-black/25" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: reducedMotion ? 0 : 0.22 }} onClick={onClose} />
    <motion.aside ref={paneRef} role="dialog" aria-modal="true" aria-label="文件查看器"
      initial={reducedMotion ? false : { x: '100%', opacity: 0 }}
      animate={{ x: 0, opacity: 1, transition: { duration: reducedMotion ? 0 : 0.34, ease: [0.22, 1, 0.36, 1] } }}
      exit={{ x: reducedMotion ? 0 : '100%', opacity: 0, transition: { duration: reducedMotion ? 0 : 0.22, ease: [0.4, 0, 1, 1] } }}
      className="fixed inset-y-0 right-0 z-50 flex w-full min-h-0 min-w-0 flex-col border-l border-line bg-paper shadow-[-16px_0_48px_-16px_rgba(0,0,0,0.18)] md:w-[min(860px,52vw)] md:min-w-[420px]">

    <header className="flex h-(--header-h) flex-none items-center gap-2.5 border-b border-line px-4 wails-mac:h-[74px] wails-mac:pt-[22px]">
      <span className="text-ink-muted"><FileIcon path={c.path} size={16} /></span><span className="min-w-0 flex-1 truncate text-sm font-medium text-ink" title={c.path}>{name}</span>
      <span className="text-xs text-ink-muted">{statusLabel[state]}</span>
      <button ref={closeRef} aria-label="关闭文件查看器" className="grid h-7 w-7 place-items-center rounded-md text-ink-muted hover:bg-paper-wash hover:text-ink" onClick={onClose}><X size={16} /></button>
    </header>
    {files.length > 1 && onFile && <div className="flex flex-none items-center gap-3 border-b border-line px-4 py-2">
      <label htmlFor="review-file" className="text-xs text-ink-muted">文件</label>
      <select id="review-file" value={Math.max(0, files.findIndex(f => sameChange(f.change, c)))} onChange={event => onFile(files[Number(event.target.value)])} className="min-w-0 flex-1 rounded-md border border-line bg-paper px-2 py-1.5 text-xs text-ink">
        {files.map((f, index) => <option key={index} value={index}>{f.change.path}</option>)}
      </select>
    </div>}
    <div className="flex flex-none items-center gap-1 border-b border-line px-3 py-2">
      <div role="tablist" aria-label="文件视图" className="flex items-center gap-1">{tabs.map(tab => <button role="tab" aria-selected={active === tab.id} key={tab.id} onClick={() => onView(tab.id)} className={`flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs ${active === tab.id ? 'bg-surface-active font-medium text-ink' : 'text-ink-muted hover:bg-paper-wash'}`}><tab.icon size={13} />{tab.label}</button>)}</div>
      <span className="ml-auto"><ChangeStats change={c} /></span>
      <button aria-label="下载文件" title="下载文件" className="ml-1 grid h-7 w-7 place-items-center rounded-md text-ink-muted hover:bg-paper-wash" onClick={() => downloadFile((c.after.kind === 'missing' ? c.before.data : c.after.data) || '', name)}><Download size={14} /></button>
    </div>
    {active === 'preview' && <div className="flex flex-none items-center gap-2 border-b border-line bg-paper-wash px-3 py-2">
      <button aria-label="刷新预览" className="grid h-6 w-6 place-items-center text-ink-muted" onClick={() => setReload(reload + 1)}><RotateCw size={14} /></button>
      <div className="flex min-w-0 flex-1 items-center gap-2 rounded-md border border-line bg-paper px-3 py-1.5 text-xs text-ink-soft"><Globe size={12} className="flex-none text-ink-muted" /><span className="truncate">{c.path}</span></div>
    </div>}
    <div className="min-h-0 flex-1 overflow-auto">
      {active === 'preview' && html ? <iframe ref={frameRef} key={`${c.path}:${reload}`} title={`${name} 网页预览`} className="block h-full min-h-[300px] w-full border-0 bg-white" sandbox="allow-scripts" referrerPolicy="no-referrer" srcDoc={previewDocument} />
        : active === 'diff' ? <ChangeDiff change={c} />
        : imageType && c.after.kind !== 'missing' ? <div className="grid min-h-full place-items-center p-6"><img className="max-h-full max-w-full object-contain" src={`data:${imageType};base64,${c.after.data}`} alt={name} /></div>
        : text !== null ? <pre className="m-0 min-w-max py-4 font-mono text-xs leading-6 text-ink-soft">{text.split('\n').map((line, i) => <div key={i} className="flex"><span className="sticky left-0 w-14 flex-none select-none bg-paper pr-4 text-right text-ink-muted/60">{i + 1}</span><span className="whitespace-pre pr-5">{line || ' '}</span></div>)}</pre>
        : <p className="px-5 py-4 text-sm text-ink-muted">此文件无法显示为文本，可下载查看。</p>}
    </div>
    {state === 'pending' && <footer className="flex flex-none items-center gap-3 border-t border-line px-4 py-3">
      <span className="mr-auto text-xs text-ink-muted">保存到工作区</span>
      <button disabled={disabled || resolving} className="text-xs text-ink-muted disabled:opacity-40" onClick={() => void resolve(false)}>丢弃</button>
      <button disabled={disabled || resolving} className="flex items-center gap-1.5 rounded-md bg-ink px-3 py-1.5 text-xs text-paper disabled:opacity-40" onClick={() => void resolve(true)}><Check size={13} />保存文件</button>
    </footer>}
  </motion.aside>
  </>
}
