/*
 * Minimal anchored menu for the JsonTree copy actions (stand-in for the DSH
 * Menu primitive): a portal list under the anchor, closed by Escape or an
 * outside press.
 */
import { useEffect, useRef, type ReactNode } from 'react'
import { createPortal } from 'react-dom'

export interface MenuItem { id: string; label: string }
export interface MenuSeparator { type: 'separator'; id: string }
export interface MenuLabel { type: 'label'; id: string; text: string }
export type MenuEntry = MenuItem | MenuSeparator | MenuLabel

export function Menu({ open, anchor, items = [], onSelect, onClose, getAnchorRect }: {
  open: boolean
  anchor: ReactNode
  items?: readonly MenuEntry[]
  onSelect?: (id: string) => void
  onClose: () => void
  align?: 'start' | 'end'
  portal?: boolean
  compact?: boolean
  getAnchorRect?: () => DOMRect
}) {
  const listRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!open) return
    const onPointer = (event: PointerEvent) => { if (!listRef.current?.contains(event.target as Node)) onClose() }
    const onKey = (event: KeyboardEvent) => { if (event.key === 'Escape') onClose() }
    document.addEventListener('pointerdown', onPointer)
    window.addEventListener('keydown', onKey)
    return () => { document.removeEventListener('pointerdown', onPointer); window.removeEventListener('keydown', onKey) }
  }, [open, onClose])
  const rect = open ? getAnchorRect?.() : undefined
  return <>
    {anchor}
    {open && rect && createPortal(
      <div ref={listRef} role="menu" className="trajectory-menu" style={{ position: 'fixed', top: rect.bottom + 4, left: Math.max(8, rect.right - 180) }}>
        {items.map(item => 'type' in item
          ? item.type === 'label' ? <div key={item.id} className="trajectory-menu-label">{item.text}</div> : <div key={item.id} className="trajectory-menu-separator" role="separator" />
          : <button key={item.id} type="button" role="menuitem" className="trajectory-menu-item" onClick={() => { onSelect?.(item.id); onClose() }}>{item.label}</button>)}
      </div>,
      document.body,
    )}
  </>
}
