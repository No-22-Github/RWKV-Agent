import { useEffect, useRef, useState } from 'react'
import { Events } from '@wailsio/runtime'
import {
  AgentPromptPreview, AgentProtocol, Config, Provider, Status, type RemoteModel,
} from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { AppBootstrap } from '../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/models'
import type { SavedProvider } from '../../bindings/github.com/no22/RWKV-Agent/internal/appstorage/models'
import * as Backend from '../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import { derivedProviderLabel, firstDraftError, validateDraft } from './draftValidation'
import { DEFAULT_SAMPLING, matchSamplingPreset, normalizeSampling, presetById } from './samplingPresets'

/* 自动保存的防抖：停止输入这么久后才落盘，敲到一半的值不会触发保存或重连。 */
export const AUTOSAVE_DELAY_MS = 800

/*
 * 自动保存状态机。idle：没有待保存内容；pending：等防抖；saving：请求进行中；
 * saved：最近一次保存成功（message 说明是否已生效）；invalid：字段校验未通过，
 * 不会保存；error：后端拒绝（message 为原因，同一份草稿不会自动重试）。
 */
export type SaveState =
  | { kind: 'idle' | 'pending' | 'saving'; message?: string }
  | { kind: 'saved' | 'invalid' | 'error'; message: string }

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

/* 只看配置、不看名称的签名：改名不应触发重连。 */
function configSignature(config: Config): string {
  return JSON.stringify(stableValue(config))
}

