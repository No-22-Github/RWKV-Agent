/** 提取 endpoint 的 host 部分；非法 URL 时回退为去掉协议头的首段。 */
export function hostOf(endpoint?: string): string {
  const value = (endpoint || '').trim()
  if (!value) return ''
  try {
    return new URL(value).host || value
  } catch {
    return value.replace(/^https?:\/\//, '').split('/')[0]
  }
}
