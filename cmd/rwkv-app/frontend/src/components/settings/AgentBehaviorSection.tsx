import type { ReactNode } from 'react'
import { CloudSun, Globe2, Route, SquareTerminal, Users } from 'lucide-react'
import type { ProviderManager } from '../../state/providerManager'
import { Field, GroupTitle, Row, SettingsPane, Toggle, SaveStatus } from './ui'
import { Select } from './Select'
import { autosaveHint } from './autosaveHint'

type Props = {
  manager: ProviderManager
}

/*
 * Agent 能力分区：模型能做什么——联网（搜索、天气）、工作区工具、调度（工具路由、子 Agent）。字段随当前编辑的
 * 连接档案自动保存；编辑运行中的远端档案时自动重连，更改即时生效——因此本分区
 * 没有保存按钮。删除连接等身份操作在连接页。
 *
 * "怎么调用模型"（对话协议、思考模式、采样、预算、附加约定与提示词预览）在参数分区。
 */
export default function AgentBehaviorSection({ manager }: Props) {
  const budgets = [
    ['活动批量', 'maxActiveBatch', 'setMaxActiveBatch', 1, 8],
    ['子 Agent 并发', 'subagentMaxParallel', 'setSubagentMaxParallel', 2, 8],
    ['单 Agent 步数', 'subagentMaxSteps', 'setSubagentMaxSteps', 2, 32],
    ['批次超时（秒）', 'subagentTimeoutSeconds', 'setSubagentTimeoutSeconds', 1, 3600],
    ['远端聚合窗口（毫秒）', 'remoteBatchWaitMS', 'setRemoteBatchWaitMS', 0, 1000],
  ] as const

  return (
    <SettingsPane>
      <div className="mb-[10px] flex items-center justify-between gap-[12px]">
        <GroupTitle title="Agent 能力" hint={autosaveHint(manager)} />
        <SaveStatus state={manager.saveState} />
      </div>

      <section className="mt-[18px]">
        <GroupTitle title="联网" />
        <Toggle icon={<Globe2 size={15} />} label="网页搜索与正文获取" description="web_search 与 web_fetch 两个工具" checked={manager.enableWeb} onChange={manager.setEnableWeb} />
        {manager.enableWeb && (
          <SubSettings>
            <Row label="搜索后端" description="先用哪个；查不到或出错时换另一个">
              <Select label="搜索后端" className="w-[230px] flex-none" value={manager.webSearchBackend} onChange={manager.setWebSearchBackend} options={SEARCH_BACKENDS} />
            </Row>
            <div className="grid grid-cols-3 gap-[10px] pt-[6px]">
              <Field label="Brave API Key" value={manager.braveAPIKey} onChange={manager.setBraveAPIKey} type="password" />
              <Field label="DeepSeek API Key" value={manager.deepseekWebAPIKey} onChange={manager.setDeepseekWebAPIKey} type="password" />
              <Field label="Tavily API Key" value={manager.tavilyAPIKey} onChange={manager.setTavilyAPIKey} type="password" />
            </div>
            <p className="m-0 pb-[4px] text-2xs leading-[1.6] text-ink-muted">搜索用 Brave 或 DeepSeek，填一个就能用；正文抓取用 Tavily，读不到的页面再用 DeepSeek 补。</p>
          </SubSettings>
        )}
        <Toggle icon={<CloudSun size={15} />} label="实时天气" description="get_weather 工具，免 API Key" checked={manager.weatherBackend !== ''} onChange={(value) => manager.setWeatherBackend(value ? 'open-meteo' : '')} />
        {manager.weatherBackend !== '' && (
          <SubSettings>
            <Row label="天气数据源">
              <Select label="天气数据源" className="w-[230px] flex-none" value={manager.weatherBackend} onChange={manager.setWeatherBackend} options={WEATHER_BACKENDS} />
            </Row>
          </SubSettings>
        )}
      </section>

      <section className="mt-[22px]">
        <GroupTitle title="工作区" />
        <Toggle icon={<SquareTerminal size={15} />} label="沙箱 bash" description="在工作区里跑 grep、sed、awk 等命令；无网络、无 Python，碰不到工作区以外的文件" checked={manager.enableBash} onChange={manager.setEnableBash} />
      </section>

      <section className="mt-[22px]">
        <GroupTitle title="调度" />
        <Toggle icon={<Route size={15} />} label="渐进式工具路由" description="可选：先由短 Router 选择能力组，再暴露 schema" checked={manager.progressiveTools} onChange={manager.setProgressiveTools} />
        <Toggle icon={<Users size={15} />} label="并发子 Agent" description="一次派发 2–8 个独立任务，不允许嵌套委派" checked={manager.enableSubagents} onChange={manager.setEnableSubagents} />
        {manager.enableSubagents && (
          <SubSettings>
            <div className="grid grid-cols-3 gap-[10px] py-[6px]">
              {budgets.map(([label, key, setter, min, max]) => (
                <label key={key} className="flex flex-col gap-[5px] text-xs text-ink-muted">
                  {label}
                  <input aria-label={label} className="h-[36px] rounded-md border border-line bg-paper-wash px-[10px] text-base text-ink outline-0 focus:border-brand" type="number" min={min} max={max} value={manager[key]} onChange={(event) => manager[setter](Number(event.target.value))} />
                </label>
              ))}
            </div>
          </SubSettings>
        )}
      </section>
    </SettingsPane>
  )
}

const SEARCH_BACKENDS = [
  { value: 'auto', label: '自动', hint: '中文查询先用 DeepSeek，其余先用 Brave' },
  { value: 'deepseek', label: 'DeepSeek 优先' },
  { value: 'brave', label: 'Brave 优先' },
]

const WEATHER_BACKENDS = [
  { value: 'open-meteo', label: 'Open-Meteo', hint: '7 天预报' },
  { value: 'wttr', label: 'wttr.in', hint: '3 天预报' },
]

/* 开关打开后才出现的子设置：左侧细线缩进，表明从属于上面那个开关。 */
function SubSettings({ children }: { children: ReactNode }) {
  return <div className="ml-[7px] border-b border-l border-line-soft pb-[8px] pl-[18px] [&>div:last-child]:border-b-0">{children}</div>
}
