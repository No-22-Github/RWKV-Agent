import { useState } from 'react'
import {
  ArrowLeft, Check, Cloud, Cpu, FolderOpen, Globe2, Moon, Plus, Sun, Trash2, Users,
} from 'lucide-react'
import { AgentProtocol, ModelState, Provider, type RemoteModel, type Status } from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { SavedProvider } from '../../bindings/github.com/no22/RWKV-Agent/internal/appstorage/models'
import type { ThemeMode } from '../theme'

type HeaderRow = { id: number; name: string; value: string }

type Props = {
  status: Status
  ready: boolean
  providers: SavedProvider[]
  activeProviderId: string
  runtimeProviderId: string
  editingProviderId: string
  draftLabel: string
  setDraftLabel: (value: string) => void
  draftDirty: boolean
  draftIsRunning: boolean
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
  settingsMessage: string
  settingsBusy: boolean
  workspaceName: string
  onChooseWorkspace: () => void
  onTestRemote: () => void
  onEditProvider: (id: string) => void
  onNewProvider: () => void
  onDeleteProvider: (id: string) => void
  onDiscardDraft: () => void
  onSaveDraft: () => void
  onSaveAndUseDraft: () => void
  onClose: () => void
  theme: ThemeMode
  onToggleTheme: () => void
}

const NAV_ITEMS = ['连接', 'Agent', '工作区', '外观'] as const
type Section = (typeof NAV_ITEMS)[number]

export default function SettingsPage(props: Props) {
  const [section, setSection] = useState<Section>('连接')
  const showDraftActions = section === '连接' || section === 'Agent'

  return (
    <div className="flex h-full w-full bg-paper text-ink">
      <aside className="settings-sidebar flex h-full w-[216px] flex-none flex-col border-r border-line bg-paper-sidebar py-[18px]">
        <div className="px-[18px] pb-[18px] font-serif text-[16px] font-semibold">设置</div>
        {NAV_ITEMS.map((item) => (
          <button key={item} className={`flex items-center gap-[9px] px-[18px] py-[8px] text-left text-[12.5px] ${section === item ? 'bg-surface-active font-semibold text-ink' : 'text-ink-soft'}`} onClick={() => setSection(item)}>
            <span className={`h-[14px] w-[3px] flex-none ${section === item ? 'bg-brand' : 'bg-transparent'}`} />
            {item}
          </button>
        ))}
        <div className="flex-1" />
        <button className="mx-[18px] mb-3 flex items-center gap-[9px] border border-line bg-transparent px-3 py-2 text-[13.5px] text-ink-soft" onClick={props.onClose}>
          <ArrowLeft size={15} />
          返回对话
        </button>
      </aside>

      <main className="flex min-w-0 flex-1 flex-col">
        <header className="settings-header flex h-[52px] flex-none items-end gap-[10px] border-b border-line px-[30px] pb-[10px]">
          <span className="font-serif text-[16px] font-semibold">{section}</span>
          {section === '连接' && <span className="text-[10.5px] text-ink-ghost">管理档案不会自动改变当前运行连接</span>}
        </header>

        <div className="flex min-h-0 flex-1 justify-center overflow-auto">
          <div className={`settings-content min-w-0 py-[24px] ${section === '连接' ? 'w-[min(1040px,calc(100%-44px))]' : 'w-[min(826px,calc(100%-52px))]'}`}>
            {section === '连接' && <ConnectionSection {...props} />}
            {section === 'Agent' && <AgentSection {...props} />}
            {section === '工作区' && <WorkspaceSection {...props} />}
            {section === '外观' && <AppearanceSection {...props} />}
          </div>
        </div>

        {showDraftActions && <DraftActions {...props} section={section} />}
      </main>
    </div>
  )
}

