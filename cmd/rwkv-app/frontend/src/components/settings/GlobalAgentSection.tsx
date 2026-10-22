import { useState } from 'react'
import type { Config } from '../../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { AgentSettingsState } from '../../state/agentSettings'
import { PANE_WIDTH, Row, SaveStatus, Section, SettingsPane, TextRow } from './ui'
import { Select } from './Select'
import ParametersSection from './ParametersSection'
import AgentBehaviorSection from './AgentBehaviorSection'

type Tab = 'generation' | 'tools' | 'search'

const TABS: { id: Tab; label: string }[] = [
  { id: 'generation', label: '生成' },
  { id: 'tools', label: '工具' },
  { id: 'search', label: '搜索与数据源' },
]

/*
 * 全局 Agent 分区：所有连接共用、和用哪个端点无关的设置，只存一份，换连接不用重设，
 * 改了下一轮对话就生效。三个标签：生成（采样、预算、提示词）、工具（开关与调度）、
 * 搜索与数据源（后端、天气源与各服务的 Key）。
 * 跟着端点走的对话格式、State 与 MiSS 适配器不在这里，在对话页输入框上方的芯片里切换。
 */
export default function GlobalAgentSection({ agent, runtimeConfig }: { agent: AgentSettingsState; runtimeConfig: Config | null }) {
  const [tab, setTab] = useState<Tab>('generation')
  return (
    <div className="flex min-h-0 min-w-0 flex-1 flex-col">
      <div className="flex-none border-b border-line">
        <div className={`${PANE_WIDTH} pt-[18px]`}>
          <header className="flex min-h-[34px] items-center gap-[12px]">
            <h2 className="m-0 min-w-0 flex-1 text-md font-semibold text-ink">Agent</h2>
            {/* 整个分区任何一项改动都在这里报「已保存」。 */}
            <SaveStatus state={agent.saveState} />
          </header>
          <p className="m-0 mt-[2px] text-sm text-ink-muted">所有连接共用；对话格式、State 与 MiSS 跟着连接走，在对话页的芯片里切换</p>
          <div role="tablist" aria-label="Agent 设置" className="mt-[12px] flex gap-[22px]">
            {TABS.map((item) => (
              <button
                key={item.id}
                role="tab"
                aria-selected={tab === item.id}
                className={`-mb-px border-0 border-b-2 bg-transparent px-0 pb-[10px] pt-[4px] text-base transition-colors ${tab === item.id ? 'border-ink font-medium text-ink' : 'border-transparent text-ink-muted hover:text-ink'}`}
                onClick={() => setTab(item.id)}
              >{item.label}</button>
            ))}
          </div>
        </div>
      </div>
      {/* 按标签重建滚动区：换标签从顶部看起。 */}
      <SettingsPane key={tab}>
        {tab === 'generation' ? <ParametersSection agent={agent} runtimeConfig={runtimeConfig} /> : tab === 'tools' ? <AgentBehaviorSection agent={agent} /> : <SearchSection agent={agent} />}
      </SettingsPane>
    </div>
  )
}

function SearchSection({ agent }: { agent: AgentSettingsState }) {
  const { value, update } = agent
  return (
    <>
      {/* 先放"怎么用"（选哪个后端、哪个数据源），再放"用什么账号"（各服务的 Key）：两类东西不混在一组里。 */}
      <Section title="网页搜索与读取">
        <Row label="搜索后端" description="查不到或出错时自动换另一个">
          <Select label="搜索后端" className="w-[240px]" value={value.webSearchBackend || 'auto'} onChange={(next) => update({ webSearchBackend: next === 'auto' ? '' : next })} options={SEARCH_BACKENDS} />
        </Row>
        <Row label="正文抓取" description="读不到的页面自动换另一个">
          <Select label="正文抓取" className="w-[240px]" value={value.webFetchBackend || 'tavily'} onChange={(next) => update({ webFetchBackend: next === 'tavily' ? '' : next })} options={FETCH_BACKENDS} />
        </Row>
      </Section>

      <Section title="实时天气">
        <Row label="数据源" description="免 API Key">
          <Select label="天气数据源" className="w-[240px]" value={value.weatherBackend || 'open-meteo'} onChange={(next) => update({ weatherBackend: next })} options={WEATHER_BACKENDS} />
        </Row>
      </Section>

      <Section title="API Key">
        <TextRow label="Brave" inputLabel="Brave API Key" description="英文搜索" width="w-[240px]" value={value.braveApiKey || ''} onChange={(next) => update({ braveApiKey: next })} type="password" placeholder="未设置" />
        <TextRow label="DeepSeek" inputLabel="DeepSeek API Key" description="中文搜索，也能读网页正文" width="w-[240px]" value={value.deepseekWebApiKey || ''} onChange={(next) => update({ deepseekWebApiKey: next })} type="password" placeholder="未设置" />
        <TextRow label="Tavily" inputLabel="Tavily API Key" description="读取网页正文" width="w-[240px]" value={value.tavilyApiKey || ''} onChange={(next) => update({ tavilyApiKey: next })} type="password" placeholder="未设置" />
      </Section>
    </>
  )
}

const SEARCH_BACKENDS = [
  { value: 'auto', label: '自动', hint: '中文查询先用 DeepSeek，其余先用 Brave' },
  { value: 'deepseek', label: 'DeepSeek 优先' },
  { value: 'brave', label: 'Brave 优先' },
]

const FETCH_BACKENDS = [
  { value: 'tavily', label: 'Tavily 优先' },
  { value: 'deepseek', label: 'DeepSeek 优先', hint: '页面更新更及时，单页较慢' },
]

const WEATHER_BACKENDS = [
  { value: 'open-meteo', label: 'Open-Meteo', hint: '7 天预报' },
  { value: 'wttr', label: 'wttr.in', hint: '3 天预报' },
]
