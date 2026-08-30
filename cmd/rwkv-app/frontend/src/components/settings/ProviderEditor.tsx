import { Cloud, Cpu, Plus, Trash2 } from 'lucide-react'
import type { ProviderManager } from '../../state/providerManager'
import { Field, GroupTitle } from './ui'
import ProfileFooter from './ProfileFooter'

type Props = {
  manager: ProviderManager
  ready: boolean
  onTestRemote: () => void
  onSave: () => void
  onSaveAndUse: () => void
  onRequestDelete: () => void
}

/* 右侧编辑器：点列表中的档案进入，表单即档案本身。只承载连接身份：模型来源与凭据；
 * 工具协议、思考模式、网页、子 Agent 等行为字段在独立的 Agent 分区。 */
export default function ProviderEditor({ manager, ready, onTestRemote, onSave, onSaveAndUse, onRequestDelete }: Props) {
  const isNew = manager.editingProviderId === ''
  const headerRows = manager.headers
  const addHeader = () => manager.setHeaders([...headerRows, { id: Date.now(), name: '', value: '' }])
  const updateHeader = (id: number, patch: Partial<{ name: string; value: string }>) => manager.setHeaders(headerRows.map((row) => row.id === id ? { ...row, ...patch } : row))
  const removeHeader = (id: number) => manager.setHeaders(headerRows.filter((row) => row.id !== id))

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
            <p className="mb-0 mt-[12px] text-xs leading-[1.65] text-ink-muted">填写连接信息后点击「保存」存为档案；「保存并使用」会保存并立即切换为当前运行连接。工具协议与思考模式在「Agent」分区。</p>
          )}

          <section className="mt-[18px] pb-[24px]">
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
        </div>
      </div>

      <ProfileFooter manager={manager} ready={ready} onTestRemote={onTestRemote} onSave={onSave} onSaveAndUse={onSaveAndUse} onRequestDelete={onRequestDelete} />
    </div>
  )
}
