import { AgentProtocol } from '../../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { ProviderManager } from '../../state/providerManager'
import { CUSTOM_PRESET_ID, SAMPLING_PRESETS, presetById } from '../../state/samplingPresets'
import { GroupTitle, Row, SettingsPane } from './ui'

type Props = {
  manager: ProviderManager
}

/*
 * 参数分区：所有"发给模型的东西"。对话协议、思考模式、采样与预算决定模型怎么被
 * 调用，附加任务约定与系统提示词预览是同一条链路的输入与结果；"模型能做什么"
 * （工具路由、网页、子 Agent）留在这里旁边的 Agent 分区。
 *
 * 字段随当前编辑的连接档案自动保存；编辑运行中的远端档案时自动重连，因此本分区
 * 没有保存按钮。
 */
export default function ParametersSection({ manager }: Props) {
  const activePreset = presetById(manager.matchedSamplingPreset)

  /*
   * 选择器在自定义模式下不再显示预设名，说明文字也要跟着走：数值恰好等于某个预设
   * 时说清楚是"等同"而不是"选中"，否则下拉说自定义、说明说预设，两者互相矛盾。
   */
  const samplingHint = (() => {
    if (!manager.samplingIsCustom) return activePreset?.use ?? ''
    if (activePreset) return `自定义：当前数值等同 ${activePreset.label}，改动任意一项即离开该预设`
    return '自定义：下面六个参数直接决定采样'
  })()

  /* 采样数值的读写口：预设只改这六个值，高级模式直接编辑它们。 */
  const samplingFields = [
    ['温度', 'sampleTemperature', 'setSampleTemperature', 0, 2, 0.1],
    ['top-k 截断', 'sampleTopK', 'setSampleTopK', 0, 65536, 1],
    ['top-p 截断', 'sampleTopP', 'setSampleTopP', 0, 1, 0.05],
    ['presence 惩罚', 'samplePresencePenalty', 'setSamplePresencePenalty', 0, 2, 0.1],
    ['frequency 惩罚', 'sampleFrequencyPenalty', 'setSampleFrequencyPenalty', 0, 2, 0.1],
    ['惩罚衰减', 'samplePenaltyDecay', 'setSamplePenaltyDecay', 0, 1, 0.001],
  ] as const

  const budgetFields = [
    ['最大步数', 'maxSteps', 'setMaxSteps', 2, 64, 1],
    ['最大输出 token', 'maxTokens', 'setMaxTokens', 1, 32768, 1],
    ['决策输出 token', 'decisionMaxTokens', 'setDecisionMaxTokens', 0, 4096, 1],
  ] as const

  return (
    <SettingsPane>
      <div className="mb-[10px] flex items-center justify-between gap-[12px]">
        <GroupTitle title="参数" hint="自动保存；编辑运行中的远端档案时即时生效" />
        {manager.autoApplyNote && (
          <span className="flex-none font-mono text-2xs text-ink-ghost">{manager.autoApplyNote}</span>
        )}
      </div>

      <section className="mt-[18px]">
        <GroupTitle title="对话协议" />
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
      </section>

      <section className="mt-[18px]">
        <GroupTitle title="采样" hint="预设的数值来自 2026-09-23 的 g1k 扫参" />
        <Row
          label="采样预设"
          description={samplingHint}
        >
          <select
            aria-label="采样预设"
            className="h-[36px] w-[190px] flex-none border border-line bg-paper-wash px-[8px] text-base text-ink outline-0 focus:border-brand"
            value={manager.samplingIsCustom ? CUSTOM_PRESET_ID : manager.matchedSamplingPreset}
            onChange={(event) => manager.applySamplingPreset(event.target.value)}
          >
            {SAMPLING_PRESETS.map((preset) => (
              <option key={preset.id} value={preset.id}>{preset.label}</option>
            ))}
            <option value={CUSTOM_PRESET_ID}>自定义</option>
          </select>
        </Row>
        {manager.samplingIsCustom ? (
          <div className="grid grid-cols-3 gap-2 pt-[4px]">
            {samplingFields.map(([label, key, setter, min, max, step]) => (
              <label key={key} className="flex flex-col gap-[5px] text-sm text-ink-muted">
                {label}
                <input aria-label={label} className="rounded-none border border-line bg-paper-wash px-2 py-[8px] text-base text-ink outline-0" type="number" min={min} max={max} step={step} value={manager[key]} onChange={(event) => manager[setter](Number(event.target.value))} />
              </label>
            ))}
          </div>
        ) : (
          <p className="mb-0 mt-[8px] font-mono text-2xs leading-[1.7] text-ink-ghost">
            温度 {manager.samplingValues.temperature} · top_k {manager.samplingValues.topK} · top_p {manager.samplingValues.topP}
            {' · '}presence {manager.samplingValues.presencePenalty} · frequency {manager.samplingValues.frequencyPenalty}
            {' · '}decay {manager.samplingValues.penaltyDecay}
          </p>
        )}
      </section>

      <section className="mt-[18px]">
        <GroupTitle title="预算" hint="扫参时用的是一次 16 步 / 4096 token 的配置" />
        <div className="grid grid-cols-3 gap-2 pt-[10px]">
          {budgetFields.map(([label, key, setter, min, max, step]) => (
            <label key={key} className="flex flex-col gap-[5px] text-sm text-ink-muted">
              {label}
              <input aria-label={label} className="rounded-none border border-line bg-paper-wash px-2 py-[8px] text-base text-ink outline-0" type="number" min={min} max={max} step={step} value={manager[key]} onChange={(event) => manager[setter](Number(event.target.value))} />
            </label>
          ))}
        </div>
        <p className="mb-0 mt-[8px] text-xs leading-[1.65] text-ink-muted">
          决策输出 token 填 0 表示按协议自动（XML 512，其余 96）。
        </p>
      </section>

      <section className="mt-[18px]">
        <GroupTitle title="附加任务约定" />
        <div className="py-[11px]">
          <div className="flex flex-col gap-[6px]">
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
      </section>

      <section className="mt-[18px]">
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
      </section>
    </SettingsPane>
  )
}
