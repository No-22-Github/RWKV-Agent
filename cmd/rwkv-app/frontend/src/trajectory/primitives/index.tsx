/*
 * Local stand-ins for the @deepseek-ai/dsh-client-ui-primitives exports the
 * ported trajectory view uses. Tooltip, JsonTree and StateDot are ported
 * verbatim (MIT, see ../LICENSE.deepseek-harness); icons, Markdown, code
 * blocks and attachment helpers map onto what this app already ships.
 */
import type { ReactNode } from 'react'
import { File } from 'lucide-react'
import MarkdownMessage from '../../MarkdownMessage'

export { Tooltip } from './Tooltip.tsx'
export { JsonTree } from './JsonTree.tsx'
export type { JsonTreeLabels, JsonTreeProps } from './JsonTree.tsx'
export { StateDot } from './StateDot.tsx'
export { writeClipboard } from './clipboard.ts'

export * from './icons.tsx'

export interface MarkdownLabels {
  code?: { copyLabel: string; copiedLabel: string }
  footnotes?: string
}

/** Markdown body rendered with the chat's renderer; `compact` tightens it for the inspector. */
export function MarkdownText({ text, variant = 'body' }: { text: string; labels?: MarkdownLabels; variant?: 'body' | 'compact' }) {
  return (
    <div className={`text-[13px] text-ink [overflow-wrap:anywhere] ${variant === 'compact' ? 'leading-5' : 'leading-[1.7]'}`}>
      <MarkdownMessage content={text} />
    </div>
  )
}

/** Source listing with optional line numbers; highlighting is left to a later pass. */
export function CodeBlock({ code, lineNumbers = false, className }: {
  code: string
  lang?: string
  lineNumbers?: boolean
  showHeader?: boolean
  className?: string
  copyLabel?: string
  copiedLabel?: string
}): ReactNode {
  const lines = code.replace(/\n$/, '').split('\n')
  return (
    <pre className={className} style={{ margin: 0, fontFamily: 'var(--ds-font-family-code)', whiteSpace: 'pre' }}>
      {lines.map((line, index) => (
        <div key={index}>
          {lineNumbers && <span style={{ display: 'inline-block', minWidth: '3ch', marginRight: 12, color: 'var(--dsw-alias-label-tertiary)', textAlign: 'right', userSelect: 'none' }}>{index + 1}</span>}
          {line}
        </div>
      ))}
    </pre>
  )
}

export function FileTypeIcon({ path: _path }: { path: string }) {
  return <File size={16} strokeWidth={1.5} aria-hidden="true" />
}

export function fileExtension(path: string): string {
  const name = path.split(/[\\/]/).at(-1) ?? ''
  const dot = name.lastIndexOf('.')
  return dot > 0 ? name.slice(dot + 1) : ''
}

export function fileSizeText(bytes: number): string {
  if (!Number.isFinite(bytes)) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

/** Markdown → one-line plain text for previews: drops markup, keeps link labels and code text. */
export function extractMarkdownPlainText(source: string): string {
  return source
    .replace(/```[^\n]*\n?/g, '')
    .replace(/`([^`]*)`/g, '$1')
    .replace(/!\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/^\s{0,3}(#{1,6}|>|[-*+]|\d+[.)])\s+/gm, '')
    .replace(/(\*\*|__)(.*?)\1/g, '$2')
    .replace(/(\*|_)(.*?)\1/g, '$2')
    .replace(/~~(.*?)~~/g, '$1')
    .replace(/^\s*\|?(\s*:?-{3,}:?\s*\|)+\s*$/gm, '')
    .replace(/\|/g, ' ')
}
