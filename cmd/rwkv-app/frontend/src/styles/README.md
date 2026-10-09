# 样式组织

全局入口为 `src/index.css`，只在 `main.tsx` 导入。

- `styles/tokens.css`：应用亮暗主题与语义变量。
- `tailwind.css`：使用 `@theme inline` 将应用变量映射为工具类；`@theme` 定义 `animate-*`；`@utility` 定义正文宽度、流光、流式块和输入框运行高光。
- `styles/base.css`：`@layer base` 文档默认、焦点和滚动条。
- `styles/markdown.css`：`@layer components` 消息正文排版。

组件布局与交互直接使用工具类。窗口收窄使用 `compact:*`（包含 1180px 边界）；抽屉使用 `lg:*`；桌面适配使用 `wails-mac:*`；会话菜单使用具名 group 与 data 状态；动画搭配 `motion-reduce:animate-none`。复杂 utility 内部自行处理减少动态效果。

`turn-enter`、`answer-reveal`、`stream-tok` 等标记保留供行为测试使用，不再承担全局 CSS 样式。

轨迹页保留邻近组件的 CSS Modules，`trajectory/tokens.css` 适配 DSH 变量。portal 菜单、Markdown 容器和导出按钮直接使用 Tailwind。不要用长串任意值替换已有的复杂表格排版模块。
