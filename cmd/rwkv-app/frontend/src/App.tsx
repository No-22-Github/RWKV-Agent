import { FormEvent, KeyboardEvent, useEffect, useMemo, useRef, useState } from 'react'
import {
  ArrowUp, Bot, ChevronDown, CircleAlert, CirclePlus, Cloud, Cpu, Download,
  FileText, Folder, FolderOpen, GitBranch, Globe2, LoaderCircle, Menu, MessageSquareText,
  MoreHorizontal, PanelRight, RefreshCw, Search, Settings, Sparkles, SquarePen, Trash2,
  Users, Wrench, X,
} from 'lucide-react'
import { Events } from '@wailsio/runtime'
import * as Backend from '../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import {
  AgentProtocol, Config, ModelState, Provider, Status, type RemoteModel, type Result, type Step,
} from '../bindings/github.com/no22/RWKV-Agent/api/models'
import type {
  AppBootstrap, ConversationSummary, ConversationView, WorkspaceItem,
} from '../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/models'
import MarkdownMessage from './MarkdownMessage'
import type { ToolTrace } from './ToolTrajectory'
import Md3Dialog from './components/shared/Md3Dialog'
import Md3TextField from './components/shared/Md3TextField'

type Message = {
  id: string
  role: 'user' | 'assistant' | 'error'
  content: string
  prompt?: string
  meta?: string
  trajectory?: ToolTrace[]
  trace?: Result
  createdAt?: string
}
type HeaderRow = { id: number; name: string; value: string }
type AgentActivity = {
  kind: string; step?: number; parentStep?: number; tool?: string; arguments?: string; route?: string
  bundles?: string[]; subagentIndex?: number; subagentTask?: string; durationMs?: number
  attempt?: number; maxAttempts?: number; statusCode?: number; delayMs?: number; error?: string
}
type ChatTurn = { user?: Message; response?: Message }
type GutterStatus = { label: string; state: 'idle' | 'running' | 'completed' | 'failed' }
type LedgerEvent = {
  id: string
  order: number
  kind: 'input' | 'route' | 'model' | 'tool' | 'retry' | 'subagent' | 'output'
  title: string
  summary: string
  state: GutterStatus['state']
  request?: unknown
  result?: unknown
  timing?: unknown
  raw?: unknown
}

const emptyStatus = new Status({ state: ModelState.ModelIdle, workspace: '', hasApiKey: false, updatedAt: new Date(0).toISOString(), message: '正在连接后端…' })
const STARTER_PROMPTS = ['概括这个仓库的近期进度', '找出最近改动可能引入的风险', '解释这个项目的整体架构']
let nextMessageID = 1
let nextHeaderID = 1

