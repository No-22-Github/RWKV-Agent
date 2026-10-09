import { KeyboardEvent, useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import {
  Check, Copy, CornerDownLeft, Folder, ListTree, RotateCcw, FolderOpen,
  Menu, MoreHorizontal, PenLine, Pin, Settings, Square, SquarePen,
  Trash2, X,
} from 'lucide-react'
import { Events } from '@wailsio/runtime'
import * as Backend from '../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import { ModelState, Status, type Result, type Step } from '../bindings/github.com/no22/RWKV-Agent/api/models'
import type {
  AppBootstrap, ConversationSummary, ConversationView, WorkspaceItem,
} from '../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/models'
import MarkdownMessage from './MarkdownMessage'
import PacedAnswer from './components/PacedAnswer'
import ConfirmDialog from './components/ConfirmDialog'
import type { ToolTrace } from './trajectory-types'
import RunChips from './components/RunChips'
import SettingsPage from './components/SettingsPage'
import PixelLoader from './components/PixelLoader'
import Wordmark from './components/Wordmark'
import ToolActivity, { ThinkingMark, callsFromEvents, callsFromSteps, callsFromTrajectory } from './components/ToolActivity'
import TrajectoryView from './trajectory/TrajectoryView'
import type { LiveTurn } from './trajectory/rwkv-adapter'
import { traceStats } from './ledger'
import { useProviderManager } from './state/providerManager'
import { getInitialTheme, toggleTheme, type ThemeMode } from './theme'
import { useSnackbar } from './snackbar'

type Message = {
  id: string
  role: 'user' | 'assistant' | 'error'
  content: string
  prompt?: string
  meta?: string
  trajectory?: ToolTrace[]
  trace?: Result
  createdAt?: string
  // 回答已经流式显示过：落定时不再播放显影动画，免得同一段字又闪一次。
  streamed?: boolean
}
// 动画只播一次：对话页在切到轨迹时会整页卸载，这份记录放在 App 层跨越重新挂载。
// seen 记已经播过入场/显影的回合与回答；progress 记流式回答已放出的字数。
type MotionMemory = { seen: Set<string>; progress: Map<string, number> }
type AgentActivity = {
  // 收到事件的时刻：事件本身不带时间戳，轨迹页实时轮次靠它画时间线。
  at: number
  kind: string; step?: number; parentStep?: number; tool?: string; arguments?: string; route?: string
  bundles?: string[]; subagentIndex?: number; subagentTask?: string; durationMs?: number
  attempt?: number; maxAttempts?: number; statusCode?: number; delayMs?: number; error?: string; text?: string
}
type ChatTurn = { user?: Message; response?: Message }

const emptyStatus = new Status({ state: ModelState.ModelIdle, workspace: '', hasApiKey: false, updatedAt: new Date(0).toISOString(), message: '正在连接后端…' })
const STARTER_PROMPTS = ['概括这个仓库的近期进度', '找出最近改动可能引入的风险', '解释这个项目的整体架构']
let nextMessageID = 1

export default function App() {
  const [status, setStatus] = useState<Status>(emptyStatus)
  const [messages, setMessages] = useState<Message[]>([])
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [workspaces, setWorkspaces] = useState<WorkspaceItem[]>([])
  const [activeConversationID, setActiveConversationID] = useState('')
  const [activity, setActivity] = useState<AgentActivity[]>([])
  // 正在生成的回答预览：后端 answer_delta 逐段追加、answer_reset 清空；一轮结束后由正式结果取代。
  const [liveAnswer, setLiveAnswer] = useState('')
  const liveAnswerRef = useRef('')
  const motionMemory = useRef<MotionMemory>({ seen: new Set(), progress: new Map() })
  const [prompt, setPrompt] = useState('')
  const [busy, setBusy] = useState(false)
  const [activeTab, setActiveTab] = useState<'chat' | 'trace'>('chat')
  const [selectedTraceID, setSelectedTraceID] = useState('')
  const [runConfigOpen, setRunConfigOpen] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [theme, setTheme] = useState<ThemeMode>(() => getInitialTheme())
  const messagesEnd = useRef<HTMLDivElement>(null)
  // 是否贴底跟随：用户往上滚就松开，滚回底部附近或发出新一轮时重新贴住。
  // 无条件 scrollIntoView 会在流式的每一帧把正在往上看的用户拽回底部，滚动来回抽搐。
  const followBottom = useRef(true)
  const ready = status.state === ModelState.ModelReady
  const manager = useProviderManager({ onStatus: setStatus, ready })
  const { show: notify } = useSnackbar()
  // 进行中的一轮：Wails 绑定返回可取消的 Promise，取消会中断后端 ctx。
  const runningChat = useRef<{ cancel: () => void } | null>(null)
  // 同步生效的「本轮进行中」标记。busy 是状态，要等下一次渲染才更新：同一瞬间触发两次发送
  // （如输入法确认时连发两次回车）两次都会读到 busy=false，第二条会在后端操作锁上排队，
  // 等第一轮结束后被悄悄跑掉。
  const turnInFlight = useRef(false)
  // 聊天页的失败要在聊天页看得见：settingsMessage 只在设置页底部渲染。
  const reportError = (error: unknown) => notify(errorText(error), 'error')
  const { settingsOpen } = manager

  useEffect(() => {
    Backend.Bootstrap().then(applyBootstrap).catch((error: unknown) => setStatus(new Status({ ...emptyStatus, state: ModelState.ModelError, message: errorText(error) })))
    const offStatus = Events.On('model:status', (event) => setStatus(Status.createFrom(event.data)))
    const offAgent = Events.On('agent:event', (event) => {
      const data = event.data as AgentActivity
      if (data.kind === 'answer_delta' || data.kind === 'answer_reset') {
        // 子 Agent 的回答只是它交回主 Agent 的中间结果，不显示在对话里。
        if (data.subagentIndex) return
        liveAnswerRef.current = data.kind === 'answer_reset' ? '' : liveAnswerRef.current + (data.text || '')
        setLiveAnswer(liveAnswerRef.current)
        return
      }
      setActivity((current) => [...current, { ...data, at: Date.now() }])
    })
    return () => { offStatus(); offAgent() }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
  useEffect(() => { if (followBottom.current) messagesEnd.current?.scrollIntoView({ block: 'end' }) }, [messages, liveAnswer])

  // 快捷键监听只挂一次，经 ref 调最新一轮渲染的处理函数：过去依赖 [busy] 的闭包会拿着
  // 空的档案列表打开设置（首轮对话前按 ⌘, 总是落到"新建连接"）。
  const shortcutRef = useRef<(event: globalThis.KeyboardEvent) => void>(() => {})
  shortcutRef.current = (event) => {
    const mod = event.metaKey || event.ctrlKey
      if (!mod) return
    if (event.key.toLowerCase() === 'n') {
      event.preventDefault()
      void newConversation()
    } else if (event.key === ',') {
      event.preventDefault()
      setRunConfigOpen(false)
      if (!settingsOpen) manager.openSettings()
    } else if (event.key.toLowerCase() === 'k') {
      event.preventDefault()
      document.querySelector<HTMLTextAreaElement>('textarea[aria-label="消息"]')?.focus()
    }
  }
  useEffect(() => {
    const onKeyDown = (event: globalThis.KeyboardEvent) => shortcutRef.current(event)
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [])

  const workspaceName = useMemo(() => status.workspace ? status.workspace.split(/[\\/]/).filter(Boolean).at(-1) || status.workspace : '未打开工作区', [status.workspace])
  // 运行标签（能力、State）的单一事实源：当前运行中档案的已保存配置，而非正在编辑的草稿。
  // 取实际运行的配置（bootstrap.config）：本地档案改了参数但未重新加载时，档案的
  // 已保存值并不是正在生效的值。
  const runtimeConfig = manager.runtimeConfig

  function handleToggleTheme() {
    setTheme((current) => toggleTheme(current))
  }

  function applyBootstrap(value: AppBootstrap, options: { preserveDraft?: boolean } = {}) {
    setStatus(Status.createFrom(value.status)); setConversations(value.conversations || []); setWorkspaces(value.workspaces || [])
    manager.applyProviderBootstrapState(value)
    applyConversation(value.conversation || undefined, options); if (value.hasConfig && !settingsOpen) manager.applyConfig(value.config); if (value.warning) notify(value.warning, 'error')
  }
  async function activateProviderNow(id: string) {
    if (busy) return
    setRunConfigOpen(false); setBusy(true)
    try { await manager.activateProvider(id) } catch (error) { if (settingsOpen) manager.setSettingsMessage(errorText(error)); else reportError(error) } finally { setBusy(false) }
  }
  async function toggleCapabilityNow(key: 'enableWeb' | 'enableSubagents', value: boolean) {
    if (busy) return
    setBusy(true)
    try { await manager.setRuntimeCapability(key, value) } catch (error) { reportError(error) } finally { setBusy(false) }
  }
  // 导出当前会话所有轮次的原始 trace，每行一轮（JSONL）。
  async function exportTrajectory() {
    const data = messages.filter((message) => message.role !== 'user' && (message.trace || message.trajectory?.length)).map((message) => JSON.stringify({
      id: message.id, role: message.role, prompt: message.prompt, createdAt: message.createdAt,
      trace: message.trace || { legacyTrajectory: message.trajectory },
    })).join('\n')
    try {
      const path = await Backend.ExportTrajectory(data)
      if (path) notify(`轨迹已导出：${path.split('/').at(-1)}`, 'success')
    } catch (error) { reportError(error) }
  }
  async function setStateNow(stateId: string) {
    if (busy) return
    setBusy(true)
    try { await manager.setRuntimeState(stateId) } catch (error) { reportError(error); throw error } finally { setBusy(false) }
  }
  async function deleteProviderNow(id: string) {
    if (busy) return
    setBusy(true)
    try { await manager.deleteProvider(id) } catch (error) { manager.setSettingsMessage(errorText(error)) } finally { setBusy(false) }
  }
  function applyConversation(value?: ConversationView, options: { preserveDraft?: boolean } = {}) {
    setActiveConversationID(value?.id || ''); setActiveTab('chat'); setActivity([]); followBottom.current = true; if (!options.preserveDraft) setPrompt('')
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
  function ensureReady() {
    if (ready) return true
    manager.openSettings(); manager.setSettingsMessage('请先选择一个已保存连接，或新建草稿后点击“保存并使用”。')
    return false
  }
  async function sendMessage(value: string) {
    const content = value.trim(); if (!content || busy || turnInFlight.current || !ensureReady()) return
    setPrompt('')
    await runTurn(content, (current) => [...current, userMessage(content)], () => Backend.Chat(content), true)
  }
  // 原地重新生成：撤掉最后一轮的回复，由后端回退历史后用同一条用户消息重跑，而不是追加一条重复消息。
  async function regenerateLast() {
    if (busy || turnInFlight.current) return
    const lastUser = [...messages].reverse().find((message) => message.role === 'user')
    const content = lastUser?.content
    if (!content || !ensureReady()) return
    // 同一条用户消息重跑：上一版回答的放字进度不能带给新回答。
    motionMemory.current.progress.delete(`turn:${lastUser.id}`)
    await runTurn(content, (current) => current.at(-1)?.role === 'user' ? current : current.slice(0, -1), () => Backend.Regenerate(), false)
  }
  // 编辑最近一轮：撤掉最后一条用户消息及其回复，由后端回退历史后用改过的内容重跑。
  async function editLast(value: string) {
    const content = value.trim()
    if (!content || busy || turnInFlight.current || !ensureReady()) return
    const lastUserIndex = messages.findLastIndex((message) => message.role === 'user')
    if (lastUserIndex < 0) return
    motionMemory.current.progress.delete(`turn:${messages[lastUserIndex].id}`)
    await runTurn(content, (current) => [...current.slice(0, current.findLastIndex((message) => message.role === 'user')), userMessage(content)], () => Backend.EditLast(content), true)
  }
  async function runTurn(content: string, stage: (current: Message[]) => Message[], run: () => Promise<Result> & { cancel: () => void }, restoreUser: boolean) {
    turnInFlight.current = true
    followBottom.current = true
    setActivity([]); setMessages(stage); setBusy(true)
    liveAnswerRef.current = ''; setLiveAnswer('')
    try {
      const call = run()
      runningChat.current = call
      const result = await call
      const assistant: Message = { id: `pending-${nextMessageID++}`, role: 'assistant', content: result.output, prompt: content, trace: result, createdAt: new Date().toISOString(), meta: [`${result.steps.length} 步 · ${(result.durationMs / 1000).toFixed(1)} 秒`, status.model?.split(/[\\/]/).at(-1), status.stateId].filter(Boolean).join(' · '), trajectory: legacyTrajectory(result.steps), streamed: liveAnswerRef.current !== '' }
      setMessages((current) => [...current, assistant]); setSelectedTraceID(assistant.id)
      const persisted = await Backend.Bootstrap(); setConversations(persisted.conversations || []); setActiveConversationID(persisted.conversation?.id || '')
    } catch (error) {
      try {
        const persisted = await Backend.Bootstrap()
        // 停止或失败后重载历史，保留运行期间输入的下一条草稿。
        applyBootstrap(persisted, { preserveDraft: true })
        setSelectedTraceID('')
        // 会话建立前就失败（如连接配置错误）时后端不落盘，重载会吞掉这一轮和报错，这里补回。
        const persistedMessages = persisted.conversation?.messages || []
        const persistedThisTurn = persistedMessages.at(-1)?.role === 'error' && persistedMessages.at(-2)?.content === content
        if (!persistedThisTurn) {
          setMessages((current) => [...current,
            ...(restoreUser ? [userMessage(content)] : []),
            { id: `error-${nextMessageID++}`, role: 'error', content: errorText(error) }])
        }
      } catch {
        setMessages((current) => [...current, { id: `error-${nextMessageID++}`, role: 'error', content: errorText(error) }])
      }
    }
    finally { runningChat.current = null; turnInFlight.current = false; setBusy(false); liveAnswerRef.current = ''; setLiveAnswer('') }
  }
  function stopRun() { runningChat.current?.cancel() }
  function submitMessage() { void sendMessage(prompt) }
  function onComposerKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    // 输入法组字中的回车是确认候选词，不是发送（WebKit 组字时 keyCode 为 229）。
    if (event.nativeEvent.isComposing || event.keyCode === 229 || busy) return
    if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); void sendMessage(prompt) } }
  async function newConversation() { if (busy) return; await Backend.NewConversation(); setMessages([]); setActivity([]); setPrompt(''); setActiveConversationID(''); setActiveTab('chat') }
  async function openConversation(id: string) { if (busy || id === activeConversationID) return; setBusy(true); try { applyConversation(await Backend.OpenConversation(id)) } catch (error) { reportError(error) } finally { setBusy(false) } }
  async function deleteConversation(id: string) { if (busy) return; setBusy(true); try { await Backend.DeleteConversation(id); if (id === activeConversationID) applyConversation(); const persisted = await Backend.Bootstrap(); setConversations(persisted.conversations || []) } catch (error) { reportError(error) } finally { setBusy(false) } }
  async function chooseWorkspace() { if (busy) return; setBusy(true); try { applyBootstrap(await Backend.ChooseWorkspace()) } catch (error) { if (!errorText(error).toLowerCase().includes('cancel')) { if (settingsOpen) manager.setSettingsMessage(errorText(error)); else reportError(error) } } finally { setBusy(false) } }
  async function openWorkspace(path: string) { if (busy) return; setBusy(true); try { applyBootstrap(await Backend.OpenWorkspace(path)) } catch (error) { reportError(error) } finally { setBusy(false) } }
  async function renameConversation(id: string, title: string) {
    try { await Backend.RenameConversation(id, title); const persisted = await Backend.Bootstrap(); setConversations(persisted.conversations || []) } catch (error) { reportError(error) }
  }
  async function togglePinConversation(id: string, pinned: boolean) {
    try { await Backend.SetConversationPinned(id, pinned); const persisted = await Backend.Bootstrap(); setConversations(persisted.conversations || []) } catch (error) { reportError(error) }
  }

  const traceMessages = messages.filter((message) => message.role !== 'user' && (message.trace || message.trajectory?.length))
  // 运行中的一轮：最后一条用户消息还没有回答时，用实时事件拼出它的轨迹。
  const pendingUser = busy && messages.at(-1)?.role === 'user' ? messages.at(-1) : undefined
  const liveTurn = useMemo<LiveTurn | null>(() => pendingUser
    ? { id: pendingUser.id, prompt: pendingUser.content, startedAt: new Date(pendingUser.createdAt || Date.now()).getTime(), events: activity }
    : null, [pendingUser, activity])

  return <div className="flex h-full w-full bg-paper">
    {settingsOpen ? <SettingsPage manager={manager} status={status} ready={ready} onChooseWorkspace={chooseWorkspace} theme={theme} onToggleTheme={handleToggleTheme} onActivateProvider={(id) => void activateProviderNow(id)} onDeleteProvider={(id) => void deleteProviderNow(id)} /> : <>
      <Sidebar conversations={conversations} workspaces={workspaces} activeId={activeConversationID} busy={busy} open={sidebarOpen} onCloseSidebar={() => setSidebarOpen(false)} onNewChat={() => { setSidebarOpen(false); void newConversation() }} onChooseWorkspace={() => void chooseWorkspace()} onOpenSettings={() => { setSidebarOpen(false); manager.openSettings() }} onOpen={(id) => { setSidebarOpen(false); void openConversation(id) }} onDelete={deleteConversation} onRename={renameConversation} onTogglePin={togglePinConversation} onOpenWorkspace={openWorkspace} />
      <main className="flex min-w-0 flex-1 flex-col bg-paper">
        <header className="app-header [--wails-draggable:drag] [&_button]:[--wails-draggable:no-drag] wails-mac:pt-[22px] wails-mac:h-[74px] wails-mac:basis-[74px] relative flex h-(--header-h) flex-none items-end gap-[18px] border-b border-line px-[30px]">
          <button className="sidebar-toggle relative mr-[-6px] grid h-8 w-8 flex-none place-items-center border-0 bg-transparent text-ink-soft before:absolute before:inset-[-6px] before:content-[''] lg:hidden" aria-label="打开导航" onClick={() => setSidebarOpen(true)}><Menu size={18} /></button>
          <div className="flex h-9 flex-none items-end gap-[22px]" role="tablist">
            <button role="tab" aria-selected={activeTab === 'chat'} className={`relative border-0 border-b-2 bg-transparent pb-[9px] text-md transition-[border-color,color] duration-[180ms] ease-[cubic-bezier(.2,0,0,1)] motion-reduce:transition-none before:absolute before:inset-x-0 before:bottom-0 before:top-[-15px] before:content-[''] ${activeTab === 'chat' ? 'border-brand font-semibold text-ink' : 'border-transparent text-ink-muted'}`} onClick={() => setActiveTab('chat')}>对话</button>
            <button role="tab" aria-selected={activeTab === 'trace'} className={`relative min-w-[58px] border-0 border-b-2 bg-transparent pb-[9px] text-center text-md transition-[border-color,color] duration-[180ms] ease-[cubic-bezier(.2,0,0,1)] motion-reduce:transition-none before:absolute before:inset-x-0 before:bottom-0 before:top-[-15px] before:content-[''] ${activeTab === 'trace' ? 'border-brand font-semibold text-ink' : 'border-transparent text-ink-muted'}`} onClick={() => setActiveTab('trace')} disabled={!traceMessages.length && !liveTurn}>轨迹 <span className="ml-1 font-mono text-2xs text-ink-muted">{traceMessages.length + (liveTurn ? 1 : 0) || ''}</span></button>
          </div>
        </header>
        {activeTab === 'trace' ? <TrajectoryView messages={traceMessages} live={liveTurn} focusMessageId={selectedTraceID} onExport={() => void exportTrajectory()} /> : <ChatView chips={<RunChips ready={ready} busy={busy} status={status} runtimeConfig={runtimeConfig} providers={manager.providers} runtimeProviderId={manager.runtimeProviderId} workspace={workspaceName} runConfigOpen={runConfigOpen} setRunConfigOpen={setRunConfigOpen} onActivate={(id) => void activateProviderNow(id)} onToggleCapability={(key, value) => void toggleCapabilityNow(key, value)} onSetState={setStateNow} onChooseWorkspace={() => void chooseWorkspace()} onOpenSettings={() => { setRunConfigOpen(false); manager.openSettings() }} />} messages={messages} activity={activity} liveAnswer={liveAnswer} motion={motionMemory.current} busy={busy} prompt={prompt} setPrompt={setPrompt} onSubmit={submitMessage} onRegenerate={() => void regenerateLast()} onEditLast={(content) => void editLast(content)} onKeyDown={onComposerKeyDown} onStop={stopRun} onTrace={(id) => { setSelectedTraceID(id); setActiveTab('trace') }} messagesEnd={messagesEnd} followBottom={followBottom} />}
      </main>
    </>}
  </div>
}

function Sidebar({ conversations, workspaces, activeId, busy, open, onCloseSidebar, onNewChat, onChooseWorkspace, onOpenSettings, onOpen, onDelete, onRename, onTogglePin, onOpenWorkspace }: { conversations: ConversationSummary[]; workspaces: WorkspaceItem[]; activeId: string; busy: boolean; open: boolean; onCloseSidebar: () => void; onNewChat: () => void; onChooseWorkspace: () => void; onOpenSettings: () => void; onOpen: (id: string) => void; onDelete: (id: string) => void; onRename: (id: string, title: string) => Promise<void>; onTogglePin: (id: string, pinned: boolean) => Promise<void>; onOpenWorkspace: (path: string) => void }) {
  const [menu, setMenu] = useState<{ id: string; up: boolean } | null>(null)
  const [renaming, setRenaming] = useState<string | null>(null)
  const [renameValue, setRenameValue] = useState('')
  const [deleteTarget, setDeleteTarget] = useState<ConversationSummary | null>(null)
  const sidebarRef = useRef<HTMLElement>(null)

  // 点击侧栏空白处或按 Esc 时收起会话菜单/重命名（HIG：菜单可经外部交互关闭）。
  useEffect(() => {
    if (!menu && !renaming) return
    function onPointerDown(event: PointerEvent) {
      // 「…」按钮自己负责开合（toggleMenu）；这里也关的话，按下关、松开又开，菜单会闪一下又弹出来。
      if (event.target instanceof Element && event.target.closest('[data-conversation-menu],.conversation-menu,input[aria-label="重命名会话"]')) return
      setMenu(null); setRenaming(null)
    }
    function onKeyDown(event: globalThis.KeyboardEvent) {
      if (event.key === 'Escape') { setMenu(null); setRenaming(null) }
    }
    document.addEventListener('pointerdown', onPointerDown)
    document.addEventListener('keydown', onKeyDown)
    return () => { document.removeEventListener('pointerdown', onPointerDown); document.removeEventListener('keydown', onKeyDown) }
  }, [menu, renaming])

  // 列表视口下方放不下菜单（约 128px 高）时向上弹出，避免末行菜单被裁剪。
  function toggleMenu(id: string, event: React.MouseEvent<HTMLButtonElement>) {
    if (menu?.id === id) { setMenu(null); return }
    let up = false
    const list = event.currentTarget.closest('section')
    if (list) {
      const listRect = list.getBoundingClientRect()
      const buttonRect = event.currentTarget.getBoundingClientRect()
      up = listRect.bottom - buttonRect.bottom < 132
    }
    setMenu({ id, up })
  }
  function startRename(conversation: ConversationSummary) {
    setMenu(null); setRenaming(conversation.id); setRenameValue(conversation.title || '')
  }
  function commitRename(id: string) {
    const title = renameValue.trim()
    setRenaming(null)
    if (title) void onRename(id, title)
  }
  return <>
    {open && <div className="sidebar-scrim fixed inset-0 z-[40] bg-overlay lg:hidden" onClick={onCloseSidebar} />}
    <aside ref={sidebarRef} data-open={open} className={`app-sidebar compact:w-[196px] compact:basis-[196px] max-lg:data-[open=true]:shadow-[0_12px_40px_rgba(60,50,35,.2)] [--wails-draggable:drag] [&_button]:[--wails-draggable:no-drag] [&_input]:[--wails-draggable:no-drag] wails-mac:pt-[44px] fixed inset-y-0 left-0 z-[50] flex h-full w-(--sidebar-w) flex-none flex-col border-r border-line bg-paper-sidebar py-[18px] text-ink transition-transform duration-200 motion-reduce:transition-none lg:static lg:translate-x-0 ${open ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
      <div className="flex items-center gap-[9px] px-[18px] pb-[18px] text-md font-semibold"><Wordmark /><span className="ml-auto font-mono text-2xs font-medium leading-none text-ink-muted">⌘K</span></div>
      <button className="mx-[18px] mb-[14px] flex h-8 items-center justify-center gap-2 rounded-md border border-line bg-paper-wash px-[10px] text-sm font-medium text-ink shadow-hair transition-colors hover:bg-surface-active" onClick={onNewChat} disabled={busy}><SquarePen size={16} />新的对话 <kbd className="ml-[2px] font-mono text-2xs text-ink-muted">⌘N</kbd></button>
      <button className="mx-[10px] mb-3 flex items-center gap-2 rounded-md border-0 bg-transparent p-[6px_8px] text-sm text-ink-soft transition-colors hover:bg-surface-active hover:text-ink" onClick={onChooseWorkspace} disabled={busy}><FolderOpen size={16} /><span>打开工作区</span><MoreHorizontal size={15} className="ml-auto" /></button>
      {workspaces.length > 0 && <section className="mb-[6px] flex flex-col"><div className="px-[18px] pb-[7px] text-2xs font-medium text-ink-muted">工作区</div>{workspaces.map((workspace) => (
        <button key={workspace.path} className={`relative mx-[10px] flex items-center gap-[9px] rounded-md border-0 bg-transparent p-[6px_8px] text-left text-sm transition-colors ${workspace.active ? 'bg-surface-active font-medium text-ink' : 'text-ink-soft hover:bg-surface-active hover:text-ink'}`} onClick={() => onOpenWorkspace(workspace.path)} disabled={!workspace.available || busy} title={workspace.path}><Folder size={14} /><span className="truncate">{workspace.name}</span>{workspace.active && <span className="ml-auto h-[5px] w-[5px] rounded-full bg-brand-bright" />}</button>
      ))}</section>}
      <section className="min-h-0 flex-1 overflow-y-auto"><div className="px-[18px] pb-[7px] text-2xs font-medium text-ink-muted">近期</div>
        {conversations.length === 0 ? <div className="px-[18px] py-2 text-sm text-ink-muted">暂无历史对话</div> : conversations.map((conversation) => (
          <div key={conversation.id} data-active={conversation.id === activeId} className={`conversation-row group/conversation relative mx-[10px] flex items-center rounded-md border-0 bg-transparent transition-colors ${conversation.id === activeId ? 'active bg-surface-active text-ink' : 'text-ink-soft hover:bg-surface-active hover:text-ink'}`}>
            {renaming === conversation.id ? <div className="flex min-w-0 flex-1 p-[5px_8px]"><input autoFocus aria-label="重命名会话" className="min-w-0 flex-1 rounded-md border border-line-strong bg-paper px-[7px] py-[4px] text-sm text-ink outline-none focus:border-brand" value={renameValue} onChange={(event) => setRenameValue(event.target.value)} onBlur={() => commitRename(conversation.id)} onKeyDown={(event) => { if (event.key === 'Enter') commitRename(conversation.id); if (event.key === 'Escape') setRenaming(null) }} /></div> : <button className="flex min-w-0 flex-1 flex-col gap-[1px] border-0 bg-transparent p-[7px_8px] text-left text-inherit" onClick={() => onOpen(conversation.id)} title={conversation.title || '未命名会话'}><span className="flex min-w-0 items-center gap-[5px] text-sm">{conversation.pinned && <Pin size={11} className="flex-none text-brand" aria-label="已置顶" />}<span className="min-w-0 truncate">{conversation.title || '未命名会话'}</span></span><span className="text-2xs text-ink-muted">{relativeTime(conversation.updatedAt)}</span></button>}
            <button className="conversation-menu invisible group-hover/conversation:visible group-focus-within/conversation:visible group-data-[active=true]/conversation:visible grid h-[26px] w-[26px] place-items-center border-0 bg-transparent text-ink-muted" aria-label={`会话“${conversation.title || '未命名会话'}”的更多操作`} aria-haspopup="menu" aria-expanded={menu?.id === conversation.id} onClick={(event) => toggleMenu(conversation.id, event)}><MoreHorizontal size={15} /></button>
            {menu?.id === conversation.id && (
              <div data-conversation-menu className={`absolute right-2 z-[5] flex min-w-[128px] flex-col rounded-lg border border-line bg-paper-wash p-1 shadow-pop ${menu.up ? 'bottom-[30px]' : 'top-[30px]'}`} role="menu" aria-label="会话操作">
                <button role="menuitem" className="flex items-center gap-[7px] rounded-sm border-0 bg-transparent px-[8px] py-[6px] text-left text-sm text-ink hover:bg-surface-active" onClick={() => { setMenu(null); void onTogglePin(conversation.id, !conversation.pinned) }}><Pin size={14} />{conversation.pinned ? '取消置顶' : '置顶'}</button>
                <button role="menuitem" className="flex items-center gap-[7px] rounded-sm border-0 bg-transparent px-[8px] py-[6px] text-left text-sm text-ink hover:bg-surface-active" onClick={() => startRename(conversation)}><PenLine size={14} />重命名</button>
                <button role="menuitem" className="flex items-center gap-[7px] rounded-sm border-0 bg-transparent px-[8px] py-[6px] text-left text-sm text-danger hover:bg-surface-active" onClick={() => { setMenu(null); setDeleteTarget(conversation) }}><Trash2 size={14} />删除会话</button>
              </div>
            )}
          </div>
        ))}
      </section>
      <ConfirmDialog open={deleteTarget !== null} title="删除会话" body={deleteTarget ? `将删除“${deleteTarget.title || '未命名会话'}”及其全部消息，此操作无法撤销。` : ''} onClose={() => setDeleteTarget(null)} actions={[{ label: '取消', onClick: () => setDeleteTarget(null) }, { label: '删除', variant: 'danger', onClick: () => { const target = deleteTarget; setDeleteTarget(null); if (target) onDelete(target.id) } }]} />
      <button className="mt-3 flex items-center gap-[9px] border-0 border-t border-line bg-transparent px-[18px] pb-0 pt-3 text-left text-sm text-ink-soft" onClick={onOpenSettings} aria-label="设置"><Settings size={16} /><span className="flex-1">设置</span><kbd className="ml-[2px] font-mono text-2xs text-ink-muted">⌘,</kbd></button>
    </aside>
  </>
}

function ChatView({ chips, messages, activity, liveAnswer, motion, busy, prompt, setPrompt, onSubmit, onStop, onRegenerate, onEditLast, onKeyDown, onTrace, messagesEnd, followBottom }: { chips: React.ReactNode; messages: Message[]; activity: AgentActivity[]; liveAnswer: string; motion: MotionMemory; busy: boolean; prompt: string; setPrompt: (value: string) => void; onSubmit: () => void; onStop: () => void; onRegenerate: () => void; onEditLast: (content: string) => void; onKeyDown: (event: KeyboardEvent<HTMLTextAreaElement>) => void; onTrace: (id: string) => void; messagesEnd: React.RefObject<HTMLDivElement | null>; followBottom: React.RefObject<boolean> }) {
  const turns = groupMessagesIntoTurns(messages)
  const empty = turns.length === 0
  // 匀速显示会比消息到达晚一点长高，滚动要跟着显示层走，而不只是跟着消息。
  const followAnswer = useCallback(() => { if (followBottom.current) messagesEnd.current?.scrollIntoView({ block: 'end' }) }, [messagesEnd, followBottom])
  // busy 也覆盖打开会话等短操作；只有最后一轮在等回答才算 Agent 运行中。
  const running = busy && !empty && !turns[turns.length - 1].response
  const stageRef = useRef<HTMLDivElement>(null)
  const scrollRef = useRef<HTMLDivElement>(null)
  const anchorRef = useRef<HTMLDivElement>(null)
  // 程序滚动只会往下（贴底），所以 scrollTop 变小就是用户在往上看：松开跟随。
  useEffect(() => {
    const scroller = scrollRef.current
    if (!scroller) return
    let lastTop = scroller.scrollTop
    const onScroll = () => {
      const top = scroller.scrollTop
      const distance = scroller.scrollHeight - top - scroller.clientHeight
      if (top < lastTop - 2) followBottom.current = false
      else if (distance < 48) followBottom.current = true
      lastTop = top
    }
    scroller.addEventListener('scroll', onScroll, { passive: true })
    return () => scroller.removeEventListener('scroll', onScroll)
  }, [empty, followBottom])
  const metrics = useRef({ dockedTop: 0, offset: 0 })
  const settled = useRef(false)
  const emptyRef = useRef(empty)
  emptyRef.current = empty

  // 输入框是同一元素，仅用 transform 位移（不改 top，避免逐帧重排抽搐）。
  const measure = useCallback(() => {
    const stage = stageRef.current, anchor = anchorRef.current
    if (!stage || !anchor) return
    const stageHeight = stage.clientHeight
    const anchorHeight = anchor.offsetHeight
    const dockedTop = Math.max(0, stageHeight - anchorHeight - 28)
    const centeredTop = Math.max(24, Math.round((stageHeight - anchorHeight) / 2))
    metrics.current = { dockedTop, offset: centeredTop - dockedTop }
  }, [])
  const place = useCallback((animate: boolean) => {
    const anchor = anchorRef.current
    if (!anchor) return
    anchor.style.transition = animate ? '' : 'none' // animate: 交回 CSS 类过渡；否则临时禁用
    anchor.style.top = `${metrics.current.dockedTop}px`
    anchor.style.transform = emptyRef.current ? `translateY(${metrics.current.offset}px)` : 'translateY(0)'
    if (scrollRef.current) scrollRef.current.style.paddingBottom = `${anchor.offsetHeight + 40}px`
    if (!animate) {
      void anchor.offsetHeight // 强制回流锁定当前位置，再于下一帧恢复过渡
      requestAnimationFrame(() => { if (anchorRef.current) anchorRef.current.style.transition = '' })
    }
  }, [])

  // 空态↔对话态切换：仅此处触发滑动（首次挂载不动画）。
  useLayoutEffect(() => {
    measure()
    place(settled.current)
    settled.current = true
  }, [empty, measure, place])

  // 尺寸变化（窗口/输入框伸长）：即时重排，不触发滑动动画。独立挂载一次，避免切换时误重建打断过渡。
  useLayoutEffect(() => {
    const stage = stageRef.current, anchor = anchorRef.current
    if (!stage || !anchor || typeof ResizeObserver === 'undefined') return
    const observer = new ResizeObserver(() => { measure(); place(false) })
    observer.observe(stage)
    observer.observe(anchor)
    return () => observer.disconnect()
  }, [measure, place])

  return <div className="chat-panel relative flex min-h-0 flex-1 flex-col overflow-hidden">
    <div ref={stageRef} className="chat-stage relative min-h-0 flex-1 overflow-hidden">
      {!empty && <div ref={scrollRef} className="conversation-scroll absolute inset-0 mx-auto content-narrow overflow-auto pt-[30px]">
        {turns.map((turn, index) => <TurnView key={turn.user?.id || turn.response?.id || index} turn={turn} index={index + 1} last={index === turns.length - 1} busy={busy} pending={busy && index === turns.length - 1 && !turn.response} activity={activity} liveAnswer={liveAnswer} motion={motion} onGrow={followAnswer} onTrace={onTrace} onRegenerate={onRegenerate} onEditLast={onEditLast} />)}
        <div ref={messagesEnd} />
      </div>}
    </div>
    <div ref={anchorRef} className="composer-anchor absolute left-0 right-0 z-[2] mx-auto content-narrow will-change-transform transition-transform duration-[420ms] ease-[cubic-bezier(.2,0,0,1)] motion-reduce:transition-none">
      {/* 渐隐底衬：正文滚到输入区时先淡出、再被纸色盖住，不从标签和输入框之间直接穿过去。
          延伸到舞台底边（锚点下方留的 28px）；空态输入框居中，没有正文要盖。 */}
      {!empty && <div aria-hidden className="composer-fade pointer-events-none absolute inset-x-0 top-[-56px] bottom-[-28px] -z-10 bg-[linear-gradient(to_bottom,transparent,var(--paper)_56px)]" />}
      <Composer chips={chips} prompt={prompt} setPrompt={setPrompt} busy={busy} running={running} empty={empty} onSubmit={onSubmit} onStop={onStop} onKeyDown={onKeyDown} />
    </div>
  </div>
}

function TurnView({ turn, index, last, busy, pending, activity, liveAnswer, motion, onGrow, onTrace, onRegenerate, onEditLast }: { turn: ChatTurn; index: number; last: boolean; busy: boolean; pending: boolean; activity: AgentActivity[]; liveAnswer: string; motion: MotionMemory; onGrow: () => void; onTrace: (id: string) => void; onRegenerate: () => void; onEditLast: (content: string) => void }) {
  const response = turn.response
  const hasTrace = Boolean(response?.trace || response?.trajectory?.length)
  const calls = pending ? callsFromEvents(activity) : response?.trace ? callsFromSteps(response.trace.steps) : callsFromTrajectory(response?.trajectory || [])
  const lastEvent = activity.at(-1)
  // 运行中摘要行：正在调用工具时显示最新那次调用，其余阶段（决策、路由、子 Agent）沿用活动文字。
  const liveLabel = lastEvent && !lastEvent.subagentIndex && lastEvent.kind.startsWith('tool_') && lastEvent.kind !== 'tool_done' ? undefined : activityLabel(lastEvent)
  const stats = response?.trace ? traceStats(response.trace) : undefined
  const time = turn.user?.createdAt || response?.createdAt
  const streamText = pending ? liveAnswer : response?.role === 'assistant' && response.streamed ? response.content : ''
  // 每个回合、每条回答的入场动画只在第一次挂载时播放：切页回来、重新挂载不再重播。
  const turnKey = `turn:${turn.user?.id || response?.id || index}`
  const answerKey = response ? `answer:${response.id}` : ''
  const [enterFresh] = useState(() => !motion.seen.has(turnKey))
  const answerFresh = useRef<boolean | null>(null)
  if (answerKey && answerFresh.current === null) answerFresh.current = !motion.seen.has(answerKey)
  useEffect(() => { motion.seen.add(turnKey) }, [motion, turnKey])
  useEffect(() => { if (answerKey) motion.seen.add(answerKey) }, [motion, answerKey])
  // 入场动效只给最后一轮：新发出的回合，或刚打开会话时的最末一轮；历史回合不整片闪动。
  return <article className={`mb-[42px] conversation-turn${pending ? ' pending' : ''}${last && enterFresh ? ' turn-enter animate-turn-enter motion-reduce:animate-none' : ''}`} data-testid={`conversation-turn-${index}`}>
    <div className="turn-main flex min-w-0 flex-col gap-4">
      {turn.user && <UserMessage content={turn.user.content} canEdit={last} busy={busy} onEdit={onEditLast} />}
      {calls.length > 0 && <ToolActivity calls={calls} running={pending && !liveAnswer} liveLabel={liveLabel} />}
      {pending && !liveAnswer && calls.length === 0 && <div className="turn-pending-answer flex min-h-7 items-center gap-[6px] pt-[2px] text-ink-muted" aria-live="polite"><ThinkingMark /><span className="shimmer-text text-sm">{activityLabel(activity.at(-1))}</span></div>}
      {/* 流式回答：生成中与落定后必须是同一位置的同一个 PacedAnswer，落定时它才能把没放完的字按节奏放完。 */}
      {streamText
        ? <div className="turn-answer answer-streaming text-md leading-[1.8] text-ink [overflow-wrap:anywhere]" aria-busy={pending}><PacedAnswer text={streamText} live={pending} onGrow={onGrow} initialShown={motion.progress.get(turnKey)} onProgress={(shown) => motion.progress.set(turnKey, shown)} /></div>
        : response?.role === 'assistant' && <div className={`turn-answer${last && answerFresh.current ? ' answer-reveal animate-answer-reveal motion-reduce:animate-none' : ''} text-md leading-[1.8] text-ink [overflow-wrap:anywhere]`}><MarkdownMessage content={response.content} /></div>}
      {response?.role === 'error' && <div className="flex items-start gap-2 rounded-lg border border-danger/30 bg-danger-wash p-[10px_12px] text-sm leading-[1.65] text-danger"><X size={15} className="mt-[3px] flex-none" /><span className="min-w-0 whitespace-pre-wrap [overflow-wrap:anywhere]">{response.content}</span></div>}
      {response && <TurnActions response={response} meta={[formatTurnTime(time), response.meta, stats && stats.tokens > 0 ? `${stats.tokens.toLocaleString('zh-CN')} tok` : ''].filter(Boolean).join(' · ')} canRegenerate={last && Boolean(turn.user)} busy={busy} hasTrace={hasTrace} onRegenerate={onRegenerate} onTrace={() => onTrace(response.id)} />}
    </div>
  </article>
}

// 用户消息：悬停出复制/编辑。只有最后一轮可编辑——更早的回合改了会让后续回合失去依据（与重新生成同理）。
function UserMessage({ content, canEdit, busy, onEdit }: { content: string; canEdit: boolean; busy: boolean; onEdit: (content: string) => void }) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(content)
  const [copied, setCopied] = useState(false)
  useEffect(() => { if (!copied) return; const timer = setTimeout(() => setCopied(false), 1500); return () => clearTimeout(timer) }, [copied])
  const changed = draft.trim() !== '' && draft.trim() !== content.trim()
  function submit() { if (!changed || busy) return; setEditing(false); onEdit(draft) }
  function cancel() { setEditing(false); setDraft(content) }
  if (editing) {
    return <div className="user-edit flex flex-col gap-2 rounded-xl border border-line bg-paper-wash p-[10px_12px]">
      <textarea
        aria-label="编辑消息"
        autoFocus
        rows={Math.min(8, Math.max(2, draft.split('\n').length))}
        className="w-full resize-none border-0 bg-transparent text-base leading-[1.7] text-ink outline-0"
        value={draft}
        onChange={(event) => setDraft(event.target.value)}
        onFocus={(event) => event.currentTarget.setSelectionRange(event.currentTarget.value.length, event.currentTarget.value.length)}
        onKeyDown={(event) => {
          if (event.nativeEvent.isComposing || event.keyCode === 229) return
          if (event.key === 'Escape') { event.preventDefault(); cancel() }
          if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); submit() }
        }}
      />
      <div className="flex justify-end gap-2">
        <button type="button" onClick={cancel} className="rounded-md px-3 py-1 text-sm text-ink-muted hover:bg-surface-active hover:text-ink">取消</button>
        <button type="button" aria-label="发送修改" onClick={submit} disabled={!changed || busy} className="rounded-md bg-ink px-3 py-1 text-sm text-paper disabled:opacity-40">发送</button>
      </div>
    </div>
  }
  return <div className="group/user flex flex-col items-end gap-1">
    <div className="max-w-[82%] whitespace-pre-wrap rounded-xl bg-user-bg p-[10px_14px] text-base leading-[1.7] text-user-text [overflow-wrap:anywhere]">{content}</div>
    <div className="flex items-center gap-[2px] opacity-0 transition-opacity duration-[120ms] focus-within:opacity-100 group-hover/user:opacity-100">
      <IconButton label={copied ? '已复制' : '复制'} onClick={() => { void navigator.clipboard?.writeText(content); setCopied(true) }}>{copied ? <Check size={15} /> : <Copy size={15} />}</IconButton>
      {canEdit && <IconButton label="编辑" disabled={busy} onClick={() => { setDraft(content); setEditing(true) }}><PenLine size={15} /></IconButton>}
    </div>
  </div>
}

// 回答下方的操作栏：图标按钮（悬停出提示）+ 右侧一行运行信息。
function TurnActions({ response, meta, canRegenerate, busy, hasTrace, onRegenerate, onTrace }: { response: Message; meta: string; canRegenerate: boolean; busy: boolean; hasTrace: boolean; onRegenerate: () => void; onTrace: () => void }) {
  const [copied, setCopied] = useState(false)
  useEffect(() => { if (!copied) return; const timer = setTimeout(() => setCopied(false), 1500); return () => clearTimeout(timer) }, [copied])
  const regenerateLabel = response.role === 'error' ? '重试' : '重新生成'
  return <div className="turn-actions -ml-[6px] flex items-center gap-[2px]">
    {response.role === 'assistant' && <IconButton label={copied ? '已复制' : '复制'} onClick={() => { void navigator.clipboard?.writeText(response.content); setCopied(true) }}>{copied ? <Check size={15} /> : <Copy size={15} />}</IconButton>}
    {/* 只有最后一轮能原地重跑；更早的回合重跑会让后续回合失去依据。 */}
    {canRegenerate && <IconButton label={regenerateLabel} disabled={busy} onClick={onRegenerate}><RotateCcw size={15} /></IconButton>}
    {hasTrace && <IconButton label="查看轨迹" onClick={onTrace}><ListTree size={15} /></IconButton>}
    {meta && <span className="ml-[10px] min-w-0 truncate font-mono text-2xs text-ink-ghost">{meta}</span>}
  </div>
}

function IconButton({ label, disabled, onClick, children }: { label: string; disabled?: boolean; onClick: () => void; children: React.ReactNode }) {
  return <button type="button" aria-label={label} title={label} disabled={disabled} onClick={onClick} className="flex h-[28px] w-[28px] flex-none items-center justify-center rounded-md border-0 bg-transparent p-0 text-ink-muted transition-colors duration-[120ms] hover:bg-surface-active hover:text-ink disabled:pointer-events-none disabled:opacity-40">{children}</button>
}

function Composer({ chips, prompt, setPrompt, busy, running, empty, onSubmit, onStop, onKeyDown }: { chips: React.ReactNode; prompt: string; setPrompt: (value: string) => void; busy: boolean; running?: boolean; empty?: boolean; onSubmit: () => void; onStop: () => void; onKeyDown: (event: KeyboardEvent<HTMLTextAreaElement>) => void }) {
  function autoGrow(element: HTMLTextAreaElement) { element.style.height = 'auto'; element.style.height = `${Math.min(element.scrollHeight, 180)}px` }
  // 问候与快速开始都在流外(absolute)：输入框尺寸恒定，空↔对话仅位移，不改尺寸。
  return <div className="composer">
    <div className="relative min-w-0">
      <div className={`composer-greeting pointer-events-none absolute inset-x-0 bottom-full mb-[26px] flex flex-col gap-[6px] transition-opacity duration-[240ms] ease-[cubic-bezier(.2,0,0,1)] motion-reduce:transition-none ${empty ? 'opacity-100' : 'opacity-0'}`} aria-hidden={!empty}>
        {/* 空态的品牌标记：噪点解码播一次后常亮；每次回到空态（新对话）重播。 */}
        {empty && <PixelLoader className="mb-[10px] text-ink" layout="row" animation="decode" cell={3} gap={1} letterSpacing={6} decode={{ once: true }} label="RWKV" />}
        <span className=" text-lg text-brand">你好</span>
        <h1 className="m-0 text-display font-semibold leading-[1.35] tracking-[.01em] text-ink">需要我为你做些什么？</h1>
      </div>
      {/* 输入框上方的运行标签：模型、State、能力、工作区 */}
      <div className="mb-[8px]">{chips}</div>
      <div data-running={running || undefined} className="composer-box data-running:running-ring relative flex min-h-[52px] min-w-0 items-end rounded-lg border border-line bg-paper-wash shadow-hair transition-[border-color,box-shadow] duration-[120ms] ease-[cubic-bezier(.2,0,0,1)] motion-reduce:transition-none focus-within:border-line-strong focus-within:ring-[3px] focus-within:ring-ink/10">
        <textarea aria-label="消息" rows={1} value={prompt} placeholder="描述你想要完成的任务" className="block min-h-[52px] max-h-[180px] min-w-0 flex-1 resize-none border-0 bg-transparent p-[13px_4px_12px_15px] text-md leading-[1.7] text-ink outline-0 focus:outline-none focus-visible:outline-none placeholder:text-placeholder" onChange={(event) => { setPrompt(event.target.value); autoGrow(event.target) }} onKeyDown={onKeyDown} />
        <div className="flex flex-none items-center p-[12px_12px_12px_6px]">
          {busy
            // 运行中发送键变成停止键：中断后端这一轮，已完成的步骤保留在轨迹里。
            ? <button type="button" title="停止" aria-label="停止运行" onClick={onStop} className="flex h-[28px] w-[28px] items-center justify-center rounded-md border-0 bg-ink p-0 text-paper transition-opacity hover:opacity-85"><Square size={10} fill="currentColor" /></button>
            : <button type="button" title="发送（⏎）" aria-label="发送" onClick={() => void onSubmit()} disabled={!prompt.trim()} className="flex h-[28px] w-[28px] items-center justify-center rounded-md border-0 bg-brand p-0 text-brand-fg transition-colors duration-[120ms] ease-[cubic-bezier(.2,0,0,1)] motion-reduce:transition-none disabled:bg-transparent disabled:text-ink-ghost"><CornerDownLeft size={15} /></button>}
        </div>
      </div>
      <div className={`composer-starters absolute inset-x-0 top-full mt-[9px] flex flex-wrap gap-[9px] transition-opacity duration-[240ms] ease-[cubic-bezier(.2,0,0,1)] motion-reduce:transition-none ${empty ? 'opacity-100' : 'pointer-events-none opacity-0'}`} aria-hidden={!empty} aria-label="快速开始">
        {STARTER_PROMPTS.map((starter) => <button key={starter} tabIndex={empty ? 0 : -1} className="rounded-lg border border-line bg-paper-wash px-3 py-[6px] text-sm shadow-hair text-ink-soft transition-colors hover:bg-surface-active hover:text-ink" onClick={() => setPrompt(starter)}>{starter}</button>)}
      </div>
    </div>
  </div>
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




function activityLabel(item?: AgentActivity) { if (!item) return '正在思考…'; const child = item.subagentIndex ? `Agent ${item.subagentIndex} · ` : ''; if (item.kind === 'subagent_start') return `Agent ${item.subagentIndex} · 已开始子任务`; if (item.kind === 'subagent_done') return `Agent ${item.subagentIndex} · ${item.error ? '子任务失败' : '子任务完成'}`; if (item.kind === 'model_start') return `${child}步骤 ${item.step || 1} · 正在决定下一步`; if (item.kind === 'route_start') return `${child}正在选择能力组`; if (item.kind === 'tool_start') return `${child}步骤 ${item.step} · 正在使用 ${item.tool}`; if (item.kind === 'tool_retry') return `${child}步骤 ${item.step} · ${item.tool} 自动退避后重试`; if (item.kind === 'tool_done') return `${child}步骤 ${item.step} · ${item.tool} 已完成`; return 'Agent 正在工作…' }
function relativeTime(value: string) { const timestamp = new Date(value).getTime(); if (!Number.isFinite(timestamp)) return ''; const elapsed = Math.max(0, Math.floor((Date.now() - timestamp) / 1000)); if (elapsed < 60) return '刚刚'; const minutes = Math.floor(elapsed / 60); if (minutes < 60) return `${minutes} 分钟前`; const hours = Math.floor(minutes / 60); if (hours < 24) return `${hours} 小时前`; return `${Math.floor(hours / 24)} 天前` }
function normalizeTimestamp(value?: string) { if (!value) return undefined; const timestamp = new Date(value).getTime(); return Number.isFinite(timestamp) && timestamp >= Date.UTC(2000, 0, 1) ? value : undefined }
function formatTurnTime(value?: string) {
  if (!value) return '本地'
  const date = new Date(value)
  if (Number.isNaN(date.getTime()) || date.getUTCFullYear() <= 1) return '本地'
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}
function userMessage(content: string): Message { return { id: `pending-${nextMessageID++}`, role: 'user', content, createdAt: new Date().toISOString() } }
function errorText(error: unknown) { return error instanceof Error ? error.message : String(error) }
