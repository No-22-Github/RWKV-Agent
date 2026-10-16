import { useState } from 'react'
import { ChevronRight } from 'lucide-react'
import type { Step } from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import { splitModelOutput } from '../ledger'

/*
 * 运行中的思考：后端 thinking_delta 推来当前这一步的思考，这里只露最后两行，
 * 底部对齐、顶部渐隐，新字从下面长出来，让人看得到模型在动，而不把整段思考摊开。
 */
export function LiveThought({ text }: { text: string }) {
  const tail = text.replace(/\s+/g, ' ').trim().slice(-240)
  if (!tail) return null
  return <div
    className="live-thought flex max-h-[3.3em] flex-col justify-end overflow-hidden pl-[24px] text-xs leading-[1.65] text-ink-muted [mask-image:linear-gradient(to_bottom,transparent,black_45%)]"
    aria-live="off"
    data-testid="live-thought"
  >
    <p className="m-0 [overflow-wrap:anywhere]">{tail}</p>
  </div>
}

/** 每一步模型输出里的前导思考；没有思考的步骤略过。 */
export function stepThoughts(steps: readonly Step[] | undefined): { step: number; text: string }[] {
  return (steps || [])
    .map((step) => ({ step: step.number, text: splitModelOutput(step.modelOutput).thinking }))
    .filter((item) => item.text !== '')
}

/* 回合结束后的思考记录：默认收起，展开后按步骤列出原文。 */
export default function ThinkingTrail({ steps }: { steps: readonly Step[] | undefined }) {
  const [open, setOpen] = useState(false)
  const thoughts = stepThoughts(steps)
  if (thoughts.length === 0) return null
  return <div className="thinking-trail text-sm" data-testid="thinking-trail">
    <button type="button" aria-expanded={open} onClick={() => setOpen((value) => !value)} className="flex items-center gap-[6px] border-0 bg-transparent p-0 text-left text-ink-muted transition-colors hover:text-ink">
      <span>思考过程 · {thoughts.length} 段</span>
      <ChevronRight size={15} className={`flex-none transition-transform duration-200 motion-reduce:transition-none ${open ? 'rotate-90' : ''}`} />
    </button>
    {open && <div className="mt-[8px] flex flex-col gap-[10px] border-l-2 border-line pl-[12px]">
      {thoughts.map((item) => <div key={item.step} className="flex flex-col gap-[2px]">
        <span className="font-mono text-2xs text-ink-ghost">步骤 {item.step}</span>
        <p className="m-0 whitespace-pre-wrap text-xs leading-[1.7] text-ink-soft [overflow-wrap:anywhere]">{item.text}</p>
      </div>)}
    </div>}
  </div>
}
