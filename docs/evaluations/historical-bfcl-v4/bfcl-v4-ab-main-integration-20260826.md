# BFCL v4 A+B 主线迁移

日期：2026-08-26（Asia/Shanghai）

## 结论

`feat/bfcl-v4-ab` 已完成评测阶段。本次把分支中已经完成的 BFCL loader、renderer/parser、单轮与多轮 runner、sidecar、采样/重解析工具、CLI 入口、样本 manifest 和评测归档整体迁移到 `main`，同时保留主线已有的产品 Harness suite 与协议边界说明。BFCL 评测协议通过独立 `internal/bfcl` 包和 `bfcl-*` CLI 命令接入，不改变产品默认 Agent 协议。

归档边界：

- 分支最新提交：`557e3eb`（`docs(eval): close and archive the BFCL evaluation branch`）
- 归档 tag：`archive/bfcl-v4-ab-20260826`
- 完整 BFCL 实验实现、报告和运行归档：现已位于 `main`；原分支仍作为同一快照的历史归档保留

## 已迁移的功能

- `internal/bfcl`：BFCL JSONL loader、Markdown/原生 FC renderer/parser、单轮与 multi-turn runner、结果归档和官方评分适配。
- `internal/bfcl/pysidecar`：Python sidecar 客户端、服务端和依赖门禁，用于复用官方 evaluator。
- `cmd/rwkv-cli`：`bfcl-eval`、`bfcl-mt-eval`、`bfcl-reparse`、`bfcl-sample` 和 `bfcl-sampling-diagnostic` 命令。
- `configs/` 与 `scripts/`：数据 commit/config、样本 manifest、BFCL 环境安装和运行/比较辅助脚本。
- `docs/` 与 `archive/`：实验报告、规格书、E8 机器可读归档和项目索引。

## 主线已有的 Harness 修复

1. `1d2e1a6` → `4adad5b`：让 route prompt framing 显式、可复现，并增加对应 runner/eval 回归测试。
2. `d0e8223` → `7b06835`：区分主动弃权、route fail-closed、普通 final、tool-like 提取失败和兼容修复；case schema 支持 `require_active_no_call` 与 `forbid_route_fallback`。

这两项修复在完整 BFCL 功能迁移后仍保留，并通过 `internal/agent/...` 与 `api/...` 测试。

## 证据边界

- E8 wrapped Qwen 的 baseline/enhanced 差异是同一 wrapped/anchor 系统内的完整观测，不是公开模型能力或纯 Harness 因果量。
- E9 native Qwen 的 30.00% 是带题池、reasoning replay 和 deadline 约束的诊断结果，不能写成 thinking 的独立收益，也不能宣称复现官方 50.5%。
- `rwkv-abstention-lab` 的 `no_tool`、锚点和 fast-think 结果是模型与实验协议诊断；在产品协议题库完成单因子 A/B 前，不改变产品默认协议。
- wire-compat 修复只记录可恢复量，不能把修复后的输出当作原始协议成功。

BFCL runner 只用于 BFCL 题库的可复现评测；产品题集仍使用 `internal/agent/eval` 的独立 schema。BFCL 的 JSON anchor、`finish_task`、`no_tool` 不会自动进入产品默认协议，若要调整产品 Harness，仍需先做单因子 A/B。

## 验证

在分支归档快照和本次主线迁移后的工作区执行 `go test ./...` 均通过；`bfcl-sample --verify configs/bfcl-sample-v1.json` 也通过。测试过程中只有现存的 macOS deployment-target linker warning，没有失败项。
