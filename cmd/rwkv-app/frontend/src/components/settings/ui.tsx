import { useId, type ButtonHTMLAttributes, type ReactNode } from 'react'
import { ChevronDown, RotateCcw } from 'lucide-react'
import type { SaveState } from '../../state/providerManager'

/*
 * 设置页的基础控件。版式只有一种：一行 = 左边标签（可带一行灰色说明）+ 右边控件，行与行之间一条细线；
 * 若干行组成一个 Section，Section 之间靠标题和留白分开。
 *
 * 字号只用三档，不要在分区组件里再加第四档：
 *   标题  text-md font-semibold text-ink        Section 标题、详情页名称、导航页头
 *   正文  text-base text-ink                    行标签、输入框、按钮、标签页
 *   说明  text-sm text-ink-muted                行说明、列表副标题、保存状态
 *
 * 说明文字是例外不是默认：只给「不看会填错」的行写，取值范围放进 title，预设的用途放进下拉选项的 hint。
 * 所有 aria-label 供测试与读屏使用。
 */

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger'

const BUTTON_VARIANT: Record<ButtonVariant, string> = {
  primary: 'border-transparent bg-brand font-medium text-brand-fg hover:opacity-90',
  secondary: 'border-line bg-paper-wash text-ink shadow-hair hover:bg-surface-active',
  ghost: 'border-transparent bg-transparent text-ink-soft hover:bg-surface-active hover:text-ink',
  danger: 'border-line bg-paper-wash text-danger shadow-hair hover:border-danger hover:bg-danger-wash',
}

/*
 * 设置页唯一的按钮：高度只有 sm(28) / md(32) 两档，同一行的按钮因此必然对齐。
 * 新按钮一律用它，不要再手写 h-[..] px-[..]。
 */
export function Button({ variant = 'secondary', size = 'md', icon, className = '', children, ...rest }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: ButtonVariant; size?: 'sm' | 'md'; icon?: ReactNode }) {
  const sizing = size === 'sm' ? 'h-[28px] gap-[5px] px-[10px] text-sm' : 'h-[32px] gap-[6px] px-[12px] text-base'
  return (
    <button type="button" className={`inline-flex flex-none items-center justify-center whitespace-nowrap rounded-md border transition-colors disabled:pointer-events-none disabled:opacity-40 ${sizing} ${BUTTON_VARIANT[variant]} ${className}`} {...rest}>
      {icon}
      {children}
    </button>
  )
}

/* 输入框本体：32px 高，和 Select、Button 对齐。宽度由调用方给。 */
export function TextInput({ label, value, onChange, placeholder, type = 'text', list, invalid, id, describedBy, className = '' }: { label: string; value: string; onChange: (value: string) => void; placeholder?: string; type?: string; list?: string[]; invalid?: boolean; id?: string; describedBy?: string; className?: string }) {
  const own = useId()
  const inputId = id || own
  return (
    <>
      <input
        id={inputId}
        aria-label={label}
        aria-invalid={invalid ? true : undefined}
        aria-describedby={describedBy}
        className={`h-[32px] min-w-0 rounded-md border bg-paper-wash px-[10px] text-base text-ink outline-0 transition-colors placeholder:text-ink-ghost hover:border-line-strong focus:border-brand ${invalid ? 'border-danger' : 'border-line'} ${className}`}
        type={type}
        value={value}
        placeholder={placeholder}
        list={list ? `${inputId}-list` : undefined}
        onChange={(event) => onChange(event.target.value)}
      />
      {list && list.length > 0 && <datalist id={`${inputId}-list`}>{list.map((item) => <option key={item} value={item} />)}</datalist>}
    </>
  )
}

/* 一行设置：左标签 + 说明（或错误），右控件。 */
export function Row({ label, description, error, htmlFor, children }: { label: ReactNode; description?: ReactNode; error?: string; htmlFor?: string; children?: ReactNode }) {
  const noteId = htmlFor ? `${htmlFor}-note` : undefined
  return (
    <div className="flex min-h-[52px] items-center gap-[24px] border-b border-line-soft py-[10px] last:border-b-0">
      <div className="flex min-w-0 flex-1 flex-col gap-[2px]">
        {htmlFor ? <label htmlFor={htmlFor} className="text-base text-ink">{label}</label> : <span className="text-base text-ink">{label}</span>}
        {error
          ? <span id={noteId} className="text-sm leading-[1.5] text-danger">{error}</span>
          : description && <span id={noteId} className="text-sm leading-[1.5] text-ink-muted [overflow-wrap:anywhere]">{description}</span>}
      </div>
      {children && <div className="flex flex-none items-center gap-[8px]">{children}</div>}
    </div>
  )
}

