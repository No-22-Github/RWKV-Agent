# RWKV-Agent 文档索引

> 根目录 [`README.md`](../README.md) 是入口。这里按用途列出 `docs/` 下的全部文档。
>
> [English README](../README.en.md)

## 上手

| 文档 | 说明 |
| --- | --- |
| [getting-started-macos.md](getting-started-macos.md) | macOS 从零上手：环境、构建、模型准备、运行、更新与常见问题 |
| [app.md](app.md) | Wails V3 桌面 App 与 headless server：构建、公开 API、持久化存储、配置与开发 |

## 设计与协议

| 文档 | 说明 |
| --- | --- |
| [inference-core-design.md](inference-core-design.md) | 跨平台推理核心设计：分层、对象生命周期、State 模型、调度与契约测试 |
| [direct-pth-loading.md](direct-pth-loading.md) | 直接加载 `.pth`：mmap、索引缓存、转换链路 |
| [continuation-and-agent-protocol.md](continuation-and-agent-protocol.md) | 续写接口与 Agent 协议边界：内建协议、渐进式工具、远程 Provider 映射 |
| [agent-harness-milestone.md](agent-harness-milestone.md) | 早期 XML Harness 里程碑与路线（历史文档，不代表当前默认协议） |

## 评测与基线

| 文档 | 说明 |
| --- | --- |
| [evaluations/primitive-bench-v12-baseline-2026-08-13.md](evaluations/primitive-bench-v12-baseline-2026-08-13.md) | Primitive Bench v12 基线，以及 v13–v21 演进、失败分类与政策记录 |
| [evaluations/api-13b-evaluation-report-20260803.md](evaluations/api-13b-evaluation-report-20260803.md) | RWKV G1I 13B Harness 实测问题报告（2026-08-03） |
| [evaluations/api-13b-v8-evaluation-report-20260805.md](evaluations/api-13b-v8-evaluation-report-20260805.md) | RWKV 13.3B 20260805 Harness 评测（v8 profile） |
| [evaluations/api-13b-v9-evaluation-report-20260806.md](evaluations/api-13b-v9-evaluation-report-20260806.md) | 20260806 三项修复后的复测报告 |
| [evaluations/local-assistant-p0-effect-report-20260804.md](evaluations/local-assistant-p0-effect-report-20260804.md) | 本地优先助手 Agent P0 落地效果报告 |
| [evaluations/bfcl-v4-ab-main-integration-20260826.md](evaluations/bfcl-v4-ab-main-integration-20260826.md) | BFCL v4 A+B 分支收口、证据边界与主线迁移说明 |

## 报告

| 文档 | 说明 |
| --- | --- |
| [reports/harness-layer-optimization-report.html](reports/harness-layer-optimization-report.html) | Harness 层优化报告（中文 HTML） |
| [reports/harness-layer-optimization-report-en.html](reports/harness-layer-optimization-report-en.html) | Harness 层优化报告（English HTML） |

## 归档

| 文档 | 说明 |
| --- | --- |
| [archive/rwkv-mobile-adoption-and-cli-milestone.md](archive/rwkv-mobile-adoption-and-cli-milestone.md) | RWKV Mobile 采用与 CLI 里程碑（历史计划） |
| [archive/rwkv-mobile-macos-cli-implementation-plan.md](archive/rwkv-mobile-macos-cli-implementation-plan.md) | RWKV Mobile macOS CLI 实施计划（历史计划） |
| [archive/rwkv-cli-tui-redesign-plan.md](archive/rwkv-cli-tui-redesign-plan.md) | CLI TUI 重设计计划（历史计划） |
| [archive/macos-cli-implementation-validation.md](archive/macos-cli-implementation-validation.md) | macOS CLI 实现验证记录 |
| [archive/local-assistant-agent-plan.md](archive/local-assistant-agent-plan.md) | 本地助手 Agent 计划（历史） |
| [archive/rwkv-g1i-13b-agent-data-feedback.md](archive/rwkv-g1i-13b-agent-data-feedback.md) | G1I 13B Agent 数据反馈记录 |

## 约定

- `docs/evaluations/` 存放实测数据、基线与复跑说明；单一文档会随复跑持续追加，例如
  `primitive-bench-v12-baseline-2026-08-13.md` 虽然以 v12 命名，也包含后续 v13–v21 的
  演进记录。
- `docs/reports/` 存放长报告（HTML/PDF 等）。
- `docs/archive/` 只归档、不再维护；其中过时的协议描述不应作为当前行为依据。
- 目录重组或改名时，同步更新本索引与两个 README 中的链接。
