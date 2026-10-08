import { useEffect, useRef } from 'react'
import RWKVLoader from './rwkv-loader'

export type PixelLoaderOptions = {
  layout?: 'row' | 'single'
  text?: string
  animation?: 'scan' | 'comet' | 'relay' | 'decode'
  glyph?: 'bold9' | 'thin7'
  cell?: number
  gap?: number
  radius?: number
  letterSpacing?: number
  baseAlpha?: number
  decode?: { once?: boolean; onDone?: () => void }
}

/** RWKV 像素点阵动画；颜色跟随容器的 color，系统「减少动态效果」时静态常亮。 */
export default function PixelLoader({ className, label = '加载中', ...options }: PixelLoaderOptions & { className?: string; label?: string }) {
  const ref = useRef<HTMLSpanElement>(null)
  const key = JSON.stringify(options)
  useEffect(() => {
    if (!ref.current) return
    const loader = new RWKVLoader(ref.current, options)
    ref.current.querySelector('canvas')?.setAttribute('aria-label', label)
    return () => loader.destroy()
    // 选项按值比较：父组件每次渲染都会传新对象，只在内容变了才重建。
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, label])
  return <span ref={ref} className={`inline-flex flex-none ${className || ''}`} />
}
