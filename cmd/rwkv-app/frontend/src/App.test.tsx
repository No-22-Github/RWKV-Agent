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
import { SavedProvider, SubagentStep, SubagentTrace, ToolRetryTrace, ToolTrace } from '../bindings/github.com/no22/RWKV-Agent/internal/appstorage/models'
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
  Status: vi.fn().mockResolvedValue({ state: 'idle', workspace: '/tmp/RWKV-Agent', hasApiKey: false, updatedAt: new Date().toISOString() }),
  Chat: vi.fn(),
  Regenerate: vi.fn(),
  Configure: vi.fn(),
  ConfigureProvider: vi.fn(),
  SaveProvider: vi.fn(),
  ActivateProvider: vi.fn(),
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

function openSettings() {
  fireEvent.click(screen.getByRole('button', { name: '设置' }))
}

function openSettingsSection(name: string) {
  fireEvent.click(screen.getByRole('button', { name }))
}

/* 网页与子 Agent 字段在设置页的 Agent 分区。 */
function openAgentSection() {
  openSettingsSection('Agent')
}

/* 对话协议、思考模式、采样、预算与附加约定在设置页的参数分区。 */
function openParametersSection() {
  openSettingsSection('参数')
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
  await screen.findAllByText('rwkv7-test')
}

function switchToRemoteProvider() {
  fireEvent.click(screen.getByRole('button', { name: '远端 Provider' }))
}

