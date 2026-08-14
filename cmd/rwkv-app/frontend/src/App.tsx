import { FormEvent, KeyboardEvent, useEffect, useMemo, useRef, useState } from 'react'
import {
  ArrowUp,
  ChevronDown,
  CirclePlus,
  Cloud,
  Cpu,
  Folder,
  Globe2,
  LoaderCircle,
  MonitorCog,
  Sparkles,
  SquarePen,
  Trash2,
  Users,
  X,
} from 'lucide-react'
import { isDark } from './theme'
import { Events } from '@wailsio/runtime'
import * as Backend from '../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import {
  AgentProtocol,
  Config,
  ModelState,
  Provider,
  Status,
  type RemoteModel,
} from '../bindings/github.com/no22/RWKV-Agent/api/models'
import type {
  AppBootstrap,
  ConversationSummary,
  ConversationView,
  WorkspaceItem,
} from '../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/models'
import MarkdownMessage from './MarkdownMessage'
import ToolTrajectory, { type ToolTrace } from './ToolTrajectory'
import NavDrawer from './components/NavDrawer'
import ChatSessionRail from './components/ChatSessionRail'
import Md3Dialog from './components/shared/Md3Dialog'
import Md3TextField from './components/shared/Md3TextField'

type Message = {
  id: string
  role: 'user' | 'assistant' | 'error'
  content: string
  meta?: string
  trajectory?: ToolTrace[]
}

type HeaderRow = { id: number; name: string; value: string }

type AgentActivity = {
  kind: string
  step?: number
  parentStep?: number
  tool?: string
  arguments?: string
  route?: string
  bundles?: string[]
  subagentIndex?: number
  subagentTask?: string
  durationMs?: number
  attempt?: number
  maxAttempts?: number
  statusCode?: number
  delayMs?: number
  error?: string
}

const emptyStatus = new Status({
  state: ModelState.ModelIdle,
  workspace: '',
  hasApiKey: false,
  updatedAt: new Date(0).toISOString(),
  message: '正在连接后端…',
})

let nextMessageID = 1
let nextHeaderID = 1

