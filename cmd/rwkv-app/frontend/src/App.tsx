import { FormEvent, KeyboardEvent, useEffect, useMemo, useRef, useState } from 'react'
import {
  ArrowUp,
  Bot,
  Check,
  ChevronDown,
  CirclePlus,
  Cloud,
  Cpu,
  FileText,
  Folder,
  LoaderCircle,
  Menu,
  MessageSquarePlus,
  MonitorCog,
  Plus,
  RotateCcw,
  Settings,
  SlidersHorizontal,
  Sparkles,
  Trash2,
  X,
} from 'lucide-react'
import { Events } from '@wailsio/runtime'
import * as Backend from '../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import {
  Config,
  ModelState,
  Provider,
  Status,
  type RemoteModel,
} from '../bindings/github.com/no22/RWKV-Agent/api/models'

type Message = {
  id: number
  role: 'user' | 'assistant' | 'error'
  content: string
  meta?: string
}

type HeaderRow = { id: number; name: string; value: string }

type AgentActivity = {
  kind: string
  step?: number
  tool?: string
  route?: string
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
  const [activity, setActivity] = useState<AgentActivity[]>([])
  const [prompt, setPrompt] = useState('')
  const [busy, setBusy] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [settingsTab, setSettingsTab] = useState<'local' | 'remote'>('local')
  const [modelPath, setModelPath] = useState('')
  const [tokenizerPath, setTokenizerPath] = useState('')
  const [remoteEndpoint, setRemoteEndpoint] = useState('')
  const [remoteModel, setRemoteModel] = useState('')
  const [remoteProtocol, setRemoteProtocol] = useState<'rwkv' | 'openai'>('rwkv')
  const [apiKey, setAPIKey] = useState('')
  const [headers, setHeaders] = useState<HeaderRow[]>([])
  const [availableModels, setAvailableModels] = useState<RemoteModel[]>([])
  const [settingsMessage, setSettingsMessage] = useState('')
  const [settingsBusy, setSettingsBusy] = useState(false)
  const messagesEnd = useRef<HTMLDivElement>(null)

  useEffect(() => {
    Backend.Status().then(setStatus).catch((error: unknown) => {
      setStatus(new Status({ ...emptyStatus, state: ModelState.ModelError, message: errorText(error) }))
    })
    const offStatus = Events.On('model:status', (event) => {
      setStatus(Status.createFrom(event.data))
    })
    const offAgent = Events.On('agent:event', (event) => {
      const item = event.data as AgentActivity
      setActivity((current) => [...current.slice(-7), item])
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
    const parts = status.workspace.split('/').filter(Boolean)
    return parts.at(-1) || 'Workspace'
  }, [status.workspace])

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
    setMessages((current) => [...current, { id: nextMessageID++, role: 'user', content: value }])
    setBusy(true)
    try {
      const result = await Backend.Chat(value)
      setMessages((current) => [
        ...current,
        {
          id: nextMessageID++,
          role: 'assistant',
          content: result.output,
          meta: `${result.steps.length} 步 · ${(result.durationMs / 1000).toFixed(1)} 秒`,
        },
      ])
    } catch (error) {
      setMessages((current) => [
        ...current,
        { id: nextMessageID++, role: 'error', content: errorText(error) },
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
      }))
      setStatus(configured)
      setSettingsMessage('本地模型已就绪。')
      setSettingsOpen(false)
      setMessages([])
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
    })
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
      setMessages([])
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
      <button className="mobile-menu" onClick={() => setSidebarOpen(true)} aria-label="打开侧栏">
        <Menu size={20} />
      </button>
      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="window-drag" />
        <div className="brand-row">
          <div className="brand-mark"><Sparkles size={17} strokeWidth={2.4} /></div>
          <span className="brand-name">rwkv</span>
          <span className="brand-badge">AGENT</span>
          <button className="icon-button sidebar-close" onClick={() => setSidebarOpen(false)} aria-label="关闭侧栏"><X size={18} /></button>
        </div>
        <button className="new-chat" onClick={() => void newConversation()} disabled={busy}>
          <MessageSquarePlus size={17} />
          新会话
        </button>
        <div className="section-heading">
          <span>工作区</span>
          <div className="section-actions"><SlidersHorizontal size={16} /><Plus size={17} /></div>
        </div>
        <div className="workspace-row">
          <Folder size={18} />
          <span>{workspaceName}</span>
        </div>
        <div className="session-row active"><span>新会话</span></div>
        {messages.length > 0 && (
          <div className="session-row"><span>{messages.find((message) => message.role === 'user')?.content}</span><time>刚刚</time></div>
        )}
        <div className="sidebar-spacer" />
        <button className="settings-button" onClick={() => setSettingsOpen(true)}>
          <Settings size={17} />
          设置
        </button>
      </aside>

      <main className={`main ${messages.length > 0 ? 'has-conversation' : ''}`}>
        <header className="topbar">
          <div />
          <button className={`model-status ${status.state}`} onClick={() => setSettingsOpen(true)}>
            <span className="status-dot" />
            <span>{statusLabel(status)}</span>
            <ChevronDown size={14} />
          </button>
        </header>

        {messages.length === 0 ? (
          <section className="hero">
            <div className="hero-title">
              <div className="hero-logo"><Sparkles size={25} /></div>
              <h1>探索智能之境</h1>
              <span>预览版</span>
            </div>
            <p className="hero-subtitle">本地优先的 RWKV 工作区助手</p>
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
            />
            {!ready && (
              <button className="setup-hint" onClick={() => setSettingsOpen(true)}>
                <MonitorCog size={16} />
                加载本地模型或连接远端 API
              </button>
            )}
          </section>
        ) : (
          <section className="conversation">
            <div className="conversation-inner">
              {messages.map((message) => (
                <article className={`message ${message.role}`} key={message.id}>
                  <div className="message-avatar">
                    {message.role === 'user' ? '你' : message.role === 'error' ? <X size={16} /> : <Bot size={17} />}
                  </div>
                  <div className="message-body">
                    <div className="message-label">{message.role === 'user' ? '你' : message.role === 'error' ? '错误' : 'RWKV Agent'}</div>
                    <div className="message-content">{message.content}</div>
                    {message.meta && <div className="message-meta">{message.meta}</div>}
                  </div>
                </article>
              ))}
              {busy && (
                <article className="message assistant working">
                  <div className="message-avatar"><Bot size={17} /></div>
                  <div className="message-body">
                    <div className="message-label">RWKV Agent</div>
                    <div className="activity-card">
                      <LoaderCircle className="spin" size={17} />
                      <span>{activityLabel(activity.at(-1))}</span>
                    </div>
                    {activity.filter((item) => item.tool).slice(-4).map((item, index) => (
                      <div className="tool-row" key={`${item.kind}-${item.step}-${index}`}>
                        {item.error ? <X size={14} /> : item.kind === 'tool_done' ? <Check size={14} /> : <FileText size={14} />}
                        <span>步骤 {item.step} · {item.tool}{item.kind === 'tool_done' ? ' 完成' : ''}</span>
                      </div>
                    ))}
                  </div>
                </article>
              )}
              <div ref={messagesEnd} />
            </div>
            <div className="composer-dock">
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
              />
            </div>
          </section>
        )}
      </main>

      {settingsOpen && (
        <div className="modal-backdrop" onMouseDown={(event) => event.target === event.currentTarget && setSettingsOpen(false)}>
          <section className="settings-modal" role="dialog" aria-modal="true" aria-label="模型设置">
            <header className="settings-header">
				<div><h2>模型设置</h2><p>选择本地 RWKV 模型，或连接远端推理服务。</p></div>
              <button className="icon-button" onClick={() => setSettingsOpen(false)} aria-label="关闭设置"><X size={19} /></button>
            </header>
            <div className="settings-tabs">
              <button className={settingsTab === 'local' ? 'active' : ''} onClick={() => setSettingsTab('local')}><Cpu size={16} />本地模型</button>
              <button className={settingsTab === 'remote' ? 'active' : ''} onClick={() => setSettingsTab('remote')}><Cloud size={16} />远端 API</button>
            </div>
            {settingsTab === 'local' ? (
              <form className="settings-form" onSubmit={configureLocal}>
                <label>模型路径<input value={modelPath} onChange={(event) => setModelPath(event.target.value)} placeholder="/absolute/path/to/rwkv7-model.pth" required /></label>
                <label>Tokenizer 路径 <small>可选，默认自动查找</small><input value={tokenizerPath} onChange={(event) => setTokenizerPath(event.target.value)} placeholder="/path/to/rwkv_vocab_v20230424.txt" /></label>
                <div className="info-panel"><Cpu size={17} /><span>支持 Apple Silicon macOS 上的 RWKV-7 .pth 和 MLX safetensors 目录。</span></div>
                <SettingsFooter busy={settingsBusy} message={settingsMessage} action="加载模型" />
              </form>
            ) : (
              <form className="settings-form" onSubmit={configureRemote}>
				<div className="protocol-switch" aria-label="远端协议">
					<button type="button" className={remoteProtocol === 'rwkv' ? 'active' : ''} onClick={() => setRemoteProtocol('rwkv')}>RWKV 续写</button>
					<button type="button" className={remoteProtocol === 'openai' ? 'active' : ''} onClick={() => setRemoteProtocol('openai')}>OpenAI 兼容</button>
				</div>
                <label>API 地址<input value={remoteEndpoint} onChange={(event) => setRemoteEndpoint(event.target.value)} placeholder="https://example.com 或 …/v1/models" required /></label>
                <div className="inline-fields">
                  <label>模型 ID<input value={remoteModel} onChange={(event) => setRemoteModel(event.target.value)} placeholder="选择或输入模型" required /></label>
					<label>{remoteProtocol === 'rwkv' ? '服务密码' : 'API Key'} <small>可选</small><input type="password" value={apiKey} onChange={(event) => setAPIKey(event.target.value)} placeholder="仅保存在内存" autoComplete="off" /></label>
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
                <footer className="settings-footer">
                  <div className="settings-result">{settingsBusy && <LoaderCircle className="spin" size={15} />}{settingsMessage}</div>
                  <div className="footer-actions"><button type="button" className="secondary" onClick={() => void testRemote()} disabled={settingsBusy}>测试并获取模型</button><button type="submit" className="primary" disabled={settingsBusy}>{settingsBusy ? <LoaderCircle className="spin" size={16} /> : <Cloud size={16} />}连接 API</button></div>
                </footer>
              </form>
            )}
          </section>
        </div>
      )}
    </div>
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
}

