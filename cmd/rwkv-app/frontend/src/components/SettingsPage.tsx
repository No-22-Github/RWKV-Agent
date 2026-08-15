import { useState } from 'react'
import {
  ArrowLeft, Cloud, Cpu, FolderOpen, Globe2, Moon, Plus, Sun, Trash2, Users,
} from 'lucide-react'
import { AgentProtocol, type RemoteModel, type Status } from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { ThemeMode } from '../theme'

type HeaderRow = { id: number; name: string; value: string }

type Props = {
  status: Status
  ready: boolean
  settingsTab: 'local' | 'remote'
  setSettingsTab: (tab: 'local' | 'remote') => void
  modelPath: string
  setModelPath: (value: string) => void
  tokenizerPath: string
  setTokenizerPath: (value: string) => void
  remoteEndpoint: string
  setRemoteEndpoint: (value: string) => void
  remoteModel: string
  setRemoteModel: (value: string) => void
  remoteProtocol: 'rwkv' | 'openai'
  setRemoteProtocol: (value: 'rwkv' | 'openai') => void
  apiKey: string
  setAPIKey: (value: string) => void
  headers: HeaderRow[]
  setHeaders: (value: HeaderRow[]) => void
  agentProtocol: AgentProtocol
  setAgentProtocol: (value: AgentProtocol) => void
  progressiveTools: boolean
  setProgressiveTools: (value: boolean) => void
  enableWeb: boolean
  setEnableWeb: (value: boolean) => void
  braveAPIKey: string
  setBraveAPIKey: (value: string) => void
  tavilyAPIKey: string
  setTavilyAPIKey: (value: string) => void
  enableSubagents: boolean
  setEnableSubagents: (value: boolean) => void
  maxActiveBatch: number
  setMaxActiveBatch: (value: number) => void
  remoteBatchWaitMS: number
  setRemoteBatchWaitMS: (value: number) => void
  subagentMaxParallel: number
  setSubagentMaxParallel: (value: number) => void
  subagentMaxSteps: number
  setSubagentMaxSteps: (value: number) => void
  subagentTimeoutSeconds: number
  setSubagentTimeoutSeconds: (value: number) => void
  availableModels: RemoteModel[]
  setAvailableModels: (value: RemoteModel[]) => void
  settingsMessage: string
  settingsBusy: boolean
  workspaceName: string
  onChooseWorkspace: () => void
  onTestRemote: () => void
  onSaveLocal: () => void
  onSaveRemote: () => void
  onClose: () => void
  theme: ThemeMode
  onToggleTheme: () => void
}

const NAV_ITEMS = ['模型', 'Agent', '网络与凭证', '工作区', '外观'] as const
type Section = (typeof NAV_ITEMS)[number]

export default function SettingsPage(props: Props) {
  const [section, setSection] = useState<Section>('模型')
  const { settingsTab, setSettingsTab } = props

  return (
    <div className="flex h-full w-full bg-paper text-ink">
      <aside className="flex h-full w-[216px] flex-none flex-col border-r border-line bg-paper-sidebar py-[18px]">
        <div className="px-[18px] pb-[18px] font-serif text-[16px] font-semibold">设置</div>
        {NAV_ITEMS.map((item) => (
          <button key={item} className={`flex items-center gap-[9px] px-[18px] py-2 text-left text-[12.5px] ${section === item ? 'bg-surface-active font-semibold text-ink' : 'text-ink-soft'}`} onClick={() => setSection(item)}>
            <span className={`h-[14px] w-[3px] flex-none ${section === item ? 'bg-brand' : 'bg-transparent'}`} />
            {item}
          </button>
        ))}
        <div className="flex-1" />
        <button className="mx-[18px] mb-3 flex items-center gap-[9px] border border-line bg-transparent px-3 py-2 text-[12px] text-ink-soft" onClick={props.onClose}>
          <ArrowLeft size={15} />
          返回对话
        </button>
      </aside>

      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-[52px] flex-none items-end border-b border-line px-[30px] pb-[10px]">
          <span className="font-serif text-[14.5px] font-semibold">{section}</span>
        </header>

        <div className="flex min-h-0 flex-1 justify-center overflow-auto">
          <div className="w-[826px] min-w-0 py-[30px]">
            {section === '模型' && <ModelSection {...props} />}
            {section === 'Agent' && <AgentSection {...props} />}
            {section === '网络与凭证' && <NetworkSection {...props} />}
            {section === '工作区' && <WorkspaceSection {...props} />}
            {section === '外观' && <AppearanceSection {...props} />}
          </div>
        </div>

        <footer className="flex flex-none justify-center pb-[24px] pt-[16px]">
          <div className="grid w-[826px] grid-cols-[112px_minmax(0,672px)] gap-[42px]">
            <span />
            <div className="flex items-center gap-[12px] border-t-[1.5px] border-ink pt-[13px]">
              <span className="text-[11px] text-ink-muted">配置保存在 ~/Library/Application Support/RWKV-Agent</span>
              <span className="flex-1" />
              <button className="h-[30px] border-[1.5px] border-ink bg-transparent px-[14px] text-[12.5px] font-medium text-ink" onClick={() => void props.onTestRemote()} disabled={props.settingsBusy}>测试连接</button>
              <button className="h-[30px] border-0 bg-brand px-[16px] text-[12.5px] font-medium text-white" onClick={() => { if (settingsTab === 'local') props.onSaveLocal(); else props.onSaveRemote() }} disabled={props.settingsBusy}>{props.settingsBusy ? '保存中…' : '保存'}</button>
            </div>
          </div>
        </footer>
      </main>
    </div>
  )
}