export default function App() {
  const [status, setStatus] = useState<Status>(emptyStatus)
  const [messages, setMessages] = useState<Message[]>([])
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [workspaces, setWorkspaces] = useState<WorkspaceItem[]>([])
  const [activeConversationID, setActiveConversationID] = useState('')
  const [activity, setActivity] = useState<AgentActivity[]>([])
  const [prompt, setPrompt] = useState('')
  const [busy, setBusy] = useState(false)
  const [activeTab, setActiveTab] = useState<'chat' | 'trace'>('chat')
  const [selectedTraceID, setSelectedTraceID] = useState('')
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
  const messagesEnd = useRef<HTMLDivElement>(null)

  useEffect(() => {
    Backend.Bootstrap().then(applyBootstrap).catch((error: unknown) => setStatus(new Status({ ...emptyStatus, state: ModelState.ModelError, message: errorText(error) })))
    const offStatus = Events.On('model:status', (event) => setStatus(Status.createFrom(event.data)))
    const offAgent = Events.On('agent:event', (event) => setActivity((current) => [...current, event.data as AgentActivity]))
    return () => { offStatus(); offAgent() }
  }, [])
  useEffect(() => { messagesEnd.current?.scrollIntoView({ block: 'end' }) }, [messages, activity])

  const ready = status.state === ModelState.ModelReady
  const workspaceName = useMemo(() => status.workspace.split(/[\\/]/).filter(Boolean).at(-1) || 'Workspace', [status.workspace])

  function applyBootstrap(value: AppBootstrap) {
    setStatus(Status.createFrom(value.status)); setConversations(value.conversations || []); setWorkspaces(value.workspaces || [])
    applyConversation(value.conversation || undefined); if (value.hasConfig) applyConfig(value.config); if (value.warning) setSettingsMessage(value.warning)
  }
  function applyConversation(value?: ConversationView) {
    setActiveConversationID(value?.id || ''); setActiveTab('chat'); setActivity([]); setPrompt('')
    let lastPrompt = ''
    setMessages((value?.messages || []).map((message) => {
      if (message.role === 'user') lastPrompt = message.content
      return {
        id: message.id, role: message.role as Message['role'], content: message.content,
        prompt: message.role !== 'user' ? lastPrompt : undefined, meta: message.meta,
        trajectory: message.trajectory as ToolTrace[] | undefined,
        trace: message.trace as Result | undefined, createdAt: normalizeTimestamp(message.createdAt),
      }
    }))
  }
  function applyConfig(config: Config) {
    const remote = config.provider === Provider.ProviderRWKVLightning || config.provider === Provider.ProviderChatCompletions
    setSettingsTab(remote ? 'remote' : 'local'); setModelPath(config.provider === Provider.ProviderLocal ? config.model : '')
    setTokenizerPath(config.tokenizerPath || ''); setRemoteEndpoint(remote ? config.endpoint || '' : ''); setRemoteModel(remote ? config.model : '')
    setRemoteProtocol(config.provider === Provider.ProviderChatCompletions ? 'openai' : 'rwkv'); setAPIKey(config.provider === Provider.ProviderChatCompletions ? config.apiKey || '' : config.password || '')
    setHeaders(Object.entries(config.headers || {}).map(([name, value]) => ({ id: nextHeaderID++, name, value: value || '' })))
    setAgentProtocol(config.agentProtocol || AgentProtocol.AgentProtocolMarkdown); setProgressiveTools(config.progressiveTools ?? true)
    setEnableWeb(config.enableWeb || false); setBraveAPIKey(config.braveApiKey || ''); setTavilyAPIKey(config.tavilyApiKey || '')
    setEnableSubagents(config.enableSubagents || false); setMaxActiveBatch(config.maxActiveBatch || 4); setRemoteBatchWaitMS(config.remoteBatchWaitMs ?? 10)
    setSubagentMaxParallel(config.subagentMaxParallel || 4); setSubagentMaxSteps(config.subagentMaxSteps || 4); setSubagentTimeoutSeconds(config.subagentTimeoutSeconds || 120)
  }
  async function submitMessage() {
    const value = prompt.trim(); if (!value || busy) return
    if (!ready) { setSettingsOpen(true); setSettingsMessage('请先加载本地模型或配置远端 API。'); return }
    setPrompt(''); setActivity([]); setMessages((current) => [...current, { id: `pending-${nextMessageID++}`, role: 'user', content: value, createdAt: new Date().toISOString() }]); setBusy(true)
    try {
      const result = await Backend.Chat(value)
      const assistant: Message = { id: `pending-${nextMessageID++}`, role: 'assistant', content: result.output, prompt: value, trace: result, createdAt: new Date().toISOString(), meta: `${result.steps.length} 步 · ${(result.durationMs / 1000).toFixed(1)} 秒`, trajectory: legacyTrajectory(result.steps) }
      setMessages((current) => [...current, assistant]); setSelectedTraceID(assistant.id)
      const persisted = await Backend.Bootstrap(); setConversations(persisted.conversations || []); setActiveConversationID(persisted.conversation?.id || '')
    } catch (error) {
      try {
        const persisted = await Backend.Bootstrap()
        applyBootstrap(persisted)
        setSelectedTraceID('')
      } catch {
        setMessages((current) => [...current, { id: `error-${nextMessageID++}`, role: 'error', content: errorText(error) }])
      }
    }
    finally { setBusy(false) }
  }
  function onComposerKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); void submitMessage() } }
  async function newConversation() { if (busy) return; await Backend.NewConversation(); setMessages([]); setActivity([]); setPrompt(''); setActiveConversationID(''); setActiveTab('chat') }
  async function openConversation(id: string) { if (busy || id === activeConversationID) return; setBusy(true); try { applyConversation(await Backend.OpenConversation(id)) } catch (error) { setSettingsMessage(errorText(error)) } finally { setBusy(false) } }
  async function deleteConversation(id: string) { if (busy) return; setBusy(true); try { await Backend.DeleteConversation(id); if (id === activeConversationID) applyConversation(); const persisted = await Backend.Bootstrap(); setConversations(persisted.conversations || []) } catch (error) { setSettingsMessage(errorText(error)) } finally { setBusy(false) } }
  async function chooseWorkspace() { if (busy) return; setBusy(true); try { applyBootstrap(await Backend.ChooseWorkspace()) } catch (error) { if (!errorText(error).toLowerCase().includes('cancel')) setSettingsMessage(errorText(error)) } finally { setBusy(false) } }
  async function openWorkspace(path: string) { if (busy) return; setBusy(true); try { applyBootstrap(await Backend.OpenWorkspace(path)) } catch (error) { setSettingsMessage(errorText(error)) } finally { setBusy(false) } }

  async function configureLocal(event: FormEvent) {
    event.preventDefault(); setSettingsBusy(true); setSettingsMessage('正在加载本地模型，这可能需要一些时间…')
    try { const configured = await Backend.Configure(new Config({ provider: Provider.ProviderLocal, model: modelPath.trim(), tokenizerPath: tokenizerPath.trim() || undefined, thinking: 'off', maxSteps: 6, maxTokens: 1024, ...agentCapabilityConfig() })); setStatus(configured); setSettingsMessage('本地模型已就绪。'); setSettingsOpen(false) }
    catch (error) { setSettingsMessage(errorText(error)) } finally { setSettingsBusy(false) }
  }
  function remoteConfig() {
    const headerMap = Object.fromEntries(headers.map((row) => [row.name.trim(), row.value.trim()] as const).filter(([name]) => name.length > 0))
    return new Config({ provider: remoteProtocol === 'rwkv' ? Provider.ProviderRWKVLightning : Provider.ProviderChatCompletions, model: remoteModel.trim() || availableModels[0]?.id || '', endpoint: remoteEndpoint.trim(), apiKey: remoteProtocol === 'openai' ? apiKey.trim() || undefined : undefined, password: remoteProtocol === 'rwkv' ? apiKey.trim() || undefined : undefined, headers: headerMap, chatPromptMode: 'native-chat', chatThinking: 'disabled', stream: remoteProtocol === 'rwkv' ? false : undefined, rwkvStopTokens: remoteProtocol === 'rwkv' ? 'none' : undefined, maxSteps: 6, maxTokens: 1024, ...agentCapabilityConfig() })
  }
  function agentCapabilityConfig() { return { agentProtocol, progressiveTools, enableWeb, braveApiKey: enableWeb ? braveAPIKey.trim() || undefined : undefined, tavilyApiKey: enableWeb ? tavilyAPIKey.trim() || undefined : undefined, enableSubagents, maxActiveBatch, remoteBatchWaitMs: remoteBatchWaitMS, subagentMaxParallel, subagentMaxSteps, subagentTimeoutSeconds } }
  async function testRemote() { setSettingsBusy(true); setSettingsMessage('正在请求 /v1/models…'); try { const models = await Backend.ListRemoteModels(remoteConfig()); setAvailableModels(models); if (!remoteModel && models[0]) setRemoteModel(models[0].id); setSettingsMessage(`连接成功，发现 ${models.length} 个模型。`) } catch (error) { setSettingsMessage(errorText(error)) } finally { setSettingsBusy(false) } }
  async function configureRemote(event: FormEvent) { event.preventDefault(); setSettingsBusy(true); setSettingsMessage('正在配置远端模型…'); try { const configured = await Backend.Configure(remoteConfig()); setStatus(configured); setSettingsMessage('远端模型已就绪。'); setSettingsOpen(false) } catch (error) { setSettingsMessage(errorText(error)) } finally { setSettingsBusy(false) } }
  function addHeader() { setHeaders((current) => [...current, { id: nextHeaderID++, name: '', value: '' }]) }

  const traceMessages = messages.filter((message) => message.role !== 'user' && (message.trace || message.trajectory?.length))
  const selectedMessage = traceMessages.find((message) => message.id === selectedTraceID) || traceMessages.at(-1)
  return <div className="app-shell">
    <Sidebar conversations={conversations} workspaces={workspaces} activeId={activeConversationID} busy={busy} onNewChat={() => void newConversation()} onChooseWorkspace={() => void chooseWorkspace()} onOpenSettings={() => setSettingsOpen(true)} onOpen={openConversation} onDelete={deleteConversation} onOpenWorkspace={openWorkspace} />
    <main className="content-area">
      <header className="app-header">
        <div className="header-title"><button className="icon-button header-menu" aria-label="导航"><Menu size={18} /></button><span className="brand-mark" /> <strong>{messages.length ? (messages.find((message) => message.role === 'user')?.content || '新对话') : '新对话'}</strong></div>
        <div className="header-tabs" role="tablist"><button role="tab" aria-selected={activeTab === 'chat'} className={activeTab === 'chat' ? 'active' : ''} onClick={() => setActiveTab('chat')}>对话</button><button role="tab" aria-selected={activeTab === 'trace'} className={activeTab === 'trace' ? 'active' : ''} onClick={() => setActiveTab('trace')} disabled={!traceMessages.length}>轨迹 <span>{traceMessages.length || ''}</span></button></div>
        <button className="model-select" onClick={() => setSettingsOpen(true)} title={statusLabel(status)} aria-label={!ready ? '加载本地模型或连接远端 API' : undefined}><span className={`status-dot ${ready ? 'ready' : ''}`} /> <span>{status.model || '选择模型'}</span><ChevronDown size={14} /></button>
      </header>
      {activeTab === 'trace' ? <TraceView messages={traceMessages} selected={selectedMessage} onSelect={setSelectedTraceID} /> : <ChatView messages={messages} activity={activity} busy={busy} ready={ready} workspace={workspaceName} model={status.model || '选择模型'} prompt={prompt} setPrompt={setPrompt} onSubmit={submitMessage} onKeyDown={onComposerKeyDown} openSettings={() => setSettingsOpen(true)} chooseWorkspace={chooseWorkspace} onTrace={(id) => { setSelectedTraceID(id); setActiveTab('trace') }} messagesEnd={messagesEnd} />}
    </main>
    <Md3Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} title="模型设置" wide>
      <p className="settings-subtitle">本地模型、远端续写服务与 Agent 能力配置保存在当前 Mac 用户目录。</p>
      <div className="settings-tabs"><button className={settingsTab === 'local' ? 'active' : ''} onClick={() => setSettingsTab('local')}><Cpu size={16} />本地模型</button><button className={settingsTab === 'remote' ? 'active' : ''} onClick={() => setSettingsTab('remote')}><Cloud size={16} />远端 API</button></div>
      {settingsTab === 'local' ? <form className="settings-form" onSubmit={configureLocal}><Md3TextField label="模型路径" value={modelPath} onChange={setModelPath} placeholder="/absolute/path/to/rwkv7-model.pth" /><Md3TextField label="Tokenizer 路径（可选，默认自动查找）" value={tokenizerPath} onChange={setTokenizerPath} placeholder="/path/to/rwkv_vocab_v20230424.txt" /><CapabilitySettings {...{ agentProtocol, setAgentProtocol, progressiveTools, setProgressiveTools, enableWeb, setEnableWeb, braveAPIKey, setBraveAPIKey, tavilyAPIKey, setTavilyAPIKey, enableSubagents, setEnableSubagents, maxActiveBatch, setMaxActiveBatch, remoteBatchWaitMS, setRemoteBatchWaitMS, subagentMaxParallel, setSubagentMaxParallel, subagentMaxSteps, setSubagentMaxSteps, subagentTimeoutSeconds, setSubagentTimeoutSeconds }} /><div className="info-panel"><Cpu size={17} /><span>支持 Apple Silicon macOS 上的 RWKV-7 .pth 和 MLX safetensors 目录。</span></div><SettingsFooter busy={settingsBusy} message={settingsMessage} action="加载模型" /></form> : <form className="settings-form" onSubmit={configureRemote}><div className="protocol-switch" aria-label="远端协议"><button type="button" className={remoteProtocol === 'rwkv' ? 'active' : ''} onClick={() => setRemoteProtocol('rwkv')}>RWKV 续写</button><button type="button" className={remoteProtocol === 'openai' ? 'active' : ''} onClick={() => setRemoteProtocol('openai')}>OpenAI 兼容</button></div><Md3TextField label="API 地址" value={remoteEndpoint} onChange={setRemoteEndpoint} placeholder="https://example.com 或 …/v1/models" /><div className="inline-fields"><Md3TextField label="模型 ID" value={remoteModel} onChange={setRemoteModel} placeholder="选择或输入模型" /><Md3TextField label={remoteProtocol === 'rwkv' ? '服务密码（可选）' : 'API Key（可选）'} type="password" value={apiKey} onChange={setAPIKey} placeholder="保存到本机配置" /></div>{availableModels.length > 0 && <div className="model-pills">{availableModels.slice(0, 8).map((model) => <button type="button" className={remoteModel === model.id ? 'active' : ''} key={model.id} onClick={() => setRemoteModel(model.id)}>{model.id}</button>)}</div>}<div className="headers-heading"><div><strong>自定义 HTTP 头</strong><small>支持 Cloudflare Access 等网关</small></div><button type="button" onClick={addHeader}><CirclePlus size={15} />添加</button></div>{headers.map((row) => <div className="header-row" key={row.id}><input aria-label="Header 名称" value={row.name} onChange={(event) => setHeaders((current) => current.map((item) => item.id === row.id ? { ...item, name: event.target.value } : item))} placeholder="CF-Access-Client-Id" /><input aria-label="Header 值" type="password" value={row.value} onChange={(event) => setHeaders((current) => current.map((item) => item.id === row.id ? { ...item, value: event.target.value } : item))} placeholder="Header value" autoComplete="off" /><button type="button" onClick={() => setHeaders((current) => current.filter((item) => item.id !== row.id))} aria-label="删除 Header"><Trash2 size={16} /></button></div>)}<CapabilitySettings {...{ agentProtocol, setAgentProtocol, progressiveTools, setProgressiveTools, enableWeb, setEnableWeb, braveAPIKey, setBraveAPIKey, tavilyAPIKey, setTavilyAPIKey, enableSubagents, setEnableSubagents, maxActiveBatch, setMaxActiveBatch, remoteBatchWaitMS, setRemoteBatchWaitMS, subagentMaxParallel, setSubagentMaxParallel, subagentMaxSteps, setSubagentMaxSteps, subagentTimeoutSeconds, setSubagentTimeoutSeconds }} /><footer className="settings-footer"><div className="settings-result">{settingsBusy && <LoaderCircle className="spin" size={15} />}{settingsMessage}</div><div className="footer-actions"><button type="button" className="secondary" onClick={() => void testRemote()} disabled={settingsBusy}>测试并获取模型</button><button type="submit" className="primary" disabled={settingsBusy}>{settingsBusy ? <LoaderCircle className="spin" size={16} /> : <Cloud size={16} />}连接 API</button></div></footer></form>}
    </Md3Dialog>
  </div>
}

