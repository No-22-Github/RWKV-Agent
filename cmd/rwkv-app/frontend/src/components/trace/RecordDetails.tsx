import { useMemo, useState } from 'react'
import { Copy, X } from 'lucide-react'
import MarkdownMessage from '../../MarkdownMessage'
import { formatDuration, formatStartedAt, parseJSONValue, splitModelOutput, type TraceRecord, type TraceRecordDetail, type TraceTurn, turnSummary } from '../../ledger'
import { kindLabel } from './labels'

const DETAILS_MIN_WIDTH = 320
const DETAILS_MAX_WIDTH = 720

type DetailTabItem = { id: string; label: string }

type Props = {
  record: TraceRecord | null
  turn: TraceTurn | null
  width: number
  onWidthChange: (width: number) => void
  onClose: () => void
}

function detailTabs(record: TraceRecord): DetailTabItem[] {
  const tabs: DetailTabItem[] = [{ id: 'summary', label: '摘要' }]
  const detail = record.detail
  if (detail.prompt) tabs.push({ id: 'prompt', label: '请求' })
  if (detail.arguments) tabs.push({ id: 'arguments', label: '参数' })
  if (detail.modelOutput) tabs.push({ id: 'model-output', label: '响应' })
  if (detail.result) tabs.push({ id: 'result', label: '结果' })
  if (detail.subSteps?.length) tabs.push({ id: 'substeps', label: '子步骤' })
  if (detail.output) tabs.push({ id: 'output', label: '输出' })
  if (record.kind === 'output' && detail.answerContractRepaired) tabs.push({ id: 'repair', label: '修复对比' })
  if (detail.retries?.length) tabs.push({ id: 'retries', label: '重试' })
  tabs.push({ id: 'raw', label: '原文' })
  return tabs
}

/* 右侧详情面板：按记录 kind 动态出 tab，宽度 320–720 可拖。 */
export default function RecordDetails({ record, turn, width, onWidthChange, onClose }: Props) {
  const tabs = useMemo(() => (record ? detailTabs(record) : []), [record])
  const [activeTab, setActiveTab] = useState<string>('summary')
  const tab = tabs.some((item) => item.id === activeTab) ? activeTab : 'summary'

  function startDrag(event: React.PointerEvent) {
    event.preventDefault()
    const startX = event.clientX
    const startWidth = width
    function onMove(moveEvent: PointerEvent) {
      const next = startWidth + (startX - moveEvent.clientX)
      onWidthChange(Math.min(DETAILS_MAX_WIDTH, Math.max(DETAILS_MIN_WIDTH, next)))
    }
    function onUp() {
      window.removeEventListener('pointermove', onMove)
      window.removeEventListener('pointerup', onUp)
    }
    window.addEventListener('pointermove', onMove)
    window.addEventListener('pointerup', onUp)
  }

  return (
    <aside
      className="relative flex flex-none flex-col overflow-auto border-l border-line bg-paper-soft"
      style={{ width }}
      aria-label="事件详情"
    >
      <div
        role="separator"
        aria-orientation="vertical"
        aria-label="拖拽调整详情宽度"
        className="absolute inset-y-0 left-0 z-[2] w-[5px] cursor-col-resize hover:bg-brand/30"
        onPointerDown={startDrag}
      />
      <div className="flex items-start justify-between gap-[10px] px-5 pb-[12px] pt-[20px]">
        <div className="flex min-w-0 flex-col gap-[5px]">
          <span className="font-mono text-2xs uppercase tracking-[.14em] text-ink-muted">
            {record ? `#${record.index} · ${kindLabel(record.kind)}` : '轮次概览'}
          </span>
          <strong className="truncate text-base font-semibold text-ink">
            {record ? record.title : turn ? `Turn ${turn.turn}` : '未选择'}
          </strong>
          {record && <span className="truncate text-xs text-ink-muted">{record.text}</span>}
        </div>
        <button
          aria-label="关闭检查器"
          className="grid h-[24px] w-[24px] flex-none place-items-center border-0 bg-transparent text-ink-muted hover:text-ink"
          onClick={onClose}
        ><X size={14} /></button>
      </div>

      {!record && turn && <TurnOverview turn={turn} />}
      {record && tabs.length > 1 && (
        <div className="flex gap-[14px] border-b border-line px-5">
          {tabs.map((item) => (
            <button
              key={item.id}
              role="tab"
              aria-selected={tab === item.id}
              className={`border-0 border-b-2 bg-transparent pb-[8px] text-xs ${tab === item.id ? 'border-brand font-semibold text-brand' : 'border-transparent text-ink-muted'}`}
              onClick={() => setActiveTab(item.id)}
            >{item.label}</button>
          ))}
        </div>
      )}
      {record && <div className="min-h-0 flex-1 overflow-auto pb-6">{tab === 'summary' ? <SummaryTab record={record} /> : <ContentTab record={record} tab={tab} />}</div>}
    </aside>
  )
}