function Composer({ prompt, setPrompt, busy, ready, workspace, model, onSubmit, onKeyDown, openSettings }: ComposerProps) {
  return (
    <div className="composer-card">
      <textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} onKeyDown={onKeyDown} placeholder="描述你想要完成的任务" rows={3} disabled={busy} aria-label="消息" />
      <div className="composer-toolbar">
        <div className="composer-options">
          <button type="button" className="round-button" aria-label="添加附件"><Plus size={19} /></button>
          <button type="button" className="option-chip"><Folder size={15} />{workspace}<ChevronDown size={13} /></button>
          <button type="button" className="option-chip"><Sparkles size={15} />标准模式<ChevronDown size={13} /></button>
        </div>
        <div className="composer-actions">
          <button type="button" className="model-chip" onClick={openSettings}><span className={`mini-dot ${ready ? 'ready' : ''}`} />{model}<ChevronDown size={13} /></button>
          <button type="button" className="send-button" onClick={() => void onSubmit()} disabled={!prompt.trim() || busy} aria-label="发送">{busy ? <LoaderCircle className="spin" size={19} /> : <ArrowUp size={20} />}</button>
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
  if (item.kind === 'model_start') return `步骤 ${item.step || 1} · 正在决定下一步`
  if (item.kind === 'tool_start') return `步骤 ${item.step} · 正在使用 ${item.tool}`
  if (item.kind === 'tool_done') return `步骤 ${item.step} · ${item.tool} 已完成`
  if (item.kind === 'protocol_retry') return `步骤 ${item.step} · 正在重试`
  return 'Agent 正在工作…'
}

function errorText(error: unknown) {
  if (error instanceof Error) return error.message
  return String(error)
}

export default App
