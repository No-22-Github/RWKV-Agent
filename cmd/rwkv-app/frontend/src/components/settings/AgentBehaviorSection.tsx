import { Globe2, Users } from 'lucide-react'
import type { ProviderManager } from '../../state/providerManager'
import { Field, GroupTitle, SettingsPane, Toggle } from './ui'

type Props = {
  manager: ProviderManager
}

/*
 * Agent 能力分区：模型能做什么——工具路由、网页搜索、子 Agent。字段随当前编辑的
 * 连接档案自动保存；编辑运行中的远端档案时自动重连，更改即时生效——因此本分区
 * 没有保存按钮。删除连接等身份操作在连接页。
 *
 * "怎么调用模型"（对话协议、思考模式、采样、预算、附加约定与提示词预览）在参数分区。
 */
export default function AgentBehaviorSection({ manager }: Props) {
  const budgets = [
    ['活动批量', 'maxActiveBatch', 'setMaxActiveBatch', 1, 8],
    ['子 Agent 并发', 'subagentMaxParallel', 'setSubagentMaxParallel', 2, 8],
    ['单 Agent 步数', 'subagentMaxSteps', 'setSubagentMaxSteps', 2, 32],
    ['批次超时（秒）', 'subagentTimeoutSeconds', 'setSubagentTimeoutSeconds', 1, 3600],
    ['远端聚合窗口（毫秒）', 'remoteBatchWaitMS', 'setRemoteBatchWaitMS', 0, 1000],
  ] as const

  return (
    <SettingsPane>
      <div className="mb-[10px] flex items-center justify-between gap-[12px]">
        <GroupTitle title="Agent 能力" hint="自动保存；编辑运行中的远端档案时即时生效" />
        {manager.autoApplyNote && (
          <span className="flex-none font-mono text-2xs text-ink-ghost">{manager.autoApplyNote}</span>
        )}
      </div>
      <section>
        <Toggle label="渐进式工具路由" description="可选：先由短 Router 选择能力组，再暴露 schema" checked={manager.progressiveTools} onChange={manager.setProgressiveTools} />
        <Toggle icon={<Globe2 size={15} />} label="网页搜索与正文获取" description="Brave Search + Tavily Extract" checked={manager.enableWeb} onChange={manager.setEnableWeb} />
        {manager.enableWeb && (
          <div className="grid grid-cols-2 gap-[10px] pt-[4px]">
            <Field label="Brave API Key" value={manager.braveAPIKey} onChange={manager.setBraveAPIKey} type="password" />
            <Field label="Tavily API Key" value={manager.tavilyAPIKey} onChange={manager.setTavilyAPIKey} type="password" />
          </div>
        )}
        <Toggle icon={<Users size={15} />} label="并发子 Agent" description="一次派发 2–8 个独立任务，不允许嵌套委派" checked={manager.enableSubagents} onChange={manager.setEnableSubagents} />
        {manager.enableSubagents && (
          <div className="grid grid-cols-3 gap-2 pt-[4px]">
            {budgets.map(([label, key, setter, min, max]) => (
              <label key={key} className="flex flex-col gap-[5px] text-sm text-ink-muted">
                {label}
                <input aria-label={label} className="rounded-none border border-line bg-paper-wash px-2 py-[8px] text-base text-ink outline-0" type="number" min={min} max={max} value={manager[key]} onChange={(event) => manager[setter](Number(event.target.value))} />
              </label>
            ))}
          </div>
        )}
      </section>
    </SettingsPane>
  )
}
