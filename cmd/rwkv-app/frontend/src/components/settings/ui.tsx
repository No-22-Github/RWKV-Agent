import { useId, type ButtonHTMLAttributes, type ReactNode } from 'react'
import type { SaveState } from '../../state/providerManager'

/* 设置表单的基础控件：按钮、输入框、数字框、分段选择、开关、单行设置。所有 aria-label 供测试与读屏使用。 */

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger'

const BUTTON_VARIANT: Record<ButtonVariant, string> = {
  primary: 'border-transparent bg-brand font-medium text-brand-fg hover:opacity-90',
  secondary: 'border-line bg-paper-wash text-ink shadow-hair hover:bg-surface-active',
  ghost: 'border-transparent bg-transparent text-ink-soft hover:bg-surface-active hover:text-ink',
  danger: 'border-danger bg-transparent text-danger hover:bg-danger-wash',
}

/*
 * 设置页唯一的按钮：高度只有 sm(28) / md(32) 两档，同一行的按钮因此必然对齐。
 * 新按钮一律用它，不要再手写 h-[..] px-[..]。
 */
export function Button({ variant = 'secondary', size = 'md', icon, className = '', children, ...rest }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: ButtonVariant; size?: 'sm' | 'md'; icon?: ReactNode }) {
  const sizing = size === 'sm' ? 'h-[28px] gap-[5px] px-[10px] text-xs' : 'h-[32px] gap-[6px] px-[12px] text-sm'
  return (
    <button type="button" className={`inline-flex flex-none items-center justify-center whitespace-nowrap rounded-md border transition-colors disabled:pointer-events-none disabled:opacity-40 ${sizing} ${BUTTON_VARIANT[variant]} ${className}`} {...rest}>
      {icon}
      {children}
    </button>
  )
}

/* 字段下方的一行说明；error 优先显示。 */
function FieldNote({ id, hint, error }: { id: string; hint?: ReactNode; error?: string }) {
  if (error) return <span id={id} className="text-xs text-danger">{error}</span>
  if (hint) return <span id={id} className="text-2xs leading-[1.55] text-ink-muted">{hint}</span>
  return null
}

export function Field({ label, value, onChange, placeholder, type = 'text', list, error, hint, trailing }: { label: string; value: string; onChange: (value: string) => void; placeholder?: string; type?: string; list?: string[]; error?: string; hint?: ReactNode; trailing?: ReactNode }) {
  // useId：同名字段（多行请求头）不能共用 id，否则 datalist 与错误说明会串行。
  const id = useId()
  const noteId = `${id}-note`
  return (
    <div className="flex flex-col gap-[5px] py-[6px] text-xs text-ink-muted">
      <label htmlFor={id}>{label}</label>
      <div className="flex items-center gap-[8px]">
        <input id={id} aria-label={label} aria-invalid={error ? true : undefined} aria-describedby={error || hint ? noteId : undefined} className={`h-[40px] min-w-0 flex-1 rounded-md border bg-paper-wash px-[10px] text-base text-ink outline-0 placeholder:text-ink-ghost focus:border-brand ${error ? 'border-danger' : 'border-line'}`} type={type} value={value} placeholder={placeholder} list={list ? `${id}-list` : undefined} onChange={(event) => onChange(event.target.value)} />
        {trailing}
      </div>
      <FieldNote id={noteId} hint={hint} error={error} />
      {list && list.length > 0 && <datalist id={`${id}-list`}>{list.map((item) => <option key={item} value={item} />)}</datalist>}
    </div>
  )
}

/*
 * 数字框：标签 + 一行人话说明 + 取值范围。给了 defaultValue 且当前值不同时，
 * 标签右侧出现「恢复默认」。
 */
export function NumberField({ label, hint, value, onChange, min, max, step = 1, defaultValue }: { label: string; hint: string; value: number; onChange: (value: number) => void; min: number; max: number; step?: number; defaultValue?: number }) {
  const id = useId()
  const changed = defaultValue !== undefined && value !== defaultValue
  return (
    <div className="flex flex-col gap-[5px] text-xs text-ink-muted">
      <div className="flex h-[18px] items-center justify-between gap-[6px]">
        <label htmlFor={id} className="min-w-0 truncate">{label}</label>
        {changed && <button type="button" className="flex-none border-0 bg-transparent p-0 text-2xs text-brand hover:underline" onClick={() => onChange(defaultValue)} title={`恢复为 ${defaultValue}`}>恢复默认</button>}
      </div>
      <input id={id} aria-label={label} aria-describedby={`${id}-note`} className="h-[36px] rounded-md border border-line bg-paper-wash px-[10px] text-base text-ink outline-0 focus:border-brand" type="number" min={min} max={max} step={step} value={value} onChange={(event) => onChange(Number(event.target.value))} />
      <span id={`${id}-note`} className="text-2xs leading-[1.55] text-ink-muted">{hint}<span className="text-ink-ghost">{` · ${min}–${max}${defaultValue !== undefined ? `，默认 ${defaultValue}` : ''}`}</span></span>
    </div>
  )
}

/* 分段选择：两到四个互斥选项并排，比下拉框少点一下。 */
export function Segmented<T extends string>({ label, value, onChange, options }: { label: string; value: T; onChange: (value: T) => void; options: { value: T; label: string; icon?: ReactNode }[] }) {
  return (
    <div role="radiogroup" aria-label={label} className="flex flex-none rounded-lg border border-line bg-surface-active p-[2px]">
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          role="radio"
          aria-checked={value === option.value}
          className={`flex h-[28px] items-center gap-[5px] rounded-md border-0 px-[10px] text-xs transition-colors ${value === option.value ? 'bg-paper font-medium text-ink shadow-hair' : 'bg-transparent text-ink-muted hover:text-ink'}`}
          onClick={() => onChange(option.value)}
        >{option.icon}{option.label}</button>
      ))}
    </div>
  )
}

const SAVE_STATE_TONE: Record<SaveState['kind'], string> = {
  idle: 'text-ink-ghost',
  pending: 'text-ink-muted',
  saving: 'text-ink-muted',
  saved: 'text-ink-ghost',
  invalid: 'text-warning',
  error: 'text-danger',
}

/* 自动保存状态：读屏以 polite 播报，失败与校验提示用醒目色。idle 不渲染文字。 */
export function SaveStatus({ state }: { state: SaveState }) {
  const text = state.kind === 'invalid' ? `未保存：${state.message}` : state.message || ''
  return (
    <span role="status" aria-live="polite" className={`min-w-0 truncate font-mono text-2xs ${SAVE_STATE_TONE[state.kind]}`} title={text || undefined}>{text}</span>
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
      <input type="checkbox" aria-label={label} checked={checked} onChange={(event) => onChange(event.target.checked)} className="h-[18px] w-[32px] flex-none cursor-pointer appearance-none rounded-[9px] bg-line-strong p-0 transition-colors after:ml-[2px] after:mt-[2px] after:block after:h-[13px] after:w-[13px] after:rounded-full after:bg-paper after:content-[''] after:transition-transform after:duration-200 checked:bg-brand checked:after:translate-x-[15px]" />
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
      <h3 className="m-0 font-mono text-2xs font-semibold text-ink-muted">{title}</h3>
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