function Sidebar({ conversations, workspaces, activeId, busy, onNewChat, onChooseWorkspace, onOpenSettings, onOpen, onDelete, onOpenWorkspace }: { conversations: ConversationSummary[]; workspaces: WorkspaceItem[]; activeId: string; busy: boolean; onNewChat: () => void; onChooseWorkspace: () => void; onOpenSettings: () => void; onOpen: (id: string) => void; onDelete: (id: string) => void; onOpenWorkspace: (path: string) => void }) {
  const [menu, setMenu] = useState<string | null>(null)
  return <aside className="app-sidebar">
    <div className="sidebar-brand"><span className="brand-mark" /><span>RWKV Agent</span><span className="sidebar-version">LOCAL</span></div>
    <button className="new-chat-button" onClick={onNewChat} disabled={busy}><SquarePen size={16} />新的对话 <kbd>⌘N</kbd></button>
    <button className="workspace-button" onClick={onChooseWorkspace} disabled={busy}><FolderOpen size={16} /><span>打开工作区</span><MoreHorizontal size={15} /></button>
    {workspaces.length > 0 && <section className="sidebar-section"><div className="sidebar-section-label">工作区</div>{workspaces.map((workspace) => (
      <button key={workspace.path} className={`workspace-row ${workspace.active ? 'active' : ''}`} onClick={() => onOpenWorkspace(workspace.path)} disabled={!workspace.available || busy} title={workspace.path}><Folder size={14} /><span>{workspace.name}</span>{workspace.active && <i />}</button>
    ))}</section>}
    <section className="sidebar-section recent-section"><div className="sidebar-section-label">近期</div>
      {conversations.length === 0 ? <div className="sidebar-empty">暂无历史对话</div> : conversations.map((conversation) => (
        <div key={conversation.id} className={`conversation-row ${conversation.id === activeId ? 'active' : ''}`}>
          <button onClick={() => onOpen(conversation.id)} title={conversation.title || '未命名会话'}><span className="conversation-title">{conversation.title || '未命名会话'}</span><span className="conversation-time">{relativeTime(conversation.updatedAt)}</span></button>
          <button className="conversation-menu" aria-label="更多操作" onClick={() => setMenu(menu === conversation.id ? null : conversation.id)}><MoreHorizontal size={15} /></button>
          {menu === conversation.id && <button className="conversation-delete" onClick={() => { setMenu(null); onDelete(conversation.id) }}><Trash2 size={14} />删除会话</button>}
        </div>
      ))}
    </section>
    <button className="sidebar-footer-button" onClick={onOpenSettings} aria-label="设置"><Settings size={16} /><span>设置</span><kbd>⌘,</kbd></button>
  </aside>
}

function ChatView({ messages, activity, busy, ready, workspace, model, prompt, setPrompt, onSubmit, onKeyDown, openSettings, chooseWorkspace, onTrace, messagesEnd }: { messages: Message[]; activity: AgentActivity[]; busy: boolean; ready: boolean; workspace: string; model: string; prompt: string; setPrompt: (value: string) => void; onSubmit: () => Promise<void>; onKeyDown: (event: KeyboardEvent<HTMLTextAreaElement>) => void; openSettings: () => void; chooseWorkspace: () => Promise<void>; onTrace: (id: string) => void; messagesEnd: React.RefObject<HTMLDivElement | null> }) {
  const turns = groupMessagesIntoTurns(messages)
  const empty = turns.length === 0
  const composer = <Composer prompt={prompt} setPrompt={setPrompt} busy={busy} ready={ready} workspace={workspace} model={model} onSubmit={onSubmit} onKeyDown={onKeyDown} openSettings={openSettings} chooseWorkspace={chooseWorkspace} />
  if (empty) return <div className="chat-panel empty">
    <div className="empty-layout">
      <div className="empty-gutter">
        <span className="empty-meta">工作区<br /><b>{workspace}</b></span>
        <span className="empty-meta-rule" />
        <span className="empty-meta">模型<br /><b className={ready ? 'teal' : ''}>{ready ? model : '待配置'}</b></span>
      </div>
      <div className="empty-column">
        <div className="empty-greeting">
          <span className="empty-hello">你好</span>
          <h1>需要我为你做些什么？</h1>
        </div>
        {composer}
        <div className="starter-chips-row" aria-label="快速开始">{STARTER_PROMPTS.map((item) => <button key={item} type="button" className="starter-chip" onClick={() => setPrompt(item)}>{item}</button>)}</div>
      </div>
    </div>
  </div>
  return <div className="chat-panel has-conversation">
    <div className="chat-stage">
      <div className="conversation-scroll">
        {turns.map((turn, index) => <TurnView key={turn.user?.id || turn.response?.id || index} turn={turn} index={index + 1} pending={busy && index === turns.length - 1 && !turn.response} activity={activity} onTrace={onTrace} />)}
        <div ref={messagesEnd} />
      </div>
    </div>
    {composer}
  </div>
}

