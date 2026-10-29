import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import * as Backend from '../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import { AgentProtocol, AgentPromptPreview, Config, ModelState, Provider, Result, Status } from '../bindings/github.com/no22/RWKV-Agent/api/models'
import {
  AppBootstrap,
  ConversationSummary,
  ConversationView,
  DisplayMessage,
  StoragePaths,
  WorkspaceItem,
} from '../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/models'
import { AgentSettings, SavedProvider, SubagentStep, SubagentTrace, ToolRetryTrace, ToolTrace } from '../bindings/github.com/no22/RWKV-Agent/internal/appstorage/models'
import App from './App'
import { SnackbarProvider } from './snackbar-context'

const eventHandlers = vi.hoisted(() => new Map<string, (event: { data: unknown }) => void>())

vi.mock('@wailsio/runtime', () => ({
  Events: { On: (name: string, handler: (event: { data: unknown }) => void) => {
    eventHandlers.set(name, handler)
    return () => eventHandlers.delete(name)
  } },
  Call: { ByID: vi.fn() },
  Create: {
    Array: (create: (value: unknown) => unknown) => (values?: unknown[]) => values == null ? values : values.map(create),
    Map: () => (value: unknown) => value,
    Nullable: (create: (value: unknown) => unknown) => (value: unknown) => value == null ? value : create(value),
    Any: (value: unknown) => value,
  },
}))

vi.mock('../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice', () => ({
  Bootstrap: vi.fn(),
  UnloadModel: vi.fn(),
  GetAgentSettings: vi.fn().mockResolvedValue({}),
  SaveAgentSettings: vi.fn().mockImplementation(async (value) => value),
  FileChanges: vi.fn().mockResolvedValue([]),
  ResolveFileChanges: vi.fn().mockResolvedValue([]),
  Status: vi.fn().mockResolvedValue({ state: 'idle', workspace: '/tmp/RWKV-Agent', hasApiKey: false, updatedAt: new Date().toISOString() }),
  Chat: vi.fn(),
  Regenerate: vi.fn(),
  EditLast: vi.fn(),
  Configure: vi.fn(),
  ConfigureProvider: vi.fn(),
  SaveProvider: vi.fn(),
  ActivateProvider: vi.fn(),
  SetRuntimeFormat: vi.fn(),
  SetRuntimeState: vi.fn(),
  ListStates: vi.fn().mockResolvedValue({ states: [{ id: 'state-1', filename: 'test.pth' }] }),
  ListAdapters: vi.fn().mockResolvedValue({ adapters: [{ id: 'miss-1' }] }),
  SetRuntimeAdapter: vi.fn(),
  DeleteProvider: vi.fn(),
  ListRemoteModels: vi.fn(),
  PreviewSystemPrompt: vi.fn(),
  NewConversation: vi.fn().mockResolvedValue(undefined),
  ChooseWorkspace: vi.fn(),
  OpenWorkspace: vi.fn(),
  OpenConversation: vi.fn(),
  DeleteConversation: vi.fn().mockResolvedValue(undefined),
  ExportTrajectory: vi.fn().mockResolvedValue('/tmp/exported.jsonl'),
}))

function bootstrap(overrides: Partial<AppBootstrap> = {}) {
  return new AppBootstrap({
    status: new Status({
      state: ModelState.ModelIdle,
      workspace: '/tmp/RWKV-Agent',
      hasApiKey: false,
      updatedAt: new Date().toISOString(),
      message: 'Choose a model',
    }),
    config: new Config(),
    hasConfig: false,
    conversations: [],
    workspaces: [new WorkspaceItem({ path: '/tmp/RWKV-Agent', name: 'RWKV-Agent', available: true, active: true })],
    paths: new StoragePaths(),
    ...overrides,
  })
}

function savedRemoteProvider(config: Partial<Config> = {}, profile: Partial<SavedProvider> = {}) {
  return new SavedProvider({
    id: 'saved-provider',
    label: 'Saved connection',
    config: new Config({
      provider: Provider.ProviderRWKVLightningCUDA,
      endpoint: 'https://saved.example.test',
      model: 'saved-model',
      ...config,
    }),
    lastUsedAt: new Date().toISOString(),
    ...profile,
  })
}

/* 和 main.tsx 一样包在通知层里：设置的结果与错误都以右下角通知出现。 */
function renderApp() {
  return render(<SnackbarProvider><App /></SnackbarProvider>)
}

/* 设置页下拉是自绘 combobox：点开后点对应 data-value 的选项。 */
function chooseOption(label: string, value: string) {
  fireEvent.click(screen.getByLabelText(label))
  const option = document.querySelector(`[role="option"][data-value="${value}"]`)
  if (!option) throw new Error(`${label} has no option ${value}`)
  fireEvent.click(option)
}

function openSettings() {
  fireEvent.click(screen.getByRole('button', { name: '设置' }))
}

/* 连接分区先显示列表：有已保存档案时点进正在编辑的那一行（默认是运行中的），新建草稿本来就在详情里。 */
function openDetail() {
  if (screen.queryByRole('button', { name: /^返回.*列表$/ })) return
  const list = screen.getByRole('list', { name: /列表$/ })
  fireEvent.click(within(list).getAllByRole('button')[0])
}

/* 生成参数、工具与搜索 Key 在全局「Agent」分区的三个标签里，所有连接共用。 */
async function openAgentTab(name: '生成' | '工具' | '搜索与数据源') {
  fireEvent.click(screen.getByRole('button', { name: 'Agent' }))
  await waitFor(() => expect(Backend.GetAgentSettings).toHaveBeenCalled())
  fireEvent.click(screen.getByRole('tab', { name }))
}

/* 请求头、State 这类不常改的项收在「高级」的折叠行里。 */
function expandDisclosure(label: string) {
  const button = screen.getByRole('button', { name: new RegExp(`^${label}`) })
  if (button.getAttribute('aria-expanded') !== 'true') fireEvent.click(button)
}

/* 最近一次保存的共用设置。 */
function lastAgentSave() {
  return vi.mocked(Backend.SaveAgentSettings).mock.calls.at(-1)![0]
}

const readyStatus = () => new Status({
  state: ModelState.ModelReady,
  provider: Provider.ProviderRWKVLightningCUDA,
  model: 'rwkv7-test',
  workspace: '/tmp/RWKV-Agent',
  hasApiKey: false,
  updatedAt: new Date().toISOString(),
})

/* 种子一个正在运行的远端档案：Agent 分区的自动应用会直接 ConfigureProvider。 */
function bootstrapWithRunningProvider(config: Partial<Config> = {}, profile: Partial<SavedProvider> = {}) {
  const provider = savedRemoteProvider(config, profile)
  vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
    status: new Status({
      state: ModelState.ModelReady,
      provider: Provider.ProviderRWKVLightningCUDA,
      model: 'rwkv7-test',
      workspace: '/tmp/RWKV-Agent',
      hasApiKey: false,
      updatedAt: new Date().toISOString(),
    }),
    config: provider.config,
    hasConfig: true,
    providers: [provider],
    activeProviderId: provider.id,
    runtimeProviderId: provider.id,
  }))
  vi.mocked(Backend.ConfigureProvider).mockResolvedValue(readyStatus())
  vi.mocked(Backend.SaveProvider).mockResolvedValue(provider)
  return provider
}

/* 等 Bootstrap 的档案列表真正水合（模型徽标渲染）再打开设置，否则会走新建草稿分支。 */
async function waitRuntimeReady() {
  // 芯片显示缩短后的名字（去掉 rwkv7- 前缀），完整名在悬停提示里。
  await waitFor(() => expect(document.querySelector('button[title^="rwkv7-test"]')).not.toBeNull())
}

/* 新建连接默认就在「远端连接」分区：不再有远端/本地切换，这里只确认表单是远端的。 */
function switchToRemoteProvider() {
  openDetail()
  expect(screen.getByLabelText('API 地址')).toBeInTheDocument()
}

