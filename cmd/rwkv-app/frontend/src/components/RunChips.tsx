import { useEffect, useRef, useState, type ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { Check, ChevronDown, Folder, Globe, Layers, Loader2, MessageSquareCode, Network, Puzzle, Search } from 'lucide-react'
import { ModelState, Provider, type Config, type Status } from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import { shortRunName } from '../runNames'
import type { SavedProvider } from '../../bindings/github.com/no22/RWKV-Agent/internal/appstorage/models'
import * as Backend from '../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import RunConfigDropdown from './RunConfigDropdown'
import type { OpenSettingsOptions, SettingsSection } from '../state/providerManager'
import { FORMAT_PRESETS, formatPresetById, formatValuesOf, matchFormatPreset } from '../state/formatPresets'

/*
 * 输入框上方的一排运行标签（参照 Claude Code）：从左到右是「谁来跑 → 带什么跑 → 在哪跑」。
 * 模型（点开切换连接）· 对话格式 · MiSS 适配器与 State（仅 Lightning CUDA，可同时用）· 能力开关 · 工作区。
 * 格式、MiSS 与 State 跟着连接走：选了就记在这个连接上，下次切回来自动用上。能力开关所有连接共用。
 * 选择不随对话变：切到别的对话仍是同一套；每轮实际用了什么记在回答下面的运行信息里。
 */

type Props = {
  ready: boolean
  busy: boolean
  status: Status
  runtimeConfig: Config | null
  providers: SavedProvider[]
  runtimeProviderId: string
  workspace: string
  runConfigOpen: boolean
  setRunConfigOpen: (value: boolean | ((current: boolean) => boolean)) => void
  onActivate: (id: string) => void
  onToggleCapability: (key: 'enableWeb' | 'enableSubagents', value: boolean) => void
  onSetFormat: (presetId: string) => Promise<void>
  onSetState: (stateId: string) => Promise<void>
  onSetAdapter: (adapterId: string) => Promise<void>
  onChooseWorkspace: () => void
  onUnload: () => void
  onOpenSettings: (section?: SettingsSection, options?: OpenSettingsOptions) => void
}

const chipClass = 'flex h-[26px] min-w-0 items-center gap-[6px] rounded-lg border border-line bg-paper-wash px-[9px] text-xs text-ink-soft shadow-hair transition-colors duration-[120ms] hover:bg-surface-active hover:text-ink disabled:pointer-events-none disabled:opacity-60'

export default function RunChips(props: Props) {
  const { ready, busy, status, runtimeConfig, providers, runtimeProviderId, workspace, runConfigOpen, setRunConfigOpen } = props
  const runtime = providers.find((provider) => provider.id === runtimeProviderId)
  const supportsState = ready && runtime?.config.provider === Provider.ProviderRWKVLightningCUDA
  const capabilities = [runtimeConfig?.enableWeb ? 'web' : null, runtimeConfig?.enableSubagents ? 'subagents' : null, runtimeConfig?.weatherBackend ? 'weather' : null, runtimeConfig?.enableBash ? 'bash' : null].filter(Boolean).join(' · ') || '无'
  const loading = status.state === ModelState.ModelLoading

  return <div className="flex min-w-0 flex-wrap items-center gap-[6px]">
    <div className="relative min-w-0">
      {/* 模型标签：完整信息放在悬停提示与弹出菜单里，标签本身只认得出「是哪个」。 */}
      <button type="button" className={`${chipClass} max-w-[200px]`} data-run-config-trigger aria-label={status.model ? `运行配置：${status.model}` : '运行配置'} aria-haspopup="dialog" aria-expanded={runConfigOpen} onClick={() => setRunConfigOpen((value) => !value)}
        title={[status.model || '运行配置', ready && status.adapterId ? `MiSS：${status.adapterId}` : '', ready && status.stateId ? `State：${status.stateId}` : '', ready ? `能力：${capabilities}` : ''].filter(Boolean).join('\n')}>
        {loading ? <Loader2 size={11} className="animate-spin-fast motion-reduce:animate-none flex-none" /> : <span className={`h-[6px] w-[6px] flex-none rounded-full ${ready ? 'bg-brand-bright' : 'bg-ink-ghost'}`} />}
        <span className="truncate text-ink">{status.model ? shortRunName(status.model) : '选择模型'}</span>
        <ChevronDown size={12} className={`flex-none text-ink-muted transition-transform duration-200 motion-reduce:transition-none ${runConfigOpen ? 'rotate-180' : ''}`} />
      </button>
      <RunConfigDropdown open={runConfigOpen} onClose={() => setRunConfigOpen(false)} ready={ready} busy={busy} status={status} providers={providers} runtimeProviderId={runtimeProviderId} onActivate={props.onActivate} onUnload={props.onUnload} onOpenSettings={props.onOpenSettings} />
    </div>
    {ready && runtimeConfig && <FormatChip config={runtimeConfig} busy={busy} onSelect={props.onSetFormat} />}
    {supportsState && runtimeConfig && <AdapterChip config={runtimeConfig} current={status.adapterId || ''} busy={busy} onSelect={props.onSetAdapter} onManage={() => props.onOpenSettings('远端连接', { focus: 'adapter' })} />}
    {supportsState && runtimeConfig && <StateChip config={runtimeConfig} current={status.stateId || ''} busy={busy} onSelect={props.onSetState} onManage={() => props.onOpenSettings('远端连接', { focus: 'state' })} />}
    {ready && <>
      <CapabilityToggle icon={<Globe size={13} />} label="网页搜索" checked={Boolean(runtimeConfig?.enableWeb)} disabled={busy} onChange={(value) => props.onToggleCapability('enableWeb', value)} />
      <CapabilityToggle icon={<Network size={13} />} label="子 Agent" checked={Boolean(runtimeConfig?.enableSubagents)} disabled={busy} onChange={(value) => props.onToggleCapability('enableSubagents', value)} />
    </>}
    <button type="button" title="切换工作区" disabled={busy} onClick={props.onChooseWorkspace} className={`${chipClass} max-w-[200px]`}>
      <Folder size={13} className="flex-none" /><span className="truncate">{workspace}</span>
    </button>
  </div>
}

/** 能力开关：开着是深色图标，关着是浅灰。所有连接共用，下一轮生效（不重连、不重新加载）。 */
function CapabilityToggle({ icon, label, checked, disabled, onChange }: { icon: ReactNode; label: string; checked: boolean; disabled: boolean; onChange: (value: boolean) => void }) {
  const title = `${label}：${checked ? '已开启' : '已关闭'}，点击切换（所有连接共用）`
  return <button type="button" role="switch" aria-checked={checked} aria-label={label} title={title} disabled={disabled} onClick={() => onChange(!checked)}
    className={`flex h-[26px] w-[30px] flex-none items-center justify-center rounded-lg border transition-colors duration-[120ms] disabled:pointer-events-none ${checked ? 'border-line bg-paper-wash text-ink shadow-hair hover:bg-surface-active' : 'border-dashed border-line bg-transparent text-ink-ghost hover:text-ink-soft'} ${disabled ? 'opacity-60' : ''}`}>
    {icon}
  </button>
}

const CLOSE_MS = 120

/*
 * 芯片弹出菜单的开合与定位：菜单挂在 body 上、贴着芯片上沿向上展开，关闭时留 CLOSE_MS 播退场动画；
 * 点菜单外或按 Esc 关闭。onOpen 在每次打开时调用（State、适配器在这里重新拉列表）。
 */
function useChipMenu(onOpen?: () => void | (() => void)) {
  const [open, setOpen] = useState(false)
  const [mounted, setMounted] = useState(false)
  const [placement, setPlacement] = useState({ left: 16, bottom: 0, width: 300, maxHeight: 440 })
  const anchorRef = useRef<HTMLDivElement>(null)
  const menuRef = useRef<HTMLDivElement>(null)
  if (open && !mounted) setMounted(true)

  useEffect(() => {
    if (open || !mounted) return
    const reduced = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    const timer = setTimeout(() => setMounted(false), reduced ? 0 : CLOSE_MS)
    return () => clearTimeout(timer)
  }, [open, mounted])

  useEffect(() => {
    if (!open) return
    function positionMenu() {
      const rect = anchorRef.current?.getBoundingClientRect()
      if (!rect) return
      const width = Math.min(300, window.innerWidth - 32)
      setPlacement({
        left: Math.max(16, Math.min(rect.left, window.innerWidth - width - 16)),
        bottom: window.innerHeight - rect.top + 8,
        width,
        maxHeight: Math.max(0, Math.min(440, rect.top - 24)),
      })
    }
    positionMenu()
    const cleanup = onOpen?.()
    window.addEventListener('resize', positionMenu)
    window.addEventListener('scroll', positionMenu, true)
    function onPointerDown(event: MouseEvent) { if (anchorRef.current && !anchorRef.current.contains(event.target as Node) && !menuRef.current?.contains(event.target as Node)) setOpen(false) }
    function onKeyDown(event: KeyboardEvent) { if (event.key === 'Escape') setOpen(false) }
    document.addEventListener('mousedown', onPointerDown)
    window.addEventListener('keydown', onKeyDown)
    return () => { cleanup?.(); window.removeEventListener('resize', positionMenu); window.removeEventListener('scroll', positionMenu, true); document.removeEventListener('mousedown', onPointerDown); window.removeEventListener('keydown', onKeyDown) }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open])

  const menuClass = `fixed z-[60] flex origin-bottom-left flex-col overflow-hidden rounded-xl border border-line bg-paper-wash py-[4px] shadow-pop ${open ? 'animate-menu-up-in motion-reduce:animate-none' : 'animate-menu-up-out motion-reduce:animate-none'}`
  return { open, setOpen, mounted, placement, anchorRef, menuRef, menuClass }
}

/*
 * 对话格式标签：芯片上是档位短名，悬停看内部 wire 名。选中即对之后的消息生效（不重连，
 * 本地模型也不重新加载），并记在这个连接上。不推荐的旧档位只在正用着时出现，芯片标黄提示。
 */
function FormatChip({ config, busy, onSelect }: { config: Config; busy: boolean; onSelect: (id: string) => Promise<void> }) {
  const menu = useChipMenu()
  const [applying, setApplying] = useState('')
  const [error, setError] = useState('')
  const current = matchFormatPreset(formatValuesOf(config))
  const preset = formatPresetById(current)
  const wireName = config.profile ? (config.thinking === 'full' ? config.profile.replace(/^agent-wire-/, 'agent-wire-think-') : config.profile) : 'xml-v1'
  const warn = current === 'custom' || Boolean(preset?.hidden)
  const options = FORMAT_PRESETS.filter((item) => !item.hidden || item.id === current)

  async function choose(id: string) {
    if (id === current) { menu.setOpen(false); return }
    setApplying(id); setError('')
    try { await onSelect(id); menu.setOpen(false) } catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)) } finally { setApplying('') }
  }

  return <div ref={menu.anchorRef} className="relative min-w-0">
    <button type="button" aria-label="对话格式" aria-haspopup="listbox" aria-expanded={menu.open} disabled={busy} onClick={() => menu.setOpen((value) => !value)}
      title={`对话格式：${preset?.label ?? '自定义'}（${wireName}）${warn ? '\n不推荐，建议改成标准或深度思考' : ''}`} className={`${chipClass} max-w-[160px] ${warn ? 'text-warning' : ''}`}>
      <MessageSquareCode size={13} className="flex-none" />
      <span className="truncate">{preset?.short ?? '自定义'}</span>
      <ChevronDown size={12} className={`flex-none text-ink-muted transition-transform duration-200 motion-reduce:transition-none ${menu.open ? 'rotate-180' : ''}`} />
    </button>
    {menu.mounted && createPortal(<div ref={menu.menuRef} inert={!menu.open} style={menu.placement} className={menu.menuClass}>
      <div className="px-[12px] pb-[4px] pt-[6px] text-2xs text-ink-muted">对话格式 · 记在这个连接上，对之后的消息生效</div>
      <div role="listbox" aria-label="选择对话格式" className="min-h-0 flex-1 overflow-y-auto overscroll-contain">
        {options.map((item) => <StateOption key={item.id} label={item.label} hint={item.use} plain wrapHint selected={item.id === current} pending={applying === item.id} onClick={() => void choose(item.id)} />)}
        {current === 'custom' && <StateOption label={`自定义（${config.profile}）`} plain selected pending={false} onClick={() => menu.setOpen(false)} />}
        {error && <div className="px-[12px] py-[8px] text-xs text-danger">{error}</div>}
      </div>
    </div>, document.body)}
  </div>
}