function TurnView({ turn, index, pending, activity, onTrace }: { turn: ChatTurn; index: number; pending: boolean; activity: AgentActivity[]; onTrace: (id: string) => void }) {
  const response = turn.response
  const hasTrace = Boolean(response?.trace || response?.trajectory?.length)
  const statuses = pending ? liveGutterStatuses(activity) : completedGutterStatuses(response)
  const stats = response?.trace ? traceStats(response.trace) : undefined
  const time = turn.user?.createdAt || response?.createdAt
  return <article className={`conversation-turn${pending ? ' pending' : ''}${response?.role === 'error' ? ' failed' : ''}`} data-testid={`conversation-turn-${index}`}>
    <aside className="turn-gutter">
      <span className="turn-number">{String(index).padStart(2, '0')}</span>
      <time>{formatTurnTime(time)}</time>
      <span className="gutter-rule" />
      <div className="gutter-statuses" aria-label={pending ? 'Agent 运行状态' : 'Agent 完成状态'}>
        {statuses.map((item, statusIndex) => <div className={`gutter-status ${item.state}`} key={`${item.label}-${statusIndex}`}><span>{item.label}</span><i /></div>)}
      </div>
      {(stats || (response?.trajectory?.length && !response.trace)) && <><span className="gutter-rule" /><span className="turn-stats">{stats ? <>{formatDuration(stats.durationMs)}{stats.tokens > 0 && <><br />{stats.tokens.toLocaleString('zh-CN')} tok</>}</> : <>历史摘要<br />工具 {response?.trajectory?.length}</>}</span></>}
    </aside>
    <div className="turn-main">
      {turn.user && <div className="turn-user"><div className="plain-message">{turn.user.content}</div></div>}
      {pending && <div className="turn-pending-answer" aria-live="polite"><span className="answer-cursor" /><span className="sr-only">{activityLabel(activity.at(-1))}</span></div>}
      {response?.role === 'assistant' && <div className="turn-answer"><MarkdownMessage content={response.content} /></div>}
      {response?.role === 'error' && <div className="turn-error"><X size={15} /><span>{response.content}</span></div>}
      {response?.meta && <div className="message-meta">{response.meta}</div>}
      {response && <div className="turn-actions">
        {response.role === 'assistant' && <button onClick={() => void navigator.clipboard?.writeText(response.content)}>复制</button>}
        {hasTrace && <button onClick={() => onTrace(response.id)}>查看轨迹</button>}
      </div>}
    </div>
  </article>
}

function Composer({ prompt, setPrompt, busy, ready, workspace, model, onSubmit, onKeyDown, openSettings, chooseWorkspace }: { prompt: string; setPrompt: (value: string) => void; busy: boolean; ready: boolean; workspace: string; model: string; onSubmit: () => Promise<void>; onKeyDown: (event: KeyboardEvent<HTMLTextAreaElement>) => void; openSettings: () => void; chooseWorkspace: () => Promise<void> }) {
  function autoGrow(element: HTMLTextAreaElement) { element.style.height = 'auto'; element.style.height = `${Math.min(element.scrollHeight, 180)}px` }
  return <div className="composer"><div className="composer-gutter"><span>{workspace}</span><span>{ready ? 'Agent 已就绪' : '等待模型'}</span></div><div className="composer-box">
      <textarea aria-label="消息" rows={1} value={prompt} disabled={busy} placeholder="描述你想要完成的任务" onChange={(event) => { setPrompt(event.target.value); autoGrow(event.target) }} onKeyDown={onKeyDown} />
      <div className="composer-footer">
        <div className="composer-context">
          <button className="composer-chip" onClick={() => void chooseWorkspace()} title={workspace}><Folder size={14} /><span>{workspace}</span></button>
          <button className="composer-chip" onClick={openSettings} title={model}><span className={`status-dot ${ready ? 'ready' : ''}`} /><span>{model}</span></button>
        </div>
        <button className="send-button" aria-label="发送" onClick={() => void onSubmit()} disabled={!prompt.trim() || busy}>{busy ? <LoaderCircle size={17} className="spin" /> : <ArrowUp size={17} />}</button>
      </div>
    </div></div>
}

function TraceView({ messages, selected, onSelect }: { messages: Message[]; selected?: Message; onSelect: (id: string) => void }) {
  const [query, setQuery] = useState(''); const [inspector, setInspector] = useState(true); const [detail, setDetail] = useState<'summary' | 'request' | 'result' | 'timing'>('summary'); const [selectedEventID, setSelectedEventID] = useState('')
  const visible = messages.filter((message) => !query || `${message.prompt} ${message.content} ${JSON.stringify(message.trace || message.trajectory)}`.toLowerCase().includes(query.toLowerCase()))
  const selectedEvent = selectedEventID ? selected && buildLedgerEvents(selected).find((event) => event.id === selectedEventID) : undefined
  const eventCount = messages.reduce((sum, message) => sum + buildLedgerEvents(message).length, 0)
  const timelineEvents = visible.flatMap((message) => buildLedgerEvents(message).map((event) => ({ event, messageId: message.id })))
  function exportTrace() { const data = visible.map((message) => JSON.stringify({ id: message.id, role: message.role, prompt: message.prompt, createdAt: message.createdAt, trace: message.trace || { legacyTrajectory: message.trajectory } })).join('\n'); const url = URL.createObjectURL(new Blob([data], { type: 'application/jsonl' })); const anchor = document.createElement('a'); anchor.href = url; anchor.download = 'rwkv-agent-trajectory.jsonl'; anchor.click(); window.setTimeout(() => URL.revokeObjectURL(url), 0) }
  function selectTurn(id: string) { setSelectedEventID(''); onSelect(id) }
  function selectEvent(messageID: string, eventID: string) { onSelect(messageID); setSelectedEventID(eventID) }
  return <div className="trace-layout">
    <div className="trace-toolbar"><div className="trace-stats"><strong>{messages.length}</strong><span>轮次</span><strong>{eventCount}</strong><span>事件</span></div><label className="trace-search"><Search size={15} /><input aria-label="搜索轨迹" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索请求、工具或错误" /></label><button className="icon-button" title="导出 JSONL" aria-label="导出 JSONL" onClick={exportTrace}><Download size={16} /></button><button className={`icon-button ${inspector ? 'selected' : ''}`} title="检查器" aria-label="检查器" onClick={() => setInspector(!inspector)}><PanelRight size={16} /></button></div>
    {timelineEvents.length > 0 && <TraceTimeline events={timelineEvents} selectedEventID={selectedEventID} onEvent={selectEvent} />}
    <div className="trace-workspace"><div className="trace-main"><div className="trace-ledger">{visible.map((message, index) => <TraceTurn key={message.id} message={message} index={index + 1} selected={message.id === selected?.id} selectedEventID={selectedEventID} onClick={() => selectTurn(message.id)} onEvent={(eventID) => selectEvent(message.id, eventID)} />)}{visible.length === 0 && <div className="trace-empty">没有匹配的轨迹</div>}</div></div>{inspector && <TraceInspector message={selected} event={selectedEvent} detail={detail} setDetail={setDetail} />}</div>
  </div>
}

