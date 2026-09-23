import type { Config } from '../../bindings/github.com/no22/RWKV-Agent/api/models'

/*
 * 采样预设表，镜像 Go 侧 internal/samplingpreset/presets.go。数值来自 2026-09-23
 * 的 g1k 扫参（docs/evaluations/g1k-sampling-sweep-20260923/）：改一个数字是一次新的
 * 测量，不是随手调参。预设名不是"某个最好"，而是各自在一类任务上测出来的赢家。
 *
 * 与 DEFAULT_AGENT_LIMITS 同样的约定：后端改表时这里必须同步。采样数值由
 * samplingPresets.test.ts 钉住，漂移会被测试挡住。
 */

/* 不截断的 top_k：CLI 与后端都拒绝 0，所以"没有 top-k 截断"写成词表大小。 */
export const NO_TRUNCATION = 65536

/* 预设选择器里代表"不用预设、直接填六个参数"的那一项。 */
export const CUSTOM_PRESET_ID = 'custom'

export type SamplingValues = {
  temperature: number
  topK: number
  topP: number
  presencePenalty: number
  frequencyPenalty: number
  penaltyDecay: number
}

export type SamplingPreset = SamplingValues & {
  id: string
  /** 下拉里显示的名字，与 CLI 的 --sampling 取值一致。 */
  label: string
  /** 扫参报告里"何时用"一栏，作为选择器的说明文字。 */
  use: string
}

/* 顺序照搬扫参报告的结论表：从最常用的推荐档到基线档。 */
export const SAMPLING_PRESETS: readonly SamplingPreset[] = [
  {
    id: 'g1k-agent', label: 'g1k-agent',
    use: '默认推荐，工具调用决策；bfcl-product 最高（均 48/60）',
    temperature: 0.3, topK: NO_TRUNCATION, topP: 0.5,
    presencePenalty: 0, frequencyPenalty: 0, penaltyDecay: 1,
  },
  {
    id: 'g1k-agent-fast', label: 'g1k-agent-fast',
    use: '长的多步任务；分数同一档、快约 27%，但缺参数时的追问变差',
    temperature: 0.3, topK: NO_TRUNCATION, topP: 0.5,
    presencePenalty: 0.5, frequencyPenalty: 0.1, penaltyDecay: 0.996,
  },
  {
    id: 'g1k-stable', label: 'g1k-stable',
    use: '少副本 A/B 对比；跑与跑之间波动最小',
    temperature: 1, topK: 20, topP: 0.3,
    presencePenalty: 0, frequencyPenalty: 0, penaltyDecay: 1,
  },
  {
    id: 'greedy', label: 'greedy',
    use: '回归与调试；最接近可复现（批处理仍有约 ±1 题抖动）',
    temperature: 1, topK: 1, topP: 1,
    presencePenalty: 0, frequencyPenalty: 0, penaltyDecay: 1,
  },
  {
    id: 'backend', label: 'backend',
    use: '聊天与最快跑分；rwkv_lightning 作者默认，重惩罚把输出长度减半',
    temperature: 1, topK: 20, topP: 0.3,
    presencePenalty: 2, frequencyPenalty: 0.2, penaltyDecay: 0.996,
  },
]

/* 后端 applyConfigDefaults 的归一：未设置的采样落到 greedy。 */
export const DEFAULT_SAMPLING: SamplingValues = {
  temperature: 1, topK: 1, topP: 1, presencePenalty: 0, frequencyPenalty: 0, penaltyDecay: 1,
}

export function presetById(id: string): SamplingPreset | undefined {
  return SAMPLING_PRESETS.find((preset) => preset.id === id)
}

/*
 * 把可能缺省（或为零值）的采样补成后端实际生效的数值。零值在这几个字段上不是
 * 合法取值——后端会把它们各自归一成默认——所以"未设置"与"默认"在这里等价。
 */
export function normalizeSampling(values: Partial<SamplingValues>): SamplingValues {
  return {
    temperature: values.temperature || DEFAULT_SAMPLING.temperature,
    topK: values.topK || DEFAULT_SAMPLING.topK,
    topP: values.topP || DEFAULT_SAMPLING.topP,
    presencePenalty: values.presencePenalty ?? DEFAULT_SAMPLING.presencePenalty,
    frequencyPenalty: values.frequencyPenalty ?? DEFAULT_SAMPLING.frequencyPenalty,
    penaltyDecay: values.penaltyDecay || DEFAULT_SAMPLING.penaltyDecay,
  }
}

export function samplingOf(config: Config): SamplingValues {
  return normalizeSampling(config)
}

/*
 * 反查当前数值对应的预设名，等同 Go 侧 samplingpreset.Match：被改过任何一个值的
 * 预设不再冒充原名，返回空串表示这是自定义参数。这样界面说"当前是 g1k-agent"
 * 时就真的是那份测量过的配置，而不是"曾经从它出发"。
 */
export function matchSamplingPreset(values: Partial<SamplingValues>): string {
  const current = normalizeSampling(values)
  for (const preset of SAMPLING_PRESETS) {
    if (near(preset.temperature, current.temperature) &&
      preset.topK === current.topK &&
      near(preset.topP, current.topP) &&
      near(preset.presencePenalty, current.presencePenalty) &&
      near(preset.frequencyPenalty, current.frequencyPenalty) &&
      near(preset.penaltyDecay, current.penaltyDecay)) {
      return preset.id
    }
  }
  return ''
}

function near(a: number, b: number): boolean {
  return Math.abs(a - b) < 1e-4
}
