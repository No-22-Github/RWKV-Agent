import { NEW_CONFIG_DEFAULTS, type ProviderManager } from '../../state/providerManager'
import { FORMAT_PRESETS, formatPresetById, matchFormatPreset } from '../../state/formatPresets'
import { CUSTOM_PRESET_ID, SAMPLING_PRESETS, presetById } from '../../state/samplingPresets'
import { Button, GroupTitle, NumberField, Row, Toggle } from './ui'
import { Select } from './Select'

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
  const formatId = matchFormatPreset({ agentProtocol: manager.agentProtocol, profile: manager.profile, thinking: manager.thinking })
  const formatHint = formatPresetById(formatId)?.use ?? `连接档案里写的是自定义 wire 预设 ${manager.profile}，选一档即可改回`

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
    ['温度', 'sampleTemperature', 'setSampleTemperature', 0, 2, 0.1, '越高越发散、越低越保守；top-k 为 1 时不起作用'],
    ['top-k 截断', 'sampleTopK', 'setSampleTopK', 0, 65536, 1, '只在概率最高的 k 个候选里抽；1 = 总选最可能的，65536 = 不截断'],
    ['top-p 截断', 'sampleTopP', 'setSampleTopP', 0, 1, 0.05, '只在累计概率到 p 的候选里抽；越小越稳'],
    ['presence 惩罚', 'samplePresencePenalty', 'setSamplePresencePenalty', 0, 2, 0.1, '出现过的词统一扣分，抑制复读'],
    ['frequency 惩罚', 'sampleFrequencyPenalty', 'setSampleFrequencyPenalty', 0, 2, 0.1, '按出现次数扣分，出现越多扣得越多'],
    ['惩罚衰减', 'samplePenaltyDecay', 'setSamplePenaltyDecay', 0, 1, 0.001, '每生成一个 token 旧惩罚乘一次这个数；1 = 永不衰减'],
  ] as const

  /* 默认值即新建连接的默认（providerManager.ts 的 NEW_CONFIG_DEFAULTS 与 DEFAULT_AGENT_LIMITS）。 */
  const budgetFields = [
    ['最大步数', 'maxSteps', 'setMaxSteps', 2, 64, 16, '一次回答最多调几轮工具，到数就收尾作答'],
    ['最大输出 token', 'maxTokens', 'setMaxTokens', 1, 32768, NEW_CONFIG_DEFAULTS.maxTokens, '单次生成的长度上限，最终回答也受它限制'],
    ['决策输出 token', 'decisionMaxTokens', 'setDecisionMaxTokens', 0, 4096, NEW_CONFIG_DEFAULTS.decisionMaxTokens, '每一步决定"调哪个工具"时最多写多少，含思考；0 = 按协议自动'],
  ] as const

  return (
    <>
      <section className="mt-[18px]">
        <GroupTitle title="对话格式" />
        <Row label="格式预设" description={formatHint}>
          <Select
            label="格式预设"
            className="w-[230px] flex-none"
            value={formatId}
            onChange={(id) => {
              const preset = formatPresetById(id)
              if (!preset) return
              manager.setAgentProtocol(preset.agentProtocol)
              manager.setProfile(preset.profile)
              manager.setThinking(preset.thinking)
            }}
            options={[
              ...FORMAT_PRESETS.filter((preset) => !preset.hidden || preset.id === formatId).map((preset) => ({ value: preset.id, label: preset.label })),
              ...(formatId === 'custom' ? [{ value: 'custom', label: `自定义（${manager.profile}）` }] : []),
            ]}
          />
        </Row>
      </section>

      <section className="mt-[18px]">
        <GroupTitle title="采样" hint="预设的数值来自 2026-09-23 的 g1k 扫参" />
        <Row
          label="采样预设"
          description={samplingHint}
        >
          <Select
            label="采样预设"
            className="w-[230px] flex-none"
            value={manager.samplingIsCustom ? CUSTOM_PRESET_ID : manager.matchedSamplingPreset}
            onChange={manager.applySamplingPreset}
            options={[...SAMPLING_PRESETS.map((preset) => ({ value: preset.id, label: preset.label })), { value: CUSTOM_PRESET_ID, label: '自定义' }]}
          />
        </Row>
        {manager.samplingIsCustom ? (
          <div className="grid grid-cols-2 gap-x-[16px] gap-y-[14px] pt-[10px]">
            {samplingFields.map(([label, key, setter, min, max, step, hint]) => (
              <NumberField key={key} label={label} hint={hint} min={min} max={max} step={step} value={manager[key]} onChange={manager[setter]} />
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
        <div className="grid grid-cols-2 gap-x-[16px] gap-y-[14px] pt-[10px]">
          {budgetFields.map(([label, key, setter, min, max, fallback, hint]) => (
            <NumberField key={key} label={label} hint={hint} min={min} max={max} defaultValue={fallback} value={manager[key]} onChange={manager[setter]} />
          ))}
        </div>
      </section>

      <section className="mt-[18px]">
        <GroupTitle title="时间上下文" />
        <Toggle
          label="注入会话启动时间"
          description="在系统消息后追加独立的时间上下文，包含日期、星期、时分与本机时区；会话内保持不变。"
          checked={manager.injectSessionTime}
          onChange={manager.setInjectSessionTime}
        />
        {manager.previewOpen && manager.promptPreview?.sessionContext && (
          <pre className="rounded-md mt-[8px] whitespace-pre-wrap border border-line bg-paper-wash px-[10px] py-[8px] font-mono text-xs leading-[1.7] text-ink-soft">{manager.promptPreview.sessionContext}</pre>
        )}
      </section>

      <section className="mt-[18px]">
        <GroupTitle title="附加任务约定" />
        <div className="py-[11px]">
          <div className="flex flex-col gap-[6px]">
            <span className="text-xs leading-[1.55] text-ink-muted">可选的个性化提示词，原文追加在整个系统提示词最后（Task-specific contract 之后）。下面的预览可以直接看到效果。</span>
            <textarea
              aria-label="附加任务约定"
              className="rounded-md min-h-[88px] resize-y border border-line bg-paper-wash px-[10px] py-[8px] text-base leading-[1.6] text-ink outline-0 placeholder:text-ink-ghost focus:border-brand"
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
          <Button size="sm" aria-label="预览系统提示词" className="ml-auto font-sans" onClick={() => manager.setPreviewOpen(!manager.previewOpen)} disabled={manager.previewBusy}>{manager.previewBusy ? '生成中…' : manager.previewOpen ? '收起' : '展开'}</Button>
        </div>
        {manager.previewOpen && manager.promptPreview && (
          <pre className="rounded-md m-0 max-h-[420px] overflow-auto whitespace-pre-wrap border border-line bg-paper-wash px-[10px] py-[8px] font-mono text-xs leading-[1.7] text-ink-soft [overflow-wrap:anywhere]">{manager.promptPreview.control}</pre>
        )}
      </section>
    </>
  )
}
