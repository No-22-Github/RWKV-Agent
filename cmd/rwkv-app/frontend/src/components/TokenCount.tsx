import { useEffect, useRef, useState } from 'react'

// 显示值追目标值的时间常数：后端约 100 ms 推一次计数，追得比推送稍慢，两次推送之间数字一直在走，不会停顿再跳。
const CHASE_MS = 180

/**
 * 正在生成的调用的 token 数。后端是一段一段推的，这里逐帧把显示值追向最新计数，
 * 读起来是连续往上数；等宽数字让位数不变时宽度不变，整行不跟着抖。
 */
export default function TokenCount({ value }: { value: number }) {
  const [shown, setShown] = useState(value)
  const shownRef = useRef(value)
  useEffect(() => {
    if (value <= shownRef.current || window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) {
      shownRef.current = value
      setShown(value)
      return
    }
    let frame = 0
    let last = performance.now()
    const tick = (now: number) => {
      const exact = shownRef.current + (value - shownRef.current) * (1 - Math.exp(-(now - last) / CHASE_MS))
      last = now
      // 至少走 1，免得指数逼近在最后几个数上拖很久。
      shownRef.current = Math.min(value, Math.max(exact, shownRef.current + 1))
      setShown(Math.floor(shownRef.current))
      if (shownRef.current < value) frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [value])
  return <span className="tabular-nums">{formatTokens(shown)}</span>
}

/** 1000 以内照写；往上按 k 取一位小数（1k、1.1k、12.3k），整数不带 .0，长数字不撑宽整行。 */
export function formatTokens(count: number): string {
  if (count < 1000) return String(count)
  const k = Math.floor(count / 100) / 10
  return `${k % 1 === 0 ? k.toFixed(0) : k.toFixed(1)}k`
}