function TraceTimeline({ events, selectedEventID, onEvent }: { events: { event: LedgerEvent; messageId: string }[]; selectedEventID: string; onEvent: (messageID: string, eventID: string) => void }) {
  const total = events.length || 1
  return <div className="trace-timeline">
    <div className="trace-timeline-labels"><span>Input</span><span>Model</span><span>Tools</span></div>
    <div className="trace-timeline-track">
      {events.map(({ event, messageId }, index) => <button key={event.id} type="button" className={`trace-span ${event.kind} ${event.state}${event.id === selectedEventID ? ' current' : ''}`} style={{ left: `${(index / total) * 100}%`, width: `calc(${(1 / total) * 100}% - 2px)`, top: `${eventLane(event.kind) * 14 + 7}px` }} onClick={() => onEvent(messageId, event.id)} title={`${event.title}${event.summary ? ' · ' + event.summary : ''}`} aria-label={event.title} />)}
    </div>
  </div>
}
function TraceTurn({ message, index, selected, selectedEventID, onClick, onEvent }: { message: Message; index: number; selected: boolean; selectedEventID: string; onClick: () => void; onEvent: (eventID: string) => void }) {
  const trace = message.trace
  const events = buildLedgerEvents(message)
  const duration = trace?.durationMs || 0
  return <article className={`trace-turn ${selected ? 'selected' : ''}${message.role === 'error' ? ' failed' : ''}`}>
    <div className="turn-index">{String(index).padStart(2, '0')}<small>{message.createdAt ? new Date(message.createdAt).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) : '本地'}</small></div>
    <div className="turn-content"><button className="trace-turn-heading" onClick={onClick}><span className="turn-summary"><span className="turn-role">TURN {index}</span><span>{events.length} 个事件</span><span>{duration ? formatDuration(duration) : '时长 --'}</span>{trace?.route && <span className="route-chip">{trace.route}</span>}{message.role === 'error' && <span className="route-chip error">失败</span>}</span><span className="turn-prompt">{message.prompt || message.content}</span></button>
      <div className="turn-events">{events.map((event) => <TraceEventRow key={event.id} event={event} selected={selected && selectedEventID === event.id} onClick={() => onEvent(event.id)} />)}</div>
    </div>
  </article>
}
const ROLE_TAGS: Record<LedgerEvent['kind'], { tag: string; cls: string }> = {
  input: { tag: 'USER', cls: 'user' }, route: { tag: 'ROUTE', cls: 'route' }, model: { tag: 'MODEL', cls: 'model' },
  tool: { tag: 'TOOL', cls: 'tool' }, retry: { tag: 'RETRY', cls: 'retry' }, subagent: { tag: 'AGENT', cls: 'agent' }, output: { tag: 'SUBMIT', cls: 'submit' },
}
const EVENT_TITLE_PREFIX = /^(用户输入|路由请求|路由响应|模型请求|模型响应|协议修复|工具调用|工具结果|工具重试|最终回复)\s*·?\s*/
function eventLane(kind: LedgerEvent['kind']) { if (kind === 'tool' || kind === 'retry' || kind === 'subagent') return 2; if (kind === 'model' || kind === 'output') return 1; return 0 }
function eventName(event: LedgerEvent) { return event.title.replace(EVENT_TITLE_PREFIX, '').trim() }
function isResultEvent(event: LedgerEvent) { return /响应|结果|回复/.test(event.title) }
function TraceEventRow({ event, selected, onClick }: { event: LedgerEvent; selected: boolean; onClick: () => void }) {
  const role = ROLE_TAGS[event.kind] || { tag: 'EVENT', cls: 'model' }
  const name = eventName(event)
  return <button className={`trace-event ${event.kind} ${event.state}${selected ? ' selected' : ''}`} data-state={event.state} title={event.title} onClick={onClick} aria-pressed={selected}>
    <span className="event-rail" />
    <span className="event-slot"><span className={`kind-tag ${role.cls}${event.state === 'failed' ? ' failed' : ''}`}>{role.tag}</span></span>
    <span className="event-body">
      {name && <span className="event-name">{name}</span>}
      {event.summary && <>{isResultEvent(event) && <span className="event-arrow" aria-hidden="true">→</span>}<span className="event-payload">{event.summary}</span></>}
    </span>
  </button>
}
function TraceInspector({ message, event, detail, setDetail }: { message?: Message; event?: LedgerEvent; detail: 'summary' | 'request' | 'result' | 'timing'; setDetail: (value: 'summary' | 'request' | 'result' | 'timing') => void }) {
  const trace = message?.trace
  return <aside className="trace-inspector">
    <div className="inspector-heading"><div><span className="eyebrow">检查器</span><strong>{event?.title || (message ? `Turn ${message.id.split('-').at(-1)}` : '未选择')}</strong>{event && <small>事件 {String(event.order).padStart(2, '0')} · {event.kind}</small>}</div><FileText size={16} /></div>
    <div className="inspector-tabs">{(['summary', 'request', 'result', 'timing'] as const).map((tab) => <button key={tab} className={detail === tab ? 'active' : ''} onClick={() => setDetail(tab)}>{tab === 'summary' ? '摘要' : tab === 'request' ? '请求' : tab === 'result' ? '结果' : '时序'}</button>)}</div>
    {message && <div className="sensitive-note">完整请求可能包含对话内容、工具参数或本地文件片段，仅保存在本机。</div>}
    {detail === 'summary' && event ? <EventSummary event={event} /> : <pre className="inspector-code">{event ? eventInspectorBody(event, detail) : inspectorBody(message, detail)}</pre>}
    {trace?.answerContractRepaired && <div className="inspector-warning"><X size={14} />答案契约已修复：{trace.forcedAnswerReason || trace.answerViolations?.join(', ')}</div>}
  </aside>
}
function EventSummary({ event }: { event: LedgerEvent }) {
  const role = ROLE_TAGS[event.kind] || { tag: 'EVENT', cls: 'model' }
  const timing = event.timing as { durationMs?: number; usage?: { promptTokens?: number; completionTokens?: number } } | undefined
  const rows: Array<[string, string]> = [['类型', role.tag], ['状态', event.state === 'failed' ? '失败' : event.state === 'running' ? '进行中' : '完成']]
  if (timing?.durationMs) rows.push(['耗时', formatDuration(timing.durationMs)])
  if (timing?.usage?.promptTokens) rows.push(['输入 tokens', timing.usage.promptTokens.toLocaleString('zh-CN')])
  if (timing?.usage?.completionTokens) rows.push(['输出 tokens', timing.usage.completionTokens.toLocaleString('zh-CN')])
  return <dl className="inspector-overview">
    {rows.map(([key, value]) => <div key={key}><dt>{key}</dt><dd className={key === '状态' && event.state === 'failed' ? 'error' : ''}>{value}</dd></div>)}
    {event.summary && <div className="inspector-overview-full"><dt>摘要</dt><dd>{event.summary}</dd></div>}
  </dl>
}

