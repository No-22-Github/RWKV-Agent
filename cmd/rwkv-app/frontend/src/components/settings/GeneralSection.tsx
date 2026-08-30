import { FolderOpen, Moon, Sun } from 'lucide-react'
import type { Status } from '../../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { ThemeMode } from '../../theme'
import { GroupTitle, Row, Toggle } from './ui'

type Props = {
  status: Status
  onChooseWorkspace: () => void | Promise<void>
  theme: ThemeMode
  onToggleTheme: () => void
}

/* 通用：工作区与外观，全局生效，不随连接档案保存。 */
export default function GeneralSection({ status, onChooseWorkspace, theme, onToggleTheme }: Props) {
  const dark = theme === 'dark'
  return (
    <div className="mx-auto w-[min(720px,calc(100%-56px))] py-[24px]">
      <section>
        <GroupTitle title="工作区" hint="Agent 可读写的根目录" />
        <Row label="当前工作区" description={status.workspace || '未打开工作区'}>
          <button className="flex items-center gap-[7px] border border-line bg-paper-wash px-3 py-[8px] text-base text-ink-soft" onClick={() => void onChooseWorkspace()}><FolderOpen size={16} />选择文件夹</button>
        </Row>
      </section>
      <section className="mt-[24px]">
        <GroupTitle title="外观" />
        <Toggle icon={dark ? <Sun size={15} /> : <Moon size={15} />} label="深色模式" description="暗棕灰纸面，teal 提亮" checked={dark} onChange={() => onToggleTheme()} />
      </section>
    </div>
  )
}
