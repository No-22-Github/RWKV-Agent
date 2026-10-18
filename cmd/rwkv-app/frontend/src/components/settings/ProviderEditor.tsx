import { useState } from 'react'
import { Plus, Trash2 } from 'lucide-react'
import type { ProviderManager } from '../../state/providerManager'
import { Button, Field, GroupTitle, SaveStatus, SettingsPane } from './ui'
import { Select } from './Select'
import AdapterSection from './AdapterSection'
import StateSection from './StateSection'
import { derivedProviderLabel } from '../../state/draftValidation'
import ParametersSection from './ParametersSection'
import AgentBehaviorSection from './AgentBehaviorSection'
import { autosaveHint } from './autosaveHint'

type Tab = 'source' | 'params' | 'agent'

type Props = {
  manager: ProviderManager
  ready: boolean
  onTestRemote: () => void
  onSave: () => void
  onSaveAndUse: () => void
  onUnload: () => void
  onRequestDelete: () => void
}

/*
 * 右侧详情：点列表中的档案进入，表单即档案本身。页头（名称、状态、动作）固定，
 * 下面三个标签编辑同一份档案：连接或模型（来源与凭据）、生成参数（格式、采样、预算）、
 * 工具（能力开关与预算）。切换档案时停留在当前标签。
 *
 * 页头动作按类别分开：远端连接只有新建时的「保存」，切换在对话页做；本地模型有加载、
 * 重新加载与释放——它们占内存、要时间，必须由用户显式触发。
 */
