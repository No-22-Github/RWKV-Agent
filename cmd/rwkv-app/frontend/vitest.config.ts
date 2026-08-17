import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'jsdom',
    execArgv: ['--no-experimental-webstorage'],
    setupFiles: './src/test-setup.ts',
    // @material/material-color-utilities 内部使用无扩展名的 ESM 相对导入，
    // Vite/rolldown 构建可解析，但 Vitest 的 node 解析器不行；inline 走 Vite 转换管线即可修复。
    server: {
      deps: {
        inline: ['@material/material-color-utilities'],
      },
    },
  },
})
