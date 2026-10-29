import { useEffect, useRef, useState } from 'react'
import { AgentSettings } from '../../bindings/github.com/no22/RWKV-Agent/internal/appstorage/models'
import * as Backend from '../../bindings/github.com/no22/RWKV-Agent/cmd/rwkv-app/appservice'
import { useSnackbar } from '../snackbar'
import type { SaveState } from './providerManager'
import { matchSamplingPreset, normalizeSampling, presetById } from './samplingPresets'

// 测试里缩短防抖，免得每个自动保存用例白等大半秒。
const AUTOSAVE_DELAY_MS = import.meta.env.MODE === 'test' ? 50 : 600

/*
 * 所有连接共用的 Agent 设置：采样、预算、工具开关与调度、提示词，以及搜索 Key、搜索路由、
 * 天气数据源。和用哪个端点无关，只存一份（appstorage.AgentSettings），换连接不用重设。
 * 设置打开时读一次，改动停顿后自动保存，后端让运行中的模型下一轮就用上（不重连、不重新加载）。
 * 挂在 App 上而不是设置页里，关掉设置时还在防抖中的改动照样会存下去。
 */
export function useAgentSettings(open: boolean) {
  const { show: notify } = useSnackbar()
  const [value, setValue] = useState(() => new AgentSettings())
  const [loaded, setLoaded] = useState(false)
  const [saveState, setSaveState] = useState<SaveState>({ kind: 'idle' })
  // 选了「自定义」或打开的是一组非预设数值：展开六个采样输入。
  const [advancedSampling, setAdvancedSampling] = useState(false)
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
        setAdvancedSampling(matchSamplingPreset(normalizeSampling(next)) === '')
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
          notify('Agent 设置已保存，所有连接下一轮生效', 'success', { key: 'agent-settings' })
        })
        .catch((error) => {
          setSaveState({ kind: 'error', message: `保存失败：${errorText(error)}` })
          notify(`Agent 设置保存失败：${errorText(error)}`, 'error', { key: 'agent-settings' })
        })
    }, AUTOSAVE_DELAY_MS)
    return () => clearTimeout(timer)
  }, [value, loaded])

  function update(patch: Partial<AgentSettings>) {
    setValue((current) => new AgentSettings({ ...current, ...patch }))
  }

  /*
   * 反查当前数值属于哪个预设。数值被改过（或存着一组非预设的组合）就报自定义，
   * 并把高级输入展开——否则选择器会显示一个名字，而实际发出去的是别的数。
   */
  const samplingValues = normalizeSampling(value)
  const matchedSamplingPreset = matchSamplingPreset(samplingValues)
  const samplingIsCustom = advancedSampling || matchedSamplingPreset === ''

  /* 选中一个预设：六个参数一起写成测量过的那组值；选"自定义"只展开输入，不动数值。 */
  function applySamplingPreset(id: string) {
    const preset = presetById(id)
    if (!preset) {
      setAdvancedSampling(true)
      return
    }
    update({
      temperature: preset.temperature, topK: preset.topK, topP: preset.topP,
      presencePenalty: preset.presencePenalty, frequencyPenalty: preset.frequencyPenalty, penaltyDecay: preset.penaltyDecay,
    })
    setAdvancedSampling(false)
  }

  return { value, loaded, saveState, update, samplingValues, matchedSamplingPreset, samplingIsCustom, applySamplingPreset }
}

export type AgentSettingsState = ReturnType<typeof useAgentSettings>

/*
 * 对话页能力开关用：不经设置页，直接读一份最新的共用设置、改一项、存回去。
 * 后端保存后广播 providers:changed，运行配置（芯片的开关状态）随之刷新。
 */
export async function patchAgentSettings(patch: Partial<AgentSettings>) {
  const current = AgentSettings.createFrom(await Backend.GetAgentSettings())
  await Backend.SaveAgentSettings(new AgentSettings({ ...current, ...patch }))
}

function errorText(error: unknown): string {
  return error instanceof Error ? error.message : String(error)
}
