import { useEffect, useState } from 'react'
import { AgentPromptPreview, Config } from '../../../bindings/github.com/no22/RWKV-Agent/api/models'
import * as Backend from '../../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import { NEW_CONFIG_DEFAULTS } from '../../state/providerManager'
import type { AgentSettingsState } from '../../state/agentSettings'
import { CUSTOM_PRESET_ID, SAMPLING_PRESETS, presetById } from '../../state/samplingPresets'
import { Disclosure, NumberRow, Row, Section, Toggle } from './ui'
import { Select } from './Select'

type Props = {
  agent: AgentSettingsState
  /** 运行中连接的配置：提示词预览用它的对话格式；没有运行连接时按新连接的默认格式。 */
  runtimeConfig: Config | null
}

/*
 * 全局 Agent 分区的「生成」标签：采样、预算与提示词附加项，所有连接共用。
 * 对话格式跟着连接走，不在这里，在对话页的格式芯片里切换。
 *
 * 预设的用途写在下拉选项的 hint 里，不在页面上常驻；只有「自定义」这种会让人困惑的状态才在行下说明。
 * 改动自动保存，下一轮对话生效，因此本分区没有保存按钮。
 */
export default function ParametersSection({ agent, runtimeConfig }: Props) {
  const { value, update } = agent
  const activePreset = presetById(agent.matchedSamplingPreset)

  /*
   * 选择器在自定义模式下不再显示预设名，说明文字也要跟着走：数值恰好等于某个预设
   * 时说清楚是"等同"而不是"选中"，否则下拉说自定义、说明说预设，两者互相矛盾。
   */
  const samplingNote = (() => {
    const values = agent.samplingValues
    if (!agent.samplingIsCustom) return `温度 ${values.temperature} · top_k ${values.topK} · top_p ${values.topP} · presence ${values.presencePenalty} · frequency ${values.frequencyPenalty} · decay ${values.penaltyDecay}`
    if (activePreset) return `自定义：当前数值等同 ${activePreset.label}，改动任意一项即离开该预设`
    return '自定义：下面六个参数直接决定采样'
  })()

  /* 采样数值的读写口：预设只改这六个值，自定义模式直接编辑它们。 */
  const samplingFields = [
    ['温度', 'temperature', 0, 2, 0.1, 'top-k 为 1 时不起作用'],
    ['top-k 截断', 'topK', 0, 65536, 1, '1 = 总选最可能的'],
    ['top-p 截断', 'topP', 0, 1, 0.05, undefined],
    ['presence 惩罚', 'presencePenalty', 0, 2, 0.1, '出现过就扣分，抑制复读'],
    ['frequency 惩罚', 'frequencyPenalty', 0, 2, 0.1, '出现越多扣得越多'],
    ['惩罚衰减', 'penaltyDecay', 0, 1, 0.001, '1 = 永不衰减'],
  ] as const

  /*
   * [标签, 字段, 最小, 最大, 默认, 存成 0 时后端实际用的值, 说明]。默认即新连接的默认（api/defaults.go）；
   * 0 表示没设，按后端 normalizeConfig 的缺省显示，决策预算的 0 本身就是「按格式自动」。
   */
  const budgetFields = [
    ['最大步数', 'maxSteps', 2, 64, 16, 16, '一次回答最多调几轮工具'],
    ['最大输出 token', 'maxTokens', 1, 32768, NEW_CONFIG_DEFAULTS.maxTokens, 1024, undefined],
    ['决策输出 token', 'decisionMaxTokens', 0, 4096, NEW_CONFIG_DEFAULTS.decisionMaxTokens, 0, '含思考；0 = 按格式自动'],
  ] as const

  const [previewOpen, setPreviewOpen] = useState(false)
  const preview = usePromptPreview(previewOpen, agent, runtimeConfig)

  return (
    <>
      <Section title="采样">
        <Row label="采样预设" description={samplingNote}>
          <Select
            label="采样预设"
            className="w-[240px]"
            value={agent.samplingIsCustom ? CUSTOM_PRESET_ID : agent.matchedSamplingPreset}
            onChange={agent.applySamplingPreset}
            options={[...SAMPLING_PRESETS.map((preset) => ({ value: preset.id, label: preset.label, hint: preset.use })), { value: CUSTOM_PRESET_ID, label: '自定义', hint: '直接编辑六个采样参数' }]}
          />
        </Row>
        {agent.samplingIsCustom && samplingFields.map(([label, key, min, max, step, hint]) => (
          <NumberRow key={key} label={label} description={hint} min={min} max={max} step={step} value={agent.samplingValues[key]} onChange={(next) => update({ [key]: next })} />
        ))}
      </Section>

      <Section title="预算">
        {budgetFields.map(([label, key, min, max, fallback, unset, hint]) => (
          <NumberRow key={key} label={label} description={hint} min={min} max={max} defaultValue={fallback} value={value[key] || unset} onChange={(next) => update({ [key]: next })} />
        ))}
      </Section>

      <Section title="提示词">
        <Toggle
          label="注入会话启动时间"
          description="日期、星期与本机时区，会话内不变"
          checked={value.injectSessionTime}
          onChange={(next) => update({ injectSessionTime: next })}
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
              value={value.taskControl || ''}
              placeholder="回答使用中文；先列出步骤再给结论。"
              onChange={(event) => update({ taskControl: event.target.value })}
            />
          </label>
        </div>
        <Disclosure
          label="系统提示词预览"
          summary={preview.value && previewOpen
            ? `协议 ${preview.value.protocolId} · 渲染器 ${preview.value.rendererId} · 思考 ${preview.value.thinkingMode} · ${preview.value.native ? '原生工具调用' : '文本续写'} · 工具 ${preview.value.toolNames.length} 项`
            : runtimeConfig ? '按当前连接的对话格式，决策阶段实际发送的提示词，只读' : '还没有运行中的连接，按新连接的默认格式预览，只读'}
          open={previewOpen}
          onToggle={() => setPreviewOpen(!previewOpen)}
        >
          {preview.busy && !preview.value && <p className="m-0 py-[4px] text-sm text-ink-muted">生成中…</p>}
          {preview.error && <p className="m-0 py-[4px] text-sm text-danger">{preview.error}</p>}
          {preview.value && (
            <div className="flex flex-col gap-[8px]">
              {preview.value.sessionContext && <pre className="m-0 whitespace-pre-wrap font-mono text-sm leading-[1.7] text-ink-soft">{preview.value.sessionContext}</pre>}
              <pre className="m-0 max-h-[420px] overflow-auto whitespace-pre-wrap font-mono text-sm leading-[1.7] text-ink-soft [overflow-wrap:anywhere]">{preview.value.control}</pre>
            </div>
          )}
        </Disclosure>
      </Section>
    </>
  )
}

