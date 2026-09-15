# RWKV-Agent 文档索引

> 根目录 [`README.md`](../README.md) 是使用入口，[`INDEX.md`](../INDEX.md) 是项目总索引。
> 这里按用途列出 `docs/` 下的全部文档。
>
> [English README](../README.en.md)

## 上手指南

| 文档 | 说明 |
| --- | --- |
| [getting-started-macos.md](getting-started-macos.md) | macOS 从零上手：环境、构建、模型准备、运行、更新与常见问题 |
| [app.md](app.md) | Wails V3 桌面 App 与 headless server：构建、公开 API、持久化存储、配置与开发 |

## 工具调用与对话格式 (Wire & Protocols)

| 文档 | 说明 |
| --- | --- |
| [tool-and-wire-formats.md](tool-and-wire-formats.md) | **★ 工具格式与对话协议门户 ★**：RWKV 续写到 Agent 动作的分层、G1K 现行推荐、全景对比矩阵与演进历程 |
| [corpus-g1k-wire-format.md](corpus-g1k-wire-format.md) | **数据侧逐字节契约**：G1K 对齐语料生产/清洗标准（System、`<tools>`、User `<tool_response>`、纯文本终答） |
| [wire-configuration.md](wire-configuration.md) | **运行时配置指南**：Spec 参数全表、Profile 预设、CLI/API 统一入口（受单测锁守护） |
| [continuation-and-agent-protocol.md](continuation-and-agent-protocol.md) | **架构与协议实现**：ActionProtocol、PromptRenderer 与 Provider 续写分层设计 |

## 设计与底层架构

| 文档 | 说明 |
| --- | --- |
| [inference-core-design.md](inference-core-design.md) | 跨平台推理核心设计：分层、对象生命周期、State 模型、调度与契约测试 |
| [direct-pth-loading.md](direct-pth-loading.md) | 直接加载 `.pth`：mmap、索引缓存、转换链路 |

## 现行评测基准

| 文档 | 说明 |
| --- | --- |
| [evaluations/g1k-wire-ablation/wire-ablation-g1k-summary-20260915.md](evaluations/g1k-wire-ablation/wire-ablation-g1k-summary-20260915.md) | **G1K 现行消融旗舰**：Wire 格式 R0–R4 消融总结（40→49 题，请求字节 −56%） |
| [evaluations/bfcl-v4-product-suite-20260826.md](evaluations/bfcl-v4-product-suite-20260826.md) | **现行评测题库**：60 题 BFCL 产品语义迁移 suite 规格与运行边界 |
| [evaluations/primitive-bench-v12-baseline-2026-08-13.md](evaluations/primitive-bench-v12-baseline-2026-08-13.md) | **持续演进基准**：Primitive Bench v12 基线，以及 v13–v21 持续追加演进记录 |

## 评测专题与历史证据库

### [G1K Wire 格式消融实验专题 (2026-09-15)](evaluations/g1k-wire-ablation/README.md)
- [00-r0-baseline.md](evaluations/g1k-wire-ablation/00-r0-baseline.md) | R0 干净基线 ×3（40/60，零抖动确定性）
- [01-r1-align.md](evaluations/g1k-wire-ablation/01-r1-align.md) | R1 标签对齐（41/60，User 轮 `<tool_response>` 与 `<tools>` 目录，采纳）
- [02-r1.5-probe-nocall.md](evaluations/g1k-wire-ablation/02-r1.5-probe-nocall.md) | R1.5 示范探针（39/60，同事实示范无法唤起直接回答，驳回）
- [03-exit-notool.md](evaluations/g1k-wire-ablation/03-exit-notool.md) | no-tool 出口轮（41/60，forced answer 54→8，字节 −23%，采纳）
- [04-r2-cutoff-rules.md](evaluations/g1k-wire-ablation/04-r2-cutoff-rules.md) | R2 砍训诫（40/60，首步弃权翻挂，弱锚定不可轻杀，驳回）
- [05-r3-bare.md](evaluations/g1k-wire-ablation/05-r3-bare.md) | R3 砍示例块（49/60，整块砍掉 Examples，消除负迁移，最大杠杆采纳）
- [06-r4-one-stage.md](evaluations/g1k-wire-ablation/06-r4-one-stage.md) | R4 两阶段合一（49/60，去 `<answer>` 包络，请求字节 −56%，采纳）

### [Harness 偏好重建三部曲 (2026-08-31)](evaluations/preference-rebuild-20260831/README.md)
配套仓库根目录 [`PREFERENCES.md`](../PREFERENCES.md)：
- [第一轮：偏好重建报告](evaluations/preference-rebuild-20260831/harness-preference-rebuild-report-20260831.md) | P1–P5 探针结论、16 条工程规则
- [第二轮：量尺重建与重判](evaluations/preference-rebuild-20260831/harness-round2-report-20260831.md) | 题集校准、发现 4.5k–5k 长提取工作流悬崖
- [第三轮：真实计数、压缩修复与检索纪律](evaluations/preference-rebuild-20260831/harness-round3-report-20260831.md) | 真词表计数器、Query-Aware 压缩修复

