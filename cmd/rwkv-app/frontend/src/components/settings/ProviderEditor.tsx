import { Cloud, Cpu, Globe2, Plus, Trash2, Users } from 'lucide-react'
import { AgentProtocol } from '../../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { ProviderManager } from '../../state/providerManager'
import { Field, GroupTitle, Toggle } from './ui'

type Props = {
  manager: ProviderManager
  ready: boolean
  onTestRemote: () => void
  onSave: () => void
  onSaveAndUse: () => void
  onRequestDelete: () => void
}

/* 右侧编辑器：点列表中的档案进入，表单即档案本身；底部为该档案的动作。 */
export default function ProviderEditor({ manager, ready, onTestRemote, onSave, onSaveAndUse, onRequestDelete }: Props) {
  const isNew = manager.editingProviderId === ''
  const headerRows = manager.headers
  const addHeader = () => manager.setHeaders([...headerRows, { id: Date.now(), name: '', value: '' }])
  const updateHeader = (id: number, patch: Partial<{ name: string; value: string }>) => manager.setHeaders(headerRows.map((row) => row.id === id ? { ...row, ...patch } : row))
  const removeHeader = (id: number) => manager.setHeaders(headerRows.filter((row) => row.id !== id))
  const budgets = [
    ['活动批量', 'maxActiveBatch', 'setMaxActiveBatch', 1, 8],
    ['子 Agent 并发', 'subagentMaxParallel', 'setSubagentMaxParallel', 2, 8],
    ['单 Agent 步数', 'subagentMaxSteps', 'setSubagentMaxSteps', 2, 32],
    ['批次超时（秒）', 'subagentTimeoutSeconds', 'setSubagentTimeoutSeconds', 1, 3600],
    ['远端聚合窗口（毫秒）', 'remoteBatchWaitMS', 'setRemoteBatchWaitMS', 0, 1000],
  ] as const

  return (
    <div className="flex min-w-0 flex-1 flex-col">
      <div className="flex min-w-0 flex-1 flex-col overflow-auto">
        <div className="mx-auto w-[min(720px,calc(100%-56px))] flex-none pt-[22px]">
          <header className="flex min-h-[54px] items-end justify-between gap-[16px] border-b border-line pb-[12px]">
            <div className="min-w-0 flex-1">
              <span className="block text-2xs uppercase tracking-[.12em] text-ink-muted">{isNew ? '新连接' : '连接档案'}</span>
              <input
                aria-label="连接名称"
                className="mt-[3px] h-[30px] w-full max-w-[420px] border-0 bg-transparent p-0 font-serif text-lg font-semibold text-ink outline-0 placeholder:text-ink-ghost"
                value={manager.draftLabel}
                placeholder="未命名连接"
                onChange={(event) => manager.setDraftLabel(event.target.value)}
              />
            </div>
            {manager.draftDirty ? (
              <span className="flex flex-none items-center gap-[6px] text-xs text-warning"><span className="h-[6px] w-[6px] rounded-full bg-warning" />未保存更改</span>
            ) : manager.draftIsRunning ? (
              <span className="flex flex-none items-center gap-[6px] text-xs text-brand"><span className="h-[6px] w-[6px] rounded-full bg-brand-bright" />运行中</span>
            ) : (
              <span className="flex-none text-xs text-ink-muted">已保存</span>
            )}
          </header>
          {isNew && (
            <p className="mb-0 mt-[12px] text-xs leading-[1.65] text-ink-muted">填写连接信息后点击「保存」存为档案；「保存并使用」会保存并立即切换为当前运行连接。</p>
          )}

          <section className="mt-[18px]">
            <GroupTitle title="模型来源" />
            <div className="flex items-center gap-[10px] pt-[10px]">
              <div className="flex border border-line bg-paper-soft p-[2px]">
                <button aria-label="远端 Provider" className={`flex h-[28px] items-center gap-[5px] border-0 px-[9px] text-xs ${manager.settingsTab === 'remote' ? 'bg-paper font-medium text-brand shadow-sm' : 'bg-transparent text-ink-muted'}`} onClick={() => manager.setSettingsTab('remote')}><Cloud size={13} />远端</button>
                <button aria-label="本地模型" className={`flex h-[28px] items-center gap-[5px] border-0 px-[9px] text-xs ${manager.settingsTab === 'local' ? 'bg-paper font-medium text-brand shadow-sm' : 'bg-transparent text-ink-muted'}`} onClick={() => manager.setSettingsTab('local')}><Cpu size={13} />本地</button>
              </div>
            </div>
            {manager.settingsTab === 'local' ? (
              <div className="flex flex-col gap-[8px]">
                <Field label="模型路径" value={manager.modelPath} onChange={manager.setModelPath} placeholder="/absolute/path/to/rwkv7-model.pth" />
                <Field label="Tokenizer 路径（可选，默认自动查找）" value={manager.tokenizerPath} onChange={manager.setTokenizerPath} placeholder="/path/to/rwkv_vocab_v20230424.txt" />
              </div>
            ) : (
              <>
                <label className="mt-[8px] flex flex-col gap-[6px] text-xs text-ink-muted">
                  接口协议
                  <select aria-label="远端协议" className="h-[40px] border border-line bg-paper-wash px-[10px] text-base text-ink outline-0 focus:border-brand" value={manager.remoteProtocol} onChange={(event) => manager.setRemoteProtocol(event.target.value as 'rwkv' | 'openai')}>
                    <option value="rwkv">RWKV 续写</option>
                    <option value="openai">OpenAI 兼容</option>
                  </select>
                </label>
                <Field label="API 地址" value={manager.remoteEndpoint} onChange={manager.setRemoteEndpoint} placeholder="https://example.com 或 …/v1/models" />
                <Field label="模型 ID" value={manager.remoteModel} onChange={manager.setRemoteModel} placeholder="rwkv7-g1i-13.3b" list={manager.availableModels.map((model) => model.id)} />
                <Field label={manager.remoteProtocol === 'rwkv' ? '服务密码' : 'API Key'} value={manager.apiKey} onChange={manager.setAPIKey} type="password" />
                <div className="mt-[2px] border-t border-line-soft pt-[12px]">
                  <div className="mb-[7px] flex items-center gap-[8px]"><strong className="text-sm font-semibold">请求头</strong><span className="text-xs text-ink-muted">可选，随档案保存</span></div>
                  {headerRows.map((row) => (
                    <div key={row.id} className="flex items-end gap-[8px]">
                      <div className="flex-1"><Field label="Header 名称" value={row.name} onChange={(value) => updateHeader(row.id, { name: value })} /></div>
                      <div className="flex-1"><Field label="Header 值" value={row.value} onChange={(value) => updateHeader(row.id, { value })} type="password" /></div>
                      <button className="mb-[6px] grid h-[40px] w-[40px] flex-none place-items-center border border-line bg-transparent text-ink-muted" onClick={() => removeHeader(row.id)} aria-label={`删除 Header ${row.name || row.id}`}><Trash2 size={15} /></button>
                    </div>
                  ))}
                  <button className="flex items-center gap-[6px] border-0 bg-transparent px-0 py-[7px] text-sm text-brand" onClick={addHeader}><Plus size={14} />添加请求头</button>
                </div>
              </>
            )}
          </section>

          <section className="mt-[22px] pb-[24px]">
            <GroupTitle title="Agent 行为" hint="随档案保存，保存并使用后生效" />
            <Toggle label="渐进式工具路由" description="可选：先由短 Router 选择能力组，再暴露 schema" checked={manager.progressiveTools} onChange={manager.setProgressiveTools} />
            <div className="flex items-center justify-between gap-[20px] border-b border-line-soft py-[11px]">
              <span className="flex min-w-0 flex-1 flex-col gap-[2px]">
                <span className="text-base text-ink-strong">工具协议</span>
                <span className="text-xs leading-[1.55] text-ink-muted">XML 默认直达工具决策；Markdown 保留为可选模式</span>
              </span>
              <select aria-label="工具协议" className="h-[36px] w-[170px] flex-none border border-line bg-paper-wash px-[8px] text-base text-ink outline-0 focus:border-brand" value={manager.agentProtocol} onChange={(event) => manager.setAgentProtocol(event.target.value as AgentProtocol)}>
                <option value={AgentProtocol.AgentProtocolXML}>XML（推荐）</option>
                <option value={AgentProtocol.AgentProtocolMarkdown}>Markdown（可选）</option>
              </select>
            </div>
            <Toggle icon={<Globe2 size={15} />} label="网页搜索与正文获取" description="Brave Search + Tavily Extract" checked={manager.enableWeb} onChange={manager.setEnableWeb} />
            {manager.enableWeb && (
              <div className="grid grid-cols-2 gap-[10px] pt-[4px]">
                <Field label="Brave API Key" value={manager.braveAPIKey} onChange={manager.setBraveAPIKey} type="password" />
                <Field label="Tavily API Key" value={manager.tavilyAPIKey} onChange={manager.setTavilyAPIKey} type="password" />
              </div>
            )}
            <Toggle icon={<Users size={15} />} label="并发子 Agent" description="一次派发 2–8 个独立任务，不允许嵌套委派" checked={manager.enableSubagents} onChange={manager.setEnableSubagents} />
            {manager.enableSubagents && (
              <div className="grid grid-cols-3 gap-2 pt-[4px]">
                {budgets.map(([label, key, setter, min, max]) => (
                  <label key={key} className="flex flex-col gap-[5px] text-sm text-ink-muted">
                    {label}
                    <input aria-label={label} className="rounded-none border border-line bg-paper-wash px-2 py-[8px] text-base text-ink outline-0" type="number" min={min} max={max} value={manager[key]} onChange={(event) => manager[setter](Number(event.target.value))} />
                  </label>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>

      {manager.settingsMessage && (
        <div className="flex-none border-t border-line-soft px-[28px] py-[8px]">
          <span className="block truncate text-xs text-ink-muted" title={manager.settingsMessage}>{manager.settingsMessage}</span>
        </div>
      )}
      <footer className="flex flex-none items-center gap-[10px] border-t border-line bg-paper-soft px-[28px] py-[12px]">
        <button
          className="h-[32px] border border-danger bg-transparent px-[12px] text-sm text-danger disabled:opacity-40"
          onClick={onRequestDelete}
          disabled={isNew || manager.settingsBusy}
          aria-label="删除连接"
        ><Trash2 size={13} className="mr-[6px] inline align-[-2px]" />删除连接</button>
        <span className="flex-1" />
        {manager.settingsTab === 'remote' && (
          <button className="h-[32px] border border-line bg-transparent px-[12px] text-sm text-ink disabled:opacity-40" onClick={onTestRemote} disabled={manager.settingsBusy}>测试连接</button>
        )}
        <button className="h-[32px] border border-ink bg-transparent px-[13px] text-sm font-medium text-ink disabled:opacity-40" onClick={onSave} disabled={!manager.draftDirty || manager.settingsBusy}>{manager.settingsBusy ? '处理中…' : '保存'}</button>
        <button className="h-[32px] border-0 bg-brand px-[15px] text-sm font-medium text-white disabled:opacity-40" onClick={onSaveAndUse} disabled={manager.draftIsRunning || manager.settingsBusy} title={ready ? undefined : '当前未连接，保存后将建立连接'}>{manager.settingsBusy ? '处理中…' : '保存并使用'}</button>
      </footer>
    </div>
  )
}