export default function ProviderEditor({ manager, ready, onTestRemote, onSave, onSaveAndUse, onUnload, onRequestDelete }: Props) {
  const isNew = manager.editingProviderId === ''
  const local = manager.settingsTab === 'local'
  const busy = manager.settingsBusy
  const blocked = !isNew && manager.draftError !== ''
  const noun = local ? '模型' : '连接'
  const tabs: { id: Tab; label: string }[] = [
    { id: 'source', label: local ? '模型' : '连接' },
    { id: 'params', label: '生成参数' },
    // 「工具」是这个连接开哪些工具；所有连接共用的 Key 与数据源在全局「Agent」分区。
    { id: 'agent', label: '工具' },
  ]
  const headerRows = manager.headers
  const addHeader = () => manager.setHeaders([...headerRows, { id: Date.now(), name: '', value: '' }])
  const updateHeader = (id: number, patch: Partial<{ name: string; value: string }>) => manager.setHeaders(headerRows.map((row) => row.id === id ? { ...row, ...patch } : row))
  const removeHeader = (id: number) => manager.setHeaders(headerRows.filter((row) => row.id !== id))
  const [tab, setTab] = useState<Tab>('source')

  return (
    <div className="flex min-h-0 min-w-0 flex-1 flex-col">
      <div className="flex-none border-b border-line">
      <div className="mx-auto w-[min(720px,calc(100%-56px))] pt-[16px]">
      <header className="flex min-h-[54px] items-end justify-between gap-[16px]">
        <div className="min-w-0 flex-1">
          <span className="block text-2xs text-ink-muted">{isNew ? `新${noun} · 名称` : `${noun}名称`}</span>
          <input
            aria-label="连接名称"
            className="mt-[3px] h-[30px] w-full max-w-[420px] border-0 border-b border-dashed border-transparent bg-transparent p-0 text-lg font-semibold text-ink outline-0 transition-[border-color] duration-[120ms] placeholder:text-ink-ghost hover:border-line-strong focus:border-solid focus:border-brand focus-visible:outline-0"
            title={`点击修改${noun}名称`}
            value={manager.draftLabel}
            placeholder={isNew ? `未命名${noun}` : `${derivedProviderLabel(manager.draftConfigValue)}（自动）`}
            onChange={(event) => manager.setDraftLabel(event.target.value)}
          />
        </div>
        <span className="flex max-w-[55%] flex-none flex-col items-end gap-[6px]">
          <span className="flex items-center gap-[8px]">
            {local ? (<>
              {manager.draftIsRunning && !busy && <Button onClick={onUnload}>释放模型</Button>}
              {isNew && <Button onClick={onSave} disabled={!manager.draftDirty || busy}>{busy ? '处理中…' : '保存'}</Button>}
              {(isNew || !manager.draftIsRunning || manager.draftNeedsReload) && (
                <Button variant="primary" onClick={onSaveAndUse} disabled={busy || blocked} title={blocked ? manager.draftError : '读入模型文件、占用内存，加载期间无法对话'}>
                  {busy ? '处理中…' : isNew ? '保存并加载' : manager.draftNeedsReload ? '重新加载模型' : '加载模型'}
                </Button>
              )}
            </>) : isNew && (
              // 远端只有建档：还没有任何运行连接时顺手连上，否则保持当前连接不变。
              <Button variant="primary" onClick={ready ? onSave : onSaveAndUse} disabled={!manager.draftDirty || busy} title={ready ? '保存后在对话页的模型标签里切换' : undefined}>{busy ? '处理中…' : ready ? '保存' : '保存并连接'}</Button>
            )}
          </span>
          <span className="flex items-center gap-[8px]">
            {!isNew && <SaveStatus state={manager.saveState} />}
            {isNew && manager.draftDirty ? (
              <span className="flex items-center gap-[6px] text-xs text-warning"><span className="h-[6px] w-[6px] rounded-full bg-warning" />未保存更改</span>
            ) : manager.draftIsRunning ? (
              <span className="flex items-center gap-[6px] text-xs text-brand"><span className="h-[6px] w-[6px] rounded-full bg-brand-bright" />{local ? (manager.draftNeedsReload ? '已加载 · 待重新加载' : '已加载') : '运行中'}</span>
            ) : !isNew && !manager.draftDirty ? (
              <span className="text-xs text-ink-muted">{local ? '已保存 · 未加载' : '已保存'}</span>
            ) : null}
          </span>
        </span>
      </header>
      <div className="mt-[10px] flex items-end justify-between gap-[16px]">
        <div role="tablist" aria-label="连接详情" className="flex gap-[20px]">
          {tabs.map((item) => (
            <button
              key={item.id}
              role="tab"
              aria-selected={tab === item.id}
              className={`-mb-px border-0 border-b-2 bg-transparent px-0 pb-[9px] pt-[4px] text-sm transition-colors ${tab === item.id ? 'border-brand font-semibold text-ink' : 'border-transparent text-ink-muted hover:text-ink'}`}
              onClick={() => setTab(item.id)}
            >{item.label}</button>
          ))}
        </div>
        <span className="min-w-0 truncate pb-[9px] text-2xs text-ink-ghost">{autosaveHint(manager)}</span>
      </div>
      </div>
      </div>

      <SettingsPane>
      {isNew ? (
        <p className="mb-0 mt-[12px] text-xs leading-[1.65] text-ink-muted">{local
          ? '填写模型文件路径后点右上「保存」建档，「保存并加载」会立即读入模型。建档后所有改动自动保存，上方「生成参数」「工具」两个标签也属于这个模型。'
          : '填写连接信息后点右上「保存」建档；建档后所有改动自动保存，在对话页的模型标签里切换到它。上方「生成参数」「工具」两个标签也属于这个连接。'}</p>
      ) : manager.draftNeedsReload ? (
        <p role="status" className="mb-0 mt-[12px] rounded-md border border-warning/40 bg-paper-soft px-[10px] py-[7px] text-xs leading-[1.65] text-ink-soft">更改已保存，但本地模型仍在用旧配置运行。点右上「重新加载模型」使其生效（会重新加载模型文件）。</p>
      ) : null}

      {manager.settingsMessage && (
        <p role="status" aria-live="polite" className="mb-0 mt-[12px] rounded-md border border-line bg-paper-soft px-[10px] py-[7px] text-xs leading-[1.65] text-ink-soft [overflow-wrap:anywhere]">{manager.settingsMessage}</p>
      )}

      {tab === 'params' ? <ParametersSection manager={manager} /> : tab === 'agent' ? <AgentBehaviorSection manager={manager} /> : <>
      <section className="mt-[18px] pb-[24px]">
        <GroupTitle title={local ? '模型文件' : '远端服务'} />
        {manager.settingsTab === 'local' ? (
          <div className="flex flex-col gap-[8px]">
            <Field label="模型路径" hint="本机上的 RWKV-7 权重文件，填绝对路径" value={manager.modelPath} onChange={manager.setModelPath} placeholder="/absolute/path/to/rwkv7-model.pth" error={isNew ? undefined : manager.draftErrors.model} />
            <Field label="Tokenizer 路径（可选）" hint="留空时在模型文件旁边自动查找词表" value={manager.tokenizerPath} onChange={manager.setTokenizerPath} placeholder="/path/to/rwkv_vocab_v20230424.txt" />
          </div>
        ) : (
          <>
            <label className="mt-[8px] flex flex-col gap-[6px] text-xs text-ink-muted">
              接口协议
              <Select label="远端协议" className="h-[40px] w-full" value={manager.remoteProtocol} onChange={(value) => manager.setRemoteProtocol(value as 'python' | 'cuda' | 'openai')} options={[
                { value: 'python', label: 'RWKV Lightning Python' },
                { value: 'cuda', label: 'RWKV Lightning CUDA' },
                { value: 'openai', label: 'OpenAI 兼容' },
              ]} />
            </label>
            {/* 新建连接只在填了内容后才报地址错误，空表单不先挂满红字。 */}
            <Field label="API 地址" hint="推理服务的网址；填到域名即可，也接受 …/v1/models 这样的完整地址" trailing={<Button onClick={onTestRemote} disabled={manager.settingsBusy || !manager.remoteEndpoint.trim()}>测试连接</Button>} value={manager.remoteEndpoint} onChange={manager.setRemoteEndpoint} placeholder="https://example.com 或 …/v1/models" error={isNew && !manager.remoteEndpoint.trim() ? undefined : manager.draftErrors.endpoint} />
            <Field label="模型 ID" hint="服务端加载的模型名；点「测试连接」后可从下拉里选" value={manager.remoteModel} onChange={manager.setRemoteModel} placeholder="rwkv7-g1i-13.3b" list={manager.availableModels.map((model) => model.id)} error={isNew ? undefined : manager.draftErrors.model} />
            <Field label={manager.remoteProtocol !== 'openai' ? '服务密码' : 'API Key'} hint={manager.remoteProtocol !== 'openai' ? '服务端启动时设了密码才需要填，没有就留空' : '服务商给的密钥'} value={manager.apiKey} onChange={manager.setAPIKey} type="password" />
            <div className="mt-[2px] border-t border-line-soft pt-[12px]">
              <div className="mb-[7px] flex items-center gap-[8px]"><strong className="text-sm font-semibold">请求头</strong><span className="text-xs text-ink-muted">可选，每次请求都会带上；比如 Cloudflare Access 的 CF-Access-Client-Id / Secret</span></div>
              {headerRows.map((row) => (
                <div key={row.id} className="flex items-end gap-[8px]">
                  <div className="flex-1"><Field label="Header 名称" value={row.name} onChange={(value) => updateHeader(row.id, { name: value })} /></div>
                  <div className="flex-1"><Field label="Header 值" value={row.value} onChange={(value) => updateHeader(row.id, { value })} type="password" /></div>
                  <Button variant="ghost" className="mb-[6px] h-[40px] w-[40px] px-0" onClick={() => removeHeader(row.id)} aria-label={`删除 Header ${row.name || row.id}`}><Trash2 size={15} /></Button>
                </div>
              ))}
              <Button variant="ghost" className="mt-[4px] -ml-[8px] px-[8px] text-brand hover:text-brand" icon={<Plus size={14} />} onClick={addHeader}>添加请求头</Button>
            </div>
          </>
        )}
      </section>
      {manager.settingsTab === 'remote' && manager.remoteProtocol === 'cuda' && <><AdapterSection manager={manager} /><StateSection manager={manager} /></>}
      {!isNew && (
        <section className="mt-[18px]">
          <GroupTitle title="危险操作" />
          <div className="flex items-center gap-[20px] py-[11px]">
            <span className="min-w-0 flex-1 text-xs leading-[1.55] text-ink-muted">{`删除这个${noun}档案，连同它的生成参数与工具设置；不可撤销。`}</span>
            <Button variant="danger" icon={<Trash2 size={13} />} onClick={onRequestDelete} disabled={manager.settingsBusy} aria-label="删除连接">删除连接</Button>
          </div>
        </section>
      )}
      </>}
      </SettingsPane>
    </div>
  )
}
