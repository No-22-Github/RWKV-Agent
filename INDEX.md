# RWKV-Agent 项目索引

> 本文档是仓库级导航入口，用于定位当前设计、有效文档、评测结论和可复现证据。
> 使用与构建说明从 [`README.md`](README.md) 开始；英文入口见
> [`README.en.md`](README.en.md)。`docs/` 内部的逐文件索引见
> [`docs/README.md`](docs/README.md)。
>
> 最后更新：2026-08-26

## 快速定位

| 想找什么 | 推荐入口 | 说明 |
| --- | --- | --- |
| 安装、构建和基本使用 | [`README.md`](README.md) | 项目主入口、CLI、Provider、Agent 和测试说明 |
| macOS 从零运行 | [`docs/getting-started-macos.md`](docs/getting-started-macos.md) | 环境、模型准备、构建、运行、更新和常见问题 |
| 桌面 App 与公开 API | [`docs/app.md`](docs/app.md) | Wails App、headless server、存储和开发说明 |
| 当前续写与 Agent 协议 | [`docs/continuation-and-agent-protocol.md`](docs/continuation-and-agent-protocol.md) | 内建续写协议、渐进式工具和远程 Provider 边界 |
| 推理核心和 State 设计 | [`docs/inference-core-design.md`](docs/inference-core-design.md) | 分层、生命周期、State、调度和契约测试 |
| 当前已提交的 13B 边界基线 | [`archive/v10-baseline/README.md`](archive/v10-baseline/README.md) | v10 RWKV 13B 为 13/18；同版本内比较，附原始证据 |
| Primitive Bench 演进 | [`docs/evaluations/primitive-bench-v12-baseline-2026-08-13.md`](docs/evaluations/primitive-bench-v12-baseline-2026-08-13.md) | v12 基线以及 v13–v21 的实验、复跑和政策记录 |
| BFCL 当前进度 | [`docs/evaluations/bfcl-v4-run-log.md`](docs/evaluations/bfcl-v4-run-log.md) | 固定环境、正式评分总表、可比性分组和辅助运行 |
| Harness 优化总结 | [`docs/reports/harness-layer-optimization-report.html`](docs/reports/harness-layer-optimization-report.html) | 中文长报告；另有英文版 |

## 如何理解评测材料

项目中的评测材料分为四层，查找“现在表现如何”时不要混用：

1. **结论文档**：`docs/evaluations/` 中的报告和持续维护的跑分日志，优先用于理解结果、限制和下一步。
2. **已提交证据**：`archive/` 中冻结的 `run.json`、`summary.json` 和 `trace.jsonl`，用于复核特定基线。
3. **本地原始运行**：`runs/` 中的可再生成产物。该目录被 Git 忽略，其他 checkout 或 GitHub 页面不保证存在。
4. **历史材料**：`docs/archive/` 中已经停止维护的计划和验证记录，只用于回顾背景，不代表当前默认行为。

“日期更新”不自动等于“结论更权威”。环境异常、只做离线重解析、Harness 版本变化或评分规则变化，都会导致结果不可直接比较；应以对应报告的可比性说明为准。

## 设计、协议与实现

| 文档 | 状态与用途 |
| --- | --- |
| [`docs/inference-core-design.md`](docs/inference-core-design.md) | 当前推理核心设计：backend、State、调度、并发与契约 |
| [`docs/direct-pth-loading.md`](docs/direct-pth-loading.md) | 当前 `.pth` 直载链路：mmap、索引缓存和转换路径 |
| [`docs/continuation-and-agent-protocol.md`](docs/continuation-and-agent-protocol.md) | 当前续写接口和 Agent 协议边界 |
| [`docs/agent-harness-milestone.md`](docs/agent-harness-milestone.md) | 早期只读 XML Harness 里程碑；历史参考，不是当前默认协议 |

## 上手与产品文档

| 文档 | 用途 |
| --- | --- |
| [`README.md`](README.md) | 中文主文档 |
| [`README.en.md`](README.en.md) | English README |
| [`docs/getting-started-macos.md`](docs/getting-started-macos.md) | macOS 完整上手指南 |
| [`docs/app.md`](docs/app.md) | 桌面 App、浏览器模式与公开 API |
| [`docs/README.md`](docs/README.md) | `docs/` 目录的逐文件索引 |

## 评测与基线

### Agent 边界与 Harness

| 文档或证据 | 结论定位 |
| --- | --- |
| [`archive/v10-baseline/README.md`](archive/v10-baseline/README.md) | 当前已提交的 v10 基线入口；RWKV 13B 13/18，DeepSeek v4 Flash 17/18；v8/v9/v10 不跨版本比较 |
| [`archive/v10-baseline/`](archive/v10-baseline/) | 六组冻结证据，每组包含运行配置、逐条 trace 和汇总 |
| [`docs/evaluations/api-13b-v9-evaluation-report-20260806.md`](docs/evaluations/api-13b-v9-evaluation-report-20260806.md) | v9 三项 Harness 修复后的完整复测报告 |
| [`docs/evaluations/api-13b-v8-evaluation-report-20260805.md`](docs/evaluations/api-13b-v8-evaluation-report-20260805.md) | v8 profile 的 13.3B Harness 评测 |
| [`docs/evaluations/api-13b-evaluation-report-20260803.md`](docs/evaluations/api-13b-evaluation-report-20260803.md) | 早期 13B Harness 问题报告 |
| [`docs/evaluations/local-assistant-p0-effect-report-20260804.md`](docs/evaluations/local-assistant-p0-effect-report-20260804.md) | 本地优先助手 P0 落地效果 |

