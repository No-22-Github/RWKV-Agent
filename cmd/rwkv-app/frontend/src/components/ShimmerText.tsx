import { useLayoutEffect, useRef, type ReactNode } from 'react'

/**
 * 流光文字。CSS 动画从元素挂载时起算，等待行换成工具卡片标题这类换元素的时刻
 * 流光会扫到一半跳回开头；这里把动画起点钉在文档时间 0，所有流光共用一个相位，换元素也接得上。
 */
export default function ShimmerText({ className = '', title, children }: { className?: string; title?: string; children: ReactNode }) {
  const ref = useRef<HTMLSpanElement>(null)
  useLayoutEffect(() => {
    for (const animation of ref.current?.getAnimations?.() ?? []) animation.startTime = 0
  }, [])
  return <span ref={ref} className={`shimmer-text ${className}`} title={title}>{children}</span>
}
