import { Children, isValidElement, type ReactNode, useEffect, useRef, useState } from 'react'
import { Check, Copy, X } from 'lucide-react'
import { Highlight, Prism, type PrismTheme } from 'prism-react-renderer'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

type MarkdownMessageProps = {
  content: string
}

type CodeBlockProps = {
  className?: string
  code: string
}

const languageAliases: Record<string, string> = {
  csharp: 'csharp',
  'c#': 'csharp',
  'c++': 'cpp',
  html: 'markup',
  js: 'javascript',
  jsx: 'jsx',
  md: 'markdown',
  py: 'python',
  rb: 'ruby',
  sh: 'bash',
  shell: 'bash',
  text: 'plain',
  plaintext: 'plain',
  ts: 'typescript',
  tsx: 'tsx',
  xml: 'markup',
  yml: 'yaml',
  zsh: 'bash',
}

const languageLabels: Record<string, string> = {
  bash: 'Shell',
  c: 'C',
  cpp: 'C++',
  csharp: 'C#',
  css: 'CSS',
  diff: 'Diff',
  go: 'Go',
  graphql: 'GraphQL',
  javascript: 'JavaScript',
  json: 'JSON',
  jsx: 'React JSX',
  lua: 'Lua',
  markdown: 'Markdown',
  markup: 'HTML',
  plain: 'Plain text',
  python: 'Python',
  rust: 'Rust',
  sql: 'SQL',
  swift: 'Swift',
  tsx: 'React TSX',
  typescript: 'TypeScript',
  yaml: 'YAML',
}

const codeTheme: PrismTheme = {
  plain: { color: '#303642', backgroundColor: '#f7f8fa' },
  styles: [
    { types: ['comment', 'prolog', 'doctype', 'cdata'], style: { color: '#7b8492', fontStyle: 'italic' } },
    { types: ['keyword', 'atrule'], style: { color: '#7653b4', fontWeight: '600' } },
    { types: ['string', 'char', 'attr-value', 'regex'], style: { color: '#28766b' } },
    { types: ['number', 'boolean', 'constant'], style: { color: '#b65c25' } },
    { types: ['function', 'function-variable', 'class-name'], style: { color: '#356cbd' } },
    { types: ['operator', 'punctuation'], style: { color: '#687282' } },
    { types: ['property', 'parameter', 'attr-name', 'selector', 'variable'], style: { color: '#a05b18' } },
    { types: ['tag', 'namespace'], style: { color: '#a84070' } },
    { types: ['builtin', 'symbol', 'important'], style: { color: '#904738' } },
    { types: ['deleted'], style: { color: '#b94b4b', backgroundColor: '#fff0f0' } },
    { types: ['inserted'], style: { color: '#2d7450', backgroundColor: '#edf8f1' } },
  ],
}

export default function MarkdownMessage({ content }: MarkdownMessageProps) {
  const blocks = splitTopLevelBlocks(content)
  let plainCount = 0

  return (
    <div className="md-markdown">
      {blocks.map((block, index) => {
        const isPlain = isPlainParagraph(block)
        if (isPlain) plainCount++
        // 首个普通段落作为引言不编号，其后的论点从 1 开始编号（对齐设计稿的「引言 + 编号论点」）
        const numbered = isPlain && plainCount > 1
        const pointNumber = plainCount - 1
        const markdown = (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            skipHtml
            components={{
              pre({ children }) {
                const child = Children.toArray(children)[0]
                if (!isValidElement<{ className?: string; children?: ReactNode }>(child)) {
                  return <pre>{children}</pre>
                }
                return <CodeBlock className={child.props.className} code={textContent(child.props.children).replace(/\n$/, '')} />
              },
              table({ children, ...props }) {
                return (
                  <div className="overflow-x-auto">
                    <table {...props}>{children}</table>
                  </div>
                )
              },
              a({ href, children, ...props }) {
                const external = /^(?:https?:|mailto:)/i.test(href || '')
                return (
                  <a {...props} href={href} target={external ? '_blank' : undefined} rel={external ? 'noopener noreferrer' : undefined}>
                    {children}
                  </a>
                )
              },
            }}
          >
            {block}
          </ReactMarkdown>
        )

        if (!numbered) return <div key={index}>{markdown}</div>

        return (
          <div key={index} className="answer-para grid grid-cols-[22px_minmax(0,1fr)] items-baseline gap-[12px]">
            <span className="answer-para-num font-serif text-md font-bold leading-[1.95] text-brand">{pointNumber}</span>
            <div className="min-w-0">{markdown}</div>
          </div>
        )
      })}
    </div>
  )
}

