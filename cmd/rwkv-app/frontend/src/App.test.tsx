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
      provider: Provider.ProviderRWKVLightning,
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

/* 工具协议、思考模式、网页与子 Agent 字段在设置页的 Agent 分区。 */
function openAgentSection() {
  openSettingsSection('Agent')
}

const readyStatus = () => new Status({
  state: ModelState.ModelReady,
  provider: Provider.ProviderRWKVLightning,
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
      provider: Provider.ProviderRWKVLightning,
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
    protocolId: 'rwkv-g1i-envelope-v1',
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

    const modelChipSelector = `button[title="${model}"]`
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
      provider: Provider.ProviderRWKVLightning,
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
    expect(config.provider).toBe('rwkv-lightning')
    expect(config.rwkvStopTokens).toBe('none')
    expect(config.stream).toBe(false)
    expect(config.headers).toEqual({ 'CF-Access-Client-Id': 'secret' })
    expect(config.agentProtocol).toBe('xml')
    expect(config.progressiveTools).toBe(false)
    expect(config.enableSubagents).toBe(false)
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
    openAgentSection()
    fireEvent.change(screen.getByLabelText('工具协议'), { target: { value: 'markdown' } })

    await waitFor(() => expect(Backend.ConfigureProvider).toHaveBeenCalled(), { timeout: 3000 })
    expect(vi.mocked(Backend.ConfigureProvider).mock.calls[0][2].agentProtocol).toBe('markdown')
  })

  it('submits the selected thinking mode through auto-apply', async () => {
    bootstrapWithRunningProvider()
    render(<App />)
    await waitRuntimeReady()
    openSettings()
    openAgentSection()
    fireEvent.change(screen.getByLabelText('思考模式'), { target: { value: 'fast' } })

    await waitFor(() => expect(Backend.ConfigureProvider).toHaveBeenCalled(), { timeout: 3000 })
    expect(vi.mocked(Backend.ConfigureProvider).mock.calls[0][2].thinking).toBe('fast')
  })

  it('submits the personal task contract through auto-apply', async () => {
    bootstrapWithRunningProvider()
    render(<App />)
    await waitRuntimeReady()
    openSettings()
    openAgentSection()
    fireEvent.change(screen.getByLabelText('附加任务约定'), { target: { value: '  回答使用中文。  ' } })

    await waitFor(() => expect(Backend.ConfigureProvider).toHaveBeenCalled(), { timeout: 3000 })
    expect(vi.mocked(Backend.ConfigureProvider).mock.calls[0][2].taskControl).toBe('回答使用中文。')
  })

  it('auto-saves a non-running profile without reconnecting', async () => {
    const provider = bootstrapWithRunningProvider()
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      status: new Status({
        state: ModelState.ModelReady,
        provider: Provider.ProviderRWKVLightning,
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
    openAgentSection()
    fireEvent.change(screen.getByLabelText('思考模式'), { target: { value: 'fast' } })

    await waitFor(() => expect(Backend.SaveProvider).toHaveBeenCalled(), { timeout: 3000 })
    expect(Backend.ConfigureProvider).not.toHaveBeenCalled()
    expect(await screen.findByText('已自动保存')).toBeInTheDocument()
  })

  it('previews the system prompt in the Agent section', async () => {
    vi.mocked(Backend.PreviewSystemPrompt).mockResolvedValue(new AgentPromptPreview({
      control: 'You are a local-first assistant with read-only tools.',
      responseControl: '',
      toolNames: ['list_files', 'datetime'],
      protocolId: 'rwkv-g1i-envelope-v1',
      rendererId: 'rwkv-chat-continuation-v2',
      thinkingMode: 'off',
      native: false,
    }))
    render(<App />)
    openSettings()
    switchToRemoteProvider()
    openAgentSection()
    // 预览默认展开：设置页打开即按当前草稿拉取。
    expect(screen.getByRole('button', { name: '预览系统提示词' })).toHaveTextContent('收起')

    expect(await screen.findByText(/You are a local-first assistant/)).toBeInTheDocument()
    expect(screen.getByText(/协议 rwkv-g1i-envelope-v1/)).toBeInTheDocument()
    expect(screen.getByText(/工具 2 项/)).toBeInTheDocument()
  })

  it('resets the thinking mode when the Markdown protocol is selected', async () => {    render(<App />)
    openSettings()
    switchToRemoteProvider()
    openAgentSection()
    fireEvent.change(screen.getByLabelText('思考模式'), { target: { value: 'fast' } })
    expect(screen.getByLabelText('思考模式')).toHaveValue('fast')
    fireEvent.change(screen.getByLabelText('工具协议'), { target: { value: 'markdown' } })

    expect(screen.getByLabelText('思考模式')).toHaveValue('off')
    expect(screen.getByLabelText('思考模式')).toBeDisabled()
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
        provider: Provider.ProviderRWKVLightning,
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

  it('asks for confirmation when switching away from a dirty draft and applies the choice', async () => {
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
    fireEvent.change(screen.getByLabelText('模型 ID'), { target: { value: 'edited-model' } })
    fireEvent.click(screen.getByRole('button', { name: /^Second connection/ }))

    expect(screen.getByLabelText('连接名称')).toHaveValue('First connection')
    const dialog = await screen.findByRole('dialog', { name: '有未保存的更改' })
    expect(dialog).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: '放弃更改' }))
    expect(await screen.findByLabelText('连接名称')).toHaveValue('Second connection')
    expect(Backend.SaveProvider).not.toHaveBeenCalled()
  })

  it('saves through the confirm dialog when switching profiles', async () => {
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
    const dialog = await screen.findByRole('dialog', { name: '有未保存的更改' })
    fireEvent.click(within(dialog).getByRole('button', { name: '保存' }))

    await waitFor(() => expect(Backend.SaveProvider).toHaveBeenCalledOnce())
    expect(vi.mocked(Backend.SaveProvider).mock.calls[0][0]).toBe('first-provider')
    expect(await screen.findByLabelText('连接名称')).toHaveValue('Second connection')
  })

  it('activates a saved provider from the connection list', async () => {
    const provider = savedRemoteProvider({}, { id: 'p1', label: 'Solo connection' })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      providers: [provider],
      activeProviderId: provider.id,
    }))
    vi.mocked(Backend.ActivateProvider).mockResolvedValue(new Status({
      state: ModelState.ModelReady,
      provider: Provider.ProviderRWKVLightning,
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

  it('derives the capability indicator from the running profile, not the draft', async () => {
    const runtime = savedRemoteProvider({ enableWeb: true, enableSubagents: true }, { id: 'runtime-provider', label: 'Runtime connection' })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      status: new Status({
        state: ModelState.ModelReady,
        provider: Provider.ProviderRWKVLightning,
        endpoint: runtime.config.endpoint,
        model: runtime.config.model,
        workspace: '/tmp/RWKV-Agent',
        hasApiKey: false,
        updatedAt: new Date().toISOString(),
      }),
      config: runtime.config,
      hasConfig: true,
      providers: [runtime],
      activeProviderId: runtime.id,
      runtimeProviderId: runtime.id,
    }))

    render(<App />)
    expect((await screen.findAllByText('web · subagents')).length).toBeGreaterThan(0)
    openSettings()
    openAgentSection()
    fireEvent.click(screen.getByLabelText('网页搜索与正文获取'))
    expect(screen.getByLabelText('网页搜索与正文获取')).not.toBeChecked()

    fireEvent.keyDown(window, { key: 'Escape' })
    fireEvent.click(await screen.findByRole('button', { name: '放弃更改' }))
    expect((await screen.findAllByText('web · subagents')).length).toBeGreaterThan(0)
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
    openAgentSection()

    expect(screen.getByLabelText('工具协议')).toHaveValue('markdown')
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

    openAgentSection()
    expect(screen.getByLabelText('工具协议')).toHaveValue('xml')
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

  it('reopens a saved conversation and shows subagent cards', async () => {
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
    expect(screen.getByText('检查官方文档')).toBeInTheDocument()
    expect(screen.queryByText('{"urls":["https://example.test/docs"]}')).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: '查看轨迹' }))
    expect(screen.getAllByText('spawn_agents').length).toBeGreaterThan(0)
    expect(screen.getAllByText('read_file').length).toBeGreaterThan(0)
    fireEvent.click(screen.getByRole('button', { name: /spawn_agents/ }))
    fireEvent.click(screen.getByRole('tab', { name: '原文' }))
    expect(screen.getByText(/legacySubagents/)).toHaveTextContent('检查官方文档')
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
    // 生成期间正文栏保持干净：工具参数与子任务详情不再出现在对话中央
    expect(screen.queryByText('{"query":"RWKV"}')).not.toBeInTheDocument()
    expect(screen.queryByText('检查文档')).not.toBeInTheDocument()
    // 运行状态只在左侧页边栏以缩略标签呈现
    expect(screen.getByText(/调用 spawn_agents/)).toBeInTheDocument()
    expect(screen.getByText(/工具重试 · web_search/)).toBeInTheDocument()
    expect(screen.getAllByText(/子 Agent 1/).length).toBeGreaterThan(0)

    await act(async () => {
      resolveChat(new Result({ output: 'done', steps: [], duration: 0, durationMs: 1 }))
    })
    await waitFor(() => expect(screen.getByTestId('conversation-turn-1')).not.toHaveClass('pending'))
    expect(screen.getAllByTestId(/conversation-turn-/)).toHaveLength(1)
    expect(screen.getByText('done')).toBeInTheDocument()
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

    expect((screen.getAllByText('输入')).length).toBeGreaterThan(0)
    expect((screen.getAllByText('模型')).length).toBeGreaterThan(0)
    expect((screen.getAllByText('工具')).length).toBeGreaterThan(0)
    expect(screen.getAllByText('读取 README').length).toBeGreaterThan(0)

    fireEvent.click(screen.getByRole('button', { name: /Step 1 · 决策/ }))
    fireEvent.click(screen.getByRole('tab', { name: '请求' }))
    expect((screen.getAllByText(/读取 README/)).length).toBeGreaterThan(0)

    // 调用默认折叠：先展开再点工具记录
    fireEvent.click(screen.getByRole('button', { name: '调用' }))
    fireEvent.click(screen.getByRole('button', { name: /read_file/ }))
    fireEvent.click(screen.getByRole('tab', { name: '参数' }))
    expect(screen.getByText(/README\.md/)).toBeInTheDocument()
    fireEvent.click(screen.getByRole('tab', { name: '结果' }))
    expect((screen.getAllByText(/# RWKV Agent/)).length).toBeGreaterThan(0)

    fireEvent.click(screen.getByRole('button', { name: '导出 trace.jsonl' }))
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
    expect(screen.getByText('TURN 1')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /read_file/ })).toBeInTheDocument()
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
    expect((screen.getAllByText(/用户输入/)).length).toBeGreaterThan(0)
    expect((screen.getAllByText(/模型服务返回 503/)).length).toBeGreaterThan(0)
    fireEvent.click(screen.getByRole('button', { name: /Step 1 · 决策/ }))
    fireEvent.click(screen.getByRole('tab', { name: '原文' }))
    expect(screen.getByText(/modelError/)).toHaveTextContent('模型服务返回 503')
  })



  it('toggles the raw tab between formatted and JSON views', async () => {
    const trace = new Result({
      output: '完成',
      steps: [
        { number: 1, stage: 'tool', request: { prompt: '带换行的请求\n第二行内容', bytes: 30 }, tool: 'web_search', toolArguments: '{"query":"x"}', toolResult: 'ok', toolExecuted: true, usage: {} },
      ],
      durationMs: 100,
    })
    const summary = new ConversationSummary({ id: 'raw-conversation', title: '原文验证', updatedAt: new Date().toISOString() })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({ conversations: [summary] }))
    vi.mocked(Backend.OpenConversation).mockResolvedValue(new ConversationView({
      id: summary.id,
      title: summary.title,
      messages: [
        new DisplayMessage({ id: 'raw-user', role: 'user', content: '带换行的请求\n第二行内容' }),
        new DisplayMessage({ id: 'raw-assistant', role: 'assistant', content: '完成', trace }),
      ],
    }))

    render(<App />)
    fireEvent.click(await screen.findByTitle('原文验证'))
    expect(await screen.findByText('完成')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: '查看轨迹' }))
    fireEvent.click(document.querySelector('[data-record-row$=":s1:message"] button') as Element)
    fireEvent.click(screen.getByRole('tab', { name: '原文' }))

    // 默认规整视图：字段平铺，长文本保留真实换行（不存在 JSON 转义的 \n 字面量）
    expect(screen.getByText('原文 JSON')).toBeInTheDocument()
    const formatted = screen.getByText(/prompt:/)
    expect(formatted).toHaveTextContent('带换行的请求')
    expect(formatted.textContent).not.toContain('\\n')

    fireEvent.click(screen.getByRole('button', { name: '原文 JSON' }))
    const raw = screen.getByText(/"prompt"/)
    expect(raw.textContent).toContain('\\n')
  })

  it('switches to wall-clock projection when records carry start times', async () => {
    const trace = new Result({
      output: '完成',
      startedAtMs: Date.UTC(2026, 0, 1, 12, 0, 0),
      steps: [
        { number: 1, stage: 'tool', startedAtMs: Date.UTC(2026, 0, 1, 12, 0, 100), modelDurationMs: 100, tool: 'web_search', toolStartedAtMs: Date.UTC(2026, 0, 1, 12, 0, 300), toolDurationMs: 200, usage: {} },
      ],
      durationMs: 500,
    })
    const summary = new ConversationSummary({ id: 'wallclock-conversation', title: '墙钟验证', updatedAt: new Date().toISOString() })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({ conversations: [summary] }))
    vi.mocked(Backend.OpenConversation).mockResolvedValue(new ConversationView({
      id: summary.id,
      title: summary.title,
      messages: [
        new DisplayMessage({ id: 'wallclock-user', role: 'user', content: '搜索一下' }),
        new DisplayMessage({ id: 'wallclock-assistant', role: 'assistant', content: '完成', trace }),
      ],
    }))

    render(<App />)
    fireEvent.click(await screen.findByTitle('墙钟验证'))
    expect(await screen.findByText('完成')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: '查看轨迹' }))

    // 时刻/墙钟按钮可用（所有记录都有开始时间）
    const wallButton = screen.getByRole('button', { name: '墙钟' })
    expect(wallButton).toBeEnabled()
    const slider = screen.getByRole('slider', { name: /时间轴总览/ })
    fireEvent.click(wallButton)
    expect(slider.getAttribute('aria-valuetext')).toMatch(/^\d{2}:\d{2}:\d{2}\.\d{3}$/)

    // 详情面板展示开始时间行（调用默认折叠，先展开）
    fireEvent.click(screen.getByRole('button', { name: '调用' }))
    fireEvent.click(screen.getByRole('button', { name: /web_search/ }))
    expect(screen.getByText('开始时间')).toBeInTheDocument()
  })

  it('keeps wall-clock projections disabled for legacy traces without timestamps', async () => {
    const summary = new ConversationSummary({ id: 'legacy-wall-conversation', title: '旧墙钟验证', updatedAt: new Date().toISOString() })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({ conversations: [summary] }))
    vi.mocked(Backend.OpenConversation).mockResolvedValue(new ConversationView({
      id: summary.id,
      title: summary.title,
      messages: [
        new DisplayMessage({ id: 'legacy-wall-assistant', role: 'assistant', content: '旧数据', trajectory: [{ step: 1, tool: 'read_file', status: 'completed' }] }),
      ],
    }))

    render(<App />)
    fireEvent.click(await screen.findByTitle('旧墙钟验证'))
    expect(await screen.findByText('旧数据')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('tab', { name: /轨迹/ }))
    // 旧轨迹直接不提供墙钟入口，只保留时序/时长
    expect(screen.queryByRole('button', { name: '墙钟' })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: '时序' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '时长' })).toBeInTheDocument()
  })

  it('folds tool calls by default and toggles from the toolbar and the row chevron', async () => {
    const trace = new Result({
      output: '完成',
      steps: [
        { number: 1, stage: 'tool', tool: 'web_search', toolArguments: '{"query":"x"}', toolResult: 'ok', toolExecuted: true, toolDurationMs: 50, modelDurationMs: 800, usage: {} },
      ],
      durationMs: 900,
    })
    const summary = new ConversationSummary({ id: 'fold-conversation', title: '折叠验证', updatedAt: new Date().toISOString() })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({ conversations: [summary] }))
    vi.mocked(Backend.OpenConversation).mockResolvedValue(new ConversationView({
      id: summary.id,
      title: summary.title,
      messages: [
        new DisplayMessage({ id: 'fold-user', role: 'user', content: '搜索一下' }),
        new DisplayMessage({ id: 'fold-assistant', role: 'assistant', content: '完成', trace }),
      ],
    }))

    render(<App />)
    fireEvent.click(await screen.findByTitle('折叠验证'))
    expect(await screen.findByText('完成')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: '查看轨迹' }))

    expect(screen.queryByRole('button', { name: /web_search/ })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: '调用' })).toHaveAttribute('aria-pressed', 'false')

    fireEvent.click(screen.getByRole('button', { name: '调用' }))
    expect(screen.getByRole('button', { name: /web_search/ })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: '折叠 Step 1 · 决策 的调用' }))
    expect(screen.queryByRole('button', { name: /web_search/ })).not.toBeInTheDocument()
  })

  it('filters the ledger by search query and reports the match count', async () => {
    const trace = new Result({
      output: '完成',
      steps: [
        { number: 1, stage: 'tool', tool: 'web_search', toolArguments: '{"query":"x"}', toolResult: 'ok', toolExecuted: true, toolDurationMs: 50, usage: {} },
      ],
      durationMs: 100,
    })
    const summary = new ConversationSummary({ id: 'search-conversation', title: '搜索验证', updatedAt: new Date().toISOString() })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({ conversations: [summary] }))
    vi.mocked(Backend.OpenConversation).mockResolvedValue(new ConversationView({
      id: summary.id,
      title: summary.title,
      messages: [
        new DisplayMessage({ id: 'search-user', role: 'user', content: '搜索一下' }),
        new DisplayMessage({ id: 'search-assistant', role: 'assistant', content: '完成', trace }),
      ],
    }))

    render(<App />)
    fireEvent.click(await screen.findByTitle('搜索验证'))
    expect(await screen.findByText('完成')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: '查看轨迹' }))

    fireEvent.change(screen.getByLabelText('搜索轨迹'), { target: { value: 'web_search' } })
    expect(await screen.findByText('1 条命中')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /web_search/ })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /最终回复/ })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /用户输入/ })).not.toBeInTheDocument()
  })

  it('switches the timeline projection between sequence and duration', async () => {
    const trace = new Result({
      output: '完成',
      steps: [
        { number: 1, stage: 'tool', tool: 'web_search', toolArguments: '{"query":"x"}', toolResult: 'ok', toolExecuted: true, toolDurationMs: 50, modelDurationMs: 800, usage: {} },
      ],
      durationMs: 900,
    })
    const summary = new ConversationSummary({ id: 'timeline-conversation', title: '时间轴验证', updatedAt: new Date().toISOString() })
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({ conversations: [summary] }))
    vi.mocked(Backend.OpenConversation).mockResolvedValue(new ConversationView({
      id: summary.id,
      title: summary.title,
      messages: [
        new DisplayMessage({ id: 'timeline-user', role: 'user', content: '搜索一下' }),
        new DisplayMessage({ id: 'timeline-assistant', role: 'assistant', content: '完成', trace }),
      ],
    }))

    render(<App />)
    fireEvent.click(await screen.findByTitle('时间轴验证'))
    expect(await screen.findByText('完成')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: '查看轨迹' }))

    const slider = screen.getByRole('slider', { name: /时间轴总览/ })
    expect(slider).toHaveAttribute('aria-valuetext', '4 条记录')
    fireEvent.click(screen.getByRole('button', { name: '时长' }))
    expect(slider).toHaveAttribute('aria-valuetext', '850 ms')
  })
})
