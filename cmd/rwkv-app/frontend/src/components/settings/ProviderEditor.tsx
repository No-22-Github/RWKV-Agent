import { useState } from 'react'
import { ChevronRight, Plus, Trash2 } from 'lucide-react'
import type { ProviderManager, RemoteProtocol } from '../../state/providerManager'
import { Button, Disclosure, Notice, NumberRow, PANE_HEADER_TOP, PANE_WIDTH, Row, RunningBadge, SaveStatus, Section, SettingsPane, TextInput, TextRow } from './ui'
import { Select } from './Select'
import AdapterSection from './AdapterSection'
import StateSection from './StateSection'
import { derivedProviderLabel } from '../../state/draftValidation'

type Props = {
  manager: ProviderManager
  ready: boolean
  backLabel: string
  onBack: () => void
  onTestRemote: () => void
  onSave: () => void
  onSaveAndUse: () => void
  onUnload: () => void
  onRequestDelete: () => void
  onCancel: () => void
}

/*
 * 档案详情：从列表点进来，页头面包屑「远端连接 ›」回到列表。页头只有一层——名称、状态、动作；
 * 下面只有连接本身：来源与凭据、请求头、批处理参数，以及记在这个连接上的 State 与适配器（MiSS / NoRA）。
 * 对话格式也记在连接上，但在对话页的格式芯片里切换；生成参数与工具所有连接共用，在「Agent」分区。
 *
 * 页头动作按类别分开：远端连接只有新建时的「保存」，切换在对话页做；本地模型有加载、
 * 重新加载与释放——它们占内存、要时间，必须由用户显式触发。已建档的档案改动自动保存，
 * 保存状态在页头右侧一闪而过，不常驻说明。
 */
export default function ProviderEditor({ manager, ready, backLabel, onBack, onTestRemote, onSave, onSaveAndUse, onUnload, onRequestDelete, onCancel }: Props) {
  const isNew = manager.editingProviderId === ''
  const local = manager.settingsTab === 'local'
  const busy = manager.settingsBusy
  const blocked = !isNew && manager.draftError !== ''
  const noun = local ? '模型' : '连接'

  // 新建是在填一张表：底部固定「取消 / 保存」，主按钮在右下角；已建档的改动自动保存，没有保存按钮。
  const status = isNew
    ? null
    : manager.draftIsRunning
      ? (local && manager.draftNeedsReload ? <RunningBadge tone="warning">已加载 · 待重新加载</RunningBadge> : <RunningBadge>{local ? '已加载' : '运行中'}</RunningBadge>)
      : null

  return (
    <div className="flex min-h-0 min-w-0 flex-1 flex-col">
      <div className="flex-none border-b border-line">
        <div className={`${PANE_WIDTH} ${PANE_HEADER_TOP} pb-[14px]`}>
          {/* 面包屑与列表页标题同字号、同位置：进出详情时「远端连接」几个字原地不动，只是变灰、后面接上名称。 */}
          <header className="flex min-h-[34px] items-center gap-[12px]">
            <button aria-label={`返回${backLabel}列表`} className="-ml-[6px] flex h-[32px] flex-none items-center gap-[4px] rounded-md border-0 bg-transparent px-[6px] text-md font-semibold text-ink-muted transition-colors hover:bg-surface-active hover:text-ink" onClick={onBack}>
              {backLabel}<ChevronRight size={15} className="text-ink-ghost" />
            </button>
            <input
              aria-label="连接名称"
              className={`h-[32px] min-w-0 flex-1 text-ellipsis rounded-md border border-transparent bg-transparent px-[6px] -ml-[6px] text-md font-semibold text-ink outline-0 transition-colors ${isNew ? 'placeholder:font-normal placeholder:text-ink-ghost' : 'placeholder:text-ink'} hover:border-line focus:border-brand`}
              title={`点击修改${noun}名称`}
              value={manager.draftLabel}
              placeholder={isNew ? `新${noun}` : `${derivedProviderLabel(manager.draftConfigValue)}（自动命名）`}
              onChange={(event) => manager.setDraftLabel(event.target.value)}
            />
            {status}
            <span className="flex flex-none items-center gap-[8px]">
              {!isNew && <SaveStatus state={manager.saveState} />}
              {/* 本地模型的加载与释放占内存、要时间，是动作不是保存，留在页头。 */}
              {local && !isNew && (<>
                {manager.draftIsRunning && !busy && <Button onClick={onUnload}>释放模型</Button>}
                {(!manager.draftIsRunning || manager.draftNeedsReload) && (
                  <Button variant="primary" onClick={onSaveAndUse} disabled={busy || blocked} title={blocked ? manager.draftError : '读入模型文件、占用内存，加载期间无法对话'}>
                    {busy ? '处理中…' : manager.draftNeedsReload ? '重新加载模型' : '加载模型'}
                  </Button>
                )}
              </>)}
            </span>
          </header>
        </div>
      </div>

      <SettingsPane footer={isNew && (
        <div className="flex-none border-t border-line">
          <div className={`${PANE_WIDTH} flex min-h-[56px] items-center justify-end gap-[8px] py-[12px]`}>
            {manager.draftBlockReason && manager.draftDirty && <span className="mr-auto min-w-0 truncate text-sm text-warning" title={manager.draftBlockReason}>{manager.draftBlockReason}</span>}
            <Button onClick={onCancel} disabled={busy}>取消</Button>
            {local ? (<>
              <Button onClick={onSave} disabled={!manager.draftDirty || busy}>保存</Button>
              <Button variant="primary" onClick={onSaveAndUse} disabled={busy || blocked} title="读入模型文件、占用内存，加载期间无法对话">{busy ? '处理中…' : '保存并加载'}</Button>
            </>) : (
              // 远端只有建档：还没有任何运行连接时顺手连上，否则保持当前连接不变。
              <Button variant="primary" onClick={ready ? onSave : onSaveAndUse} disabled={!manager.draftDirty || busy} title={ready ? '保存后在对话页的模型标签里切换' : undefined}>{busy ? '处理中…' : ready ? '保存' : '保存并连接'}</Button>
            )}
          </div>
        </div>
      )}>
        {local && manager.draftNeedsReload && (
          <Notice tone="warning">更改已保存，但本地模型仍在用旧配置运行；点右上「重新加载模型」生效。</Notice>
        )}

        {local ? (
          <LocalSource manager={manager} isNew={isNew} onRequestDelete={onRequestDelete} />
        ) : (
          <RemoteSource manager={manager} isNew={isNew} onTestRemote={onTestRemote} onRequestDelete={onRequestDelete} />
        )}
      </SettingsPane>
    </div>
  )
}