本地原始运行通常位于 `runs/agent-eval-*`、`runs/api-13b-*`、`runs/deepseek-*` 和 `runs/cmp-*`。优先阅读报告或归档 README，再按其中记录的运行目录查看原始证据。

### Primitive Bench

| 文档或证据 | 结论定位 |
| --- | --- |
| [`docs/evaluations/primitive-bench-v12-baseline-2026-08-13.md`](docs/evaluations/primitive-bench-v12-baseline-2026-08-13.md) | 主记录：v12 基线、v13–v21 演进、负向实验、失败分析和钩子政策 |
| [`internal/agent/eval/testdata/primitive_orig30/UPSTREAM.md`](internal/agent/eval/testdata/primitive_orig30/UPSTREAM.md) | 原始 30 题快照的来源说明 |
| [`internal/agent/eval/testdata/primitive_feedback30/UPSTREAM.md`](internal/agent/eval/testdata/primitive_feedback30/UPSTREAM.md) | 反馈集 30 题快照的来源说明 |

本地运行以 `runs/primitive-*` 和 `runs/api125-*` 为主。文件名中的版本号表示 Harness/实验阶段，不应脱离主记录单独解释为稳定回归结论。

### BFCL v4

| 文档或证据 | 结论定位 |
| --- | --- |
| [`docs/evaluations/bfcl-v4-eval-branch-closure-20260826.md`](docs/evaluations/bfcl-v4-eval-branch-closure-20260826.md) | BFCL 分支收口入口：统一 E8/E9 与 7.2b lab 勘误，冻结源码/归档哈希，并记录 focused commit 的 main 可移植性 |
| [`docs/evaluations/bfcl-v4-run-log.md`](docs/evaluations/bfcl-v4-run-log.md) | BFCL 的主跑分日志和正式评分总表；新增运行统一追加到这里 |
| [`docs/evaluations/bfcl-v4-ab-m0.md`](docs/evaluations/bfcl-v4-ab-m0.md) | M0 数据、evaluator 和本地判分入口预热 |
| [`docs/evaluations/bfcl-v4-m2.5-wire-compat-20260818.md`](docs/evaluations/bfcl-v4-m2.5-wire-compat-20260818.md) | 同一批 400 条输出的离线兼容重解析：strict 28.75%，compat 91.25%；不是新模型跑分，二者不能互相替代 |
| [`docs/evaluations/bfcl-v4-determinism-concurrency-20260820.md`](docs/evaluations/bfcl-v4-determinism-concurrency-20260820.md) | 确定性归因：并发不是原因（c16 对 c48 p=1.000），thinking 拉长解码是主因，批处理有无是次因；含对 08-19 两处表述的修正 |
| [`docs/evaluations/rwkv-g1i-toolcall-abstention-defect-20260820.md`](docs/evaluations/rwkv-g1i-toolcall-abstention-defect-20260820.md) | 历史诊断，核心“预填后必然无法弃权”已被 2026-08-25 的 7.2b 复测修正；13.3b 未复测，现行解释以分支收口说明为准 |
| [`docs/evaluations/bfcl-v4-anchor-position-20260820.md`](docs/evaluations/bfcl-v4-anchor-position-20260820.md) | 小优化：锚点延长到 `{"name":"`（并行用 `[{"name":"`），non-live 1000 题 strict 51.10% → 88.90%，超过带兜底的 88.00% |
| [`docs/evaluations/bfcl-v4-multi-turn-e4-e7-20260821.md`](docs/evaluations/bfcl-v4-multi-turn-e4-e7-20260821.md) | Multi-turn E4–E7：上游判分语义、800 题上下文可行集、sidecar GT 100% 门禁与双模型单题闭环 |
| [`docs/evaluations/bfcl-v4-e8-qwen-enhanced-base-20260822.md`](docs/evaluations/bfcl-v4-e8-qwen-enhanced-base-20260822.md) | E8 Qwen enhanced `multi_turn_base`：57/200，含 baseline 对照、失败迁移、干预事件与冻结归档 |
| [`docs/evaluations/bfcl-v4-run-log.md`](docs/evaluations/bfcl-v4-run-log.md)（E9 条目）| E9 原生 FC 多轮诊断：Qwen no-think 47/200 = 23.5%；thinking 主结果 18/60 = 30.0%，18/51 仅为条件指标；reasoning history 修复并同池重跑前不量化增益 |
| [`archive/bfcl-v4-e8-qwen-enhanced-base-20260822/README.md`](archive/bfcl-v4-e8-qwen-enhanced-base-20260822/README.md) | E8 Qwen enhanced 的 200 条合并结果、机器可读汇总、官方分数摘要与哈希 |
| [`docs/evaluations/bfcl-v4-qwen-native-fc-alignment-20260819.md`](docs/evaluations/bfcl-v4-qwen-native-fc-alignment-20260819.md) | Qwen3-8B 原生 FC 全量与公开榜单逐 split 对齐；用作管道体检，不是本项目成绩 |
| [`docs/evaluations/bfcl-v4-qwen-markdown-baseline-full-20260819.md`](docs/evaluations/bfcl-v4-qwen-markdown-baseline-full-20260819.md) | Markdown baseline 全量诊断；负样本分受 prompt 预填影响，不代表模型拒调能力 |
| [`docs/evaluations/bfcl-v4-m3-sampling-20260819.md`](docs/evaluations/bfcl-v4-m3-sampling-20260819.md) | M3 抽样冻结与代表性诊断，manifest v1 → v2 |
| [`docs/archive/bfcl-ab-spec-v3.1.md`](docs/archive/bfcl-ab-spec-v3.1.md) | 已归档的 A+B 接入实施规格，用于追溯评测设计 |

