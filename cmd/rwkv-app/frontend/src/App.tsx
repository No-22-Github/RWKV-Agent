import { FormEvent, KeyboardEvent, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import {
  ChevronDown, Download, FileText, Folder, FolderOpen, LoaderCircle,
  Menu, MoreHorizontal, PanelRight, Search, Settings, SquarePen,
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
import { useSnackbar } from './snackbar'
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

function ChatView({ messages, activity, busy, ready, workspace, model, capabilities, prompt, setPrompt, onSubmit, onRegenerate, onKeyDown, openSettings, chooseWorkspace, onTrace, messagesEnd }: { messages: Message[]; activity: AgentActivity[]; busy: boolean; ready: boolean; workspace: string; model: string; capabilities: string; prompt: string; setPrompt: (value: string) => void; onSubmit: () => void; onRegenerate: (value: string) => void; onKeyDown: (event: KeyboardEvent<HTMLTextAreaElement>) => void; openSettings: () => void; chooseWorkspace: () => Promise<void>; onTrace: (id: string) => void; messagesEnd: React.RefObject<HTMLDivElement | null> }) {
  const turns = groupMessagesIntoTurns(messages)
  const empty = turns.length === 0
  const stageRef = useRef<HTMLDivElement>(null)
  const composerHostRef = useRef<HTMLDivElement>(null)
  const composer = <Composer prompt={prompt} setPrompt={setPrompt} busy={busy} ready={ready} workspace={workspace} model={model} capabilities={capabilities} turnNumber={turns.length + 1} empty={empty} onSubmit={onSubmit} onKeyDown={onKeyDown} openSettings={openSettings} chooseWorkspace={chooseWorkspace} />

  useLayoutEffect(() => {
    const stage = stageRef.current
    const host = composerHostRef.current
    if (!stage || !host) return
    const stageHeight = stage.clientHeight
    const hostHeight = host.offsetHeight
    host.style.top = empty
      ? `${Math.max(24, (stageHeight - hostHeight) / 2)}px`
      : `${Math.max(0, stageHeight - hostHeight - 28)}px`
  }, [empty, messages.length])

  return <div className="chat-panel relative flex min-h-0 flex-1 flex-col overflow-hidden">
    <div ref={stageRef} className="chat-stage relative min-h-0 flex-1 overflow-hidden">
      {empty && <div className="absolute inset-0 flex items-center justify-center pb-36">
        <div className="flex min-w-0 flex-col items-center gap-[6px] text-center">
          <span className="font-serif text-[16px] text-brand">你好</span>
          <h1 className="m-0 font-serif text-[34px] font-semibold leading-[1.35] tracking-[.01em] text-ink">需要我为你做些什么？</h1>
        </div>
      </div>}
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

function Composer({ prompt, setPrompt, busy, ready, workspace, model, capabilities, turnNumber, empty, onSubmit, onKeyDown, openSettings, chooseWorkspace }: { prompt: string; setPrompt: (value: string) => void; busy: boolean; ready: boolean; workspace: string; model: string; capabilities: string; turnNumber: number; empty?: boolean; onSubmit: () => void; onKeyDown: (event: KeyboardEvent<HTMLTextAreaElement>) => void; openSettings: () => void; chooseWorkspace: () => Promise<void> }) {
  function autoGrow(element: HTMLTextAreaElement) { element.style.height = 'auto'; element.style.height = `${Math.min(element.scrollHeight, 180)}px` }
  return <div className={`flex gap-[42px] ${empty ? 'items-center' : 'items-center'}`}>
    <div className="composer-gutter flex w-[112px] flex-none flex-col items-end gap-1 text-[10.5px] leading-[1.7] text-ink-ghost">
      {!empty && <span className="font-serif text-[19px] font-bold leading-none text-ink-faint">{String(turnNumber).padStart(2, '0')}</span>}
      {!empty && <span className="my-1 h-px w-[34px] bg-line" />}
      <span className="max-w-full truncate text-ink-ghost">工作区<br /><b className="block truncate font-normal text-ink-soft">{workspace}</b></span>
      <span className="max-w-full truncate text-ink-ghost">能力<br /><b className={`block truncate font-normal ${ready ? 'text-brand' : 'text-ink-soft'}`}>{capabilities}</b></span>
    </div>
    <div className="min-w-0 flex-1 border-l-[3px] border-line-strong bg-paper-soft transition-[border-color] duration-[120ms] ease-[cubic-bezier(.2,0,0,1)] motion-reduce:transition-none focus-within:border-brand">
      <textarea aria-label="消息" rows={1} value={prompt} disabled={busy} placeholder="描述你想要完成的任务" className="block w-full min-h-[52px] max-h-[180px] resize-none border-0 bg-transparent p-[13px_15px_6px] text-[14.5px] leading-[1.7] text-ink outline-0 placeholder:text-placeholder" onChange={(event) => { setPrompt(event.target.value); autoGrow(event.target) }} onKeyDown={onKeyDown} />
      <div className="flex min-h-[42px] items-end justify-end gap-3 px-[12px] pb-[12px] pl-3">
        <button className="h-[29px] border-0 bg-brand px-[14px] text-[12.5px] font-semibold text-white transition-colors duration-[120ms] ease-[cubic-bezier(.2,0,0,1)] motion-reduce:transition-none disabled:bg-disabled-bg disabled:text-disabled-text" aria-label="发送" onClick={() => void onSubmit()} disabled={!prompt.trim() || busy}>{busy ? <LoaderCircle size={15} className="spin" /> : <>发送<span className="ml-[7px] font-mono text-[10px] opacity-70">⏎</span></>}</button>
      </div>
    </div>
  </div>
}

function TraceView({ messages, selected, onSelect, onBackToChat }: { messages: Message[]; selected?: Message; onSelect: (id: string) => void; onBackToChat: () => void }) {
  const [query, setQuery] = useState(''); const [inspector, setInspector] = useState(true); const [detail, setDetail] = useState<'summary' | 'original' | 'diff'>('summary'); const [selectedEventID, setSelectedEventID] = useState('')
  const { show } = useSnackbar()
  const visible = messages.filter((message) => !query || `${message.prompt} ${message.content} ${JSON.stringify(message.trace || message.trajectory)}`.toLowerCase().includes(query.toLowerCase()))
  const selectedEvent = selectedEventID ? selected && buildLedgerEvents(selected).find((event) => event.id === selectedEventID) : undefined
  const eventCount = messages.reduce((sum, message) => sum + buildLedgerEvents(message).length, 0)
  const timelineEvents = visible.flatMap((message) => buildLedgerEvents(message).map((event) => ({ event, messageId: message.id })))
  async function exportTrace() {
    const data = visible.map((message) => JSON.stringify({ id: message.id, role: message.role, prompt: message.prompt, createdAt: message.createdAt, trace: message.trace || { legacyTrajectory: message.trajectory } })).join('\n')
    try {
      const path = await Backend.ExportTrajectory(data)
      if (path) show(`轨迹已导出：${path.split('/').at(-1)}`, 'success')
    } catch (error) {
      show(errorText(error), 'error')
    }
  }
  function selectTurn(id: string) { setSelectedEventID(''); onSelect(id) }
  function selectEvent(messageID: string, eventID: string) { onSelect(messageID); setSelectedEventID(eventID) }
  return <div className="flex min-h-0 flex-1 flex-col">
    <div className="trace-toolbar flex min-h-[56px] items-center gap-[10px] border-b border-line px-[30px]"><div className="mr-auto flex items-baseline gap-[5px] text-[10px] text-ink-muted"><strong className="ml-[7px] font-mono text-[15px] font-semibold text-ink">{messages.length}</strong><span>轮次</span><strong className="ml-[7px] font-mono text-[15px] font-semibold text-ink">{eventCount}</strong><span>事件</span></div><label className="flex h-[30px] w-[235px] items-center gap-[7px] border border-line bg-paper-wash px-[9px] text-ink-muted"><Search size={15} /><input aria-label="搜索轨迹" className="w-full border-0 bg-transparent text-[11px] text-ink outline-0" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索请求、工具或错误" /></label><button className="grid h-[30px] w-[30px] place-items-center rounded-[3px] border border-transparent bg-transparent text-ink-soft hover:border-line-strong hover:bg-paper-wash hover:text-brand" title="检查器" aria-label="检查器" onClick={() => setInspector(!inspector)}><PanelRight size={16} /></button></div>
    {timelineEvents.length > 0 && <TraceTimeline events={timelineEvents} selectedEventID={selectedEventID} onEvent={selectEvent} />}
    <div className="trace-workspace flex min-h-0 flex-1"><div className="trace-main min-w-0 flex-1 overflow-auto"><div className="mx-auto w-[min(940px,calc(100%-60px))] py-[14px] pb-10">{visible.map((message, index) => <TraceTurn key={message.id} message={message} index={index + 1} selected={message.id === selected?.id} selectedEventID={selectedEventID} onClick={() => selectTurn(message.id)} onEvent={(eventID) => selectEvent(message.id, eventID)} />)}{visible.length === 0 && <div className="py-[50px] text-center text-[12px] text-ink-muted">没有匹配的轨迹</div>}</div></div>{inspector && <TraceInspector message={selected} event={selectedEvent} detail={detail} setDetail={setDetail} onBackToChat={onBackToChat} />}</div>
    <div className="flex flex-none items-center gap-[22px] border-t-[1.5px] border-ink px-[30px] py-[10px] font-mono text-[10.5px] text-ink-soft">
      <span>{messages.length} 轮 · {eventCount} 步</span><span className="text-ink-ghost">/</span>
      <span>LLM {formatDuration(totalTiming(messages).llmMs)} · 工具 {formatDuration(totalTiming(messages).toolMs)}</span><span className="text-ink-ghost">/</span>
      <span>首 token {formatDuration(totalTiming(messages).firstTokenMs)} · {totalTiming(messages).tokensPerSec} tok/s</span><span className="text-ink-ghost">/</span>
      <span>缓存 {totalTiming(messages).cachePercent}%</span>
      <span className="flex-1" />
      <button className="border-0 bg-transparent p-0 text-[12px] text-brand" onClick={() => void exportTrace()}>导出 trace.jsonl</button>
    </div>
  </div>
}

function TraceTimeline({ events, selectedEventID, onEvent }: { events: { event: LedgerEvent; messageId: string }[]; selectedEventID: string; onEvent: (messageID: string, eventID: string) => void }) {
  const lanes = [
    { key: 'input', label: '输入', color: 'var(--accent-warm)' },
    { key: 'model', label: '模型', color: 'var(--brand)' },
    { key: 'tool', label: '工具', color: 'var(--warning)' },
  ] as const
  const totalDuration = Math.max(1, events.reduce((sum, { event }) => sum + ((event.timing as { durationMs?: number } | undefined)?.durationMs || 0), 0))
  return <div className="grid h-[68px] flex-none grid-cols-[38px_minmax(0,1fr)] items-center border-b border-line bg-paper-soft px-[30px]">
    <div />
    <div className="flex flex-col gap-[3px]">
      {lanes.map((lane) => {
        const laneEvents = events.filter(({ event }) => eventLane(event.kind) === (lane.key === 'input' ? 0 : lane.key === 'model' ? 1 : 2))
        return (
          <div key={lane.key} className="grid grid-cols-[38px_minmax(0,1fr)] items-center gap-[12px]">
            <span className="text-right font-mono text-[9.5px] uppercase tracking-[.1em] text-ink-muted">{lane.label}</span>
            <div className="flex h-[9px] items-center gap-[3px] overflow-hidden">
              {laneEvents.map(({ event, messageId }) => {
                const duration = ((event.timing as { durationMs?: number } | undefined)?.durationMs || 0)
                const width = Math.max(2, (duration / totalDuration) * 100)
                return <button key={event.id} title={event.title} aria-label={event.title} onClick={() => onEvent(messageId, event.id)} className={`h-[7px] flex-none border-0 p-0 ${event.id === selectedEventID ? 'ring-1 ring-paper-soft ring-offset-1' : ''}`} style={{ width: `${width}%`, background: lane.color, opacity: event.state === 'failed' ? 1 : 0.7 }} />
              })}
            </div>
          </div>
        )
      })}
      <div className="mt-[3px] grid grid-cols-[38px_minmax(0,1fr)] gap-[12px]">
        <span />
        <div className="flex justify-between font-mono text-[9.5px] text-ink-ghost"><span>00:00</span><span>{formatClock(totalDuration * 0.25)}</span><span>{formatClock(totalDuration * 0.5)}</span><span>{formatClock(totalDuration * 0.75)}</span><span>{formatClock(totalDuration)}</span></div>
      </div>
    </div>
  </div>
}

function TraceTurn({ message, index, selected, selectedEventID, onClick, onEvent }: { message: Message; index: number; selected: boolean; selectedEventID: string; onClick: () => void; onEvent: (eventID: string) => void }) {
  const trace = message.trace
  const events = buildLedgerEvents(message)
  const duration = trace?.durationMs || 0
  return <article className="mb-[18px] grid w-full grid-cols-[56px_minmax(0,1fr)] gap-4">
    <div className="flex flex-col items-end gap-[3px] font-serif text-[20px] font-bold leading-none text-ink-faint">{String(index).padStart(2, '0')}<small className="font-mono text-[10px] text-ink-muted">{message.createdAt ? new Date(message.createdAt).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) : '本地'}</small></div>
    <div className="min-w-0"><button className="mb-[6px] block w-full border-0 bg-transparent p-0 text-left text-inherit" onClick={onClick}><span className="flex items-center gap-[10px] text-[10px] text-ink-muted"><span className="font-mono text-[10px] font-semibold tracking-[.04em] text-brand">TURN {index}</span><span>{events.length} 个事件</span><span>{duration ? formatDuration(duration) : '时长 --'}</span>{trace?.route && <span className="ml-auto font-mono text-[10px] text-brand">{trace.route}</span>}{message.role === 'error' && <span className="ml-auto font-mono text-[10px] text-danger">失败</span>}</span><span className="mt-[6px] block truncate text-[12px] text-ink-soft">{message.prompt || message.content}</span></button>
      <div className="flex flex-col border-t border-line">{events.map((event) => <TraceEventRow key={event.id} event={event} selected={selected && selectedEventID === event.id} onClick={() => onEvent(event.id)} />)}</div>
    </div>
  </article>
}
const ROLE_TAGS: Record<LedgerEvent['kind'], { tag: string; cls: string }> = {
  input: { tag: 'USER', cls: 'user' }, route: { tag: 'ROUTE', cls: 'route' }, model: { tag: 'MODEL', cls: 'model' },
  tool: { tag: 'TOOL', cls: 'tool' }, retry: { tag: 'RETRY', cls: 'tool' }, subagent: { tag: 'AGENT', cls: 'model' }, output: { tag: 'SUBMIT', cls: 'submit' },
}
const KIND_TAG_CLASS: Record<string, string> = {
  user: 'text-ink-strong',
  route: 'text-brand',
  model: 'text-brand',
  agent: 'text-brand',
  tool: 'text-warning',
  retry: 'text-warning',
  submit: 'text-brand',
}
const EVENT_TITLE_PREFIX = /^(用户输入|路由请求|路由响应|模型请求|模型响应|协议修复|工具调用|工具结果|工具重试|最终回复)\s*·?\s*/
function eventLane(kind: LedgerEvent['kind']) { if (kind === 'tool' || kind === 'retry' || kind === 'subagent') return 2; if (kind === 'model' || kind === 'output') return 1; return 0 }
function eventName(event: LedgerEvent) { return event.title.replace(EVENT_TITLE_PREFIX, '').trim() }
function isResultEvent(event: LedgerEvent) { return /响应|结果|回复/.test(event.title) }
function TraceEventRow({ event, selected, onClick }: { event: LedgerEvent; selected: boolean; onClick: () => void }) {
  const role = ROLE_TAGS[event.kind] || { tag: 'EVENT', cls: 'model' }
  const name = eventName(event)
  const railWidth = selected ? 'w-[3px]' : 'w-[2px]'
  const railColor = event.state === 'failed' ? 'bg-danger' : selected ? 'bg-brand' : 'bg-transparent'
  return <button className={`trace-event relative grid w-full min-h-[30px] grid-cols-[76px_minmax(0,1fr)] items-center gap-2 overflow-hidden border-0 border-b border-line bg-transparent p-[4px_8px_4px_0] text-left hover:bg-paper-soft${selected ? ' bg-brand-wash' : ''}${selected && event.state === 'failed' ? ' bg-danger-wash' : ''}`} data-state={event.state} title={event.title} onClick={onClick} aria-pressed={selected}>
    <span className={`absolute bottom-0 left-0 top-0 ${railWidth} ${railColor}`} />
    <span className="flex justify-end pl-3"><span className={`inline-flex font-mono text-[10px] font-medium tracking-[.14em] ${KIND_TAG_CLASS[role.cls] || 'text-brand'}`}>{role.tag}</span></span>
    <span className="flex min-w-0 items-baseline gap-[7px] overflow-hidden">
      {name && <span className="event-name max-w-[46%] flex-none truncate font-mono text-[12px] leading-[18px] text-ink">{name}</span>}
      {event.summary && <>{isResultEvent(event) && <span className="event-arrow flex-none text-[12px] text-ink-muted" aria-hidden="true">→</span>}<span className={`event-payload min-w-0 flex-1 truncate font-mono text-[12px] leading-[18px] ${event.state === 'failed' ? 'text-danger' : 'text-ink-soft'}`}>{event.summary}</span></>}
    </span>
  </button>
}
function TraceInspector({ message, event, detail, setDetail, onBackToChat }: { message?: Message; event?: LedgerEvent; detail: 'summary' | 'original' | 'diff'; setDetail: (value: 'summary' | 'original' | 'diff') => void; onBackToChat: () => void }) {
  const trace = message?.trace
  return <aside className="trace-inspector w-[320px] flex-none overflow-auto border-l border-line bg-paper-soft">
    <div className="flex items-center justify-between px-5 pb-[14px] pt-[22px]"><div className="flex min-w-0 flex-col gap-[5px]"><span className="font-mono text-[10px] uppercase tracking-[.14em] text-ink-muted">检查器</span><strong className="truncate text-[14px] font-semibold">{event?.title || (message ? `Turn ${message.id.split('-').at(-1)}` : '未选择')}</strong>{event && <small className="font-mono text-[9px] text-ink-muted">事件 {String(event.order).padStart(2, '0')} · {event.kind}</small>}</div><FileText size={16} /></div>
    <div className="flex gap-[15px] border-b border-line px-5">{(['summary', 'original', 'diff'] as const).map((tab) => <button key={tab} className={`border-0 border-b-2 bg-transparent pb-[9px] text-[11px] ${detail === tab ? 'border-brand font-semibold text-brand' : 'border-transparent text-ink-muted'}`} onClick={() => setDetail(tab)}>{tab === 'summary' ? '摘要' : tab === 'original' ? '原文' : '差异'}</button>)}</div>
    {message && <div className="mx-5 mt-4 border-l-2 border-warning bg-warning/10 px-[10px] py-2 text-[10px] leading-[1.6] text-warning">完整请求可能包含对话内容、工具参数或本地文件片段，仅保存在本机。</div>}
    {detail === 'summary' && event ? <EventSummary event={event} /> : <pre className="mx-5 my-[14px] overflow-auto whitespace-pre-wrap font-mono text-[10px] leading-[1.65] text-ink-soft [overflow-wrap:anywhere]">{detail === 'diff' ? inspectorDiff(message, event) : inspectorBody(message, event, detail)}</pre>}
    {trace?.answerContractRepaired && <div className="mx-5 my-[14px] flex gap-[6px] bg-danger-wash p-[9px] text-[10px] leading-[1.5] text-danger"><X size={14} />答案契约已修复：{trace.forcedAnswerReason || trace.answerViolations?.join(', ')}</div>}
    <div className="mt-auto border-t border-line px-5 py-4"><button className="h-[30px] border-[1.5px] border-ink bg-transparent px-[14px] text-[12px] font-medium text-ink" onClick={onBackToChat}>回到对话第 1 轮</button></div>
  </aside>
}
function EventSummary({ event }: { event: LedgerEvent }) {
  const role = ROLE_TAGS[event.kind] || { tag: 'EVENT', cls: 'model' }
  const timing = event.timing as { durationMs?: number; usage?: { promptTokens?: number; completionTokens?: number } } | undefined
  const rows: Array<[string, string]> = [['类型', role.tag], ['状态', event.state === 'failed' ? '失败' : event.state === 'running' ? '进行中' : '完成']]
  if (timing?.durationMs) rows.push(['耗时', formatDuration(timing.durationMs)])
  if (timing?.usage?.promptTokens) rows.push(['输入 tokens', timing.usage.promptTokens.toLocaleString('zh-CN')])
  if (timing?.usage?.completionTokens) rows.push(['输出 tokens', timing.usage.completionTokens.toLocaleString('zh-CN')])
  return <dl className="mt-[14px] py-[6px]">
    {rows.map(([key, value]) => <div key={key} className="grid min-h-[26px] grid-cols-[88px_minmax(0,1fr)] items-center gap-[10px] px-5"><dt className="text-[12px] text-ink-muted">{key}</dt><dd className={`m-0 truncate text-[12px] ${key === '状态' && event.state === 'failed' ? 'text-danger' : 'text-ink'}`}>{value}</dd></div>)}
    {event.summary && <div className="grid min-h-0 grid-cols-1 items-start gap-[5px] px-5 pt-[10px]"><dt className="text-[12px] text-ink-muted">摘要</dt><dd className="m-0 text-[12px] leading-[1.65] text-ink-soft [overflow-wrap:anywhere]">{event.summary}</dd></div>}
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

function eventInspectorBody(event: LedgerEvent, detail: 'summary' | 'original' | 'diff') {
  if (detail === 'original') return JSON.stringify(event.raw ?? event.request ?? event.result ?? {}, null, 2)
  if (detail === 'diff') return JSON.stringify({ sequence: event.order, type: event.kind, title: event.title, status: event.state, summary: event.summary, raw: event.raw }, null, 2)
  return JSON.stringify({ sequence: event.order, type: event.kind, title: event.title, status: event.state, summary: event.summary }, null, 2)
}

function parseJSONValue(value?: string) { if (!value) return value; try { return JSON.parse(value) } catch { return value } }
function shortValue(value: unknown) { const text = typeof value === 'string' ? value : JSON.stringify(value); const compact = (text || '').replace(/\s+/g, ' ').trim(); return compact.length > 92 ? `${compact.slice(0, 89)}...` : compact }

function inspectorBody(message: Message | undefined, event: LedgerEvent | undefined, detail: 'summary' | 'original' | 'diff') {
  if (!message) return '选择一轮轨迹查看详情'
  if (event) return eventInspectorBody(event, detail)
  const trace = message.trace
  if (!trace) return detail === 'summary'
    ? JSON.stringify({ legacyTrajectory: message.trajectory || [], timing: 'unavailable', request: 'unavailable' }, null, 2)
    : '这条历史轨迹未保存该类详情。'
  if (detail === 'original') return JSON.stringify({
    routeAttempts: trace.routeSteps?.map((route) => ({ attempt: route.attempt, request: route.request, result: route })),
    steps: trace.steps.map((step) => ({ step: step.number, raw: step })),
    output: trace.output, originalOutput: trace.originalOutput,
  }, null, 2)
  if (detail === 'diff') return JSON.stringify({
    output: trace.output, originalOutput: trace.originalOutput,
    answerContractRepaired: trace.answerContractRepaired,
    forcedAnswerReason: trace.forcedAnswerReason,
    answerViolations: trace.answerViolations,
  }, null, 2)
  return JSON.stringify({ route: trace.route, bundles: trace.bundles, routeAttempts: trace.routeSteps?.length || 0, steps: trace.steps.length, toolCalls: trace.steps.filter((step) => step.tool).length, subagents: trace.steps.reduce((total, step) => total + (step.subagents?.length || 0), 0), usage: trace.steps.reduce((total, step) => ({ promptTokens: total.promptTokens + (step.usage?.promptTokens || 0), completionTokens: total.completionTokens + (step.usage?.completionTokens || 0) }), { promptTokens: 0, completionTokens: 0 }), repaired: trace.answerContractRepaired }, null, 2)
}

function inspectorDiff(message: Message | undefined, event: LedgerEvent | undefined) {
  return inspectorBody(message, event, 'diff')
}

function traceStats(trace: Result) {
  const tokens = trace.steps.reduce((total, step) => total + (step.usage?.promptTokens || 0) + (step.usage?.completionTokens || 0), 0)
  return { durationMs: trace.durationMs, tokens }
}

function totalTiming(messages: Message[]) {
  let llmMs = 0, toolMs = 0, tokens = 0, firstTokenMs = 0
  for (const message of messages) {
    const trace = message.trace
    if (!trace) continue
    for (const step of trace.steps) {
      llmMs += step.modelDurationMs || 0
      toolMs += step.toolDurationMs || 0
      tokens += (step.usage?.promptTokens || 0) + (step.usage?.completionTokens || 0)
      if (!firstTokenMs) firstTokenMs = step.modelDurationMs || 0
    }
  }
  const tokensPerSec = tokens > 0 && llmMs > 0 ? Math.round((tokens / llmMs) * 1000) : 0
  const cachePercent = 96
  return { llmMs, toolMs, tokensPerSec, cachePercent, firstTokenMs }
}

function formatClock(ms: number) {
  const totalSeconds = Math.max(0, Math.round(ms / 1000))
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
}

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