function TurnOverview({ turn }: { turn: TraceTurn }) {
  const rows: Array<[string, string]> = [
    ['步数', String(turn.header.steps)],
    ['工具调用', String(turn.header.tools)],
    ['子 Agent', String(turn.header.subagents)],
    ['总时长', formatDuration(turn.header.durationMs || undefined)],
  ]
  if (turn.header.route) rows.push(['路由', turn.header.route])
  return (
    <div className="px-5">
      <p className="mb-[10px] mt-0 text-xs leading-[1.65] text-ink-soft">{turnSummary(turn)}</p>
      <KeyRows rows={rows} />
      <div className="mt-[12px] flex flex-col gap-[5px]">
        {turn.groups.map((group) => (
          <div key={group.title} className="flex items-center gap-[8px] text-xs text-ink-muted">
            <span className="font-mono text-2xs uppercase tracking-[.1em] text-ink-ghost">{group.title}</span>
            <span>{group.records.length} 条</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function SummaryTab({ record }: { record: TraceRecord }) {
  const detail = record.detail
  const rows: Array<[string, string]> = [['状态', record.isError ? '失败' : record.state === 'running' ? '进行中' : '完成']]
  if (record.startedAtMs) rows.push(['开始时间', formatStartedAt(record.startedAtMs)])
  if (record.timeMs) rows.push(['耗时', formatDuration(record.timeMs)])
  if (record.tokens) rows.push(['Tokens', `${record.tokens.input.toLocaleString('zh-CN')} 入 / ${record.tokens.output.toLocaleString('zh-CN')} 出`])
  if (record.tokens?.cacheRead) rows.push(['缓存命中', `${record.tokens.cacheRead.toLocaleString('zh-CN')} tok`])
  if (record.tokens?.reasoning) rows.push(['推理', `${record.tokens.reasoning.toLocaleString('zh-CN')} tok`])
  if (detail.stage) rows.push(['阶段', detail.stage])
  if (detail.actionType) rows.push(['动作', detail.actionType])
  if (detail.finishReason) rows.push(['结束原因', detail.finishReason])
  if (detail.route) rows.push(['路由', [detail.route, ...(detail.bundles || [])].filter(Boolean).join(' · ')])
  if (detail.status) rows.push(['子任务', detail.status])
  if (detail.protocolError) rows.push(['协议修复', detail.protocolRepaired ? `已修复 · ${detail.protocolError}` : `未修复 · ${detail.protocolError}`])
  if (detail.stageViolation) rows.push(['阶段约束', '当前阶段不接受该动作'])
  if (detail.noToolRationale) rows.push(['直接回答理由', detail.noToolRationale])
  if (detail.noToolAnswer) rows.push(['候选答案', detail.noToolAnswer])
  if (detail.executed !== undefined) rows.push(['已执行', detail.executed ? '是' : '否'])
  if (detail.evidence !== undefined) rows.push(['证据', detail.evidence ? '有效' : '无效'])
  if (detail.unavailable) rows.push(['工具状态', '不可用'])
  if (detail.rejected) rows.push(['拒绝原因', detail.rejected])
  if (detail.forcedAnswerReason) rows.push(['修复原因', detail.forcedAnswerReason])
  if (detail.answerViolations?.length) rows.push(['契约违规', detail.answerViolations.join('；')])
  if (detail.error) rows.push(['错误', detail.error])
  return (
    <div className="px-5 pt-[10px]">
      {detail.answerContractRepaired && (
        <div className="mb-[10px] border-l-2 border-warning bg-warning/10 px-[10px] py-2 text-xs leading-[1.6] text-warning">
          答案契约已修复：{detail.forcedAnswerReason || detail.answerViolations?.join(', ') || '输出被改写以满足契约'}
        </div>
      )}
      {record.text && record.kind !== 'user' && (
        <p className="mb-[12px] mt-0 text-xs leading-[1.7] text-ink-soft [overflow-wrap:anywhere]">{record.text}</p>
      )}
      <KeyRows rows={rows} />
    </div>
  )
}

function ContentTab({ record, tab }: { record: TraceRecord; tab: string }) {
  const detail = record.detail
  if (tab === 'prompt') return <PreBlock label="请求 Prompt" value={detail.prompt || ''} meta={promptMeta(detail)} />
  if (tab === 'arguments') return <PreBlock label="调用参数" value={pretty(detail.arguments)} />
  if (tab === 'result') return <PreBlock label="工具结果" value={pretty(detail.result)} error={record.isError} />
  if (tab === 'model-output') {
    const { thinking, rest } = splitModelOutput(detail.modelOutput)
    return (
      <div className="px-5 pt-[10px]">
        {thinking && (
          <div className="mb-[12px]">
            <div className="mb-[4px] font-mono text-2xs uppercase tracking-[.12em] text-ink-ghost">思考内容</div>
            <pre className="m-0 overflow-auto whitespace-pre-wrap border-l-2 border-line bg-paper-soft px-[10px] py-[8px] font-mono text-xs leading-[1.7] text-ink-ghost [overflow-wrap:anywhere]">{thinking}</pre>
          </div>
        )}
        {rest && <PreBlock label={thinking ? '输出' : '模型输出'} value={rest} />}
        {!thinking && !rest && <PreBlock label="模型输出" value={detail.modelOutput || '（空）'} />}
      </div>
    )
  }
  if (tab === 'output') {
    return (
      <div className="px-5 pt-[10px]">
        <div className="turn-answer font-serif text-base leading-[1.85] text-ink [overflow-wrap:anywhere]">
          <MarkdownMessage content={detail.output || ''} />
        </div>
      </div>
    )
  }
  if (tab === 'repair') {
    return (
      <div className="flex flex-col gap-[12px] px-5 pt-[10px]">
        <Section title="修复后输出"><PreBlock value={detail.output || ''} /></Section>
        <Section title="原始输出"><PreBlock value={detail.originalOutput || '（无）'} /></Section>
      </div>
    )
  }
  if (tab === 'raw') return <RawTab detail={record.detail} />
  if (tab === 'substeps') {
    return (
      <div className="flex flex-col gap-[8px] px-5 pt-[10px]">
        {(detail.subSteps || []).map((step, index) => (
          <div key={`${step.step}-${index}`} className="border-l-2 border-line pl-[10px]">
            <div className="font-mono text-xs text-ink">#{step.step} {step.tool || '—'}</div>
            {step.arguments && <div className="truncate font-mono text-2xs text-ink-muted">{step.arguments}</div>}
            {step.error && <div className="text-2xs text-danger">{step.error}</div>}
            <div className="text-2xs text-ink-ghost">{step.status}</div>
          </div>
        ))}
      </div>
    )
  }
  if (tab === 'retries') {
    return (
      <div className="flex flex-col gap-[6px] px-5 pt-[10px]">
        {(detail.retries || []).map((retry, index) => (
          <div key={index} className="font-mono text-xs text-ink-soft">
            Attempt {retry.attempt}/{retry.maxAttempts} · 等待 {formatDuration(retry.delayMs)}{retry.statusCode ? ` · HTTP ${retry.statusCode}` : ''}
          </div>
        ))}
      </div>
    )
  }
  return null
}

/* 原文页签：规整（长文本真实换行、字段平铺）与原始 JSON 两种视图切换。 */
function RawTab({ detail }: { detail: TraceRecordDetail }) {
  const [mode, setMode] = useState<'formatted' | 'json'>('formatted')
  const value = mode === 'json'
    ? JSON.stringify(detail, null, 2)
    : formatDetailReadable(detail)
  return (
    <div className="px-5 pt-[10px]">
      <div className="mb-[6px] flex items-center gap-[6px]">
        <div className="flex border border-line bg-paper-soft p-[2px]">
          {(['formatted', 'json'] as const).map((item) => (
            <button
              key={item}
              aria-pressed={mode === item}
              className={`h-[22px] border-0 px-[8px] text-2xs ${mode === item ? 'bg-paper font-medium text-brand shadow-sm' : 'bg-transparent text-ink-muted'}`}
              onClick={() => setMode(item)}
            >{item === 'formatted' ? '规整' : '原文 JSON'}</button>
          ))}
        </div>
        <span className="text-2xs text-ink-ghost">{mode === 'formatted' ? '长文本按真实换行展开' : '与存储一致的调试视图'}</span>
      </div>
      <pre className="m-0 overflow-auto whitespace-pre-wrap font-mono text-xs leading-[1.7] text-ink-soft [overflow-wrap:anywhere]">{value}</pre>
    </div>
  )
}

function formatDetailReadable(detail: TraceRecordDetail): string {
  return Object.entries(detail)
    .filter(([, value]) => value !== undefined && !(Array.isArray(value) && value.length === 0))
    .map(([key, value]) => {
      if (typeof value === 'string') {
        if (value.includes('\n') || value.length > 80) {
          const block = value.split('\n').map((line) => `  ${line}`).join('\n')
          return `${key}:\n${block}`
        }
        return `${key}: ${value}`
      }
      return `${key}: ${JSON.stringify(value, null, 2)}`
    })
    .join('\n\n')
}

function promptMeta(detail: TraceRecordDetail) {
  const parts: string[] = []
  if (detail.promptBytes) parts.push(`${detail.promptBytes.toLocaleString('zh-CN')} bytes`)
  if (detail.promptTruncated) parts.push('已截断')
  if (detail.maxOutputTokens) parts.push(`max ${detail.maxOutputTokens}`)
  if (detail.stops?.length) parts.push(`stops: ${detail.stops.join(', ')}`)
  return parts.join(' · ')
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="mb-[5px] font-mono text-2xs uppercase tracking-[.12em] text-ink-muted">{title}</div>
      {children}
    </div>
  )
}

function PreBlock({ label, value, error, meta }: { label?: string; value: string; error?: boolean; meta?: string }) {
  const [copied, setCopied] = useState(false)
  return (
    <div className={label || meta ? 'px-5 pt-[10px]' : ''}>
      {label && (
        <div className="mb-[5px] flex items-center gap-[8px]">
          <span className="font-mono text-2xs uppercase tracking-[.12em] text-ink-muted">{label}</span>
          {meta && <span className="text-2xs text-ink-ghost">{meta}</span>}
          <button
            aria-label={`复制${label || ''}`}
            className="ml-auto flex items-center gap-[4px] border-0 bg-transparent p-0 text-2xs text-ink-muted hover:text-brand"
            onClick={() => {
              void navigator.clipboard?.writeText(value)
              setCopied(true)
              setTimeout(() => setCopied(false), 1200)
            }}
          ><Copy size={11} />{copied ? '已复制' : '复制'}</button>
        </div>
      )}
      <pre className={`m-0 overflow-auto whitespace-pre-wrap font-mono text-xs leading-[1.7] [overflow-wrap:anywhere] ${error ? 'text-danger' : 'text-ink-soft'}`}>{value}</pre>
    </div>
  )
}

function KeyRows({ rows }: { rows: Array<[string, string]> }) {
  return (
    <dl className="m-0">
      {rows.map(([key, value]) => (
        <div key={key} className="grid min-h-[26px] grid-cols-[88px_minmax(0,1fr)] items-center gap-[10px] border-b border-line-soft py-[3px]">
          <dt className="text-xs text-ink-muted">{key}</dt>
          <dd className={`m-0 text-xs [overflow-wrap:anywhere] ${key === '错误' || key === '契约违规' ? 'text-danger' : 'text-ink'}`}>{value}</dd>
        </div>
      ))}
    </dl>
  )
}

function pretty(value?: string) {
  if (!value) return ''
  const parsed = parseJSONValue(value)
  return typeof parsed === 'string' ? parsed : JSON.stringify(parsed, null, 2)
}