function splitTopLevelBlocks(content: string): string[] {
  const lines = content.split('\n')
  const blocks: string[] = []
  let current: string[] = []
  let inFence = false
  for (const line of lines) {
    if (/^\s*(```|~~~)/.test(line)) {
      inFence = !inFence
      current.push(line)
      continue
    }
    if (!inFence && line.trim() === '') {
      if (current.length > 0) {
        blocks.push(current.join('\n'))
        current = []
      }
      continue
    }
    current.push(line)
  }
  if (current.length > 0) blocks.push(current.join('\n'))
  return blocks
}

function isPlainParagraph(block: string): boolean {
  const trimmed = block.trim()
  if (!trimmed) return false
  if (/^(#{1,6})\s/.test(trimmed)) return false
  if (/^([-*+]|\d+[.)])\s+/.test(trimmed)) return false
  if (/^```|^~~~/.test(trimmed)) return false
  if (/^>\s?/.test(trimmed)) return false
  if (/^\s*\|/.test(trimmed) || trimmed.includes('\n|')) return false
  return true
}

function CodeBlock({ className, code }: CodeBlockProps) {
  const [copyState, setCopyState] = useState<'idle' | 'copied' | 'failed'>('idle')
  const resetTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const detectedLanguage = className?.match(/(?:language|lang)-([\w#+-]+)/)?.[1]?.toLowerCase()
  const normalizedLanguage = normalizeLanguage(detectedLanguage)
  const language = Prism.languages[normalizedLanguage] ? normalizedLanguage : 'plain'
  const label = languageLabel(detectedLanguage)

  useEffect(() => () => {
    if (resetTimer.current) clearTimeout(resetTimer.current)
  }, [])

  async function copyCode() {
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(code)
      } else if (!fallbackCopy(code)) {
        throw new Error('copy failed')
      }
      setCopyState('copied')
    } catch {
      setCopyState('failed')
    }
    if (resetTimer.current) clearTimeout(resetTimer.current)
    resetTimer.current = setTimeout(() => setCopyState('idle'), 1500)
  }

  const copyClass =
    copyState === 'copied' ? 'text-brand' : copyState === 'failed' ? 'text-danger' : 'text-ink-muted hover:text-brand';

  return (
    <div className="my-4 overflow-hidden rounded border border-line bg-[#f7f8fa]">
      <div className="flex items-center justify-between gap-2 border-b border-line bg-[#f1f2f5] px-3 py-1.5">
        <span className="font-mono text-2xs font-medium text-ink-muted">{label}</span>
        <button
          type="button"
          className={`flex items-center gap-1 rounded px-2 py-1 font-sans text-2xs transition-colors ${copyClass}`}
          onClick={() => void copyCode()}
          aria-label={`复制 ${label} 代码`}
        >
          {copyState === 'copied' ? <Check size={14} /> : copyState === 'failed' ? <X size={14} /> : <Copy size={14} />}
          <span>{copyState === 'copied' ? '已复制' : copyState === 'failed' ? '复制失败' : '复制'}</span>
        </button>
      </div>
      <Highlight theme={codeTheme} code={code} language={language}>
        {({ className: prismClassName, style, tokens, getLineProps, getTokenProps }) => (
          <pre className={`${prismClassName} overflow-auto p-3 font-mono text-sm leading-relaxed`} style={style} tabIndex={0}>
            <code>
              {tokens.map((line, lineIndex) => (
                <span {...getLineProps({ line })} className="block" key={lineIndex}>
                  {line.map((token, tokenIndex) => <span {...getTokenProps({ token })} key={tokenIndex} />)}
                </span>
              ))}
            </code>
          </pre>
        )}
      </Highlight>
    </div>
  )
}

function normalizeLanguage(language?: string) {
  if (!language) return 'plain'
  return languageAliases[language] || language
}

function languageLabel(language?: string) {
  const normalized = normalizeLanguage(language)
  return languageLabels[normalized] || language || 'Plain text'
}

function textContent(value: ReactNode): string {
  if (typeof value === 'string' || typeof value === 'number') return String(value)
  if (Array.isArray(value)) return value.map(textContent).join('')
  if (isValidElement<{ children?: ReactNode }>(value)) return textContent(value.props.children)
  return ''
}

function fallbackCopy(code: string) {
  const textarea = document.createElement('textarea')
  textarea.value = code
  textarea.readOnly = true
  textarea.style.position = 'fixed'
  textarea.style.top = '-9999px'
  document.body.appendChild(textarea)
  textarea.select()
  const copied = document.execCommand('copy')
  textarea.remove()
  return copied
}
