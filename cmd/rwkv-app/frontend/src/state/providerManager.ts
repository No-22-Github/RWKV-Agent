import { useEffect, useRef, useState } from 'react'
import { Events } from '@wailsio/runtime'
import { AgentProtocol, Config, Provider, Status, type RemoteModel } from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { AppBootstrap } from '../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/models'
import type { SavedProvider } from '../../bindings/github.com/no22/RWKV-Agent/internal/appstorage/models'
import * as Backend from '../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import { firstDraftError, isAutoProviderLabel, validateDraft } from './draftValidation'
import { DEFAULT_SAMPLING, NEW_CONFIG_SAMPLING_ID, presetById } from './samplingPresets'
import { formatPresetById, formatSelection } from './formatPresets'
import { useSnackbar } from '../snackbar'

/* 自动保存的防抖：停止输入这么久后才落盘，敲到一半的值不会触发保存或重连。 */
export const AUTOSAVE_DELAY_MS = 800

/*
 * 自动保存状态机。idle：没有待保存内容；pending：等防抖；saving：请求进行中；
 * saved：最近一次保存成功（message 说明是否已生效）；invalid：字段校验未通过，
 * 不会保存；error：后端拒绝（message 为原因，同一份草稿不会自动重试）。
 */
/* 设置弹窗的分区；远端连接与本地推理各管一类档案。 */
export type SettingsSection = '远端连接' | '本地推理' | 'Agent' | '外观' | '通用'
export type SettingsFocus = 'state' | 'adapter' | null
export type OpenSettingsOptions = { detail?: boolean; focus?: SettingsFocus }
export type ProviderKind = 'remote' | 'local'

export function kindOf(config: Config): ProviderKind {
  return config.provider === Provider.ProviderLocal ? 'local' : 'remote'
}

export type SaveState =
  | { kind: 'idle' | 'pending' | 'saving'; message?: string }
  | { kind: 'saved' | 'invalid' | 'error'; message: string }

const REMOTE_BACKENDS = {
  openai: { provider: Provider.ProviderChatCompletions, stops: undefined },
  python: { provider: Provider.ProviderRWKVLightningPython, stops: 'text' },
  cuda: { provider: Provider.ProviderRWKVLightningCUDA, stops: 'eos' },
  irwkv: { provider: Provider.ProviderIRWKV, stops: 'text' },
} as const

export type RemoteProtocol = keyof typeof REMOTE_BACKENDS

/* 连接列表和运行配置里显示的协议名。 */
export function remoteProtocolLabel(provider: Config['provider']): string {
  switch (provider) {
    case Provider.ProviderChatCompletions: return 'OpenAI 兼容'
    case Provider.ProviderRWKVLightningPython: return 'Lightning Python'
    case Provider.ProviderIRWKV: return 'iRWKV'
    default: return 'Lightning CUDA'
  }
}

/* OpenAI 兼容和 iRWKV 用 Bearer API Key；Lightning 用请求体里的服务密码。 */
function usesAPIKey(protocol: RemoteProtocol): boolean {
  return protocol === 'openai' || protocol === 'irwkv'
}

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
 * 连接自己的批处理参数默认值，与后端 api/service.go normalizeConfig 的缺省值一致：
 * 两个都是在建连接时读的（本地合批、远端聚合窗口），所以跟着连接存，不进共用设置。
 */
const DEFAULT_CONNECTION_LIMITS = {
  maxActiveBatch: 4,
  remoteBatchWaitMS: 10,
}

/*
 * 新档案的默认值，对应后端 api.NewConfigDefaults（api/defaults.go）：新连接的对话格式是评测与
 * 训练语料用的 agent-wire-v1.0（原名 g1k）；其余各项是共用设置第一次建立时的默认值（后端迁移
 * 时写入，见 appstorage.AgentSettings）——agent-default 采样、联网/天气/bash 默认开。
 * 已保存的档案按自己存的格式水合，不会被改写。
 */
