import { useEffect, useRef } from 'react'
import { Check, ChevronDown, Plus, Trash2 } from 'lucide-react'
import type { Status } from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import { Provider } from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { SavedProvider } from '../../bindings/github.com/no22/RWKV-Agent/internal/appstorage/models'

type Props = {
  open: boolean
  onClose: () => void
  status: Status
  ready: boolean
  busy: boolean
  providers: SavedProvider[]
  activeProviderId: string
  enableWeb: boolean
  enableSubagents: boolean
  progressiveTools: boolean
  onActivate: (id: string) => void
  onDelete: (id: string) => void
  onToggleWeb: (value: boolean) => void
  onToggleSubagents: (value: boolean) => void
  onToggleProgressive: (value: boolean) => void
  onOpenSettings: () => void
}

export default function RunConfigDropdown({
  open, onClose, status, ready, busy, providers, activeProviderId,
  enableWeb, enableSubagents, progressiveTools,
  onActivate, onDelete, onToggleWeb, onToggleSubagents, onToggleProgressive, onOpenSettings,
}: Props) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    function onPointerDown(event: MouseEvent) {
      if (ref.current && !ref.current.contains(event.target as Node)) onClose()
    }
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('mousedown', onPointerDown)
    window.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('mousedown', onPointerDown)
      window.removeEventListener('keydown', onKeyDown)
    }
  }, [open, onClose])

  if (!open) return null

  return (
    <div ref={ref} className="run-config-dropdown absolute right-[30px] top-[56px] z-[60] flex w-[340px] flex-col border border-line-strong bg-paper-wash shadow-[0_12px_32px_rgba(60,50,35,.16)]">
      <div className="border-b border-line px-[14px] pb-[9px] pt-[11px] text-[10.5px] uppercase tracking-[.14em] text-ink-muted">已保存连接</div>
      {providers.length === 0 ? (
        <div className="border-b border-line px-[14px] py-[10px] text-[11px] text-ink-muted">尚无保存的连接，去设置里连接一次即可记住</div>
      ) : (
        providers.map((provider) => {
          // “当前”看真实连接状态：服务已就绪且正是这条档案。仅仅是"上次用过"（activeProviderId）
          // 但尚未连接时，仍可点击去连接。
          const live = ready && provider.id === activeProviderId
          const lastUsed = !live && provider.id === activeProviderId
          return (
            <div key={provider.id} className={`group relative flex items-center gap-[11px] border-b border-line px-[14px] py-[10px] ${live ? 'bg-brand-wash' : ''}`}>
              <button
                type="button"
                className="flex min-w-0 flex-1 items-center gap-[11px] border-0 bg-transparent p-0 text-left disabled:opacity-100"
                onClick={() => { if (!live) onActivate(provider.id) }}
                disabled={busy || live}
                title={live ? '当前连接' : '连接到此 Provider'}
              >
                <span className={`h-[5px] w-[5px] flex-none rounded-full ${live ? 'bg-brand-bright' : 'bg-accent-warm'}`} />
                <span className="flex min-w-0 flex-1 flex-col gap-[2px]">
                  <span className={`truncate text-[12.5px] ${live ? 'font-semibold text-ink' : 'text-ink'}`}>{provider.label || provider.config.model || '未命名连接'}</span>
                  <span className="truncate font-mono text-[10px] text-ink-muted">{providerMeta(provider)}</span>
                </span>
              </button>
              {live ? (
                <span className="flex flex-none items-center gap-[4px] text-[10.5px] text-brand"><Check size={12} />当前</span>
              ) : (
                <div className="flex flex-none items-center gap-[6px]">
                  {lastUsed && <span className="text-[10px] text-ink-muted">上次</span>}
                  <button
                    type="button"
                    className="invisible rounded-[3px] p-[3px] text-ink-muted hover:bg-danger-wash hover:text-danger group-hover:visible"
                    aria-label={`删除连接 ${provider.label}`}
                    title="删除此连接"
                    onClick={() => onDelete(provider.id)}
                    disabled={busy}
                  ><Trash2 size={13} /></button>
                </div>
              )}
            </div>
          )
        })
      )}

      <button className="flex items-center gap-[9px] border-b border-line px-[14px] py-[10px] text-left text-[12.5px] text-brand hover:bg-paper-soft" onClick={() => { onClose(); onOpenSettings() }}>
        <Plus size={14} />
        <span>添加模型或 Provider</span>
      </button>

      <div className="border-b border-line bg-paper-soft px-[14px] pb-[9px] pt-[11px] text-[10.5px] uppercase tracking-[.14em] text-ink-muted">本轮能力</div>
      <DropdownToggle label="Web 搜索与抓取" description="Brave + Tavily" checked={enableWeb} onChange={onToggleWeb} />
      <DropdownToggle label="子 Agent" description="spawn_agents 并发上限" checked={enableSubagents} onChange={onToggleSubagents} />
      <DropdownToggle label="渐进式工具暴露" description="先路由再暴露 schema" checked={progressiveTools} onChange={onToggleProgressive} />

      <button className="flex items-center gap-[9px] bg-paper-soft px-[14px] py-[10px] text-left" onClick={() => { onClose(); onOpenSettings() }}>
        <span className="flex-1 text-[12px] text-ink-soft">采样、步数与协议</span>
        <ChevronDown size={13} className="rotate-180 text-ink-muted" />
        <span className="text-[12px] text-brand">打开设置</span>
      </button>
    </div>
  )
}

function providerMeta(provider: SavedProvider): string {
  const config = provider.config
  if (config.provider === Provider.ProviderLocal) return '本地模型'
  const host = endpointHost(config.endpoint)
  const kind = config.provider === Provider.ProviderChatCompletions ? 'OpenAI 兼容' : 'RWKV 续写'
  return host ? `${kind} · ${host}` : kind
}

function endpointHost(endpoint?: string): string {
  const value = (endpoint || '').trim()
  if (!value) return ''
  try {
    return new URL(value).host || value
  } catch {
    return value.replace(/^https?:\/\//, '').split('/')[0]
  }
}

function DropdownToggle({ label, description, checked, onChange }: { label: string; description: string; checked: boolean; onChange: (value: boolean) => void }) {
  return (
    <label className="flex items-center gap-[12px] bg-paper-soft px-[14px] py-[9px] text-[12.5px] text-ink">
      <span className="flex min-w-0 flex-1 flex-col gap-[2px]">
        <span>{label}</span>
        <span className="text-[10.5px] leading-[1.5] text-ink-muted">{description}</span>
      </span>
      <input type="checkbox" aria-label={label} checked={checked} onChange={(event) => onChange(event.target.checked)} className="h-[18px] w-[32px] flex-none cursor-pointer appearance-none rounded-[9px] bg-line-strong p-0 transition-colors after:ml-[2px] after:mt-[2px] after:block after:h-[13px] after:w-[13px] after:rounded-full after:bg-white after:content-[''] after:transition-transform after:duration-200 checked:bg-brand checked:after:translate-x-[15px]" />
    </label>
  )
}