/* 文本行：输入框固定宽度靠右，长地址在框里横向滚动，不撑满整行。分组标题已经说明了是什么时（如「API Key」组里只写服务名），用 inputLabel 给读屏一个完整名称。 */
export function TextRow({ label, inputLabel, description, value, onChange, placeholder, type, list, error, trailing, width = 'w-[300px]' }: { label: string; inputLabel?: string; description?: ReactNode; value: string; onChange: (value: string) => void; placeholder?: string; type?: string; list?: string[]; error?: string; trailing?: ReactNode; width?: string }) {
  const id = useId()
  return (
    <Row label={label} description={description} error={error} htmlFor={id}>
      <TextInput id={id} label={inputLabel || label} value={value} onChange={onChange} placeholder={placeholder} type={type} list={list} invalid={Boolean(error)} describedBy={error || description ? `${id}-note` : undefined} className={width} />
      {trailing}
    </Row>
  )
}

/* 数字行：窄输入框靠右；取值范围放在悬停提示里，偏离默认值时出现「恢复默认」小按钮。 */
export function NumberRow({ label, description, value, onChange, min, max, step = 1, defaultValue }: { label: string; description?: string; value: number; onChange: (value: number) => void; min: number; max: number; step?: number; defaultValue?: number }) {
  const id = useId()
  const changed = defaultValue !== undefined && value !== defaultValue
  const range = `${min}–${max}${defaultValue !== undefined ? `，默认 ${defaultValue}` : ''}`
  return (
    <Row label={label} description={description} htmlFor={id}>
      {changed && (
        <button type="button" className="grid h-[28px] w-[28px] place-items-center rounded-md border-0 bg-transparent text-ink-muted transition-colors hover:bg-surface-active hover:text-ink" onClick={() => onChange(defaultValue)} aria-label={`${label}恢复默认`} title={`恢复为 ${defaultValue}`}><RotateCcw size={13} /></button>
      )}
      <input id={id} aria-label={label} title={range} className="h-[32px] w-[104px] rounded-md border border-line bg-paper-wash px-[10px] text-right text-base tabular-nums text-ink outline-0 transition-colors hover:border-line-strong focus:border-brand" type="number" min={min} max={max} step={step} value={value} onChange={(event) => onChange(Number(event.target.value))} />
    </Row>
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
          className={`flex h-[28px] items-center gap-[5px] rounded-md border-0 px-[10px] text-sm transition-colors ${value === option.value ? 'bg-paper font-medium text-ink shadow-hair' : 'bg-transparent text-ink-muted hover:text-ink'}`}
          onClick={() => onChange(option.value)}
        >{option.icon}{option.label}</button>
      ))}
    </div>
  )
}

const SAVE_STATE_TONE: Record<SaveState['kind'], string> = {
  idle: 'text-ink-muted',
  pending: 'text-ink-muted',
  saving: 'text-ink-muted',
  saved: 'text-ink-muted',
  invalid: 'text-warning',
  error: 'text-danger',
}

/* 自动保存状态：读屏以 polite 播报，失败与校验提示用醒目色。idle 不渲染文字。 */
export function SaveStatus({ state }: { state: SaveState }) {
  const text = state.kind === 'invalid' ? `未保存：${state.message}` : state.message || ''
  return (
    <span role="status" aria-live="polite" className={`min-w-0 truncate text-sm ${SAVE_STATE_TONE[state.kind]}`} title={text || undefined}>{text}</span>
  )
}

/* 开关行。说明可省；开关本身就是 label 的一部分，点整行都能切换。 */
export function Toggle({ label, description, checked, onChange }: { label: string; description?: string; checked: boolean; onChange: (value: boolean) => void }) {
  return (
    <label className="flex min-h-[52px] cursor-pointer items-center justify-between gap-[24px] border-b border-line-soft py-[10px] last:border-b-0">
      <span className="flex min-w-0 flex-1 flex-col gap-[2px]">
        <span className="text-base text-ink">{label}</span>
        {description && <span className="text-sm leading-[1.5] text-ink-muted">{description}</span>}
      </span>
      <input type="checkbox" aria-label={label} checked={checked} onChange={(event) => onChange(event.target.checked)} className="h-[20px] w-[34px] flex-none cursor-pointer appearance-none rounded-full bg-line-strong p-0 transition-colors after:ml-[2px] after:mt-[2px] after:block after:h-[16px] after:w-[16px] after:rounded-full after:bg-paper after:shadow-hair after:content-[''] after:transition-transform after:duration-200 checked:bg-brand checked:after:translate-x-[14px]" />
    </label>
  )
}

