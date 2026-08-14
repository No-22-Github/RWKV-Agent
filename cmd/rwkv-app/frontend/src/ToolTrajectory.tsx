import { useEffect, useRef, useState } from 'react'
import { CheckCircle2, ChevronDown, LoaderCircle, Wrench, XCircle } from 'lucide-react'

export type ToolTrace = {
  step: number
  tool: string
  status: 'running' | 'completed' | 'failed'
  error?: string
}

type ToolTrajectoryProps = {
  calls: ToolTrace[]
  done: boolean
  status?: string
}

export default function ToolTrajectory({ calls, done, status }: ToolTrajectoryProps) {
  const [expanded, setExpanded] = useState(false)
  const [animationKey, setAnimationKey] = useState(0)
  const failures = calls.filter((call) => call.status === 'failed').length
  const summary = failures > 0
    ? `完成 ${calls.length} 次工具调用，${failures} 次失败`
    : `已完成 ${calls.length} 次工具调用`
  const latest = done ? summary : status || 'Agent 正在工作…'
  const [current, setCurrent] = useState(latest)
  const [outgoing, setOutgoing] = useState<string | null>(null)
  const previous = useRef(latest)
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (latest === previous.current) return
    if (timer.current) clearTimeout(timer.current)
    setOutgoing(previous.current)
    setCurrent(latest)
    previous.current = latest
    timer.current = setTimeout(() => setOutgoing(null), 350)
    return () => {
      if (timer.current) clearTimeout(timer.current)
    }
  }, [latest])

  function toggle() {
    if (!done || calls.length === 0) return
    setExpanded((value) => {
      if (!value) setAnimationKey((key) => key + 1)
      return !value
    })
  }

  return (
    <div className={`tool-trajectory${failures > 0 ? ' has-failures' : ''}`}>
      <div className="trajectory-stage" aria-live="polite">
        <div className={outgoing ? 'trajectory-track sliding' : 'trajectory-track'}>
          {outgoing && <TrajectoryPill text={outgoing} done={false} />}
          <button
            type="button"
            className={`trajectory-pill${done ? ' done' : ''}`}
            onClick={toggle}
            disabled={!done || calls.length === 0}
            aria-expanded={done ? expanded : undefined}
          >
            {done
              ? failures > 0 ? <XCircle size={15} /> : <CheckCircle2 size={15} />
              : <LoaderCircle className="spin" size={15} />}
            <span>{current}</span>
            {done && calls.length > 0 && <ChevronDown className={expanded ? 'open' : ''} size={15} />}
          </button>
        </div>
      </div>

      {done && calls.length > 0 && (
        <div className={`trajectory-body${expanded ? ' open' : ''}`}>
          <ol className="trajectory-list" key={animationKey}>
            {calls.map((call, index) => (
              <li
                className={`trajectory-item ${call.status}`}
                style={{ animationDelay: `${index * 35}ms` }}
                key={`${call.step}-${call.tool}-${index}`}
              >
                {call.status === 'failed' ? <XCircle size={13} /> : <Wrench size={13} />}
                <div>
                  <span className="trajectory-tool">{call.tool}</span>
                  <span className="trajectory-step">步骤 {call.step} · {call.status === 'failed' ? '失败' : '已完成'}</span>
                  {call.error && <span className="trajectory-error">{call.error}</span>}
                </div>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  )
}

function TrajectoryPill({ text, done }: { text: string; done: boolean }) {
  return (
    <div className={`trajectory-pill${done ? ' done' : ''}`}>
      <LoaderCircle className="spin" size={15} />
      <span>{text}</span>
    </div>
  )
}
