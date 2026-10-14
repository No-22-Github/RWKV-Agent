import { forwardRef, useImperativeHandle, type HTMLAttributes } from 'react'
import { motion, useAnimation } from 'motion/react'

type Handle = { startAnimation: () => void; stopAnimation: () => void }
type Props = HTMLAttributes<HTMLDivElement> & { size?: number }

/** 箭头取回内容，随后文字逐行出现；与文件读取和网页搜索区分。 */
export const FileFetchIcon = forwardRef<Handle, Props>(({ size = 15, ...props }, ref) => {
  const controls = useAnimation()
  useImperativeHandle(ref, () => ({
    startAnimation: () => { void controls.start('animate') },
    stopAnimation: () => { void controls.start('normal') },
  }), [controls])
  return <div {...props}>
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4M14 2v5h4" />
      <motion.g initial="normal" animate={controls} variants={{
        normal: { y: 0, opacity: 1 },
        animate: { y: [-3, 1, 0], opacity: [0.35, 1, 1], transition: { duration: 0.55, ease: 'easeOut' } },
      }}>
        <path d="M18 3v10m-3-3 3 3 3-3" />
      </motion.g>
      {[15, 18].map((y, index) => <motion.path key={y} d={`M8 ${y}h5`} initial="normal" animate={controls} variants={{
        normal: { pathLength: 1, opacity: 1 },
        animate: { pathLength: [0, 1], opacity: [0, 1], transition: { duration: 0.3, delay: 0.55 + index * 0.18, ease: 'easeOut' } },
      }} />)}
    </svg>
  </div>
})
FileFetchIcon.displayName = 'FileFetchIcon'
