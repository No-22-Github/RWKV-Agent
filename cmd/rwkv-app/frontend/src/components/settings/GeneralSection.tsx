import type { ReactNode } from 'react'
import { FolderOpen, Monitor, Moon, Sun } from 'lucide-react'
import type { Status } from '../../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { ThemePreference } from '../../theme'
import { Button, GroupTitle, Row, Segmented, SettingsPane } from './ui'

const THEME_OPTIONS: { value: ThemePreference; label: string; icon: ReactNode }[] = [
  { value: 'system', label: '跟随系统', icon: <Monitor size={13} /> },
  { value: 'light', label: '浅色', icon: <Sun size={13} /> },
  { value: 'dark', label: '深色', icon: <Moon size={13} /> },
]

/* 通用：工作区，全局生效，不随连接档案保存。 */
export default function GeneralSection({ status, onChooseWorkspace }: { status: Status; onChooseWorkspace: () => void | Promise<void> }) {
  return (
    <SettingsPane>
      <GroupTitle title="工作区" hint="Agent 可读写的根目录" />
      <Row label="当前工作区" description={status.workspace || '未打开工作区'}>
        <Button icon={<FolderOpen size={14} />} onClick={() => void onChooseWorkspace()}>选择文件夹</Button>
      </Row>
    </SettingsPane>
  )
}

/* 外观：只存在本机浏览器存储里，不随连接档案保存。 */
export function AppearanceSection({ themePreference, onThemeChange }: { themePreference: ThemePreference; onThemeChange: (preference: ThemePreference) => void }) {
  return (
    <SettingsPane>
      <GroupTitle title="主题" />
      <Row label="颜色模式" description="跟随系统时，macOS 切换浅色/深色外观后这里自动跟着变">
        <Segmented label="颜色模式" value={themePreference} onChange={onThemeChange} options={THEME_OPTIONS} />
      </Row>
    </SettingsPane>
  )
}
