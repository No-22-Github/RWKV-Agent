import type { ReactNode } from 'react'

/* 设置表单的三个基础控件：输入框、开关、单行设置。所有 aria-label 供测试与读屏使用。 */

export function Field({ label, value, onChange, placeholder, type = 'text', list }: { label: string; value: string; onChange: (value: string) => void; placeholder?: string; type?: string; list?: string[] }) {
  const id = label.replace(/\s+/g, '-')
  return (
    <label className="flex flex-col gap-[5px] py-[6px] text-xs text-ink-muted">
      <span>{label}</span>
      <input id={id} aria-label={label} className="h-[40px] w-full rounded-none border border-line bg-paper-wash px-[10px] text-base text-ink outline-0 placeholder:text-ink-ghost focus:border-brand" type={type} value={value} placeholder={placeholder} list={list ? `${id}-list` : undefined} onChange={(event) => onChange(event.target.value)} />
      {list && list.length > 0 && <datalist id={`${id}-list`}>{list.map((item) => <option key={item} value={item} />)}</datalist>}
    </label>
  )
}

export function Toggle({ icon, label, description, checked, onChange }: { icon?: ReactNode; label: string; description: string; checked: boolean; onChange: (value: boolean) => void }) {
  return (
    <label className="flex items-center justify-between gap-[20px] border-b border-line-soft py-[11px]">
      <span className="flex min-w-0 flex-1 items-start gap-[10px] text-base text-ink-strong">
        {icon && <span className="mt-[1px] flex-none text-ink-muted">{icon}</span>}
        <span className="flex min-w-0 flex-col gap-[2px]">
          <span>{label}</span>
          <span className="text-xs leading-[1.55] text-ink-muted">{description}</span>
        </span>
      </span>
      <input type="checkbox" aria-label={label} checked={checked} onChange={(event) => onChange(event.target.checked)} className="h-[18px] w-[32px] flex-none cursor-pointer appearance-none rounded-[9px] bg-line-strong p-0 transition-colors after:ml-[2px] after:mt-[2px] after:block after:h-[13px] after:w-[13px] after:rounded-full after:bg-white after:content-[''] after:transition-transform after:duration-200 checked:bg-brand checked:after:translate-x-[15px]" />
    </label>
  )
}

export function Row({ label, description, children }: { label: string; description?: string; children: ReactNode }) {
  return (
    <div className="flex items-center gap-[20px] border-b border-line-soft px-0 py-[11px]">
      <div className="flex min-w-0 flex-1 flex-col gap-[2px]">
        <span className="text-base text-ink-strong">{label}</span>
        {description && <span className="text-xs leading-[1.55] text-ink-muted">{description}</span>}
      </div>
      {children}
    </div>
  )
}

/* 分组标题：小型大写字 + 分隔线 */
export function GroupTitle({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="mb-[6px] flex items-baseline gap-[10px] border-b border-line pb-[8px]">
      <h3 className="m-0 font-mono text-2xs font-semibold uppercase tracking-[.14em] text-ink-muted">{title}</h3>
      {hint && <span className="text-2xs text-ink-ghost">{hint}</span>}
    </div>
  )
}
