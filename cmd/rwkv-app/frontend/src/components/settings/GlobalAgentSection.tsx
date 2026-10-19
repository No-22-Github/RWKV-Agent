import type { AgentSettingsState } from '../../state/agentSettings'
import { Row, SaveStatus, Section, SettingsPane, TextRow } from './ui'
import { Select } from './Select'

/*
 * 全局 Agent 分区：所有连接共用、和用哪个模型无关的设置——搜索与抓取的 Key、
 * 搜索与正文抓取先用谁、天气数据源。只存一份，换连接不用重填，改了下一轮对话就生效。
 * 某个连接开不开这些工具，在那个连接详情的「工具」标签里。
 */
export default function GlobalAgentSection({ agent }: { agent: AgentSettingsState }) {
  const { value, update } = agent
  return (
    <SettingsPane>
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

      {/* 保存状态挂在最常敲字的地方：整页任何一项改动都在这里报「已保存」。 */}
      <Section title="API Key" action={<SaveStatus state={agent.saveState} />}>
        <TextRow label="Brave" inputLabel="Brave API Key" description="英文搜索" width="w-[240px]" value={value.braveApiKey || ''} onChange={(next) => update({ braveApiKey: next })} type="password" placeholder="未设置" />
        <TextRow label="DeepSeek" inputLabel="DeepSeek API Key" description="中文搜索，也能读网页正文" width="w-[240px]" value={value.deepseekWebApiKey || ''} onChange={(next) => update({ deepseekWebApiKey: next })} type="password" placeholder="未设置" />
        <TextRow label="Tavily" inputLabel="Tavily API Key" description="读取网页正文" width="w-[240px]" value={value.tavilyApiKey || ''} onChange={(next) => update({ tavilyApiKey: next })} type="password" placeholder="未设置" />
      </Section>
    </SettingsPane>
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