type ChipProps = { config: Config; current: string; busy: boolean; onSelect: (id: string) => Promise<void>; onManage: () => void }

/** State 标签：点开列出部署上的 State，选中即对运行中的连接生效。 */
function StateChip(props: ChipProps) {
  return <RemotePickerChip {...props} icon={<Layers size={13} className="flex-none" />} kind="State" noneLabel="不使用 State" chipNone="无 State" manageLabel="上传或管理 State…" searchPlaceholder="搜索名称或 State ID…"
    load={async (config) => ((await Backend.ListStates(config)).states || []).map((entry) => ({ id: entry.id, label: entry.filename && entry.filename !== entry.id ? entry.filename : entry.id, hint: entry.filename && entry.filename !== entry.id ? entry.id : undefined }))} />
}

/** MiSS 适配器标签：和 State 并列、互不影响；选中即对运行中的连接生效。 */
function AdapterChip(props: ChipProps) {
  return <RemotePickerChip {...props} icon={<Puzzle size={13} className="flex-none" />} kind="MiSS 适配器" noneLabel="基模（不使用适配器）" chipNone="基模" manageLabel="注册或管理适配器…" searchPlaceholder="搜索适配器 ID…"
    load={async (config) => ((await Backend.ListAdapters(config)).adapters || []).map((entry) => ({ id: entry.id, label: entry.id, hint: [entry.rank ? `rank ${entry.rank}` : '', entry.version ? entry.version.slice(0, 8) : ''].filter(Boolean).join(' · ') || undefined }))} />
}

