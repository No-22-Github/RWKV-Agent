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

function openSettings() {
  fireEvent.click(screen.getByRole('button', { name: '设置' }))
}

function openSettingsSection(name: string) {
  fireEvent.click(screen.getByRole('button', { name }))
}

function switchToRemoteProvider() {
  fireEvent.click(screen.getByRole('button', { name: '远端 Provider' }))
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

    const modelChipSelector = `button[title="${model}"]`
    await waitFor(() => expect(container.querySelector(modelChipSelector)).not.toBeNull())
    expect(container.querySelector(modelChipSelector)).toHaveTextContent(model)
  })

  it('opens the settings page from the sidebar', () => {
    render(<App />)
    openSettings()
    expect(screen.getByText('设置')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '模型' })).toBeInTheDocument()
    expect(screen.getByText('本地模型')).toBeInTheDocument()
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
    openSettings()
    switchToRemoteProvider()
    openSettingsSection('网络与凭证')
    fireEvent.change(screen.getByLabelText('API 地址'), { target: { value: 'https://example.test' } })
    fireEvent.change(screen.getByLabelText('模型 ID'), { target: { value: 'rwkv7-test' } })
    fireEvent.click(screen.getByRole('button', { name: '添加' }))
    fireEvent.change(screen.getByLabelText('Header 名称'), { target: { value: 'CF-Access-Client-Id' } })
    fireEvent.change(screen.getByLabelText('Header 值'), { target: { value: 'secret' } })
    fireEvent.click(screen.getByRole('button', { name: '保存' }))

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
    openSettings()
    switchToRemoteProvider()
    openSettingsSection('Agent')
    fireEvent.click(screen.getByLabelText('网页搜索与正文获取'))
    fireEvent.change(screen.getByLabelText('Brave API Key'), { target: { value: 'brave-secret' } })
    fireEvent.change(screen.getByLabelText('Tavily API Key'), { target: { value: 'tavily-secret' } })
    fireEvent.click(screen.getByLabelText('并发子 Agent'))
    fireEvent.change(screen.getByLabelText('活动批量'), { target: { value: '6' } })
    fireEvent.change(screen.getByLabelText('子 Agent 并发'), { target: { value: '6' } })
    fireEvent.change(screen.getByLabelText('单 Agent 步数'), { target: { value: '5' } })
    fireEvent.change(screen.getByLabelText('批次超时（秒）'), { target: { value: '180' } })
    fireEvent.change(screen.getByLabelText('远端聚合窗口（毫秒）'), { target: { value: '15' } })
    fireEvent.click(screen.getByRole('button', { name: '保存' }))

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
    openSettings()
    switchToRemoteProvider()
    openSettingsSection('Agent')
    fireEvent.change(screen.getByLabelText('工具协议'), { target: { value: 'xml' } })
    fireEvent.click(screen.getByRole('button', { name: '保存' }))

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
    openSettings()
    openSettingsSection('网络与凭证')

    expect(screen.getByLabelText('API 地址')).toHaveValue('https://saved.example.test')
    expect(screen.getByLabelText('模型 ID')).toHaveValue('saved-model')
    expect(screen.getByLabelText(/服务密码/)).toHaveValue('saved-password')
    expect(screen.getByLabelText('Header 名称')).toHaveValue('X-Service-Key')
    expect(screen.getByLabelText('Header 值')).toHaveValue('saved-header')

    openSettingsSection('Agent')
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
    expect(screen.getByText(/STEP 1 · spawn_agents/)).toBeInTheDocument()
    expect(screen.getByText(/STEP 2 · read_file/)).toBeInTheDocument()
    expect(screen.getByText(/legacyTrajectory/)).toHaveTextContent('检查官方文档')
    expect(screen.getByText(/legacyTrajectory/)).toHaveTextContent('文件暂时不可读')
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

    expect(screen.getByText('输入')).toBeInTheDocument()
    expect(screen.getByText('模型')).toBeInTheDocument()
    expect(screen.getByText('工具')).toBeInTheDocument()
    expect(screen.getAllByText('读取 README').length).toBeGreaterThan(0)
    fireEvent.click(screen.getAllByTitle('工具调用 · read_file')[1])
    fireEvent.click(screen.getByRole('button', { name: '原文' }))
    expect(screen.getByText(/toolArguments/)).toHaveTextContent('README.md')
    fireEvent.click(screen.getAllByTitle('工具结果 · read_file')[1])
    fireEvent.click(screen.getByRole('button', { name: '原文' }))
    expect(screen.getByText(/toolResult/)).toHaveTextContent('# RWKV Agent')
    fireEvent.click(screen.getAllByTitle('模型响应 · Step 1')[1])
    fireEvent.click(screen.getByRole('button', { name: '原文' }))
    expect(screen.getByText(/promptTokens/)).toHaveTextContent('120')
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
    expect(screen.getByText('STEP 1 · read_file')).toBeInTheDocument()
    expect(screen.getByText('本地')).toBeInTheDocument()
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
    expect(screen.getAllByTitle('用户输入')[1]).toBeInTheDocument()
    expect(screen.getAllByTitle('模型响应 · Step 1')[1]).toBeInTheDocument()
    expect(screen.getAllByTitle('Agent 运行失败')[1]).toBeInTheDocument()
    fireEvent.click(screen.getAllByTitle('模型响应 · Step 1')[1])
    fireEvent.click(screen.getByRole('button', { name: '原文' }))
    expect(screen.getByText(/modelError/)).toHaveTextContent('模型服务返回 503')
  })
})
