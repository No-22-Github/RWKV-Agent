import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as Backend from '../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import { ModelState, Provider, Status } from '../bindings/github.com/no22/RWKV-Agent/api/models'
import App from './App'

vi.mock('@wailsio/runtime', () => ({
  Events: { On: () => () => undefined },
  Call: { ByID: vi.fn() },
  Create: { Array: (create: (value: unknown) => unknown) => (values: unknown[]) => values.map(create), Map: () => (value: unknown) => value, Any: (value: unknown) => value },
}))

vi.mock('../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice', () => ({
  Status: vi.fn().mockResolvedValue({ state: 'idle', workspace: '/tmp/RWKV-Agent', hasApiKey: false, updatedAt: new Date().toISOString() }),
  Chat: vi.fn(),
  Configure: vi.fn(),
  ListRemoteModels: vi.fn(),
  NewConversation: vi.fn().mockResolvedValue(undefined),
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe('App', () => {
  it('renders the stable empty conversation layout', async () => {
    render(<App />)
    expect(screen.getByText('探索智能之境')).toBeInTheDocument()
    expect(screen.getByLabelText('消息')).toBeInTheDocument()
    expect((await screen.findAllByText('RWKV-Agent')).length).toBeGreaterThan(0)
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
})
