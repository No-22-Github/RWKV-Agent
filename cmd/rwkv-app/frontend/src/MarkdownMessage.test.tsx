import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import MarkdownMessage from './MarkdownMessage'

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
})

describe('MarkdownMessage', () => {
  it('renders GFM content and keeps external links isolated', () => {
    render(<MarkdownMessage content={'## 结果\n\n- [x] 已完成\n\n| 名称 | 状态 |\n| --- | --- |\n| Agent | **正常** |\n\n[来源](https://example.test)'} />)

    expect(screen.getByRole('heading', { name: '结果' })).toBeInTheDocument()
    expect(screen.getByRole('checkbox')).toBeChecked()
    expect(screen.getByRole('table')).toBeInTheDocument()
    expect(screen.getByText('正常')).toHaveStyle({ fontWeight: 'bold' })
    expect(screen.getByRole('link', { name: '来源' })).toMatchObject({ target: '_blank', rel: 'noopener noreferrer' })
  })

  it('renders and copies highlighted fenced code without injecting HTML', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined)
    Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText } })
    const { container } = render(<MarkdownMessage content={'```ts\nconst answer = 42\n```\n\n<script>alert("unsafe")</script>'} />)

    expect(container.querySelector('script')).toBeNull()
    expect(container.querySelector('pre')).toHaveTextContent('const answer = 42')
    const copyButton = screen.getByRole('button', { name: '复制 TypeScript 代码' })
    fireEvent.click(copyButton)

    await waitFor(() => expect(writeText).toHaveBeenCalledWith('const answer = 42'))
    expect(screen.getByText('已复制')).toBeInTheDocument()
  })

  it('treats an unlabelled fence as a block and inline code as inline', () => {
    const { container } = render(<MarkdownMessage content={'`inline`\n\n```\nplain block\n```'} />)

    expect(container.querySelector('pre')).toHaveTextContent('plain block')
    expect(screen.getByRole('button', { name: '复制 Plain text 代码' })).toBeInTheDocument()
    expect(container.querySelector(':not(pre) > code')).toHaveTextContent('inline')
  })
})