beforeEach(() => {
  eventHandlers.clear()
  vi.mocked(Backend.FileChanges).mockResolvedValue([])
  vi.mocked(Backend.ResolveFileChanges).mockResolvedValue([])
  vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap())
  vi.mocked(Backend.PreviewSystemPrompt).mockResolvedValue(new AgentPromptPreview({
    control: 'preview-prompt',
    responseControl: '',
    toolNames: ['list_files'],
    protocolId: 'rwkv-g1-envelope-v1',
    rendererId: 'rwkv-chat-continuation-v2',
    thinkingMode: 'off',
    native: false,
  }))
})

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe('App', () => {
  it('renders the stable empty conversation layout', async () => {
    renderApp()
    expect(screen.getByText('你好')).toBeInTheDocument()
    expect(screen.getByLabelText('消息')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '概括这个仓库的近期进度' })).toBeInTheDocument()
    expect((await screen.findAllByText('RWKV-Agent')).length).toBeGreaterThan(0)
  })

  it('constrains long model names in the composer', async () => {
    const model = 'rwkv7-g1i-13.3b-20260805-ctx16384-release-history'
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      status: new Status({
        state: ModelState.ModelReady,
        model,
        workspace: '/tmp/RWKV-Agent',
        hasApiKey: false,
        updatedAt: new Date().toISOString(),
      }),
    }))

    const { container } = renderApp()

    const modelChipSelector = `button[title^="${model}"]`
    await waitFor(() => expect(container.querySelector(modelChipSelector)).not.toBeNull())
    // 芯片只显示认得出是哪个的前半段，完整名留在悬停提示里。
    expect(container.querySelector(modelChipSelector)).toHaveTextContent('g1i-13.3b-20260805…')
  })

  it('opens the settings page from the sidebar', () => {
    renderApp()
    openSettings()
    expect(screen.getByRole('dialog', { name: '设置' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '远端连接' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '本地推理' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Agent' })).toBeInTheDocument()
  })

  it('uses RWKV continuation by default and passes custom HTTP headers', async () => {
    vi.mocked(Backend.ConfigureProvider).mockResolvedValue(new Status({
      state: ModelState.ModelReady,
      provider: Provider.ProviderRWKVLightningCUDA,
      model: 'rwkv7-test',
      workspace: '/tmp/RWKV-Agent',
      hasApiKey: false,
      updatedAt: new Date().toISOString(),
    }))
    renderApp()
    openSettings()
    switchToRemoteProvider()
    fireEvent.change(screen.getByLabelText('API 地址'), { target: { value: 'https://example.test' } })
    fireEvent.change(screen.getByLabelText('模型 ID'), { target: { value: 'rwkv7-test' } })
    expandDisclosure('请求头')
    fireEvent.click(screen.getByRole('button', { name: '添加请求头' }))
    fireEvent.change(screen.getByLabelText('Header 名称'), { target: { value: 'CF-Access-Client-Id' } })
    fireEvent.change(screen.getByLabelText('Header 值'), { target: { value: 'secret' } })
    fireEvent.click(screen.getByRole('button', { name: '保存并连接' }))

    await waitFor(() => expect(Backend.ConfigureProvider).toHaveBeenCalledOnce())
    const config = vi.mocked(Backend.ConfigureProvider).mock.calls[0][2]
    expect(config.provider).toBe('rwkv-lightning-cuda')
    expect(config.rwkvStopTokens).toBe('eos')
    expect(config.stream).toBeUndefined()
    expect(config.headers).toEqual({ 'CF-Access-Client-Id': 'secret' })
    expect(config.agentProtocol).toBe('xml')
    // 工具开关是共用设置，由后端在连接时填进运行配置。
    expect(config.progressiveTools).toBeUndefined()
    expect(config.enableSubagents).toBeUndefined()
  })

  it.each([
    ['python', Provider.ProviderRWKVLightningPython, 'text'],
    ['cuda', Provider.ProviderRWKVLightningCUDA, 'eos'],
    ['openai', Provider.ProviderChatCompletions, undefined],
    ['irwkv', Provider.ProviderIRWKV, 'text'],
  ] as const)('saves a new %s connection with its own backend identity', async (protocol, provider, stops) => {
    renderApp()
    openSettings()
    switchToRemoteProvider()
    chooseOption('远端协议', protocol)
    fireEvent.change(screen.getByLabelText('API 地址'), { target: { value: 'https://example.test' } })
    fireEvent.change(screen.getByLabelText('模型 ID'), { target: { value: 'test-model' } })
    const bearer = protocol === 'openai' || protocol === 'irwkv'
    fireEvent.change(screen.getByLabelText(bearer ? 'API Key' : '服务密码'), { target: { value: 'test-secret' } })
    fireEvent.click(screen.getByRole('button', { name: '保存并连接' }))
    await waitFor(() => expect(Backend.ConfigureProvider).toHaveBeenCalledOnce())
    const config = vi.mocked(Backend.ConfigureProvider).mock.calls[0][2]
    expect(config.provider).toBe(provider)
    expect(config.rwkvStopTokens).toBe(stops)
    expect(bearer ? config.apiKey : config.password).toBe('test-secret')
    expect(bearer ? config.password : config.apiKey).toBeUndefined()
    expect(config.agentProtocol).toBe('xml')
  })

  it('saves web credentials once in the shared Agent section, not in the profile', async () => {
    bootstrapWithRunningProvider()
    renderApp()
    await waitRuntimeReady()
    openSettings()
    await openAgentTab('搜索与数据源')
    fireEvent.change(await screen.findByLabelText('Brave API Key'), { target: { value: 'brave-secret' } })
    fireEvent.change(screen.getByLabelText('Tavily API Key'), { target: { value: 'tavily-secret' } })
    fireEvent.change(screen.getByLabelText('DeepSeek API Key'), { target: { value: 'deepseek-secret' } })
    chooseOption('搜索后端', 'brave')
    chooseOption('天气数据源', 'wttr')

    await waitFor(() => expect(Backend.SaveAgentSettings).toHaveBeenCalled(), { timeout: 3000 })
    expect(lastAgentSave()).toMatchObject({
      braveApiKey: 'brave-secret', tavilyApiKey: 'tavily-secret', deepseekWebApiKey: 'deepseek-secret',
      webSearchBackend: 'brave', weatherBackend: 'wttr',
    })
    expect(await screen.findByText('已保存，下一轮对话生效')).toBeInTheDocument()
    expect(Backend.SaveProvider).not.toHaveBeenCalled()
    expect(Backend.ConfigureProvider).not.toHaveBeenCalled()
  })

  it('saves tool switches and subagent budgets as shared settings without reconnecting', async () => {
    bootstrapWithRunningProvider()
    renderApp()
    await waitRuntimeReady()
    openSettings()
    await openAgentTab('工具')
    fireEvent.click(await screen.findByLabelText('网页搜索与正文获取'))
    fireEvent.click(screen.getByLabelText('并发子 Agent'))
    fireEvent.change(screen.getByLabelText('子 Agent 并发'), { target: { value: '6' } })
    fireEvent.change(screen.getByLabelText('单 Agent 步数'), { target: { value: '5' } })
    fireEvent.change(screen.getByLabelText('批次超时（秒）'), { target: { value: '180' } })

    await waitFor(() => expect(lastAgentSave()).toMatchObject({
      enableWeb: true, enableSubagents: true, subagentMaxParallel: 6, subagentMaxSteps: 5, subagentTimeoutSeconds: 180,
    }), { timeout: 3000 })
    expect(Backend.SaveProvider).not.toHaveBeenCalled()
    expect(Backend.ConfigureProvider).not.toHaveBeenCalled()
  })

  it('keeps only the connection and its batching knobs in the connection detail', async () => {
    bootstrapWithRunningProvider()
    renderApp()
    await waitRuntimeReady()
    openSettings()
    openDetail()
    // 生成参数与工具不在连接里了：没有标签，也没有格式选择器。
    expect(screen.queryByRole('tablist', { name: '连接详情' })).not.toBeInTheDocument()
    expect(screen.queryByLabelText('格式预设')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('采样预设')).not.toBeInTheDocument()
    fireEvent.change(screen.getByLabelText('远端聚合窗口（毫秒）'), { target: { value: '15' } })

    await waitFor(() => expect(Backend.ConfigureProvider).toHaveBeenCalled(), { timeout: 3000 })
    expect(vi.mocked(Backend.ConfigureProvider).mock.calls[0][2]).toMatchObject({ remoteBatchWaitMs: 15 })
    expect(await screen.findByText('已自动生效')).toBeInTheDocument()
  })

  it.each([
    ['Markdown 工具调用（实验）', { agentProtocol: 'markdown', profile: '', thinking: 'off' }],
    ['深度思考', { agentProtocol: 'xml', profile: 'agent-wire-v1.0', wire: 'thinking=full,nudge=think', thinking: 'full' }],
  ] as const)('switches the running connection to %s from the format chip', async (label, expected) => {
    bootstrapWithRunningProvider({ profile: 'agent-wire-v1.0', agentProtocol: AgentProtocol.AgentProtocolXML, thinking: 'off' })
    vi.mocked(Backend.SetRuntimeFormat).mockResolvedValue(readyStatus())
    renderApp()
    await waitRuntimeReady()
    const chip = screen.getByRole('button', { name: '对话格式' })
    expect(chip).toHaveTextContent('标准')
    fireEvent.click(chip)
    fireEvent.click(await screen.findByText(label))

    await waitFor(() => expect(Backend.SetRuntimeFormat).toHaveBeenCalledOnce())
    expect(vi.mocked(Backend.SetRuntimeFormat).mock.calls[0][0]).toMatchObject(expected)
    expect(Backend.ConfigureProvider).not.toHaveBeenCalled()
  })

  it('submits the personal task contract as a shared setting', async () => {
    bootstrapWithRunningProvider()
    renderApp()
    await waitRuntimeReady()
    openSettings()
    await openAgentTab('生成')
    fireEvent.change(await screen.findByLabelText('附加任务约定'), { target: { value: '回答使用中文。' } })

    await waitFor(() => expect(lastAgentSave().taskControl).toBe('回答使用中文。'), { timeout: 3000 })
    expect(Backend.ConfigureProvider).not.toHaveBeenCalled()
  })

  it('auto-saves a non-running profile without reconnecting', async () => {
    const provider = bootstrapWithRunningProvider()
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      status: readyStatus(),
      config: provider.config,
      hasConfig: true,
      providers: [provider],
      activeProviderId: provider.id,
    }))
    renderApp()
    await waitRuntimeReady()
    openSettings()
    openDetail()
    fireEvent.change(screen.getByLabelText('模型 ID'), { target: { value: 'other-model' } })

    await waitFor(() => expect(Backend.SaveProvider).toHaveBeenCalled(), { timeout: 3000 })
    expect(Backend.ConfigureProvider).not.toHaveBeenCalled()
    expect(await screen.findByText('已自动保存')).toBeInTheDocument()
  })

  it('previews the system prompt with the running connection format', async () => {
    vi.mocked(Backend.PreviewSystemPrompt).mockResolvedValue(new AgentPromptPreview({
      control: 'You are a local-first assistant with read-only tools.',
      responseControl: '',
      toolNames: ['list_files', 'datetime'],
      protocolId: 'rwkv-g1-envelope-v1',
      rendererId: 'rwkv-chat-continuation-v2',
      thinkingMode: 'off',
      native: false,
    }))
    bootstrapWithRunningProvider({ profile: 'agent-wire-v1.0', thinking: 'full', wire: 'thinking=full,nudge=think' })
    renderApp()
    await waitRuntimeReady()
    openSettings()
    await openAgentTab('生成')
    // 预览默认收起，展开时才拉取。
    expect(screen.getByRole('button', { name: /^系统提示词预览/ })).toHaveAttribute('aria-expanded', 'false')
    expandDisclosure('系统提示词预览')

    expect(await screen.findByText(/You are a local-first assistant/)).toBeInTheDocument()
    expect(screen.getByText(/协议 rwkv-g1-envelope-v1/)).toBeInTheDocument()
    expect(screen.getByText(/工具 2 项/)).toBeInTheDocument()
    expect(vi.mocked(Backend.PreviewSystemPrompt).mock.calls[0][0]).toMatchObject({ profile: 'agent-wire-v1.0', thinking: 'full', wire: 'thinking=full,nudge=think' })
  })

  it('toggles session time injection independently of the system prompt', async () => {
    const preview = new AgentPromptPreview({
      control: '原有系统提示词',
      toolNames: [],
    })
    vi.mocked(Backend.PreviewSystemPrompt).mockResolvedValue(preview)
    renderApp()
    openSettings()
    await openAgentTab('生成')
    expandDisclosure('系统提示词预览')
    const toggle = screen.getByRole('checkbox', { name: '注入会话启动时间' })
    expect(toggle).not.toBeChecked()
    expect(await screen.findByText('原有系统提示词')).toBeInTheDocument()
    vi.mocked(Backend.PreviewSystemPrompt).mockResolvedValue(new AgentPromptPreview({ ...preview, sessionContext: '会话启动时间为 2026年10月12日 星期一 11时30分（UTC+08:00）。' }))
    fireEvent.click(toggle)
    expect(await screen.findByText(/会话启动时间为 2026年10月12日 星期一/)).toBeInTheDocument()
    expect(vi.mocked(Backend.PreviewSystemPrompt).mock.lastCall?.[0].injectSessionTime).toBe(true)
    expect(screen.getByText('原有系统提示词')).toBeInTheDocument()
    vi.mocked(Backend.PreviewSystemPrompt).mockResolvedValue(preview)
    fireEvent.click(toggle)
    await waitFor(() => expect(screen.queryByText(/会话启动时间为 2026年10月12日 星期一/)).not.toBeInTheDocument())
    expect(vi.mocked(Backend.PreviewSystemPrompt).mock.lastCall?.[0].injectSessionTime).toBe(false)
  })

  it('applies a named sampling preset as a shared setting', async () => {
    renderApp()
    openSettings()
    await openAgentTab('生成')
    // 没存过采样，后端会归一成 greedy，选择器应当认出它而不是报自定义。
    expect(screen.getByLabelText('采样预设')).toHaveAttribute('data-value', 'greedy')
    chooseOption('采样预设', 'agent-default')

    await waitFor(() => expect(Backend.SaveAgentSettings).toHaveBeenCalled(), { timeout: 3000 })
    expect(lastAgentSave()).toMatchObject({
      temperature: 0.3, topK: 65536, topP: 0.5,
      presencePenalty: 0, frequencyPenalty: 0, penaltyDecay: 1,
    })
  })

  it('drops to custom sampling once a preset value is overridden', async () => {
    renderApp()
    openSettings()
    await openAgentTab('生成')
    // 预设模式下六个数字是只读的展示，不占编辑位。
    expect(screen.queryByLabelText('温度')).not.toBeInTheDocument()
    chooseOption('采样预设', 'agent-default')
    chooseOption('采样预设', 'custom')
    // 切到自定义不改数值，从预设那组值出发继续调。
    expect(screen.getByLabelText('温度')).toHaveValue(0.3)
    // 下拉说自定义时说明文字不能说成"选中了预设"。
    expect(screen.getByText(/当前数值等同 Agent 推荐/)).toBeInTheDocument()
    fireEvent.change(screen.getByLabelText('温度'), { target: { value: '0.9' } })

    // 改过的配置不再冒充预设名。
    expect(screen.getByLabelText('采样预设')).toHaveAttribute('data-value', 'custom')
    expect(screen.getByText(/六个参数直接决定采样/)).toBeInTheDocument()
    await waitFor(() => expect(lastAgentSave()).toMatchObject({ temperature: 0.9, topK: 65536, topP: 0.5 }), { timeout: 3000 })
  })

  it('opens non-preset shared sampling in custom mode', async () => {
    vi.mocked(Backend.GetAgentSettings).mockResolvedValue(new AgentSettings({ temperature: 0.7, topK: 40, topP: 0.8, penaltyDecay: 0.98 }))
    renderApp()
    openSettings()
    await openAgentTab('生成')

    await waitFor(() => expect(screen.getByLabelText('采样预设')).toHaveAttribute('data-value', 'custom'))
    expect(screen.getByLabelText('温度')).toHaveValue(0.7)
    expect(screen.getByLabelText('top-k 截断')).toHaveValue(40)
  })

  it('saves the generation budget as a shared setting', async () => {
    renderApp()
    openSettings()
    await openAgentTab('生成')
    // 没存过的预算按后端缺省显示。
    expect(screen.getByLabelText('最大步数')).toHaveValue(16)
    expect(screen.getByLabelText('最大输出 token')).toHaveValue(1024)
    fireEvent.change(screen.getByLabelText('最大步数'), { target: { value: '24' } })
    fireEvent.change(screen.getByLabelText('最大输出 token'), { target: { value: '4096' } })
    fireEvent.change(screen.getByLabelText('决策输出 token'), { target: { value: '2048' } })

    await waitFor(() => expect(lastAgentSave()).toMatchObject({ maxSteps: 24, maxTokens: 4096, decisionMaxTokens: 2048 }), { timeout: 3000 })
  })

  it('saves a draft without switching the runtime connection', async () => {
    const saved = savedRemoteProvider({
      endpoint: 'https://draft.example.test',
      model: 'draft-model',
    }, {
      id: 'draft-provider',
      label: 'Draft connection',
    })
    vi.mocked(Backend.SaveProvider).mockResolvedValue(saved)
    bootstrapWithRunningProvider()

    renderApp()
    await waitRuntimeReady()
    openSettings()
    fireEvent.click(screen.getByRole('button', { name: '新建连接' }))
    switchToRemoteProvider()
    fireEvent.change(screen.getByLabelText('连接名称'), { target: { value: 'Draft connection' } })
    fireEvent.change(screen.getByLabelText('API 地址'), { target: { value: 'https://draft.example.test' } })
    fireEvent.change(screen.getByLabelText('模型 ID'), { target: { value: 'draft-model' } })
    fireEvent.click(screen.getByRole('button', { name: '保存' }))

    await waitFor(() => expect(Backend.SaveProvider).toHaveBeenCalledOnce())
    expect(Backend.ConfigureProvider).not.toHaveBeenCalled()
    expect(vi.mocked(Backend.SaveProvider).mock.calls[0][0]).toBe('')
    expect(vi.mocked(Backend.SaveProvider).mock.calls[0][1]).toBe('Draft connection')
    expect(vi.mocked(Backend.SaveProvider).mock.calls[0][2]).toMatchObject({
      endpoint: 'https://draft.example.test',
      model: 'draft-model',
    })
    expect(await screen.findByText(/档案已保存；当前运行连接保持不变/)).toBeInTheDocument()
  })

  it('marks edited fields as an unsaved draft', async () => {
    renderApp()
    openSettings()
    fireEvent.change(screen.getByLabelText('连接名称'), { target: { value: 'Unsaved connection' } })

    expect(await screen.findByText('未保存更改')).toBeInTheDocument()
  })

  it('marks only the running profile in the list and opens others without the badge', async () => {
    const runtime = savedRemoteProvider({}, { id: 'runtime-provider', label: 'Runtime connection' })
    const backup = savedRemoteProvider({
      endpoint: 'https://backup.example.test',
      model: 'backup-model',
    }, {
      id: 'backup-provider',
      label: 'Backup connection',
    })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      status: new Status({
        state: ModelState.ModelReady,
        provider: Provider.ProviderRWKVLightningCUDA,
        endpoint: runtime.config.endpoint,
        model: runtime.config.model,
        workspace: '/tmp/RWKV-Agent',
        hasApiKey: false,
        updatedAt: new Date().toISOString(),
      }),
      config: runtime.config,
      hasConfig: true,
      providers: [runtime, backup],
      activeProviderId: runtime.id,
      runtimeProviderId: runtime.id,
    }))

    renderApp()
    await waitFor(() => expect(Backend.Bootstrap).toHaveBeenCalledOnce())
    openSettings()
    // 设置打开先看列表：运行中的那一行带徽标，其他行没有。
    const list = screen.getByRole('list', { name: '远端连接列表' })
    expect(within(list).getByRole('button', { name: /^Runtime connection/ })).toHaveTextContent('运行中')
    expect(within(list).getByRole('button', { name: /^Backup connection/ })).not.toHaveTextContent('运行中')
    fireEvent.click(within(list).getByRole('button', { name: /^Backup connection/ }))

    expect(screen.getByLabelText('连接名称')).toHaveValue('Backup connection')
    expect(screen.queryByText('运行中')).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: '返回远端连接列表' }))
    expect(await screen.findByRole('button', { name: /^Runtime connection/ })).toHaveTextContent('运行中')
  })

  it('auto-saves a valid edit before switching profiles instead of asking', async () => {
    const first = savedRemoteProvider({}, { id: 'first-provider', label: 'First connection' })
    const second = savedRemoteProvider({ model: 'second-model' }, { id: 'second-provider', label: 'Second connection' })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      config: first.config,
      hasConfig: true,
      providers: [first, second],
      activeProviderId: first.id,
    }))
    vi.mocked(Backend.SaveProvider).mockResolvedValue(first)

    renderApp()
    await waitFor(() => expect(Backend.Bootstrap).toHaveBeenCalledOnce())
    openSettings()
    openDetail()
    fireEvent.change(screen.getByLabelText('模型 ID'), { target: { value: 'edited-model' } })
    fireEvent.click(screen.getByRole('button', { name: '返回远端连接列表' }))
    fireEvent.click(await screen.findByRole('button', { name: /^Second connection/ }))

    await waitFor(() => expect(Backend.SaveProvider).toHaveBeenCalledOnce())
    expect(vi.mocked(Backend.SaveProvider).mock.calls[0][0]).toBe('first-provider')
    expect(vi.mocked(Backend.SaveProvider).mock.calls[0][2].model).toBe('edited-model')
    expect(await screen.findByLabelText('连接名称')).toHaveValue('Second connection')
    expect(screen.queryByRole('dialog', { name: '有未保存的更改' })).not.toBeInTheDocument()
  })

  it('asks before leaving an edit that cannot be saved and never persists it', async () => {
    const first = savedRemoteProvider({}, { id: 'first-provider', label: 'First connection' })
    const second = savedRemoteProvider({ model: 'second-model' }, { id: 'second-provider', label: 'Second connection' })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      config: first.config,
      hasConfig: true,
      providers: [first, second],
      activeProviderId: first.id,
    }))

    renderApp()
    await waitFor(() => expect(Backend.Bootstrap).toHaveBeenCalledOnce())
    openSettings()
    openDetail()
    fireEvent.change(screen.getByLabelText('API 地址'), { target: { value: 'not a url' } })
    expect(screen.getByLabelText('API 地址')).toHaveAttribute('aria-invalid', 'true')
    expect(screen.getByText('API 地址必须是 http:// 或 https:// 开头的完整地址')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: '返回远端连接列表' }))

    const dialog = await screen.findByRole('dialog', { name: '有未保存的更改' })
    expect(within(dialog).queryByRole('button', { name: '保存' })).not.toBeInTheDocument()
    fireEvent.click(within(dialog).getByRole('button', { name: '放弃更改' }))
    fireEvent.click(await screen.findByRole('button', { name: /^Second connection/ }))
    expect(await screen.findByLabelText('连接名称')).toHaveValue('Second connection')
    expect(Backend.SaveProvider).not.toHaveBeenCalled()
  })

  it('still confirms leaving an unsaved new connection and can save it from the dialog', async () => {
    const created = savedRemoteProvider({ endpoint: 'https://new.example.test', model: 'new-model' }, { id: 'created', label: 'New one' })
    vi.mocked(Backend.SaveProvider).mockResolvedValue(created)
    renderApp()
    openSettings()
    switchToRemoteProvider()
    fireEvent.change(screen.getByLabelText('API 地址'), { target: { value: 'https://new.example.test' } })
    fireEvent.change(screen.getByLabelText('模型 ID'), { target: { value: 'new-model' } })
    // 新建连接不自动建档：等过防抖窗口也不会保存。
    await new Promise((resolve) => setTimeout(resolve, 1000))
    expect(Backend.SaveProvider).not.toHaveBeenCalled()

    fireEvent.keyDown(window, { key: 'Escape' })
    const dialog = await screen.findByRole('dialog', { name: '有未保存的更改' })
    fireEvent.click(within(dialog).getByRole('button', { name: '保存并返回' }))
    await waitFor(() => expect(Backend.SaveProvider).toHaveBeenCalledOnce())
    expect(vi.mocked(Backend.SaveProvider).mock.calls[0][0]).toBe('')
  })
  it('starts a new connection on the agent-wire-v1.0 wire without carrying shared settings', async () => {
    const created = savedRemoteProvider({ endpoint: 'https://new.example.test', model: 'new-model' }, { id: 'created', label: 'New one' })
    vi.mocked(Backend.SaveProvider).mockResolvedValue(created)
    renderApp()
    openSettings()
    switchToRemoteProvider()
    fireEvent.change(screen.getByLabelText('API 地址'), { target: { value: 'https://new.example.test' } })
    fireEvent.change(screen.getByLabelText('模型 ID'), { target: { value: 'new-model' } })
    fireEvent.keyDown(window, { key: 'Escape' })
    const dialog = await screen.findByRole('dialog', { name: '有未保存的更改' })
    fireEvent.click(within(dialog).getByRole('button', { name: '保存并返回' }))
    await waitFor(() => expect(Backend.SaveProvider).toHaveBeenCalledOnce())
    const config = vi.mocked(Backend.SaveProvider).mock.calls[0][2]
    expect(config).toMatchObject({ profile: 'agent-wire-v1.0', agentProtocol: 'xml', thinking: 'off', maxActiveBatch: 4, remoteBatchWaitMs: 10 })
    // 采样、预算与工具开关是共用设置，新连接的档案里不带。
    expect(config.temperature).toBeUndefined()
    expect(config.enableWeb).toBeUndefined()
    expect(config.maxTokens).toBeUndefined()
  })

  it('shows a saved connection without a profile as the legacy format on the chip', async () => {
    bootstrapWithRunningProvider({ profile: undefined })
    renderApp()
    await waitRuntimeReady()
    const chip = screen.getByRole('button', { name: '对话格式' })
    expect(chip).toHaveTextContent('旧版 XML')
    expect(chip.getAttribute('title')).toContain('不推荐')
  })

  it('activates a saved remote connection from the model chip', async () => {
    const provider = savedRemoteProvider({}, { id: 'p1', label: 'Solo connection' })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      providers: [provider],
      activeProviderId: provider.id,
    }))
    vi.mocked(Backend.ActivateProvider).mockResolvedValue(new Status({
      state: ModelState.ModelReady,
      provider: Provider.ProviderRWKVLightningCUDA,
      model: provider.config.model,
      workspace: '/tmp/RWKV-Agent',
      hasApiKey: false,
      updatedAt: new Date().toISOString(),
    }))

    renderApp()
    await waitFor(() => expect(Backend.Bootstrap).toHaveBeenCalledOnce())
    // 切换只在对话页的模型标签里做；设置里的列表行只是打开详情。
    fireEvent.click(screen.getByRole('button', { name: /运行配置|选择模型/ }))
    fireEvent.click(screen.getByTitle('连接到此 Provider'))

    await waitFor(() => expect(Backend.ActivateProvider).toHaveBeenCalledOnce())
    expect(vi.mocked(Backend.ActivateProvider).mock.calls[0][0]).toBe('p1')
    expect(await screen.findByText('已切换到：Solo connection')).toBeInTheDocument()
  })

  it.each([
    ['State', '默认状态', 'test.pth', 'state-1', 'SetRuntimeState'],
    ['MiSS 适配器', '基模', 'miss-1', 'miss-1', 'SetRuntimeAdapter'],
  ] as const)('notifies %s only after the backend confirms applying it', async (noun, chip, option, id, method) => {
    bootstrapWithRunningProvider()
    let resolve!: (value: Status) => void
    vi.mocked(Backend[method]).mockReturnValue(new Promise<Status>((done) => { resolve = done }) as ReturnType<typeof Backend.SetRuntimeState>)
    renderApp()
    await waitRuntimeReady()
    fireEvent.click(screen.getByRole('button', { name: chip }))
    fireEvent.click(await screen.findByRole('option', { name: new RegExp(option) }))
    expect(await screen.findByText(`正在使用 ${noun}…`)).toBeInTheDocument()
    expect(screen.queryByText(`已使用 ${noun}：${id}`)).not.toBeInTheDocument()
    await act(async () => resolve(new Status({ state: ModelState.ModelReady })))
    expect(await screen.findByText(`已使用 ${noun}：${id}`)).toBeInTheDocument()
    expect(screen.queryByText(`正在使用 ${noun}…`)).not.toBeInTheDocument()
  })

  it('replaces a failed connection notification without claiming success', async () => {
    const provider = savedRemoteProvider({}, { id: 'p1', label: 'Broken connection' })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({ providers: [provider], activeProviderId: provider.id }))
    vi.mocked(Backend.ActivateProvider).mockRejectedValue(new Error('服务器不可用'))
    renderApp()
    await waitFor(() => expect(Backend.Bootstrap).toHaveBeenCalledOnce())
    fireEvent.click(screen.getByRole('button', { name: /运行配置|选择模型/ }))
    fireEvent.click(screen.getByTitle('连接到此 Provider'))
    expect(await screen.findByRole('alert')).toHaveTextContent('切换连接失败：服务器不可用')
    expect(screen.queryByText('正在切换连接…')).not.toBeInTheDocument()
    expect(screen.queryByText('已切换到：Broken connection')).not.toBeInTheDocument()
  })

  it('closes the run config dropdown when its chip is clicked again', async () => {
    bootstrapWithRunningProvider()

    renderApp()
    const chip = await screen.findByRole('button', { name: /rwkv7-test/ })
    fireEvent.mouseDown(chip); fireEvent.click(chip)
    expect(screen.getByText('当前运行')).toBeInTheDocument()
    // 真实点击的顺序：mousedown（面板的点击外部关闭）先于 click（芯片的开合切换）。
    fireEvent.mouseDown(chip); fireEvent.click(chip)
    // 收起动画播完才卸载。
    await waitFor(() => expect(screen.queryByText('当前运行')).not.toBeInTheDocument())
  })

  it('toggles a shared capability from the chip without touching the profile', async () => {
    bootstrapWithRunningProvider({ enableWeb: true, enableSubagents: true })
    vi.mocked(Backend.GetAgentSettings).mockResolvedValue(new AgentSettings({ enableWeb: true, enableSubagents: true, braveApiKey: 'kept' }))

    renderApp()
    await waitRuntimeReady()
    const web = screen.getByRole('switch', { name: '网页搜索' })
    expect(web).toHaveAttribute('aria-checked', 'true')
    fireEvent.click(web)

    await waitFor(() => expect(Backend.SaveAgentSettings).toHaveBeenCalledOnce())
    // 只改这一项，其余共用设置原样存回去。
    expect(lastAgentSave()).toMatchObject({ enableWeb: false, enableSubagents: true, braveApiKey: 'kept' })
    expect(await screen.findByText('网页搜索已关闭，所有连接下一轮生效')).toBeInTheDocument()
    expect(Backend.ConfigureProvider).not.toHaveBeenCalled()
    expect(Backend.SaveProvider).not.toHaveBeenCalled()
  })

  it('derives the capability indicator from the running config', async () => {
    bootstrapWithRunningProvider({ enableWeb: true, enableSubagents: true })
    renderApp()
    expect(await screen.findByTitle(/能力：web · subagents/)).toBeInTheDocument()
  })

  it('closes via Escape with confirmation when the draft is dirty', async () => {
    renderApp()
    openSettings()
    fireEvent.change(screen.getByLabelText('连接名称'), { target: { value: 'Esc draft' } })

    fireEvent.keyDown(window, { key: 'Escape' })
    expect(await screen.findByRole('dialog', { name: '有未保存的更改' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: '放弃更改' }))
    await waitFor(() => expect(screen.queryByLabelText('连接名称')).not.toBeInTheDocument())
  })

  it('closes the settings sheet with the close button, a backdrop click or a second Cmd+,', async () => {
    renderApp()
    fireEvent.keyDown(window, { key: ',', metaKey: true })
    expect(screen.getByRole('dialog', { name: '设置' })).toBeInTheDocument()
    fireEvent.keyDown(window, { key: ',', metaKey: true })
    await waitFor(() => expect(screen.queryByRole('dialog', { name: '设置' })).not.toBeInTheDocument())

    openSettings()
    const backdrop = screen.getByRole('dialog', { name: '设置' }).parentElement!
    fireEvent.pointerDown(backdrop)
    fireEvent.click(backdrop)
    await waitFor(() => expect(screen.queryByRole('dialog', { name: '设置' })).not.toBeInTheDocument())

    openSettings()
    fireEvent.click(screen.getByRole('button', { name: '关闭设置' }))
    await waitFor(() => expect(screen.queryByRole('dialog', { name: '设置' })).not.toBeInTheDocument())
  })

  it('keeps an auto-derived name in sync with the model in the list and on save', async () => {
    const provider = bootstrapWithRunningProvider({}, { label: 'saved-model · saved.example.test' })
    renderApp()
    await waitRuntimeReady()
    openSettings()
    openDetail()
    expect(screen.getByLabelText('连接名称')).toHaveValue('')
    fireEvent.change(screen.getByLabelText('模型 ID'), { target: { value: 'next-model' } })
    fireEvent.click(screen.getByRole('button', { name: '返回远端连接列表' }))
    expect(await screen.findByRole('button', { name: /^next-model · saved\.example\.test/ })).toBeInTheDocument()
    await waitFor(() => expect(Backend.SaveProvider).toHaveBeenCalledOnce(), { timeout: 3000 })
    // 空名称交给后端按新模型重新派生。
    expect(vi.mocked(Backend.SaveProvider).mock.calls[0][0]).toBe(provider.id)
    expect(vi.mocked(Backend.SaveProvider).mock.calls[0][1]).toBe('')
  })

  it('updates an outdated model and its automatic name from 测试连接', async () => {
    const provider = bootstrapWithRunningProvider({ model: 'old-model' }, { label: 'older-model · saved.example.test' })
    vi.mocked(Backend.ListRemoteModels).mockResolvedValue([{ id: 'served-model' } as never])
    renderApp()
    await waitRuntimeReady()
    openSettings()
    openDetail()
    // 旧模型派生的名字也是自动名：表单留空，按当前模型显示。
    expect(screen.getByLabelText('连接名称')).toHaveValue('')
    fireEvent.click(screen.getByRole('button', { name: '测试连接' }))

    expect(await screen.findByText(/模型 ID 已从 old-model 更新为 served-model/)).toBeInTheDocument()
    expect(screen.getByLabelText('模型 ID')).toHaveValue('served-model')
    expect(screen.getByLabelText('连接名称')).toHaveAttribute('placeholder', 'served-model · saved.example.test（自动命名）')
    await waitFor(() => expect(Backend.SaveProvider).toHaveBeenCalled(), { timeout: 3000 })
    expect(vi.mocked(Backend.SaveProvider).mock.calls.at(-1)!.slice(0, 2)).toEqual([provider.id, ''])
    expect(vi.mocked(Backend.SaveProvider).mock.calls.at(-1)![2].model).toBe('served-model')
  })

  it('shows settings results as a corner toast instead of a notice that follows you to other pages', async () => {
    bootstrapWithRunningProvider()
    vi.mocked(Backend.ListRemoteModels).mockResolvedValue([{ id: 'saved-model' }] as never)
    renderApp()
    await waitRuntimeReady()
    openSettings()
    openDetail()
    fireEvent.click(screen.getByRole('button', { name: '测试连接' }))
    const toast = await screen.findByText('连接成功，发现 1 个模型。')
    // 通知挂在设置弹窗外面：回到列表、换到本地推理，页面里都没有这句话。
    const dialog = screen.getByRole('dialog', { name: '设置' })
    expect(dialog).not.toContainElement(toast)
    fireEvent.click(screen.getByRole('button', { name: '返回远端连接列表' }))
    fireEvent.click(within(dialog).getByRole('button', { name: '本地推理' }))
    expect(within(dialog).queryByText(/连接成功/)).not.toBeInTheDocument()
  })

  it('keeps a model the server still serves and a name the user wrote', async () => {
    bootstrapWithRunningProvider({}, { label: '我的连接' })
    vi.mocked(Backend.ListRemoteModels).mockResolvedValue([{ id: 'other-model' }, { id: 'saved-model' }] as never)
    renderApp()
    await waitRuntimeReady()
    openSettings()
    openDetail()
    fireEvent.click(screen.getByRole('button', { name: '测试连接' }))

    expect(await screen.findByText('连接成功，发现 2 个模型。')).toBeInTheDocument()
    expect(screen.getByLabelText('模型 ID')).toHaveValue('saved-model')
    expect(screen.getByLabelText('连接名称')).toHaveValue('我的连接')
  })

  it('applies connection edits to the running remote profile without a save button', async () => {
    const provider = bootstrapWithRunningProvider()
    renderApp()
    await waitRuntimeReady()
    openSettings()
    openDetail()
    expect(screen.queryByRole('button', { name: '保存' })).not.toBeInTheDocument()
    // 运行中的档案没有可点的主按钮，只显示状态。
    expect(screen.queryByRole('button', { name: '使用此连接' })).not.toBeInTheDocument()
    expect(screen.getAllByText('运行中').length).toBeGreaterThan(0)

    fireEvent.change(screen.getByLabelText('模型 ID'), { target: { value: 'rwkv-live-edit' } })
    expect(screen.getByText('待保存…')).toBeInTheDocument()

    await waitFor(() => expect(Backend.ConfigureProvider).toHaveBeenCalledOnce(), { timeout: 3000 })
    expect(Backend.SaveProvider).toHaveBeenCalledOnce()
    expect(vi.mocked(Backend.SaveProvider).mock.calls[0][0]).toBe(provider.id)
    expect(vi.mocked(Backend.ConfigureProvider).mock.calls[0][2].model).toBe('rwkv-live-edit')
    expect(await screen.findByText('已自动生效')).toBeInTheDocument()
  })

  it('renames a running profile without reconnecting and shows the new name in the list', async () => {
    bootstrapWithRunningProvider()
    renderApp()
    await waitRuntimeReady()
    openSettings()
    openDetail()
    fireEvent.change(screen.getByLabelText('连接名称'), { target: { value: 'Renamed connection' } })
    fireEvent.click(screen.getByRole('button', { name: '返回远端连接列表' }))
    expect(await screen.findByRole('button', { name: /^Renamed connection/ })).toBeInTheDocument()

    await waitFor(() => expect(Backend.SaveProvider).toHaveBeenCalledOnce(), { timeout: 3000 })
    expect(vi.mocked(Backend.SaveProvider).mock.calls[0][1]).toBe('Renamed connection')
    expect(Backend.ConfigureProvider).not.toHaveBeenCalled()
  })

  it('does not auto-save an invalid endpoint and explains why', async () => {
    bootstrapWithRunningProvider()
    renderApp()
    await waitRuntimeReady()
    openSettings()
    openDetail()
    fireEvent.change(screen.getByLabelText('API 地址'), { target: { value: 'https://user:pw@host.test' } })
    expect(await screen.findByText(/未保存：API 地址不能内嵌账号密码/)).toBeInTheDocument()
    // 远端档案没有切换按钮：这里只确认没有偷偷保存或重连。
    await new Promise((resolve) => setTimeout(resolve, 1000))
    expect(Backend.SaveProvider).not.toHaveBeenCalled()
    expect(Backend.ConfigureProvider).not.toHaveBeenCalled()
  })

  it('surfaces a rejected auto-save and does not retry the same draft', async () => {
    bootstrapWithRunningProvider()
    vi.mocked(Backend.SaveProvider).mockRejectedValue(new Error('another provider profile already uses this provider, endpoint, and model'))
    renderApp()
    await waitRuntimeReady()
    openSettings()
    openDetail()
    fireEvent.change(screen.getByLabelText('模型 ID'), { target: { value: 'duplicate-model' } })
    expect(await screen.findByText(/保存失败：another provider profile/, undefined, { timeout: 3000 })).toBeInTheDocument()
    await new Promise((resolve) => setTimeout(resolve, 1000))
    expect(Backend.SaveProvider).toHaveBeenCalledOnce()
    expect(Backend.ConfigureProvider).not.toHaveBeenCalled()
  })

  it('keeps local models in their own section and releases a loaded one', async () => {
    const local = new SavedProvider({
      id: 'local-provider', label: 'Local model',
      config: new Config({ provider: Provider.ProviderLocal, model: '/models/m.pth' }),
      lastUsedAt: new Date().toISOString(),
    })
    const remote = savedRemoteProvider({}, { id: 'remote-provider', label: 'Remote connection' })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      status: readyStatus(),
      config: local.config,
      hasConfig: true,
      providers: [local, remote],
      activeProviderId: local.id,
      runtimeProviderId: local.id,
    }))
    vi.mocked(Backend.UnloadModel).mockResolvedValue(new Status({ state: ModelState.ModelIdle }))
    renderApp()
    await waitRuntimeReady()

    // 对话页的模型菜单只列远端连接，本地模型走「加载与释放」入口。
    fireEvent.click(screen.getByRole('button', { name: /运行配置|选择模型/ }))
    expect(screen.getByText('Remote connection')).toBeInTheDocument()
    expect(screen.getByTitle('连接到此 Provider')).toBeInTheDocument()
    expect(screen.queryByText('Local model')).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /运行配置|选择模型/ }))

    // 本地模型在运行时，设置默认进「本地推理」，列表里只有本地模型。
    openSettings()
    expect(screen.getByRole('button', { name: '本地推理' })).toHaveAttribute('aria-current', 'page')
    expect(screen.getByRole('button', { name: /^Local model/ })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /^Remote connection/ })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: /^Local model/ })).toHaveTextContent('已加载')
    openDetail()
    fireEvent.click(screen.getByRole('button', { name: '释放模型' }))
    await waitFor(() => expect(Backend.UnloadModel).toHaveBeenCalledOnce())
  })

  it('marks a running local profile as needing a reload and reloads on demand', async () => {
    const local = new SavedProvider({
      id: 'local-provider', label: 'Local model',
      config: new Config({ provider: Provider.ProviderLocal, model: '/models/new.pth' }),
      lastUsedAt: new Date().toISOString(),
    })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      status: readyStatus(),
      config: new Config({ provider: Provider.ProviderLocal, model: '/models/old.pth' }),
      hasConfig: true,
      providers: [local],
      activeProviderId: local.id,
      runtimeProviderId: local.id,
      runtimeOutdated: true,
    }))
    vi.mocked(Backend.ConfigureProvider).mockResolvedValue(readyStatus())
    renderApp()
    await waitRuntimeReady()
    openSettings()
    openDetail()
    expect(screen.getByText('已加载 · 待重新加载')).toBeInTheDocument()
    expect(screen.getByText(/本地模型仍在用旧配置运行/)).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: '重新加载模型' }))
    await waitFor(() => expect(Backend.ConfigureProvider).toHaveBeenCalledOnce())
    expect(vi.mocked(Backend.ConfigureProvider).mock.calls[0][0]).toBe('local-provider')
    expect(vi.mocked(Backend.ConfigureProvider).mock.calls[0][2].model).toBe('/models/new.pth')
  })

  it('refreshes the provider list when the backend announces a change', async () => {
    renderApp()
    await waitFor(() => expect(Backend.Bootstrap).toHaveBeenCalledOnce())
    fireEvent.click(screen.getByRole('button', { name: /运行配置|选择模型/ }))
    expect(screen.getByText('尚无保存的远端连接，去设置里添加一个')).toBeInTheDocument()

    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({ providers: [savedRemoteProvider({}, { label: 'Pushed connection' })] }))
    await act(async () => { eventHandlers.get('providers:changed')?.({ data: undefined }) })
    expect(await screen.findByText('Pushed connection')).toBeInTheDocument()
  })

  it('allows drafting during a run and preserves the draft when stopped', async () => {
    bootstrapWithRunningProvider()
    const cancel = vi.fn()
    let reject: (reason: unknown) => void = () => {}
    const pending = new Promise<Result>((_, rejectRun) => { reject = rejectRun }) as Promise<Result> & { cancel: () => void }
    pending.cancel = () => { cancel(); reject(new Error('cancelled')) }
    vi.mocked(Backend.Chat).mockReturnValue(pending as unknown as ReturnType<typeof Backend.Chat>)

    renderApp()
    await waitRuntimeReady()
    fireEvent.change(screen.getByLabelText('消息'), { target: { value: 'long task' } })
    fireEvent.click(screen.getByRole('button', { name: '发送' }))
    const stop = await screen.findByRole('button', { name: '停止运行' })
    const composer = screen.getByLabelText('消息')
    expect(composer).toBeEnabled()
    fireEvent.focus(composer)
    fireEvent.change(composer, { target: { value: '下一条消息\n继续检查' } })
    expect(composer).toHaveValue('下一条消息\n继续检查')
    // 运行中的 Enter 保留浏览器换行行为，不触发第二次请求。
    expect(fireEvent.keyDown(composer, { key: 'Enter', code: 'Enter' })).toBe(true)
    expect(Backend.Chat).toHaveBeenCalledOnce()
    fireEvent.click(stop)

    expect(cancel).toHaveBeenCalledOnce()
    expect(await screen.findByRole('button', { name: '发送' })).toBeInTheDocument()
    expect(screen.getByLabelText('消息')).toHaveValue('下一条消息\n继续检查')
  })

  it('preserves stopped output and rejects late events in the next conversation', async () => {
    bootstrapWithRunningProvider()
    let reject!: (reason: unknown) => void
    const pending = new Promise<Result>((_, fail) => { reject = fail }) as Promise<Result> & { cancel: () => void }
    pending.cancel = () => reject(new Error('cancelled'))
    vi.mocked(Backend.Chat).mockReturnValue(pending as ReturnType<typeof Backend.Chat>)
    renderApp()
    await waitRuntimeReady()
    fireEvent.change(screen.getByLabelText('消息'), { target: { value: 'first' } })
    fireEvent.click(screen.getByRole('button', { name: '发送' }))
    await screen.findByRole('button', { name: '停止运行' })
    const emit = (data: object) => act(async () => { eventHandlers.get('agent:event')?.({ data }) })
    await emit({ kind: 'run_start', runId: '1' })
    const partial = '已经收到的回答'.repeat(50)
    await emit({ kind: 'answer_delta', runId: '1', text: partial })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({ status: readyStatus(), conversation: new ConversationView({ id: 'stopped', messages: [
      new DisplayMessage({ id: 'u1', role: 'user', content: 'first' }),
      new DisplayMessage({ id: 'a1', role: 'error', content: '已停止', trace: new Result({ output: partial, steps: [] }) }),
    ] }) }))
    fireEvent.click(screen.getByRole('button', { name: '停止运行' }))
    expect(screen.getByText(partial)).toBeInTheDocument()
    await screen.findByRole('button', { name: '发送' })
    expect(screen.getByText(partial)).toBeInTheDocument()
    expect(document.querySelector('.stream-tok')).toBeNull()
    fireEvent.keyDown(window, { key: 'n', metaKey: true })
    await waitFor(() => expect(screen.queryByText(partial)).not.toBeInTheDocument())
    vi.mocked(Backend.Chat).mockReturnValue(new Promise(() => {}) as ReturnType<typeof Backend.Chat>)
    fireEvent.change(screen.getByLabelText('消息'), { target: { value: 'second' } })
    fireEvent.click(screen.getByRole('button', { name: '发送' }))
    await screen.findByRole('button', { name: '停止运行' })
    await emit({ kind: 'run_start', runId: '2' })
    await emit({ kind: 'answer_delta', runId: '1', text: '旧会话不应出现' })
    await emit({ kind: 'tool_start', runId: '1', tool: 'web_search' })
    expect(document.querySelector('.turn-answer')).toBeNull()
    expect(screen.queryByText('旧会话不应出现')).not.toBeInTheDocument()
  })

  it('keeps Stop available for local playback and flushes without cancelling a completed request', async () => {
    bootstrapWithRunningProvider()
    let resolve!: (result: Result) => void
    const pending = new Promise<Result>(done => { resolve = done }) as Promise<Result> & { cancel: () => void }
    pending.cancel = vi.fn()
    vi.mocked(Backend.Chat).mockReturnValue(pending as ReturnType<typeof Backend.Chat>)
    renderApp()
    await waitRuntimeReady()
    fireEvent.change(screen.getByLabelText('消息'), { target: { value: 'animation' } })
    fireEvent.click(screen.getByRole('button', { name: '发送' }))
    await screen.findByRole('button', { name: '停止运行' })
    const text = '本地积压的完整回答'.repeat(500)
    await act(async () => {
      eventHandlers.get('agent:event')?.({ data: { kind: 'answer_delta', text } })
      resolve(new Result({ output: text, steps: [], durationMs: 1 }))
    })
    fireEvent.click(await screen.findByRole('button', { name: '停止运行' }))
    expect(screen.getByText(text)).toBeInTheDocument()
    expect(document.querySelector('.stream-tok')).toBeNull()
    expect(pending.cancel).not.toHaveBeenCalled()
    expect(await screen.findByRole('button', { name: '发送' })).toBeInTheDocument()
  })

  it('closes a conversation menu when its own button is clicked again', async () => {
    const conversation = new ConversationSummary({ id: 'c1', title: '检查项目', updatedAt: new Date().toISOString(), pinned: false })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({ conversations: [conversation] }))
    renderApp()
    const more = await screen.findByRole('button', { name: '会话“检查项目”的更多操作' })
    fireEvent.pointerDown(more); fireEvent.click(more)
    expect(screen.getByRole('menu', { name: '会话操作' })).toBeInTheDocument()
    fireEvent.pointerDown(more); fireEvent.click(more)
    expect(screen.queryByRole('menu', { name: '会话操作' })).not.toBeInTheDocument()
  })

  it('shows chat-page failures in the snackbar instead of the hidden settings footer', async () => {
    const conversation = new ConversationSummary({ id: 'c1', title: 'Broken', updatedAt: new Date().toISOString(), pinned: false })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({ conversations: [conversation] }))
    vi.mocked(Backend.OpenConversation).mockRejectedValue(new Error('conversation belongs to another workspace'))
    renderApp()
    fireEvent.click(await screen.findByTitle('Broken'))
    expect(await screen.findByText('conversation belongs to another workspace')).toBeInTheDocument()
  })

  it('shows a remembered Markdown format on the chip and the shared Router switch in Agent', async () => {
    bootstrapWithRunningProvider({ agentProtocol: AgentProtocol.AgentProtocolMarkdown })
    vi.mocked(Backend.GetAgentSettings).mockResolvedValue(new AgentSettings({ progressiveTools: true }))

    renderApp()
    await waitRuntimeReady()
    expect(screen.getByRole('button', { name: '对话格式' })).toHaveTextContent('Markdown')
    openSettings()
    await openAgentTab('工具')
    await waitFor(() => expect(screen.getByLabelText('渐进式工具路由')).toBeChecked())
  })

  it('hydrates saved provider settings and plaintext credentials', async () => {
    const provider = savedRemoteProvider({
      password: 'saved-password',
      headers: { 'X-Service-Key': 'saved-header' },
      enableWeb: true,
      braveApiKey: 'saved-brave',
      tavilyApiKey: 'saved-tavily',
      deepseekWebApiKey: 'saved-deepseek',
      webSearchBackend: 'deepseek',
    })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      config: provider.config,
      hasConfig: true,
      providers: [provider],
      activeProviderId: provider.id,
      runtimeProviderId: provider.id,
    }))

    renderApp()
    await waitFor(() => expect(Backend.Bootstrap).toHaveBeenCalledOnce())
    openSettings()
    openDetail()

    expect(screen.getByLabelText('API 地址')).toHaveValue('https://saved.example.test')
    expect(screen.getByLabelText('模型 ID')).toHaveValue('saved-model')
    expect(screen.getByLabelText(/服务密码/)).toHaveValue('saved-password')
    // 请求头收在折叠行里，摘要只露名称不露值。
    expect(screen.getByRole('button', { name: /^请求头/ })).toHaveTextContent('X-Service-Key')
    expandDisclosure('请求头')
    expect(screen.getByLabelText('Header 名称')).toHaveValue('X-Service-Key')
    expect(screen.getByLabelText('Header 值')).toHaveValue('saved-header')
    expect(screen.getByLabelText('Header 值')).toHaveAttribute('type', 'password')

    // 共用的 Key 与搜索后端由后端从旧档案迁出，在全局「Agent」分区里显示。
    vi.mocked(Backend.GetAgentSettings).mockResolvedValue(new AgentSettings({
      braveApiKey: 'saved-brave', tavilyApiKey: 'saved-tavily', deepseekWebApiKey: 'saved-deepseek', webSearchBackend: 'deepseek',
    }))
    fireEvent.click(screen.getByRole('button', { name: '关闭设置' }))
    await waitFor(() => expect(screen.queryByRole('dialog', { name: '设置' })).not.toBeInTheDocument())
    openSettings()
    await openAgentTab('搜索与数据源')
    expect(await screen.findByDisplayValue('saved-brave')).toBeInTheDocument()
    expect(screen.getByLabelText('Tavily API Key')).toHaveValue('saved-tavily')
    expect(screen.getByLabelText('DeepSeek API Key')).toHaveValue('saved-deepseek')
    expect(screen.getByLabelText('搜索后端')).toHaveAttribute('data-value', 'deepseek')
  })

  it('switches to a remembered workspace', async () => {
    const workspaces = [
      new WorkspaceItem({ path: '/tmp/project-a', name: 'project-a', available: true, active: true }),
      new WorkspaceItem({ path: '/tmp/project-b', name: 'project-b', available: true, active: false }),
    ]
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      status: new Status({ state: ModelState.ModelIdle, workspace: '/tmp/project-a', hasApiKey: false, updatedAt: new Date().toISOString() }),
      workspaces,
    }))
    vi.mocked(Backend.OpenWorkspace).mockResolvedValue(bootstrap({
      status: new Status({ state: ModelState.ModelIdle, workspace: '/tmp/project-b', hasApiKey: false, updatedAt: new Date().toISOString() }),
      workspaces: workspaces.map((item) => new WorkspaceItem({ ...item, active: item.path === '/tmp/project-b' })),
    }))

    renderApp()
    fireEvent.click(await screen.findByRole('button', { name: 'project-b' }))

    await waitFor(() => expect(Backend.OpenWorkspace).toHaveBeenCalledWith('/tmp/project-b'))
    expect(screen.getAllByText('project-b').length).toBeGreaterThan(0)
  })

  it('reopens a saved conversation and shows the tool activity card', async () => {
    const summary = new ConversationSummary({ id: 'conversation-1', title: '检查项目', updatedAt: new Date().toISOString() })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({ conversations: [summary] }))
    vi.mocked(Backend.OpenConversation).mockResolvedValue(new ConversationView({
      id: summary.id,
      title: summary.title,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      messages: [
        new DisplayMessage({ id: 'm1', role: 'user', content: '读取 README' }),
        new DisplayMessage({
          id: 'm2',
          role: 'assistant',
          content: '项目说明已读取',
          trajectory: [
            new ToolTrace({
              step: 1,
              tool: 'spawn_agents',
              status: 'completed',
              subagents: [new SubagentTrace({
                index: 1,
                task: '检查官方文档',
                status: 'completed',
                route: 'inspect',
                bundles: ['web'],
                durationMs: 23200,
                output: '确认了官方说明',
                sources: ['https://example.test/docs'],
                steps: [new SubagentStep({
                  step: 1,
                  tool: 'web_fetch',
                  arguments: '{"urls":["https://example.test/docs"]}',
                  status: 'completed',
                  retries: [new ToolRetryTrace({ attempt: 1, maxAttempts: 5, statusCode: 429, delayMs: 2000 })],
                })],
              })],
            }),
            new ToolTrace({ step: 2, tool: 'read_file', status: 'failed', error: '文件暂时不可读' }),
          ],
        }),
      ],
    }))

    renderApp()
    fireEvent.click(await screen.findByTitle('检查项目'))

    expect(await screen.findByText('项目说明已读取')).toBeInTheDocument()
    expect(Backend.OpenConversation).toHaveBeenCalledWith('conversation-1')
    const turn = screen.getByTestId('conversation-turn-1')
    expect(turn).toHaveTextContent('读取 README')
    expect(turn).toHaveTextContent('项目说明已读取')
    // 落定的工具卡片收起时只有汇总一行，失败次数一并标出
    const activity = within(turn).getByTestId('tool-activity')
    expect(activity).toHaveTextContent('派出了子 Agent、读取了文件 · 1 次失败')
    expect(screen.queryByText('检查官方文档')).not.toBeInTheDocument()
    fireEvent.click(within(activity).getByRole('button', { expanded: false }))
    fireEvent.click(within(activity).getByText('派出'))
    expect(within(activity).getByText('检查官方文档')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: '查看轨迹' }))
    const ledger = screen.getByRole('table')
    expect(within(ledger).getAllByText('spawn_agents').length).toBeGreaterThan(0)
    expect(within(ledger).getAllByText('read_file').length).toBeGreaterThan(0)
    // 旧会话的子 Agent 也作为子工具记录列出
    expect(within(ledger).getByText('检查官方文档')).toBeInTheDocument()
  })

  it('sends one turn when Enter fires twice before the next render', async () => {
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      status: new Status({ state: ModelState.ModelReady, model: 'scripted', workspace: '/tmp/RWKV-Agent', hasApiKey: false, updatedAt: new Date().toISOString() }),
    }))
    vi.mocked(Backend.Chat).mockReturnValue(new Promise(() => {}) as ReturnType<typeof Backend.Chat>)

    renderApp()
    const composer = await screen.findByLabelText('消息')
    fireEvent.change(composer, { target: { value: '你好' } })
    act(() => {
      fireEvent.keyDown(composer, { key: 'Enter' })
      fireEvent.keyDown(composer, { key: 'Enter' })
    })
    await waitFor(() => expect(Backend.Chat).toHaveBeenCalledOnce())
    expect(screen.getAllByTestId(/^conversation-turn-/)).toHaveLength(1)
  })

  it('does not send while an input method is composing', async () => {
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      status: new Status({ state: ModelState.ModelReady, model: 'scripted', workspace: '/tmp/RWKV-Agent', hasApiKey: false, updatedAt: new Date().toISOString() }),
    }))

    renderApp()
    const composer = await screen.findByLabelText('消息')
    fireEvent.change(composer, { target: { value: 'nihao' } })
    fireEvent.keyDown(composer, { key: 'Enter', keyCode: 229 })
    expect(Backend.Chat).not.toHaveBeenCalled()
  })

  it('groups live child activity under spawn_agents', async () => {
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      status: new Status({
        state: ModelState.ModelReady,
        model: 'scripted',
        workspace: '/tmp/RWKV-Agent',
        hasApiKey: false,
        updatedAt: new Date().toISOString(),
      }),
    }))
    let resolveChat!: (result: Result) => void
    vi.mocked(Backend.Chat).mockReturnValue(
      new Promise((resolve) => { resolveChat = resolve }) as ReturnType<typeof Backend.Chat>,
    )

    renderApp()
    const composer = await screen.findByLabelText('消息')
    fireEvent.change(composer, { target: { value: '并行检查' } })
    fireEvent.keyDown(composer, { key: 'Enter' })
    await waitFor(() => expect(Backend.Chat).toHaveBeenCalledWith('并行检查'))
    expect(screen.getByLabelText('消息')).toBeInTheDocument()

    const emit = eventHandlers.get('agent:event')
    expect(emit).toBeDefined()
    act(() => {
      emit?.({ data: { kind: 'tool_start', step: 1, tool: 'spawn_agents', arguments: '{"tasks":["检查文档","检查代码"]}' } })
      emit?.({ data: { kind: 'subagent_start', parentStep: 1, subagentIndex: 1, subagentTask: '检查文档' } })
      emit?.({ data: { kind: 'route_done', parentStep: 1, subagentIndex: 1, subagentTask: '检查文档', route: 'inspect', bundles: ['web'] } })
      emit?.({ data: { kind: 'tool_start', parentStep: 1, subagentIndex: 1, subagentTask: '检查文档', step: 1, tool: 'web_search', arguments: '{"query":"RWKV"}' } })
      emit?.({ data: { kind: 'tool_retry', parentStep: 1, subagentIndex: 1, subagentTask: '检查文档', step: 1, tool: 'web_search', attempt: 1, maxAttempts: 5, statusCode: 429, delayMs: 2000 } })
    })

    const runningTurn = screen.getByTestId('conversation-turn-1')
    expect(runningTurn).toHaveClass('pending')
    expect(runningTurn).toHaveTextContent('并行检查')
    // 工具调用卡片默认收起：只有一行运行状态，参数与子任务详情要展开才看得到
    const activity = screen.getByTestId('tool-activity')
    expect(activity).toHaveTextContent('web_search 自动退避后重试')
    expect(screen.queryByText('检查文档')).not.toBeInTheDocument()
    fireEvent.click(within(activity).getByRole('button', { expanded: false }))
    expect(within(activity).getByText('2 个子任务')).toBeInTheDocument()
    fireEvent.click(within(activity).getByText('2 个子任务'))
    expect(within(activity).getByText('检查文档')).toBeInTheDocument()
    expect(within(activity).getByText('web_search')).toBeInTheDocument()

    await act(async () => {
      resolveChat(new Result({ output: 'done', steps: [], duration: 0, durationMs: 1 }))
    })
    await waitFor(() => expect(screen.getByTestId('conversation-turn-1')).not.toHaveClass('pending'))
    expect(screen.getAllByTestId(/conversation-turn-/)).toHaveLength(1)
    expect(screen.getByText('done')).toBeInTheDocument()
  })

  it('does not replay entrance or streaming animations after switching to the trace tab and back', async () => {
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      status: new Status({ state: ModelState.ModelReady, model: 'scripted', workspace: '/tmp/RWKV-Agent', hasApiKey: false, updatedAt: new Date().toISOString() }),
    }))
    let resolveChat!: (result: Result) => void
    vi.mocked(Backend.Chat).mockReturnValue(new Promise((resolve) => { resolveChat = resolve }) as ReturnType<typeof Backend.Chat>)

    const { container } = renderApp()
    const composer = await screen.findByLabelText('消息')
    fireEvent.change(composer, { target: { value: '打个招呼' } })
    fireEvent.keyDown(composer, { key: 'Enter' })
    await waitFor(() => expect(Backend.Chat).toHaveBeenCalledOnce())
    expect(screen.getByTestId('conversation-turn-1')).toHaveClass('turn-enter')

    act(() => { eventHandlers.get('agent:event')?.({ data: { kind: 'answer_delta', step: 1, text: '你好世界' } }) })
    await act(async () => { resolveChat(new Result({ output: '你好世界', steps: [], durationMs: 1 })) })
    // 后端已返回但仍在吐字：收尾信息不能提前占位。
    expect(container.querySelector('.turn-actions')).toBeNull()
    // 匀速放完后交回普通渲染。
    await waitFor(() => {
      expect(screen.getByText('你好世界')).toBeInTheDocument()
      expect(container.querySelector('.turn-actions')).not.toBeNull()
      expect(container.querySelector('.stream-tok')).toBeNull()
    })

    fireEvent.click(screen.getByRole('tab', { name: /轨迹/ }))
    fireEvent.click(screen.getByRole('tab', { name: '对话' }))

    expect(screen.getByTestId('conversation-turn-1')).not.toHaveClass('turn-enter')
    expect(container.querySelector('.answer-reveal, .stream-tok')).toBeNull()
    expect(screen.getByText('你好世界')).toBeInTheDocument()
  })

  it('stops following the stream once the user scrolls up, and follows again near the bottom', async () => {
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      status: new Status({ state: ModelState.ModelReady, model: 'scripted', workspace: '/tmp/RWKV-Agent', hasApiKey: false, updatedAt: new Date().toISOString() }),
    }))
    vi.mocked(Backend.Chat).mockReturnValue(new Promise(() => undefined) as ReturnType<typeof Backend.Chat>)

    const { container } = renderApp()
    const composer = await screen.findByLabelText('消息')
    fireEvent.change(composer, { target: { value: '写一段长回答' } })
    fireEvent.keyDown(composer, { key: 'Enter' })
    await waitFor(() => expect(Backend.Chat).toHaveBeenCalledOnce())
    const scroller = container.querySelector('.conversation-scroll') as HTMLDivElement
    Object.defineProperty(scroller, 'scrollHeight', { configurable: true, value: 2000 })
    Object.defineProperty(scroller, 'clientHeight', { configurable: true, value: 500 })
    scroller.scrollTop = 1500
    fireEvent.scroll(scroller)

    // 用户往上滚：后续流式增量不再把视口拽回底部。
    scroller.scrollTop = 900
    fireEvent.scroll(scroller)
    fireEvent.wheel(scroller, { cancelable: false, deltaY: -100 })
    act(() => { eventHandlers.get('agent:event')?.({ data: { kind: 'answer_delta', step: 1, text: '第一段' } }) })
    await new Promise(resolve => setTimeout(resolve, 40))
    expect(scroller.scrollTop).toBe(900)
    expect(screen.getByRole('button', { name: '回到底部' })).toBeInTheDocument()

    // 滚回底部附近：重新贴底跟随。
    fireEvent.wheel(scroller, { cancelable: false, deltaY: 100 })
    scroller.scrollTop = 1500
    fireEvent.scroll(scroller)
    act(() => { eventHandlers.get('agent:event')?.({ data: { kind: 'answer_delta', step: 1, text: '第二段' } }) })
    await waitFor(() => expect(screen.queryByRole('button', { name: '回到底部' })).not.toBeInTheDocument())
    fireEvent.wheel(scroller, { cancelable: false, deltaY: -100 })
    scroller.scrollTop = 800
    fireEvent.scroll(scroller)
    fireEvent.click(screen.getByRole('button', { name: '回到底部' }))
    expect(scroller.scrollTop).toBe(1500)
  })

  it('opens the trace ledger inspector and exports JSONL', async () => {
    const trace = new Result({
      output: '已完成读取。',
      route: 'inspect',
      bundles: ['workspace'],
      routeSteps: [{ attempt: 1, request: { prompt: '路由到 inspect', bytes: 24 }, modelOutput: '{"route":"inspect"}', route: 'inspect', durationMs: 34 }],
      durationMs: 1234,
      steps: [
        { number: 1, stage: 'model', request: { prompt: '读取 README', bytes: 42 }, modelDurationMs: 800, usage: { promptTokens: 120, completionTokens: 20 } },
        { number: 2, stage: 'tool', tool: 'read_file', toolArguments: '{"path":"README.md"}', toolResult: '# RWKV Agent', toolExecuted: true, toolDurationMs: 400, usage: {} },
      ],
    })
    const summary = new ConversationSummary({ id: 'trace-conversation', title: '轨迹验收', updatedAt: new Date().toISOString() })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({ conversations: [summary] }))
    vi.mocked(Backend.OpenConversation).mockResolvedValue(new ConversationView({
      id: summary.id,
      title: summary.title,
      messages: [
        new DisplayMessage({ id: 'trace-user', role: 'user', content: '读取 README' }),
        new DisplayMessage({ id: 'trace-assistant', role: 'assistant', content: '已完成读取。', trace }),
      ],
    }))
    renderApp()
    fireEvent.click(await screen.findByTitle('轨迹验收'))
    expect(await screen.findByText('已完成读取。')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: '查看轨迹' }))

    // 新轨迹页：请求编号、请求检查器里的提示词、工具记录的参数与结果
    const ledger = screen.getByRole('table')
    expect(within(ledger).getAllByText('读取 README').length).toBeGreaterThan(0)
    fireEvent.click(screen.getByRole('button', { name: '请求 #2' }))
    fireEvent.click(screen.getByRole('tab', { name: '提示词' }))
    expect(screen.getAllByText(/读取 README/).length).toBeGreaterThan(0)
    fireEvent.click(within(ledger).getAllByText('read_file')[0])
    fireEvent.click(screen.getByRole('tab', { name: '结果' }))
    expect(screen.getAllByText(/# RWKV Agent/).length).toBeGreaterThan(0)

    fireEvent.click(screen.getByRole('button', { name: /导出/ }))
    await waitFor(() => expect(Backend.ExportTrajectory).toHaveBeenCalledOnce())
    expect(vi.mocked(Backend.ExportTrajectory).mock.calls[0][0]).toContain('读取 README')
  })

  it('shows legacy tool traces in the trajectory tab', async () => {
    const summary = new ConversationSummary({ id: 'legacy-conversation', title: '旧轨迹', updatedAt: new Date().toISOString() })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({ conversations: [summary] }))
    vi.mocked(Backend.OpenConversation).mockResolvedValue(new ConversationView({
      id: summary.id,
      title: summary.title,
      messages: [
        new DisplayMessage({ id: 'legacy-assistant', role: 'assistant', content: '旧数据已恢复', createdAt: '0001-01-01T00:00:00.000Z', trajectory: [{ step: 1, tool: 'read_file', status: 'completed' }] }),
      ],
    }))

    renderApp()
    fireEvent.click(await screen.findByTitle('旧轨迹'))
    expect(await screen.findByText('旧数据已恢复')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('tab', { name: /轨迹/ }))
    expect(within(screen.getByRole('table')).getAllByText('read_file').length).toBeGreaterThan(0)
  })

  it('restores and opens a failed run trajectory without reloading the page', async () => {
    const failure = new Result({
      error: '模型服务返回 503',
      durationMs: 612,
      steps: [{
        number: 1,
        stage: 'model',
        request: { prompt: '检查失败原因', bytes: 36 },
        modelDurationMs: 600,
        modelError: '模型服务返回 503',
        usage: {},
      }],
    })
    const failedConversation = new ConversationView({
      id: 'failed-conversation',
      title: '检查失败原因',
      messages: [
        new DisplayMessage({ id: 'failed-user', role: 'user', content: '检查失败原因' }),
        new DisplayMessage({ id: 'failed-error', role: 'error', content: '模型服务返回 503', trace: failure }),
      ],
    })
    vi.mocked(Backend.Bootstrap)
      .mockResolvedValueOnce(bootstrap({ status: new Status({ state: ModelState.ModelReady, model: 'scripted', workspace: '/tmp/RWKV-Agent', hasApiKey: false, updatedAt: new Date().toISOString() }) }))
      .mockResolvedValueOnce(bootstrap({
        status: new Status({ state: ModelState.ModelReady, model: 'scripted', workspace: '/tmp/RWKV-Agent', hasApiKey: false, updatedAt: new Date().toISOString() }),
        conversation: failedConversation,
      }))
    vi.mocked(Backend.Chat).mockRejectedValue(new Error('模型服务返回 503'))

    renderApp()
    const composer = await screen.findByLabelText('消息')
    fireEvent.change(composer, { target: { value: '检查失败原因' } })
    fireEvent.keyDown(composer, { key: 'Enter' })

    expect(await screen.findByText('模型服务返回 503')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '查看轨迹' })).toBeEnabled()
    expect(screen.getByRole('tab', { name: /轨迹/ })).toBeEnabled()
    fireEvent.click(screen.getByRole('button', { name: '查看轨迹' }))
    const ledger = screen.getByRole('table')
    expect(within(ledger).getAllByText('检查失败原因').length).toBeGreaterThan(0)
    fireEvent.click(within(ledger).getAllByText('模型服务返回 503')[0])
    expect(within(screen.getByRole('complementary', { name: '事件详情' })).getAllByText('模型服务返回 503').length).toBeGreaterThan(0)
  })



  it('keeps the prompt and error when the run fails before anything is persisted', async () => {
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({ status: readyStatus() }))
    vi.mocked(Backend.Chat).mockRejectedValue(new Error('连接未配置'))

    renderApp()
    const composer = await screen.findByLabelText('消息')
    fireEvent.change(composer, { target: { value: '检查会话建立失败' } })
    fireEvent.keyDown(composer, { key: 'Enter' })

    expect(await screen.findByText('连接未配置')).toBeInTheDocument()
    expect(screen.getByText('检查会话建立失败')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '重试' })).toBeEnabled()
  })

  it('regenerates the last turn in place instead of resending the prompt', async () => {
    const summary = new ConversationSummary({ id: 'regen-conversation', title: '重新生成', updatedAt: new Date().toISOString() })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      status: readyStatus(),
      conversations: [summary],
      conversation: new ConversationView({
        id: summary.id,
        title: summary.title,
        messages: [
          new DisplayMessage({ id: 'r1', role: 'user', content: '第一问' }),
          new DisplayMessage({ id: 'r2', role: 'assistant', content: '旧回答一' }),
          new DisplayMessage({ id: 'r3', role: 'user', content: '第二问' }),
          new DisplayMessage({ id: 'r4', role: 'assistant', content: '旧回答二' }),
        ],
      }),
    }))
    vi.mocked(Backend.Chat).mockClear()
    vi.mocked(Backend.Regenerate).mockResolvedValue(new Result({ output: '新回答二', steps: [], durationMs: 5 }))

    renderApp()
    await screen.findByText('旧回答二')
    const buttons = screen.getAllByRole('button', { name: '重新生成' })
    expect(buttons).toHaveLength(1)
    fireEvent.click(buttons[0])

    expect(await screen.findByText('新回答二')).toBeInTheDocument()
    expect(Backend.Regenerate).toHaveBeenCalledOnce()
    expect(Backend.Chat).not.toHaveBeenCalled()
    expect(screen.queryByText('旧回答二')).not.toBeInTheDocument()
    expect(screen.getByText('旧回答一')).toBeInTheDocument()
    expect(screen.getAllByText('第二问')).toHaveLength(1)
  })

  it('edits only the last user message and reruns that turn in place', async () => {
    const summary = new ConversationSummary({ id: 'edit-conversation', title: '编辑', updatedAt: new Date().toISOString() })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      status: readyStatus(),
      conversations: [summary],
      conversation: new ConversationView({
        id: summary.id,
        title: summary.title,
        messages: [
          new DisplayMessage({ id: 'e1', role: 'user', content: '第一问' }),
          new DisplayMessage({ id: 'e2', role: 'assistant', content: '回答一' }),
          new DisplayMessage({ id: 'e3', role: 'user', content: '第二问' }),
          new DisplayMessage({ id: 'e4', role: 'assistant', content: '旧回答二' }),
        ],
      }),
    }))
    vi.mocked(Backend.Chat).mockClear()
    vi.mocked(Backend.EditLast).mockResolvedValue(new Result({ output: '新回答二', steps: [], durationMs: 5 }))

    renderApp()
    await screen.findByText('旧回答二')
    const editButtons = screen.getAllByRole('button', { name: '编辑' })
    expect(editButtons).toHaveLength(1)
    fireEvent.click(editButtons[0])
    const editor = screen.getByRole('textbox', { name: '编辑消息' })
    expect(editor).toHaveValue('第二问')
    fireEvent.change(editor, { target: { value: '改过的第二问' } })
    fireEvent.click(screen.getByRole('button', { name: '发送修改' }))

    expect(await screen.findByText('新回答二')).toBeInTheDocument()
    expect(Backend.EditLast).toHaveBeenCalledWith('改过的第二问')
    expect(Backend.Chat).not.toHaveBeenCalled()
    expect(screen.queryByText('第二问')).not.toBeInTheDocument()
    expect(screen.queryByText('旧回答二')).not.toBeInTheDocument()
    expect(screen.getByText('改过的第二问')).toBeInTheDocument()
    expect(screen.getByText('回答一')).toBeInTheDocument()
  })

  it('closes the navigation drawer after opening a conversation', async () => {
    const summary = new ConversationSummary({ id: 'drawer-conversation', title: '抽屉会话', updatedAt: new Date().toISOString() })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({ conversations: [summary] }))
    vi.mocked(Backend.OpenConversation).mockResolvedValue(new ConversationView({ id: summary.id, title: summary.title, messages: [] }))

    renderApp()
    fireEvent.click(screen.getByRole('button', { name: '打开导航' }))
    expect(document.querySelector('.sidebar-scrim')).not.toBeNull()
    fireEvent.click(await screen.findByRole('button', { name: /^抽屉会话/ }))

    await waitFor(() => expect(Backend.OpenConversation).toHaveBeenCalledWith('drawer-conversation'))
    expect(document.querySelector('.sidebar-scrim')).toBeNull()
  })

})
