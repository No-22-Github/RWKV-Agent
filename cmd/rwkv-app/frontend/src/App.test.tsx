import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import * as Backend from '../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import { Config, ModelState, Provider, Result, Status } from '../bindings/github.com/no22/RWKV-Agent/api/models'
import {
  AppBootstrap,
  ConversationSummary,
  ConversationView,
  DisplayMessage,
  StoragePaths,
  SubagentStep,
  SubagentTrace,
  ToolRetryTrace,
  ToolTrace,
  WorkspaceItem,
} from '../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/models'
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
  ListRemoteModels: vi.fn(),
  NewConversation: vi.fn().mockResolvedValue(undefined),
  ChooseWorkspace: vi.fn(),
  OpenWorkspace: vi.fn(),
  OpenConversation: vi.fn(),
  DeleteConversation: vi.fn().mockResolvedValue(undefined),
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

beforeEach(() => {
  eventHandlers.clear()
  vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap())
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

    const modelChipSelector = `.composer-chip[title="${model}"]`
    await waitFor(() => expect(container.querySelector(modelChipSelector)).not.toBeNull())
    expect(container.querySelector(modelChipSelector)).toHaveTextContent(model)
  })

  it('opens model settings from the empty state', () => {
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: '加载本地模型或连接远端 API' }))
    expect(screen.getByRole('dialog', { name: '模型设置' })).toBeInTheDocument()
    expect(screen.getByText('本地模型')).toBeInTheDocument()
    expect(screen.getByText('远端 API')).toBeInTheDocument()
  })

  it('uses RWKV continuation by default and passes custom HTTP headers', async () => {
    vi.mocked(Backend.Configure).mockResolvedValue(new Status({
      state: ModelState.ModelReady,
      provider: Provider.ProviderRWKVLightning,
      model: 'rwkv7-test',
      workspace: '/tmp/RWKV-Agent',
      hasApiKey: false,
      updatedAt: new Date().toISOString(),
    }))
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: '加载本地模型或连接远端 API' }))
    fireEvent.click(screen.getByRole('button', { name: '远端 API' }))
    fireEvent.change(screen.getByLabelText('API 地址'), { target: { value: 'https://example.test' } })
    fireEvent.change(screen.getByLabelText('模型 ID'), { target: { value: 'rwkv7-test' } })
    fireEvent.click(screen.getByRole('button', { name: '添加' }))
    fireEvent.change(screen.getByLabelText('Header 名称'), { target: { value: 'CF-Access-Client-Id' } })
    fireEvent.change(screen.getByLabelText('Header 值'), { target: { value: 'secret' } })
    fireEvent.click(screen.getByRole('button', { name: '连接 API' }))

    await waitFor(() => expect(Backend.Configure).toHaveBeenCalledOnce())
    const config = vi.mocked(Backend.Configure).mock.calls[0][0]
    expect(config.provider).toBe('rwkv-lightning')
    expect(config.rwkvStopTokens).toBe('none')
    expect(config.stream).toBe(false)
    expect(config.headers).toEqual({ 'CF-Access-Client-Id': 'secret' })
    expect(config.agentProtocol).toBe('markdown')
    expect(config.progressiveTools).toBe(true)
    expect(config.enableSubagents).toBe(false)
  })

  it('passes web credentials and concurrent subagent budgets', async () => {
    vi.mocked(Backend.Configure).mockResolvedValue(new Status({
      state: ModelState.ModelReady,
      provider: Provider.ProviderRWKVLightning,
      model: 'rwkv7-test',
      workspace: '/tmp/RWKV-Agent',
      hasApiKey: false,
      updatedAt: new Date().toISOString(),
    }))
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: '加载本地模型或连接远端 API' }))
    fireEvent.click(screen.getByRole('button', { name: '远端 API' }))
    fireEvent.change(screen.getByLabelText('API 地址'), { target: { value: 'https://example.test' } })
    fireEvent.change(screen.getByLabelText('模型 ID'), { target: { value: 'rwkv7-test' } })
    fireEvent.click(screen.getByLabelText('网页搜索与正文获取'))
    fireEvent.change(screen.getByLabelText('Brave API Key'), { target: { value: 'brave-secret' } })
    fireEvent.change(screen.getByLabelText('Tavily API Key'), { target: { value: 'tavily-secret' } })
    fireEvent.click(screen.getByLabelText('并发子 Agent'))
    fireEvent.change(screen.getByLabelText('活动批量'), { target: { value: '6' } })
    fireEvent.change(screen.getByLabelText('子 Agent 并发'), { target: { value: '6' } })
    fireEvent.change(screen.getByLabelText('单 Agent 步数'), { target: { value: '5' } })
    fireEvent.change(screen.getByLabelText('批次超时（秒）'), { target: { value: '180' } })
    fireEvent.change(screen.getByLabelText('远端聚合窗口（毫秒）'), { target: { value: '15' } })
    fireEvent.click(screen.getByRole('button', { name: '连接 API' }))

    await waitFor(() => expect(Backend.Configure).toHaveBeenCalledOnce())
    const config = vi.mocked(Backend.Configure).mock.calls[0][0]
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
  })

  it('allows the XML compatibility protocol to be selected', async () => {
    vi.mocked(Backend.Configure).mockResolvedValue(new Status({
      state: ModelState.ModelReady,
      provider: Provider.ProviderRWKVLightning,
      model: 'rwkv7-test',
      workspace: '/tmp/RWKV-Agent',
      hasApiKey: false,
      updatedAt: new Date().toISOString(),
    }))
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: '加载本地模型或连接远端 API' }))
    fireEvent.click(screen.getByRole('button', { name: '远端 API' }))
    fireEvent.change(screen.getByLabelText('API 地址'), { target: { value: 'https://example.test' } })
    fireEvent.change(screen.getByLabelText('模型 ID'), { target: { value: 'rwkv7-test' } })
    fireEvent.change(screen.getByLabelText('工具协议'), { target: { value: 'xml' } })
    fireEvent.click(screen.getByRole('button', { name: '连接 API' }))

    await waitFor(() => expect(Backend.Configure).toHaveBeenCalledOnce())
    expect(vi.mocked(Backend.Configure).mock.calls[0][0].agentProtocol).toBe('xml')
  })

  it('hydrates saved provider settings and plaintext credentials', async () => {
    vi.mocked(Backend.Bootstrap).mockResolvedValue(bootstrap({
      config: new Config({
        provider: Provider.ProviderRWKVLightning,
        endpoint: 'https://saved.example.test',
        model: 'saved-model',
        password: 'saved-password',
        headers: { 'X-Service-Key': 'saved-header' },
        enableWeb: true,
        braveApiKey: 'saved-brave',
        tavilyApiKey: 'saved-tavily',
      }),
      hasConfig: true,
    }))

    render(<App />)
    await waitFor(() => expect(Backend.Bootstrap).toHaveBeenCalledOnce())
    fireEvent.click(screen.getByRole('button', { name: '设置' }))

    expect(screen.getByLabelText('API 地址')).toHaveValue('https://saved.example.test')
    expect(screen.getByLabelText('模型 ID')).toHaveValue('saved-model')
    expect(screen.getByLabelText(/服务密码/)).toHaveValue('saved-password')
    expect(screen.getByLabelText('Header 名称')).toHaveValue('X-Service-Key')
    expect(screen.getByLabelText('Header 值')).toHaveValue('saved-header')
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

  it('reopens a saved conversation', async () => {
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

    const summaryButton = screen.getByRole('button', { name: '完成 2 次工具调用，1 次失败 · 1 个子 Agent' })
    expect(summaryButton).toHaveAttribute('aria-expanded', 'false')
    fireEvent.click(summaryButton)
    expect(summaryButton).toHaveAttribute('aria-expanded', 'true')
    expect(screen.getByText('步骤 2 · 失败')).toBeInTheDocument()
    expect(screen.getByText('文件暂时不可读')).toBeInTheDocument()
    expect(screen.getByText('spawn_agents')).toBeInTheDocument()
    expect(screen.getByText('Agent 1')).toBeInTheDocument()
    expect(screen.getByText('检查官方文档')).toBeInTheDocument()
    expect(screen.getByText('web_fetch')).toBeInTheDocument()
    expect(screen.getByText('{"urls":["https://example.test/docs"]}')).toBeInTheDocument()
    expect(screen.getByText('尝试 1/5 · HTTP 429 · 2 秒后重试')).toBeInTheDocument()
    expect(screen.getByText('确认了官方说明')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /https:\/\/example\.test\/docs/ })).toHaveAttribute('href', 'https://example.test/docs')
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

    const emit = eventHandlers.get('agent:event')
    expect(emit).toBeDefined()
    act(() => {
      emit?.({ data: { kind: 'tool_start', step: 1, tool: 'spawn_agents', arguments: '{"tasks":["检查文档","检查代码"]}' } })
      emit?.({ data: { kind: 'subagent_start', parentStep: 1, subagentIndex: 1, subagentTask: '检查文档' } })
      emit?.({ data: { kind: 'route_done', parentStep: 1, subagentIndex: 1, subagentTask: '检查文档', route: 'inspect', bundles: ['web'] } })
      emit?.({ data: { kind: 'tool_start', parentStep: 1, subagentIndex: 1, subagentTask: '检查文档', step: 1, tool: 'web_search', arguments: '{"query":"RWKV"}' } })
      emit?.({ data: { kind: 'tool_retry', parentStep: 1, subagentIndex: 1, subagentTask: '检查文档', step: 1, tool: 'web_search', attempt: 1, maxAttempts: 5, statusCode: 429, delayMs: 2000 } })
    })

    expect(screen.getByText('spawn_agents')).toBeInTheDocument()
    expect(screen.getByText('Agent 1')).toBeInTheDocument()
    expect(screen.getByText('检查文档')).toBeInTheDocument()
    expect(screen.getByText('web_search')).toBeInTheDocument()
    expect(screen.getByText('{"query":"RWKV"}')).toBeInTheDocument()
    expect(screen.getByText('bundles: web')).toBeInTheDocument()
    expect(screen.getByText('尝试 1/5 · HTTP 429 · 2 秒后重试')).toBeInTheDocument()

    await act(async () => {
      resolveChat(new Result({ output: 'done', steps: [], duration: 0, durationMs: 1 }))
    })
  })
})
