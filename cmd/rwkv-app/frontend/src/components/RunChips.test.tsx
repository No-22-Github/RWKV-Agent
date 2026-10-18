import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, expect, it, vi } from 'vitest'
import { Config, Provider, Status } from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import { SavedProvider } from '../../bindings/github.com/no22/RWKV-Agent/internal/appstorage/models'
import RunChips from './RunChips'

vi.mock('../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice', () => ({
  ListAdapters: vi.fn().mockResolvedValue({ adapters: [{ id: 'r16-lr3e-5', version: 'abcdef0123456789', versions: 1, rank: 16 }], missing: [] }),
  ListStates: vi.fn().mockResolvedValue({ states: Array.from({ length: 80 }, (_, i) => ({ id: `state-${i}`, filename: `Model-${i}.pth` })) }),
}))
afterEach(() => { cleanup(); vi.restoreAllMocks() })

it('keeps a long menu within available space and searches filenames and IDs', async () => {
  vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockReturnValue({ top: 280, left: 200, bottom: 306, right: 420, width: 220, height: 26, x: 200, y: 280, toJSON: () => ({}) })
  const onSelect = vi.fn().mockResolvedValue(undefined)
  render(<RunChips ready busy={false} status={new Status({ stateId: 'state-1' })} runtimeConfig={new Config()} providers={[new SavedProvider({ id: 'cuda', config: new Config({ provider: Provider.ProviderRWKVLightningCUDA }) })]} runtimeProviderId="cuda" workspace="workspace" runConfigOpen={false} setRunConfigOpen={vi.fn()} onActivate={vi.fn()} onToggleCapability={vi.fn()} onSetState={onSelect} onSetAdapter={vi.fn()} onChooseWorkspace={vi.fn()} onUnload={vi.fn()} onOpenSettings={vi.fn()} />)
  fireEvent.click(screen.getByTitle('State：state-1'))
  await screen.findByText('Model-79.pth')
  const list = screen.getByRole('listbox', { name: '选择 State' })
  expect(list.parentElement).toHaveStyle({ maxHeight: '256px', bottom: `${window.innerHeight - 280 + 8}px` })
  const input = screen.getByRole('textbox', { name: '搜索 State' })
  fireEvent.change(input, { target: { value: ' MODEL-79 ' } })
  expect(screen.queryByText('Model-1.pth')).toBeNull()
  expect(screen.getByText('Model-79.pth')).toBeInTheDocument()
  fireEvent.change(input, { target: { value: 'missing' } })
  expect(screen.getByText('没有匹配的 State')).toBeInTheDocument()
  expect(screen.getByText('不使用 State')).toBeInTheDocument()
  fireEvent.change(input, { target: { value: 'state-42' } })
  fireEvent.mouseDown(screen.getByText('Model-42.pth'))
  fireEvent.click(screen.getByText('Model-42.pth'))
  await waitFor(() => expect(onSelect).toHaveBeenCalledWith('state-42'))
})

it('picks a MiSS adapter alongside the state', async () => {
  const onSetAdapter = vi.fn().mockResolvedValue(undefined)
  const onSetState = vi.fn()
  render(<RunChips ready busy={false} status={new Status({ stateId: 'state-1' })} runtimeConfig={new Config()} providers={[new SavedProvider({ id: 'cuda', config: new Config({ provider: Provider.ProviderRWKVLightningCUDA }) })]} runtimeProviderId="cuda" workspace="workspace" runConfigOpen={false} setRunConfigOpen={vi.fn()} onActivate={vi.fn()} onToggleCapability={vi.fn()} onSetState={onSetState} onSetAdapter={onSetAdapter} onChooseWorkspace={vi.fn()} onUnload={vi.fn()} onOpenSettings={vi.fn()} />)
  expect(screen.getByTitle('State：state-1')).toBeInTheDocument()
  fireEvent.click(screen.getByTitle('未使用 MiSS 适配器'))
  await screen.findByText('rank 16 · abcdef01')
  fireEvent.click(screen.getByText('r16-lr3e-5'))
  await waitFor(() => expect(onSetAdapter).toHaveBeenCalledWith('r16-lr3e-5'))
  expect(onSetState).not.toHaveBeenCalled()
})
