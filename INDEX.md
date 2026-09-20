# RWKV-Agent 项目索引

> 本文档是仓库级导航入口，用于定位当前设计、有效文档、评测结论和可复现证据。
> 使用与构建说明从 [`README.md`](README.md) 开始；英文入口见
> [`README.en.md`](README.en.md)。`docs/` 内部的逐文件索引见
> [`docs/README.md`](docs/README.md)。
>
> 最后更新：2026-09-20

## 快速定位

| 想找什么 | 推荐入口 | 说明 |
| --- | --- | --- |
| 安装、构建和基本使用 | [`README.md`](README.md) | 项目主入口、CLI、Provider、Agent 和测试说明 |
| macOS 从零运行 | [`docs/getting-started-macos.md`](docs/getting-started-macos.md) | 环境、模型准备、构建、运行、更新和常见问题 |
| 桌面 App 与公开 API | [`docs/app.md`](docs/app.md) | Wails App、headless server、存储和开发说明 |
| **700 条精品 Agent 轨迹数据集** | [`datasets/README.md`](datasets/README.md) | 36 种子 700 条（630 train / 70 val）精品轨迹工作区与送训 text-only 归档 |
| **工具调用与对话格式总览** | [`docs/tool-and-wire-formats.md`](docs/tool-and-wire-formats.md) | **★ 统一格式门户 ★**：分层设计、G1K 推荐格式、矩阵对比与演进 |
| **G1K 对齐语料格式契约** | [`docs/corpus-g1k-wire-format.md`](docs/corpus-g1k-wire-format.md) | 数据侧逐字节契约：System、`<tools>`、User `<tool_response>`、纯文本终答 |
| **Wire 运行时配置指南** | [`docs/wire-configuration.md`](docs/wire-configuration.md) | Spec 参数全表、Profile 预设、CLI/API 统一入口（受单测锁守护） |
| **G1K Wire 消融旗舰总结** | [`docs/evaluations/g1k-wire-ablation/wire-ablation-g1k-summary-20260915.md`](docs/evaluations/g1k-wire-ablation/wire-ablation-g1k-summary-20260915.md) | R0–R4 全轮实测、定音分数卡（40→49 题，请求字节 −56%）、语料靶子 |
| **Harness 偏好重建三部曲** | [`docs/evaluations/preference-rebuild-20260831/`](docs/evaluations/preference-rebuild-20260831/) | 配套根目录 [`PREFERENCES.md`](PREFERENCES.md)，记录 P1–P5 探针、量尺重建与真词表收敛 |
| 现行 60 题产品语义评测集 | [`docs/evaluations/bfcl-v4-product-suite-20260826.md`](docs/evaluations/bfcl-v4-product-suite-20260826.md) | bfcl-product 规格与测试边界，G1K 消融主测试集 |
| 推理核心和 State 设计 | [`docs/inference-core-design.md`](docs/inference-core-design.md) | 分层、生命周期、State、调度和契约测试 |
| Primitive Bench 演进 | [`docs/evaluations/primitive-bench-v12-baseline-2026-08-13.md`](docs/evaluations/primitive-bench-v12-baseline-2026-08-13.md) | v12 基线以及 v13–v21 的实验、复跑和政策记录 |
| Harness 优化总结长报告 | [`docs/reports/harness-layer-optimization-report.html`](docs/reports/harness-layer-optimization-report.html) | 中文长报告（17 招实战经验）；另有英文版 |

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
| [`docs/tool-and-wire-formats.md`](docs/tool-and-wire-formats.md) | **★ 工具格式与对话协议门户 ★**：分层机制、推荐格式、全景矩阵与演进历程 |
| [`docs/corpus-g1k-wire-format.md`](docs/corpus-g1k-wire-format.md) | G1K 对齐语料格式契约：数据清洗/生产逐字节规范 |
| [`docs/wire-configuration.md`](docs/wire-configuration.md) | Agent Wire Spec 参数全表、Profile 预设与 CLI/API 配置指南 |
| [`docs/continuation-and-agent-protocol.md`](docs/continuation-and-agent-protocol.md) | 当前续写接口与 Agent 协议分层实现 |
| [`docs/inference-core-design.md`](docs/inference-core-design.md) | 当前推理核心设计：backend、State、调度、并发与契约 |
| [`docs/direct-pth-loading.md`](docs/direct-pth-loading.md) | 当前 `.pth` 直载链路：mmap、索引缓存和转换路径 |

