import type { TraceRecord, TraceTurn } from '../../ledger'

/** 搜索索引的逐记录条目：命中判断只做小写子串。 */
export type SearchIndexEntry = { recordId: string; haystack: string }

export function buildSearchIndex(turns: readonly TraceTurn[]): SearchIndexEntry[] {
  const entries: SearchIndexEntry[] = []
  for (const turn of turns) {
    for (const record of turn.records) {
      const detail = record.detail
      const blocks = [record.title, record.text, record.kind, record.groupTitle]
      if (detail.prompt) blocks.push(detail.prompt)
      if (detail.arguments) blocks.push(detail.arguments)
      if (detail.result) blocks.push(detail.result)
      if (detail.modelOutput) blocks.push(detail.modelOutput)
      if (detail.output) blocks.push(detail.output)
      if (detail.error) blocks.push(detail.error)
      if (detail.task) blocks.push(detail.task)
      if (detail.route) blocks.push(detail.route)
      entries.push({ recordId: record.recordId, haystack: blocks.join('\n').toLowerCase() })
    }
  }
  return entries
}

/** 返回命中的 recordId 集合；空查询返回 null 表示不过滤。 */
export function searchRecordIds(entries: readonly SearchIndexEntry[], query: string): Set<string> | null {
  const needle = query.trim().toLowerCase()
  if (!needle) return null
  const ids = new Set<string>()
  for (const entry of entries) {
    if (entry.haystack.includes(needle)) ids.add(entry.recordId)
  }
  return ids
}

/** 防抖：查询变化后延迟触发重建，避免长台账逐键全量过滤。 */
export function debounce<A extends unknown[]>(fn: (...args: A) => void, delayMs: number): (...args: A) => void {
  let timer: ReturnType<typeof setTimeout> | null = null
  return (...args: A) => {
    if (timer !== null) clearTimeout(timer)
    timer = setTimeout(() => {
      timer = null
      fn(...args)
    }, delayMs)
  }
}

export function collectVisibleRecords(turns: readonly TraceTurn[]): TraceRecord[] {
  return turns.flatMap((turn) => turn.records)
}
