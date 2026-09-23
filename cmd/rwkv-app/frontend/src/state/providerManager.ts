import { useEffect, useRef, useState } from 'react'
import {
  AgentPromptPreview, AgentProtocol, Config, Provider, Status, type RemoteModel,
} from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { AppBootstrap } from '../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/models'
import type { SavedProvider } from '../../bindings/github.com/no22/RWKV-Agent/internal/appstorage/models'
import * as Backend from '../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import { DEFAULT_SAMPLING, matchSamplingPreset, normalizeSampling, presetById } from './samplingPresets'

const REMOTE_BACKENDS = {
  openai: { provider: Provider.ProviderChatCompletions, stops: undefined },
  python: { provider: Provider.ProviderRWKVLightningPython, stops: 'text' },
  cuda: { provider: Provider.ProviderRWKVLightningCUDA, stops: 'eos' },
} as const

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

/* 决策阶段输出预算的"自动"：0 让后端按协议挑默认（XML 512，其余 96）。 */
const DECISION_MAX_TOKENS_AUTO = 0

/*
 * Agent 行为字段的签名：只覆盖 Agent 分区的开关（协议、思考、约定、网页、子
 * Agent 与预算），连接身份字段（地址、密钥、名称）不参与。自动保存/重连以它为
 * 触发器，因此打开设置或编辑连接字段永远不会引发重连。缺省值归一必须与上面
 * DEFAULT_AGENT_LIMITS 及后端 normalizeConfig 保持一致。
 */
