import type { TraceRecordKind } from '../../ledger'

/** 台账记录 kind 的缩写标签，左侧时间线与右侧详情共用。 */
export const KIND_LABELS: Record<TraceRecordKind, string> = {
  user: 'USER', route: 'ROUTE', message: 'MSG', tool: 'TOOL', subtool: 'AGENT', output: 'OUT',
}

export function kindLabel(kind: TraceRecordKind): string {
  return KIND_LABELS[kind]
}
