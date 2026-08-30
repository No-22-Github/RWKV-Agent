import { useEffect, useRef } from 'react'
import { Check, Plus } from 'lucide-react'
import { Provider, type Status } from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { SavedProvider } from '../../bindings/github.com/no22/RWKV-Agent/internal/appstorage/models'

type Props = {
  open: boolean
  onClose: () => void
  ready: boolean
  busy: boolean
  providers: SavedProvider[]
  runtimeProviderId: string
  onActivate: (id: string) => void
  onOpenSettings: () => void
}

/* 运行配置下拉：只读切换器。能力开关属于连接档案，在设置的编辑器里修改。 */
export default function RunConfigDropdown({ open, onClose, ready, busy, providers, runtimeProviderId, onActivate, onOpenSettings }: Props) {
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
      <div className="border-b border-line px-[14px] pb-[9px] pt-[11px] text-2xs uppercase tracking-[.14em] text-ink-muted">已保存连接</div>
      {providers.length === 0 ? (
        <div className="border-b border-line px-[14px] py-[10px] text-xs text-ink-muted">尚无保存的连接，去设置里连接一次即可记住</div>
      ) : (
        providers.map((provider) => {
          const live = ready && provider.id === runtimeProviderId
          return (
            <div key={provider.id} className={`group flex items-center gap-[11px] border-b border-line px-[14px] py-[10px] ${live ? 'bg-brand-wash' : ''}`}>
              <button
                type="button"
                className="flex min-w-0 flex-1 items-center gap-[11px] border-0 bg-transparent p-0 text-left disabled:opacity-100"
                onClick={() => { if (!live) onActivate(provider.id) }}
                disabled={busy || live}
                title={live ? '当前连接' : '连接到此 Provider'}
              >
                <span className={`h-[5px] w-[5px] flex-none rounded-full ${live ? 'bg-brand-bright' : 'bg-accent-warm'}`} />
                <span className="flex min-w-0 flex-1 flex-col gap-[2px]">
                  <span className={`truncate text-sm ${live ? 'font-semibold text-ink' : 'text-ink'}`}>{provider.label || provider.config.model || '未命名连接'}</span>
                  <span className="truncate font-mono text-2xs text-ink-muted">{providerMeta(provider)}</span>
                </span>
              </button>
              {live && <span className="flex flex-none items-center gap-[4px] text-xs text-brand"><Check size={12} />当前</span>}
            </div>
          )
        })
      )}

      <button className="flex items-center gap-[9px] bg-paper-soft px-[14px] py-[10px] text-left" onClick={onOpenSettings}>
        <Plus size={14} className="text-brand" />
        <span className="flex-1 text-sm text-ink-soft">管理连接档案</span>
        <span className="text-xs text-brand">打开设置</span>
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