function buildLedgerEvents(message: Message): LedgerEvent[] {
  const events: LedgerEvent[] = []
  const add = (event: Omit<LedgerEvent, 'order'>) => events.push({ ...event, order: events.length + 1 })
  const trace = message.trace
  if (message.prompt) add({ id: `${message.id}:input`, kind: 'input', title: '用户输入', summary: shortValue(message.prompt), state: 'completed', request: { prompt: message.prompt }, raw: message.prompt })
  trace?.routeSteps?.forEach((route, index) => {
    const attempt = route.attempt || index + 1
    add({ id: `${message.id}:route:${attempt}:request`, kind: 'route', title: `路由请求 · Attempt ${attempt}`, summary: `${route.request?.bytes || 0} bytes`, state: 'completed', request: route.request, timing: { durationMs: route.durationMs }, raw: route })
    const error = route.protocolError || (route.failedClosed ? '路由失败关闭' : '')
    add({ id: `${message.id}:route:${attempt}:response`, kind: 'route', title: `路由响应 · ${route.route || '未决'}`, summary: error || [route.route, ...(route.bundles || [])].filter(Boolean).join(' · ') || '无可用响应', state: error ? 'failed' : 'completed', result: { modelOutput: route.modelOutput, route: route.route, bundles: route.bundles, protocolError: route.protocolError, failedClosed: route.failedClosed }, timing: { durationMs: route.durationMs }, raw: route })
  })
  trace?.steps.forEach((step) => {
    const prefix = `${message.id}:step:${step.number}`
    if (step.request) add({ id: `${prefix}:model-request`, kind: 'model', title: `模型请求 · Step ${step.number}`, summary: `${step.stage || 'decision'} · ${step.request.bytes || 0} bytes`, state: 'completed', request: step.request, timing: { durationMs: step.modelDurationMs }, raw: step })
    const modelError = step.modelError || step.protocolError
    add({ id: `${prefix}:model-response`, kind: 'model', title: `模型响应 · Step ${step.number}`, summary: shortValue(modelError || step.modelOutput || step.actionType || '空响应'), state: modelError ? 'failed' : 'completed', result: { modelOutput: step.modelOutput, finishReason: step.finishReason, actionType: step.actionType, protocolError: step.protocolError, modelError: step.modelError, usage: step.usage }, timing: { durationMs: step.modelDurationMs, usage: step.usage }, raw: step })
    if (step.protocolError) add({ id: `${prefix}:protocol-retry`, kind: 'retry', title: `协议修复 · Step ${step.number}`, summary: shortValue(step.protocolError), state: step.modelError ? 'failed' : 'completed', request: { correctionFor: step.protocolError }, result: { repaired: step.protocolRepaired, stageViolation: step.stageViolation }, raw: step })
    if (step.tool) {
      add({ id: `${prefix}:tool-call`, kind: 'tool', title: `工具调用 · ${step.tool}`, summary: shortValue(step.toolArguments || '无参数'), state: step.toolError || step.toolRejected ? 'failed' : 'completed', request: { tool: step.tool, arguments: parseJSONValue(step.toolArguments) }, timing: { durationMs: step.toolDurationMs }, raw: step })
      step.toolRetries?.forEach((retry, retryIndex) => add({ id: `${prefix}:tool-retry:${retryIndex + 1}`, kind: 'retry', title: `工具重试 · ${step.tool}`, summary: `Attempt ${retry.attempt}/${retry.maxAttempts} · 等待 ${formatDuration(retry.delayMs)}`, state: 'completed', request: retry, timing: { delayMs: retry.delayMs }, raw: retry }))
      const toolFailure = step.toolError || step.toolRejected
      add({ id: `${prefix}:tool-result`, kind: 'tool', title: `工具结果 · ${step.tool}`, summary: shortValue(toolFailure || step.toolResult || (step.toolExecuted ? '执行完成' : '未执行')), state: toolFailure ? 'failed' : 'completed', result: { result: parseJSONValue(step.toolResult), error: step.toolError, rejected: step.toolRejected, executed: step.toolExecuted, evidence: step.toolEvidence, unavailable: step.toolUnavailable }, timing: { durationMs: step.toolDurationMs }, raw: step })
    }
    step.subagents?.forEach((child) => {
      const childPrefix = `${prefix}:agent:${child.index}`
      add({ id: `${childPrefix}:start`, kind: 'subagent', title: `子 Agent ${child.index} · 启动`, summary: shortValue(child.task), state: 'completed', request: { task: child.task }, raw: child })
      if (child.route) add({ id: `${childPrefix}:route`, kind: 'route', title: `子 Agent ${child.index} · 路由`, summary: [child.route, ...(child.bundles || [])].join(' · '), state: 'completed', result: { route: child.route, bundles: child.bundles }, raw: child })
      child.steps?.forEach((childStep) => {
        const childStepPrefix = `${childPrefix}:step:${childStep.number}`
        add({ id: `${childStepPrefix}:call`, kind: 'tool', title: `子 Agent ${child.index} · 调用 ${childStep.tool}`, summary: shortValue(childStep.arguments || '无参数'), state: childStep.status === 'failed' ? 'failed' : 'completed', request: { tool: childStep.tool, arguments: parseJSONValue(childStep.arguments) }, raw: childStep })
        childStep.retries?.forEach((retry, retryIndex) => add({ id: `${childStepPrefix}:retry:${retryIndex + 1}`, kind: 'retry', title: `子 Agent ${child.index} · 重试 ${childStep.tool}`, summary: `Attempt ${retry.attempt}/${retry.maxAttempts} · 等待 ${formatDuration(retry.delayMs)}`, state: 'completed', request: retry, timing: { delayMs: retry.delayMs }, raw: retry }))
        add({ id: `${childStepPrefix}:result`, kind: 'tool', title: `子 Agent ${child.index} · 工具结果`, summary: childStep.error || childStep.status, state: childStep.status === 'failed' ? 'failed' : 'completed', result: { status: childStep.status, error: childStep.error }, raw: childStep })
      })
      add({ id: `${childPrefix}:result`, kind: 'subagent', title: `子 Agent ${child.index} · ${child.status === 'failed' ? '失败' : '完成'}`, summary: shortValue(child.error || child.output || child.status), state: child.status === 'failed' ? 'failed' : 'completed', result: { status: child.status, output: child.output, error: child.error, sources: child.sources }, timing: { durationMs: child.durationMs }, raw: child })
    })
  })
  if (trace?.error || message.role === 'error') add({ id: `${message.id}:error`, kind: 'output', title: 'Agent 运行失败', summary: shortValue(trace?.error || message.content), state: 'failed', result: { error: trace?.error || message.content }, timing: { durationMs: trace?.durationMs }, raw: trace || message })
  else if (trace?.output || message.role === 'assistant') add({ id: `${message.id}:output`, kind: 'output', title: '最终回复', summary: shortValue(trace?.output || message.content), state: 'completed', result: { output: trace?.output || message.content }, timing: { durationMs: trace?.durationMs }, raw: trace || message })
  if (!trace && message.trajectory?.length) message.trajectory.forEach((item, index) => add({ id: `${message.id}:legacy:${item.step}:${index}`, kind: 'tool', title: `STEP ${item.step} · ${item.tool}`, summary: item.error || item.status, state: item.status === 'failed' ? 'failed' : 'completed', request: { tool: item.tool, arguments: item.arguments }, result: { status: item.status, error: item.error, subagents: item.subagents }, raw: item }))
  return events
}

function liveLedgerEvents(activity: AgentActivity[]): LedgerEvent[] {
  const matchesScope = (left: AgentActivity, right: AgentActivity) => left.step === right.step && left.parentStep === right.parentStep && left.subagentIndex === right.subagentIndex && (!left.tool || !right.tool || left.tool === right.tool)
  const later = (index: number, doneKind: string) => activity.slice(index + 1).some((candidate) => candidate.kind === doneKind && matchesScope(activity[index], candidate))
  return activity.map((item, index) => {
    const child = item.subagentIndex ? `子 Agent ${item.subagentIndex} · ` : ''
    let title = 'Agent 事件'; let summary = activityLabel(item); let kind: LedgerEvent['kind'] = 'model'; let state: LedgerEvent['state'] = item.error ? 'failed' : 'completed'
    if (item.kind === 'route_start') { title = `${child}路由请求`; summary = '正在选择能力组'; kind = 'route'; state = later(index, 'route_done') ? 'completed' : 'running' }
    else if (item.kind === 'route_done') { title = `${child}路由响应`; summary = item.error || [item.route, ...(item.bundles || [])].filter(Boolean).join(' · '); kind = 'route' }
    else if (item.kind === 'model_start') { title = `${child}模型请求 · Step ${item.step || 1}`; summary = '等待模型响应'; state = later(index, 'model_done') ? 'completed' : 'running' }
    else if (item.kind === 'model_done') { title = `${child}模型响应 · Step ${item.step || 1}`; summary = item.error || formatDuration(item.durationMs); state = item.error ? 'failed' : 'completed' }
    else if (item.kind === 'protocol_retry') { title = `${child}协议修复 · Step ${item.step || 1}`; summary = item.error || '重新请求模型'; kind = 'retry' }
    else if (item.kind === 'tool_start') { title = `${child}工具调用 · ${item.tool}`; summary = shortValue(item.arguments || '无参数'); kind = 'tool'; state = later(index, 'tool_done') ? 'completed' : 'running' }
    else if (item.kind === 'tool_retry') { title = `${child}工具重试 · ${item.tool}`; summary = `Attempt ${item.attempt || 1}/${item.maxAttempts || 1} · 等待 ${formatDuration(item.delayMs)}`; kind = 'retry'; state = 'running' }
    else if (item.kind === 'tool_done') { title = `${child}工具结果 · ${item.tool}`; summary = item.error || formatDuration(item.durationMs); kind = 'tool'; state = item.error ? 'failed' : 'completed' }
    else if (item.kind === 'subagent_start') { title = `子 Agent ${item.subagentIndex} · 启动`; summary = shortValue(item.subagentTask || '子任务'); kind = 'subagent'; state = later(index, 'subagent_done') ? 'completed' : 'running' }
    else if (item.kind === 'subagent_done') { title = `子 Agent ${item.subagentIndex} · ${item.error ? '失败' : '完成'}`; summary = item.error || formatDuration(item.durationMs); kind = 'subagent'; state = item.error ? 'failed' : 'completed' }
    return { id: `live:${index}:${item.kind}:${item.parentStep || 0}:${item.step || 0}:${item.subagentIndex || 0}`, order: index + 1, kind, title, summary, state, request: item.arguments ? { arguments: parseJSONValue(item.arguments) } : undefined, result: item.error ? { error: item.error } : undefined, timing: { durationMs: item.durationMs, delayMs: item.delayMs }, raw: item }
  })
}

