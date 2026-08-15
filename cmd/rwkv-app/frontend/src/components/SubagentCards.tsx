import { ChevronDown } from 'lucide-react'
import type { SubagentTrace, ToolTrace } from '../trajectory-types'

type Props = {
  trajectory?: ToolTrace[]
  done?: boolean
}

export default function SubagentCards({ trajectory, done = true }: Props) {
  const groups = (trajectory || []).filter((call) => call.subagents && call.subagents.length > 0)
  if (groups.length === 0) return null

  return (
    <div className="flex flex-col gap-[18px]">
      {groups.map((group, groupIndex) => {
        const subagents = group.subagents || []
        const completed = subagents.filter((item) => item.status === 'completed').length
        const failed = subagents.filter((item) => item.status === 'failed').length
        const statusText = !done ? '运行中' : failed > 0 ? `${completed} 完成 · ${failed} 失败` : `${subagents.length} 路并发 · 全部完成`
        return (
          <div key={`${group.step}-${group.tool}-${groupIndex}`} className="border border-line bg-card-bg">
            <div className="flex items-center gap-[10px] border-b border-line px-[14px] py-[9px]">
              <span className="font-mono text-[9.5px] font-bold uppercase tracking-[.16em] text-brand">SPAWN_AGENTS</span>
              <span className="text-[11.5px] text-ink-muted">{statusText}</span>
              <span className="flex-1" />
              {group.subagents?.[0]?.durationMs != null && <span className="font-mono text-[10.5px] text-ink-ghost">{formatDuration(group.subagents[0].durationMs)}</span>}
              <ChevronDown size={12} className="text-ink-ghost" />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3">
              {subagents.map((agent) => (
                <SubagentCard key={agent.index} agent={agent} />
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function SubagentCard({ agent }: { agent: SubagentTrace }) {
  const dot = agent.status === 'failed' ? 'bg-danger' : agent.status === 'running' ? 'bg-brand-bright' : 'bg-brand'
  return (
    <div className="flex min-w-0 flex-col gap-[8px] border-b border-line p-[12px_14px] md:border-b-0 md:border-r last:border-r-0 last:border-b-0">
      <div className="flex items-center gap-[7px]">
        <span className={`h-[5px] w-[5px] flex-none rounded-full ${dot}`} />
        <span className="font-mono text-[9.5px] font-bold uppercase tracking-[.12em] text-ink-soft">AGENT {agent.index}</span>
        <span className="flex-1" />
        {agent.durationMs != null && <span className="font-mono text-[10px] text-ink-ghost">{formatDuration(agent.durationMs)}</span>}
      </div>
      <div className="text-[12px] leading-[1.55] text-ink">{agent.task}</div>
      <div className="flex flex-col gap-[3px] border-l border-line pl-[10px]">
        {(agent.steps || []).map((step, index) => (
          <span key={`${agent.index}-${step.step}-${index}`} className={`truncate font-mono text-[10.5px] leading-[1.5] ${step.status === 'failed' ? 'text-danger' : step.status === 'running' ? 'text-brand' : 'text-ink-muted'}`}>
            {step.tool}{step.status === 'failed' ? ' · 失败' : step.status === 'running' ? ' · 进行中' : ''}
          </span>
        ))}
      </div>
      {(agent.output || agent.error) && (
        <div className="border-t border-line pt-[7px] text-[11px] leading-[1.5] text-ink-muted">
          {agent.error || agent.output}
        </div>
      )}
    </div>
  )
}

function formatDuration(durationMs?: number) {
  if (durationMs == null) return '--'
  return durationMs < 1000 ? `${durationMs}ms` : `${(durationMs / 1000).toFixed(1)}s`
}