function agentBehaviorSignatureOf(config: Config): string {
  const sampling = normalizeSampling(config)
  return JSON.stringify(stableValue({
    agentProtocol: config.agentProtocol || AgentProtocol.AgentProtocolXML,
    thinking: config.thinking || 'off',
    taskControl: (config.taskControl || '').trim() || undefined,
    progressiveTools: config.progressiveTools ?? false,
    enableWeb: config.enableWeb || false,
    braveApiKey: config.enableWeb ? config.braveApiKey || undefined : undefined,
    tavilyApiKey: config.enableWeb ? config.tavilyApiKey || undefined : undefined,
    enableSubagents: config.enableSubagents || false,
    maxActiveBatch: config.maxActiveBatch || DEFAULT_AGENT_LIMITS.maxActiveBatch,
    remoteBatchWaitMs: config.remoteBatchWaitMs ?? DEFAULT_AGENT_LIMITS.remoteBatchWaitMS,
    subagentMaxParallel: config.subagentMaxParallel || DEFAULT_AGENT_LIMITS.subagentMaxParallel,
    subagentMaxSteps: config.subagentMaxSteps || DEFAULT_AGENT_LIMITS.subagentMaxSteps,
    subagentTimeoutSeconds: config.subagentTimeoutSeconds || DEFAULT_AGENT_LIMITS.subagentTimeoutSeconds,
    // 步数与输出预算过去是前端写死的常量，所以不在签名里；现在可调，必须参与。
    maxSteps: config.maxSteps || DEFAULT_AGENT_LIMITS.maxSteps,
    maxTokens: config.maxTokens || DEFAULT_AGENT_LIMITS.maxTokens,
    decisionMaxTokens: config.decisionMaxTokens ?? DECISION_MAX_TOKENS_AUTO,
    // 采样走归一后的值：未设置与 greedy 是同一份配置，打开设置不该触发重连。
    ...sampling,
  }))
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
  const [remoteProtocol, setRemoteProtocol] = useState<keyof typeof REMOTE_BACKENDS>('cuda')
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
  const [maxSteps, setMaxSteps] = useState(DEFAULT_AGENT_LIMITS.maxSteps)
  const [maxTokens, setMaxTokens] = useState(DEFAULT_AGENT_LIMITS.maxTokens)
  const [decisionMaxTokens, setDecisionMaxTokens] = useState(DECISION_MAX_TOKENS_AUTO)
  const [sampleTemperature, setSampleTemperature] = useState(DEFAULT_SAMPLING.temperature)
  const [sampleTopK, setSampleTopK] = useState(DEFAULT_SAMPLING.topK)
  const [sampleTopP, setSampleTopP] = useState(DEFAULT_SAMPLING.topP)
  const [samplePresencePenalty, setSamplePresencePenalty] = useState(DEFAULT_SAMPLING.presencePenalty)
  const [sampleFrequencyPenalty, setSampleFrequencyPenalty] = useState(DEFAULT_SAMPLING.frequencyPenalty)
  const [samplePenaltyDecay, setSamplePenaltyDecay] = useState(DEFAULT_SAMPLING.penaltyDecay)
  const [advancedSampling, setAdvancedSampling] = useState(false)
  const [availableModels, setAvailableModels] = useState<RemoteModel[]>([])
  const [settingsMessage, setSettingsMessage] = useState('')
  const [settingsBusy, setSettingsBusy] = useState(false)
  const [promptPreview, setPromptPreview] = useState<AgentPromptPreview | null>(null)
  const [previewOpen, setPreviewOpen] = useState(true)
  const [previewBusy, setPreviewBusy] = useState(false)
  const [taskControl, setTaskControl] = useState('')
  const [autoApplyNote, setAutoApplyNote] = useState('')
  const appliedAgentSignatureRef = useRef('')

  const samplingValues = normalizeSampling({
    temperature: sampleTemperature, topK: sampleTopK, topP: sampleTopP,
    presencePenalty: samplePresencePenalty, frequencyPenalty: sampleFrequencyPenalty, penaltyDecay: samplePenaltyDecay,
  })
  /*
   * 反查当前数值属于哪个预设。数值被改过（或档案里存着一组非预设的组合）就报自定义，
   * 并把高级输入展开——否则选择器会显示一个名字，而实际发出去的是别的数。
   */
  const matchedSamplingPreset = matchSamplingPreset(samplingValues)
  const samplingIsCustom = advancedSampling || matchedSamplingPreset === ''

  function agentCapabilityConfig() {
    return {
      agentProtocol, thinking, taskControl: taskControl.trim() || undefined, progressiveTools, enableWeb,
      braveApiKey: enableWeb ? braveAPIKey.trim() || undefined : undefined,
      tavilyApiKey: enableWeb ? tavilyAPIKey.trim() || undefined : undefined,
      enableSubagents, maxActiveBatch, remoteBatchWaitMs: remoteBatchWaitMS,
      subagentMaxParallel, subagentMaxSteps, subagentTimeoutSeconds,
      maxSteps, maxTokens, decisionMaxTokens,
      ...samplingValues,
    }
  }

  /* 选中一个预设：六个参数一起写成测量过的那组值；选"自定义"只展开输入，不动数值。 */
  function applySamplingPreset(id: string) {
    const preset = presetById(id)
    if (!preset) {
      setAdvancedSampling(true)
      return
    }
    setSampleTemperature(preset.temperature); setSampleTopK(preset.topK); setSampleTopP(preset.topP)
    setSamplePresencePenalty(preset.presencePenalty); setSampleFrequencyPenalty(preset.frequencyPenalty)
    setSamplePenaltyDecay(preset.penaltyDecay)
    setAdvancedSampling(false)
  }

  function localConfig() {
    return new Config({
      ...draftBaseConfig,
      provider: Provider.ProviderLocal,
      model: modelPath.trim(), tokenizerPath: tokenizerPath.trim() || undefined,
      endpoint: undefined, apiKey: undefined, password: undefined, headers: undefined,
      ...agentCapabilityConfig(),
    })
  }
  function remoteConfig() {
    const backend = REMOTE_BACKENDS[remoteProtocol]
    const stops = draftBaseConfig.provider === backend.provider ? draftBaseConfig.rwkvStopTokens || backend.stops : backend.stops
    const headerMap = Object.fromEntries(headers.map((row) => [row.name.trim(), row.value.trim()] as const).filter(([name]) => name.length > 0))
    return new Config({
      ...draftBaseConfig,
      provider: backend.provider,
      model: remoteModel.trim() || availableModels[0]?.id || '',
      endpoint: remoteEndpoint.trim(),
      apiKey: remoteProtocol === 'openai' ? apiKey.trim() || undefined : undefined,
      password: remoteProtocol !== 'openai' ? apiKey.trim() || undefined : undefined,
      headers: headerMap, tokenizerPath: undefined,
      chatPromptMode: 'native-chat', chatThinking: 'disabled',
      stream: remoteProtocol !== 'openai' ? draftBaseConfig.stream ?? false : undefined,
      rwkvStopTokens: remoteProtocol === 'openai' ? undefined : stops,
      ...agentCapabilityConfig(),
    })
  }
  function providerDraftConfig() { return settingsTab === 'local' ? localConfig() : remoteConfig() }

  const draftConfigValue = providerDraftConfig()
  const draftSignature = providerDraftSignature(draftLabel, draftConfigValue)
  const draftDirty = draftInitialized && draftSignature !== draftSnapshot
  const draftIsRunning = ready && editingProviderId !== '' && editingProviderId === runtimeProviderId && !draftDirty
  const agentBehaviorSignature = agentBehaviorSignatureOf(draftConfigValue)

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

  /*
   * Agent 行为自动应用：分区里的开关变化后防抖落盘。编辑的是运行中的远端档案时
   * 直接 ConfigureProvider（保存 + 激活 + 重连一体），更改即时生效；本地模型档案
   * 与未运行的档案只自动保存——本地重连意味着重新加载模型，不能由敲字触发；
   * 新建草稿（尚无档案 ID）不自动落盘，仍由连接页的保存动作建立档案。
   */
  useEffect(() => {
    if (!settingsOpen || !draftInitialized || settingsBusy) return
    if (editingProviderId === '') return
    if (agentBehaviorSignature === appliedAgentSignatureRef.current) return
    const timer = setTimeout(() => {
      const config = providerDraftConfig()
      const remote = config.provider !== Provider.ProviderLocal
      const running = editingProviderId !== '' && editingProviderId === runtimeProviderId
      const apply = async () => {
        setAutoApplyNote(running && remote ? '正在应用…' : '正在自动保存…')
        if (running && remote) {
          const status = await Backend.ConfigureProvider(editingProviderId, draftLabel.trim(), config)
          onStatus(status)
          await refreshProviders()
          setAutoApplyNote('已自动生效')
        } else {
          await Backend.SaveProvider(editingProviderId, draftLabel.trim(), config)
          await refreshProviders()
          setAutoApplyNote(running ? '已自动保存；本地模型将在下次连接时生效' : '已自动保存')
        }
        // 自动应用后把脏基线推到当前值：切换档案/关闭设置不再弹确认框。
        appliedAgentSignatureRef.current = agentBehaviorSignatureOf(config)
        setDraftSnapshot(providerDraftSignature(draftLabel, config))
      }
      apply().catch((error) => {
        setAutoApplyNote('')
        setSettingsMessage(error instanceof Error ? error.message : String(error))
      })
    }, 800)
    return () => clearTimeout(timer)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [settingsOpen, draftInitialized, settingsBusy, editingProviderId, runtimeProviderId, agentBehaviorSignature, draftLabel])

  function applyConfig(config: Config) {
    const remote = config.provider === Provider.ProviderRWKVLightningPython || config.provider === Provider.ProviderRWKVLightningCUDA || config.provider === Provider.ProviderChatCompletions
    setSettingsTab(remote ? 'remote' : 'local'); setModelPath(config.provider === Provider.ProviderLocal ? config.model : '')
    setTokenizerPath(config.tokenizerPath || ''); setRemoteEndpoint(remote ? config.endpoint || '' : ''); setRemoteModel(remote ? config.model : '')
    setRemoteProtocol(config.provider === Provider.ProviderChatCompletions ? 'openai' : config.provider === Provider.ProviderRWKVLightningPython ? 'python' : 'cuda'); setAPIKey(config.provider === Provider.ProviderChatCompletions ? config.apiKey || '' : config.password || '')
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
    setMaxSteps(config.maxSteps || DEFAULT_AGENT_LIMITS.maxSteps)
    setMaxTokens(config.maxTokens || DEFAULT_AGENT_LIMITS.maxTokens)
    setDecisionMaxTokens(config.decisionMaxTokens ?? DECISION_MAX_TOKENS_AUTO)
    const sampling = normalizeSampling(config)
    setSampleTemperature(sampling.temperature); setSampleTopK(sampling.topK); setSampleTopP(sampling.topP)
    setSamplePresencePenalty(sampling.presencePenalty); setSampleFrequencyPenalty(sampling.frequencyPenalty)
    setSamplePenaltyDecay(sampling.penaltyDecay)
    // 存着一组非预设数值的档案直接进高级模式，否则选择器会顶着一个不成立的名字。
    setAdvancedSampling(matchSamplingPreset(sampling) === '')
    // 水合即基线：自动应用效果只看这里之后的增量，打开设置永远不会触发重连。
    appliedAgentSignatureRef.current = agentBehaviorSignatureOf(config)
    setAutoApplyNote('')
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
      provider: Provider.ProviderRWKVLightningCUDA,
      model: '', endpoint: '', apiKey: undefined, password: undefined, headers: {},
      chatPromptMode: 'native-chat', chatThinking: 'disabled', stream: false, rwkvStopTokens: 'eos',
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
    maxSteps, setMaxSteps, maxTokens, setMaxTokens,
    decisionMaxTokens, setDecisionMaxTokens,
    sampleTemperature, setSampleTemperature, sampleTopK, setSampleTopK,
    sampleTopP, setSampleTopP, samplePresencePenalty, setSamplePresencePenalty,
    sampleFrequencyPenalty, setSampleFrequencyPenalty, samplePenaltyDecay, setSamplePenaltyDecay,
    samplingValues, matchedSamplingPreset, samplingIsCustom, applySamplingPreset,
    availableModels, setAvailableModels,
    settingsMessage, setSettingsMessage, settingsBusy,
    promptPreview, previewOpen, setPreviewOpen, previewBusy,
    taskControl, setTaskControl,
    autoApplyNote,
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
