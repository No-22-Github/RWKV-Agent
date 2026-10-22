import { describe, expect, it } from 'vitest'
import { AgentProtocol } from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import { FORMAT_PRESETS, formatPresetById, formatSelection, isAgentWireV1, matchFormatPreset } from './formatPresets'

describe('format presets', () => {
  it('recognises a saved connection that still says g1k', () => {
    // 旧档案存在用户本机，改名不会改写它：只认新名会让设置里的格式变成「自定义」。
    expect(matchFormatPreset({ agentProtocol: AgentProtocol.AgentProtocolXML, profile: 'g1k', thinking: 'off' })).toBe('standard')
    expect(matchFormatPreset({ agentProtocol: AgentProtocol.AgentProtocolXML, profile: 'g1k', thinking: 'full' })).toBe('think')
    expect(matchFormatPreset({ agentProtocol: AgentProtocol.AgentProtocolXML, profile: 'g1k', thinking: 'fast' })).toBe('fast')
  })

  it('recognises the current name', () => {
    expect(matchFormatPreset({ agentProtocol: AgentProtocol.AgentProtocolXML, profile: 'agent-wire-v1.0', thinking: 'off' })).toBe('standard')
  })

  it('reports an unknown profile as custom', () => {
    expect(matchFormatPreset({ agentProtocol: AgentProtocol.AgentProtocolXML, profile: 'something-else', thinking: 'off' })).toBe('custom')
  })

  it('writes the current name into every agent-wire preset', () => {
    for (const preset of FORMAT_PRESETS.filter((item) => item.id === 'standard' || item.id === 'think' || item.id === 'fast')) {
      expect(preset.profile).toBe('agent-wire-v1.0')
      expect(isAgentWireV1(preset.profile)).toBe(true)
    }
  })

  it('writes deep thinking as the agent-wire-think-v1.0 wire override and clears it again', () => {
    expect(formatSelection(formatPresetById('think')!).wire).toBe('thinking=full,nudge=think')
    expect(formatSelection(formatPresetById('standard')!, 'thinking=full,nudge=think').wire).toBe('')
    expect(formatSelection(formatPresetById('standard')!, 'loop=off').wire).toBe('loop=off')
  })
})