/*
 * 连接档案域的唯一状态所有者：档案列表、编辑器表单、脏标记与全部档案动作。
 * App 只保留聊天/会话域状态，通过这里的方法操作设置。
 *
 * 保存模型：已有档案的全部字段（连接、参数、Agent）停止输入 AUTOSAVE_DELAY_MS 后
 * 自动保存；校验不过的草稿只提示、不保存。编辑的是运行中的远端档案时直接重连，
 * 更改即时生效；本地模型需要重新加载（重的操作，不由敲字触发），档案保存后标
 * 「待重新加载」，由用户点「重新加载模型」。新建连接没有档案 ID，仍由显式的
 * 「保存」/「保存并使用」建档，避免半截输入生成垃圾档案。
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
  const [stateId, setStateId] = useState('')
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
  const [saveState, setSaveState] = useState<SaveState>({ kind: 'idle' })
  // 运行中连接实际使用的配置（bootstrap.config），与档案的已保存配置分开：
  // 能力指示与"待重新加载"都以它为准，而不是以正在编辑的草稿为准。
  const [runtimeConfig, setRuntimeConfig] = useState<Config | null>(null)
  const [runtimeOutdated, setRuntimeOutdated] = useState(false)
  // 同步镜像：draftSnapshot 是渲染用的 state，这里的 ref 供异步保存流程读取最新基线。
  const snapshotRef = useRef('')
  const snapshotConfigRef = useRef('')
  const inFlightRef = useRef<Promise<boolean> | null>(null)
  // 后端拒绝过的草稿签名：同一份内容不再自动重试，改动任意字段后恢复。
  const failedSignatureRef = useRef('')

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
      endpoint: undefined, apiKey: undefined, password: undefined, headers: undefined, stateId: undefined,
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
      // 流式由后端统一决定（App 一律流式显示回答），旧档案里的 stream:false 不再带出去。
      stream: undefined,
      rwkvStopTokens: remoteProtocol === 'openai' ? undefined : stops,
      // 只有 CUDA 支持上传的 State；切到别的协议时不带出去，否则 Python 会直接拒绝。
      stateId: remoteProtocol === 'cuda' ? stateId.trim() || undefined : undefined,
      ...agentCapabilityConfig(),
    })
  }
  function providerDraftConfig() { return settingsTab === 'local' ? localConfig() : remoteConfig() }

  const draftConfigValue = providerDraftConfig()
  const draftSignature = providerDraftSignature(draftLabel, draftConfigValue)
  const draftDirty = draftInitialized && draftSignature !== draftSnapshot
  const draftIsRunning = ready && editingProviderId !== '' && editingProviderId === runtimeProviderId && !draftDirty
  const draftErrors = validateDraft(draftConfigValue)
  const draftError = firstDraftError(draftErrors)
  // 运行中的本地档案已保存、但加载的还是旧配置：需要用户显式重新加载。
  const draftNeedsReload = draftIsRunning && runtimeOutdated

  useEffect(() => {
    if (!settingsOpen || draftInitialized) return
    setDraftSnapshot(draftSignature)
    snapshotRef.current = draftSignature
    snapshotConfigRef.current = configSignature(draftConfigValue)
    failedSignatureRef.current = ''
    setDraftInitialized(true)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [settingsOpen, draftInitialized])

  /* 档案列表的单一刷新入口：后端任何档案变更（任一窗口、任一入口）都广播这个事件。 */
  useEffect(() => {
    const off = Events.On('providers:changed', () => { void refreshProviders() })
    return () => { off() }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

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
   * 自动保存一次：只对已有档案生效。先 SaveProvider（后端校验唯一性、落盘），编辑的是
   * 运行中的远端档案且配置真的变了才 ConfigureProvider 重连——改名不重连；本地模型只
   * 保存，由 runtimeOutdated 提示重新加载。保存成功后只推进脏基线、刷新列表，绝不重新
   * 水合表单：用户在请求期间继续输入的内容不会被覆盖，而会在下一轮防抖里保存。
   */
  async function persistDraft(): Promise<boolean> {
    if (inFlightRef.current) await inFlightRef.current
    const id = editingProviderId
    const label = draftLabel.trim()
    const config = draftConfigValue
    const signature = providerDraftSignature(draftLabel, config)
    if (!id) return false
    if (signature === snapshotRef.current) return true
    const error = firstDraftError(validateDraft(config))
    if (error) {
      setSaveState({ kind: 'invalid', message: error })
      return false
    }
    const remote = config.provider !== Provider.ProviderLocal
    const running = ready && id === runtimeProviderId
    const configChanged = configSignature(config) !== snapshotConfigRef.current
    const reconnect = running && remote && configChanged
    const task = (async () => {
      setSaveState({ kind: 'saving', message: reconnect ? '正在应用…' : '正在自动保存…' })
      try {
        await Backend.SaveProvider(id, label, config)
        if (reconnect) onStatus(await Backend.ConfigureProvider(id, label, config))
        snapshotRef.current = signature
        snapshotConfigRef.current = configSignature(config)
        failedSignatureRef.current = ''
        setDraftSnapshot(signature)
        const value = await refreshProviders()
        const outdated = Boolean(value?.runtimeOutdated && value.runtimeProviderId === id)
        setSaveState({
          kind: 'saved',
          message: reconnect ? '已自动生效' : outdated ? '已自动保存；重新加载模型后生效' : '已自动保存',
        })
        return true
      } catch (reason) {
        failedSignatureRef.current = signature
        setSaveState({ kind: 'error', message: `保存失败：${errorText(reason)}` })
        return false
      }
    })()
    inFlightRef.current = task
    try {
      return await task
    } finally {
      if (inFlightRef.current === task) inFlightRef.current = null
    }
  }

  /* 防抖触发自动保存；校验不过或后端拒绝过的同一份草稿不发请求。 */
  useEffect(() => {
    if (!settingsOpen || !draftInitialized || settingsBusy || editingProviderId === '') return
    if (!draftDirty) {
      setSaveState((current) => current.kind === 'pending' || current.kind === 'invalid' ? { kind: 'idle' } : current)
      return
    }
    if (draftError) {
      setSaveState({ kind: 'invalid', message: draftError })
      return
    }
    if (draftSignature === failedSignatureRef.current) return
    setSaveState((current) => current.kind === 'saving' ? current : { kind: 'pending', message: '待保存…' })
    const timer = setTimeout(() => { void persistDraft() }, AUTOSAVE_DELAY_MS)
    return () => clearTimeout(timer)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [settingsOpen, draftInitialized, settingsBusy, editingProviderId, draftDirty, draftSignature, draftError])

  /*
   * 离开当前草稿（关闭设置、切换或新建档案）前调用：把防抖中的更改立即落盘。
   * 返回 true 表示可以直接离开；false 表示草稿无法自动保存（新建连接未建档、
   * 校验不过或保存失败），调用方应弹确认框，原因见 draftBlockReason。
   */
  async function flushDraft(): Promise<boolean> {
    if (inFlightRef.current) await inFlightRef.current
    if (editingProviderId === '') return !draftDirty
    if (providerDraftSignature(draftLabel, draftConfigValue) === snapshotRef.current) return true
    return persistDraft()
  }
  const draftBlockReason = editingProviderId === ''
    ? '新连接还没有保存。'
    : draftError
      ? `当前更改无法保存：${draftError}`
      : saveState.kind === 'error' ? saveState.message : ''

  function applyConfig(config: Config) {
    const remote = config.provider === Provider.ProviderRWKVLightningPython || config.provider === Provider.ProviderRWKVLightningCUDA || config.provider === Provider.ProviderChatCompletions
    setSettingsTab(remote ? 'remote' : 'local'); setModelPath(config.provider === Provider.ProviderLocal ? config.model : '')
    setTokenizerPath(config.tokenizerPath || ''); setRemoteEndpoint(remote ? config.endpoint || '' : ''); setRemoteModel(remote ? config.model : '')
    setRemoteProtocol(config.provider === Provider.ProviderChatCompletions ? 'openai' : config.provider === Provider.ProviderRWKVLightningPython ? 'python' : 'cuda'); setAPIKey(config.provider === Provider.ProviderChatCompletions ? config.apiKey || '' : config.password || '')
    setStateId(config.provider === Provider.ProviderRWKVLightningCUDA ? config.stateId || '' : '')
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
    // 水合即基线（由 draftInitialized 效果记录）：打开设置永远不会触发保存或重连。
    setSaveState({ kind: 'idle' })
  }

  function applyProviderBootstrapState(value: AppBootstrap) {
    setProviders(value.providers || [])
    setActiveProviderId(value.activeProviderId || '')
    setRuntimeProviderId(value.runtimeProviderId || '')
    setRuntimeConfig(value.runtimeProviderId ? Config.createFrom(value.config) : null)
    setRuntimeOutdated(Boolean(value.runtimeOutdated))
  }

  function beginEditingProvider(provider: SavedProvider) {
    const config = Config.createFrom(provider.config)
    setDraftInitialized(false)
    setEditingProviderId(provider.id)
    // 自动名（与后端派生规则一致）在表单里留空：改模型或地址后名称随之更新，而不是冻结成旧模型名。
    setDraftLabel(provider.label && provider.label !== derivedProviderLabel(config) ? provider.label : '')
    setDraftBaseConfig(config)
    setAvailableModels([])
    applyConfig(config)
  }
  function beginNewProvider() {
    const config = new Config({
      ...draftBaseConfig,
      provider: Provider.ProviderRWKVLightningCUDA,
      model: '', endpoint: '', apiKey: undefined, password: undefined, headers: {}, stateId: undefined,
      chatPromptMode: 'native-chat', chatThinking: 'disabled', rwkvStopTokens: 'eos',
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
    } catch (error) {
      // 刷新失败不能静默：否则列表停在旧状态、看起来像"没保存上"。
      setSettingsMessage(`刷新连接列表失败：${errorText(error)}`)
      return undefined
    }
  }

  /*
   * 顶栏下拉里的能力开关：直接改运行中档案的一个字段并重连生效（远端重连不加载模型，
   * 对话历史由后端在下一轮恢复）。本地模型重配要重新加载，不走这里。
   */
  async function setRuntimeCapability(key: 'enableWeb' | 'enableSubagents', value: boolean) {
    const provider = providers.find((item) => item.id === runtimeProviderId)
    if (!provider || provider.config.provider === Provider.ProviderLocal) return
    const config = new Config({ ...provider.config, [key]: value })
    onStatus(await Backend.ConfigureProvider(provider.id, provider.label, config))
    await refreshProviders()
  }

  /** 切换运行中连接的 State（仅 Lightning CUDA）；空串表示不使用 State。 */
  async function setRuntimeState(stateId: string) {
    const provider = providers.find((item) => item.id === runtimeProviderId)
    if (!provider || provider.config.provider !== Provider.ProviderRWKVLightningCUDA) return
    const config = new Config({ ...provider.config, stateId: stateId || undefined })
    onStatus(await Backend.ConfigureProvider(provider.id, provider.label, config))
    await refreshProviders()
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

  /* 显式保存：新建连接建档用（已有档案自动保存，界面上不再提供这个按钮）。 */
  async function saveProviderDraft(): Promise<boolean> {
    if (inFlightRef.current) await inFlightRef.current
    setSettingsBusy(true)
    setSettingsMessage('正在保存连接档案…')
    try {
      const saved = await Backend.SaveProvider(editingProviderId, draftLabel.trim(), draftConfigValue)
      await refreshProviders()
      beginEditingProvider(saved)
      setSettingsMessage(ready ? '档案已保存；当前运行连接保持不变，点「使用此连接」切换。' : '档案已保存，尚未连接。')
      return true
    } catch (error) {
      setSettingsMessage(errorText(error))
      return false
    } finally {
      setSettingsBusy(false)
    }
  }

  /* 保存并切换为运行连接；也是本地模型的「加载/重新加载模型」。 */
  async function saveAndUseProviderDraft() {
    if (inFlightRef.current) await inFlightRef.current
    setSettingsBusy(true)
    setSettingsMessage(settingsTab === 'local' ? '正在加载本地模型，这可能需要一些时间…' : '正在切换远端连接…')
    try {
      const configured = await Backend.ConfigureProvider(editingProviderId, draftLabel.trim(), draftConfigValue)
      onStatus(configured)
      const value = await refreshProviders()
      const running = value?.providers.find((provider) => provider.id === value.runtimeProviderId)
      if (running) beginEditingProvider(running)
      else setDraftSnapshot(providerDraftSignature(draftLabel, draftConfigValue))
      setSettingsMessage(settingsTab === 'local' ? '模型已加载，成为当前运行连接。' : '已切换为当前运行连接。')
    } catch (error) {
      setSettingsMessage(errorText(error))
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
    stateId, setStateId,
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
    saveState, runtimeConfig, runtimeOutdated,
    // 派生
    draftConfigValue, draftErrors, draftError, draftNeedsReload, draftBlockReason,
    // 动作
    openSettings, discardDraft, selectProvider, startNewDraft,
    applyProviderBootstrapState, applyConfig, refreshProviders,
    activateProvider, setRuntimeCapability, setRuntimeState, deleteProvider, testRemote,
    saveProviderDraft, saveAndUseProviderDraft, flushDraft,
  }
}

function errorText(error: unknown): string {
  return error instanceof Error ? error.message : String(error)
}

export type ProviderManager = ReturnType<typeof useProviderManager>
