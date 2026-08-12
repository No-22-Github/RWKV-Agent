# Primitive Bench v12 基线（2026-08-13）

## 范围

- 数据集：`RWKV-Vibe/rwkv-Primitive-Bench/agent_cases_orig30`，共 30 题。
- 上游快照：`416b073d2c5442ae34bfbf8a3b84ed414b5b85ff`。
- RWKV-Agent：`c94a35b`，Harness `rwkv-agent-eval-v12`。
- 模型：`rwkv7-g1i-7.2b-20260805-ctx16384`。
- 接口：`rwkv_lightning_cuda /v1/batch/completions`。
- 每题使用上游原始 `max_turns`（6–22），case 间目前串行，case 内工具调用串行。

## 结果

全量原始结果为 **12/30（40.0%）**。其中 `find_read_submit` 因单次 HTTP 请求
`unexpected EOF` 失败；相同配置单题补跑为 1/1 通过。替换这一项后的当前有效基线为
**13/30（43.3%）**。这不是一次完全无网络错误的整轮结果，后续对外发布时应再跑一轮确认。

| 指标 | 结果 |
| --- | ---: |
| Protocol validity | 93.6%（219/234） |
| Required-tool completion | 72.2%（52/72） |
| Forbidden-tool avoidance | 100%（2/2） |
| 重复工具调用拒绝 | 101 次 |

排除网络失败后，17 个失败由 9 个步数耗尽、6 个工具调用协议错误，以及 2 个评分条件未满足组成。目前最明显的问题是模型重复调用已经成功或已经失败的工具，导致无法进入 `submit`；其次是长 JSON 工具调用出现截断或非法换行。

旧 v11 的 14/30 使用统一 `--max-steps 12`，会截断原始预算为 16、18、22 的案例，不应作为正式对外分数与 v12 直接比较。

## 复跑

凭证只通过环境变量传入，不写入命令、代码或评测产物：

```sh
export RWKV_CF_ACCESS_CLIENT_ID='...'
export RWKV_CF_ACCESS_CLIENT_SECRET='...'

go run ./cmd/rwkv-cli agent-eval \
  --completion rwkv-lightning \
  --api-url https://api-125-7b.rwkvos.com/v1/batch/completions \
  --api-header-env CF-Access-Client-Id=RWKV_CF_ACCESS_CLIENT_ID \
  --api-header-env CF-Access-Client-Secret=RWKV_CF_ACCESS_CLIENT_SECRET \
  --api-stop-tokens cuda \
  --api-stream=true \
  --model rwkv7-g1i-7.2b-20260805-ctx16384 \
  --suite primitive \
  --case-timeout 8m \
  --temperature 0.1 --top-k 1 --top-p 1 \
  --presence-penalty 0 --frequency-penalty 0 --penalty-decay 1 \
  --output runs/primitive-v12
```

本次本地产物位于：

- `/tmp/rwkv-agent-primitive-full-v12-20260813-16`
- `/tmp/rwkv-agent-primitive-v12-rerun-find-20260813-17`
