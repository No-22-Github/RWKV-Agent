import { useEffect, useRef, useState } from 'react'
import { AgentSettings } from '../../bindings/github.com/no22/RWKV-Agent/internal/appstorage/models'
import * as Backend from '../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import type { SaveState } from './providerManager'

const AUTOSAVE_DELAY_MS = 600

/*
 * 所有连接共用的 Agent 设置（搜索 Key、搜索路由、天气数据源）：设置打开时读一次，
 * 改动停顿后自动保存，后端让运行中的模型下一轮就用上。挂在 App 上而不是设置页里，
 * 关掉设置时还在防抖中的改动照样会存下去。
 */
export function useAgentSettings(open: boolean) {
  const [value, setValue] = useState(() => new AgentSettings())
  const [loaded, setLoaded] = useState(false)
  const [saveState, setSaveState] = useState<SaveState>({ kind: 'idle' })
  const savedRef = useRef('')

  useEffect(() => {
    if (!open) return
    let cancelled = false
    Backend.GetAgentSettings()
      .then((loadedValue) => {
        if (cancelled) return
        const next = AgentSettings.createFrom(loadedValue)
        savedRef.current = JSON.stringify(next)
        setValue(next)
        setLoaded(true)
        setSaveState({ kind: 'idle' })
      })
      .catch((error) => {
        if (!cancelled) setSaveState({ kind: 'error', message: `读取失败：${errorText(error)}` })
      })
    return () => { cancelled = true }
  }, [open])

  useEffect(() => {
    if (!loaded) return
    const signature = JSON.stringify(value)
    if (signature === savedRef.current) return
    setSaveState({ kind: 'pending', message: '待保存…' })
    const timer = setTimeout(() => {
      setSaveState({ kind: 'saving', message: '正在保存…' })
      Backend.SaveAgentSettings(value)
        .then(() => {
          savedRef.current = signature
          setSaveState({ kind: 'saved', message: '已保存，下一轮对话生效' })
        })
        .catch((error) => setSaveState({ kind: 'error', message: `保存失败：${errorText(error)}` }))
    }, AUTOSAVE_DELAY_MS)
    return () => clearTimeout(timer)
  }, [value, loaded])

  function update(patch: Partial<AgentSettings>) {
    setValue((current) => new AgentSettings({ ...current, ...patch }))
  }

  return { value, loaded, saveState, update }
}

export type AgentSettingsState = ReturnType<typeof useAgentSettings>

function errorText(error: unknown): string {
  return error instanceof Error ? error.message : String(error)
}