function LocalSource({ manager, isNew, onRequestDelete }: { manager: ProviderManager; isNew: boolean; onRequestDelete: () => void }) {
  return (
    <>
      <Section title="模型文件">
        <TextRow label="模型路径" width="w-[340px]" value={manager.modelPath} onChange={manager.setModelPath} placeholder="/path/to/rwkv7-model.pth" error={isNew ? undefined : manager.draftErrors.model} />
        <TextRow label="Tokenizer 路径" width="w-[340px]" value={manager.tokenizerPath} onChange={manager.setTokenizerPath} placeholder="留空则在模型旁边自动查找" />
      </Section>
      <Section title="高级">
        <NumberRow label="活动批量" description="同时解码的请求数；改后重新加载模型生效" min={1} max={8} defaultValue={4} value={manager.maxActiveBatch} onChange={manager.setMaxActiveBatch} />
      </Section>
      {!isNew && <DeleteSection noun="模型" onRequestDelete={onRequestDelete} disabled={manager.settingsBusy} />}
    </>
  )
}

function RemoteSource({ manager, isNew, onTestRemote, onRequestDelete }: { manager: ProviderManager; isNew: boolean; onTestRemote: () => void; onRequestDelete: () => void }) {
  const lightning = manager.remoteProtocol === 'python' || manager.remoteProtocol === 'cuda'
  const cuda = manager.remoteProtocol === 'cuda'
  // 从对话页「管理 State / 适配器」进来时直接展开对应项。
  const [open, setOpen] = useState<Record<string, boolean>>(() => ({ state: manager.settingsFocus === 'state', adapter: manager.settingsFocus === 'adapter' }))
  const toggle = (key: string) => setOpen((value) => ({ ...value, [key]: !value[key] }))

  const headerRows = manager.headers
  const addHeader = () => manager.setHeaders([...headerRows, { id: Date.now(), name: '', value: '' }])
  const updateHeader = (id: number, patch: Partial<{ name: string; value: string }>) => manager.setHeaders(headerRows.map((row) => row.id === id ? { ...row, ...patch } : row))
  const removeHeader = (id: number) => manager.setHeaders(headerRows.filter((row) => row.id !== id))
  const headerNames = headerRows.map((row) => row.name.trim()).filter(Boolean)

  return (
    <>
      <Section title="服务">
        <Row label="接口协议">
          <Select label="远端协议" className="w-[300px]" value={manager.remoteProtocol} onChange={(value) => manager.setRemoteProtocol(value as RemoteProtocol)} options={[
            { value: 'openai', label: 'OpenAI Chat Completions', hint: '/v1/chat/completions 接口；Responses 接口暂不支持' },
            { value: 'python', label: 'RWKV Lightning Python' },
            { value: 'cuda', label: 'RWKV Lightning CUDA' },
            { value: 'irwkv', label: 'iRWKV（不支持 State / 适配器）' },
          ]} />
        </Row>
        {/* 新建连接只在填了内容后才报地址错误，空表单不先挂满红字。 */}
        <TextRow label="API 地址" width="w-[212px]" value={manager.remoteEndpoint} onChange={manager.setRemoteEndpoint} placeholder="https://example.com" error={isNew && !manager.remoteEndpoint.trim() ? undefined : manager.draftErrors.endpoint}
          trailing={<Button onClick={onTestRemote} disabled={manager.settingsBusy || !manager.remoteEndpoint.trim()} title="请求 /v1/models，成功后模型 ID 可从下拉里选">测试连接</Button>} />
        <TextRow label="模型 ID" value={manager.remoteModel} onChange={manager.setRemoteModel} placeholder="rwkv7-g1i-13.3b" list={manager.availableModels.map((model) => model.id)} error={isNew ? undefined : manager.draftErrors.model} />
        <TextRow label={lightning ? '服务密码' : 'API Key'} value={manager.apiKey} onChange={manager.setAPIKey} type="password" placeholder={manager.remoteProtocol === 'openai' ? 'sk-…' : '未设置'} />
      </Section>

      <Section title="高级">
        <Disclosure label="请求头" summary={headerNames.length ? headerNames.join('、') : '未设置'} open={Boolean(open.headers)} onToggle={() => toggle('headers')}>
          {headerRows.map((row) => (
            <div key={row.id} className="flex items-center gap-[8px] py-[4px]">
              <TextInput label="Header 名称" className="flex-1" value={row.name} onChange={(value) => updateHeader(row.id, { name: value })} placeholder="CF-Access-Client-Id" />
              <TextInput label="Header 值" className="flex-1" value={row.value} onChange={(value) => updateHeader(row.id, { value })} type="password" placeholder="值" />
              <Button variant="ghost" square onClick={() => removeHeader(row.id)} aria-label={`删除 Header ${row.name || row.id}`}><Trash2 size={14} /></Button>
            </div>
          ))}
          <Button variant="ghost" size="sm" className="-ml-[8px] mt-[2px]" icon={<Plus size={14} />} onClick={addHeader}>添加请求头</Button>
        </Disclosure>
        {lightning && <NumberRow label="远端聚合窗口（毫秒）" description="等一下再合批发送；0 = 不等" min={0} max={1000} defaultValue={10} value={manager.remoteBatchWaitMS} onChange={manager.setRemoteBatchWaitMS} />}
        {cuda && (
          <Disclosure label="State" summary={manager.stateId ? `当前：${manager.stateId}` : '记在这个连接上；服务端重启会清空已上传的 State'} open={Boolean(open.state)} onToggle={() => toggle('state')}>
            <StateSection manager={manager} />
          </Disclosure>
        )}
        {cuda && (
          <Disclosure label="适配器（MiSS / NoRA）" summary={manager.adapterId ? `当前：${manager.adapterId}` : '记在这个连接上，可与 State 同时使用'} open={Boolean(open.adapter)} onToggle={() => toggle('adapter')}>
            <AdapterSection manager={manager} />
          </Disclosure>
        )}
      </Section>

      {!isNew && <DeleteSection noun="连接" onRequestDelete={onRequestDelete} disabled={manager.settingsBusy} />}
    </>
  )
}

function DeleteSection({ noun, disabled, onRequestDelete }: { noun: string; disabled: boolean; onRequestDelete: () => void }) {
  return (
    <Section title="管理">
      <Row label={`删除这个${noun}`} description="连同它记住的对话格式、State 与适配器选择，不可撤销">
        <Button variant="danger" onClick={onRequestDelete} disabled={disabled} aria-label={`删除${noun}`}>删除</Button>
      </Row>
    </Section>
  )
}
