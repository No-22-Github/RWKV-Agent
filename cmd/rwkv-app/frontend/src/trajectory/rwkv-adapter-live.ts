/*
 * The running turn, rebuilt from agent:event as it streams. Events carry no
 * timestamps of their own, so each is stamped on arrival (`at`). Records stay
 * open (no duration, no result) until their *_done event arrives, which the
 * ledger shows as pending and the timeline as a start marker only.
 */
import type { TrajectoryCellProps } from './trajectory-record.ts'
import type { Builder, Group, LiveEvent, LiveTurn } from './rwkv-adapter.ts'
import { toGroupModel, userCell } from './rwkv-adapter.ts'

type Scope = { group: Group; message?: TrajectoryCellProps; tool?: TrajectoryCellProps; agents: Map<number, TrajectoryCellProps> }

export function buildLiveTurn(builder: Builder, live: LiveTurn, turn: number) {
  const { t } = builder
  builder.messageIds.set(turn, live.id)
  const groups: Group[] = [{ title: t('group.message'), cells: [userCell(builder, live.prompt, live.startedAt)] }]
  const steps = new Map<number, Scope>()
  let routeAttempt = 0
  let route: TrajectoryCellProps | undefined

  const scope = (step: number): Scope => {
    let entry = steps.get(step)
    if (entry === undefined) {
      entry = { group: { title: t('group.step', { step }), cells: [] }, agents: new Map() }
      steps.set(step, entry)
      groups.push(entry.group)
    }
    return entry
  }

  for (const event of live.events) {
    if (event.subagentIndex) { applySubagentEvent(builder, live, scope, event); continue }
    if (event.kind === 'route_start') {
      routeAttempt += 1
      route = { index: builder.next(), recordId: `route\u0000${live.id}\u0000${routeAttempt}`, kind: 'message', text: '正在选择能力组', timeSeconds: null, startedAt: event.at }
      groups.push({ title: t('group.route', { attempt: routeAttempt }), cells: [route] })
    } else if (event.kind === 'route_done' && route) {
      route.text = event.error || [event.route, ...(event.bundles || [])].filter(Boolean).join(' · ')
      route.timeSeconds = (event.at - (route.startedAt ?? event.at)) / 1000
      if (event.error) route.isError = true
    } else if (event.kind === 'model_start') {
      const entry = scope(event.step || 1)
      entry.message = { index: builder.next(), recordId: `assistant\u0000${live.id}\u0000${event.step || 1}`, kind: 'message', text: '正在决定下一步…', timeSeconds: null, startedAt: event.at }
      entry.group.cells.push(entry.message)
      builder.request(turn, event.step || 1, entry.group.title, { status: 'running', startedAt: event.at })
    } else if (event.kind === 'model_done') {
      const message = steps.get(event.step || 1)?.message
      const request = builder.requests.findLast(candidate => candidate.turn === turn && candidate.step === (event.step || 1))
      if (request) Object.assign(request, { status: event.error ? 'error' : 'complete', completedAt: event.at, ...(event.error ? { error: event.error } : {}) })
      if (message) {
        message.text = event.error || ''
        message.timeSeconds = event.durationMs !== undefined ? event.durationMs / 1000 : (event.at - (message.startedAt ?? event.at)) / 1000
        if (event.error) { message.isError = true; message.outputDetail = event.error }
      }
    } else if (event.kind === 'protocol_retry') {
      const message = steps.get(event.step || 1)?.message
      if (message) message.harness = [...(message.harness ?? []), { label: '协议修复', value: event.error || '重新请求模型', tone: 'warn' }]
    } else if (event.kind === 'tool_start' && event.tool) {
      const entry = scope(event.step || 1)
      entry.tool = {
        index: builder.next(), kind: 'tool', callId: `${live.id}\u0000${event.step}`, toolName: event.tool, text: event.tool,
        ...(event.arguments ? { previewMarkdown: event.arguments, inputDetail: event.arguments } : {}),
        timeSeconds: null, startedAt: event.at,
      }
      if (entry.message && !entry.message.text && !entry.message.isError) entry.message.text = t('layout.toolCallOnly')
      entry.group.cells.push(entry.tool)
    } else if (event.kind === 'tool_retry') {
      const tool = steps.get(event.step || 1)?.tool
      if (tool) tool.harness = [...(tool.harness ?? []), { label: '传输重试', value: `${event.attempt}/${event.maxAttempts}${event.statusCode ? ` · HTTP ${event.statusCode}` : ''} · 等待 ${event.delayMs} ms`, tone: 'warn' }]
    } else if (event.kind === 'tool_done') {
      const tool = steps.get(event.step || 1)?.tool
      if (tool) {
        tool.timeSeconds = event.durationMs !== undefined ? event.durationMs / 1000 : (event.at - (tool.startedAt ?? event.at)) / 1000
        // Live events carry no tool result; the settled trace fills it in when the turn ends.
        tool.outputDetail = event.error || t('record.noOutput')
        if (event.error) { tool.isError = true; tool.result = event.error }
      }
    }
  }
  builder.turns.push({ turn, groups: groups.filter(group => group.cells.length > 0).map(toGroupModel) })
}

function applySubagentEvent(builder: Builder, live: LiveTurn, scope: (step: number) => Scope, event: LiveEvent) {
  const { t } = builder
  const parent = scope(event.parentStep || 1)
  const index = event.subagentIndex as number
  let agent = parent.agents.get(index)
  if (agent === undefined) {
    agent = {
      index: builder.next(), kind: 'subtool', callId: `${live.id}\u0000${event.parentStep}\u0000a${index}`,
      toolName: `子 Agent ${index}`, text: `子 Agent ${index}`,
      ...(event.subagentTask ? { previewMarkdown: event.subagentTask, inputDetail: event.subagentTask } : {}),
      timeSeconds: null, startedAt: event.at,
    }
    parent.agents.set(index, agent)
    parent.group.cells.push(agent)
  }
  if (event.kind === 'subagent_done') {
    agent.timeSeconds = event.durationMs !== undefined ? event.durationMs / 1000 : (event.at - (agent.startedAt ?? event.at)) / 1000
    agent.outputDetail = event.error || t('record.noOutput')
    if (event.error) { agent.isError = true; agent.result = event.error }
  } else if (event.kind === 'tool_start' && event.tool) {
    parent.group.cells.push({
      index: builder.next(), kind: 'subtool', callId: `${live.id}\u0000${event.parentStep}\u0000a${index}\u0000${event.step}`,
      toolName: event.tool, text: event.tool,
      ...(event.arguments ? { previewMarkdown: event.arguments, inputDetail: event.arguments } : {}),
      timeSeconds: null, startedAt: event.at,
    })
  } else if (event.kind === 'tool_done') {
    const callId = `${live.id}\u0000${event.parentStep}\u0000a${index}\u0000${event.step}`
    const cell = parent.group.cells.find(candidate => candidate.callId === callId)
    if (cell) {
      cell.timeSeconds = event.durationMs !== undefined ? event.durationMs / 1000 : (event.at - (cell.startedAt ?? event.at)) / 1000
      cell.outputDetail = event.error || t('record.noOutput')
      if (event.error) { cell.isError = true; cell.result = event.error }
    }
  }
}