function ledgerEventIcon(event: LedgerEvent) {
  if (event.state === 'failed') return <CircleAlert size={14} />
  if (event.kind === 'route') return <GitBranch size={14} />
  if (event.kind === 'model') return <Bot size={14} />
  if (event.kind === 'tool') return <Wrench size={14} />
  if (event.kind === 'retry') return <RefreshCw size={14} />
  if (event.kind === 'subagent') return <Users size={14} />
  return <MessageSquareText size={14} />
}

function eventInspectorBody(event: LedgerEvent, detail: 'summary' | 'request' | 'result' | 'timing') {
  if (detail === 'request') return event.request === undefined ? '此事件没有请求数据。' : JSON.stringify(event.request, null, 2)
  if (detail === 'result') return event.result === undefined ? '此事件没有结果数据。' : JSON.stringify(event.result, null, 2)
  if (detail === 'timing') return event.timing === undefined ? '此事件没有时序数据。' : JSON.stringify(event.timing, null, 2)
  return JSON.stringify({ sequence: event.order, type: event.kind, title: event.title, status: event.state, summary: event.summary }, null, 2)
}

function parseJSONValue(value?: string) { if (!value) return value; try { return JSON.parse(value) } catch { return value } }
function shortValue(value: unknown) { const text = typeof value === 'string' ? value : JSON.stringify(value); const compact = (text || '').replace(/\s+/g, ' ').trim(); return compact.length > 92 ? `${compact.slice(0, 89)}...` : compact }

function inspectorBody(message: Message | undefined, detail: 'summary' | 'request' | 'result' | 'timing') {
  if (!message) return '选择一轮轨迹查看详情'
  const trace = message.trace
  if (!trace) return detail === 'summary'
    ? JSON.stringify({ legacyTrajectory: message.trajectory || [], timing: 'unavailable', request: 'unavailable' }, null, 2)
    : '这条历史轨迹未保存该类详情。'
  if (detail === 'request') return JSON.stringify({
    routeAttempts: trace.routeSteps?.map((route) => ({ attempt: route.attempt, request: route.request })),
    steps: trace.steps.map((step) => ({
      step: step.number, stage: step.stage, request: step.request, tool: step.tool, toolArguments: step.toolArguments,
      subagents: step.subagents?.map((child) => ({ index: child.index, task: child.task, route: child.route, bundles: child.bundles, steps: child.steps?.map((childStep) => ({ step: childStep.number, tool: childStep.tool, arguments: childStep.arguments })) })),
    })),
  }, null, 2)
  if (detail === 'result') return JSON.stringify({
    output: trace.output, originalOutput: trace.originalOutput,
    routeAttempts: trace.routeSteps?.map((route) => ({ attempt: route.attempt, modelOutput: route.modelOutput, route: route.route, bundles: route.bundles, protocolError: route.protocolError })),
    steps: trace.steps.map((step) => ({
      step: step.number, modelOutput: step.modelOutput, tool: step.tool, toolResult: step.toolResult, toolError: step.toolError, protocolError: step.protocolError,
      subagents: step.subagents?.map((child) => ({ index: child.index, task: child.task, status: child.status, output: child.output, error: child.error, sources: child.sources, steps: child.steps })),
    })),
  }, null, 2)
  if (detail === 'timing') return JSON.stringify({
    durationMs: trace.durationMs,
    routeAttempts: trace.routeSteps?.map((route) => ({ attempt: route.attempt, durationMs: route.durationMs })),
    steps: trace.steps.map((step) => ({ step: step.number, modelMs: step.modelDurationMs, toolMs: step.toolDurationMs, usage: step.usage, subagents: step.subagents?.map((child) => ({ index: child.index, durationMs: child.durationMs })) })),
  }, null, 2)
  const usage = trace.steps.reduce((total, step) => ({ promptTokens: total.promptTokens + (step.usage?.promptTokens || 0), completionTokens: total.completionTokens + (step.usage?.completionTokens || 0) }), { promptTokens: 0, completionTokens: 0 })
  return JSON.stringify({ route: trace.route, bundles: trace.bundles, routeAttempts: trace.routeSteps?.length || 0, steps: trace.steps.length, toolCalls: trace.steps.filter((step) => step.tool).length, subagents: trace.steps.reduce((total, step) => total + (step.subagents?.length || 0), 0), usage, repaired: trace.answerContractRepaired }, null, 2)
}

function CapabilitySettings(props: any) {
  const budgets = [
    ['活动批量', 'maxActiveBatch', 'setMaxActiveBatch', 1, 8],
    ['子 Agent 并发', 'subagentMaxParallel', 'setSubagentMaxParallel', 2, 8],
    ['单 Agent 步数', 'subagentMaxSteps', 'setSubagentMaxSteps', 2, 32],
    ['批次超时（秒）', 'subagentTimeoutSeconds', 'setSubagentTimeoutSeconds', 1, 3600],
    ['远端聚合窗口（毫秒）', 'remoteBatchWaitMS', 'setRemoteBatchWaitMS', 0, 1000],
  ] as const
  return <section className="capability-settings" aria-label="Agent 能力">
    <div className="capability-heading"><strong>Agent 能力</strong><small>按需暴露工具并控制并发预算</small></div>
    <label>工具协议<select aria-label="工具协议" value={props.agentProtocol} onChange={(event) => props.setAgentProtocol(event.target.value as AgentProtocol)}><option value={AgentProtocol.AgentProtocolMarkdown}>Markdown（推荐）</option><option value={AgentProtocol.AgentProtocolXML}>XML（兼容模式）</option></select></label>
    <Toggle icon={<Sparkles size={16} />} label="渐进式工具暴露" description="先选择能力组，再加载具体工具 schema" checked={props.progressiveTools} onChange={props.setProgressiveTools} />
    <Toggle icon={<Globe2 size={16} />} label="网页搜索与正文获取" description="Brave Search + Tavily Extract" checked={props.enableWeb} onChange={props.setEnableWeb} />
    {props.enableWeb && <div className="inline-fields capability-fields"><label>Brave API Key<input type="password" value={props.braveAPIKey} onChange={(event) => props.setBraveAPIKey(event.target.value)} required /></label><label>Tavily API Key<input type="password" value={props.tavilyAPIKey} onChange={(event) => props.setTavilyAPIKey(event.target.value)} required /></label></div>}
    <Toggle icon={<Users size={16} />} label="并发子 Agent" description="一次派发 2–8 个独立任务，不允许嵌套委派" checked={props.enableSubagents} onChange={props.setEnableSubagents} />
    {props.enableSubagents && <div className="budget-grid">{budgets.map(([label, key, setter, min, max]) => <label key={key}>{label}<input aria-label={label} type="number" min={min} max={max} value={props[key]} onChange={(event) => props[setter](Number(event.target.value))} /></label>)}</div>}
  </section>
}
function Toggle({ icon, label, description, checked, onChange }: { icon: React.ReactNode; label: string; description: string; checked: boolean; onChange: (value: boolean) => void }) { return <label className="toggle-row"><span>{icon}<span>{label}<small>{description}</small></span></span><input type="checkbox" aria-label={label} checked={checked} onChange={(event) => onChange(event.target.checked)} /></label> }
function SettingsFooter({ busy, message, action }: { busy: boolean; message: string; action: string }) { return <footer className="settings-footer"><div className="settings-result">{busy && <LoaderCircle className="spin" size={15} />}{message}</div><button type="submit" className="primary" disabled={busy}>{busy ? <LoaderCircle className="spin" size={16} /> : <Cpu size={16} />}{action}</button></footer> }
function ComposerContextLabel() { return null }
function statusLabel(status: Status) { if (status.state === ModelState.ModelReady) return status.model || '模型已就绪'; if (status.state === ModelState.ModelLoading) return '模型加载中'; if (status.state === ModelState.ModelError) return '模型错误'; return '未选择模型' }
function relativeTime(value: string) { const timestamp = new Date(value).getTime(); if (!Number.isFinite(timestamp)) return ''; const elapsed = Math.max(0, Math.floor((Date.now() - timestamp) / 1000)); if (elapsed < 60) return '刚刚'; const minutes = Math.floor(elapsed / 60); if (minutes < 60) return `${minutes} 分钟前`; const hours = Math.floor(minutes / 60); if (hours < 24) return `${hours} 小时前`; return `${Math.floor(hours / 24)} 天前` }
function normalizeTimestamp(value?: string) { if (!value) return undefined; const timestamp = new Date(value).getTime(); return Number.isFinite(timestamp) && timestamp >= Date.UTC(2000, 0, 1) ? value : undefined }
function formatDuration(value?: number) { if (!value) return '--'; return value < 1000 ? `${value} ms` : `${(value / 1000).toFixed(1)} s` }
function legacyTrajectory(steps: Step[]): ToolTrace[] {
  return steps.filter((step) => step.tool).map((step) => ({
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
  }))
}

