import { Provider } from '../../../bindings/github.com/no22/RWKV-Agent/api/models'
import type { ProviderManager } from '../../state/providerManager'

/*
 * 连接详情标签栏旁的一句话：说清这里的改动什么时候生效。不一刀切——远端运行中即时生效，
 * 本地模型要重新加载，新建连接要先保存建档。
 */
export function autosaveHint(manager: ProviderManager): string {
  if (manager.editingProviderId === '') return '新档案：先点右上「保存」建档，之后改动自动保存'
  if (manager.draftConfigValue.provider === Provider.ProviderLocal) return '自动保存；本地模型需「重新加载模型」后生效'
  return '自动保存；编辑运行中的远端档案时即时生效'
}