export const NEW_CONFIG_DEFAULTS = {
  profile: 'agent-wire-v1.0',
  enableWeb: true,
  enableBash: true,
  weatherBackend: 'open-meteo',
  sampling: presetById(NEW_CONFIG_SAMPLING_ID) ?? DEFAULT_SAMPLING,
  /* agent-wire-v1.0 第一步几乎都会先思考：决策 512 会截断思考，规程定的是 2048 / 4096（docs/evaluations/benchmark-protocol.md）。 */
  maxTokens: 4096,
  decisionMaxTokens: 2048,
}

/* 只看配置、不看名称的签名：改名不应触发重连。 */
function configSignature(config: Config): string {
  return JSON.stringify(stableValue(config))
}

/*
 * 连接档案域的唯一状态所有者：档案列表、编辑器表单、脏标记与全部档案动作。
 * App 只保留聊天/会话域状态，通过这里的方法操作设置。
 *
 * 档案只管连接本身：地址、模型、凭据与批处理参数。对话格式、State 与 MiSS 适配器也记在档案里，
 * 但在对话页的芯片里改（后端保存草稿时沿用档案里的值）；生成参数、工具与提示词是所有连接共用的，
 * 见 agentSettings.ts。
 *
 * 保存模型：已有档案的字段停止输入 AUTOSAVE_DELAY_MS 后
 * 自动保存；校验不过的草稿只提示、不保存。编辑的是运行中的远端档案时直接重连，
 * 更改即时生效；本地模型需要重新加载（重的操作，不由敲字触发），档案保存后标
 * 「待重新加载」，由用户点「重新加载模型」。新建连接没有档案 ID，仍由显式的
 * 「保存」/「保存并使用」建档，避免半截输入生成垃圾档案。
 */