## 上手与产品文档

| 文档 | 用途 |
| --- | --- |
| [`README.md`](README.md) | 中文主文档 |
| [`README.en.md`](README.en.md) | English README |
| [`docs/getting-started-macos.md`](docs/getting-started-macos.md) | macOS 完整上手指南 |
| [`docs/app.md`](docs/app.md) | 桌面 App、浏览器模式与公开 API |
| [`docs/README.md`](docs/README.md) | `docs/` 目录的逐文件多级索引 |

## 评测与基线

### 700 条 Agent 精品轨迹数据集 (2026-09-20 现行)

| 文档或证据 | 结论定位 |
| --- | --- |
| [`datasets/workspace-agent-700-20260920/README.md`](datasets/workspace-agent-700-20260920/README.md) | **700 条制作工作区入口**：36 道种子、9 大场景、700 条（630 训练 + 70 验证）全绿验收 |
| [`datasets/workspace-agent-700-20260920/verification/acceptance-report.md`](datasets/workspace-agent-700-20260920/verification/acceptance-report.md) | 单快照硬门槛验收报告（`data_ready`，回放 100% 绑定闭环，二次无污染回放 349/349 通过） |
| [`datasets/workspace-agent-700-20260920/verification/phase3-repair-report.md`](datasets/workspace-agent-700-20260920/verification/phase3-repair-report.md) | Phase 3 修复执行报告与用户授权保留政策（近重复处置与独立审查覆盖） |
| `outputs/workspace-agent-700-state-tune-textonly/` | 实际送进丹炉训练的纯 text 格式（兼容 `rwkv_state_tune`，含转换脚本与报告） |

### G1K Wire 格式消融实验 (2026-09-15 基线)

| 文档或证据 | 结论定位 |
| --- | --- |
| [`docs/evaluations/g1k-wire-ablation/wire-ablation-g1k-summary-20260915.md`](docs/evaluations/g1k-wire-ablation/wire-ablation-g1k-summary-20260915.md) | **现行消融旗舰**：全轮对比表（R0–R4）、跨套件分数卡（40→49/60）、三条核心教训与语料靶子 |
| [`docs/evaluations/g1k-wire-ablation/`](docs/evaluations/g1k-wire-ablation/) | 逐轮报告：00-r0 基线、01-r1 标签对齐、02-r1.5 示范探针、03-exit 出口轮、04-r2 砍训诫、05-r3 砍示例块、06-r4 两阶段合一 |
| [`docs/evaluations/bfcl-v4-product-suite-20260826.md`](docs/evaluations/bfcl-v4-product-suite-20260826.md) | 现行 60 题产品语义测试集（bfcl-product），消融评测基准 |

### Harness 偏好重建三部曲 (2026-08-31)

| 文档或证据 | 结论定位 |
| --- | --- |
| [`PREFERENCES.md`](PREFERENCES.md) | 模型偏好与 16 条工程落地规则总纲（合并自原三处分节，置顶执行含义） |
| [`docs/evaluations/preference-rebuild-20260831/harness-preference-rebuild-report-20260831.md`](docs/evaluations/preference-rebuild-20260831/harness-preference-rebuild-report-20260831.md) | 第一轮偏好重建报告：P1–P5 探针结论、16 条规则与改动清单 |
| [`docs/evaluations/preference-rebuild-20260831/harness-round2-report-20260831.md`](docs/evaluations/preference-rebuild-20260831/harness-round2-report-20260831.md) | 第二轮量尺重建：题集校准、首次发现 4.5k–5k 长提取工作流悬崖 |
| [`docs/evaluations/preference-rebuild-20260831/harness-round3-report-20260831.md`](docs/evaluations/preference-rebuild-20260831/harness-round3-report-20260831.md) | 第三轮真词表计数、压缩修复与检索纪律：精确重标悬崖为 4673–5021 tokens |

