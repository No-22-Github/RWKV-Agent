import { Config, Provider } from '../../bindings/github.com/no22/RWKV-Agent/api/models'

/* 草稿的字段级错误：键是出错的输入框，值是给用户看的原因。空对象表示可以保存。 */
export type DraftErrors = Partial<Record<'model' | 'endpoint', string>>

/*
 * 前端版的 validateProviderDraft（cmd/rwkv-app/appservice.go）。自动保存只在草稿
 * 通过这里时才发请求：敲到一半的地址不会被存进档案、更不会触发重连。规则必须与
 * 后端保持一致——后端仍是最终裁决，这里只负责提前在输入框下给出原因。
 */
export function validateDraft(config: Config): DraftErrors {
  const errors: DraftErrors = {}
  const local = config.provider === Provider.ProviderLocal
  if (!config.model.trim()) errors.model = local ? '请填写本地模型路径' : '请填写模型 ID'
  if (!local) {
    const endpoint = (config.endpoint || '').trim()
    if (!endpoint) {
      errors.endpoint = '请填写 API 地址'
    } else {
      let parsed: URL | undefined
      try { parsed = new URL(endpoint) } catch { parsed = undefined }
      if (!parsed || (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') || !parsed.host) {
        errors.endpoint = 'API 地址必须是 http:// 或 https:// 开头的完整地址'
      } else if (parsed.username || parsed.password) {
        errors.endpoint = 'API 地址不能内嵌账号密码，请改用下方的密码或请求头'
      }
    }
  }
  return errors
}

export function firstDraftError(errors: DraftErrors): string {
  return errors.endpoint || errors.model || ''
}

/*
 * 前端版的 providerLabel（internal/appstorage/store.go）：名称留空时后端按
 * "模型 · 主机" 派生。编辑时用它判断档案名是不是自动名——是的话表单里留空，
 * 保存时后端随模型/地址重新派生，列表不会停在旧模型名上。
 */
export function derivedProviderLabel(config: Config): string {
  const model = config.model.trim()
  if (config.provider === Provider.ProviderLocal) {
    if (!model) return '本地模型'
    const index = Math.max(model.lastIndexOf('/'), model.lastIndexOf('\\'))
    return index >= 0 && index + 1 < model.length ? model.slice(index + 1) : model
  }
  const endpoint = (config.endpoint || '').trim()
  let host = ''
  if (endpoint) {
    try { host = new URL(endpoint).host || endpoint } catch { host = endpoint }
  }
  if (model && host) return `${model} · ${host}`
  return model || host || '远端连接'
}
