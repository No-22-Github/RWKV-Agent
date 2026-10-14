import { forwardRef, useImperativeHandle, type HTMLAttributes, type RefAttributes, type ForwardRefExoticComponent } from 'react'
import { Calculator, Clock, Database, PackageOpen, type LucideIcon } from 'lucide-react'
import { motion, useAnimation } from 'motion/react'

type Handle = { startAnimation: () => void; stopAnimation: () => void }
type Props = HTMLAttributes<HTMLDivElement> & { size?: number }

// 与其余工具图标共用受控接口，运行状态和减少动态效果由 AnimatedToolIcon 管理。
function animatedIcon(Icon: LucideIcon, name: string, keyframes: number[]): ForwardRefExoticComponent<Props & RefAttributes<Handle>> {
  const Component = forwardRef<Handle, Props>(({ size = 15, ...props }, ref) => {
    const controls = useAnimation()
    useImperativeHandle(ref, () => ({
      startAnimation: () => { void controls.start('animate') },
      stopAnimation: () => { void controls.start('normal') },
    }), [controls])
    return <div {...props}>
      <motion.div initial="normal" animate={controls} variants={{
        normal: { rotate: 0, scale: 1 },
        animate: { rotate: keyframes, scale: [1, 1.12, 1], transition: { duration: 0.9, ease: 'easeInOut' } },
      }}><Icon size={size} /></motion.div>
    </div>
  })
  Component.displayName = name
  return Component
}

export const CalculatorIcon = animatedIcon(Calculator, 'CalculatorIcon', [0, -8, 8, 0])
export const ClockIcon = animatedIcon(Clock, 'ClockIcon', [0, 20, 0])
export const DatabaseIcon = animatedIcon(Database, 'DatabaseIcon', [0, -6, 6, 0])
export const PackageOpenIcon = animatedIcon(PackageOpen, 'PackageOpenIcon', [0, -10, 0])