/* 一组设置：标题 + 若干行。标题右侧可放一个次要动作（链接式按钮、保存状态）。 */
export function Section({ title, action, children }: { title: string; action?: ReactNode; children: ReactNode }) {
  return (
    <section className="mt-[32px] first:mt-0">
      <div className="flex min-h-[28px] items-center justify-between gap-[12px]">
        <h3 className="m-0 text-md font-semibold text-ink">{title}</h3>
        {action}
      </div>
      <div className="mt-[2px]">{children}</div>
    </section>
  )
}

/*
 * 折叠行：不常改的东西（请求头、State、提示词预览）平时只露一行摘要，点开在下面展开。
 * 展开区域缩进到一块浅底卡片里，表明它从属于这一行。
 */
export function Disclosure({ label, summary, open, onToggle, children }: { label: string; summary?: ReactNode; open: boolean; onToggle: () => void; children: ReactNode }) {
  const id = useId()
  return (
    <div className="border-b border-line-soft last:border-b-0">
      <button
        type="button"
        aria-expanded={open}
        aria-controls={id}
        className="flex min-h-[52px] w-full items-center gap-[24px] border-0 bg-transparent px-0 py-[10px] text-left"
        onClick={onToggle}
      >
        <span className="flex min-w-0 flex-1 flex-col gap-[2px]">
          <span className="text-base text-ink">{label}</span>
          {summary && <span className="truncate text-sm leading-[1.5] text-ink-muted">{summary}</span>}
        </span>
        <ChevronDown size={15} className={`flex-none text-ink-muted transition-transform duration-150 ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && <div id={id} className="mb-[14px] rounded-lg bg-paper-soft px-[14px] py-[10px]">{children}</div>}
    </div>
  )
}

/* 运行状态徽标：列表行与详情页头共用。 */
export function RunningBadge({ tone = 'running', children }: { tone?: 'running' | 'warning'; children: string }) {
  return (
    <span className="flex flex-none items-center gap-[6px] rounded-full border border-line px-[8px] py-[2px] text-sm text-ink-soft">
      <span className={`h-[6px] w-[6px] rounded-full ${tone === 'warning' ? 'bg-warning' : 'bg-brand-bright'}`} />
      {children}
    </span>
  )
}

/* 页内提示条：操作结果、需要用户动手的状态。只放这一类，不放常驻说明。 */
export function Notice({ tone = 'neutral', children }: { tone?: 'neutral' | 'warning'; children: ReactNode }) {
  return (
    <p role="status" aria-live="polite" className={`mb-[20px] mt-0 rounded-md border px-[12px] py-[8px] text-sm leading-[1.6] text-ink-soft [overflow-wrap:anywhere] ${tone === 'warning' ? 'border-warning/40 bg-paper-soft' : 'border-line bg-paper-soft'}`}>{children}</p>
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
 *
 * 左右各留 56px：弹窗右上角的关闭按钮悬在内容区之上，窄窗口时不能压住标题行的按钮。
 *
 * 内容按外层（不滚动的那层）的宽度定位，而不是按滚动区：macOS「始终显示滚动条」下，内容一超过
 * 一屏滚动条就出现、滚动区变窄，按滚动区居中的内容会往左抽一下（打开详情、数据加载完、展开折叠行
 * 都会触发）。外层是 container，100cqw 是外层宽度、不随滚动条变，左边距因此固定；滚动条只吃掉
 * 右侧 56px 留白，和上方按同一宽度居中的页头始终对齐。不用 scrollbar-gutter：WKWebView 不一定支持。
 * 横向不滚动，免得触控板左右一划整块挪动。
 */
export function SettingsPane({ children, footer }: { children: ReactNode; footer?: ReactNode }) {
  return (
    <div className="@container flex min-w-0 min-h-0 flex-1 flex-col">
      <div className="flex min-w-0 min-h-0 flex-1 flex-col overflow-y-auto overflow-x-hidden">
        <div className="flex-none pb-[40px] pt-[28px]" style={PANE_FIXED_POSITION}>
          {children}
        </div>
      </div>
      {footer}
    </div>
  )
}

/* 详情页与 SettingsPane 同宽的固定页头容器（页头不滚动，按自身宽度居中即可）。 */
export const PANE_WIDTH = 'mx-auto w-[min(640px,calc(100%-112px))]'

/* SettingsPane 里同一宽度、同一位置，但按外层容器宽度（100cqw）算，滚动条出现也不动。 */
const PANE_FIXED_WIDTH = 'min(640px, calc(100cqw - 112px))'
const PANE_FIXED_POSITION = { width: PANE_FIXED_WIDTH, marginLeft: `calc((100cqw - ${PANE_FIXED_WIDTH}) / 2)` }
