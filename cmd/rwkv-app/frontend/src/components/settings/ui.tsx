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

/*
 * 设置分区的内容容器：设置页页头之下唯一的滚动区。分区组件只管往里塞内容，
 * 不自己搭滚动结构；需要常驻底部的动作栏走 footer，不进滚动区。
 *
 * 两层 flex 都必须带 min-h-0。flex 项默认 min-height:auto，不会缩到内容高度
 * 以下；漏掉它时内层 overflow-auto 永远等不到受限高度、滚动条不出现，多出来的
 * 内容又被 body 的 overflow:hidden 裁掉——现象就是"下面明显还有内容但够不着"。
 * 这条契约只写在这里一处，避免再被复制到第 N 个分区时漏掉。
 */
export function SettingsPane({ children, footer, bottomPad = true }: { children: ReactNode; footer?: ReactNode; bottomPad?: boolean }) {
  return (
    <div className="flex min-w-0 min-h-0 flex-1 flex-col">
      <div className="flex min-w-0 min-h-0 flex-1 flex-col overflow-auto">
        <div className={`mx-auto w-[min(720px,calc(100%-56px))] flex-none pt-[22px] ${bottomPad ? 'pb-[24px]' : ''}`}>
          {children}
        </div>
      </div>
      {footer}
    </div>
  )
}
