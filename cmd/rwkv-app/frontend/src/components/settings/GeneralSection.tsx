import type { ReactNode } from 'react'
import { FolderOpen, Monitor, Moon, Sun } from 'lucide-react'
import type { Status } from '../../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { ThemePreference } from '../../theme'
import { Button, Row, Section, Segmented, SettingsPane } from './ui'

const THEME_OPTIONS: { value: ThemePreference; label: string; icon: ReactNode }[] = [
  { value: 'system', label: '跟随系统', icon: <Monitor size={13} /> },
  { value: 'light', label: '浅色', icon: <Sun size={13} /> },
  { value: 'dark', label: '深色', icon: <Moon size={13} /> },
]

/* 通用：工作区，全局生效，不随连接档案保存。 */
export default function GeneralSection({ status, onChooseWorkspace }: { status: Status; onChooseWorkspace: () => void | Promise<void> }) {
  return (
    <SettingsPane>
      <Section title="工作区">
        <Row label="当前工作区" description={status.workspace || '未打开工作区'}>
          <Button icon={<FolderOpen size={14} />} onClick={() => void onChooseWorkspace()}>选择文件夹</Button>
        </Row>
      </Section>
    </SettingsPane>
  )
}

/* 外观：只存在本机浏览器存储里，不随连接档案保存。 */
export function AppearanceSection({ themePreference, onThemeChange }: { themePreference: ThemePreference; onThemeChange: (preference: ThemePreference) => void }) {
  return (
    <SettingsPane>
      <Section title="主题">
        <Row label="颜色模式">
          <Segmented label="颜色模式" value={themePreference} onChange={onThemeChange} options={THEME_OPTIONS} />
        </Row>
      </Section>
    </SettingsPane>
  )
}
