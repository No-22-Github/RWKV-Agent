# RWKV-Agent 评测体系与实测证据库 (Evaluations)

> 本目录收录 RWKV-Agent 的实测数据、Benchmark 规范、消融实验报告与历史归档证据。

---

## 现行基准与测试集 (Active Baselines & Suites)

| 文档 | 类别 | 说明 |
| --- | --- | --- |
| [bfcl-v4-product-suite-20260826.md](bfcl-v4-product-suite-20260826.md) | **现行评测题库** | 60 题产品语义迁移测试集（bfcl-product），覆盖无工具直答、参数必填与多轮状态；G1K 消融主测试集 |
| [primitive-bench-v12-baseline-2026-08-13.md](primitive-bench-v12-baseline-2026-08-13.md) | **持续演进基准** | Primitive Bench v12 基线，以及 v13–v21 持续追加的演进记录、负向实验与钩子政策 |

---

## 专题评测与历史归档 (Specialized Topics & Historical Archives)

### 1. [G1K Wire 格式消融实验专题 (2026-09-15)](g1k-wire-ablation/README.md)
最新 G1K 模型上的完整格式消融专题，从 R0 干净基线到 R4 两阶段合一，将 60 题通过率从 40 提高到 49，请求字节削减 56%：
- **总纲**：[wire-ablation-g1k-summary-20260915.md](g1k-wire-ablation/wire-ablation-g1k-summary-20260915.md)（全轮对比、三条教训、跨套件分数卡与语料靶子）
- **分轮报告**：包含 `00-r0-baseline`、`01-r1-align`、`02-r1.5-probe-nocall`、`03-exit-notool`、`04-r2-cutoff-rules`、`05-r3-bare`、`06-r4-one-stage` 逐轮严密因果记录。

### 2. [Harness 偏好重建三部曲 (2026-08-31)](preference-rebuild-20260831/README.md)
配套仓库根目录 [`PREFERENCES.md`](../../PREFERENCES.md)，记录围绕 `rwkv7-g1i-7.2b` 输出偏好重建 Harness 的全过程：
- [第一轮：偏好测绘报告](preference-rebuild-20260831/harness-preference-rebuild-report-20260831.md)（P1–P5 探针、16 条工程规则）
- [第二轮：量尺重建与重判](preference-rebuild-20260831/harness-round2-report-20260831.md)（题集校准、4.5k–5k 长提取悬崖）
- [第三轮：真实计数、压缩修复与检索纪律](preference-rebuild-20260831/harness-round3-report-20260831.md)（真词表计数、Query-Aware 压缩）

### 3. [BFCL v4 评测攻坚分支收口历史 (2026-08-18 ~ 2026-08-26)](historical-bfcl-v4/README.md)
BFCL v4 攻坚专项的 14 份历史记录，分支于 2026-08-26 收口闭环并迁移至 main：
- [分支收口入口与哈希归档](historical-bfcl-v4/bfcl-v4-eval-branch-closure-20260826.md)
- [main 分支集成验证](historical-bfcl-v4/bfcl-v4-ab-main-integration-20260826.md)
- [BFCL v4 正式跑分日志总表](historical-bfcl-v4/bfcl-v4-run-log.md)
- *(其他包含预填锚点优化、并发与解码确定性归因、多轮状态及 Qwen 对照实验报告)*

### 4. [G1I 13B / P0 早期评测基线 (2026-08-03 ~ 2026-08-06)](historical-g1i-13b/README.md)
早期 13B 模型在只读 Agent 与本地助手上的评测历史，包含 4 篇报告与关键的“撤除 `structured_query` 负收益工具”发现。
长篇展示报告见 [`docs/reports/harness-layer-optimization-report.html`](../reports/harness-layer-optimization-report.html)。