function ModelSection(props: Props) {
  return (
    <SettingsGroup title="模型" hint="本地模型或远端续写服务">
      <div className="mb-[14px] flex gap-[18px] border-b border-line">
        <button className={`flex items-center gap-[7px] border-0 border-b-2 bg-transparent px-1 pb-[9px] pt-2 text-[12px] ${props.settingsTab === 'local' ? 'border-brand font-semibold text-brand' : 'border-transparent text-ink-muted'}`} onClick={() => props.setSettingsTab('local')}><Cpu size={15} />本地模型</button>
        <button className={`flex items-center gap-[7px] border-0 border-b-2 bg-transparent px-1 pb-[9px] pt-2 text-[12px] ${props.settingsTab === 'remote' ? 'border-brand font-semibold text-brand' : 'border-transparent text-ink-muted'}`} onClick={() => props.setSettingsTab('remote')}><Cloud size={15} />远端 Provider</button>
      </div>
      {props.settingsTab === 'local' ? (
        <div className="flex flex-col gap-[13px]">
          <Field label="模型路径" value={props.modelPath} onChange={props.setModelPath} placeholder="/absolute/path/to/rwkv7-model.pth" />
          <Field label="Tokenizer 路径（可选，默认自动查找）" value={props.tokenizerPath} onChange={props.setTokenizerPath} placeholder="/path/to/rwkv_vocab_v20230424.txt" />
        </div>
      ) : (
        <div className="flex flex-col gap-[13px]">
          <Field label="API 地址" value={props.remoteEndpoint} onChange={props.setRemoteEndpoint} placeholder="https://example.com 或 …/v1/models" />
          <Field label="模型 ID" value={props.remoteModel} onChange={props.setRemoteModel} placeholder="rwkv7-g1i-13.3b" list={props.availableModels.map((m) => m.id)} />
        </div>
      )}
    </SettingsGroup>
  )
}

