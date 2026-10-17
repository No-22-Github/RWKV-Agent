import { useEffect, useId, useLayoutEffect, useRef, useState, type KeyboardEvent } from 'react'
import { createPortal } from 'react-dom'
import { Check, ChevronsUpDown } from 'lucide-react'

export type SelectOption = { value: string; label: string; hint?: string }

/*
 * 设置页的下拉框：替代原生 <select>（macOS 原生弹层是系统蓝高亮，和黑白单色界面不搭）。
 *
 * 焦点始终留在触发按钮上，键盘高亮走 aria-activedescendant：↑↓ 移动、Enter/空格选中、
 * Esc/Tab 收起。弹层挂到 body 并用 fixed 定位，避免被设置页的滚动容器裁掉；下方放不下时向上翻。
 * 当前值写在 data-value 上，测试用它断言（原生 select 的 toHaveValue 不再适用）。
 */
export function Select({ label, value, options, onChange, className = '' }: { label: string; value: string; options: SelectOption[]; onChange: (value: string) => void; className?: string }) {
  const [open, setOpen] = useState(false)
  const [active, setActive] = useState(0)
  const [placement, setPlacement] = useState<{ left: number; width: number; top?: number; bottom?: number; maxHeight: number }>({ left: 0, width: 0, top: 0, maxHeight: 320 })
  const buttonRef = useRef<HTMLButtonElement>(null)
  const listRef = useRef<HTMLDivElement>(null)
  const id = useId()
  const selectedIndex = Math.max(0, options.findIndex((option) => option.value === value))
  const selected = options.find((option) => option.value === value)

  function show() {
    setActive(selectedIndex)
    setOpen(true)
  }

  function choose(index: number) {
    const option = options[index]
    setOpen(false)
    if (option && option.value !== value) onChange(option.value)
  }

  useLayoutEffect(() => {
    if (!open) return
    function position() {
      const rect = buttonRef.current?.getBoundingClientRect()
      if (!rect) return
      const width = Math.max(rect.width, 240)
      const left = Math.max(16, Math.min(rect.right - width, window.innerWidth - width - 16))
      const below = window.innerHeight - rect.bottom - 16
      const above = rect.top - 16
      // 选项约 34px 一行；下方放得下全部或比上方宽裕就向下开。
      const wanted = options.length * 34 + 10
      if (below >= Math.min(wanted, 240) || below >= above) {
        setPlacement({ left, width, top: rect.bottom + 6, maxHeight: Math.min(320, below) })
      } else {
        setPlacement({ left, width, bottom: window.innerHeight - rect.top + 6, maxHeight: Math.min(320, above) })
      }
    }
    position()
    window.addEventListener('resize', position)
    window.addEventListener('scroll', position, true)
    return () => { window.removeEventListener('resize', position); window.removeEventListener('scroll', position, true) }
  }, [open, options.length])

  useEffect(() => {
    if (!open) return
    function onPointerDown(event: MouseEvent) {
      const target = event.target as Node
      if (!buttonRef.current?.contains(target) && !listRef.current?.contains(target)) setOpen(false)
    }
    document.addEventListener('mousedown', onPointerDown)
    return () => document.removeEventListener('mousedown', onPointerDown)
  }, [open])

  useEffect(() => {
    if (open) listRef.current?.querySelector(`[data-index="${active}"]`)?.scrollIntoView?.({ block: 'nearest' })
  }, [open, active])

  function onKeyDown(event: KeyboardEvent<HTMLButtonElement>) {
    const last = options.length - 1
    if (!open) {
      if (['ArrowDown', 'ArrowUp', 'Enter', ' '].includes(event.key)) { event.preventDefault(); show() }
      return
    }
    switch (event.key) {
      case 'ArrowDown': event.preventDefault(); setActive((index) => Math.min(last, index + 1)); break
      case 'ArrowUp': event.preventDefault(); setActive((index) => Math.max(0, index - 1)); break
      case 'Home': event.preventDefault(); setActive(0); break
      case 'End': event.preventDefault(); setActive(last); break
      case 'Enter': case ' ': event.preventDefault(); choose(active); break
      case 'Escape': event.preventDefault(); setOpen(false); break
      case 'Tab': setOpen(false); break
    }
  }

  return (
    <>
      <button
        ref={buttonRef}
        type="button"
        role="combobox"
        aria-label={label}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={open ? `${id}-list` : undefined}
        aria-activedescendant={open ? `${id}-${active}` : undefined}
        data-value={value}
        onClick={() => (open ? setOpen(false) : show())}
        onKeyDown={onKeyDown}
        className={`rounded-md flex h-[36px] min-w-0 items-center gap-[8px] border border-line bg-paper-wash px-[10px] text-left text-base text-ink outline-0 transition-colors hover:border-line-strong focus-visible:border-brand ${open ? 'border-brand' : ''} ${className}`}
      >
        <span className="min-w-0 flex-1 truncate">{selected?.label ?? value}</span>
        <ChevronsUpDown size={14} className="flex-none text-ink-muted" />
      </button>
      {open && createPortal(
        <div
          ref={listRef}
          id={`${id}-list`}
          role="listbox"
          aria-label={label}
          style={{ left: placement.left, width: placement.width, top: placement.top, bottom: placement.bottom, maxHeight: placement.maxHeight }}
          className={`fixed z-[70] overflow-y-auto overscroll-contain rounded-xl border border-line bg-paper-wash p-[4px] shadow-pop motion-reduce:animate-none ${placement.top !== undefined ? 'origin-top animate-menu-down-in' : 'origin-bottom animate-menu-up-in'}`}
        >
          {options.map((option, index) => {
            const isSelected = option.value === value
            return (
              <div
                key={option.value}
                id={`${id}-${index}`}
                role="option"
                aria-selected={isSelected}
                data-index={index}
                data-value={option.value}
                onMouseEnter={() => setActive(index)}
                onMouseDown={(event) => event.preventDefault()}
                onClick={() => choose(index)}
                className={`flex cursor-default items-center gap-[8px] rounded-lg px-[10px] py-[7px] text-sm ${index === active ? 'bg-surface-active' : ''}`}
              >
                <span className="flex min-w-0 flex-1 flex-col">
                  <span className={`truncate ${isSelected ? 'text-ink-strong' : 'text-ink'}`}>{option.label}</span>
                  {option.hint && <span className="text-2xs leading-[1.5] text-ink-muted">{option.hint}</span>}
                </span>
                {isSelected && <Check size={13} className="flex-none text-ink" />}
              </div>
            )
          })}
        </div>,
        document.body,
      )}
    </>
  )
}