function App() {
  const [status, setStatus] = useState<Status>(emptyStatus)
  const [messages, setMessages] = useState<Message[]>([])
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [workspaces, setWorkspaces] = useState<WorkspaceItem[]>([])
  const [activeConversationID, setActiveConversationID] = useState('')
  const [activity, setActivity] = useState<AgentActivity[]>([])
  const [prompt, setPrompt] = useState('')
  const [busy, setBusy] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [settingsTab, setSettingsTab] = useState<'local' | 'remote'>('local')
  const [modelPath, setModelPath] = useState('')
  const [tokenizerPath, setTokenizerPath] = useState('')
  const [remoteEndpoint, setRemoteEndpoint] = useState('')
  const [remoteModel, setRemoteModel] = useState('')
  const [remoteProtocol, setRemoteProtocol] = useState<'rwkv' | 'openai'>('rwkv')
  const [apiKey, setAPIKey] = useState('')
  const [headers, setHeaders] = useState<HeaderRow[]>([])
  const [agentProtocol, setAgentProtocol] = useState<AgentProtocol>(AgentProtocol.AgentProtocolMarkdown)
  const [progressiveTools, setProgressiveTools] = useState(true)
  const [enableWeb, setEnableWeb] = useState(false)
  const [braveAPIKey, setBraveAPIKey] = useState('')
  const [tavilyAPIKey, setTavilyAPIKey] = useState('')
  const [enableSubagents, setEnableSubagents] = useState(false)
  const [maxActiveBatch, setMaxActiveBatch] = useState(4)
  const [remoteBatchWaitMS, setRemoteBatchWaitMS] = useState(10)
  const [subagentMaxParallel, setSubagentMaxParallel] = useState(4)
  const [subagentMaxSteps, setSubagentMaxSteps] = useState(4)
  const [subagentTimeoutSeconds, setSubagentTimeoutSeconds] = useState(120)
  const [availableModels, setAvailableModels] = useState<RemoteModel[]>([])
  const [settingsMessage, setSettingsMessage] = useState('')
  const [settingsBusy, setSettingsBusy] = useState(false)
  const [dark, setDark] = useState(isDark)
  const messagesEnd = useRef<HTMLDivElement>(null)

  useEffect(() => {
    Backend.Bootstrap().then(applyBootstrap).catch((error: unknown) => {
      setStatus(new Status({ ...emptyStatus, state: ModelState.ModelError, message: errorText(error) }))
    })
    const offStatus = Events.On('model:status', (event) => {
      setStatus(Status.createFrom(event.data))
    })
    const offAgent = Events.On('agent:event', (event) => {
      const item = event.data as AgentActivity
      setActivity((current) => [...current, item])
    })
    return () => {
      offStatus()
      offAgent()
    }
  }, [])

  useEffect(() => {
    messagesEnd.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, activity])

  const ready = status.state === ModelState.ModelReady
  const workspaceName = useMemo(() => {
    const parts = status.workspace.split(/[\\/]/).filter(Boolean)
    return parts.at(-1) || 'Workspace'
  }, [status.workspace])

  function applyBootstrap(value: AppBootstrap) {
    setStatus(Status.createFrom(value.status))
    setConversations(value.conversations || [])
    setWorkspaces(value.workspaces || [])
    applyConversation(value.conversation || undefined)
    if (value.hasConfig) applyConfig(value.config)
    if (value.warning) setSettingsMessage(value.warning)
  }

  function applyConversation(value?: ConversationView) {
    setActiveConversationID(value?.id || '')
    setMessages((value?.messages || []).map((message) => ({
      id: message.id,
      role: message.role as Message['role'],
      content: message.content,
      meta: message.meta,
      trajectory: message.trajectory as ToolTrace[] | undefined,
    })))
    setActivity([])
    setPrompt('')
  }

  function applyConfig(config: Config) {
    const remote = config.provider === Provider.ProviderRWKVLightning || config.provider === Provider.ProviderChatCompletions
    setSettingsTab(remote ? 'remote' : 'local')
    setModelPath(config.provider === Provider.ProviderLocal ? config.model : '')
    setTokenizerPath(config.tokenizerPath || '')
    setRemoteEndpoint(remote ? config.endpoint || '' : '')
    setRemoteModel(remote ? config.model : '')
    setRemoteProtocol(config.provider === Provider.ProviderChatCompletions ? 'openai' : 'rwkv')
    setAPIKey(config.provider === Provider.ProviderChatCompletions ? config.apiKey || '' : config.password || '')
    setHeaders(Object.entries(config.headers || {}).map(([name, value]) => ({ id: nextHeaderID++, name, value: value || '' })))
    setAgentProtocol(config.agentProtocol || AgentProtocol.AgentProtocolMarkdown)
    setProgressiveTools(config.progressiveTools ?? true)
    setEnableWeb(config.enableWeb || false)
    setBraveAPIKey(config.braveApiKey || '')
    setTavilyAPIKey(config.tavilyApiKey || '')
    setEnableSubagents(config.enableSubagents || false)
    setMaxActiveBatch(config.maxActiveBatch || 4)
    setRemoteBatchWaitMS(config.remoteBatchWaitMs ?? 10)
    setSubagentMaxParallel(config.subagentMaxParallel || 4)
    setSubagentMaxSteps(config.subagentMaxSteps || 4)
    setSubagentTimeoutSeconds(config.subagentTimeoutSeconds || 120)
  }

  async function submitMessage() {
    const value = prompt.trim()
    if (!value || busy) return
    if (!ready) {
      setSettingsOpen(true)
      setSettingsMessage('请先加载本地模型或配置远端 API。')
      return
    }
    setPrompt('')
    setActivity([])
    setMessages((current) => [...current, { id: `pending-${nextMessageID++}`, role: 'user', content: value }])
    setBusy(true)
    try {
      const result = await Backend.Chat(value)
      setMessages((current) => [
        ...current,
        {
          id: `pending-${nextMessageID++}`,
          role: 'assistant',
          content: result.output,
          meta: `${result.steps.length} 步 · ${(result.durationMs / 1000).toFixed(1)} 秒`,
          trajectory: result.steps.filter((step) => step.tool).map((step) => ({
            step: step.number,
            tool: step.tool || '',
            arguments: step.toolArguments,
            status: step.toolError ? 'failed' : 'completed',
            error: step.toolError,
            retries: step.toolRetries,
            subagents: step.subagents?.map((child) => ({
              index: child.index,
              task: child.task,
              status: child.status as 'completed' | 'failed',
              error: child.error,
              route: child.route,
              bundles: child.bundles,
              durationMs: child.durationMs,
              output: child.output,
              sources: child.sources,
              steps: child.steps?.map((childStep) => ({
                step: childStep.number,
                tool: childStep.tool,
                arguments: childStep.arguments,
                status: childStep.status as 'completed' | 'failed',
                error: childStep.error,
                retries: childStep.retries,
              })),
            })),
          })),
        },
      ])
      const persisted = await Backend.Bootstrap()
      setConversations(persisted.conversations || [])
      setActiveConversationID(persisted.conversation?.id || '')
    } catch (error) {
      setMessages((current) => [
        ...current,
        { id: `error-${nextMessageID++}`, role: 'error', content: errorText(error) },
      ])
    } finally {
      setBusy(false)
    }
  }

  function onComposerKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      void submitMessage()
    }
  }

  async function newConversation() {
    if (busy) return
    await Backend.NewConversation()
    setMessages([])
    setActivity([])
    setPrompt('')
    setActiveConversationID('')
  }

  async function openConversation(id: string) {
    if (busy || id === activeConversationID) return
    setBusy(true)
    try {
      applyConversation(await Backend.OpenConversation(id))
    } catch (error) {
      setSettingsMessage(errorText(error))
    } finally {
      setBusy(false)
    }
  }

  async function deleteConversation(id: string) {
    if (busy) return
    setBusy(true)
    try {
      await Backend.DeleteConversation(id)
      if (id === activeConversationID) applyConversation()
      const persisted = await Backend.Bootstrap()
      setConversations(persisted.conversations || [])
    } catch (error) {
      setSettingsMessage(errorText(error))
    } finally {
      setBusy(false)
    }
  }

  async function chooseWorkspace() {
    if (busy) return
    setBusy(true)
    try {
      applyBootstrap(await Backend.ChooseWorkspace())
    } catch (error) {
      const message = errorText(error)
      if (!message.toLowerCase().includes('cancel')) setSettingsMessage(message)
    } finally {
      setBusy(false)
    }
  }

  async function openWorkspace(path: string) {
    if (busy) return
    setBusy(true)
    try {
      applyBootstrap(await Backend.OpenWorkspace(path))
    } catch (error) {
      setSettingsMessage(errorText(error))
    } finally {
      setBusy(false)
    }
  }

  async function configureLocal(event: FormEvent) {
    event.preventDefault()
    setSettingsBusy(true)
    setSettingsMessage('正在加载本地模型，这可能需要一些时间…')
    try {
      const configured = await Backend.Configure(new Config({
        provider: Provider.ProviderLocal,
        model: modelPath.trim(),
        tokenizerPath: tokenizerPath.trim() || undefined,
        thinking: 'off',
        maxSteps: 6,
        maxTokens: 1024,
        ...agentCapabilityConfig(),
      }))
      setStatus(configured)
      setSettingsMessage('本地模型已就绪。')
      setSettingsOpen(false)
    } catch (error) {
      setSettingsMessage(errorText(error))
    } finally {
      setSettingsBusy(false)
    }
  }

  function remoteConfig() {
    const headerMap = Object.fromEntries(
      headers
        .map((row) => [row.name.trim(), row.value.trim()] as const)
        .filter(([name]) => name.length > 0),
    )
    return new Config({
      provider: remoteProtocol === 'rwkv' ? Provider.ProviderRWKVLightning : Provider.ProviderChatCompletions,
      model: remoteModel.trim() || availableModels[0]?.id || '',
      endpoint: remoteEndpoint.trim(),
      apiKey: remoteProtocol === 'openai' ? apiKey.trim() || undefined : undefined,
      password: remoteProtocol === 'rwkv' ? apiKey.trim() || undefined : undefined,
      headers: headerMap,
      chatPromptMode: 'native-chat',
      chatThinking: 'disabled',
      stream: remoteProtocol === 'rwkv' ? false : undefined,
      rwkvStopTokens: remoteProtocol === 'rwkv' ? 'none' : undefined,
      maxSteps: 6,
      maxTokens: 1024,
      ...agentCapabilityConfig(),
    })
  }

  function agentCapabilityConfig() {
    return {
      agentProtocol,
      progressiveTools,
      enableWeb,
      braveApiKey: enableWeb ? braveAPIKey.trim() || undefined : undefined,
      tavilyApiKey: enableWeb ? tavilyAPIKey.trim() || undefined : undefined,
      enableSubagents,
      maxActiveBatch,
      remoteBatchWaitMs: remoteBatchWaitMS,
      subagentMaxParallel,
      subagentMaxSteps,
      subagentTimeoutSeconds,
    }
  }

  async function testRemote() {
    setSettingsBusy(true)
    setSettingsMessage('正在请求 /v1/models…')
    try {
      const models = await Backend.ListRemoteModels(remoteConfig())
      setAvailableModels(models)
      if (!remoteModel && models[0]) setRemoteModel(models[0].id)
      setSettingsMessage(`连接成功，发现 ${models.length} 个模型。`)
    } catch (error) {
      setSettingsMessage(errorText(error))
    } finally {
      setSettingsBusy(false)
    }
  }

  async function configureRemote(event: FormEvent) {
    event.preventDefault()
    setSettingsBusy(true)
    setSettingsMessage('正在配置远端模型…')
    try {
      const configured = await Backend.Configure(remoteConfig())
      setStatus(configured)
      setSettingsMessage('远端模型已就绪。')
      setSettingsOpen(false)
    } catch (error) {
      setSettingsMessage(errorText(error))
    } finally {
      setSettingsBusy(false)
    }
  }

  function addHeader() {
    setHeaders((current) => [...current, { id: nextHeaderID++, name: '', value: '' }])
  }

  return (
    <div className="app-shell">
      <NavDrawer
        dark={dark}
        onToggleDark={setDark}
        onNewChat={() => void newConversation()}
        onChooseWorkspace={() => void chooseWorkspace()}
        onOpenSettings={() => setSettingsOpen(true)}
        busy={busy}
      />
      <ChatSessionRail
        conversations={conversations}
        workspaces={workspaces}
        activeId={activeConversationID}
        busy={busy}
        onOpen={(id) => void openConversation(id)}
        onDelete={(id) => void deleteConversation(id)}
        onNewChat={() => void newConversation()}
        onOpenWorkspace={(path) => void openWorkspace(path)}
      />

      <main className="content-area">
      <div className={`chat-panel${messages.length === 0 ? ' chat-panel--empty' : ''}`}>
        {messages.length === 0 ? (
          <div className="chat-center">
            <div className="chat-welcome">
              <div className="chat-welcome-greeting">你好</div>
              <div className="chat-welcome-title">{ready ? '需要我为你做些什么？' : '先加载一个模型，我们就可以开始'}</div>
            </div>
            <Composer
              prompt={prompt}
              setPrompt={setPrompt}
              busy={busy}
              ready={ready}
              workspace={workspaceName}
              model={status.model || '选择模型'}
              onSubmit={submitMessage}
              onKeyDown={onComposerKeyDown}
              openSettings={() => setSettingsOpen(true)}
              chooseWorkspace={chooseWorkspace}
            />
            {!ready && (
              <button className="setup-hint" onClick={() => setSettingsOpen(true)}>
                <MonitorCog size={16} />
                加载本地模型或连接远端 API
              </button>
            )}
          </div>
        ) : (
          <>
            <header className="chat-topbar">
              <button className="md3-icon-btn" title="新会话" onClick={() => void newConversation()} disabled={busy}><SquarePen size={20} /></button>
              <div className="chat-topbar-title">RWKV Agent</div>
              <button className={`model-status ${status.state}`} onClick={() => setSettingsOpen(true)} title={statusLabel(status)}>
                <span className="status-dot" />
                <span>{statusLabel(status)}</span>
                <ChevronDown size={14} />
              </button>
            </header>
            <div className="chat-messages">
              {messages.map((message) => {
                const side = message.role === 'user' ? 'user' : message.role === 'error' ? 'error' : 'assistant'
                return (
                  <div className={`chat-msg chat-msg--${side}`} key={message.id}>
                    {message.role !== 'user' && (
                      <div className="chat-msg-avatar">{message.role === 'error' ? <X size={16} /> : <Sparkles size={16} />}</div>
                    )}
                    <div className={`chat-msg-content chat-msg-content--${side}`}>
                      {message.trajectory && message.trajectory.length > 0 && (
                        <ToolTrajectory calls={message.trajectory} done />
                      )}
                      {message.role === 'assistant' ? <MarkdownMessage content={message.content} /> : message.content}
                      {message.meta && <div className="message-meta">{message.meta}</div>}
                    </div>
                  </div>
                )
              })}
              {busy && (
                <div className="chat-msg chat-msg--assistant">
                  <div className="chat-msg-avatar"><Sparkles size={16} /></div>
                  <div className="chat-msg-content chat-msg-content--assistant">
                    <ToolTrajectory calls={activityToolTrace(activity)} done={false} status={activityLabel(activity.at(-1))} />
                  </div>
                </div>
              )}
              <div ref={messagesEnd} />
            </div>
            <Composer
              prompt={prompt}
              setPrompt={setPrompt}
              busy={busy}
              ready={ready}
              workspace={workspaceName}
              model={status.model || '选择模型'}
              onSubmit={submitMessage}
              onKeyDown={onComposerKeyDown}
              openSettings={() => setSettingsOpen(true)}
              chooseWorkspace={chooseWorkspace}
            />
          </>
        )}
      </div>
      </main>

      <Md3Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} title="模型设置" wide>
        <p className="settings-subtitle">选择本地 RWKV 模型，或连接远端推理服务。</p>
        <div className="settings-tabs">
          <button className={settingsTab === 'local' ? 'active' : ''} onClick={() => setSettingsTab('local')}><Cpu size={16} />本地模型</button>
          <button className={settingsTab === 'remote' ? 'active' : ''} onClick={() => setSettingsTab('remote')}><Cloud size={16} />远端 API</button>
        </div>
        {settingsTab === 'local' ? (
          <form className="settings-form" onSubmit={configureLocal}>
            <Md3TextField label="模型路径" value={modelPath} onChange={setModelPath} placeholder="/absolute/path/to/rwkv7-model.pth" />
            <Md3TextField label="Tokenizer 路径（可选，默认自动查找）" value={tokenizerPath} onChange={setTokenizerPath} placeholder="/path/to/rwkv_vocab_v20230424.txt" />
            <CapabilitySettings
              agentProtocol={agentProtocol} setAgentProtocol={setAgentProtocol}
              progressiveTools={progressiveTools} setProgressiveTools={setProgressiveTools}
              enableWeb={enableWeb} setEnableWeb={setEnableWeb} braveAPIKey={braveAPIKey} setBraveAPIKey={setBraveAPIKey} tavilyAPIKey={tavilyAPIKey} setTavilyAPIKey={setTavilyAPIKey}
              enableSubagents={enableSubagents} setEnableSubagents={setEnableSubagents}
              maxActiveBatch={maxActiveBatch} setMaxActiveBatch={setMaxActiveBatch}
              remoteBatchWaitMS={remoteBatchWaitMS} setRemoteBatchWaitMS={setRemoteBatchWaitMS}
              subagentMaxParallel={subagentMaxParallel} setSubagentMaxParallel={setSubagentMaxParallel}
              subagentMaxSteps={subagentMaxSteps} setSubagentMaxSteps={setSubagentMaxSteps}
              subagentTimeoutSeconds={subagentTimeoutSeconds} setSubagentTimeoutSeconds={setSubagentTimeoutSeconds}
            />
            <div className="info-panel"><Cpu size={17} /><span>支持 Apple Silicon macOS 上的 RWKV-7 .pth 和 MLX safetensors 目录。</span></div>
            <SettingsFooter busy={settingsBusy} message={settingsMessage} action="加载模型" />
          </form>
        ) : (
          <form className="settings-form" onSubmit={configureRemote}>
            <div className="protocol-switch" aria-label="远端协议">
              <button type="button" className={remoteProtocol === 'rwkv' ? 'active' : ''} onClick={() => setRemoteProtocol('rwkv')}>RWKV 续写</button>
              <button type="button" className={remoteProtocol === 'openai' ? 'active' : ''} onClick={() => setRemoteProtocol('openai')}>OpenAI 兼容</button>
            </div>
            <Md3TextField label="API 地址" value={remoteEndpoint} onChange={setRemoteEndpoint} placeholder="https://example.com 或 …/v1/models" />
            <div className="inline-fields">
              <Md3TextField label="模型 ID" value={remoteModel} onChange={setRemoteModel} placeholder="选择或输入模型" />
              <Md3TextField label={remoteProtocol === 'rwkv' ? '服务密码（可选）' : 'API Key（可选）'} type="password" value={apiKey} onChange={setAPIKey} placeholder="保存到本机配置" />
            </div>
            {availableModels.length > 0 && (
              <div className="model-pills">{availableModels.slice(0, 8).map((model) => <button type="button" className={remoteModel === model.id ? 'active' : ''} key={model.id} onClick={() => setRemoteModel(model.id)}>{model.id}</button>)}</div>
            )}
            <div className="headers-heading"><div><strong>自定义 HTTP 头</strong><small>支持 Cloudflare Access 等网关</small></div><button type="button" onClick={addHeader}><CirclePlus size={15} />添加</button></div>
            {headers.map((row) => (
              <div className="header-row" key={row.id}>
                <input aria-label="Header 名称" value={row.name} onChange={(event) => setHeaders((current) => current.map((item) => item.id === row.id ? { ...item, name: event.target.value } : item))} placeholder="CF-Access-Client-Id" />
                <input aria-label="Header 值" type="password" value={row.value} onChange={(event) => setHeaders((current) => current.map((item) => item.id === row.id ? { ...item, value: event.target.value } : item))} placeholder="Header value" autoComplete="off" />
                <button type="button" onClick={() => setHeaders((current) => current.filter((item) => item.id !== row.id))} aria-label="删除 Header"><Trash2 size={16} /></button>
              </div>
            ))}
            <CapabilitySettings
              agentProtocol={agentProtocol} setAgentProtocol={setAgentProtocol}
              progressiveTools={progressiveTools} setProgressiveTools={setProgressiveTools}
              enableWeb={enableWeb} setEnableWeb={setEnableWeb} braveAPIKey={braveAPIKey} setBraveAPIKey={setBraveAPIKey} tavilyAPIKey={tavilyAPIKey} setTavilyAPIKey={setTavilyAPIKey}
              enableSubagents={enableSubagents} setEnableSubagents={setEnableSubagents}
              maxActiveBatch={maxActiveBatch} setMaxActiveBatch={setMaxActiveBatch}
              remoteBatchWaitMS={remoteBatchWaitMS} setRemoteBatchWaitMS={setRemoteBatchWaitMS}
              subagentMaxParallel={subagentMaxParallel} setSubagentMaxParallel={setSubagentMaxParallel}
              subagentMaxSteps={subagentMaxSteps} setSubagentMaxSteps={setSubagentMaxSteps}
              subagentTimeoutSeconds={subagentTimeoutSeconds} setSubagentTimeoutSeconds={setSubagentTimeoutSeconds}
            />
            <footer className="settings-footer">
              <div className="settings-result">{settingsBusy && <LoaderCircle className="spin" size={15} />}{settingsMessage}</div>
              <div className="footer-actions"><button type="button" className="secondary" onClick={() => void testRemote()} disabled={settingsBusy}>测试并获取模型</button><button type="submit" className="primary" disabled={settingsBusy}>{settingsBusy ? <LoaderCircle className="spin" size={16} /> : <Cloud size={16} />}连接 API</button></div>
            </footer>
          </form>
        )}
      </Md3Dialog>
    </div>
  )
}