type PickerOption = { id: string; label: string; hint?: string }

/** 部署端资源（State、MiSS 适配器）的选择标签：每次打开重新拉一次列表，因为服务端重启就清空。 */
function RemotePickerChip({ config, current, busy, onSelect, onManage, icon, kind, noneLabel, chipNone, manageLabel, searchPlaceholder, load }: ChipProps & {
  icon: ReactNode; kind: string; noneLabel: string; chipNone: string; manageLabel: string; searchPlaceholder: string; load: (config: Config) => Promise<PickerOption[]>
}) {
  const [options, setOptions] = useState<PickerOption[] | null>(null)
  const [query, setQuery] = useState('')
  const [error, setError] = useState('')
  const [applying, setApplying] = useState('')
  const menu = useChipMenu(() => {
    let alive = true
    setQuery('')
    setError('')
    load(config).then((value) => { if (alive) setOptions(value) }).catch((reason: unknown) => { if (alive) setError(reason instanceof Error ? reason.message : String(reason)) })
    return () => { alive = false }
  })
  const { open, setOpen } = menu

  async function choose(id: string) {
    if (id === current) { setOpen(false); return }
    setApplying(id || 'none')
    try { await onSelect(id); setOpen(false) } catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)) } finally { setApplying('') }
  }

  const search = query.trim().toLocaleLowerCase()
  const filtered = options?.filter((option) => `${option.label} ${option.id}`.toLocaleLowerCase().includes(search))

  return <div ref={menu.anchorRef} className="relative min-w-0">
    <button type="button" aria-haspopup="listbox" aria-expanded={open} disabled={busy} onClick={() => setOpen((value) => !value)} title={current ? `${kind}：${current}` : `未使用 ${kind}`} className={`${chipClass} max-w-[180px]`}>
      {icon}
      <span className={`truncate ${current ? 'font-mono text-2xs text-ink' : ''}`}>{current ? shortRunName(current) : chipNone}</span>
      <ChevronDown size={12} className={`flex-none text-ink-muted transition-transform duration-200 motion-reduce:transition-none ${open ? 'rotate-180' : ''}`} />
    </button>
    {menu.mounted && createPortal(<div ref={menu.menuRef} inert={!open} style={menu.placement} className={menu.menuClass}>
      <div className="px-[12px] pb-[4px] pt-[6px] text-2xs text-ink-muted">{kind} · 对之后的消息生效</div>
      <div role="listbox" aria-label={`选择 ${kind}`} className="min-h-0 flex-1 overflow-y-auto overscroll-contain">
      <StateOption label={noneLabel} plain selected={!current} pending={applying === 'none'} onClick={() => void choose('')} />
      {options === null && !error && <div className="flex items-center gap-2 px-[12px] py-[8px] text-xs text-ink-muted"><Loader2 size={12} className="animate-spin-fast motion-reduce:animate-none" />正在读取部署上的 {kind}…</div>}
      {filtered?.map((option) => <StateOption key={option.id} label={option.label} hint={option.hint} selected={option.id === current} pending={applying === option.id} onClick={() => void choose(option.id)} />)}
      {options?.length === 0 && <div className="px-[12px] py-[8px] text-xs text-ink-muted">部署上还没有 {kind}</div>}
      {Boolean(options?.length) && filtered?.length === 0 && <div className="px-[12px] py-[8px] text-xs text-ink-muted">没有匹配的 {kind}</div>}
      {error && <div className="px-[12px] py-[8px] text-xs text-danger">{error}</div>}
      </div>
      <label className="mx-[8px] mt-[6px] flex shrink-0 items-center gap-[6px] rounded-lg border border-line px-[8px] py-[6px]">
        <Search size={13} className="flex-none text-ink-muted" />
        <input autoFocus aria-label={`搜索 ${kind}`} placeholder={searchPlaceholder} value={query} onChange={(event) => setQuery(event.target.value)} className="min-w-0 flex-1 border-0 bg-transparent text-xs text-ink outline-none" />
      </label>
      <button type="button" onClick={() => { setOpen(false); onManage() }} className="mt-[4px] shrink-0 border-0 border-t border-line bg-transparent px-[12px] pb-[6px] pt-[9px] text-left text-xs text-ink-soft hover:text-ink">{manageLabel}</button>
    </div>, document.body)}
  </div>
}

function StateOption({ label, hint, plain, wrapHint, selected, pending, onClick }: { label: string; hint?: string; plain?: boolean; wrapHint?: boolean; selected: boolean; pending: boolean; onClick: () => void }) {
  return <button type="button" role="option" aria-selected={selected} onClick={onClick} className="flex w-full min-w-0 items-center gap-[8px] border-0 bg-transparent px-[12px] py-[7px] text-left hover:bg-surface-active">
    <span className="flex min-w-0 flex-1 flex-col">
      <span className={`truncate text-ink ${plain ? 'text-xs' : 'font-mono text-2xs'}`}>{label}</span>
      {hint && <span className={wrapHint ? 'text-2xs leading-[1.5] text-ink-muted' : 'truncate font-mono text-2xs text-ink-ghost'}>{hint}</span>}
    </span>
    {pending ? <Loader2 size={13} className="animate-spin-fast motion-reduce:animate-none flex-none text-ink-muted" /> : selected ? <Check size={13} className="flex-none text-ink" /> : null}
  </button>
}