function ConnectionSection(props: Props) {
  const addHeader = () => props.setHeaders([...props.headers, { id: Date.now(), name: '', value: '' }])
  const updateHeader = (id: number, patch: Partial<HeaderRow>) => props.setHeaders(props.headers.map((row) => row.id === id ? { ...row, ...patch } : row))
  const removeHeader = (id: number) => props.setHeaders(props.headers.filter((row) => row.id !== id))
  const runtime = props.providers.find((provider) => provider.id === props.runtimeProviderId)
  const runtimeLabel = props.ready ? runtime?.label || props.status.model || '未命名运行连接' : '当前没有运行连接'
  const runtimeMeta = props.ready
    ? [providerKind(props.status.provider), props.status.model, endpointHost(props.status.endpoint)].filter(Boolean).join(' · ')
    : props.status.state === ModelState.ModelError ? props.status.message || '连接失败' : '选择已保存档案，或创建新草稿后点击“保存并使用”'

  return (
    <div className="flex flex-col gap-[22px]">
      <section className="grid min-h-[52px] grid-cols-[minmax(0,1fr)_auto] items-center gap-[18px] border-b border-line-soft pb-[14px]">
        <div className="flex min-w-0 items-center gap-[11px]">
          <span className={`h-[8px] w-[8px] flex-none rounded-full ${props.ready ? 'bg-brand-bright' : props.status.state === ModelState.ModelError ? 'bg-danger' : 'bg-ink-muted'}`} />
          <span className="min-w-0">
            <span className="flex min-w-0 items-baseline gap-[8px]">
              <span className="flex-none text-[10px] uppercase tracking-[.12em] text-ink-muted">当前运行连接</span>
              <strong className="truncate text-[13.5px] font-semibold text-ink">{runtimeLabel}</strong>
            </span>
            <span className="mt-[2px] block truncate font-mono text-[10px] text-ink-muted">{runtimeMeta}</span>
          </span>
        </div>
        <span className="max-w-[270px] text-right text-[10.5px] leading-[1.5] text-ink-muted">
          {props.ready && !props.runtimeProviderId ? '运行快照与已保存档案不同' : '编辑草稿不会影响正在进行的对话'}
        </span>
      </section>

      <section className="border-b border-line-soft pb-[18px]">
        <div className="mb-[10px] flex items-center gap-[8px]">
          <strong className="text-[12px] font-semibold">已保存连接</strong>
          <span className="font-mono text-[10px] text-ink-ghost">{props.providers.length}</span>
          <button className="ml-auto flex items-center gap-[5px] border-0 bg-transparent px-0 py-[5px] text-[11.5px] text-brand" onClick={props.onNewProvider}><Plus size={14} />新建连接</button>
        </div>
        {props.providers.length === 0 ? (
          <div className="py-[6px] text-[11px] leading-[1.65] text-ink-muted">还没有保存的连接。当前可以直接编辑下方草稿。</div>
        ) : (
          <div className="flex flex-wrap gap-[8px]">
            {props.providers.map((provider) => {
            const selected = provider.id === props.editingProviderId
            const running = props.ready && provider.id === props.runtimeProviderId
            const lastUsed = !running && provider.id === props.activeProviderId
            return (
              <div key={provider.id} className="group relative min-w-0">
                <button className={`flex min-h-[58px] w-[210px] min-w-0 items-center gap-[9px] border px-[12px] py-[9px] pr-[34px] text-left ${selected ? 'border-brand bg-surface-active' : 'border-line-soft bg-transparent hover:border-line'}`} onClick={() => props.onEditProvider(provider.id)}>
                  <span className={`h-[6px] w-[6px] flex-none rounded-full ${running ? 'bg-brand-bright' : 'bg-accent-warm'}`} />
                  <span className="min-w-0 flex-1">
                    <span className="block truncate text-[12px] font-medium text-ink">{provider.label || provider.config.model || '未命名连接'}</span>
                    <span className="mt-[2px] block truncate font-mono text-[9.5px] text-ink-muted">{providerMeta(provider)}</span>
                    <span className={`mt-[3px] block text-[9.5px] ${running ? 'text-brand' : selected ? 'text-ink-soft' : 'text-ink-ghost'}`}>{running ? '运行中' : selected ? '编辑中' : lastUsed ? '上次使用' : '已保存'}</span>
                  </span>
                </button>
                <button className="absolute right-[5px] top-[5px] grid h-[25px] w-[25px] place-items-center border-0 bg-transparent text-ink-ghost opacity-60 hover:bg-danger-wash hover:text-danger group-hover:opacity-100" onClick={() => props.onDeleteProvider(provider.id)} aria-label={`删除连接 ${provider.label || provider.config.model}`} disabled={props.settingsBusy}><Trash2 size={12} /></button>
              </div>
            )
            })}
          </div>
        )}
      </section>

      <section className="flex max-w-[820px] min-w-0 flex-col">
        <div className="flex min-h-[62px] items-end gap-[16px] border-b border-line pb-[12px]">
          <div className="min-w-0 flex-1">
            <span className="block text-[10px] uppercase tracking-[.12em] text-ink-muted">{props.editingProviderId ? '编辑档案副本' : '新连接草稿'}</span>
            <input aria-label="连接名称" className="mt-[3px] h-[28px] w-full border-0 bg-transparent px-0 text-[15px] font-semibold text-ink outline-0 placeholder:text-ink-ghost" value={props.draftLabel} placeholder="未命名连接" onChange={(event) => props.setDraftLabel(event.target.value)} />
          </div>
          <div className="flex flex-none items-center gap-[10px]">
            {props.draftDirty ? <span className="border border-warning bg-warning/10 px-[8px] py-[4px] text-[10px] text-warning">未保存草稿</span>
              : props.draftIsRunning ? <span className="flex items-center gap-[4px] text-[10.5px] text-brand"><Check size={12} />正在使用</span>
                : <span className="text-[10.5px] text-ink-muted">已保存</span>}
            <div className="flex border border-line bg-paper-soft p-[2px]">
              <button aria-label="远端 Provider" className={`flex h-[28px] items-center gap-[5px] border-0 px-[9px] text-[11.5px] ${props.settingsTab === 'remote' ? 'bg-paper font-medium text-brand shadow-sm' : 'bg-transparent text-ink-muted'}`} onClick={() => props.setSettingsTab('remote')}><Cloud size={13} />远端</button>
              <button aria-label="本地模型" className={`flex h-[28px] items-center gap-[5px] border-0 px-[9px] text-[11.5px] ${props.settingsTab === 'local' ? 'bg-paper font-medium text-brand shadow-sm' : 'bg-transparent text-ink-muted'}`} onClick={() => props.setSettingsTab('local')}><Cpu size={13} />本地</button>
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-[16px] pt-[18px]">
          {props.settingsTab === 'local' ? (
            <div className="flex flex-col gap-[8px]">
              <Field label="模型路径" value={props.modelPath} onChange={props.setModelPath} placeholder="/absolute/path/to/rwkv7-model.pth" />
              <Field label="Tokenizer 路径（可选，默认自动查找）" value={props.tokenizerPath} onChange={props.setTokenizerPath} placeholder="/path/to/rwkv_vocab_v20230424.txt" />
            </div>
          ) : (
            <>
              <label className="flex flex-col gap-[6px] text-[11px] text-ink-muted">
                接口协议
                <select aria-label="远端协议" className="h-[40px] border border-line bg-paper-wash px-[10px] text-[13px] text-ink outline-0 focus:border-brand" value={props.remoteProtocol} onChange={(event) => props.setRemoteProtocol(event.target.value as 'rwkv' | 'openai')}>
                  <option value="rwkv">RWKV 续写</option>
                  <option value="openai">OpenAI 兼容</option>
                </select>
              </label>
              <Field label="API 地址" value={props.remoteEndpoint} onChange={props.setRemoteEndpoint} placeholder="https://example.com 或 …/v1/models" />
              <Field label="模型 ID" value={props.remoteModel} onChange={props.setRemoteModel} placeholder="rwkv7-g1i-13.3b" list={props.availableModels.map((model) => model.id)} />
              <Field label={props.remoteProtocol === 'rwkv' ? '服务密码' : 'API Key'} value={props.apiKey} onChange={props.setAPIKey} type="password" />
              <div className="mt-[2px] border-t border-line-soft pt-[12px]">
                <div className="mb-[7px] flex items-center gap-[8px]"><strong className="text-[12px] font-semibold">请求头</strong><span className="text-[10.5px] text-ink-muted">可选，随档案保存</span></div>
                {props.headers.map((row) => (
                  <div key={row.id} className="flex items-end gap-[8px]">
                    <div className="flex-1"><Field label="Header 名称" value={row.name} onChange={(value) => updateHeader(row.id, { name: value })} /></div>
                    <div className="flex-1"><Field label="Header 值" value={row.value} onChange={(value) => updateHeader(row.id, { value })} type="password" /></div>
                    <button className="mb-[6px] grid h-[40px] w-[40px] flex-none place-items-center border border-line bg-transparent text-ink-muted" onClick={() => removeHeader(row.id)} aria-label={`删除 Header ${row.name || row.id}`}><Trash2 size={15} /></button>
                  </div>
                ))}
                <button className="flex items-center gap-[6px] border-0 bg-transparent px-0 py-[7px] text-[12.5px] text-brand" onClick={addHeader}><Plus size={14} />添加请求头</button>
              </div>
            </>
          )}
        </div>
      </section>
    </div>
  )
}

