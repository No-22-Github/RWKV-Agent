/*
 * 芯片与回合元数据里的模型 / MiSS / State 名：完整名太长会把输入框上方的芯片行撑成两行。
 * 去掉人人都有的 "rwkv7-" 前缀和 ".pth" 后缀，再截到能认出「是哪个」的长度；完整名留在悬停提示里。
 */
const SHORT_NAME_CHARS = 18

export function shortRunName(name: string, max = SHORT_NAME_CHARS): string {
  const base = name.split(/[\\/]/).at(-1) || name
  const trimmed = base.replace(/^rwkv7-/i, '').replace(/\.pth$/i, '')
  return trimmed.length > max ? `${trimmed.slice(0, max)}…` : trimmed
}

/*
 * 回合元数据（后端写的「N 步 · X 秒 · 模型 · MiSS … · State」）只留步数与耗时：
 * 模型、MiSS、State 输入框上方的芯片里已经有，每轮再列一遍太杂；完整内容放在悬停提示里。
 */
export function metaStats(meta: string | undefined): string[] {
  return (meta || '').split(' · ').filter((part) => /^\d+ 步$|^[\d.]+ 秒$/.test(part.trim()))
}
