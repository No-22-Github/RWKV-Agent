import { FormEvent, KeyboardEvent, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import {
  ChevronDown, Folder, FolderOpen, LoaderCircle,
  Menu, MoreHorizontal, Settings, SquarePen,
  Trash2, X,
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
import type { ToolTrace } from './trajectory-types'
import RunConfigDropdown from './components/RunConfigDropdown'
import SettingsPage from './components/SettingsPage'
import SubagentCards from './components/SubagentCards'
import TraceView from './components/TraceView'
import { buildLedgerEvents, formatDuration, parseJSONValue, shortValue, traceStats } from './ledger'
import { getInitialTheme, toggleTheme, type ThemeMode } from './theme'

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
  const [runConfigOpen, setRunConfigOpen] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
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
  const [theme, setTheme] = useState<ThemeMode>(() => getInitialTheme())
  const messagesEnd = useRef<HTMLDivElement>(null)

  useEffect(() => {
    Backend.Bootstrap().then(applyBootstrap).catch((error: unknown) => setStatus(new Status({ ...emptyStatus, state: ModelState.ModelError, message: errorText(error) })))
    const offStatus = Events.On('model:status', (event) => setStatus(Status.createFrom(event.data)))
    const offAgent = Events.On('agent:event', (event) => setActivity((current) => [...current, event.data as AgentActivity]))
    return () => { offStatus(); offAgent() }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
  useEffect(() => { messagesEnd.current?.scrollIntoView({ block: 'end' }) }, [messages])

  useEffect(() => {
    function onKeyDown(event: globalThis.KeyboardEvent) {
      const mod = event.metaKey || event.ctrlKey
      if (!mod) return
      if (event.key.toLowerCase() === 'n') {
        event.preventDefault()
        void newConversation()
      } else if (event.key === ',') {
        event.preventDefault()
        setRunConfigOpen(false)
        setSettingsOpen(true)
      } else if (event.key.toLowerCase() === 'k') {
        event.preventDefault()
        document.querySelector<HTMLTextAreaElement>('textarea[aria-label="消息"]')?.focus()
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [busy])

  const ready = status.state === ModelState.ModelReady
  const workspaceName = useMemo(() => status.workspace ? status.workspace.split(/[\\/]/).filter(Boolean).at(-1) || status.workspace : '未打开工作区', [status.workspace])
  const capabilities = [enableWeb ? 'web' : null, enableSubagents ? 'subagents' : null].filter(Boolean).join(' · ') || '无'

  function handleToggleTheme() {
    setTheme((current) => toggleTheme(current))
  }

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
  async function sendMessage(value: string) {
    const content = value.trim(); if (!content || busy) return
    if (!ready) { setSettingsOpen(true); setSettingsMessage('请先加载本地模型或配置远端 API。'); return }
    setPrompt(''); setActivity([]); setMessages((current) => [...current, { id: `pending-${nextMessageID++}`, role: 'user', content, createdAt: new Date().toISOString() }]); setBusy(true)
    try {
      const result = await Backend.Chat(content)
      const assistant: Message = { id: `pending-${nextMessageID++}`, role: 'assistant', content: result.output, prompt: content, trace: result, createdAt: new Date().toISOString(), meta: `${result.steps.length} 步 · ${(result.durationMs / 1000).toFixed(1)} 秒`, trajectory: legacyTrajectory(result.steps) }
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
  function submitMessage() { void sendMessage(prompt) }
  function regenerate(value: string) { void sendMessage(value) }
  function onComposerKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); void sendMessage(prompt) } }
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
  const turns = groupMessagesIntoTurns(messages)
  const settingsProps = {
    status, ready, settingsTab, setSettingsTab,
    modelPath, setModelPath, tokenizerPath, setTokenizerPath,
    remoteEndpoint, setRemoteEndpoint, remoteModel, setRemoteModel,
    remoteProtocol, setRemoteProtocol, apiKey, setAPIKey, headers, setHeaders,
    agentProtocol, setAgentProtocol, progressiveTools, setProgressiveTools,
    enableWeb, setEnableWeb, braveAPIKey, setBraveAPIKey, tavilyAPIKey, setTavilyAPIKey,
    enableSubagents, setEnableSubagents, maxActiveBatch, setMaxActiveBatch,
    remoteBatchWaitMS, setRemoteBatchWaitMS, subagentMaxParallel, setSubagentMaxParallel,
    subagentMaxSteps, setSubagentMaxSteps, subagentTimeoutSeconds, setSubagentTimeoutSeconds,
    availableModels, setAvailableModels, settingsMessage, settingsBusy,
    workspaceName, onChooseWorkspace: chooseWorkspace,
    onTestRemote: () => void testRemote(),
    onSaveLocal: () => void configureLocal(new Event('submit') as unknown as FormEvent),
    onSaveRemote: () => void configureRemote(new Event('submit') as unknown as FormEvent),
    onClose: () => setSettingsOpen(false),
    theme, onToggleTheme: handleToggleTheme,
  }

  return <div className="flex h-full w-full bg-paper">
    {settingsOpen ? <SettingsPage {...settingsProps} /> : <>
      <Sidebar conversations={conversations} workspaces={workspaces} activeId={activeConversationID} busy={busy} open={sidebarOpen} onCloseSidebar={() => setSidebarOpen(false)} onNewChat={() => void newConversation()} onChooseWorkspace={() => void chooseWorkspace()} onOpenSettings={() => setSettingsOpen(true)} onOpen={openConversation} onDelete={deleteConversation} onOpenWorkspace={openWorkspace} />
      <main className="flex min-w-0 flex-1 flex-col bg-paper">
        <header className="app-header relative flex h-[52px] flex-none items-end gap-[18px] border-b border-line px-[30px]">
          <button className="sidebar-toggle mr-[-6px] grid h-8 w-8 flex-none place-items-center border-0 bg-transparent text-ink-soft lg:hidden" aria-label="打开导航" onClick={() => setSidebarOpen(true)}><Menu size={18} /></button>
          <div className="flex h-9 flex-none items-end gap-[22px]" role="tablist">
            <button role="tab" aria-selected={activeTab === 'chat'} className={`border-0 border-b-2 bg-transparent pb-[9px] font-serif text-[14.5px] transition-[border-color,color] duration-[180ms] ease-[cubic-bezier(.2,0,0,1)] motion-reduce:transition-none ${activeTab === 'chat' ? 'border-brand font-semibold text-ink' : 'border-transparent text-ink-muted'}`} onClick={() => setActiveTab('chat')}>对话</button>
            <button role="tab" aria-selected={activeTab === 'trace'} className={`min-w-[58px] border-0 border-b-2 bg-transparent pb-[9px] text-center font-serif text-[14.5px] transition-[border-color,color] duration-[180ms] ease-[cubic-bezier(.2,0,0,1)] motion-reduce:transition-none ${activeTab === 'trace' ? 'border-brand font-semibold text-ink' : 'border-transparent text-ink-muted'}`} onClick={() => setActiveTab('trace')} disabled={!traceMessages.length}>轨迹 <span className="ml-1 font-mono text-[10px] text-ink-muted">{traceMessages.length || ''}</span></button>
          </div>
          <div className="ml-auto flex items-center gap-[14px] pb-[11px]">
            <span className="hidden text-[11px] text-ink-ghost sm:inline">{turns.length} 轮 · 已保存</span>
            <button className="flex h-[28px] items-center gap-[9px] border border-line bg-paper-wash px-[10px] text-[11.5px] text-ink-soft" onClick={() => setRunConfigOpen((value) => !value)} title={status.model || '运行配置'}>
              <span className={`h-[5px] w-[5px] flex-none rounded-full ${ready ? 'bg-brand-bright' : 'bg-ink-muted'}`} />
              <span className="max-w-[180px] truncate text-ink">{status.model || '选择模型'}</span>
              {ready && <><span className="h-[12px] w-px flex-none bg-line" /><span className="text-ink-muted">{capabilities}</span></>}
              <ChevronDown size={12} className="text-ink-muted" />
            </button>
          </div>
        </header>
        {activeTab === 'trace' ? <TraceView messages={traceMessages} selected={selectedMessage} onSelect={setSelectedTraceID} onBackToChat={() => setActiveTab('chat')} /> : <ChatView messages={messages} activity={activity} busy={busy} ready={ready} workspace={workspaceName} model={status.model || '选择模型'} capabilities={capabilities} prompt={prompt} setPrompt={setPrompt} onSubmit={submitMessage} onRegenerate={regenerate} onKeyDown={onComposerKeyDown} openSettings={() => setSettingsOpen(true)} chooseWorkspace={chooseWorkspace} onTrace={(id) => { setSelectedTraceID(id); setActiveTab('trace') }} messagesEnd={messagesEnd} />}
      </main>
      <RunConfigDropdown open={runConfigOpen} onClose={() => setRunConfigOpen(false)} status={status} ready={ready} availableModels={availableModels} enableWeb={enableWeb} enableSubagents={enableSubagents} progressiveTools={progressiveTools} onToggleWeb={setEnableWeb} onToggleSubagents={setEnableSubagents} onToggleProgressive={setProgressiveTools} onOpenSettings={() => { setRunConfigOpen(false); setSettingsOpen(true) }} />
    </>}
  </div>
}

function Sidebar({ conversations, workspaces, activeId, busy, open, onCloseSidebar, onNewChat, onChooseWorkspace, onOpenSettings, onOpen, onDelete, onOpenWorkspace }: { conversations: ConversationSummary[]; workspaces: WorkspaceItem[]; activeId: string; busy: boolean; open: boolean; onCloseSidebar: () => void; onNewChat: () => void; onChooseWorkspace: () => void; onOpenSettings: () => void; onOpen: (id: string) => void; onDelete: (id: string) => void; onOpenWorkspace: (path: string) => void }) {
  const [menu, setMenu] = useState<string | null>(null)
  return <>
    {open && <div className="sidebar-scrim fixed inset-0 z-[40] bg-[rgba(43,39,33,.34)] lg:hidden" onClick={onCloseSidebar} />}
    <aside className={`app-sidebar fixed inset-y-0 left-0 z-[50] flex h-full w-[216px] flex-none flex-col border-r border-line bg-paper-sidebar py-[18px] text-ink transition-transform duration-200 motion-reduce:transition-none lg:static lg:translate-x-0 ${open ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
      <div className="flex items-center gap-[9px] px-[18px] pb-[18px] font-serif text-[16px] font-semibold tracking-[.02em]"><span className="h-[9px] w-[9px] flex-none rounded-[1px] bg-brand-bright" /><span>RWKV</span><span className="ml-auto font-mono text-[9px] font-medium leading-none text-ink-muted">⌘K</span></div>
      <button className="mx-[18px] mb-[14px] flex h-8 items-center justify-center gap-2 border-[1.5px] border-ink bg-transparent px-[10px] text-[12.5px] font-medium text-ink" onClick={onNewChat} disabled={busy}><SquarePen size={16} />新的对话 <kbd className="ml-[2px] font-mono text-[10px] text-ink-muted">⌘N</kbd></button>
      <button className="mx-[18px] mb-3 flex items-center gap-2 border-0 bg-transparent p-[2px_0] text-[12px] text-ink-soft" onClick={onChooseWorkspace} disabled={busy}><FolderOpen size={16} /><span>打开工作区</span><MoreHorizontal size={15} className="ml-auto" /></button>
      {workspaces.length > 0 && <section className="mb-[6px] flex flex-col"><div className="px-[18px] pb-[7px] text-[10.5px] font-medium uppercase tracking-[.14em] text-ink-muted">工作区</div>{workspaces.map((workspace) => (
        <button key={workspace.path} className={`relative mx-[10px] flex items-center gap-[9px] rounded-[3px] border-0 bg-transparent p-[6px_8px] text-left text-[12.5px] ${workspace.active ? 'bg-surface-active font-semibold text-ink' : 'text-ink-soft'}`} onClick={() => onOpenWorkspace(workspace.path)} disabled={!workspace.available || busy} title={workspace.path}><Folder size={14} /><span className="truncate">{workspace.name}</span>{workspace.active && <span className="ml-auto h-[5px] w-[5px] rounded-full bg-brand-bright" />}</button>
      ))}</section>}
      <section className="min-h-0 flex-1 overflow-y-auto"><div className="px-[18px] pb-[7px] text-[10.5px] font-medium uppercase tracking-[.14em] text-ink-muted">近期</div>
        {conversations.length === 0 ? <div className="px-[18px] py-2 text-[12px] text-ink-muted">暂无历史对话</div> : conversations.map((conversation) => (
          <div key={conversation.id} className={`conversation-row relative mx-[10px] flex items-center rounded-[3px] border-0 bg-transparent ${conversation.id === activeId ? 'active bg-surface-active text-ink' : 'text-ink-soft'}`}>
            <button className="flex min-w-0 flex-1 flex-col gap-[1px] border-0 bg-transparent p-[7px_8px] text-left text-inherit" onClick={() => onOpen(conversation.id)} title={conversation.title || '未命名会话'}><span className="truncate text-[12.5px]">{conversation.title || '未命名会话'}</span><span className="text-[10.5px] text-ink-muted">{relativeTime(conversation.updatedAt)}</span></button>
            <button className="conversation-menu grid h-[26px] w-[26px] place-items-center border-0 bg-transparent text-ink-muted" aria-label="更多操作" onClick={() => setMenu(menu === conversation.id ? null : conversation.id)}><MoreHorizontal size={15} /></button>
            {menu === conversation.id && <button className="absolute right-2 top-[30px] z-[5] flex items-center gap-[7px] rounded-[3px] border border-line-strong bg-paper-wash p-2 px-[10px] text-[12px] text-danger shadow-[0_8px_20px_rgba(45,33,20,.12)]" onClick={() => { setMenu(null); onDelete(conversation.id) }}><Trash2 size={14} />删除会话</button>}
          </div>
        ))}
      </section>
      <button className="mt-3 flex items-center gap-[9px] border-0 border-t border-line bg-transparent px-[18px] pb-0 pt-3 text-left text-[12px] text-ink-soft" onClick={onOpenSettings} aria-label="设置"><Settings size={16} /><span className="flex-1">设置</span><kbd className="ml-[2px] font-mono text-[10px] text-ink-muted">⌘,</kbd></button>
    </aside>
  </>
}

function ChatView({ messages, activity, busy, ready, workspace, capabilities, prompt, setPrompt, onSubmit, onRegenerate, onKeyDown, onTrace, messagesEnd }: { messages: Message[]; activity: AgentActivity[]; busy: boolean; ready: boolean; workspace: string; model: string; capabilities: string; prompt: string; setPrompt: (value: string) => void; onSubmit: () => void; onRegenerate: (value: string) => void; onKeyDown: (event: KeyboardEvent<HTMLTextAreaElement>) => void; openSettings: () => void; chooseWorkspace: () => Promise<void>; onTrace: (id: string) => void; messagesEnd: React.RefObject<HTMLDivElement | null> }) {
  const turns = groupMessagesIntoTurns(messages)
  const empty = turns.length === 0
  const stageRef = useRef<HTMLDivElement>(null)
  const composerHostRef = useRef<HTMLDivElement>(null)
  const composer = <Composer prompt={prompt} setPrompt={setPrompt} busy={busy} ready={ready} workspace={workspace} capabilities={capabilities} turnNumber={turns.length + 1} empty={empty} onSubmit={onSubmit} onKeyDown={onKeyDown} />

  useLayoutEffect(() => {
    const stage = stageRef.current
    const host = composerHostRef.current
    if (!stage || !host) return
    const updatePosition = () => {
      const stageHeight = stage.clientHeight
      const hostHeight = host.offsetHeight
      host.style.top = empty
        ? `${Math.max(24, (stageHeight - hostHeight) / 2)}px`
        : `${Math.max(0, stageHeight - hostHeight - 28)}px`
    }
    updatePosition()
    if (typeof ResizeObserver === 'undefined') return
    const observer = new ResizeObserver(updatePosition)
    observer.observe(stage)
    observer.observe(host)
    return () => observer.disconnect()
  }, [empty])

  return <div className="chat-panel relative flex min-h-0 flex-1 flex-col overflow-hidden">
    <div ref={stageRef} className="chat-stage relative min-h-0 flex-1 overflow-hidden">
      {!empty && <div className="conversation-scroll absolute inset-0 mx-auto w-[min(826px,calc(100%-52px))] overflow-auto py-[30px] pb-7">
        {turns.map((turn, index) => <TurnView key={turn.user?.id || turn.response?.id || index} turn={turn} index={index + 1} pending={busy && index === turns.length - 1 && !turn.response} activity={activity} onTrace={onTrace} onRegenerate={onRegenerate} />)}
        <div ref={messagesEnd} />
      </div>}
    </div>
    <div ref={composerHostRef} className="composer-anchor absolute left-0 right-0 z-[2] mx-auto w-[min(826px,calc(100%-52px))] transition-[top] duration-[420ms] ease-[cubic-bezier(.2,0,0,1)] motion-reduce:transition-none">
      {composer}
    </div>
  </div>
}

function TurnView({ turn, index, pending, activity, onTrace, onRegenerate }: { turn: ChatTurn; index: number; pending: boolean; activity: AgentActivity[]; onTrace: (id: string) => void; onRegenerate: (value: string) => void }) {
  const response = turn.response
  const hasTrace = Boolean(response?.trace || response?.trajectory?.length)
  const subagentCalls = (response?.trajectory || []).filter((call) => call.subagents?.length)
  const subagentCount = subagentCalls.reduce((sum, call) => sum + (call.subagents?.length || 0), 0)
  const statuses = pending ? liveGutterStatuses(activity) : completedGutterStatuses(response)
  const stats = response?.trace ? traceStats(response.trace) : undefined
  const time = turn.user?.createdAt || response?.createdAt
  return <article className={`conversation-turn mb-[42px] grid grid-cols-[112px_minmax(0,672px)] gap-[42px]${pending ? ' pending' : ''}`} data-testid={`conversation-turn-${index}`}>
    <aside className="turn-gutter flex min-w-0 flex-col items-end gap-[6px] pt-[1px] text-right text-ink-muted">
      <span className={`font-serif text-[19px] font-bold leading-none ${response?.role === 'error' ? 'text-danger' : 'text-ink-faint'}`}>{String(index).padStart(2, '0')}</span>
      <time className="text-[10.5px] leading-[1.6]">{formatTurnTime(time)}</time>
      <span className="my-[3px] h-px w-[34px] flex-none bg-line" />
      <div className="gutter-statuses flex w-full flex-col items-end gap-1" aria-label={pending ? 'Agent 运行状态' : 'Agent 完成状态'}>
        {statuses.map((item, statusIndex) => <div className={`gutter-status flex w-full items-center justify-end gap-[7px] text-[10.5px] leading-[1.55] ${item.state === 'failed' ? 'failed text-danger' : item.state === 'running' ? 'running text-brand' : item.state === 'completed' ? 'completed text-ink-soft' : 'text-ink-soft'}`} key={`${item.label}-${statusIndex}`}><span className="min-w-0 truncate">{item.label}</span><i /></div>)}
      </div>
      {subagentCount > 0 && <div className="mt-[2px] flex items-start gap-[7px] text-[10.5px] leading-[1.5] text-ink-ghost"><span>{subagentCount} 路并发<br />见右侧</span><svg width="11" height="26" viewBox="0 0 11 26" fill="none" stroke="var(--brand)" strokeWidth="1.2" className="flex-none"><path d="M5.5 0v6M5.5 6c0 4 4.5 3 4.5 7v13M5.5 6c0 4-4.5 3-4.5 7v13M5.5 6v20" /></svg></div>}
      {(stats || (response?.trajectory?.length && !response.trace)) && <><span className="my-[3px] h-px w-[34px] flex-none bg-line" /><span className="text-[10.5px] leading-[1.6] text-ink-muted">{stats ? <>{formatDuration(stats.durationMs)}{stats.tokens > 0 && <><br />{stats.tokens.toLocaleString('zh-CN')} tok</>}</> : <>历史摘要<br />工具 {response?.trajectory?.length}</>}</span></>}
    </aside>
    <div className="turn-main flex min-w-0 flex-col gap-4">
      {turn.user && <div className="flex justify-end"><div className="min-w-[180px] max-w-[82%] border-l-2 border-user-line bg-user-bg p-[11px_15px] text-[13.5px] leading-[1.7] text-user-text [overflow-wrap:anywhere]">{turn.user.content}</div></div>}
      {pending && <div className="turn-pending-answer min-h-7 pt-[2px]" aria-live="polite"><span className="answer-cursor" /><span className="sr-only">{activityLabel(activity.at(-1))}</span></div>}
      {response?.role === 'assistant' && <div className="turn-answer font-serif text-[15.5px] leading-[1.95] text-ink [overflow-wrap:anywhere]"><MarkdownMessage content={response.content} /></div>}
      {response?.role === 'error' && <div className="flex items-start gap-2 border-l-2 border-danger bg-danger-wash p-[10px_12px] text-[13px] leading-[1.65] text-danger"><X size={15} className="mt-[3px] flex-none" /><span>{response.content}</span></div>}
      {subagentCount > 0 && response && <SubagentCards trajectory={response.trajectory} done={!pending} />}
      {response?.meta && <div className="font-mono text-[10px] text-ink-muted">{response.meta}</div>}
      {response && <div className="turn-actions flex gap-4 pt-[2px]">
        {response.role === 'assistant' && <button className="border-0 bg-transparent p-0 text-[11px] text-ink-muted hover:text-brand" onClick={() => void navigator.clipboard?.writeText(response.content)}>复制</button>}
        {response.role === 'assistant' && turn.user && <button className="border-0 bg-transparent p-0 text-[11px] text-ink-muted hover:text-brand" onClick={() => onRegenerate(turn.user?.content || '')}>重新生成</button>}
        {hasTrace && <button className="border-0 bg-transparent p-0 text-[11px] text-ink-muted hover:text-brand" onClick={() => onTrace(response.id)}>查看轨迹</button>}
      </div>}
    </div>
  </article>
}

function Composer({ prompt, setPrompt, busy, ready, workspace, capabilities, turnNumber, empty, onSubmit, onKeyDown }: { prompt: string; setPrompt: (value: string) => void; busy: boolean; ready: boolean; workspace: string; capabilities: string; turnNumber: number; empty?: boolean; onSubmit: () => void; onKeyDown: (event: KeyboardEvent<HTMLTextAreaElement>) => void }) {
  function autoGrow(element: HTMLTextAreaElement) { element.style.height = 'auto'; element.style.height = `${Math.min(element.scrollHeight, 180)}px` }
  return <div className={`composer grid grid-cols-[112px_minmax(0,672px)] gap-[42px] ${empty ? 'items-end' : 'items-center'}`}>
    <div className={`composer-gutter flex w-[112px] flex-none flex-col items-end gap-1 text-right text-[10.5px] leading-[1.7] text-ink-ghost ${empty ? 'pb-[78px]' : ''}`}>
      {!empty && <span className="font-serif text-[19px] font-bold leading-none text-ink-faint">{String(turnNumber).padStart(2, '0')}</span>}
      {!empty && <span className="my-1 h-px w-[34px] bg-line" />}
      <span className="max-w-full truncate text-ink-ghost">工作区<br /><b className="block truncate font-normal text-ink-soft">{workspace}</b></span>
      {empty && <span className="my-1 h-px w-[34px] bg-line" />}
      <span className="max-w-full truncate text-ink-ghost">能力<br /><b className={`block truncate font-normal ${ready ? 'text-brand' : 'text-ink-soft'}`}>{capabilities}</b></span>
    </div>
    <div className={`flex min-w-0 flex-col ${empty ? 'gap-[26px]' : ''}`}>
      {empty && <div className="flex min-w-0 flex-col gap-[6px]">
        <span className="font-serif text-[16px] text-brand">你好</span>
        <h1 className="m-0 font-serif text-[34px] font-semibold leading-[1.35] tracking-[.01em] text-ink">需要我为你做些什么？</h1>
      </div>}
      <div className="flex min-h-[52px] min-w-0 border-l-[3px] border-line-strong bg-paper-soft transition-[border-color] duration-[120ms] ease-[cubic-bezier(.2,0,0,1)] motion-reduce:transition-none focus-within:border-brand">
        <textarea aria-label="消息" rows={1} value={prompt} disabled={busy} placeholder="描述你想要完成的任务" className="block min-h-[52px] max-h-[180px] min-w-0 flex-1 resize-none border-0 bg-transparent p-[13px_4px_12px_15px] text-[14.5px] leading-[1.7] text-ink outline-0 placeholder:text-placeholder" onChange={(event) => { setPrompt(event.target.value); autoGrow(event.target) }} onKeyDown={onKeyDown} />
        <div className="flex flex-none items-end p-[12px_12px_12px_10px]">
          <button className="h-[29px] border-0 bg-brand px-[14px] text-[12.5px] font-semibold text-white transition-colors duration-[120ms] ease-[cubic-bezier(.2,0,0,1)] motion-reduce:transition-none disabled:bg-disabled-bg disabled:text-disabled-text" aria-label="发送" onClick={() => void onSubmit()} disabled={!prompt.trim() || busy}>{busy ? <LoaderCircle size={15} className="spin" /> : <>发送<span className="ml-[7px] font-mono text-[10px] opacity-70">⏎</span></>}</button>
        </div>
      </div>
      {empty && <div className="flex flex-wrap gap-[9px]" aria-label="快速开始">
        {STARTER_PROMPTS.map((starter) => <button key={starter} className="border border-line bg-card-bg px-3 py-[7px] text-[12px] text-ink-soft hover:border-line-strong hover:text-brand" onClick={() => setPrompt(starter)}>{starter}</button>)}
      </div>}
    </div>
  </div>
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

function activityLabel(item?: AgentActivity) { if (!item) return '正在思考…'; const child = item.subagentIndex ? `Agent ${item.subagentIndex} · ` : ''; if (item.kind === 'subagent_start') return `Agent ${item.subagentIndex} · 已开始子任务`; if (item.kind === 'subagent_done') return `Agent ${item.subagentIndex} · ${item.error ? '子任务失败' : '子任务完成'}`; if (item.kind === 'model_start') return `${child}步骤 ${item.step || 1} · 正在决定下一步`; if (item.kind === 'route_start') return `${child}正在选择能力组`; if (item.kind === 'tool_start') return `${child}步骤 ${item.step} · 正在使用 ${item.tool}`; if (item.kind === 'tool_retry') return `${child}步骤 ${item.step} · ${item.tool} 自动退避后重试`; if (item.kind === 'tool_done') return `${child}步骤 ${item.step} · ${item.tool} 已完成`; return 'Agent 正在工作…' }
function relativeTime(value: string) { const timestamp = new Date(value).getTime(); if (!Number.isFinite(timestamp)) return ''; const elapsed = Math.max(0, Math.floor((Date.now() - timestamp) / 1000)); if (elapsed < 60) return '刚刚'; const minutes = Math.floor(elapsed / 60); if (minutes < 60) return `${minutes} 分钟前`; const hours = Math.floor(minutes / 60); if (hours < 24) return `${hours} 小时前`; return `${Math.floor(hours / 24)} 天前` }
function normalizeTimestamp(value?: string) { if (!value) return undefined; const timestamp = new Date(value).getTime(); return Number.isFinite(timestamp) && timestamp >= Date.UTC(2000, 0, 1) ? value : undefined }
function formatTurnTime(value?: string) {
  if (!value) return '本地'
  const date = new Date(value)
  if (Number.isNaN(date.getTime()) || date.getUTCFullYear() <= 1) return '本地'
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}
function errorText(error: unknown) { return error instanceof Error ? error.message : String(error) }