function DraftActions(props: Props & { section: Section }) {
  return (
    <footer className="flex flex-none justify-center border-t border-line bg-paper-wash px-[22px] py-[13px]">
      <div className={`flex w-full min-w-0 items-center gap-[9px] ${props.section === '连接' ? 'max-w-[1040px]' : 'max-w-[826px]'}`}>
        <span className="min-w-0 flex-1 truncate text-[11px] text-ink-muted" title={props.settingsMessage || undefined}>
          {props.settingsMessage || (props.draftDirty ? '草稿有未保存更改；当前运行连接不受影响。' : props.draftIsRunning ? '此档案与当前运行连接一致。' : '选择“保存并使用”才会切换运行连接。')}
        </span>
        <button className="h-[32px] border-0 bg-transparent px-[10px] text-[12px] text-ink-muted disabled:opacity-40" onClick={props.onDiscardDraft} disabled={!props.draftDirty || props.settingsBusy}>放弃更改</button>
        {props.section === '连接' && props.settingsTab === 'remote' && <button className="h-[32px] border border-ink bg-transparent px-[12px] text-[12.5px] text-ink" onClick={props.onTestRemote} disabled={props.settingsBusy}>测试草稿</button>}
        <button className="h-[32px] border border-ink bg-transparent px-[13px] text-[12.5px] font-medium text-ink disabled:opacity-40" onClick={props.onSaveDraft} disabled={!props.draftDirty || props.settingsBusy}>{props.settingsBusy ? '处理中…' : '保存'}</button>
        <button className="h-[32px] border-0 bg-brand px-[15px] text-[12.5px] font-medium text-white disabled:opacity-40" onClick={props.onSaveAndUseDraft} disabled={props.draftIsRunning || props.settingsBusy}>{props.settingsBusy ? '处理中…' : '保存并使用'}</button>
      </div>
    </footer>
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
      <SettingsGroup title="当前草稿" hint="这些能力会保存到正在编辑的连接档案">
        <Row label="连接档案" description={props.draftLabel || '新连接草稿'}>
          <span className={`text-[11px] ${props.draftDirty ? 'text-warning' : 'text-ink-muted'}`}>{props.draftDirty ? '未保存' : props.draftIsRunning ? '正在使用' : '已保存'}</span>
        </Row>
      </SettingsGroup>

      <SettingsGroup title="推理" hint="影响每一轮生成">
        <Toggle label="渐进式工具路由" description="可选：先由短 Router 选择能力组，再暴露 schema" checked={props.progressiveTools} onChange={props.setProgressiveTools} />
        <Row label="Agent 协议" description="XML 默认直达工具决策；Markdown 保留为可选模式">
          <select aria-label="工具协议" className="rounded-none border border-line bg-paper-wash px-2 py-[8px] text-[13.5px] text-ink outline-0" value={props.agentProtocol} onChange={(event) => props.setAgentProtocol(event.target.value as AgentProtocol)}>
            <option value={AgentProtocol.AgentProtocolXML}>XML（推荐）</option>
            <option value={AgentProtocol.AgentProtocolMarkdown}>Markdown（可选）</option>
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
              <label key={key} className="flex flex-col gap-[5px] text-[12px] text-ink-muted">
                {label}
                <input aria-label={label} className="rounded-none border border-line bg-paper-wash px-2 py-[8px] text-[13.5px] text-ink outline-0" type="number" min={min} max={max} value={props[key]} onChange={(event) => props[setter](Number(event.target.value))} />
              </label>
            ))}
          </div>
        )}
      </SettingsGroup>
    </div>
  )
}

