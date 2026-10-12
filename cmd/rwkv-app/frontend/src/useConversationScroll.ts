import { useCallback, useLayoutEffect, useRef, useState } from 'react'

/** One owner for scrolling. Layout changes never change the user's follow intent. */
export function useConversationScroll(empty: boolean, resetKey: number) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const contentRef = useRef<HTMLDivElement>(null)
  const following = useRef(true)
  const lastTop = useRef(0)
  const frame = useRef<number | null>(null)
  const cancelWheel = useRef(() => {})
  const [showScrollButton, setShowScrollButton] = useState(false)
  const update = useCallback(() => {
    const node = scrollRef.current
    if (!node) return
    if (following.current) {
      node.scrollTop = Math.max(0, node.scrollHeight - node.clientHeight)
      lastTop.current = node.scrollTop
    }
    setShowScrollButton(node.scrollHeight - node.clientHeight - node.scrollTop > 2)
  }, [])
  const schedule = useCallback(() => {
    if (frame.current !== null) return
    frame.current = requestAnimationFrame(() => { frame.current = null; update() })
  }, [update])
  const scrollToBottom = useCallback(() => {
    cancelWheel.current()
    following.current = true
    update()
  }, [update])

  useLayoutEffect(() => {
    cancelWheel.current()
    following.current = true
    schedule()
  }, [resetKey, empty, schedule])

  useLayoutEffect(() => {
    const node = scrollRef.current, content = contentRef.current
    if (!node || !content) return
    lastTop.current = node.scrollTop
    let direction = 0
    let touchY = 0
    const intent = (delta: number) => {
      direction = Math.sign(delta)
      if (direction < 0) following.current = false
    }
    let wheelFrame: number | null = null
    let target = node.scrollTop
    const cancel = () => {
      if (wheelFrame !== null) cancelAnimationFrame(wheelFrame)
      wheelFrame = null
    }
    cancelWheel.current = cancel
    const wheel = (event: WheelEvent) => {
      if (event.ctrlKey || event.shiftKey || !event.deltaY || Math.abs(event.deltaX) > Math.abs(event.deltaY)) return
      // Leave nested code/tool panels to their own native scroll handling.
      for (let child = event.target instanceof Element ? event.target : null; child && child !== node; child = child.parentElement) {
        if (child.scrollHeight > child.clientHeight && /auto|scroll/.test(getComputedStyle(child).overflowY)) return
      }
      intent(event.deltaY)
      if (!event.cancelable || window.matchMedia('(prefers-reduced-motion: reduce)').matches) { cancel(); return }
      event.preventDefault()
      const delta = event.deltaY * (event.deltaMode === 1 ? 20 : event.deltaMode === 2 ? node.clientHeight : 1)
      const start = node.scrollTop
      // Discard old momentum immediately when the wheel reverses direction.
      if (wheelFrame === null || Math.sign(target - start) !== Math.sign(delta)) target = start
      target = Math.max(0, Math.min(node.scrollHeight - node.clientHeight, target + delta))
      cancel()
      const started = performance.now()
      const tick = (now: number) => {
        const progress = Math.max(0, Math.min(1, (now - started) / 85))
        node.scrollTop = start + (target - start) * (1 - (1 - progress) ** 3)
        scroll()
        wheelFrame = progress < 1 ? requestAnimationFrame(tick) : null
      }
      wheelFrame = requestAnimationFrame(tick)
    }
    const touchStart = (event: TouchEvent) => { cancel(); touchY = event.touches[0]?.clientY ?? 0 }
    const touchMove = (event: TouchEvent) => {
      const next = event.touches[0]?.clientY ?? touchY
      intent(touchY - next); touchY = next
    }
    const keydown = (event: KeyboardEvent) => {
      cancel()
      if ((event.target as HTMLElement).closest('input,textarea,select,[contenteditable="true"]')) return
      if (['ArrowUp', 'PageUp', 'Home'].includes(event.key) || (event.key === ' ' && event.shiftKey)) intent(-1)
      else if (['ArrowDown', 'PageDown', 'End', ' '].includes(event.key)) intent(1)
    }
    const scroll = () => {
      const top = Math.max(0, node.scrollTop)
      const distance = node.scrollHeight - node.clientHeight - top
      // Wheel/touch intent wins over queued programmatic scroll events. Only an
      // actual downward movement to the bottom resumes a paused stream.
      if (top < lastTop.current - 2 && distance > 2) following.current = false
      if (direction >= 0 && top > lastTop.current && distance <= 2) following.current = true
      lastTop.current = top
      setShowScrollButton(distance > 2)
    }
    node.addEventListener('wheel', wheel, { passive: false })
    node.addEventListener('touchstart', touchStart, { passive: true })
    node.addEventListener('touchmove', touchMove, { passive: true })
    node.addEventListener('keydown', keydown)
    node.addEventListener('scroll', scroll, { passive: true })
    const pointer = () => { cancel(); direction = 0 }
    node.addEventListener('pointerdown', pointer)
    const observer = typeof ResizeObserver === 'undefined' ? null : new ResizeObserver(schedule)
    observer?.observe(content)
    observer?.observe(node)
    schedule()
    return () => {
      cancel()
      cancelWheel.current = () => {}
      observer?.disconnect()
      node.removeEventListener('wheel', wheel)
      node.removeEventListener('touchstart', touchStart)
      node.removeEventListener('touchmove', touchMove)
      node.removeEventListener('keydown', keydown)
      node.removeEventListener('scroll', scroll)
      node.removeEventListener('pointerdown', pointer)
      if (frame.current !== null) cancelAnimationFrame(frame.current)
      frame.current = null
    }
  }, [empty, schedule])
  return { scrollRef, contentRef, showScrollButton, scrollToBottom, schedule }
}
