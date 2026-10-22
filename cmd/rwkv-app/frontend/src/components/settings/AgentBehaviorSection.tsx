import type { AgentSettingsState } from '../../state/agentSettings'
import { NumberRow, Section, Toggle } from './ui'

type Props = {
  agent: AgentSettingsState
}

/*
 * 全局 Agent 分区的「工具」标签：开哪些工具——联网（搜索、天气）、工作区 bash、调度（工具路由、子 Agent）
 * 及其预算。所有连接共用；改动自动保存，下一轮对话生效（远端不重连，本地模型不重新加载）。
 * 搜索 Key、搜索后端与天气数据源在旁边的「搜索与数据源」标签。
 */
export default function AgentBehaviorSection({ agent }: Props) {
  const { value, update } = agent
  /* [标签, 字段, 最小, 最大, 默认, 说明]：默认值与 api/service.go 的归一化一致。 */
  const budgets = [
    ['子 Agent 并发', 'subagentMaxParallel', 2, 8, 4, '越大越快，远端也要同时扛这么多请求'],
    ['单 Agent 步数', 'subagentMaxSteps', 2, 32, 4, undefined],
    ['批次超时（秒）', 'subagentTimeoutSeconds', 1, 3600, 120, '没做完的按失败返回'],
  ] as const

  return (
    <>
      <Section title="联网">
        <Toggle label="网页搜索与正文获取" checked={value.enableWeb} onChange={(next) => update({ enableWeb: next })} />
        <Toggle label="实时天气" checked={value.enableWeather} onChange={(next) => update({ enableWeather: next })} />
      </Section>

      <Section title="工作区">
        <Toggle label="沙箱 bash" description="无网络、无 Python，只能碰工作区里的文件" checked={value.enableBash} onChange={(next) => update({ enableBash: next })} />
      </Section>

      <Section title="调度">
        <Toggle label="渐进式工具路由" description="先挑出要用的几类工具再看说明；省上下文，多一次判断" checked={value.progressiveTools} onChange={(next) => update({ progressiveTools: next })} />
        <Toggle label="并发子 Agent" description="能拆开的活一次派出 2–8 个子任务并行做" checked={value.enableSubagents} onChange={(next) => update({ enableSubagents: next })} />
        {value.enableSubagents && (
          // 开关打开后才出现的子设置：左侧细线缩进，表明从属于上面那个开关。
          <div className="ml-[2px] border-b border-l-2 border-line-soft pl-[16px] last:border-b-0 [&>div:last-child]:border-b-0">
            {budgets.map(([label, key, min, max, fallback, hint]) => (
              <NumberRow key={key} label={label} description={hint} min={min} max={max} defaultValue={fallback} value={value[key] || fallback} onChange={(next) => update({ [key]: next })} />
            ))}
          </div>
        )}
      </Section>
    </>
  )
}
