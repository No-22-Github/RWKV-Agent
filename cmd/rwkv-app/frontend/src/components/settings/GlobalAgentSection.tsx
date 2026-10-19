import type { AgentSettingsState } from '../../state/agentSettings'
import { Field, GroupTitle, Row, SaveStatus, SettingsPane } from './ui'
import { Select } from './Select'

/*
 * 全局 Agent 分区：所有连接共用、和用哪个模型无关的设置——搜索与抓取的 Key、
 * 搜索与正文抓取先用谁、天气数据源。只存一份，换连接不用重填。某个连接开不开这些工具，
 * 在那个连接详情的「工具」标签里。
 */
export default function GlobalAgentSection({ agent }: { agent: AgentSettingsState }) {
  const { value, update } = agent
  return (
    <SettingsPane>
      <div className="mb-[14px] flex items-center justify-between gap-[12px]">
        <p className="m-0 text-xs leading-[1.65] text-ink-muted">这里的设置所有连接共用，改了下一轮对话就生效。每个连接开不开网页搜索、天气，在连接详情的「工具」标签里。</p>
        <SaveStatus state={agent.saveState} />
      </div>

      <section>
        <GroupTitle title="网页搜索与正文获取" hint="web_search · web_fetch" />
        <Row label="搜索后端" description="先用哪个；查不到或出错时换另一个">
          <Select label="搜索后端" className="w-[230px] flex-none" value={value.webSearchBackend || 'auto'} onChange={(next) => update({ webSearchBackend: next === 'auto' ? '' : next })} options={SEARCH_BACKENDS} />
        </Row>
        <Row label="正文抓取" description="先用哪个；读不到的页面换另一个">
          <Select label="正文抓取" className="w-[230px] flex-none" value={value.webFetchBackend || 'tavily'} onChange={(next) => update({ webFetchBackend: next === 'tavily' ? '' : next })} options={FETCH_BACKENDS} />
        </Row>
        <div className="grid grid-cols-3 gap-[10px] pt-[6px]">
          <Field label="Brave API Key" hint="英文搜索更准" value={value.braveApiKey || ''} onChange={(next) => update({ braveApiKey: next })} type="password" />
          <Field label="DeepSeek API Key" hint="中文搜索更准，也能读网页正文" value={value.deepseekWebApiKey || ''} onChange={(next) => update({ deepseekWebApiKey: next })} type="password" />
          <Field label="Tavily API Key" hint="读取网页正文" value={value.tavilyApiKey || ''} onChange={(next) => update({ tavilyApiKey: next })} type="password" />
        </div>
        <p className="m-0 pb-[4px] pt-[4px] text-2xs leading-[1.6] text-ink-muted">搜索用 Brave 或 DeepSeek，填一个就能用；正文抓取默认先用 Tavily，读不到的页面再用 DeepSeek 补，也可以改成先用 DeepSeek。都不填时工具仍在，调用会提示未配置。</p>
      </section>

      <section className="mt-[22px]">
        <GroupTitle title="实时天气" hint="get_weather · 免 API Key" />
        <Row label="天气数据源">
          <Select label="天气数据源" className="w-[230px] flex-none" value={value.weatherBackend || 'open-meteo'} onChange={(next) => update({ weatherBackend: next })} options={WEATHER_BACKENDS} />
        </Row>
      </section>
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
