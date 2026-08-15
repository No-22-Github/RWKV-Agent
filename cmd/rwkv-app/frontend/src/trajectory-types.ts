export type ToolRetryTrace = {
  attempt: number
  maxAttempts: number
  statusCode?: number
  delayMs: number
}

export type SubagentStep = {
  step: number
  tool: string
  arguments?: string
  status: 'running' | 'completed' | 'failed'
  error?: string
  retries?: ToolRetryTrace[]
}

export type SubagentTrace = {
  index: number
  task: string
  status: 'running' | 'completed' | 'failed'
  error?: string
  route?: string
  bundles?: string[]
  durationMs?: number
  output?: string
  sources?: string[]
  steps?: SubagentStep[]
}

export type ToolTrace = {
  step: number
  tool: string
  arguments?: string
  status: 'running' | 'completed' | 'failed'
  error?: string
  retries?: ToolRetryTrace[]
  subagents?: SubagentTrace[]
}
