import { Children, isValidElement, type ReactNode, useEffect, useRef, useState } from 'react'
import { Check, Copy, X } from 'lucide-react'
import { Highlight, Prism, type PrismTheme } from 'prism-react-renderer'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

type MarkdownMessageProps = {
  content: string
  // 流式生成中：正文按字（英文按词）拆成 span，新挂载的字各自由虚到实；落定后不拆。
  streaming?: boolean
  // 流式模式下前多少个字是「已经播过动画」的（切页回来时恢复的进度）：这部分静态显示，不再淡入。
  staticChars?: number
}

// 最小 hast 形状：只为下面的拆字插件服务，避免为此引入 @types/hast。
type HastNode = { type: string; tagName?: string; value?: string; properties?: Record<string, unknown>; children?: HastNode[] }

// 中日韩字符逐字、其余按词（连同空白）切分。
const STREAM_TOKEN = /[\u2e80-\u9fff\uf900-\ufaff\uff00-\uffef\u3000-\u303f]|[^\s\u2e80-\u9fff\uf900-\ufaff\uff00-\uffef\u3000-\u303f]+\s*|\s+/g

// rehype 插件：把文本节点拆成 .stream-tok span。React 按位置复用已有 span，
// 只有新追加的字才挂载、才播放入场动画。代码块保持整段文本（CodeBlock 要取纯文本高亮）。
// skip：本块里前多少个渲染字符已经播过动画，标成 stream-tok-static。按渲染后的字符计数，
// 而 skip 来自原文偏移（含 Markdown 记号），会略微多算几个字为静态，可以接受。
function rehypeStreamTokens(skip = 0) {
  return () => (tree: HastNode) => {
    let offset = 0
    const split = (node: HastNode) => {
      if (!node.children || node.tagName === 'code' || node.tagName === 'pre') return
      node.children = node.children.flatMap((child): HastNode[] => {
        if (child.type !== 'text' || !child.value) { split(child); return [child] }
        return (child.value.match(STREAM_TOKEN) || []).map((token) => {
          const seen = offset < skip
          offset += token.length
          return { type: 'element', tagName: 'span', properties: { className: [seen ? 'stream-tok-static' : 'stream-tok'] }, children: [{ type: 'text', value: token }] }
        })
      })
    }
    split(tree)
  }
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
  plain: { color: 'var(--ink)', backgroundColor: 'transparent' },
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

export default function MarkdownMessage({ content, streaming, staticChars = 0 }: MarkdownMessageProps) {
  const blocks = splitTopLevelBlocks(content)
  let plainCount = 0
  let cursor = 0

  return (
    <div className="md-markdown">
      {blocks.map((block, index) => {
        const isPlain = isPlainParagraph(block)
        if (isPlain) plainCount++
        // 首个普通段落作为引言不编号，其后的论点从 1 开始编号（对齐设计稿的「引言 + 编号论点」）
        const numbered = isPlain && plainCount > 1
        const pointNumber = plainCount - 1
        const start = Math.max(cursor, content.indexOf(block, cursor))
        cursor = start + block.length
        // 整块都在恢复进度之内：不拆字、不做块级淡入；跨越边界的块只把前半截标成静态。
        const blockStatic = Boolean(streaming) && cursor <= staticChars
        const tokens = streaming && !blockStatic ? [rehypeStreamTokens(Math.max(0, staticChars - start))] : undefined
        const markdown = (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={tokens}
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

        const staticClass = streaming && start < staticChars ? 'stream-static' : undefined
        if (!numbered) return <div key={index} className={staticClass}>{markdown}</div>

        return (
          <div key={index} className={`answer-para grid grid-cols-[22px_minmax(0,1fr)] items-baseline gap-[12px]${staticClass ? ` ${staticClass}` : ''}`}>
            <span className="answer-para-num text-md font-bold leading-[1.95] text-brand">{pointNumber}</span>
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
    <div className="my-4 overflow-hidden rounded-lg border border-line bg-paper-soft">
      <div className="flex items-center justify-between gap-2 border-b border-line bg-surface-active px-3 py-1.5">
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
