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

/* 元数据行按 " · " 分段，只缩短其中的长名字（步数、耗时、token 保持原样）。 */
export function shortMeta(meta: string): string {
  return meta.split(' · ').map((part) => {
    const [label, name] = part.startsWith('MiSS ') ? ['MiSS ', part.slice(5)] : ['', part]
    return /\s/.test(name) || name.length <= SHORT_NAME_CHARS ? part : label + shortRunName(name)
  }).join(' · ')
}