export function useProviderManager({ onStatus, ready }: { onStatus: (status: Status) => void; ready: boolean }) {
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [settingsSection, setSettingsSection] = useState<SettingsSection>('远端连接')
  // 连接分区是两层：先看列表，点进一行才看详情。新建草稿永远在详情里。
  const [settingsDetail, setSettingsDetail] = useState(false)
  // 从对话页「管理」入口进来时要直接展开的折叠项；只在打开那一刻读一次。
  const [settingsFocus, setSettingsFocus] = useState<SettingsFocus>(null)
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
  const [remoteProtocol, setRemoteProtocol] = useState<RemoteProtocol>('cuda')
  const [apiKey, setAPIKey] = useState('')
  /* 网页版（server 模式）没有系统文件对话框，上传改走浏览器的文件选择框。 */
  const [browserUploads, setBrowserUploads] = useState(false)
  const [headers, setHeaders] = useState<HeaderRow[]>([])
  const [maxActiveBatch, setMaxActiveBatch] = useState(DEFAULT_CONNECTION_LIMITS.maxActiveBatch)
  const [remoteBatchWaitMS, setRemoteBatchWaitMS] = useState(DEFAULT_CONNECTION_LIMITS.remoteBatchWaitMS)
  const [availableModels, setAvailableModels] = useState<RemoteModel[]>([])
  // 设置里的结果与错误一律走右下角通知：不再有挂在某个分区顶上、换页也不消失的提示框。
  const { show: notify } = useSnackbar()
  const [settingsBusy, setSettingsBusy] = useState(false)
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

  /* 连接自己的批处理参数；共用设置由后端在连接时填进运行配置，草稿里不带。 */
  function connectionTuning() {
    return { maxActiveBatch, remoteBatchWaitMs: remoteBatchWaitMS }
  }

  function localConfig() {
    return new Config({
      ...draftBaseConfig,
      provider: Provider.ProviderLocal,
      model: modelPath.trim(), tokenizerPath: tokenizerPath.trim() || undefined,
      endpoint: undefined, apiKey: undefined, password: undefined, headers: undefined, stateId: undefined, adapterId: undefined,
      ...connectionTuning(),
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
      apiKey: usesAPIKey(remoteProtocol) ? apiKey.trim() || undefined : undefined,
      password: usesAPIKey(remoteProtocol) ? undefined : apiKey.trim() || undefined,
      headers: headerMap, tokenizerPath: undefined,
      chatPromptMode: 'native-chat', chatThinking: 'disabled',
      // 流式由后端统一决定（App 一律流式显示回答），旧档案里的 stream:false 不再带出去。
      stream: undefined,
      rwkvStopTokens: remoteProtocol === 'openai' ? undefined : stops,
      ...connectionTuning(),
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
        if (reconnect) {
          await notifyOperation('apply-provider', '正在应用连接更改…', '连接更改已生效', async () => {
            onStatus(await Backend.ConfigureProvider(id, label, config))
          })
        }
        snapshotRef.current = signature
        snapshotConfigRef.current = configSignature(config)
        failedSignatureRef.current = ''
        setDraftSnapshot(signature)
        const value = await refreshProviders()
        const outdated = Boolean(value?.runtimeOutdated && value.runtimeProviderId === id)
        if (!reconnect) notify(outdated ? '连接更改已保存，重新加载模型后生效' : '连接档案已保存', outdated ? 'warning' : 'success', { key: 'apply-provider' })
        setSaveState({
          kind: 'saved',
          message: reconnect ? '已自动生效' : outdated ? '已自动保存；重新加载模型后生效' : '已自动保存',
        })
        return true
      } catch (reason) {
        failedSignatureRef.current = signature
        setSaveState({ kind: 'error', message: `保存失败：${errorText(reason)}` })
        notify(`连接更改未完成：${errorText(reason)}`, 'error', { key: 'apply-provider' })
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
    const remote = config.provider !== Provider.ProviderLocal
    setSettingsTab(remote ? 'remote' : 'local'); setModelPath(config.provider === Provider.ProviderLocal ? config.model : '')
    setTokenizerPath(config.tokenizerPath || ''); setRemoteEndpoint(remote ? config.endpoint || '' : ''); setRemoteModel(remote ? config.model : '')
    const protocol = (Object.keys(REMOTE_BACKENDS) as RemoteProtocol[]).find((key) => REMOTE_BACKENDS[key].provider === config.provider) || 'cuda'
    setRemoteProtocol(protocol); setAPIKey(usesAPIKey(protocol) ? config.apiKey || '' : config.password || '')
    setHeaders(Object.entries(config.headers || {}).map(([name, value]) => ({ id: nextHeaderID++, name, value: value || '' })))
    setMaxActiveBatch(config.maxActiveBatch || DEFAULT_CONNECTION_LIMITS.maxActiveBatch)
    setRemoteBatchWaitMS(config.remoteBatchWaitMs ?? DEFAULT_CONNECTION_LIMITS.remoteBatchWaitMS)
    // 水合即基线（由 draftInitialized 效果记录）：打开设置永远不会触发保存或重连。
    setSaveState({ kind: 'idle' })
  }

  function applyProviderBootstrapState(value: AppBootstrap) {
    setProviders(value.providers || [])
    setActiveProviderId(value.activeProviderId || '')
    setRuntimeProviderId(value.runtimeProviderId || '')
    setRuntimeConfig(value.runtimeProviderId ? Config.createFrom(value.config) : null)
    setRuntimeOutdated(Boolean(value.runtimeOutdated))
    setBrowserUploads(Boolean(value.browserUploads))
  }

  function beginEditingProvider(provider: SavedProvider) {
    const config = Config.createFrom(provider.config)
    setDraftInitialized(false)
    setEditingProviderId(provider.id)
    // 自动名（与后端派生规则一致）在表单里留空：改模型或地址后名称随之更新，而不是冻结成旧模型名。
    setDraftLabel(isAutoProviderLabel(provider.label, config) ? '' : provider.label)
    setDraftBaseConfig(config)
    setAvailableModels([])
    applyConfig(config)
  }
  function beginNewProvider(kind: ProviderKind = 'remote') {
    // 新连接从默认格式出发；之后在对话页的格式芯片里改，记在这个连接上。
    const config = new Config({
      provider: kind === 'local' ? Provider.ProviderLocal : Provider.ProviderRWKVLightningCUDA,
      model: '', endpoint: '', headers: {},
      chatPromptMode: 'native-chat', chatThinking: 'disabled', rwkvStopTokens: 'eos',
      agentProtocol: AgentProtocol.AgentProtocolXML, profile: NEW_CONFIG_DEFAULTS.profile, thinking: 'off',
      maxActiveBatch: DEFAULT_CONNECTION_LIMITS.maxActiveBatch, remoteBatchWaitMs: DEFAULT_CONNECTION_LIMITS.remoteBatchWaitMS,
    })
    setDraftInitialized(false)
    setEditingProviderId('')
    setDraftLabel('')
    setDraftBaseConfig(config)
    setAvailableModels([])
    applyConfig(config)
  }

  /*
   * 打开设置：不指定分区时，本地模型在运行就进「本地推理」，否则进「远端连接」。
   * 编辑器总是对准该分区那一类档案：优先运行中的，其次上次用的，再次第一个，都没有就新建。
   */
  /*
   * 打开设置：不指定分区时，本地模型在运行就进「本地推理」，否则进「远端连接」。
   * 连接分区默认停在列表；detail 为真时直接进当前档案的详情（对话页「管理 State」这类入口）。
   * 这一类一个档案都没有时直接进新建草稿。
   */
  function openSettings(section?: SettingsSection, options: OpenSettingsOptions = {}) {
    const runtime = providers.find((provider) => provider.id === runtimeProviderId)
    const next = section ?? (runtime && kindOf(runtime.config) === 'local' ? '本地推理' : '远端连接')
    setSettingsSection(next)
    // 每次打开都从已保存的档案重新水合，不沿用上次关闭时的表单。
    const editing = focusKind(next === '本地推理' ? 'local' : 'remote', true)
    setSettingsDetail(editing === 'new' || Boolean(options.detail || options.focus))
    setSettingsFocus(options.focus ?? null)
    setSettingsOpen(true)
  }
  /*
   * 让编辑器对准某一类档案；已经在编辑这一类就不动（force 时总是重新水合）。调用方负责先处理未保存的草稿。
   * 返回编辑器现在对准的是已有档案还是新建草稿。
   */
  function focusKind(kind: ProviderKind, force = false): 'existing' | 'new' {
    const editing = providers.find((provider) => provider.id === editingProviderId)
    if (!force && (editing ? kindOf(editing.config) === kind : settingsTab === kind)) return editingProviderId === '' ? 'new' : 'existing'
    const ofKind = providers.filter((provider) => kindOf(provider.config) === kind)
    const preferred = ofKind.find((provider) => provider.id === runtimeProviderId)
      || ofKind.find((provider) => provider.id === activeProviderId)
      || ofKind[0]
    if (preferred) beginEditingProvider(preferred)
    else beginNewProvider(kind)
    return preferred ? 'existing' : 'new'
  }
  function discardDraft() {
    const current = providers.find((provider) => provider.id === editingProviderId)
    if (current) beginEditingProvider(current)
    else beginNewProvider(settingsTab)
    notify('已放弃未保存更改。')
  }
  function selectProvider(id: string) {
    const provider = providers.find((item) => item.id === id)
    if (provider && provider.id !== editingProviderId) beginEditingProvider(provider)
  }
  function startNewDraft(kind: ProviderKind = settingsTab) {
    beginNewProvider(kind)
  }

  async function refreshProviders() {
    try {
      const value = await Backend.Bootstrap()
      applyProviderBootstrapState(value)
      return value
    } catch (error) {
      // 刷新失败不能静默：否则列表停在旧状态、看起来像"没保存上"。
      notify(`刷新连接列表失败：${errorText(error)}`, 'error')
      return undefined
    }
  }

  async function notifyOperation<T>(key: string, pending: string, success: string, operation: () => Promise<T>): Promise<T> {
    notify(pending, 'loading', { key })
    try {
      const result = await operation()
      notify(success, 'success', { key })
      return result
    } catch (error) {
      notify(`${pending.replace(/^正在/, '').replace(/…$/, '')}失败：${errorText(error)}`, 'error', { key })
      throw error
    }
  }

  /** 切换运行中连接的 State（仅 Lightning CUDA）；空串表示使用默认状态。记在这个连接上。 */
  async function setRuntimeState(stateId: string) {
    await notifyOperation('runtime-state', stateId ? '正在使用 State…' : '正在停用 State…',
      stateId ? `已使用 State：${stateId}` : '已恢复默认状态', async () => {
        onStatus(await Backend.SetRuntimeState(stateId))
        await refreshProviders()
      })
  }

  /** 切换运行中连接的 MiSS 适配器（仅 Lightning CUDA）；空串表示用基模本身的权重。记在这个连接上。 */
  async function setRuntimeAdapter(adapterId: string) {
    await notifyOperation('runtime-adapter', adapterId ? '正在使用 MiSS 适配器…' : '正在停用 MiSS 适配器…',
      adapterId ? `已使用 MiSS 适配器：${adapterId}` : '已恢复基模', async () => {
        onStatus(await Backend.SetRuntimeAdapter(adapterId))
        await refreshProviders()
      })
  }

  /** 切换运行中连接的对话格式：不重连、本地模型也不重新加载，下一轮生效；记在这个连接上。 */
  async function setRuntimeFormat(presetId: string) {
    const preset = formatPresetById(presetId)
    if (!preset) return
    await notifyOperation('runtime-format', '正在切换对话格式…', `已切换为${preset.short}格式，下一轮对话生效`, async () => {
      onStatus(await Backend.SetRuntimeFormat(formatSelection(preset, runtimeConfig?.wire || '')))
      await refreshProviders()
    })
  }

  /*
   * 设置里的 State / 适配器选择器读写的是运行中的那份：只有正在编辑的档案就是运行中的
   * 连接时才能选，选了立即生效并记在这个连接上。
   */
  const stateId = draftIsRunning ? runtimeConfig?.stateId || '' : ''
  const adapterId = draftIsRunning ? runtimeConfig?.adapterId || '' : ''
  function setStateId(id: string) {
    if (!draftIsRunning) return
    void setRuntimeState(id).catch(() => { /* notifyOperation 已报告失败。 */ })
  }
  function setAdapterId(id: string) {
    if (!draftIsRunning) return
    void setRuntimeAdapter(id).catch(() => { /* notifyOperation 已报告失败。 */ })
  }

  /* 释放当前运行的模型：本地模型卸载权重、归还内存；档案保留，可以再加载。 */
  async function unloadModel() {
    setSettingsBusy(true)
    try {
      const local = runtimeConfig?.provider === Provider.ProviderLocal
      await notifyOperation('unload-provider', local ? '正在释放模型…' : '正在断开连接…',
        local ? '模型已释放；连接档案已保留' : '已断开连接；连接档案已保留', async () => {
          onStatus(await Backend.UnloadModel())
          await refreshProviders()
        })
    } catch (error) {
      if (!settingsOpen) throw error
    } finally {
      setSettingsBusy(false)
    }
  }

  async function activateProvider(id: string) {
    const provider = providers.find((item) => item.id === id)
    const local = provider?.config.provider === Provider.ProviderLocal
    await notifyOperation('activate-provider', local ? '正在加载本地模型…' : '正在切换连接…',
      `已${local ? '加载' : '切换到'}：${provider?.label || provider?.config.model || '所选连接'}`, async () => {
        const configured = await Backend.ActivateProvider(id)
        onStatus(configured)
        await refreshProviders()
      })
  }

  async function deleteProvider(id: string) {
    const name = providers.find((item) => item.id === id)?.label || '所选连接'
    const value = await notifyOperation('delete-provider', '正在删除连接档案…', `已删除连接档案：${name}`, () => Backend.DeleteProvider(id))
    applyProviderBootstrapState(value)
    if (settingsOpen && id === editingProviderId) {
      const next = value.providers.find((provider) => provider.id === value.runtimeProviderId)
        || value.providers.find((provider) => provider.id === value.activeProviderId)
        || value.providers[0]
      if (next) beginEditingProvider(next)
      else beginNewProvider(settingsTab)
      // 删掉的是正在看的那个：回到列表，不跳进另一个档案的详情。
      setSettingsDetail(false)
    }
  }

  async function testRemote() {
    setSettingsBusy(true); notify('正在请求 /v1/models…', 'loading', { key: 'test-remote' })
    try {
      const models = await Backend.ListRemoteModels(remoteConfig())
      setAvailableModels(models)
      // 填的模型不在服务端列表里（没填，或部署换了模型）就换成服务端的第一个；名称没改过时随之自动更新。
      const current = remoteModel.trim()
      const replaced = models[0] && !models.some((model) => model.id === current) ? models[0].id : ''
      if (replaced) setRemoteModel(replaced)
      notify(replaced && current
        ? `连接成功，发现 ${models.length} 个模型；模型 ID 已从 ${current} 更新为 ${replaced}。`
        : `连接成功，发现 ${models.length} 个模型。`, 'success', { key: 'test-remote' })
    } catch (error) {
      notify(errorText(error), 'error', { key: 'test-remote' })
    } finally {
      setSettingsBusy(false)
    }
  }

  /* 显式保存：新建连接建档用（已有档案自动保存，界面上不再提供这个按钮）。 */
  async function saveProviderDraft(): Promise<boolean> {
    if (inFlightRef.current) await inFlightRef.current
    setSettingsBusy(true)
    notify('正在保存连接档案…', 'loading', { key: 'save-provider' })
    try {
      const saved = await Backend.SaveProvider(editingProviderId, draftLabel.trim(), draftConfigValue)
      await refreshProviders()
      beginEditingProvider(saved)
      notify(settingsTab === 'local'
        ? '档案已保存；点「加载模型」后才会占用内存。'
        : ready ? '档案已保存；当前运行连接保持不变，在对话页的模型标签里切换。' : '档案已保存，尚未连接。', 'success', { key: 'save-provider' })
      return true
    } catch (error) {
      notify(errorText(error), 'error', { key: 'save-provider' })
      return false
    } finally {
      setSettingsBusy(false)
    }
  }

  /* 保存并切换为运行连接；也是本地模型的「加载/重新加载模型」。 */
  async function saveAndUseProviderDraft() {
    if (inFlightRef.current) await inFlightRef.current
    setSettingsBusy(true)
    notify(settingsTab === 'local' ? '正在加载本地模型，这可能需要一些时间…' : '正在切换远端连接…', 'loading', { key: 'use-provider' })
    try {
      const configured = await Backend.ConfigureProvider(editingProviderId, draftLabel.trim(), draftConfigValue)
      onStatus(configured)
      const value = await refreshProviders()
      const running = value?.providers.find((provider) => provider.id === value.runtimeProviderId)
      if (running) beginEditingProvider(running)
      else setDraftSnapshot(providerDraftSignature(draftLabel, draftConfigValue))
      notify(settingsTab === 'local' ? '模型已加载，成为当前运行连接。' : '已切换为当前运行连接。', 'success', { key: 'use-provider' })
    } catch (error) {
      notify(errorText(error), 'error', { key: 'use-provider' })
    } finally {
      setSettingsBusy(false)
    }
  }

  return {
    // 展示状态
    settingsOpen, setSettingsOpen, settingsSection, setSettingsSection, settingsDetail, setSettingsDetail, settingsFocus,
    providers, activeProviderId, runtimeProviderId, editingProviderId,
    draftLabel, setDraftLabel, draftDirty, draftIsRunning,
    settingsTab, setSettingsTab,
    modelPath, setModelPath, tokenizerPath, setTokenizerPath,
    remoteEndpoint, setRemoteEndpoint, remoteModel, setRemoteModel,
    remoteProtocol, setRemoteProtocol, apiKey, setAPIKey, headers, setHeaders,
    stateId, setStateId,
    adapterId, setAdapterId,
    browserUploads,
    maxActiveBatch, setMaxActiveBatch, remoteBatchWaitMS, setRemoteBatchWaitMS,
    availableModels, setAvailableModels,
    settingsBusy,
    saveState, runtimeConfig, runtimeOutdated,
    // 派生
    draftConfigValue, draftErrors, draftError, draftNeedsReload, draftBlockReason,
    // 动作
    openSettings, focusKind, discardDraft, selectProvider, startNewDraft, unloadModel,
    applyProviderBootstrapState, applyConfig, refreshProviders,
    activateProvider, setRuntimeState, setRuntimeAdapter, setRuntimeFormat, deleteProvider, testRemote,
    saveProviderDraft, saveAndUseProviderDraft, flushDraft,
  }
}

function errorText(error: unknown): string {
  return error instanceof Error ? error.message : String(error)
}

export type ProviderManager = ReturnType<typeof useProviderManager>
