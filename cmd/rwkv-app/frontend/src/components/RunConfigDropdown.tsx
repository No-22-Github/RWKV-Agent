import { useEffect, useRef } from 'react'
import { ChevronDown, Plus } from 'lucide-react'
import type { RemoteModel, Status } from '../../bindings/github.com/no22/RWKV-Agent/api/models'

type Props = {
  open: boolean
  onClose: () => void
  status: Status
  ready: boolean
  availableModels: RemoteModel[]
  enableWeb: boolean
  enableSubagents: boolean
  progressiveTools: boolean
  onToggleWeb: (value: boolean) => void
  onToggleSubagents: (value: boolean) => void
  onToggleProgressive: (value: boolean) => void
  onOpenSettings: () => void
}

export default function RunConfigDropdown({
  open, onClose, status, ready, availableModels, enableWeb, enableSubagents, progressiveTools,
  onToggleWeb, onToggleSubagents, onToggleProgressive, onOpenSettings,
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
    <div ref={ref} className="absolute right-[30px] top-[56px] z-[60] flex w-[340px] flex-col border border-line-strong bg-paper-wash shadow-[0_12px_32px_rgba(60,50,35,.16)]">
      <div className="border-b border-line px-[14px] pb-[9px] pt-[11px] text-[10.5px] uppercase tracking-[.14em] text-ink-muted">本地模型</div>
      <div className={`flex items-center gap-[11px] border-b border-line px-[14px] py-[10px] ${ready && status.model ? 'bg-brand-wash' : ''}`}>
        <span className={`h-[5px] w-[5px] flex-none rounded-full ${ready ? 'bg-brand-bright' : 'bg-ink-muted'}`} />
        <div className="flex min-w-0 flex-1 flex-col gap-[2px]">
          <span className={`truncate text-[12.5px] ${ready ? 'font-semibold text-ink' : 'text-ink-muted'}`}>{status.model || '未选择本地模型'}</span>
          <span className="font-mono text-[10px] text-ink-muted">{ready ? '已加载' : '未加载'}</span>
        </div>
        {ready && <span className="text-[10.5px] text-brand">当前</span>}
      </div>

      <div className="border-b border-line px-[14px] pb-[9px] pt-[11px] text-[10.5px] uppercase tracking-[.14em] text-ink-muted">远端 Provider</div>
      {availableModels.length === 0 ? (
        <div className="border-b border-line px-[14px] py-[10px] text-[11px] text-ink-muted">尚未连接远端服务</div>
      ) : (
        availableModels.slice(0, 4).map((model) => (
          <div key={model.id} className="flex items-center gap-[11px] border-b border-line px-[14px] py-[10px]">
            <span className="h-[5px] w-[5px] flex-none rounded-full bg-ink-muted" />
            <div className="flex min-w-0 flex-1 flex-col gap-[2px]">
              <span className="truncate text-[12.5px] text-ink">{model.id}</span>
              <span className="font-mono text-[10px] text-ink-muted">remote</span>
            </div>
          </div>
        ))
      )}

      <button className="flex items-center gap-[9px] border-b border-line px-[14px] py-[10px] text-left text-[12.5px] text-brand hover:bg-paper-soft" onClick={() => { onClose(); onOpenSettings() }}>
        <Plus size={14} />
        <span>添加模型或 Provider</span>
      </button>

      <div className="border-b border-line bg-paper-soft px-[14px] pb-[9px] pt-[11px] text-[10.5px] uppercase tracking-[.14em] text-ink-muted">本轮能力</div>
      <DropdownToggle label="Web 搜索与抓取" description="Brave + Tavily" checked={enableWeb} onChange={onToggleWeb} />
      <DropdownToggle label="子 Agent" description={`spawn_agents 并发上限`} checked={enableSubagents} onChange={onToggleSubagents} />
      <DropdownToggle label="渐进式工具暴露" description="先路由再暴露 schema" checked={progressiveTools} onChange={onToggleProgressive} />

      <button className="flex items-center gap-[9px] bg-paper-soft px-[14px] py-[10px] text-left" onClick={() => { onClose(); onOpenSettings() }}>
        <span className="flex-1 text-[12px] text-ink-soft">采样、步数与协议</span>
        <ChevronDown size={13} className="rotate-180 text-ink-muted" />
        <span className="text-[12px] text-brand">打开设置</span>
      </button>
    </div>
  )
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