function groupMessagesIntoTurns(messages: Message[]) {
  const turns: ChatTurn[] = []
  for (const message of messages) {
    if (message.role === 'user') {
      turns.push({ user: message })
      continue
    }
    const current = turns.at(-1)
    if (current && !current.response) current.response = message
    else turns.push({ response: message })
  }
  return turns
}

function completedGutterStatuses(message?: Message): GutterStatus[] {
  if (!message) return [{ label: '等待响应', state: 'idle' }]
  const events = buildLedgerEvents(message).filter((event) => event.kind !== 'input')
  if (events.length === 0) return [{ label: message.role === 'error' ? '运行失败' : '回答完成', state: message.role === 'error' ? 'failed' : 'completed' }]
  return events.slice(-6).map((event) => ({ label: gutterEventLabel(event), state: event.state }))
}

function liveGutterStatuses(events: AgentActivity[]): GutterStatus[] {
  if (events.length === 0) return [{ label: '正在思考', state: 'running' }]
  return liveLedgerEvents(events).slice(-6).map((event) => ({ label: gutterEventLabel(event), state: event.state }))
}

function gutterEventLabel(event: LedgerEvent) { return `${String(event.order).padStart(2, '0')} ${event.title.replace(/ · Step \d+/, '').replace('工具调用 · ', '调用 ').replace('工具结果 · ', '结果 ').replace('模型请求', '请求模型').replace('模型响应', '模型回复')}` }

function aggregateToolStatuses(calls: Array<{ tool: string; status: ToolTrace['status'] }>): GutterStatus[] {
  const grouped = new Map<string, { count: number; state: GutterStatus['state'] }>()
  for (const call of calls) {
    const current = grouped.get(call.tool)
    const state = call.status === 'failed' ? 'failed' : call.status === 'running' ? 'running' : 'completed'
    if (!current) grouped.set(call.tool, { count: 1, state })
    else {
      current.count++
      if (state === 'failed' || (state === 'running' && current.state !== 'failed')) current.state = state
    }
  }
  return [...grouped].map(([tool, value]) => ({ label: `${tool}${value.count > 1 ? ` ×${value.count}` : ''}`, state: value.state }))
}

function traceStats(trace: Result) {
  const tokens = trace.steps.reduce((total, step) => total + (step.usage?.promptTokens || 0) + (step.usage?.completionTokens || 0), 0)
  return { durationMs: trace.durationMs, tokens }
}

function formatTurnTime(value?: string) {
  if (!value) return '本地'
  const date = new Date(value)
  if (Number.isNaN(date.getTime()) || date.getUTCFullYear() <= 1) return '本地'
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function activityLabel(item?: AgentActivity) { if (!item) return '正在思考…'; const child = item.subagentIndex ? `Agent ${item.subagentIndex} · ` : ''; if (item.kind === 'subagent_start') return `Agent ${item.subagentIndex} · 已开始子任务`; if (item.kind === 'subagent_done') return `Agent ${item.subagentIndex} · ${item.error ? '子任务失败' : '子任务完成'}`; if (item.kind === 'model_start') return `${child}步骤 ${item.step || 1} · 正在决定下一步`; if (item.kind === 'route_start') return `${child}正在选择能力组`; if (item.kind === 'tool_start') return `${child}步骤 ${item.step} · 正在使用 ${item.tool}`; if (item.kind === 'tool_retry') return `${child}步骤 ${item.step} · ${item.tool} 自动退避后重试`; if (item.kind === 'tool_done') return `${child}步骤 ${item.step} · ${item.tool} 已完成`; return 'Agent 正在工作…' }
function activityToolTrace(events: AgentActivity[]): ToolTrace[] {
  const result: ToolTrace[] = []
  const parents = new Map<number, ToolTrace>()
  const children = new Map<string, NonNullable<ToolTrace['subagents']>[number]>()
  const parentFor = (event: AgentActivity) => {
    const step = event.parentStep || event.step || 1
    let parent = parents.get(step)
    if (!parent) {
      parent = { step, tool: event.parentStep ? 'spawn_agents' : event.tool || 'tool', status: 'running', subagents: [] }
      parents.set(step, parent); result.push(parent)
    }
    return parent
  }
  const childFor = (event: AgentActivity) => {
    const parent = parentFor(event)
    const index = event.subagentIndex || 1
    const key = `${parent.step}:${index}`
    let child = children.get(key)
    if (!child) {
      child = { index, task: event.subagentTask || `子任务 ${index}`, status: 'running', steps: [] }
      children.set(key, child); parent.subagents = parent.subagents || []; parent.subagents.push(child)
    }
    return child
  }
  for (const event of events) {
    const isChild = event.subagentIndex !== undefined
    if (event.kind === 'tool_start' || event.kind === 'tool_done' || event.kind === 'tool_retry') {
      if (isChild) {
        const child = childFor(event)
        const step = event.step || (child.steps?.length || 0) + 1
        let detail = child.steps?.find((item) => item.step === step)
        if (!detail) { detail = { step, tool: event.tool || 'tool', status: 'running', arguments: event.arguments, retries: [] }; child.steps = child.steps || []; child.steps.push(detail) }
        if (event.kind === 'tool_done') { detail.status = event.error ? 'failed' : 'completed'; detail.error = event.error }
        if (event.kind === 'tool_retry') { detail.status = 'running'; detail.retries = [...(detail.retries || []), { attempt: event.attempt || 1, maxAttempts: event.maxAttempts || 1, statusCode: event.statusCode, delayMs: event.delayMs || 0 }] }
      } else {
        const parent = parentFor(event)
        parent.tool = event.tool || parent.tool
        parent.arguments = event.arguments || parent.arguments
        if (event.kind === 'tool_done') { parent.status = event.error ? 'failed' : 'completed'; parent.error = event.error }
        if (event.kind === 'tool_retry') { parent.status = 'running'; parent.retries = [...(parent.retries || []), { attempt: event.attempt || 1, maxAttempts: event.maxAttempts || 1, statusCode: event.statusCode, delayMs: event.delayMs || 0 }] }
      }
    } else if (event.kind === 'subagent_start') {
      childFor(event)
    } else if (event.kind === 'route_done') {
      const child = childFor(event); child.route = event.route; child.bundles = event.bundles
    } else if (event.kind === 'subagent_done') {
      const child = childFor(event); child.status = event.error ? 'failed' : 'completed'; child.error = event.error; child.durationMs = event.durationMs
    }
  }
  return result
}
function errorText(error: unknown) { return error instanceof Error ? error.message : String(error) }
