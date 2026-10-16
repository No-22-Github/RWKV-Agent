/*
 * 选一个本机文件上传。桌面版走系统对话框，拿到的是路径（后端记下来，服务端重启后可一键重传）；
 * 网页版（server 模式）没有系统对话框，走浏览器的文件选择框，文件先发给 App 服务暂存，
 * 再由绑定转发给部署——这种上传没有可记住的本机路径。
 */
export type PickedFile = { kind: 'path'; path: string; name: string } | { kind: 'browser'; file: File; name: string }

export async function pickLocalFile(browser: boolean, native: () => Promise<string>, accept = '.pth'): Promise<PickedFile | null> {
  if (!browser) {
    const path = await native()
    return path ? { kind: 'path', path, name: baseName(path) } : null
  }
  const file = await browserPick(accept)
  return file ? { kind: 'browser', file, name: file.name } : null
}

/** 把浏览器选的文件交给 App 服务暂存，返回给 UploadBrowser* 绑定用的 token。 */
export async function stageBrowserFile(file: File): Promise<string> {
  const response = await fetch(`/app/upload?name=${encodeURIComponent(file.name)}`, { method: 'POST', body: file })
  if (!response.ok) throw new Error(`发送文件失败：${(await response.text()).trim() || response.status}`)
  const body = await response.json() as { token?: string }
  if (!body.token) throw new Error('发送文件失败：服务没有返回 token')
  return body.token
}

function browserPick(accept: string): Promise<File | null> {
  return new Promise((resolve) => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = accept
    input.addEventListener('change', () => resolve(input.files?.[0] ?? null), { once: true })
    input.addEventListener('cancel', () => resolve(null), { once: true })
    input.click()
  })
}

export function baseName(path: string): string {
  const index = Math.max(path.lastIndexOf('/'), path.lastIndexOf('\\'))
  return index >= 0 ? path.slice(index + 1) : path
}
