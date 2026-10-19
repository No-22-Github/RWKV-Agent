import type { ProviderManager } from '../../state/providerManager'
import { Button, NumberRow, Section, Toggle } from './ui'

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
    ['子 Agent 并发', 'subagentMaxParallel', 'setSubagentMaxParallel', 2, 8, 4, '越大越快，远端也要同时扛这么多请求'],
    ['单 Agent 步数', 'subagentMaxSteps', 'setSubagentMaxSteps', 2, 32, 4, undefined],
    ['批次超时（秒）', 'subagentTimeoutSeconds', 'setSubagentTimeoutSeconds', 1, 3600, 120, '没做完的按失败返回'],
    ['远端聚合窗口（毫秒）', 'remoteBatchWaitMS', 'setRemoteBatchWaitMS', 0, 1000, 10, '等一下再合批发送；0 = 不等'],
    ['活动批量', 'maxActiveBatch', 'setMaxActiveBatch', 1, 8, 4, '只对本地模型生效'],
  ] as const

  return (
    <>
      <Section title="联网" action={<Button variant="ghost" size="sm" onClick={() => manager.setSettingsSection('Agent')}>Key 与数据源</Button>}>
        <Toggle label="网页搜索与正文获取" checked={manager.enableWeb} onChange={manager.setEnableWeb} />
        <Toggle label="实时天气" checked={manager.weatherBackend !== ''} onChange={(value) => manager.setWeatherBackend(value ? 'open-meteo' : '')} />
      </Section>

      <Section title="工作区">
        <Toggle label="沙箱 bash" description="无网络、无 Python，只能碰工作区里的文件" checked={manager.enableBash} onChange={manager.setEnableBash} />
      </Section>

      <Section title="调度">
        <Toggle label="渐进式工具路由" description="先挑出要用的几类工具再看说明；省上下文，多一次判断" checked={manager.progressiveTools} onChange={manager.setProgressiveTools} />
        <Toggle label="并发子 Agent" description="能拆开的活一次派出 2–8 个子任务并行做" checked={manager.enableSubagents} onChange={manager.setEnableSubagents} />
        {manager.enableSubagents && (
          // 开关打开后才出现的子设置：左侧细线缩进，表明从属于上面那个开关。
          <div className="ml-[2px] border-b border-l-2 border-line-soft pl-[16px] last:border-b-0 [&>div:last-child]:border-b-0">
            {budgets.map(([label, key, setter, min, max, fallback, hint]) => (
              <NumberRow key={key} label={label} description={hint} min={min} max={max} defaultValue={fallback} value={manager[key]} onChange={manager[setter]} />
            ))}
          </div>
        )}
      </Section>
    </>
  )
}