### Primitive Bench

| 文档或证据 | 结论定位 |
| --- | --- |
| [`docs/evaluations/primitive-bench-v12-baseline-2026-08-13.md`](docs/evaluations/primitive-bench-v12-baseline-2026-08-13.md) | 主记录：v12 基线、v13–v21 演进、负向实验、失败分析和钩子政策 |
| [`internal/agent/eval/testdata/primitive_orig30/UPSTREAM.md`](internal/agent/eval/testdata/primitive_orig30/UPSTREAM.md) | 原始 30 题快照的来源说明 |
| [`internal/agent/eval/testdata/primitive_feedback30/UPSTREAM.md`](internal/agent/eval/testdata/primitive_feedback30/UPSTREAM.md) | 反馈集 30 题快照的来源说明 |

### BFCL v4 历史评测攻坚 (2026-08-18 ~ 2026-08-26 归档)

| 文档或证据 | 结论定位 |
| --- | --- |
| [`docs/evaluations/historical-bfcl-v4/bfcl-v4-eval-branch-closure-20260826.md`](docs/evaluations/historical-bfcl-v4/bfcl-v4-eval-branch-closure-20260826.md) | BFCL 分支收口历史入口：统一 E8/E9 与 7.2b lab 勘误，记录评分边界与归档哈希 |
| [`docs/evaluations/historical-bfcl-v4/bfcl-v4-ab-main-integration-20260826.md`](docs/evaluations/historical-bfcl-v4/bfcl-v4-ab-main-integration-20260826.md) | BFCL loader、renderer/parser、单轮/多轮 runner、sidecar、CLI 与样本/归档已整体迁移到 main |
| [`docs/evaluations/historical-bfcl-v4/bfcl-v4-run-log.md`](docs/evaluations/historical-bfcl-v4/bfcl-v4-run-log.md) | BFCL 的主跑分日志和正式评分总表（分支收口后冻结） |
| [`docs/evaluations/historical-bfcl-v4/bfcl-v4-anchor-position-20260820.md`](docs/evaluations/historical-bfcl-v4/bfcl-v4-anchor-position-20260820.md) | 锚点延长到 `{"name":"`，non-live 1000 题 strict 51.10% → 88.90% |
| [`docs/evaluations/historical-bfcl-v4/bfcl-v4-determinism-concurrency-20260820.md`](docs/evaluations/historical-bfcl-v4/bfcl-v4-determinism-concurrency-20260820.md) | 确定性归因：并发不是原因，thinking 拉长解码是主因 |
| [`docs/evaluations/historical-bfcl-v4/rwkv-g1i-toolcall-abstention-defect-20260820.md`](docs/evaluations/historical-bfcl-v4/rwkv-g1i-toolcall-abstention-defect-20260820.md) | 历史诊断，核心“预填后必然无法弃权”已被 7.2b 复测修正（见收口说明） |
| [`docs/evaluations/historical-bfcl-v4/bfcl-v4-multi-turn-e4-e7-20260821.md`](docs/evaluations/historical-bfcl-v4/bfcl-v4-multi-turn-e4-e7-20260821.md) | Multi-turn E4–E7：上游判分语义、800 题上下文可行集与单题闭环 |
| [`docs/evaluations/historical-bfcl-v4/bfcl-v4-e8-qwen-enhanced-base-20260822.md`](docs/evaluations/historical-bfcl-v4/bfcl-v4-e8-qwen-enhanced-base-20260822.md) | E8 Qwen enhanced `multi_turn_base`：57/200 对照与冻结归档 |
| [`docs/evaluations/historical-bfcl-v4/`](docs/evaluations/historical-bfcl-v4/) | 完整 14 份报告，含 `ab-m0`、`m2.5-wire-compat`、`m3-sampling`、`qwen-markdown` 等过程记录 |

