# RWKV-Agent 文档索引

> 根目录 [`README.md`](../README.md) 是使用入口，[`INDEX.md`](../INDEX.md) 是项目总索引。
> 这里按用途列出 `docs/` 下的全部文档。
>
> [English README](../README.en.md)

## 上手指南

| 文档 | 说明 |
| --- | --- |
| [getting-started-macos.md](guides/getting-started-macos.md) | macOS 从零上手：环境、构建、模型准备、运行、更新与常见问题 |
| [cli.md](guides/cli.md) | `rwkv-cli` 参考手册：各子命令参数、Session、Agent、远程 Provider、评测与并发 dashboard（原 README 第 3–10 节） |
| [app.md](guides/app.md) | Wails V3 桌面 App 与 headless server：构建、公开 API、持久化存储、配置与开发 |

## 工具调用与对话格式 (Wire & Protocols)

| 文档 | 说明 |
| --- | --- |
| [tool-and-wire-formats.md](design/tool-and-wire-formats.md) | **★ 工具格式与对话协议门户 ★**：RWKV 续写到 Agent 动作的分层、G1K 现行推荐、全景对比矩阵与演进历程 |
| [corpus-g1k-wire-format.md](design/corpus-g1k-wire-format.md) | **数据侧逐字节契约**：G1K 对齐语料生产/清洗标准（System、`<tools>`、User `<tool_response>`、纯文本终答） |
| [wire-configuration.md](guides/wire-configuration.md) | **运行时配置指南**：Spec 参数全表、Profile 预设、CLI/API 统一入口（受单测锁守护） |
| [continuation-and-agent-protocol.md](design/continuation-and-agent-protocol.md) | **架构与协议实现**：ActionProtocol、PromptRenderer 与 Provider 续写分层设计 |

## 设计与底层架构

| 文档 | 说明 |
| --- | --- |
| [inference-core-design.md](design/inference-core-design.md) | 跨平台推理核心设计：分层、对象生命周期、State 模型、调度与契约测试 |
| [direct-pth-loading.md](design/direct-pth-loading.md) | 直接加载 `.pth`：mmap、索引缓存、转换链路 |
| [go-tooling-migration.md](design/go-tooling-migration.md) | Python 实验工具迁移到 Go（`bin/rwkv-lab`）的对照表与验收记录 |
| [preferences.md](design/preferences.md) | RWKV7-G1i 输出偏好与 Harness 工程规则总纲（原根目录 `PREFERENCES.md`） |

## 蒸馏语料与 State 训练（现行）

| 文档 | 说明 |
| --- | --- |
| [distill/distill-workflow.md](distill/distill-workflow.md) | **蒸馏工作流规格**：出题 → 老师在真实 harness 里跑 → 抽路径 → `corpus render` 重放切行 → 打包；各环节闸门与命令 |
| [distill/distill-allocation-v1.md](distill/distill-allocation-v1.md) | 加题分配 v1：b01–b03 的题型配额与行长约束（取代 workflow §2.4） |
| [distill/distill-allocation-v1.3.md](distill/distill-allocation-v1.3.md) | v1.3 数据构成规划：存量修复、N1–N11 新增（中文/多轮/失败汇报/自然语言交付/收尾恢复/tabular）、「查不到怎么答」规范、工具目录轮换、目标指标、验收与分批 |
| [distill/distill-b04-glm.md](distill/distill-b04-glm.md) | b04 执行规格：子 Agent 用 `bench/distill/tools/step.py` 扮演 student，在真实 harness 里逐步解题（老师无法接入 harness 时的方案） |
| [distill/fix-20260929-glm.md](distill/fix-20260929-glm.md) | 2026-09-29 修数派单：`run compare --exclude-cases` 剔除 base700 的 36 道种子题、t927 泄漏口径更正、`bank verify` 形状识别与 `--strict-shape`、nt-5278 改题、25 道 ambiguous_request 重解 |
| [distill/harness-corpus-render.md](distill/harness-corpus-render.md) | 训练行只能由 harness 重放生成：`--script` 回放、多轮按轮切行、分集规则 |
| [distill/reports/](distill/reports/) | 各批次报告：smoke、b01–b04 |
| [evaluations/distill-audit-20260926/REPORT.md](evaluations/distill-audit-20260926/REPORT.md) | 蒸馏数据审阅：判据 fail-open、stable_fact 实为本地检索、`tools: []` 名不副实；配套清洗说明 CLEANING.md |

