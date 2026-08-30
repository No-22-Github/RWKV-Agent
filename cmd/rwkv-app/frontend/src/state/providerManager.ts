import { useEffect, useState } from 'react'
import {
  AgentPromptPreview, AgentProtocol, Config, Provider, Status, type RemoteModel,
} from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { AppBootstrap } from '../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/models'
import type { SavedProvider } from '../../bindings/github.com/no22/RWKV-Agent/internal/appstorage/models'
import * as Backend from '../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'

export type HeaderRow = { id: number; name: string; value: string }

function stableValue(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(stableValue)
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value as Record<string, unknown>)
      .filter(([, item]) => item !== undefined)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([key, item]) => [key, stableValue(item)]))
  }
  return value
}

function providerDraftSignature(label: string, config: Config): string {
  return JSON.stringify(stableValue({ label: label.trim(), config }))
}

let nextHeaderID = 1

/*
 * Agent 能力与预算的默认值。与后端 api/service.go normalizeConfig 中的缺省值
 * 一一对应：后端调整默认值时这里必须同步，否则脏标记签名会静默漂移。
 */
const DEFAULT_AGENT_LIMITS = {
  maxSteps: 6,
  maxTokens: 1024,
  maxActiveBatch: 4,
  remoteBatchWaitMS: 10,
  subagentMaxParallel: 4,
  subagentMaxSteps: 4,
  subagentTimeoutSeconds: 120,
}

/*
 * 连接档案域的唯一状态所有者：档案列表、编辑器表单、脏标记与全部档案动作。
 * App 只保留聊天/会话域状态，通过这里的方法操作设置。
 */