function AgentSection(props: Props) {
  const budgets = [
    ['活动批量', 'maxActiveBatch', 'setMaxActiveBatch', 1, 8],
    ['子 Agent 并发', 'subagentMaxParallel', 'setSubagentMaxParallel', 2, 8],
    ['单 Agent 步数', 'subagentMaxSteps', 'setSubagentMaxSteps', 2, 32],
    ['批次超时（秒）', 'subagentTimeoutSeconds', 'setSubagentTimeoutSeconds', 1, 3600],
    ['远端聚合窗口（毫秒）', 'remoteBatchWaitMS', 'setRemoteBatchWaitMS', 0, 1000],
  ] as const

  return (
    <div className="flex flex-col gap-[30px]">
      <SettingsGroup title="推理" hint="影响每一轮生成">
        <Toggle label="渐进式工具暴露" description="每轮先由短 Router 选择能力组，再暴露 schema" checked={props.progressiveTools} onChange={props.setProgressiveTools} />
        <Row label="Agent 协议" description="markdown（G1i 原生）或 xml 兼容模式">
          <select aria-label="工具协议" className="rounded-none border border-line bg-paper-wash px-2 py-[7px] text-[11px] text-ink outline-0" value={props.agentProtocol} onChange={(event) => props.setAgentProtocol(event.target.value as AgentProtocol)}>
            <option value={AgentProtocol.AgentProtocolMarkdown}>Markdown（推荐）</option>
            <option value={AgentProtocol.AgentProtocolXML}>XML（兼容模式）</option>
          </select>
        </Row>
      </SettingsGroup>

      <SettingsGroup title="能力" hint="默认只读">
        <Toggle icon={<Globe2 size={15} />} label="网页搜索与正文获取" description="Brave Search + Tavily Extract" checked={props.enableWeb} onChange={props.setEnableWeb} />
        {props.enableWeb && (
          <div className="grid grid-cols-2 gap-[10px] pt-[4px]">
            <Field label="Brave API Key" value={props.braveAPIKey} onChange={props.setBraveAPIKey} type="password" />
            <Field label="Tavily API Key" value={props.tavilyAPIKey} onChange={props.setTavilyAPIKey} type="password" />
          </div>
        )}
        <Toggle icon={<Users size={15} />} label="并发子 Agent" description="一次派发 2–8 个独立任务，不允许嵌套委派" checked={props.enableSubagents} onChange={props.setEnableSubagents} />
        {props.enableSubagents && (
          <div className="grid grid-cols-3 gap-2 pt-[4px]">
            {budgets.map(([label, key, setter, min, max]) => (
              <label key={key} className="flex flex-col gap-[5px] text-[10px] text-ink-muted">
                {label}
                <input aria-label={label} className="rounded-none border border-line bg-paper-wash px-2 py-[7px] text-[11px] text-ink outline-0" type="number" min={min} max={max} value={props[key]} onChange={(event) => props[setter](Number(event.target.value))} />
              </label>
            ))}
          </div>
        )}
      </SettingsGroup>
    </div>
  )
}

function NetworkSection(props: Props) {
  const addHeader = () => props.setHeaders([...props.headers, { id: Date.now(), name: '', value: '' }])
  const updateHeader = (id: number, patch: Partial<HeaderRow>) => props.setHeaders(props.headers.map((row) => row.id === id ? { ...row, ...patch } : row))
  const removeHeader = (id: number) => props.setHeaders(props.headers.filter((row) => row.id !== id))

  return (
    <div className="flex flex-col gap-[30px]">
      <SettingsGroup title="远端连接" hint="RWKV 续写或 OpenAI 兼容">
        <div className="flex gap-[14px]" aria-label="远端协议">
          <button type="button" className={`border-0 border-b-2 bg-transparent px-[5px] py-[9px] text-[12px] ${props.remoteProtocol === 'rwkv' ? 'border-brand font-semibold text-brand' : 'border-transparent text-ink-muted'}`} onClick={() => props.setRemoteProtocol('rwkv')}>RWKV 续写</button>
          <button type="button" className={`border-0 border-b-2 bg-transparent px-[5px] py-[9px] text-[12px] ${props.remoteProtocol === 'openai' ? 'border-brand font-semibold text-brand' : 'border-transparent text-ink-muted'}`} onClick={() => props.setRemoteProtocol('openai')}>OpenAI 兼容</button>
        </div>
        <Field label="API 地址" value={props.remoteEndpoint} onChange={props.setRemoteEndpoint} placeholder="https://example.com 或 …/v1/models" />
        <Field label="模型 ID" value={props.remoteModel} onChange={props.setRemoteModel} placeholder="rwkv7-g1i-13.3b" list={props.availableModels.map((m) => m.id)} />
        <Field label={props.remoteProtocol === 'rwkv' ? '服务密码' : 'API Key'} value={props.apiKey} onChange={props.setAPIKey} type="password" />
      </SettingsGroup>

      <SettingsGroup title="请求头" hint="可选，按需添加">
        {props.headers.map((row) => (
          <div key={row.id} className="flex items-end gap-[8px]">
            <div className="flex-1"><Field label="Header 名称" value={row.name} onChange={(value) => updateHeader(row.id, { name: value })} /></div>
            <div className="flex-1"><Field label="Header 值" value={row.value} onChange={(value) => updateHeader(row.id, { value: value })} /></div>
            <button className="grid h-[38px] w-[38px] flex-none place-items-center border border-line bg-transparent text-ink-muted" onClick={() => removeHeader(row.id)} aria-label={`删除 Header ${row.name || row.id}`}><Trash2 size={15} /></button>
          </div>
        ))}
        <button className="flex items-center gap-[7px] self-start border-0 bg-transparent px-0 py-[7px] text-[12px] text-brand" onClick={addHeader}><Plus size={14} />添加</button>
      </SettingsGroup>

      <SettingsGroup title="搜索凭证" hint="Web 能力需要">
        <Field label="Brave API Key" value={props.braveAPIKey} onChange={props.setBraveAPIKey} type="password" />
        <Field label="Tavily API Key" value={props.tavilyAPIKey} onChange={props.setTavilyAPIKey} type="password" />
      </SettingsGroup>
    </div>
  )
}