type CapabilitySettingsProps = {
  agentProtocol: AgentProtocol
  setAgentProtocol: (value: AgentProtocol) => void
  progressiveTools: boolean
  setProgressiveTools: (value: boolean) => void
  enableWeb: boolean
  setEnableWeb: (value: boolean) => void
  braveAPIKey: string
  setBraveAPIKey: (value: string) => void
  tavilyAPIKey: string
  setTavilyAPIKey: (value: string) => void
  enableSubagents: boolean
  setEnableSubagents: (value: boolean) => void
  maxActiveBatch: number
  setMaxActiveBatch: (value: number) => void
  remoteBatchWaitMS: number
  setRemoteBatchWaitMS: (value: number) => void
  subagentMaxParallel: number
  setSubagentMaxParallel: (value: number) => void
  subagentMaxSteps: number
  setSubagentMaxSteps: (value: number) => void
  subagentTimeoutSeconds: number
  setSubagentTimeoutSeconds: (value: number) => void
}

function CapabilitySettings(props: CapabilitySettingsProps) {
  return (
    <section className="capability-settings" aria-label="Agent 能力">
      <div className="capability-heading"><div><strong>Agent 能力</strong><small>按需暴露工具并控制并发预算</small></div></div>
      <label>工具协议
        <select aria-label="工具协议" value={props.agentProtocol} onChange={(event) => props.setAgentProtocol(event.target.value as AgentProtocol)}>
          <option value={AgentProtocol.AgentProtocolMarkdown}>Markdown（推荐）</option>
          <option value={AgentProtocol.AgentProtocolXML}>XML（兼容模式）</option>
        </select>
      </label>
      <label className="toggle-row">
        <span><Sparkles size={16} /><span>渐进式工具暴露<small>先选择能力组，再加载具体工具 schema</small></span></span>
        <input aria-label="渐进式工具暴露" type="checkbox" checked={props.progressiveTools} onChange={(event) => props.setProgressiveTools(event.target.checked)} />
      </label>
      <label className="toggle-row">
        <span><Globe2 size={16} /><span>网页搜索与正文获取<small>Brave Search + Tavily Extract</small></span></span>
        <input aria-label="网页搜索与正文获取" type="checkbox" checked={props.enableWeb} onChange={(event) => props.setEnableWeb(event.target.checked)} />
      </label>
      {props.enableWeb && (
        <div className="inline-fields capability-fields">
          <label>Brave API Key<input type="password" value={props.braveAPIKey} onChange={(event) => props.setBraveAPIKey(event.target.value)} placeholder="保存到本机配置" autoComplete="off" required /></label>
          <label>Tavily API Key<input type="password" value={props.tavilyAPIKey} onChange={(event) => props.setTavilyAPIKey(event.target.value)} placeholder="保存到本机配置" autoComplete="off" required /></label>
        </div>
      )}
      <label className="toggle-row">
        <span><Users size={16} /><span>并发子 Agent<small>一次派发 2–8 个独立任务，不允许嵌套委派</small></span></span>
        <input aria-label="并发子 Agent" type="checkbox" checked={props.enableSubagents} onChange={(event) => props.setEnableSubagents(event.target.checked)} />
      </label>
      {props.enableSubagents && (
        <div className="budget-grid">
          <label>活动批量<input aria-label="活动批量" type="number" min="1" max="8" value={props.maxActiveBatch} onChange={(event) => props.setMaxActiveBatch(Number(event.target.value))} /></label>
          <label>子 Agent 并发<input aria-label="子 Agent 并发" type="number" min="2" max="8" value={props.subagentMaxParallel} onChange={(event) => props.setSubagentMaxParallel(Number(event.target.value))} /></label>
          <label>单 Agent 步数<input aria-label="单 Agent 步数" type="number" min="2" max="32" value={props.subagentMaxSteps} onChange={(event) => props.setSubagentMaxSteps(Number(event.target.value))} /></label>
          <label>批次超时（秒）<input aria-label="批次超时（秒）" type="number" min="1" max="3600" value={props.subagentTimeoutSeconds} onChange={(event) => props.setSubagentTimeoutSeconds(Number(event.target.value))} /></label>
          <label>远端聚合窗口（毫秒）<input aria-label="远端聚合窗口（毫秒）" type="number" min="0" max="1000" value={props.remoteBatchWaitMS} onChange={(event) => props.setRemoteBatchWaitMS(Number(event.target.value))} /></label>
        </div>
      )}
    </section>
  )
}