export function useProviderManager({ onStatus, ready }: { onStatus: (status: Status) => void; ready: boolean }) {
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [providers, setProviders] = useState<SavedProvider[]>([])
  const [activeProviderId, setActiveProviderId] = useState('')
  const [runtimeProviderId, setRuntimeProviderId] = useState('')
  const [editingProviderId, setEditingProviderId] = useState('')
  const [draftLabel, setDraftLabel] = useState('')
  const [draftBaseConfig, setDraftBaseConfig] = useState<Config>(() => new Config())
  const [draftSnapshot, setDraftSnapshot] = useState('')
  const [draftInitialized, setDraftInitialized] = useState(false)
  const [settingsTab, setSettingsTab] = useState<'local' | 'remote'>('local')
  const [modelPath, setModelPath] = useState('')
  const [tokenizerPath, setTokenizerPath] = useState('')
  const [remoteEndpoint, setRemoteEndpoint] = useState('')
  const [remoteModel, setRemoteModel] = useState('')
  const [remoteProtocol, setRemoteProtocol] = useState<'rwkv' | 'openai'>('rwkv')
  const [apiKey, setAPIKey] = useState('')
  const [headers, setHeaders] = useState<HeaderRow[]>([])
  const [agentProtocol, setAgentProtocol] = useState<AgentProtocol>(AgentProtocol.AgentProtocolXML)
  const [thinking, setThinking] = useState<'off' | 'fast' | 'full'>('off')
  const [progressiveTools, setProgressiveTools] = useState(false)
  const [enableWeb, setEnableWeb] = useState(false)
  const [braveAPIKey, setBraveAPIKey] = useState('')
  const [tavilyAPIKey, setTavilyAPIKey] = useState('')
  const [enableSubagents, setEnableSubagents] = useState(false)
  const [maxActiveBatch, setMaxActiveBatch] = useState(DEFAULT_AGENT_LIMITS.maxActiveBatch)
  const [remoteBatchWaitMS, setRemoteBatchWaitMS] = useState(DEFAULT_AGENT_LIMITS.remoteBatchWaitMS)
  const [subagentMaxParallel, setSubagentMaxParallel] = useState(DEFAULT_AGENT_LIMITS.subagentMaxParallel)
  const [subagentMaxSteps, setSubagentMaxSteps] = useState(DEFAULT_AGENT_LIMITS.subagentMaxSteps)
  const [subagentTimeoutSeconds, setSubagentTimeoutSeconds] = useState(DEFAULT_AGENT_LIMITS.subagentTimeoutSeconds)
  const [availableModels, setAvailableModels] = useState<RemoteModel[]>([])
  const [settingsMessage, setSettingsMessage] = useState('')
  const [settingsBusy, setSettingsBusy] = useState(false)
  const [promptPreview, setPromptPreview] = useState<AgentPromptPreview | null>(null)
  const [previewOpen, setPreviewOpen] = useState(true)
  const [previewBusy, setPreviewBusy] = useState(false)
  const [taskControl, setTaskControl] = useState('')

  function agentCapabilityConfig() {
    return {
      agentProtocol, thinking, taskControl: taskControl.trim() || undefined, progressiveTools, enableWeb,
      braveApiKey: enableWeb ? braveAPIKey.trim() || undefined : undefined,
      tavilyApiKey: enableWeb ? tavilyAPIKey.trim() || undefined : undefined,
      enableSubagents, maxActiveBatch, remoteBatchWaitMs: remoteBatchWaitMS,
      subagentMaxParallel, subagentMaxSteps, subagentTimeoutSeconds,
    }
  }

  function localConfig() {
    return new Config({
      ...draftBaseConfig,
      provider: Provider.ProviderLocal,
      model: modelPath.trim(), tokenizerPath: tokenizerPath.trim() || undefined,
      endpoint: undefined, apiKey: undefined, password: undefined, headers: undefined,
      maxSteps: DEFAULT_AGENT_LIMITS.maxSteps, maxTokens: DEFAULT_AGENT_LIMITS.maxTokens,
      ...agentCapabilityConfig(),
    })
  }
  function remoteConfig() {
    const headerMap = Object.fromEntries(headers.map((row) => [row.name.trim(), row.value.trim()] as const).filter(([name]) => name.length > 0))
    return new Config({
      ...draftBaseConfig,
      provider: remoteProtocol === 'rwkv' ? Provider.ProviderRWKVLightning : Provider.ProviderChatCompletions,
      model: remoteModel.trim() || availableModels[0]?.id || '',
      endpoint: remoteEndpoint.trim(),
      apiKey: remoteProtocol === 'openai' ? apiKey.trim() || undefined : undefined,
      password: remoteProtocol === 'rwkv' ? apiKey.trim() || undefined : undefined,
      headers: headerMap, tokenizerPath: undefined,
      chatPromptMode: 'native-chat', chatThinking: 'disabled',
      stream: remoteProtocol === 'rwkv' ? false : undefined,
      rwkvStopTokens: remoteProtocol === 'rwkv' ? 'none' : undefined,
      maxSteps: DEFAULT_AGENT_LIMITS.maxSteps, maxTokens: DEFAULT_AGENT_LIMITS.maxTokens,
      ...agentCapabilityConfig(),
    })
  }
  function providerDraftConfig() { return settingsTab === 'local' ? localConfig() : remoteConfig() }

  const draftConfigValue = providerDraftConfig()
  const draftSignature = providerDraftSignature(draftLabel, draftConfigValue)
  const draftDirty = draftInitialized && draftSignature !== draftSnapshot
  const draftIsRunning = ready && editingProviderId !== '' && editingProviderId === runtimeProviderId && !draftDirty

  useEffect(() => {
    if (!settingsOpen || draftInitialized) return
    setDraftSnapshot(draftSignature)
    setDraftInitialized(true)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [settingsOpen, draftInitialized])

  /*
   * 系统提示词预览：设置页打开且展开时拉取，影响提示词的开关变化后防抖刷新。
   * 草稿的其他字段（地址、密钥、采样）不影响提示词，不触发刷新。
   */
  useEffect(() => {
    if (!settingsOpen || !previewOpen) return
    let cancelled = false
    const timer = setTimeout(() => {
      setPreviewBusy(true)
      Backend.PreviewSystemPrompt(providerDraftConfig())
        .then((value) => {
          if (!cancelled) setPromptPreview(value)
        })
        .catch((error) => {
          if (!cancelled) setSettingsMessage(error instanceof Error ? error.message : String(error))
        })
        .finally(() => {
          if (!cancelled) setPreviewBusy(false)
        })
    }, 350)
    return () => {
      cancelled = true
      clearTimeout(timer)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [settingsOpen, previewOpen, settingsTab, agentProtocol, thinking, progressiveTools, enableWeb, enableSubagents, taskControl])

  function applyConfig(config: Config) {
    const remote = config.provider === Provider.ProviderRWKVLightning || config.provider === Provider.ProviderChatCompletions
    setSettingsTab(remote ? 'remote' : 'local'); setModelPath(config.provider === Provider.ProviderLocal ? config.model : '')
    setTokenizerPath(config.tokenizerPath || ''); setRemoteEndpoint(remote ? config.endpoint || '' : ''); setRemoteModel(remote ? config.model : '')
    setRemoteProtocol(config.provider === Provider.ProviderChatCompletions ? 'openai' : 'rwkv'); setAPIKey(config.provider === Provider.ProviderChatCompletions ? config.apiKey || '' : config.password || '')
    setHeaders(Object.entries(config.headers || {}).map(([name, value]) => ({ id: nextHeaderID++, name, value: value || '' })))
    setAgentProtocol(config.agentProtocol || AgentProtocol.AgentProtocolXML)
    setThinking((config.thinking as 'off' | 'fast' | 'full') || 'off')
    setTaskControl(config.taskControl || '')
    setProgressiveTools(config.progressiveTools ?? false)
    setEnableWeb(config.enableWeb || false); setBraveAPIKey(config.braveApiKey || ''); setTavilyAPIKey(config.tavilyApiKey || '')
    setEnableSubagents(config.enableSubagents || false)
    setMaxActiveBatch(config.maxActiveBatch || DEFAULT_AGENT_LIMITS.maxActiveBatch)
    setRemoteBatchWaitMS(config.remoteBatchWaitMs ?? DEFAULT_AGENT_LIMITS.remoteBatchWaitMS)
    setSubagentMaxParallel(config.subagentMaxParallel || DEFAULT_AGENT_LIMITS.subagentMaxParallel)
    setSubagentMaxSteps(config.subagentMaxSteps || DEFAULT_AGENT_LIMITS.subagentMaxSteps)
    setSubagentTimeoutSeconds(config.subagentTimeoutSeconds || DEFAULT_AGENT_LIMITS.subagentTimeoutSeconds)
  }

  function applyProviderBootstrapState(value: AppBootstrap) {
    setProviders(value.providers || [])
    setActiveProviderId(value.activeProviderId || '')
    setRuntimeProviderId(value.runtimeProviderId || '')
  }

  function beginEditingProvider(provider: SavedProvider) {
    const config = Config.createFrom(provider.config)
    setDraftInitialized(false)
    setEditingProviderId(provider.id)
    setDraftLabel(provider.label || provider.config.model || '未命名连接')
    setDraftBaseConfig(config)
    setAvailableModels([])
    applyConfig(config)
  }
  function beginNewProvider() {
    const config = new Config({
      ...draftBaseConfig,
      provider: Provider.ProviderRWKVLightning,
      model: '', endpoint: '', apiKey: undefined, password: undefined, headers: {},
      chatPromptMode: 'native-chat', chatThinking: 'disabled', stream: false, rwkvStopTokens: 'none',
      maxSteps: DEFAULT_AGENT_LIMITS.maxSteps, maxTokens: DEFAULT_AGENT_LIMITS.maxTokens,
      ...agentCapabilityConfig(),
    })
    setDraftInitialized(false)
    setEditingProviderId('')
    setDraftLabel('')
    setDraftBaseConfig(config)
    setAvailableModels([])
    applyConfig(config)
  }

  function openSettings() {
    const preferred = providers.find((provider) => provider.id === runtimeProviderId)
      || providers.find((provider) => provider.id === activeProviderId)
      || providers[0]
    if (preferred) beginEditingProvider(preferred)
    else beginNewProvider()
    setSettingsMessage('')
    setSettingsOpen(true)
  }
  function discardDraft() {
    const current = providers.find((provider) => provider.id === editingProviderId)
    if (current) beginEditingProvider(current)
    else beginNewProvider()
    setSettingsMessage('已放弃未保存更改。')
  }
  function selectProvider(id: string) {
    const provider = providers.find((item) => item.id === id)
    if (provider && provider.id !== editingProviderId) beginEditingProvider(provider)
  }
  function startNewDraft() {
    beginNewProvider()
  }

  async function refreshProviders() {
    try {
      const value = await Backend.Bootstrap()
      applyProviderBootstrapState(value)
      return value
    } catch {
      return undefined
    }
  }

  async function activateProvider(id: string) {
    const configured = await Backend.ActivateProvider(id)
    onStatus(configured)
    await refreshProviders()
  }

  async function deleteProvider(id: string) {
    const value = await Backend.DeleteProvider(id)
    applyProviderBootstrapState(value)
    if (settingsOpen && id === editingProviderId) {
      const next = value.providers.find((provider) => provider.id === value.runtimeProviderId)
        || value.providers.find((provider) => provider.id === value.activeProviderId)
        || value.providers[0]
      if (next) beginEditingProvider(next)
      else beginNewProvider()
    }
  }

  async function testRemote() {
    setSettingsBusy(true); setSettingsMessage('正在请求 /v1/models…')
    try {
      const models = await Backend.ListRemoteModels(remoteConfig())
      setAvailableModels(models)
      if (!remoteModel && models[0]) setRemoteModel(models[0].id)
      setSettingsMessage(`连接成功，发现 ${models.length} 个模型。`)
    } catch (error) {
      setSettingsMessage(error instanceof Error ? error.message : String(error))
    } finally {
      setSettingsBusy(false)
    }
  }

  async function saveProviderDraft(): Promise<boolean> {
    setSettingsBusy(true)
    setSettingsMessage('正在保存连接档案…')
    try {
      const saved = await Backend.SaveProvider(editingProviderId, draftLabel.trim(), draftConfigValue)
      await refreshProviders()
      beginEditingProvider(saved)
      setSettingsMessage(ready ? '档案已保存；当前运行连接保持不变，要使更改生效请点「保存并使用」。' : '档案已保存，尚未连接。')
      return true
    } catch (error) {
      setSettingsMessage(error instanceof Error ? error.message : String(error))
      return false
    } finally {
      setSettingsBusy(false)
    }
  }

  async function saveAndUseProviderDraft() {
    setSettingsBusy(true)
    setSettingsMessage(settingsTab === 'local' ? '正在保存并加载本地模型，这可能需要一些时间…' : '正在保存并切换远端连接…')
    try {
      const configured = await Backend.ConfigureProvider(editingProviderId, draftLabel.trim(), draftConfigValue)
      onStatus(configured)
      const value = await refreshProviders()
      const running = value?.providers.find((provider) => provider.id === value.runtimeProviderId)
      if (running) beginEditingProvider(running)
      else setDraftSnapshot(providerDraftSignature(draftLabel, draftConfigValue))
      setSettingsMessage('已保存并切换为当前运行连接。')
    } catch (error) {
      setSettingsMessage(error instanceof Error ? error.message : String(error))
    } finally {
      setSettingsBusy(false)
    }
  }

  return {
    // 展示状态
    settingsOpen, setSettingsOpen,
    providers, activeProviderId, runtimeProviderId, editingProviderId,
    draftLabel, setDraftLabel, draftDirty, draftIsRunning,
    settingsTab, setSettingsTab,
    modelPath, setModelPath, tokenizerPath, setTokenizerPath,
    remoteEndpoint, setRemoteEndpoint, remoteModel, setRemoteModel,
    remoteProtocol, setRemoteProtocol, apiKey, setAPIKey, headers, setHeaders,
    agentProtocol, setAgentProtocol, thinking, setThinking, progressiveTools, setProgressiveTools,
    enableWeb, setEnableWeb, braveAPIKey, setBraveAPIKey, tavilyAPIKey, setTavilyAPIKey,
    enableSubagents, setEnableSubagents, maxActiveBatch, setMaxActiveBatch,
    remoteBatchWaitMS, setRemoteBatchWaitMS, subagentMaxParallel, setSubagentMaxParallel,
    subagentMaxSteps, setSubagentMaxSteps, subagentTimeoutSeconds, setSubagentTimeoutSeconds,
    availableModels, setAvailableModels,
    settingsMessage, setSettingsMessage, settingsBusy,
    promptPreview, previewOpen, setPreviewOpen, previewBusy,
    taskControl, setTaskControl,
    // 派生
    draftConfigValue,
    // 动作
    openSettings, discardDraft, selectProvider, startNewDraft,
    applyProviderBootstrapState, applyConfig, refreshProviders,
    activateProvider, deleteProvider, testRemote,
    saveProviderDraft, saveAndUseProviderDraft,
  }
}

export type ProviderManager = ReturnType<typeof useProviderManager>
