import { describe, expect, it } from 'vitest'
import {
  DEFAULT_SAMPLING, NO_TRUNCATION, SAMPLING_PRESETS, matchSamplingPreset, normalizeSampling, presetById,
} from './samplingPresets'

/* 镜像 Go 侧 internal/samplingpreset/presets_test.go：数值钉死，漂移在这里失败。 */
const PINNED = {
  greedy: { temperature: 1, topK: 1, topP: 1, presencePenalty: 0, frequencyPenalty: 0, penaltyDecay: 1 },
  'g1k-agent': { temperature: 0.3, topK: NO_TRUNCATION, topP: 0.5, presencePenalty: 0, frequencyPenalty: 0, penaltyDecay: 1 },
  'g1k-agent-fast': { temperature: 0.3, topK: NO_TRUNCATION, topP: 0.5, presencePenalty: 0.5, frequencyPenalty: 0.1, penaltyDecay: 0.996 },
  'g1k-stable': { temperature: 1, topK: 20, topP: 0.3, presencePenalty: 0, frequencyPenalty: 0, penaltyDecay: 1 },
  backend: { temperature: 1, topK: 20, topP: 0.3, presencePenalty: 2, frequencyPenalty: 0.2, penaltyDecay: 0.996 },
} as const

describe('sampling presets', () => {
  it('pins the measured values so a changed number fails here first', () => {
    expect(SAMPLING_PRESETS.map((preset) => preset.id).sort()).toEqual(Object.keys(PINNED).sort())
    for (const [id, want] of Object.entries(PINNED)) {
      const preset = presetById(id)
      expect(preset, `missing preset ${id}`).toBeDefined()
      expect({
        temperature: preset?.temperature, topK: preset?.topK, topP: preset?.topP,
        presencePenalty: preset?.presencePenalty, frequencyPenalty: preset?.frequencyPenalty, penaltyDecay: preset?.penaltyDecay,
      }).toEqual(want)
      expect(preset?.use).not.toBe('')
      // top_k 1 会让温度与 top_p 失效，只有 greedy 可以用。
      if (preset?.topK === 1) expect(id).toBe('greedy')
    }
  })

  it('recognises a preset and rejects one that was overridden', () => {
    expect(matchSamplingPreset({ temperature: 0.3, topK: NO_TRUNCATION, topP: 0.5, presencePenalty: 0, frequencyPenalty: 0, penaltyDecay: 1 })).toBe('g1k-agent')
    expect(matchSamplingPreset({ temperature: 0.5, topK: NO_TRUNCATION, topP: 0.5, presencePenalty: 0, frequencyPenalty: 0, penaltyDecay: 1 })).toBe('')
    expect(matchSamplingPreset(DEFAULT_SAMPLING)).toBe('greedy')
  })

  it('treats unset sampling as the backend default', () => {
    // 后端把零值分别归一成默认，所以"未设置"必须和 greedy 等价。
    expect(normalizeSampling({})).toEqual(DEFAULT_SAMPLING)
    expect(normalizeSampling({ temperature: 0, topK: 0, topP: 0, penaltyDecay: 0 })).toEqual(DEFAULT_SAMPLING)
    // 惩罚的 0 是合法取值，不能被当成缺省。
    expect(normalizeSampling({ presencePenalty: 0, frequencyPenalty: 0 }).presencePenalty).toBe(0)
  })
})
