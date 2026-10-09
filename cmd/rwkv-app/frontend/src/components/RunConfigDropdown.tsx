import { useEffect, useRef } from 'react'
import { hostOf } from '../endpoint'
import { useState } from 'react'
import { Check, Plus } from 'lucide-react'
import { Provider, type Status } from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { SavedProvider } from '../../bindings/github.com/no22/RWKV-Agent/internal/appstorage/models'

type Props = {
  open: boolean
  onClose: () => void
  ready: boolean
  busy: boolean
  status: Status
  providers: SavedProvider[]
  runtimeProviderId: string
  onActivate: (id: string) => void
  onOpenSettings: () => void
}

// 收起动画时长；与 tailwind.css 的 --animate-menu-up-out 保持一致。
const CLOSE_MS = 120

/* 运行配置菜单：从输入框上方的模型标签向上弹出，显示当前运行信息与连接切换；能力与 State 各有自己的标签。 */
export default function RunConfigDropdown({ open, onClose, ready, busy, status, providers, runtimeProviderId, onActivate, onOpenSettings }: Props) {
  const ref = useRef<HTMLDivElement>(null)
  // 关闭后多留一个收起动画的时长再卸载；减少动态效果时立即卸载。
  const [mounted, setMounted] = useState(open)
  if (open && !mounted) setMounted(true)
  useEffect(() => {
    if (open || !mounted) return
    const reduced = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    const timer = setTimeout(() => setMounted(false), reduced ? 0 : CLOSE_MS)
    return () => clearTimeout(timer)
  }, [open, mounted])

  useEffect(() => {
    if (!open) return
    function onPointerDown(event: MouseEvent) {
      // 顶栏芯片自己负责开合：按下时在这里先关，松开时芯片的 click 又会把它切回打开，面板就闪一下又弹出来。
      if ((event.target as Element).closest?.('[data-run-config-trigger]')) return
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

  if (!mounted) return null

  return (
    // 收起动画期间已不可交互（inert），只是视觉上淡出。
    <div ref={ref} inert={!open} className={`run-config-dropdown absolute bottom-full left-0 z-[60] mb-[8px] flex max-h-[min(440px,48vh)] w-[340px] max-w-[calc(100vw-32px)] origin-bottom-left flex-col overflow-auto rounded-xl border border-line bg-paper-wash shadow-pop ${open ? 'animate-menu-up-in motion-reduce:animate-none' : 'animate-menu-up-out motion-reduce:animate-none'}`}>
      {/* 当前运行：顶栏芯片只放缩略信息，完整的模型、State、端点、能力在这里。 */}
      {ready && (() => {
        const runtime = providers.find((provider) => provider.id === runtimeProviderId)
        const endpoint = runtime ? providerMeta(runtime) : hostOf(status.endpoint || '')
        const rows: [string, string, boolean?][] = [
          ['模型', status.model || '—'],
          ['State', status.stateId || '未加载', Boolean(status.stateId)],
          ['端点', endpoint || '—'],
        ]
        return (<>
          <div className="border-b border-line px-[14px] pb-[11px] pt-[11px]">
            <div className="pb-[7px] text-2xs text-ink-muted">当前运行</div>
            <dl className="m-0 grid grid-cols-[46px_minmax(0,1fr)] gap-x-[10px] gap-y-[4px] text-xs">
              {rows.map(([label, value, mono]) => <div key={label} className="contents">
                <dt className="text-ink-muted">{label}</dt>
                <dd className={`m-0 truncate ${mono ? 'font-mono text-2xs leading-[1.8] text-ink' : label === 'State' ? 'text-ink-muted' : 'text-ink'}`} title={value}>{value}</dd>
              </div>)}
            </dl>
          </div>
        </>)
      })()}
      <div className="border-b border-line px-[14px] pb-[9px] pt-[11px] text-2xs text-ink-muted">{ready ? '切换连接' : '已保存连接'}</div>
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
  const host = hostOf(config.endpoint)
  const kind = config.provider === Provider.ProviderChatCompletions ? 'OpenAI 兼容' : config.provider === Provider.ProviderRWKVLightningPython ? 'Lightning Python' : 'Lightning CUDA'
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
