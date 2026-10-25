import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import * as Backend from '../../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import type { Config } from '../../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { ProviderManager } from '../../state/providerManager'
import { SnackbarProvider } from '../../snackbar-context'
import StateSection from './StateSection'

vi.mock('@wailsio/runtime', () => ({ Events: { On: () => () => {} }, Create: { Any: (value: unknown) => value } }))
vi.mock('../../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice', () => ({
  ListStates: vi.fn().mockResolvedValue({ states: [], missing: [] }),
  ChooseStateFile: vi.fn(),
  UploadState: vi.fn().mockResolvedValue({ id: 'uploaded-state' }),
  DeleteState: vi.fn(),
}))
vi.mock('../../localFile', () => ({
  baseName: (path: string) => path.split('/').at(-1),
  pickLocalFile: vi.fn().mockResolvedValue({ kind: 'path', path: '/tmp/state.pth', name: 'state.pth' }),
  stageBrowserFile: vi.fn(),
}))

afterEach(cleanup)
beforeEach(() => vi.clearAllMocks())

function manager(running: boolean) {
  return {
    draftConfigValue: {} as Config, remoteEndpoint: 'http://localhost:8000', draftErrors: {}, apiKey: '', headers: [],
    browserUploads: false, draftIsRunning: running, stateId: '', setStateId: vi.fn(), setRuntimeState: vi.fn(),
  } as unknown as ProviderManager
}

it('reports upload without claiming use when the connection is not running', async () => {
  const value = manager(false)
  render(<SnackbarProvider><StateSection manager={value} /></SnackbarProvider>)
  fireEvent.click(screen.getByRole('button', { name: '上传 .pth…' }))
  expect(await screen.findByText('State 已上传：uploaded-state')).toBeInTheDocument()
  expect(value.setRuntimeState).not.toHaveBeenCalled()
  expect(screen.queryByText(/已选用|已使用/)).not.toBeInTheDocument()
})

it('waits for applying an upload and still refreshes the list if applying fails', async () => {
  const value = manager(true)
  let reject!: (error: Error) => void
  vi.mocked(value.setRuntimeState).mockReturnValue(new Promise<void>((_, fail) => { reject = fail }))
  render(<SnackbarProvider><StateSection manager={value} /></SnackbarProvider>)
  fireEvent.click(screen.getByRole('button', { name: '上传 .pth…' }))
  await waitFor(() => expect(value.setRuntimeState).toHaveBeenCalledWith('uploaded-state'))
  expect(screen.getByText('State 已上传：uploaded-state')).toBeInTheDocument()
  expect(screen.queryByText(/已选用|已使用/)).not.toBeInTheDocument()
  expect(screen.getByRole('button', { name: '上传 .pth…' })).toBeDisabled()
  await act(async () => reject(new Error('应用失败')))
  await waitFor(() => expect(Backend.ListStates).toHaveBeenCalled())
  expect(screen.getByRole('button', { name: '上传 .pth…' })).toBeEnabled()
})
