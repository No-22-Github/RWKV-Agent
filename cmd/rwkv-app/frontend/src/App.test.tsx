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
  })
})
