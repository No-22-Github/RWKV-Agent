import { useEffect, useRef, useState } from 'react'
import MarkdownMessage from '../MarkdownMessage'

// 显示节奏：模型约 90 字/秒，原样跟着到达速度显示会显得急。按基础速度匀速放字，
// 积压变多时按「最多落后 MAX_LAG_S 秒」线性提速，长回答不会越拖越久。
const BASE_CHARS_PER_SECOND = 45
const MAX_LAG_S = 2.5

const prefersReducedMotion = () => typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches

/**
 * 流式回答的匀速显示层。live 期间 text 持续增长；live 结束后继续把剩余的字放完，
 * 追平后交回普通 Markdown 渲染（不再拆字）。同一实例要跨越「生成中 → 落定」，
 * 否则落定瞬间会把还没放出来的字一次性甩出来。
 */
export default function PacedAnswer({ text, live, onGrow }: { text: string; live: boolean; onGrow?: () => void }) {
  const [shown, setShown] = useState(() => (prefersReducedMotion() ? text.length : 0))
  const textRef = useRef(text)
  textRef.current = text
  const growRef = useRef(onGrow)
  growRef.current = onGrow
  const caughtUp = shown >= text.length

  // 预览被撤回（answer_reset）后文字会变短：从头按节奏放，而不是把新的一段直接甩出来。
  useEffect(() => { if (text.length < shown) setShown(0) }, [text, shown])

  useEffect(() => {
    if (caughtUp) return
    if (prefersReducedMotion()) { setShown(textRef.current.length); return }
    let frame = 0
    let last = performance.now()
    let position = shown
    let emitted = shown
    const tick = (now: number) => {
      const target = textRef.current.length
      const elapsed = Math.min(now - last, 100) / 1000
      last = now
      const backlog = target - position
      position = Math.min(target, position + Math.max(BASE_CHARS_PER_SECOND, backlog / MAX_LAG_S) * elapsed)
      let next = Math.floor(position)
      // 不把代理对切成两半（emoji 等），否则会闪出一个替换字符。
      const code = textRef.current.charCodeAt(next - 1)
      if (code >= 0xd800 && code <= 0xdbff) next += 1
      if (next > emitted) {
        emitted = next
        setShown(next)
        growRef.current?.()
      }
      // 追平后 shown 等于全文、caughtUp 变真，effect 清理会停掉循环；这里不自己停，
      // 免得「刚追平、新字又到」时 caughtUp 没翻转、循环却已停下而卡住。
      frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
    // 只在「追平 ↔ 落后」切换时重启循环；循环内部经 ref 读最新文本。
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caughtUp])

  const settled = !live && caughtUp
  return <MarkdownMessage content={settled ? text : text.slice(0, shown)} streaming={!settled} />
}
