# BFCL v4 A+B 分支收口与主线迁移

日期：2026-08-26（Asia/Shanghai）

## 结论

`feat/bfcl-v4-ab` 已完成评测阶段并保留为可回放归档；本次不把整套 BFCL loader、runner、sidecar、样本和运行产物快进到 `main`。主线只接收已经验证为产品 Harness 修复的两项提交，避免评测协议和产品协议耦合。

归档边界：

- 分支最新提交：`557e3eb`（`docs(eval): close and archive the BFCL evaluation branch`）
- 归档 tag：`archive/bfcl-v4-ab-20260826`
- 完整 BFCL 实验实现、报告和运行归档：保留在 `feat/bfcl-v4-ab`

## 已迁移到 `main`

1. `1d2e1a6` → `4adad5b`：让 route prompt framing 显式、可复现，并增加对应 runner/eval 回归测试。
2. `d0e8223` → `7b06835`：区分主动弃权、route fail-closed、普通 final、tool-like 提取失败和兼容修复；case schema 支持 `require_active_no_call` 与 `forbid_route_fallback`。

这两项迁移在 `main@351c140` 上可无冲突应用，并通过 `internal/agent/...` 与 `api/...` 测试。

## 证据边界

- E8 wrapped Qwen 的 baseline/enhanced 差异是同一 wrapped/anchor 系统内的完整观测，不是公开模型能力或纯 Harness 因果量。
- E9 native Qwen 的 30.00% 是带题池、reasoning replay 和 deadline 约束的诊断结果，不能写成 thinking 的独立收益，也不能宣称复现官方 50.5%。
- `rwkv-abstention-lab` 的 `no_tool`、锚点和 fast-think 结果是模型与实验协议诊断；在产品协议题库完成单因子 A/B 前，不改变产品默认协议。
- wire-compat 修复只记录可恢复量，不能把修复后的输出当作原始协议成功。

后续产品工作应在独立题库中验证 route parser、主动 no-call、缺 required 参数追问和多轮决策形状；BFCL 的 JSON anchor、`finish_task`、`no_tool` 不直接迁移。

## 验证

在分支归档快照上执行 `go test ./...` 全部通过；在主线迁移后的工作区再次执行同一命令也全部通过。测试过程中只有现存的 macOS deployment-target linker warning，没有失败项。
