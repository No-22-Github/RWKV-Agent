import type { ReactNode } from 'react'
import { CloudSun, Globe2, Route, SquareTerminal, Users } from 'lucide-react'
import type { ProviderManager } from '../../state/providerManager'
import { Field, GroupTitle, NumberField, Row, Toggle } from './ui'
import { Select } from './Select'

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
  /* [标签, 字段, setter, 最小, 最大, 默认, 说明]：默认值与 api/service.go 的归一化一致。 */
  const budgets = [
    ['子 Agent 并发', 'subagentMaxParallel', 'setSubagentMaxParallel', 2, 8, 4, '一次最多同时跑几个子任务；越大越快，远端也要同时扛这么多请求'],
    ['单 Agent 步数', 'subagentMaxSteps', 'setSubagentMaxSteps', 2, 32, 4, '每个子任务最多调几次工具，到数就必须交结果'],
    ['批次超时（秒）', 'subagentTimeoutSeconds', 'setSubagentTimeoutSeconds', 1, 3600, 120, '一批子任务的总时限，没做完的按失败返回'],
    ['远端聚合窗口（毫秒）', 'remoteBatchWaitMS', 'setRemoteBatchWaitMS', 0, 1000, 10, '并发请求先等这么久再合成一批发给远端，一起解码更省时；0 表示不等'],
    ['活动批量', 'maxActiveBatch', 'setMaxActiveBatch', 1, 8, 4, '只对本地模型生效：本机同时解码的请求数，越大越吃内存'],
  ] as const

  return (
    <>
      <section className="mt-[18px]">
        <GroupTitle title="联网" />
        <Toggle icon={<Globe2 size={15} />} label="网页搜索与正文获取" description="web_search 与 web_fetch 两个工具" checked={manager.enableWeb} onChange={manager.setEnableWeb} />
        {manager.enableWeb && (
          <SubSettings>
            <Row label="搜索后端" description="先用哪个；查不到或出错时换另一个">
              <Select label="搜索后端" className="w-[230px] flex-none" value={manager.webSearchBackend} onChange={manager.setWebSearchBackend} options={SEARCH_BACKENDS} />
            </Row>
            <div className="grid grid-cols-3 gap-[10px] pt-[6px]">
              <Field label="Brave API Key" hint="英文搜索更准" value={manager.braveAPIKey} onChange={manager.setBraveAPIKey} type="password" />
              <Field label="DeepSeek API Key" hint="中文搜索更准，也给抓取兜底" value={manager.deepseekWebAPIKey} onChange={manager.setDeepseekWebAPIKey} type="password" />
              <Field label="Tavily API Key" hint="读取网页正文" value={manager.tavilyAPIKey} onChange={manager.setTavilyAPIKey} type="password" />
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
        <Toggle icon={<Route size={15} />} label="渐进式工具路由" description="先让模型挑出这次要用的几类工具，再只给它看这几类的说明；工具多时省上下文，但多一次判断" checked={manager.progressiveTools} onChange={manager.setProgressiveTools} />
        <Toggle icon={<Users size={15} />} label="并发子 Agent" description="遇到能拆开的活，模型可以一次派出 2–8 个子任务并行去做；子任务不能再派子任务" checked={manager.enableSubagents} onChange={manager.setEnableSubagents} />
        {manager.enableSubagents && (
          <SubSettings>
            <div className="grid grid-cols-2 gap-x-[16px] gap-y-[14px] py-[10px]">
              {budgets.map(([label, key, setter, min, max, fallback, hint]) => (
                <NumberField key={key} label={label} hint={hint} min={min} max={max} defaultValue={fallback} value={manager[key]} onChange={manager[setter]} />
              ))}
            </div>
          </SubSettings>
        )}
      </section>
    </>
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