function WorkspaceSection(props: Props) {
  return (
    <SettingsGroup title="工作区" hint="Agent 可读写的根目录">
      <Row label="当前工作区" description={props.status.workspace || '未打开工作区'}>
        <button className="flex items-center gap-[7px] border border-line bg-paper-wash px-3 py-[8px] text-[13.5px] text-ink-soft" onClick={() => void props.onChooseWorkspace()}><FolderOpen size={16} />选择文件夹</button>
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
    <section className="settings-group grid grid-cols-[112px_minmax(0,672px)] items-start gap-[42px]">
      <div className="settings-group-title flex flex-col gap-[4px] text-right">
        <h2 className="m-0 font-serif text-[14px] font-semibold text-ink">{title}</h2>
        <p className="m-0 text-[10.5px] leading-[1.6] text-ink-ghost">{hint}</p>
      </div>
      <div className="flex min-w-0 flex-col">{children}</div>
    </section>
  )
}

function Row({ label, description, children }: { label: string; description?: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-[20px] border-b border-line-soft px-0 py-[11px]">
      <div className="flex min-w-0 flex-1 flex-col gap-[2px]">
        <span className="text-[13.5px] text-ink-strong">{label}</span>
        {description && <span className="text-[11px] leading-[1.55] text-ink-muted">{description}</span>}
      </div>
      {children}
    </div>
  )
}