type ComposerProps = {
  prompt: string
  setPrompt: (value: string) => void
  busy: boolean
  ready: boolean
  workspace: string
  model: string
  onSubmit: () => Promise<void>
  onKeyDown: (event: KeyboardEvent<HTMLTextAreaElement>) => void
  openSettings: () => void
  chooseWorkspace: () => Promise<void>
}

function Composer({ prompt, setPrompt, busy, ready, workspace, model, onSubmit, onKeyDown, openSettings, chooseWorkspace }: ComposerProps) {
  function autoGrow(el: HTMLTextAreaElement) {
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 200) + 'px'
  }
  return (
    <div className="chat-composer">
      <div className="chat-composer-inner">
        <textarea
          className="chat-composer-input"
          value={prompt}
          onChange={(event) => { setPrompt(event.target.value); autoGrow(event.target) }}
          onKeyDown={onKeyDown}
          placeholder="描述你想要完成的任务"
          rows={1}
          disabled={busy}
          aria-label="消息"
        />
        <div className="chat-composer-toolbar">
          <div className="composer-left">
            <button type="button" className="composer-chip" onClick={() => void chooseWorkspace()} title={workspace}>
              <Folder size={15} /><span>{workspace}</span>
            </button>
            <button type="button" className="composer-chip" onClick={openSettings} title={model}>
              <span className={`mini-dot ${ready ? 'ready' : ''}`} /><span>{model}</span>
            </button>
          </div>
          <button
            type="button"
            className={`chat-composer-send${prompt.trim() && !busy ? ' chat-composer-send--active' : ''}`}
            onClick={() => void onSubmit()}
            disabled={!prompt.trim() || busy}
            aria-label="发送"
          >
            {busy ? <LoaderCircle className="spin" size={20} /> : <ArrowUp size={20} />}
          </button>
        </div>
      </div>
    </div>
  )
}