### G1I 13B 早期探索基线 (2026-08-03 ~ 2026-08-06 归档)

| 文档或证据 | 结论定位 |
| --- | --- |
| [`archive/v10-baseline/README.md`](archive/v10-baseline/README.md) | 早期提交的 v10 基线入口；RWKV 13B 13/18，DeepSeek v4 Flash 17/18 |
| [`docs/evaluations/historical-g1i-13b/api-13b-v9-evaluation-report-20260806.md`](docs/evaluations/historical-g1i-13b/api-13b-v9-evaluation-report-20260806.md) | v9 三项 Harness 修复报告（10/18 严格任务，撤除 `structured_query` 关键发现） |
| [`docs/evaluations/historical-g1i-13b/api-13b-v8-evaluation-report-20260805.md`](docs/evaluations/historical-g1i-13b/api-13b-v8-evaluation-report-20260805.md) | v8 profile 的 13.3B Harness 评测 |
| [`docs/evaluations/historical-g1i-13b/api-13b-evaluation-report-20260803.md`](docs/evaluations/historical-g1i-13b/api-13b-evaluation-report-20260803.md) | 早期 13B Harness 问题报告 |
| [`docs/evaluations/historical-g1i-13b/local-assistant-p0-effect-report-20260804.md`](docs/evaluations/historical-g1i-13b/local-assistant-p0-effect-report-20260804.md) | 本地优先助手 P0 落地效果报告 |

## 长报告

| 文档 | 说明 |
| --- | --- |
| [`docs/reports/harness-layer-optimization-report.html`](docs/reports/harness-layer-optimization-report.html) | Harness 层优化实录 · 抄作业版，中文版 |
| [`docs/reports/harness-layer-optimization-report-en.html`](docs/reports/harness-layer-optimization-report-en.html) | Harness Layer Optimization Report, English version |

## 历史归档文档

以下文档不再维护。它们适合了解决策过程，但实现、命令和协议可能已经变化。

| 文档 | 历史主题 |
| --- | --- |
| [`docs/archive/agent-harness-milestone.md`](docs/archive/agent-harness-milestone.md) | 早期只读 XML Harness 里程碑（历史参考，从 docs/ 迁入） |
| [`docs/archive/bfcl-ab-spec-v3.1.md`](docs/archive/bfcl-ab-spec-v3.1.md) | BFCL v4 A+B 接入实施规格（历史设计） |
| [`docs/archive/rwkv-mobile-adoption-and-cli-milestone.md`](docs/archive/rwkv-mobile-adoption-and-cli-milestone.md) | RWKV Mobile 采用与 CLI 里程碑 |
| [`docs/archive/rwkv-mobile-macos-cli-implementation-plan.md`](docs/archive/rwkv-mobile-macos-cli-implementation-plan.md) | RWKV Mobile macOS CLI 实施计划 |
| [`docs/archive/rwkv-cli-tui-redesign-plan.md`](docs/archive/rwkv-cli-tui-redesign-plan.md) | CLI TUI 重设计计划 |
| [`docs/archive/macos-cli-implementation-validation.md`](docs/archive/macos-cli-implementation-validation.md) | macOS CLI 实现验证记录 |
| [`docs/archive/local-assistant-agent-plan.md`](docs/archive/local-assistant-agent-plan.md) | 本地助手 Agent 实施计划 |
| [`docs/archive/rwkv-g1i-13b-agent-data-feedback.md`](docs/archive/rwkv-g1i-13b-agent-data-feedback.md) | 早期 G1 13B Agent 数据反馈 |

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
