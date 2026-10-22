import { describe, expect, it } from 'vitest'
import { Config, Provider } from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import { firstDraftError, isAutoProviderLabel, validateDraft } from './draftValidation'

const remote = (patch: Partial<Config>) => new Config({ provider: Provider.ProviderRWKVLightningCUDA, model: 'm', endpoint: 'https://api.test', ...patch })

describe('validateDraft', () => {
  it('accepts a complete remote and local draft', () => {
    expect(validateDraft(remote({}))).toEqual({})
    expect(validateDraft(new Config({ provider: Provider.ProviderLocal, model: '/models/a.pth' }))).toEqual({})
  })

  it('mirrors the backend rules for endpoints', () => {
    expect(validateDraft(remote({ endpoint: '' })).endpoint).toBe('请填写 API 地址')
    expect(validateDraft(remote({ endpoint: 'api.test' })).endpoint).toMatch(/http:\/\/ 或 https:\/\//)
    expect(validateDraft(remote({ endpoint: 'ftp://api.test' })).endpoint).toMatch(/http:\/\/ 或 https:\/\//)
    expect(validateDraft(remote({ endpoint: 'https://u:p@api.test' })).endpoint).toMatch(/不能内嵌账号密码/)
  })

  it('requires a model and names the field by provider kind', () => {
    expect(validateDraft(remote({ model: '  ' })).model).toBe('请填写模型 ID')
    expect(validateDraft(new Config({ provider: Provider.ProviderLocal, model: '' })).model).toBe('请填写本地模型路径')
  })

  it('reports the endpoint problem first', () => {
    expect(firstDraftError(validateDraft(remote({ model: '', endpoint: 'x' })))).toMatch(/API 地址/)
  })
})

describe('isAutoProviderLabel', () => {
  const config = remote({ model: 'rwkv7-g1k-7.2b', endpoint: 'https://api-7b.test/v1/batch/completions' })

  it('treats the current and an outdated derived name as automatic', () => {
    expect(isAutoProviderLabel('', config)).toBe(true)
    expect(isAutoProviderLabel('rwkv7-g1k-7.2b · api-7b.test', config)).toBe(true)
    // 换过模型的老档案：名字是旧模型派生的，不算用户起的名。
    expect(isAutoProviderLabel('rwkv7-g1i-7.2b · api-7b.test', config)).toBe(true)
  })

  it('keeps names the user wrote', () => {
    expect(isAutoProviderLabel('我的 7B', config)).toBe(false)
    expect(isAutoProviderLabel('我的 7B · api-7b.test', config)).toBe(false)
    expect(isAutoProviderLabel('rwkv7-g1i-7.2b · other.test', config)).toBe(false)
  })
})