function SettingsFooter({ busy, message, action }: { busy: boolean; message: string; action: string }) {
  return (
    <footer className="settings-footer">
      <div className="settings-result">{busy && <LoaderCircle className="spin" size={15} />}{message}</div>
      <button type="submit" className="primary" disabled={busy}>{busy ? <LoaderCircle className="spin" size={16} /> : <Cpu size={16} />}{action}</button>
    </footer>
  )
}

function statusLabel(status: Status) {
  if (status.state === ModelState.ModelReady) return status.model || '模型已就绪'
  if (status.state === ModelState.ModelLoading) return '模型加载中'
  if (status.state === ModelState.ModelError) return '模型错误'
  return '未选择模型'
}

function activityLabel(item?: AgentActivity) {
  if (!item) return '正在思考…'
  const child = item.subagentIndex ? `Agent ${item.subagentIndex} · ` : ''
  if (item.kind === 'subagent_start') return `Agent ${item.subagentIndex} · 已开始子任务`
  if (item.kind === 'subagent_done') return `Agent ${item.subagentIndex} · ${item.error ? '子任务失败' : '子任务完成'}`
  if (item.kind === 'model_start') return `${child}步骤 ${item.step || 1} · 正在决定下一步`
  if (item.kind === 'route_start') return `${child}正在选择能力组`
  if (item.kind === 'route_done') return item.bundles?.length ? `${child}已加载 ${item.bundles.join('、')} 能力组` : `${child}无需加载工具`
  if (item.kind === 'tool_start') return `${child}步骤 ${item.step} · 正在使用 ${item.tool}`
  if (item.kind === 'tool_retry') return `${child}步骤 ${item.step} · ${item.tool} 自动退避后重试`
  if (item.kind === 'tool_done') return `${child}步骤 ${item.step} · ${item.tool} 已完成`
  if (item.kind === 'protocol_retry') return `${child}步骤 ${item.step} · 正在重试`
  return 'Agent 正在工作…'
}

