import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import MarkdownMessage from './MarkdownMessage'

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
})

describe('MarkdownMessage', () => {
  it('keeps standalone bold section titles outside preceding lists without a blank line', () => {
    const content = '**近期天气**  \n- 晴，16~26°C  \n- 阴，17~25°C  \n**热门景点**  \n1. **博物院**  \n   - 门票：免费  \n   - **馆内展览**  \n     - 历史展厅  \n**出游建议**  \n- 提前预约'
    for (const streaming of [false, true]) {
      const { container, unmount } = render(<MarkdownMessage content={content} streaming={streaming} />)
      for (const title of ['近期天气', '热门景点', '出游建议']) {
        const heading = [...container.querySelectorAll('strong')].find((node) => node.textContent === title)!
        expect(heading).toBeDefined()
        expect(heading.closest('li, ul, ol, .answer-para')).toBeNull()
      }
      expect(container.querySelector('ol > li > ul')).toHaveTextContent('门票：免费')
      expect(container.querySelector('ol > li > ul > li > ul')).toHaveTextContent('历史展厅')
      expect(container.querySelector('ol > li > ul')).toHaveTextContent('馆内展览')
      unmount()
    }
  })

  it('preserves bold-looking lines inside fenced code', () => {
    const { container } = render(<MarkdownMessage content={'```md\n- 天气\n**热门景点**\n1. 博物院\n```'} />)
    expect(container.querySelectorAll('pre')).toHaveLength(1)
    expect(container.querySelector('pre')).toHaveTextContent('**热门景点**')
    expect(container.querySelector('strong')).toBeNull()
  })

  it('keeps single tildes literal and only strikes through double tildes', () => {
    const content = '晴，16~26°C，体感温度约17~26°C。~保留~，~~删除~~。'
    for (const streaming of [false, true]) {
      const { container, unmount } = render(<MarkdownMessage content={content} streaming={streaming} />)
      expect(container.textContent).toBe('晴，16~26°C，体感温度约17~26°C。~保留~，删除。')
      const deletions = container.querySelectorAll('del')
      expect(deletions).toHaveLength(1)
      expect(deletions[0]).toHaveTextContent('删除')
      unmount()
    }
  })

  it('splits streamed prose into per-token spans but leaves code and settled text whole', () => {
    const content = '杭州 is **lovely**\n\n```js\nconst a = 1\n```'
    const { container, rerender } = render(<MarkdownMessage content={content} streaming />)
    const tokens = [...container.querySelectorAll('.stream-tok')].map((node) => node.textContent)
    expect(tokens).toEqual(['杭', '州', ' ', 'is ', 'lovely'])
    expect(container.querySelector('code .stream-tok')).toBeNull()
    expect(container.textContent).toContain('const a = 1')

    rerender(<MarkdownMessage content={content} />)
    expect(container.querySelector('.stream-tok')).toBeNull()
  })

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

  it('ends bare URLs at the first full-width punctuation or CJK character', () => {
    const content = '可参考重庆旅游攻略（https://www.trip.com/travel-guide/chongqing/）——第一次去重庆的必去景点。另见 [官网](https://www.cq.gov.cn/中文路径)'
    for (const streaming of [false, true]) {
      const { container, unmount } = render(<MarkdownMessage content={content} streaming={streaming} />)
      const links = [...container.querySelectorAll('a')]
      expect(links[0]).toHaveAttribute('href', 'https://www.trip.com/travel-guide/chongqing/')
      expect(links[0]).toHaveTextContent(/^https:\/\/www\.trip\.com\/travel-guide\/chongqing\/$/)
      expect(container.textContent).toContain('/）——第一次去重庆的必去景点。')
      // 显式 [文字](地址) 的链接不截断。
      expect(links[1]).toHaveTextContent('官网')
      expect(decodeURI(links[1].getAttribute('href') || '')).toBe('https://www.cq.gov.cn/中文路径')
      unmount()
    }
  })
})
