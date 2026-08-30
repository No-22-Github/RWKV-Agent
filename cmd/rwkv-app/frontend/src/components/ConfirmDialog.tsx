import { useEffect } from 'react'

export type ConfirmAction = {
  label: string
  variant?: 'primary' | 'default' | 'danger'
  onClick: () => void
}

type Props = {
  open: boolean
  title: string
  body?: string
  actions: ConfirmAction[]
  onClose: () => void
}

const ACTION_CLASS: Record<NonNullable<ConfirmAction['variant']>, string> = {
  primary: 'border-0 bg-brand text-white',
  default: 'border border-ink bg-transparent text-ink',
  danger: 'border border-danger bg-transparent text-danger',
}

/* 轻量确认对话框：未保存离开、删除确认等场景共用。Esc / 点击遮罩 = 取消。 */
export default function ConfirmDialog({ open, title, body, actions, onClose }: Props) {
  useEffect(() => {
    if (!open) return
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKeyDown)
    return () => document.removeEventListener('keydown', onKeyDown)
  }, [open, onClose])

  if (!open) return null
  return (
    <div className="fixed inset-0 z-[70] grid place-items-center bg-[rgba(43,39,33,.34)]" onClick={onClose}>
      <div role="dialog" aria-modal="true" aria-label={title} className="w-[380px] border border-line-strong bg-paper-wash p-[18px] shadow-[0_18px_48px_rgba(45,33,20,.2)]" onClick={(event) => event.stopPropagation()}>
        <h2 className="m-0 font-serif text-md font-semibold text-ink">{title}</h2>
        {body && <p className="mb-0 mt-[8px] text-sm leading-[1.65] text-ink-soft">{body}</p>}
        <div className="mt-[18px] flex justify-end gap-[9px]">
          {actions.map((action) => (
            <button
              key={action.label}
              className={`h-[32px] px-[13px] text-sm font-medium disabled:opacity-40 ${ACTION_CLASS[action.variant || 'default']}`}
              onClick={action.onClick}
            >
              {action.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