beforeEach(() => {
  eventHandlers.clear()
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
    render(<App />)
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

    const { container } = render(<App />)

    const modelChipSelector = `button[title^="${model}"]`
    await waitFor(() => expect(container.querySelector(modelChipSelector)).not.toBeNull())
    expect(container.querySelector(modelChipSelector)).toHaveTextContent(model)
  })

  it('opens the settings page from the sidebar', () => {
    render(<App />)
    openSettings()
    expect(screen.getByText('设置')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '连接' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Agent' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '本地模型' })).toBeInTheDocument()
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
    render(<App />)
    openSettings()
    switchToRemoteProvider()
    fireEvent.change(screen.getByLabelText('API 地址'), { target: { value: 'https://example.test' } })
    fireEvent.change(screen.getByLabelText('模型 ID'), { target: { value: 'rwkv7-test' } })
    fireEvent.click(screen.getByRole('button', { name: '添加请求头' }))
    fireEvent.change(screen.getByLabelText('Header 名称'), { target: { value: 'CF-Access-Client-Id' } })
    fireEvent.change(screen.getByLabelText('Header 值'), { target: { value: 'secret' } })
    fireEvent.click(screen.getByRole('button', { name: '保存并使用' }))

    await waitFor(() => expect(Backend.ConfigureProvider).toHaveBeenCalledOnce())
    const config = vi.mocked(Backend.ConfigureProvider).mock.calls[0][2]
    expect(config.provider).toBe('rwkv-lightning-cuda')
    expect(config.rwkvStopTokens).toBe('eos')
    expect(config.stream).toBeUndefined()
    expect(config.headers).toEqual({ 'CF-Access-Client-Id': 'secret' })
    expect(config.agentProtocol).toBe('xml')
    expect(config.progressiveTools).toBe(false)
    expect(config.enableSubagents).toBe(false)
  })

  it.each([
    ['python', Provider.ProviderRWKVLightningPython, 'text'],
    ['cuda', Provider.ProviderRWKVLightningCUDA, 'eos'],
    ['openai', Provider.ProviderChatCompletions, undefined],
  ] as const)('saves a new %s connection with its own backend identity', async (protocol, provider, stops) => {
    render(<App />)
    openSettings()
    switchToRemoteProvider()
    fireEvent.change(screen.getByLabelText('远端协议'), { target: { value: protocol } })
    fireEvent.change(screen.getByLabelText('API 地址'), { target: { value: 'https://example.test' } })
    fireEvent.change(screen.getByLabelText('模型 ID'), { target: { value: 'test-model' } })
    fireEvent.change(screen.getByLabelText(protocol === 'openai' ? 'API Key' : '服务密码'), { target: { value: 'test-secret' } })
    fireEvent.click(screen.getByRole('button', { name: '保存并使用' }))
    await waitFor(() => expect(Backend.ConfigureProvider).toHaveBeenCalledOnce())
    const config = vi.mocked(Backend.ConfigureProvider).mock.calls[0][2]
    expect(config.provider).toBe(provider)
    expect(config.rwkvStopTokens).toBe(stops)
    expect(protocol === 'openai' ? config.apiKey : config.password).toBe('test-secret')
    expect(config.agentProtocol).toBe('xml')
  })

  it('passes web credentials and concurrent subagent budgets through auto-apply', async () => {
    bootstrapWithRunningProvider()
    render(<App />)
    await waitRuntimeReady()
    openSettings()
    openAgentSection()
    fireEvent.click(screen.getByLabelText('网页搜索与正文获取'))
    fireEvent.change(screen.getByLabelText('Brave API Key'), { target: { value: 'brave-secret' } })
    fireEvent.change(screen.getByLabelText('Tavily API Key'), { target: { value: 'tavily-secret' } })
    fireEvent.click(screen.getByLabelText('并发子 Agent'))
    fireEvent.change(screen.getByLabelText('活动批量'), { target: { value: '6' } })
    fireEvent.change(screen.getByLabelText('子 Agent 并发'), { target: { value: '6' } })
    fireEvent.change(screen.getByLabelText('单 Agent 步数'), { target: { value: '5' } })
    fireEvent.change(screen.getByLabelText('批次超时（秒）'), { target: { value: '180' } })
    fireEvent.change(screen.getByLabelText('远端聚合窗口（毫秒）'), { target: { value: '15' } })

    await waitFor(() => expect(Backend.ConfigureProvider).toHaveBeenCalled(), { timeout: 3000 })
    const config = vi.mocked(Backend.ConfigureProvider).mock.calls[0][2]
    expect(config).toMatchObject({
      enableWeb: true,
      braveApiKey: 'brave-secret',
      tavilyApiKey: 'tavily-secret',
      enableSubagents: true,
      maxActiveBatch: 6,
      remoteBatchWaitMs: 15,
      subagentMaxParallel: 6,
      subagentMaxSteps: 5,
      subagentTimeoutSeconds: 180,
    })
    expect(await screen.findByText('已自动生效')).toBeInTheDocument()
  })

  it('allows the Markdown protocol to be selected explicitly', async () => {
    bootstrapWithRunningProvider()
    render(<App />)
    await waitRuntimeReady()
    openSettings()
    openParametersSection()
    fireEvent.change(screen.getByLabelText('工具协议'), { target: { value: 'markdown' } })

    await waitFor(() => expect(Backend.ConfigureProvider).toHaveBeenCalled(), { timeout: 3000 })
    expect(vi.mocked(Backend.ConfigureProvider).mock.calls[0][2].agentProtocol).toBe('markdown')
  })

  it('submits the selected thinking mode through auto-apply', async () => {
    bootstrapWithRunningProvider()
    render(<App />)
    await waitRuntimeReady()
    openSettings()
    openParametersSection()
    fireEvent.change(screen.getByLabelText('思考模式'), { target: { value: 'fast' } })

    await waitFor(() => expect(Backend.ConfigureProvider).toHaveBeenCalled(), { timeout: 3000 })
    expect(vi.mocked(Backend.ConfigureProvider).mock.calls[0][2].thinking).toBe('fast')
  })

  it('submits the personal task contract through auto-apply', async () => {
    bootstrapWithRunningProvider()
    render(<App />)
    await waitRuntimeReady()
    openSettings()
    openParametersSection()
    fireEvent.change(screen.getByLabelText('附加任务约定'), { target: { value: '  回答使用中文。  ' } })

    await waitFor(() => expect(Backend.ConfigureProvider).toHaveBeenCalled(), { timeout: 3000 })
    expect(vi.mocked(Backend.ConfigureProvider).mock.calls[0][2].taskControl).toBe('回答使用中文。')
  })

  it('auto-saves a non-running profile without reconnecting', async () => {
    const provider = bootstrapWithRunningProvider()
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
    }))
    render(<App />)
    await waitRuntimeReady()
    openSettings()
    openParametersSection()
    fireEvent.change(screen.getByLabelText('思考模式'), { target: { value: 'fast' } })

    await waitFor(() => expect(Backend.SaveProvider).toHaveBeenCalled(), { timeout: 3000 })
    expect(Backend.ConfigureProvider).not.toHaveBeenCalled()
    expect(await screen.findByText('已自动保存')).toBeInTheDocument()
  })

  it('previews the system prompt in the parameters section', async () => {
    vi.mocked(Backend.PreviewSystemPrompt).mockResolvedValue(new AgentPromptPreview({
      control: 'You are a local-first assistant with read-only tools.',
      responseControl: '',
      toolNames: ['list_files', 'datetime'],
      protocolId: 'rwkv-g1-envelope-v1',
      rendererId: 'rwkv-chat-continuation-v2',
      thinkingMode: 'off',
      native: false,
    }))
    render(<App />)
    openSettings()
    switchToRemoteProvider()
    openParametersSection()
    // 预览默认展开：设置页打开即按当前草稿拉取。
    expect(screen.getByRole('button', { name: '预览系统提示词' })).toHaveTextContent('收起')

    expect(await screen.findByText(/You are a local-first assistant/)).toBeInTheDocument()
    expect(screen.getByText(/协议 rwkv-g1-envelope-v1/)).toBeInTheDocument()
    expect(screen.getByText(/工具 2 项/)).toBeInTheDocument()
  })

  it('resets the thinking mode when the Markdown protocol is selected', async () => {    render(<App />)
    openSettings()
    switchToRemoteProvider()
    openParametersSection()
    fireEvent.change(screen.getByLabelText('思考模式'), { target: { value: 'fast' } })
    expect(screen.getByLabelText('思考模式')).toHaveValue('fast')
    fireEvent.change(screen.getByLabelText('工具协议'), { target: { value: 'markdown' } })

    expect(screen.getByLabelText('思考模式')).toHaveValue('off')
    expect(screen.getByLabelText('思考模式')).toBeDisabled()
  })

  it('applies a named sampling preset through auto-apply', async () => {
    bootstrapWithRunningProvider()
    render(<App />)
    await waitRuntimeReady()
    openSettings()
    openParametersSection()
    // 档案没存过采样，后端会归一成 greedy，选择器应当认出它而不是报自定义。
    expect(screen.getByLabelText('采样预设')).toHaveValue('greedy')
    fireEvent.change(screen.getByLabelText('采样预设'), { target: { value: 'g1k-agent' } })

    await waitFor(() => expect(Backend.ConfigureProvider).toHaveBeenCalled(), { timeout: 3000 })
    expect(vi.mocked(Backend.ConfigureProvider).mock.calls[0][2]).toMatchObject({
      temperature: 0.3, topK: 65536, topP: 0.5,
      presencePenalty: 0, frequencyPenalty: 0, penaltyDecay: 1,
    })
  })

  it('drops to custom sampling once a preset value is overridden', async () => {
    bootstrapWithRunningProvider()
    render(<App />)
    await waitRuntimeReady()
    openSettings()
    openParametersSection()
    // 预设模式下六个数字是只读的展示，不占编辑位。
    expect(screen.queryByLabelText('温度')).not.toBeInTheDocument()
    fireEvent.change(screen.getByLabelText('采样预设'), { target: { value: 'g1k-agent' } })
    fireEvent.change(screen.getByLabelText('采样预设'), { target: { value: 'custom' } })
    // 切到自定义不改数值，从预设那组值出发继续调。
    expect(screen.getByLabelText('温度')).toHaveValue(0.3)
    // 下拉说自定义时说明文字不能说成"选中了预设"。
    expect(screen.getByText(/当前数值等同 g1k-agent/)).toBeInTheDocument()
    fireEvent.change(screen.getByLabelText('温度'), { target: { value: '0.9' } })

    // 改过的配置不再冒充预设名。
    expect(screen.getByLabelText('采样预设')).toHaveValue('custom')
    expect(screen.getByText(/六个参数直接决定采样/)).toBeInTheDocument()
    await waitFor(() => expect(Backend.ConfigureProvider).toHaveBeenCalled(), { timeout: 3000 })
    expect(vi.mocked(Backend.ConfigureProvider).mock.calls[0][2]).toMatchObject({ temperature: 0.9, topK: 65536, topP: 0.5 })
  })

  it('opens a profile with non-preset sampling in custom mode', async () => {
    const provider = savedRemoteProvider({ temperature: 0.7, topK: 40, topP: 0.8, penaltyDecay: 0.98 })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      config: provider.config,
      hasConfig: true,
      providers: [provider],
      activeProviderId: provider.id,
      runtimeProviderId: provider.id,
    }))

    render(<App />)
    await waitFor(() => expect(Backend.Bootstrap).toHaveBeenCalledOnce())
    openSettings()
    openParametersSection()

    expect(screen.getByLabelText('采样预设')).toHaveValue('custom')
    expect(screen.getByLabelText('温度')).toHaveValue(0.7)
    expect(screen.getByLabelText('top-k 截断')).toHaveValue(40)
  })

  it('passes the generation budget through auto-apply', async () => {
    bootstrapWithRunningProvider()
    render(<App />)
    await waitRuntimeReady()
    openSettings()
    openParametersSection()
    expect(screen.getByLabelText('最大步数')).toHaveValue(6)
    expect(screen.getByLabelText('最大输出 token')).toHaveValue(1024)
    fireEvent.change(screen.getByLabelText('最大步数'), { target: { value: '16' } })
    fireEvent.change(screen.getByLabelText('最大输出 token'), { target: { value: '4096' } })
    fireEvent.change(screen.getByLabelText('决策输出 token'), { target: { value: '2048' } })

    await waitFor(() => expect(Backend.ConfigureProvider).toHaveBeenCalled(), { timeout: 3000 })
    expect(vi.mocked(Backend.ConfigureProvider).mock.calls[0][2]).toMatchObject({
      maxSteps: 16, maxTokens: 4096, decisionMaxTokens: 2048,
    })
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

    render(<App />)
    openSettings()
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
    expect(await screen.findByText('档案已保存，尚未连接。')).toBeInTheDocument()
  })

  it('marks edited fields as an unsaved draft', async () => {
    render(<App />)
    openSettings()
    fireEvent.change(screen.getByLabelText('连接名称'), { target: { value: 'Unsaved connection' } })

    expect(await screen.findByText('未保存更改')).toBeInTheDocument()
  })

  it('keeps the running badge on the list row while editing another profile', async () => {
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

    render(<App />)
    await waitFor(() => expect(Backend.Bootstrap).toHaveBeenCalledOnce())
    openSettings()
    fireEvent.click(screen.getByRole('button', { name: /^Backup connection/ }))

    expect(screen.getByLabelText('连接名称')).toHaveValue('Backup connection')
    expect(screen.getByText('当前运行：').parentElement).toHaveTextContent('Runtime connection')
    expect(screen.getByText('运行中')).toBeInTheDocument()
    expect(screen.getByText('已保存')).toBeInTheDocument()
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

    render(<App />)
    await waitFor(() => expect(Backend.Bootstrap).toHaveBeenCalledOnce())
    openSettings()
    fireEvent.change(screen.getByLabelText('模型 ID'), { target: { value: 'edited-model' } })
    fireEvent.click(screen.getByRole('button', { name: /^Second connection/ }))

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

    render(<App />)
    await waitFor(() => expect(Backend.Bootstrap).toHaveBeenCalledOnce())
    openSettings()
    fireEvent.change(screen.getByLabelText('API 地址'), { target: { value: 'not a url' } })
    expect(screen.getByLabelText('API 地址')).toHaveAttribute('aria-invalid', 'true')
    expect(screen.getByText('API 地址必须是 http:// 或 https:// 开头的完整地址')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /^Second connection/ }))

    const dialog = await screen.findByRole('dialog', { name: '有未保存的更改' })
    expect(within(dialog).queryByRole('button', { name: '保存' })).not.toBeInTheDocument()
    fireEvent.click(within(dialog).getByRole('button', { name: '放弃更改' }))
    expect(await screen.findByLabelText('连接名称')).toHaveValue('Second connection')
    expect(Backend.SaveProvider).not.toHaveBeenCalled()
  })

  it('still confirms leaving an unsaved new connection and can save it from the dialog', async () => {
    const created = savedRemoteProvider({ endpoint: 'https://new.example.test', model: 'new-model' }, { id: 'created', label: 'New one' })
    vi.mocked(Backend.SaveProvider).mockResolvedValue(created)
    render(<App />)
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
  it('activates a saved provider from the connection list', async () => {
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

    render(<App />)
    await waitFor(() => expect(Backend.Bootstrap).toHaveBeenCalledOnce())
    openSettings()
    fireEvent.click(screen.getByRole('button', { name: '使用' }))

    await waitFor(() => expect(Backend.ActivateProvider).toHaveBeenCalledOnce())
    expect(vi.mocked(Backend.ActivateProvider).mock.calls[0][0]).toBe('p1')
  })

  it('closes the run config dropdown when its chip is clicked again', async () => {
    bootstrapWithRunningProvider()

    render(<App />)
    const chip = await screen.findByRole('button', { name: /rwkv7-test/ })
    fireEvent.mouseDown(chip); fireEvent.click(chip)
    expect(screen.getByText('当前运行')).toBeInTheDocument()
    // 真实点击的顺序：mousedown（面板的点击外部关闭）先于 click（芯片的开合切换）。
    fireEvent.mouseDown(chip); fireEvent.click(chip)
    // 收起动画播完才卸载。
    await waitFor(() => expect(screen.queryByText('当前运行')).not.toBeInTheDocument())
  })

  it('toggles a capability of the running remote profile from the run config dropdown', async () => {
    const runtime = bootstrapWithRunningProvider({ enableWeb: true, enableSubagents: true }, { id: 'runtime-provider', label: 'Runtime connection' })

    render(<App />)
    fireEvent.click(await screen.findByRole('button', { name: /rwkv7-test/ }))
    const web = screen.getByRole('switch', { name: '网页搜索' })
    expect(web).toHaveAttribute('aria-checked', 'true')
    fireEvent.click(web)

    await waitFor(() => expect(Backend.ConfigureProvider).toHaveBeenCalledOnce())
    const [id, label, config] = vi.mocked(Backend.ConfigureProvider).mock.calls[0]
    expect([id, label]).toEqual([runtime.id, 'Runtime connection'])
    expect(config.enableWeb).toBe(false)
    expect(config.enableSubagents).toBe(true)
    expect(config.endpoint).toBe(runtime.config.endpoint)
  })

  it('derives the capability indicator from the running config and applies toggles on close', async () => {
    const runtime = bootstrapWithRunningProvider({ enableWeb: true, enableSubagents: true }, { id: 'runtime-provider', label: 'Runtime connection' })

    render(<App />)
    expect(await screen.findByTitle(/能力：web · subagents/)).toBeInTheDocument()
    openSettings()
    openAgentSection()
    fireEvent.click(screen.getByLabelText('网页搜索与正文获取'))
    expect(screen.getByLabelText('网页搜索与正文获取')).not.toBeChecked()
    // 草稿改了但还没生效：头部能力仍是运行中的配置。
    expect(Backend.ConfigureProvider).not.toHaveBeenCalled()

    // 后端应用后的状态：运行配置不再含 web。
    const applied = new Config({ ...runtime.config, enableWeb: false })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      status: readyStatus(), config: applied, hasConfig: true,
      providers: [new SavedProvider({ ...runtime, config: applied })],
      activeProviderId: runtime.id, runtimeProviderId: runtime.id,
    }))
    // Esc 不再弹"放弃更改"：待保存的更改立即落盘并生效，然后返回对话。
    fireEvent.keyDown(window, { key: 'Escape' })
    await waitFor(() => expect(Backend.ConfigureProvider).toHaveBeenCalledOnce())
    expect(vi.mocked(Backend.ConfigureProvider).mock.calls[0][2].enableWeb).toBe(false)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(await screen.findByTitle(/能力：subagents$/)).toBeInTheDocument()
  })
  it('closes via Escape with confirmation when the draft is dirty', async () => {
    render(<App />)
    openSettings()
    fireEvent.change(screen.getByLabelText('连接名称'), { target: { value: 'Esc draft' } })

    fireEvent.keyDown(window, { key: 'Escape' })
    expect(await screen.findByRole('dialog', { name: '有未保存的更改' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: '放弃更改' }))
    await waitFor(() => expect(screen.queryByLabelText('连接名称')).not.toBeInTheDocument())
  })

  it('keeps an auto-derived name in sync with the model in the list and on save', async () => {
    const provider = bootstrapWithRunningProvider({}, { label: 'saved-model · saved.example.test' })
    render(<App />)
    await waitRuntimeReady()
    openSettings()
    expect(screen.getByLabelText('连接名称')).toHaveValue('')
    fireEvent.change(screen.getByLabelText('模型 ID'), { target: { value: 'next-model' } })
    expect(screen.getByRole('button', { name: /^next-model · saved\.example\.test/ })).toBeInTheDocument()
    await waitFor(() => expect(Backend.SaveProvider).toHaveBeenCalledOnce(), { timeout: 3000 })
    // 空名称交给后端按新模型重新派生。
    expect(vi.mocked(Backend.SaveProvider).mock.calls[0][0]).toBe(provider.id)
    expect(vi.mocked(Backend.SaveProvider).mock.calls[0][1]).toBe('')
  })

  it('applies connection edits to the running remote profile without a save button', async () => {
    const provider = bootstrapWithRunningProvider()
    render(<App />)
    await waitRuntimeReady()
    openSettings()
    expect(screen.queryByRole('button', { name: '保存' })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: '使用中' })).toBeDisabled()

    fireEvent.change(screen.getByLabelText('模型 ID'), { target: { value: 'rwkv-live-edit' } })
    // 列表行立即跟随草稿，不等落盘。
    expect(screen.getByRole('button', { name: /^Saved connection/ })).toHaveTextContent('Saved connection')
    expect(screen.getByText('待保存…')).toBeInTheDocument()

    await waitFor(() => expect(Backend.ConfigureProvider).toHaveBeenCalledOnce(), { timeout: 3000 })
    expect(Backend.SaveProvider).toHaveBeenCalledOnce()
    expect(vi.mocked(Backend.SaveProvider).mock.calls[0][0]).toBe(provider.id)
    expect(vi.mocked(Backend.ConfigureProvider).mock.calls[0][2].model).toBe('rwkv-live-edit')
    expect(await screen.findByText('已自动生效')).toBeInTheDocument()
  })

  it('renames a running profile without reconnecting and shows the new name in the list', async () => {
    bootstrapWithRunningProvider()
    render(<App />)
    await waitRuntimeReady()
    openSettings()
    fireEvent.change(screen.getByLabelText('连接名称'), { target: { value: 'Renamed connection' } })
    expect(screen.getByRole('button', { name: /^Renamed connection/ })).toBeInTheDocument()

    await waitFor(() => expect(Backend.SaveProvider).toHaveBeenCalledOnce(), { timeout: 3000 })
    expect(vi.mocked(Backend.SaveProvider).mock.calls[0][1]).toBe('Renamed connection')
    expect(Backend.ConfigureProvider).not.toHaveBeenCalled()
  })

  it('does not auto-save an invalid endpoint and explains why', async () => {
    bootstrapWithRunningProvider()
    render(<App />)
    await waitRuntimeReady()
    openSettings()
    fireEvent.change(screen.getByLabelText('API 地址'), { target: { value: 'https://user:pw@host.test' } })
    expect(await screen.findByText(/未保存：API 地址不能内嵌账号密码/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '使用此连接' })).toBeDisabled()
    await new Promise((resolve) => setTimeout(resolve, 1000))
    expect(Backend.SaveProvider).not.toHaveBeenCalled()
    expect(Backend.ConfigureProvider).not.toHaveBeenCalled()
  })

  it('surfaces a rejected auto-save and does not retry the same draft', async () => {
    bootstrapWithRunningProvider()
    vi.mocked(Backend.SaveProvider).mockRejectedValue(new Error('another provider profile already uses this provider, endpoint, and model'))
    render(<App />)
    await waitRuntimeReady()
    openSettings()
    fireEvent.change(screen.getByLabelText('模型 ID'), { target: { value: 'duplicate-model' } })
    expect(await screen.findByText(/保存失败：another provider profile/, undefined, { timeout: 3000 })).toBeInTheDocument()
    await new Promise((resolve) => setTimeout(resolve, 1000))
    expect(Backend.SaveProvider).toHaveBeenCalledOnce()
    expect(Backend.ConfigureProvider).not.toHaveBeenCalled()
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
    render(<App />)
    await waitRuntimeReady()
    openSettings()
    expect(screen.getByText('运行中 · 待重新加载')).toBeInTheDocument()
    expect(screen.getByText(/本地模型仍在用旧配置运行/)).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: '重新加载模型' }))
    await waitFor(() => expect(Backend.ConfigureProvider).toHaveBeenCalledOnce())
    expect(vi.mocked(Backend.ConfigureProvider).mock.calls[0][0]).toBe('local-provider')
    expect(vi.mocked(Backend.ConfigureProvider).mock.calls[0][2].model).toBe('/models/new.pth')
  })

  it('refreshes the provider list when the backend announces a change', async () => {
    render(<App />)
    await waitFor(() => expect(Backend.Bootstrap).toHaveBeenCalledOnce())
    fireEvent.click(screen.getByRole('button', { name: /运行配置|选择模型/ }))
    expect(screen.getByText('尚无保存的连接，去设置里连接一次即可记住')).toBeInTheDocument()

    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({ providers: [savedRemoteProvider({}, { label: 'Pushed connection' })] }))
    await act(async () => { eventHandlers.get('providers:changed')?.({ data: undefined }) })
    expect(await screen.findByText('Pushed connection')).toBeInTheDocument()
  })

  it('stops a running turn from the composer', async () => {
    bootstrapWithRunningProvider()
    const cancel = vi.fn()
    let reject: (reason: unknown) => void = () => {}
    const pending = new Promise<Result>((_, rejectRun) => { reject = rejectRun }) as Promise<Result> & { cancel: () => void }
    pending.cancel = () => { cancel(); reject(new Error('cancelled')) }
    vi.mocked(Backend.Chat).mockReturnValue(pending as unknown as ReturnType<typeof Backend.Chat>)

    render(<App />)
    await waitRuntimeReady()
    fireEvent.change(screen.getByLabelText('消息'), { target: { value: 'long task' } })
    fireEvent.click(screen.getByRole('button', { name: '发送' }))
    const stop = await screen.findByRole('button', { name: '停止运行' })
    fireEvent.click(stop)

    expect(cancel).toHaveBeenCalledOnce()
    expect(await screen.findByRole('button', { name: '发送' })).toBeInTheDocument()
  })

  it('closes a conversation menu when its own button is clicked again', async () => {
    const conversation = new ConversationSummary({ id: 'c1', title: '检查项目', updatedAt: new Date().toISOString(), pinned: false })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({ conversations: [conversation] }))
    render(<App />)
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
    render(<SnackbarProvider><App /></SnackbarProvider>)
    fireEvent.click(await screen.findByTitle('Broken'))
    expect(await screen.findByText('conversation belongs to another workspace')).toBeInTheDocument()
  })

  it('preserves an explicitly saved Markdown and Router selection', async () => {
    const provider = savedRemoteProvider({
      agentProtocol: AgentProtocol.AgentProtocolMarkdown,
      progressiveTools: true,
    })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      config: provider.config,
      hasConfig: true,
      providers: [provider],
      activeProviderId: provider.id,
      runtimeProviderId: provider.id,
    }))

    render(<App />)
    await waitFor(() => expect(Backend.Bootstrap).toHaveBeenCalledOnce())
    openSettings()
    openParametersSection()

    expect(screen.getByLabelText('工具协议')).toHaveValue('markdown')
    openAgentSection()
    expect(screen.getByLabelText('渐进式工具路由')).toBeChecked()
  })

  it('hydrates saved provider settings and plaintext credentials', async () => {
    const provider = savedRemoteProvider({
      password: 'saved-password',
      headers: { 'X-Service-Key': 'saved-header' },
      enableWeb: true,
      braveApiKey: 'saved-brave',
      tavilyApiKey: 'saved-tavily',
    })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      config: provider.config,
      hasConfig: true,
      providers: [provider],
      activeProviderId: provider.id,
      runtimeProviderId: provider.id,
    }))

    render(<App />)
    await waitFor(() => expect(Backend.Bootstrap).toHaveBeenCalledOnce())
    openSettings()

    expect(screen.getByLabelText('API 地址')).toHaveValue('https://saved.example.test')
    expect(screen.getByLabelText('模型 ID')).toHaveValue('saved-model')
    expect(screen.getByLabelText(/服务密码/)).toHaveValue('saved-password')
    expect(screen.getByLabelText('Header 名称')).toHaveValue('X-Service-Key')
    expect(screen.getByLabelText('Header 值')).toHaveValue('saved-header')
    expect(screen.getByLabelText('Header 值')).toHaveAttribute('type', 'password')

    openParametersSection()
    expect(screen.getByLabelText('工具协议')).toHaveValue('xml')
    openAgentSection()
    expect(screen.getByLabelText('渐进式工具路由')).not.toBeChecked()
    expect(screen.getByLabelText('Brave API Key')).toHaveValue('saved-brave')
    expect(screen.getByLabelText('Tavily API Key')).toHaveValue('saved-tavily')
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

    render(<App />)
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

    render(<App />)
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

    render(<App />)
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

    render(<App />)
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

    render(<App />)
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

    const { container } = render(<App />)
    const composer = await screen.findByLabelText('消息')
    fireEvent.change(composer, { target: { value: '打个招呼' } })
    fireEvent.keyDown(composer, { key: 'Enter' })
    await waitFor(() => expect(Backend.Chat).toHaveBeenCalledOnce())
    expect(screen.getByTestId('conversation-turn-1')).toHaveClass('turn-enter')

    act(() => { eventHandlers.get('agent:event')?.({ data: { kind: 'answer_delta', step: 1, text: '你好世界' } }) })
    await act(async () => { resolveChat(new Result({ output: '你好世界', steps: [], durationMs: 1 })) })
    // 匀速放完后交回普通渲染。
    await waitFor(() => {
      expect(screen.getByText('你好世界')).toBeInTheDocument()
      expect(container.querySelector('.stream-tok')).toBeNull()
    })

    fireEvent.click(screen.getByRole('tab', { name: /轨迹/ }))
    fireEvent.click(screen.getByRole('tab', { name: '对话' }))

    expect(screen.getByTestId('conversation-turn-1')).not.toHaveClass('turn-enter')
    expect(container.querySelector('.answer-reveal, .stream-tok')).toBeNull()
    expect(screen.getByText('你好世界')).toBeInTheDocument()
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
    render(<App />)
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

    render(<App />)
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

    render(<App />)
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

    render(<App />)
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

    render(<App />)
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

  it('closes the navigation drawer after opening a conversation', async () => {
    const summary = new ConversationSummary({ id: 'drawer-conversation', title: '抽屉会话', updatedAt: new Date().toISOString() })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({ conversations: [summary] }))
    vi.mocked(Backend.OpenConversation).mockResolvedValue(new ConversationView({ id: summary.id, title: summary.title, messages: [] }))

    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: '打开导航' }))
    expect(document.querySelector('.sidebar-scrim')).not.toBeNull()
    fireEvent.click(await screen.findByRole('button', { name: /^抽屉会话/ }))

    await waitFor(() => expect(Backend.OpenConversation).toHaveBeenCalledWith('drawer-conversation'))
    expect(document.querySelector('.sidebar-scrim')).toBeNull()
  })

})
