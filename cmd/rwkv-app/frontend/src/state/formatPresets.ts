import { AgentProtocol } from '../../bindings/github.com/no22/RWKV-Agent/api/models'

/*
 * 对话格式预设：把「工具协议 × wire 预设 × 思考模式」三个旋钮收成几档有名字的组合。
 * 三个字段仍原样存在连接档案里（后端、CLI 认的还是 profile/agentProtocol/thinking），
 * 这里只负责「选一档 = 写一组值」与「读一组值 = 认出是哪档」。
 *
 * 思考模式在 profile=agent-wire-v1.0 时落成 wire 覆盖（见 providerManager.wireOverride）：
 * 深度思考 = thinking=full,nudge=think，即 agent-wire-think-v1.0 预设。
 */
export type FormatPresetId = 'standard' | 'think' | 'fast' | 'markdown' | 'legacy' | 'custom'

export type FormatValues = { agentProtocol: AgentProtocol; profile: string; thinking: 'off' | 'fast' | 'full' }

/* 本机保存的旧连接写的是 format 旧名 g1k（2026-10-21 改名）；两代写法指的是同一份 wire。 */
export const RETIRED_AGENT_WIRE_PROFILE = 'g1k'

export function isAgentWireV1(profile: string): boolean {
  return profile === 'agent-wire-v1.0' || profile === RETIRED_AGENT_WIRE_PROFILE
}

export type FormatPreset = FormatValues & {
  id: FormatPresetId
  label: string
  /** 选择器下方的说明文字。 */
  use: string
  /** 只在档案当前正用着它时才出现在下拉里：不推荐新选，但不能把旧档案显示成别的。 */
  hidden?: boolean
}

export const FORMAT_PRESETS: readonly FormatPreset[] = [
  {
    id: 'standard', label: '标准（不思考）',
    use: '直接决定调用工具或回答。State 与 v1.x 训练、正式跑分都用这个格式（agent-wire-v1.0，原名 g1k）',
    agentProtocol: AgentProtocol.AgentProtocolXML, profile: 'agent-wire-v1.0', thinking: 'off',
  },
  {
    id: 'think', label: '深度思考',
    use: '每一步先写一段思考再行动，运行中会显示思考过程。带思考训练的 MiSS 适配器（v2.x）按这个格式训练（agent-wire-think-v1.0，原名 g1k-think）',
    agentProtocol: AgentProtocol.AgentProtocolXML, profile: 'agent-wire-v1.0', thinking: 'full',
  },
  {
    id: 'markdown', label: 'Markdown 工具调用（实验）',
    use: '工具调用写成 Markdown 代码块，不支持思考；只用于对比实验',
    agentProtocol: AgentProtocol.AgentProtocolMarkdown, profile: '', thinking: 'off',
  },
  {
    id: 'fast', label: '快速思考（实验）', hidden: true,
    use: '预填一个空的思考块直接进入动作。实测在基模上掉分、MiSS 上偶尔不守格式，建议改成标准或深度思考',
    agentProtocol: AgentProtocol.AgentProtocolXML, profile: 'agent-wire-v1.0', thinking: 'fast',
  },
  {
    id: 'legacy', label: '旧版 XML（不推荐）', hidden: true,
    use: '早期档案没有指定格式时沿用的旧格式（xml-v1），与训练、评测都不一致，开思考时容易解析失败；建议改成标准或深度思考',
    agentProtocol: AgentProtocol.AgentProtocolXML, profile: '', thinking: 'off',
  },
]

export function formatPresetById(id: string): FormatPreset | undefined {
  return FORMAT_PRESETS.find((preset) => preset.id === id)
}

/* 反查当前三个字段属于哪一档；对不上的组合（手写 profile 等）报 custom，选择器显示原值。 */
export function matchFormatPreset(values: FormatValues): FormatPresetId {
  if (values.agentProtocol === AgentProtocol.AgentProtocolMarkdown) return 'markdown'
  if (!values.profile) return 'legacy'
  if (!isAgentWireV1(values.profile)) return 'custom'
  return values.thinking === 'full' ? 'think' : values.thinking === 'fast' ? 'fast' : 'standard'
}
