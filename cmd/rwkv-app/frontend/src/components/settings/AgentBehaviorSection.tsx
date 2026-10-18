import type { ReactNode } from 'react'
import { CloudSun, Globe2, Route, SquareTerminal, Users } from 'lucide-react'
import type { ProviderManager } from '../../state/providerManager'
import { Button, GroupTitle, NumberField, Toggle } from './ui'

type Props = {
  manager: ProviderManager
}

/*
 * 连接详情的「工具」标签：这个连接开哪些工具——联网（搜索、天气）、工作区 bash、调度（工具路由、子 Agent）
 * 及其预算。字段随连接档案自动保存；编辑运行中的远端档案时自动重连，更改即时生效。
 * 搜索 Key、搜索后端与天气数据源所有连接共用，在全局「Agent」分区（GlobalAgentSection）。
 *
 * "怎么调用模型"（对话协议、思考模式、采样、预算、附加约定与提示词预览）在「生成参数」标签。
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
        <GroupTitle title="联网" hint="Key、搜索后端与天气数据源所有连接共用" />
        <div className="flex items-center justify-between gap-[12px] pb-[2px]">
          <span className="text-2xs text-ink-muted">这里只决定这个连接开不开这些工具。</span>
          <Button variant="ghost" size="sm" className="text-brand hover:text-brand" onClick={() => manager.setSettingsSection('Agent')}>去设置 Key 与数据源</Button>
        </div>
        <Toggle icon={<Globe2 size={15} />} label="网页搜索与正文获取" description="web_search 与 web_fetch 两个工具" checked={manager.enableWeb} onChange={manager.setEnableWeb} />
        <Toggle icon={<CloudSun size={15} />} label="实时天气" description="get_weather 工具，免 API Key" checked={manager.weatherBackend !== ''} onChange={(value) => manager.setWeatherBackend(value ? 'open-meteo' : '')} />
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

/* 开关打开后才出现的子设置：左侧细线缩进，表明从属于上面那个开关。 */
function SubSettings({ children }: { children: ReactNode }) {
  return <div className="ml-[7px] border-b border-l border-line-soft pb-[8px] pl-[18px] [&>div:last-child]:border-b-0">{children}</div>
}