## workbank 手写题库（148 题，现行主测试集之一）

题目、账本与工具在 [`../bench/workbank/`](../bench/workbank/)；这里是出题规则和历次报告。

| 文档 | 说明 |
| --- | --- |
| [workbank/authoring-guide.md](workbank/authoring-guide.md) | **出题手册（最高权威）**：原则、陷阱、难度、反例库 |
| [workbank/drafting-brief.md](workbank/drafting-brief.md) | 起草简报：每个起草 Agent 必读的硬规则 |
| [workbank/HANDOFF.md](workbank/HANDOFF.md) | 题库建置交接文档：文件契约、工具目录、离线判分 |
| [workbank/expansion-152-handoff.md](workbank/expansion-152-handoff.md) | 40 → 152 扩量实施规格 |
| [workbank/M0-findings.md](workbank/M0-findings.md) | M0 核实结论：工具真实行为 |
| [workbank/defect-archive.md](workbank/defect-archive.md) | 模型缺陷档案（失败模式词表） |
| [workbank/solve-check-20260917.md](workbank/solve-check-20260917.md) | 试点求解检查归档 |
| [workbank/changelog.md](workbank/changelog.md) | 题库变更记录 |
| [workbank/reports/](workbank/reports/) | 30 份报告：closeout、失败诊断、判分审计、state A/B、扩量批次、剂量-反应等；机器可读数据在 `bench/workbank/reports-data/` |

## 现行评测基准

| 文档 | 说明 |
| --- | --- |
| [evaluations/g1k-wire-ablation/wire-ablation-g1k-summary-20260915.md](evaluations/g1k-wire-ablation/wire-ablation-g1k-summary-20260915.md) | **G1K 现行消融旗舰**：Wire 格式 R0–R4 消融总结（40→49 题，请求字节 −56%） |
| [evaluations/bfcl-v4-product-suite-20260826.md](evaluations/bfcl-v4-product-suite-20260826.md) | **现行评测题库**：60 题 BFCL 产品语义迁移 suite 规格与运行边界 |
| [evaluations/benchmark-protocol.md](evaluations/benchmark-protocol.md) | **跑分规程**：g1k 格式、统一预算、采样预设、`run check` 闸门（配套 `.claude/skills/rwkv-bench`） |
| [evaluations/state-v12-20260929/HANDOFF.md](evaluations/state-v12-20260929/HANDOFF.md) | **进行中**：v1.2 state 横测执行规格（交 VPS Agent）——14 个 arm、Cloudflare 单队列 64 并发、workbank 以干净 112 题为主口径、`check_v12.py` 有效性闸门；计划见同目录 PLAN.md |
| [evaluations/state-t927-20260927/REPORT.md](evaluations/state-t927-20260927/REPORT.md) | **最新 state 横测**：t927 六个 checkpoint，s316 最优（workbank 16/148 vs 基线 9）；终答不停、答案契约被拒深挖（148 题口径含泄漏，已于 2026-09-29 在 §8 更正） |
| [evaluations/state-lr-sweep-20260923/REPORT.md](evaluations/state-lr-sweep-20260923/REPORT.md) | state 学习率扫描复核：训练集泄漏 32/148 题、首动作 100% 调工具导致 bfcl 崩 |
| [evaluations/g1k-sampling-sweep-20260923/](evaluations/g1k-sampling-sweep-20260923/) | g1k 采样扫描：`--sampling` 预设来源，截断比温度更重要 |
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
配套仓库根目录 [`docs/design/preferences.md`](design/preferences.md)：
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
| [archive/removed-tools.md](archive/removed-tools.md) | 已删除的旧工具与其替代品 |

## 约定

- 文档只放 `docs/`：`guides/` 使用说明、`design/` 设计与契约、`distill/` 蒸馏流程与批次报告、`workbank/` 题库规则与报告、`evaluations/` 评测结论、`archive/` 停更材料。
- 数据只放 `bench/`：题目、老师脚本、账本、冻结的跑分证据和报告附带的 json，清单见 [`../bench/README.md`](../bench/README.md)。
- `docs/evaluations/` 存放实测数据、Benchmark 规范与消融报告；各专题以独立子目录归档。
- `docs/reports/` 存放长报告（HTML/PDF 等）。
- `docs/archive/` 只归档、不再维护；其中过时的协议描述不应作为当前行为依据。
- 目录重组或改名时，同步更新本索引与根目录 `INDEX.md`、`README.md`。
