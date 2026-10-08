import type { Result } from '../bindings/github.com/no22/RWKV-Agent/api/models'

/** 拆分前导 <think> 块：闭合时返回思考与正文，未闭合时正文为空。 */
function splitThink(output?: string): { thinking: string; rest: string } {
  if (!output) return { thinking: '', rest: '' }
  const trimmed = output.trimStart()
  if (!trimmed.startsWith('<think>')) return { thinking: '', rest: output }
  const body = trimmed.slice(7)
  const close = body.indexOf('</think>')
  if (close === -1) return { thinking: body.trim(), rest: '' }
  return { thinking: body.slice(0, close).trim(), rest: body.slice(close + 8).trim() }
}

/*
 * 快思考/完整思考预填把 think 标签的收尾字节扣在 prompt 末尾（"<think></think" 缺
 * ">"，"<think" 缺 ">"），模型的首个输出字节是补位的 ">"，随后才是思考块或协议动作。
 * 它是框架字节而非内容：仅当 ">" 之后紧跟协议动作或思考块开头时才剥掉，其余场景
 * （如 Markdown 引用）原样保留。原始字节始终保留在 detail.modelOutput / 原文页签。
 */
const PROTOCOL_ACTION_OPENINGS = ['<tool_call>', '<answer>', '```json', '<think>', '{']

function stripAssistantFraming(output: string): string {
  const trimmed = output.trimStart()
  if (!trimmed.startsWith('>')) return output
  const body = trimmed.replace(/^>\s*/, '')
  return PROTOCOL_ACTION_OPENINGS.some((opening) => body.startsWith(opening)) ? body : output
}

/** 展示层统一的模型输出拆分：先剥框架字节，再拆前导 think 块。 */
export function splitModelOutput(output?: string): { thinking: string; rest: string } {
  const { thinking, rest } = splitThink(stripAssistantFraming(output ?? ''))
  return { thinking, rest }
}

export function traceStats(trace: Result) {
  const tokens = trace.steps.reduce((total, step) => total + (step.usage?.promptTokens || 0) + (step.usage?.completionTokens || 0), 0)
  return { durationMs: trace.durationMs, tokens }
}