function Field({ label, value, onChange, placeholder, type = 'text', list }: { label: string; value: string; onChange: (value: string) => void; placeholder?: string; type?: string; list?: string[] }) {
  const id = label.replace(/\s+/g, '-')
  return (
    <label className="flex flex-col gap-[5px] py-[6px] text-[11.5px] text-ink-muted">
      <span>{label}</span>
      <input id={id} aria-label={label} className="h-[40px] w-full rounded-none border border-line bg-paper-wash px-[10px] text-[13.5px] text-ink outline-0 placeholder:text-ink-ghost focus:border-brand" type={type} value={value} placeholder={placeholder} list={list ? `${id}-list` : undefined} onChange={(event) => onChange(event.target.value)} />
      {list && list.length > 0 && <datalist id={`${id}-list`}>{list.map((item) => <option key={item} value={item} />)}</datalist>}
    </label>
  )
}

function Toggle({ icon, label, description, checked, onChange }: { icon?: React.ReactNode; label: string; description: string; checked: boolean; onChange: (value: boolean) => void }) {
  return (
    <label className="flex items-center justify-between gap-[20px] border-b border-line-soft py-[11px]">
      <span className="flex min-w-0 flex-1 items-start gap-[10px] text-[13.5px] text-ink-strong">
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

function providerMeta(provider: SavedProvider): string {
  if (provider.config.provider === Provider.ProviderLocal) return `本地模型 · ${provider.config.model.split(/[\\/]/).at(-1) || provider.config.model}`
  const kind = providerKind(provider.config.provider)
  const host = endpointHost(provider.config.endpoint)
  return [kind, host].filter(Boolean).join(' · ')
}

function providerKind(provider?: Provider): string {
  if (provider === Provider.ProviderLocal) return '本地模型'
  if (provider === Provider.ProviderChatCompletions) return 'OpenAI 兼容'
  if (provider === Provider.ProviderRWKVLightning) return 'RWKV 续写'
  return ''
}

function endpointHost(endpoint?: string): string {
  const value = (endpoint || '').trim()
  if (!value) return ''
  try {
    return new URL(value).host || value
  } catch {
    return value.replace(/^https?:\/\//, '').split('/')[0]
  }
}