function WorkspaceSection(props: Props) {
  return (
    <SettingsGroup title="工作区" hint="Agent 可读写的根目录">
      <Row label="当前工作区" description={props.status.workspace || '未打开工作区'}>
        <button className="flex items-center gap-[7px] border border-line bg-paper-wash px-3 py-[7px] text-[12px] text-ink-soft" onClick={() => void props.onChooseWorkspace()}><FolderOpen size={15} />选择文件夹</button>
      </Row>
    </SettingsGroup>
  )
}

function AppearanceSection(props: Props) {
  const dark = props.theme === 'dark'
  return (
    <SettingsGroup title="外观" hint="纸面明暗">
      <Toggle icon={dark ? <Sun size={15} /> : <Moon size={15} />} label="深色模式" description="暗棕灰纸面，teal 提亮" checked={dark} onChange={() => props.onToggleTheme()} />
    </SettingsGroup>
  )
}

function SettingsGroup({ title, hint, children }: { title: string; hint: string; children: React.ReactNode }) {
  return (
    <section className="grid grid-cols-[112px_minmax(0,672px)] items-start gap-[42px]">
      <div className="flex flex-col gap-[4px] text-right">
        <h2 className="m-0 font-serif text-[14px] font-semibold text-ink-soft">{title}</h2>
        <p className="m-0 text-[10.5px] leading-[1.6] text-ink-ghost">{hint}</p>
      </div>
      <div className="flex min-w-0 flex-col">{children}</div>
    </section>
  )
}

function Row({ label, description, children }: { label: string; description?: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-[20px] border-b border-line px-0 py-[11px]">
      <div className="flex min-w-0 flex-1 flex-col gap-[2px]">
        <span className="text-[13.5px] text-ink">{label}</span>
        {description && <span className="text-[11px] leading-[1.55] text-ink-muted">{description}</span>}
      </div>
      {children}
    </div>
  )
}

function Field({ label, value, onChange, placeholder, type = 'text', list }: { label: string; value: string; onChange: (value: string) => void; placeholder?: string; type?: string; list?: string[] }) {
  const id = label
  return (
    <label className="flex flex-col gap-[5px] py-[6px] text-[10px] text-ink-muted">
      <span>{label}</span>
      <input id={id} aria-label={label} className="h-[38px] w-full rounded-none border border-line bg-paper-wash px-[10px] text-[12px] text-ink outline-0 placeholder:text-ink-ghost focus:border-brand" type={type} value={value} placeholder={placeholder} list={list ? `${id}-list` : undefined} onChange={(event) => onChange(event.target.value)} />
      {list && list.length > 0 && <datalist id={`${id}-list`}>{list.map((item) => <option key={item} value={item} />)}</datalist>}
    </label>
  )
}

function Toggle({ icon, label, description, checked, onChange }: { icon?: React.ReactNode; label: string; description: string; checked: boolean; onChange: (value: boolean) => void }) {
  return (
    <label className="flex items-center justify-between gap-[20px] border-b border-line py-[11px]">
      <span className="flex min-w-0 flex-1 items-start gap-[10px] text-[13px] text-ink">
        {icon && <span className="mt-[1px] flex-none text-ink-muted">{icon}</span>}
        <span className="flex min-w-0 flex-col gap-[2px]">
          <span>{label}</span>
          <span className="text-[11px] leading-[1.55] text-ink-muted">{description}</span>
        </span>
      </span>
      <input type="checkbox" aria-label={label} checked={checked} onChange={(event) => onChange(event.target.checked)} className="h-[18px] w-[32px] flex-none cursor-pointer appearance-none rounded-[9px] bg-line-strong p-0 transition-colors after:ml-[2px] after:mt-[2px] after:block after:h-[13px] after:w-[13px] after:rounded-full after:bg-white after:content-[''] after:transition-transform after:duration-200 checked:bg-brand checked:after:translate-x-[15px]" />
    </label>
  )
}
