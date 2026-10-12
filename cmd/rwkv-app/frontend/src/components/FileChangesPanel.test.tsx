import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, expect, it, vi } from 'vitest'
import { FileChange, FileSnapshot } from '../../bindings/github.com/no22/RWKV-Agent/internal/agent/tools/models'
import { FileArtifact } from '../../bindings/github.com/no22/RWKV-Agent/internal/appstorage/models'
import FileChangesPanel from './FileChangesPanel'
import FileReviewPane from './FileReviewPane'

afterEach(cleanup)
const change = (path: string, before: string, after: string) => new FileChange({ path, before: new FileSnapshot({ kind: 'file', data: btoa(before), mode: 420 }), after: new FileSnapshot({ kind: 'file', data: btoa(after), mode: 420 }) })
it('starts with a compact summary and opens the exact file snapshot for review', () => {
 const c = change('a.txt', 'old\n', 'new\n'), resolve = vi.fn().mockResolvedValue(undefined), open = vi.fn()
 render(<FileChangesPanel changes={[c]} disabled={false} onResolve={resolve} onOpen={open} />)
 expect(screen.queryByRole('button',{name:'保存 a.txt'})).not.toBeInTheDocument()
 fireEvent.click(screen.getByRole('button', {name:/1 个文件待确认/}))
 fireEvent.click(screen.getByRole('button', {name: 'a.txt'}))
 expect(open).toHaveBeenCalledWith(expect.objectContaining({change:c}), 'diff')
 fireEvent.click(screen.getByRole('button', {name: '保存 a.txt'}))
 expect(resolve).toHaveBeenCalledWith([c], true)
})
it('groups a directory and its reviewed descendants when discarding', () => {
 const dir = new FileChange({path:'notes',before:new FileSnapshot({kind:'missing'}),after:new FileSnapshot({kind:'directory',mode:493})})
 const child=change('notes/a.txt','','draft'), other=change('b.txt','old','new'), resolve=vi.fn().mockResolvedValue(undefined)
 render(<FileChangesPanel changes={[dir,child,other]} disabled={false} onResolve={resolve} />)
 fireEvent.click(screen.getByRole('button', {name:/3 个文件待确认/}))
 fireEvent.click(screen.getByRole('button', {name:'丢弃 notes'}))
 expect(resolve).toHaveBeenCalledWith([dir,child],false)
})
it('keeps approved artifacts accessible while removing approval controls', () => {
 const c=change('index.html','','<h1>Hello</h1>'), open=vi.fn()
 render(<FileChangesPanel changes={[]} artifacts={[new FileArtifact({change:c,status:'saved'})]} disabled={false} onResolve={vi.fn()} onOpen={open} />)
 expect(screen.getByText('已保存')).toBeInTheDocument()
 expect(screen.queryByRole('button',{name:'保存'})).not.toBeInTheDocument()
 fireEvent.click(screen.getByRole('button',{name:'打开 index.html'}))
 expect(open).toHaveBeenCalledWith(expect.objectContaining({change:c,status:'saved'}),'preview')
})
it('disables file decisions while a turn is still running', () => {
 render(<FileChangesPanel changes={[change('a.txt','old','new')]} disabled onResolve={vi.fn()} />)
 fireEvent.click(screen.getByRole('button',{name:/1 个文件待确认/}))
 expect(screen.getByRole('button', {name:'保存 a.txt'})).toBeDisabled()
 expect(screen.getByRole('button', {name:'保存'})).toBeDisabled()
})
it('previews staged HTML in an isolated frame and permits diff inspection', () => {
 const c=change('index.html','','<h1>Hello</h1>'), file=new FileArtifact({change:c,status:'pending'}), onView=vi.fn()
 const {container}=render(<FileReviewPane file={file} view="preview" onView={onView} changes={[c]} disabled={false} onResolve={vi.fn()} onClose={vi.fn()} />)
 const frame=container.querySelector('iframe')!
 expect(frame.getAttribute('srcdoc')).toContain('<h1>Hello</h1>')
 expect(frame.getAttribute('srcdoc')).toContain('<base href="about:srcdoc">')
 expect(frame).toHaveAttribute('sandbox','allow-scripts')
 fireEvent.click(screen.getByRole('tab',{name:'改动'}))
 expect(onView).toHaveBeenCalledWith('diff')
})
it('shows actual changed lines in the diff view', () => {
 const c=change('a.txt','old\n','new\n')
 render(<FileReviewPane file={new FileArtifact({change:c,status:'pending'})} view="diff" onView={vi.fn()} changes={[c]} disabled={false} onResolve={vi.fn()} onClose={vi.fn()} />)
 expect(screen.getByText('-old')).toBeInTheDocument()
 expect(screen.getByText('+new')).toBeInTheDocument()
})

it('restores focus and accepts Escape only from the current preview frame', () => {
 const trigger=document.createElement('button'); document.body.append(trigger); trigger.focus()
 const c=change('index.html','','<h1>Hello</h1>'), close=vi.fn()
 const {container,unmount}=render(<FileReviewPane file={new FileArtifact({change:c,status:'pending'})} view="preview" onView={vi.fn()} changes={[c]} disabled={false} onResolve={vi.fn()} onClose={close} />)
 expect(screen.getByRole('button',{name:'关闭文件查看器'})).toHaveFocus()
 fireEvent(window,new MessageEvent('message',{source:window,data:{type:'rwkv-file-preview:escape'}}))
 expect(close).not.toHaveBeenCalled()
 const frame=container.querySelector('iframe')!
 fireEvent(window,new MessageEvent('message',{source:frame.contentWindow,data:{type:'rwkv-file-preview:escape'}}))
 expect(close).toHaveBeenCalledTimes(1)
 unmount();expect(trigger).toHaveFocus();trigger.remove()
})

it('opens non-HTML changes directly from the collapsed summary and file card', () => {
 const c=change('main.go','package old\n','package main\n'), open=vi.fn()
 render(<FileChangesPanel changes={[c]} disabled={false} onResolve={vi.fn()} onOpen={open} />)
 const actions=screen.getAllByRole('button',{name:'查看改动'})
 fireEvent.click(actions.at(-1)!)
 expect(open).toHaveBeenLastCalledWith(expect.objectContaining({change:c}), 'diff')
 fireEvent.click(screen.getByRole('button',{name:'打开 main.go'}))
 expect(open).toHaveBeenLastCalledWith(expect.objectContaining({change:c}), 'diff')
})

it('switches between reviewed files inside the same drawer', () => {
 const first=new FileArtifact({change:change('main.go','old','new'),status:'pending'})
 const second=new FileArtifact({change:change('config.json','{}','{"enabled":true}'),status:'pending'}), select=vi.fn()
 render(<FileReviewPane file={first} files={[first,second]} onFile={select} view="diff" onView={vi.fn()} changes={[]} disabled={false} onResolve={vi.fn()} onClose={vi.fn()} />)
 fireEvent.change(screen.getByRole('combobox',{name:'文件'}),{target:{value:'1'}})
 expect(select).toHaveBeenCalledWith(second)
 expect(screen.queryByRole('tab',{name:'预览'})).not.toBeInTheDocument()
})
