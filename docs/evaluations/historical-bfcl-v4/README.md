# BFCL v4 评测攻坚与分支收口历史 (2026-08-18 ~ 2026-08-26)

> 本目录收录 2026 年 8 月中下旬围绕 BFCL v4 A+B 组及多轮评测开展的专项攻坚报告、对照基线与跑分日志。
> **该评测分支已于 2026-08-26 正式收口闭环并迁移至 main**，本目录下材料作为历史可信证据保留，不再进行增量更新。

---

## 核心入口与资产

- **分支收口总入口**：[`bfcl-v4-eval-branch-closure-20260826.md`](bfcl-v4-eval-branch-closure-20260826.md)（统一解释 E8/E9、lab 勘误、归档哈希与评分边界）
- **main 集成验证**：[`bfcl-v4-ab-main-integration-20260826.md`](bfcl-v4-ab-main-integration-20260826.md)（Runner、Sidecar、CLI 与样本迁移验证）
- **正式跑分日志总表**：[`bfcl-v4-run-log.md`](bfcl-v4-run-log.md)（官方判分器全量记录总表）
- **提取出的现行产品题库**：[`../bfcl-v4-product-suite-20260826.md`](../bfcl-v4-product-suite-20260826.md)（60 题产品语义评测集）

---

## 报告清单

| 类别 | 文档 | 说明 |
| --- | --- | --- |
| **收口与集成** | [bfcl-v4-eval-branch-closure-20260826.md](bfcl-v4-eval-branch-closure-20260826.md) | 分支收口入口、E8/E9 勘误、哈希与迁移边界 |
| | [bfcl-v4-ab-main-integration-20260826.md](bfcl-v4-ab-main-integration-20260826.md) | 完整功能迁移 main 验证与证据边界 |
| | [bfcl-v4-run-log.md](bfcl-v4-run-log.md) | 正式评分总表与长期运行日志 |
| **方法与优化** | [bfcl-v4-anchor-position-20260820.md](bfcl-v4-anchor-position-20260820.md) | 锚点延长到 `{"name":"`：strict 从 51.10% 提升至 88.90% |
| | [bfcl-v4-determinism-concurrency-20260820.md](bfcl-v4-determinism-concurrency-20260820.md) | 确定性归因：并发不是原因，thinking 拉长解码是主因 |
| | [bfcl-v4-m2.5-wire-compat-20260818.md](bfcl-v4-m2.5-wire-compat-20260818.md) | M2.5 兼容重解析校准（strict 28.75% vs compat 91.25%） |
| | [bfcl-v4-m3-sampling-20260819.md](bfcl-v4-m3-sampling-20260819.md) | M3 抽样冻结、代表性诊断与 manifest v2 |
| | [bfcl-v4-ab-m0.md](bfcl-v4-ab-m0.md) | M0 数据、evaluator 与判分入口预热 |
| **多轮验证** | [bfcl-v4-multi-turn-e4-e7-20260821.md](bfcl-v4-multi-turn-e4-e7-20260821.md) | 多轮 E4–E7：上游核对、800 题上下文普查、sidecar 门禁 |
| | [bfcl-v4-multi-turn-state.md](bfcl-v4-multi-turn-state.md) | 多轮实验状态与 E8 准入记录 |
| **Qwen 对照** | [bfcl-v4-qwen-markdown-baseline-full-20260819.md](bfcl-v4-qwen-markdown-baseline-full-20260819.md) | Qwen Markdown 全量 3641 题诊断 |
| | [bfcl-v4-qwen-native-fc-alignment-20260819.md](bfcl-v4-qwen-native-fc-alignment-20260819.md) | 原生 FC 全量与公开榜单逐 split 对齐 |
| | [bfcl-v4-e8-qwen-enhanced-base-20260822.md](bfcl-v4-e8-qwen-enhanced-base-20260822.md) | E8 Qwen enhanced `multi_turn_base` 57/200 冻结 |
| **缺陷诊断** | [rwkv-g1i-toolcall-abstention-defect-20260820.md](rwkv-g1i-toolcall-abstention-defect-20260820.md) | 历史弃权诊断（核心命题已被 7.2b 复测修正，见收口报告） |
