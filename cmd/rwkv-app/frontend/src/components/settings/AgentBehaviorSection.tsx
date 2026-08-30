import { Globe2, Users } from 'lucide-react'
import { AgentProtocol } from '../../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { ProviderManager } from '../../state/providerManager'
import { Field, GroupTitle, Toggle } from './ui'

type Props = {
  manager: ProviderManager
}

/*
 * Agent 行为分区：工具协议、思考模式、附加约定、系统提示词预览、网页搜索与
 * 子 Agent。字段随当前编辑的连接档案自动保存；编辑运行中的远端档案时自动重连，
 * 更改即时生效——因此本分区没有保存按钮。删除连接等身份操作在连接页。
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
    <div className="flex min-w-0 flex-1 flex-col">
      <div className="flex min-w-0 flex-1 flex-col overflow-auto">
        <div className="mx-auto w-[min(720px,calc(100%-56px))] flex-none pb-[24px] pt-[22px]">
          <div className="mb-[10px] flex items-center justify-between gap-[12px]">
            <GroupTitle title="Agent 行为" hint="自动保存；编辑运行中的远端档案时即时生效" />
            {manager.autoApplyNote && (
              <span className="flex-none font-mono text-2xs text-ink-ghost">{manager.autoApplyNote}</span>
            )}
          </div>
          <section>
            <Toggle label="渐进式工具路由" description="可选：先由短 Router 选择能力组，再暴露 schema" checked={manager.progressiveTools} onChange={manager.setProgressiveTools} />
            <div className="flex items-center justify-between gap-[20px] border-b border-line-soft py-[11px]">
              <span className="flex min-w-0 flex-1 flex-col gap-[2px]">
                <span className="text-base text-ink-strong">工具协议</span>
                <span className="text-xs leading-[1.55] text-ink-muted">XML 默认直达工具决策；Markdown 保留为可选模式</span>
              </span>
              <select aria-label="工具协议" className="h-[36px] w-[170px] flex-none border border-line bg-paper-wash px-[8px] text-base text-ink outline-0 focus:border-brand" value={manager.agentProtocol} onChange={(event) => {
                const protocol = event.target.value as AgentProtocol
                manager.setAgentProtocol(protocol)
                // 与后端 applyProtocolDefaults 的契约一致：Markdown 协议没有思考预填。
                if (protocol === AgentProtocol.AgentProtocolMarkdown) manager.setThinking('off')
              }}>
                <option value={AgentProtocol.AgentProtocolXML}>XML（推荐）</option>
                <option value={AgentProtocol.AgentProtocolMarkdown}>Markdown（可选）</option>
              </select>
            </div>
            <div className="flex items-center justify-between gap-[20px] border-b border-line-soft py-[11px]">
              <span className="flex min-w-0 flex-1 flex-col gap-[2px]">
                <span className="text-base text-ink-strong">思考模式</span>
                <span className="text-xs leading-[1.55] text-ink-muted">
                  {manager.agentProtocol === AgentProtocol.AgentProtocolMarkdown
                    ? 'Markdown 协议不支持思考预填，已按关闭处理'
                    : '快速：预填闭合 think 块，直接进入动作，适合思考型模型；完整：预填开口由模型自行闭合'}
                </span>
              </span>
              <select
                aria-label="思考模式"
                className="h-[36px] w-[170px] flex-none border border-line bg-paper-wash px-[8px] text-base text-ink outline-0 focus:border-brand disabled:opacity-40"
                value={manager.thinking}
                disabled={manager.agentProtocol === AgentProtocol.AgentProtocolMarkdown}
                onChange={(event) => manager.setThinking(event.target.value as 'off' | 'fast' | 'full')}
              >
                <option value="off">关闭（默认）</option>
                <option value="fast">快速思考</option>
                <option value="full">完整思考</option>
              </select>
            </div>
            <div className="border-b border-line-soft py-[11px]">
              <div className="flex flex-col gap-[6px]">
                <span className="text-base text-ink-strong">附加任务约定</span>
                <span className="text-xs leading-[1.55] text-ink-muted">可选的个性化提示词，原文追加在整个系统提示词最后（Task-specific contract 之后）。下面的预览可以直接看到效果。</span>
                <textarea
                  aria-label="附加任务约定"
                  className="min-h-[88px] resize-y border border-line bg-paper-wash px-[10px] py-[8px] text-base leading-[1.6] text-ink outline-0 placeholder:text-ink-ghost focus:border-brand"
                  value={manager.taskControl}
                  placeholder="例如：回答使用中文；先列出步骤再给结论。"
                  onChange={(event) => manager.setTaskControl(event.target.value)}
                />
              </div>
            </div>
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
            <div className="mt-[14px]">
              <GroupTitle title="系统提示词预览" hint="只读：决策阶段实际发送的控制提示词" />
              <div className="flex flex-wrap items-center gap-x-[14px] gap-y-[4px] pb-[8px] font-mono text-2xs text-ink-ghost">
                <span>协议 {manager.promptPreview?.protocolId ?? '…'}</span>
                <span>渲染器 {manager.promptPreview?.rendererId ?? '…'}</span>
                <span>思考 {manager.promptPreview?.thinkingMode ?? '…'}</span>
                <span>{manager.promptPreview?.native ? '原生工具调用' : '文本续写'}</span>
                <span>工具 {manager.promptPreview?.toolNames.length ?? 0} 项</span>
                <button
                  aria-label="预览系统提示词"
                  className="ml-auto h-[26px] border border-line bg-paper-wash px-[10px] font-sans text-xs text-ink disabled:opacity-40"
                  onClick={() => manager.setPreviewOpen(!manager.previewOpen)}
                  disabled={manager.previewBusy}
                >{manager.previewBusy ? '生成中…' : manager.previewOpen ? '收起' : '展开'}</button>
              </div>
              {manager.previewOpen && manager.promptPreview && (
                <pre className="m-0 max-h-[420px] overflow-auto whitespace-pre-wrap border border-line bg-paper-wash px-[10px] py-[8px] font-mono text-xs leading-[1.7] text-ink-soft [overflow-wrap:anywhere]">{manager.promptPreview.control}</pre>
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}