### [BFCL v4 评测攻坚分支收口历史 (2026-08-18 ~ 2026-08-26)](evaluations/historical-bfcl-v4/README.md)
- [bfcl-v4-eval-branch-closure-20260826.md](evaluations/historical-bfcl-v4/bfcl-v4-eval-branch-closure-20260826.md) | 分支收口入口、E8/E9、勘误、哈希与迁移边界
- [bfcl-v4-ab-main-integration-20260826.md](evaluations/historical-bfcl-v4/bfcl-v4-ab-main-integration-20260826.md) | BFCL v4 A+B 完整功能迁移 main
- [bfcl-v4-run-log.md](evaluations/historical-bfcl-v4/bfcl-v4-run-log.md) | BFCL v4 主跑分日志与评分总表
- [bfcl-v4-anchor-position-20260820.md](evaluations/historical-bfcl-v4/bfcl-v4-anchor-position-20260820.md) | 锚点优化：strict 51.10% → 88.90%
- [bfcl-v4-determinism-concurrency-20260820.md](evaluations/historical-bfcl-v4/bfcl-v4-determinism-concurrency-20260820.md) | 确定性归因分析
- [rwkv-g1i-toolcall-abstention-defect-20260820.md](evaluations/historical-bfcl-v4/rwkv-g1i-toolcall-abstention-defect-20260820.md) | 历史弃权诊断（结论已被后续复测修正）
- [bfcl-v4-multi-turn-e4-e7-20260821.md](evaluations/historical-bfcl-v4/bfcl-v4-multi-turn-e4-e7-20260821.md) | 多轮 E4–E7 验证报告
- [bfcl-v4-e8-qwen-enhanced-base-20260822.md](evaluations/historical-bfcl-v4/bfcl-v4-e8-qwen-enhanced-base-20260822.md) | Qwen Enhanced 对照归档
- *(其他过程文件包含 `ab-m0`、`m2.5-wire-compat`、`m3-sampling`、`qwen-markdown`、`qwen-native`、`multi-turn-state`)*

### [G1I 13B / P0 早期评测基线 (2026-08-03 ~ 2026-08-06)](evaluations/historical-g1i-13b/README.md)
- [api-13b-v9-evaluation-report-20260806.md](evaluations/historical-g1i-13b/api-13b-v9-evaluation-report-20260806.md) | 13.3B v9 修复复测（10/18 严格任务，撤除 `structured_query` 关键发现）
- [api-13b-v8-evaluation-report-20260805.md](evaluations/historical-g1i-13b/api-13b-v8-evaluation-report-20260805.md) | 13.3B v8 profile 评测
- [api-13b-evaluation-report-20260803.md](evaluations/historical-g1i-13b/api-13b-evaluation-report-20260803.md) | 13B 早期 Harness 问题报告
- [local-assistant-p0-effect-report-20260804.md](evaluations/historical-g1i-13b/local-assistant-p0-effect-report-20260804.md) | 本地优先助手 P0 落地效果报告

## 独立长报告

| 文档 | 说明 |
| --- | --- |
| [reports/harness-layer-optimization-report.html](reports/harness-layer-optimization-report.html) | Harness 层优化实录 · 抄作业版（中文 HTML，17 招实战经验） |
| [reports/harness-layer-optimization-report-en.html](reports/harness-layer-optimization-report-en.html) | Harness Layer Optimization Report（English HTML） |

## 历史归档方案

> 本目录下材料只归档、不再维护；其中过时的协议描述不应作为当前行为依据。

| 文档 | 历史主题 |
| --- | --- |
| [archive/agent-harness-milestone.md](archive/agent-harness-milestone.md) | 早期 XML Harness 里程碑与路线（历史设计，从 docs/ 迁入） |
| [archive/bfcl-ab-spec-v3.1.md](archive/bfcl-ab-spec-v3.1.md) | BFCL v4 A+B 接入实施规格（历史设计） |
| [archive/rwkv-mobile-adoption-and-cli-milestone.md](archive/rwkv-mobile-adoption-and-cli-milestone.md) | RWKV Mobile 采用与 CLI 里程碑 |
| [archive/rwkv-mobile-macos-cli-implementation-plan.md](archive/rwkv-mobile-macos-cli-implementation-plan.md) | RWKV Mobile macOS CLI 实施计划 |
| [archive/rwkv-cli-tui-redesign-plan.md](archive/rwkv-cli-tui-redesign-plan.md) | CLI TUI 重设计计划 |
| [archive/macos-cli-implementation-validation.md](archive/macos-cli-implementation-validation.md) | macOS CLI 实现验证记录 |
| [archive/local-assistant-agent-plan.md](archive/local-assistant-agent-plan.md) | 本地助手 Agent 实施计划 |
| [archive/rwkv-g1i-13b-agent-data-feedback.md](archive/rwkv-g1i-13b-agent-data-feedback.md) | G1 13B Agent 数据反馈记录 |

## 约定

- `docs/evaluations/` 存放实测数据、Benchmark 规范与消融报告；各专题以独立子目录归档。
- `docs/reports/` 存放长报告（HTML/PDF 等）。
- `docs/archive/` 只归档、不再维护；其中过时的协议描述不应作为当前行为依据。
- 目录重组或改名时，同步更新本索引与根目录 `INDEX.md`、`README.md`。