function activityToolTrace(activity: AgentActivity[]): ToolTrace[] {
  const calls: ToolTrace[] = []
  const callIndexes = new Map<string, number>()
  for (const item of activity) {
    if (item.subagentIndex) {
      const parentStep = item.parentStep || 0
      let parentIndex = calls.findIndex((call) => call.step === parentStep && call.tool === 'spawn_agents')
      if (parentIndex < 0) {
        calls.push({ step: parentStep, tool: 'spawn_agents', status: 'running', subagents: [] })
        parentIndex = calls.length - 1
      }
      const parent = calls[parentIndex]
      const children = [...(parent.subagents || [])]
      let childIndex = children.findIndex((child) => child.index === item.subagentIndex)
      if (childIndex < 0) {
        children.push({ index: item.subagentIndex, task: item.subagentTask || '', status: 'running', steps: [] })
        childIndex = children.length - 1
      }
      const child = { ...children[childIndex], task: item.subagentTask || children[childIndex].task }
      if (item.kind === 'route_done') {
        child.route = item.route
        child.bundles = item.bundles
      }
      if (item.kind === 'subagent_done') {
        child.status = item.error ? 'failed' : 'completed'
        child.error = item.error
        child.route = item.route || child.route
        child.bundles = item.bundles || child.bundles
        child.durationMs = item.durationMs
      }
      if (item.tool) {
        const steps = [...(child.steps || [])]
        const existingStep = steps.findIndex((step) => step.step === (item.step || 0) && step.tool === item.tool)
        const previousStep = existingStep >= 0 ? steps[existingStep] : undefined
        const retries = item.kind === 'tool_retry'
          ? [...(previousStep?.retries || []), activityRetry(item)]
          : previousStep?.retries
        const nextStep = {
          step: item.step || 0,
          tool: item.tool,
          arguments: item.arguments || previousStep?.arguments,
          status: item.kind === 'tool_done' ? item.error ? 'failed' as const : 'completed' as const : 'running' as const,
          error: item.error,
          retries,
        }
        if (existingStep < 0) steps.push(nextStep)
        else steps[existingStep] = nextStep
        child.steps = steps
      }
      children[childIndex] = child
      calls[parentIndex] = { ...parent, subagents: children }
      continue
    }
    if (!item.tool) continue
    const key = `${item.step || 0}:${item.tool}`
    const existing = callIndexes.get(key)
    const previousCall = existing === undefined ? undefined : calls[existing]
    const retries = item.kind === 'tool_retry'
      ? [...(previousCall?.retries || []), activityRetry(item)]
      : previousCall?.retries
    const call: ToolTrace = {
      step: item.step || 0,
      tool: item.tool,
      arguments: item.arguments,
      status: item.kind === 'tool_done' ? item.error ? 'failed' : 'completed' : 'running',
      error: item.error,
      retries,
    }
    if (existing === undefined) {
      callIndexes.set(key, calls.length)
      calls.push(call)
    } else {
      calls[existing] = { ...calls[existing], ...call, arguments: call.arguments || calls[existing].arguments }
    }
  }
  return calls
}

function activityRetry(item: AgentActivity) {
  return {
    attempt: item.attempt || 0,
    maxAttempts: item.maxAttempts || 0,
    statusCode: item.statusCode,
    delayMs: item.delayMs || 0,
  }
}

function errorText(error: unknown) {
  if (error instanceof Error) return error.message
  return String(error)
}

export default App