本地 BFCL 证据位于 `runs/bfcl/`，包括 result、score、trace、验收记录和适配器健康检查。该目录不提交；可对外引用的结论必须先写入 `docs/evaluations/`。

## 长报告

| 文档 | 说明 |
| --- | --- |
| [`docs/reports/harness-layer-optimization-report.html`](docs/reports/harness-layer-optimization-report.html) | Harness 层优化实录，中文版 |
| [`docs/reports/harness-layer-optimization-report-en.html`](docs/reports/harness-layer-optimization-report-en.html) | Harness Optimization Report, English version |

## 历史归档文档

以下文档不再维护。它们适合了解决策过程，但实现、命令和协议可能已经变化。

| 文档 | 历史主题 |
| --- | --- |
| [`docs/archive/bfcl-ab-spec-v3.1.md`](docs/archive/bfcl-ab-spec-v3.1.md) | BFCL v4 A+B 接入实施规格 |
| [`docs/archive/rwkv-mobile-adoption-and-cli-milestone.md`](docs/archive/rwkv-mobile-adoption-and-cli-milestone.md) | RWKV Mobile 采用与 CLI 里程碑 |
| [`docs/archive/rwkv-mobile-macos-cli-implementation-plan.md`](docs/archive/rwkv-mobile-macos-cli-implementation-plan.md) | RWKV Mobile macOS CLI 实施计划 |
| [`docs/archive/rwkv-cli-tui-redesign-plan.md`](docs/archive/rwkv-cli-tui-redesign-plan.md) | CLI TUI 重设计计划 |
| [`docs/archive/macos-cli-implementation-validation.md`](docs/archive/macos-cli-implementation-validation.md) | macOS CLI 实现验证记录 |
| [`docs/archive/local-assistant-agent-plan.md`](docs/archive/local-assistant-agent-plan.md) | 本地助手 Agent 实施计划 |
| [`docs/archive/rwkv-g1i-13b-agent-data-feedback.md`](docs/archive/rwkv-g1i-13b-agent-data-feedback.md) | 早期 G1I 13B Agent 数据反馈 |

## 运行产物约定

一次标准评测运行通常包含：

| 文件 | 内容 |
| --- | --- |
| `run.json` | 模型、case、prompt、采样参数和运行配置 |
| `summary.json` | 汇总指标、逐 case 结果和失败分类 |
| `trace.jsonl` | 每次请求、模型输出、工具结果和使用量 |

需要长期保存的基线，不应只留在 `runs/`。应把最小且完整的证据复制到 `archive/<baseline-name>/`，同时新增 README，记录模型、日期、Harness/数据版本、有效与无效运行、结果和可比性边界。

## 维护规则

新增或调整材料时按以下规则维护：

1. 新增正式文档、长报告、已提交基线或主评测线时，同步更新本文档。
2. `docs/README.md` 必须覆盖 `docs/` 下的全部文档；本文档只保留有用途说明的仓库级入口。
3. 当前设计放在 `docs/`，正式评测结论放在 `docs/evaluations/`，长 HTML/PDF 报告放在 `docs/reports/`，停止维护的材料移入 `docs/archive/`。
4. `runs/` 仅保存本地可再生成证据；不要把只存在于 `runs/` 的路径当作公共永久链接。
5. 提升新基线时，明确标注日期、模型、Harness 或 parser 版本、数据集、结果、证据路径和不可比较项。
6. 不覆盖历史结果。修复 parser、评分器或环境后，用新条目记录变化，并保留 strict/原始基线。
7. 文档或目录改名时，同步检查本文档、两个根 README 和 `docs/README.md` 中的链接。