/*
 * 系统提示词预览：展开时拉取，影响提示词的设置（工具开关、附加约定、注入时间）变化后防抖刷新。
 * 采样与预算不影响提示词，不触发刷新。
 */
function usePromptPreview(open: boolean, agent: AgentSettingsState, runtimeConfig: Config | null) {
  const [value, setValue] = useState<AgentPromptPreview | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const settings = agent.value
  const key = JSON.stringify([
    runtimeConfig?.agentProtocol, runtimeConfig?.profile, runtimeConfig?.wire, runtimeConfig?.thinking,
    settings.enableWeb, settings.enableWeather, settings.enableBash, settings.progressiveTools, settings.enableSubagents,
    settings.taskControl, settings.injectSessionTime,
  ])

  useEffect(() => {
    if (!open) return
    let cancelled = false
    const timer = setTimeout(() => {
      setBusy(true)
      const format = runtimeConfig
        ? { agentProtocol: runtimeConfig.agentProtocol, profile: runtimeConfig.profile, wire: runtimeConfig.wire, thinking: runtimeConfig.thinking }
        : { profile: NEW_CONFIG_DEFAULTS.profile, thinking: 'off' }
      const config = new Config({
        ...format,
        enableWeb: settings.enableWeb, weatherBackend: settings.enableWeather ? NEW_CONFIG_DEFAULTS.weatherBackend : undefined,
        enableBash: settings.enableBash, progressiveTools: settings.progressiveTools, enableSubagents: settings.enableSubagents,
        taskControl: settings.taskControl?.trim() || undefined, injectSessionTime: settings.injectSessionTime,
      })
      Backend.PreviewSystemPrompt(config)
        .then((next) => { if (!cancelled) { setValue(next); setError('') } })
        .catch((reason) => { if (!cancelled) setError(reason instanceof Error ? reason.message : String(reason)) })
        .finally(() => { if (!cancelled) setBusy(false) })
    }, 350)
    return () => {
      cancelled = true
      clearTimeout(timer)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, key])

  return { value, busy, error }
}
