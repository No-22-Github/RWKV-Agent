import type { Step } from '../../bindings/github.com/no22/RWKV-Agent/api/models'
import { splitModelOutput } from '../ledger'
import type { Thought } from './ToolActivity'

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
export function stepThoughts(steps: readonly Step[] | undefined): Thought[] {
  return (steps || [])
    .map((step) => ({ step: step.number, text: splitModelOutput(step.modelOutput).thinking }))
    .filter((item) => item.text !== '')
}
