import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { System } from '@wailsio/runtime'
import App from './App'
import { applyTheme, getInitialTheme } from './theme'
import '@fontsource/noto-serif-sc/400.css'
import '@fontsource/noto-serif-sc/600.css'
import '@fontsource/noto-serif-sc/700.css'
import '@fontsource/jetbrains-mono/400.css'
import '@fontsource/jetbrains-mono/500.css'
import '@fontsource/jetbrains-mono/700.css'
import './tailwind.css'
import './index.css'
import './legacy.css'

// 仅桌面 macOS webview 会注入 window._wails；据此为隐藏式内嵌标题栏（红绿灯）预留顶部空间。
function detectMacDesktop(): boolean {
  try {
    return typeof window !== 'undefined' && !!(window as unknown as { _wails?: unknown })._wails && System.IsMac()
  } catch {
    return false
  }
}

document.documentElement.classList.toggle('wails-mac', detectMacDesktop())
applyTheme(getInitialTheme())

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
