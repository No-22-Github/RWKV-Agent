import { NEW_CONFIG_DEFAULTS, type ProviderManager } from '../../state/providerManager'
import { FORMAT_PRESETS, formatPresetById, matchFormatPreset } from '../../state/formatPresets'
import { CUSTOM_PRESET_ID, SAMPLING_PRESETS, presetById } from '../../state/samplingPresets'
import { Disclosure, NumberRow, Row, Section, Toggle } from './ui'
import { Select } from './Select'

type Props = {
  manager: ProviderManager
}

/*
 * 生成参数标签：所有"发给模型的东西"。对话格式、采样与预算决定模型怎么被调用，
 * 附加任务约定与系统提示词预览是同一条链路的输入与结果；"模型能做什么"在旁边的「工具」标签。
 *
 * 预设的用途写在下拉选项的 hint 里，不在页面上常驻；只有「自定义」这种会让人困惑的状态才在行下说明。
 * 字段随当前编辑的连接档案自动保存；编辑运行中的远端档案时自动重连，因此本分区没有保存按钮。
 */
export default function ParametersSection({ manager }: Props) {
  const activePreset = presetById(manager.matchedSamplingPreset)
  const formatId = matchFormatPreset({ agentProtocol: manager.agentProtocol, profile: manager.profile, thinking: manager.thinking })
  // 隐藏的旧格式（不推荐）被选中时，下拉里看不到它的说明，只能写在行下提醒改掉。
  const formatPreset = formatPresetById(formatId)
  const formatNote = formatId === 'custom' ? `档案里是自定义 wire 预设 ${manager.profile}，选一档即可改回` : formatPreset?.hidden ? formatPreset.use : undefined

  /*
   * 选择器在自定义模式下不再显示预设名，说明文字也要跟着走：数值恰好等于某个预设
   * 时说清楚是"等同"而不是"选中"，否则下拉说自定义、说明说预设，两者互相矛盾。
   */
  const samplingNote = (() => {
    const values = manager.samplingValues
    if (!manager.samplingIsCustom) return `温度 ${values.temperature} · top_k ${values.topK} · top_p ${values.topP} · presence ${values.presencePenalty} · frequency ${values.frequencyPenalty} · decay ${values.penaltyDecay}`
    if (activePreset) return `自定义：当前数值等同 ${activePreset.label}，改动任意一项即离开该预设`
    return '自定义：下面六个参数直接决定采样'
  })()

  /* 采样数值的读写口：预设只改这六个值，自定义模式直接编辑它们。 */
  const samplingFields = [
    ['温度', 'sampleTemperature', 'setSampleTemperature', 0, 2, 0.1, 'top-k 为 1 时不起作用'],
    ['top-k 截断', 'sampleTopK', 'setSampleTopK', 0, 65536, 1, '1 = 总选最可能的'],
    ['top-p 截断', 'sampleTopP', 'setSampleTopP', 0, 1, 0.05, undefined],
    ['presence 惩罚', 'samplePresencePenalty', 'setSamplePresencePenalty', 0, 2, 0.1, '出现过就扣分，抑制复读'],
    ['frequency 惩罚', 'sampleFrequencyPenalty', 'setSampleFrequencyPenalty', 0, 2, 0.1, '出现越多扣得越多'],
    ['惩罚衰减', 'samplePenaltyDecay', 'setSamplePenaltyDecay', 0, 1, 0.001, '1 = 永不衰减'],
  ] as const

  /* 默认值即新建连接的默认（providerManager.ts 的 NEW_CONFIG_DEFAULTS 与 DEFAULT_AGENT_LIMITS）。 */
  const budgetFields = [
    ['最大步数', 'maxSteps', 'setMaxSteps', 2, 64, 16, '一次回答最多调几轮工具'],
    ['最大输出 token', 'maxTokens', 'setMaxTokens', 1, 32768, NEW_CONFIG_DEFAULTS.maxTokens, undefined],
    ['决策输出 token', 'decisionMaxTokens', 'setDecisionMaxTokens', 0, 4096, NEW_CONFIG_DEFAULTS.decisionMaxTokens, '含思考；0 = 按协议自动'],
  ] as const

  const preview = manager.promptPreview

  return (
    <>
      <Section title="格式与采样">
        <Row label="对话格式" description={formatNote}>
          <Select
            label="格式预设"
            className="w-[240px]"
            value={formatId}
            onChange={(id) => {
              const preset = formatPresetById(id)
              if (!preset) return
              manager.setAgentProtocol(preset.agentProtocol)
              manager.setProfile(preset.profile)
              manager.setThinking(preset.thinking)
            }}
            options={[
              ...FORMAT_PRESETS.filter((preset) => !preset.hidden || preset.id === formatId).map((preset) => ({ value: preset.id, label: preset.label, hint: preset.use })),
              ...(formatId === 'custom' ? [{ value: 'custom', label: `自定义（${manager.profile}）` }] : []),
            ]}
          />
        </Row>
        <Row label="采样" description={samplingNote}>
          <Select
            label="采样预设"
            className="w-[240px]"
            value={manager.samplingIsCustom ? CUSTOM_PRESET_ID : manager.matchedSamplingPreset}
            onChange={manager.applySamplingPreset}
            options={[...SAMPLING_PRESETS.map((preset) => ({ value: preset.id, label: preset.label, hint: preset.use })), { value: CUSTOM_PRESET_ID, label: '自定义', hint: '直接编辑六个采样参数' }]}
          />
        </Row>
        {manager.samplingIsCustom && samplingFields.map(([label, key, setter, min, max, step, hint]) => (
          <NumberRow key={key} label={label} description={hint} min={min} max={max} step={step} value={manager[key]} onChange={manager[setter]} />
        ))}
      </Section>

      <Section title="预算">
        {budgetFields.map(([label, key, setter, min, max, fallback, hint]) => (
          <NumberRow key={key} label={label} description={hint} min={min} max={max} defaultValue={fallback} value={manager[key]} onChange={manager[setter]} />
        ))}
      </Section>

      <Section title="提示词">
        <Toggle
          label="注入会话启动时间"
          description="日期、星期与本机时区，会话内不变"
          checked={manager.injectSessionTime}
          onChange={manager.setInjectSessionTime}
        />
        <div className="border-b border-line-soft py-[12px]">
          <label className="flex flex-col gap-[8px]">
            <span className="flex flex-col gap-[2px]">
              <span className="text-base text-ink">附加任务约定</span>
              <span className="text-sm text-ink-muted">原文追加在系统提示词最后</span>
            </span>
            <textarea
              aria-label="附加任务约定"
              className="min-h-[80px] resize-y rounded-md border border-line bg-paper-wash px-[10px] py-[8px] text-base leading-[1.6] text-ink outline-0 transition-colors placeholder:text-ink-ghost hover:border-line-strong focus:border-brand"
              value={manager.taskControl}
              placeholder="回答使用中文；先列出步骤再给结论。"
              onChange={(event) => manager.setTaskControl(event.target.value)}
            />
          </label>
        </div>
        <Disclosure
          label="系统提示词预览"
          summary={preview && manager.previewOpen
            ? `协议 ${preview.protocolId} · 渲染器 ${preview.rendererId} · 思考 ${preview.thinkingMode} · ${preview.native ? '原生工具调用' : '文本续写'} · 工具 ${preview.toolNames.length} 项`
            : '决策阶段实际发送的提示词，只读'}
          open={manager.previewOpen}
          onToggle={() => manager.setPreviewOpen(!manager.previewOpen)}
        >
          {manager.previewBusy && !preview && <p className="m-0 py-[4px] text-sm text-ink-muted">生成中…</p>}
          {preview && (
            <div className="flex flex-col gap-[8px]">
              {preview.sessionContext && <pre className="m-0 whitespace-pre-wrap font-mono text-sm leading-[1.7] text-ink-soft">{preview.sessionContext}</pre>}
              <pre className="m-0 max-h-[420px] overflow-auto whitespace-pre-wrap font-mono text-sm leading-[1.7] text-ink-soft [overflow-wrap:anywhere]">{preview.control}</pre>
            </div>
          )}
        </Disclosure>
      </Section>
    </>
  )
}
