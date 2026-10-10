# 真思考（think-full）干净复测 — 预注册计划

日期：2026-10-10。HEAD `a25a94e`（工作区干净），二进制当日构建。

## 要回答的问题

正式版 `rwkv7-g1k-7.2b-20260930-ctx25600`（无 state）放开思考后，Agent 能力是否稳定好于 `g1k`（thinking=off）。
2026-10-03 的两次 `g1k+think-full`（[REPORT](../g1k-official-format-20261003/REPORT.md) fC / qC）workbank 都 +3 以上，
但有三处干扰没排除，本轮逐一去掉：

| 干扰 | 10-03 | 本轮 |
|---|---|---|
| 每步工具结果后的提醒仍写「Do not open a `<think>` block」，与 System 的「Close your thinking with `</think>`」矛盾 | 有 | `--wire nudge=think`（提醒去掉这半句，其余逐字不变） |
| 决策步预算 2048，思考写不完被截断 | 2048 | 4096 |
| 每组只跑 1–2 次 | k=1 | k=3 |

## 各组

| 组 | 参数 | 决策预算 |
|---|---|---|
| A | `--profile g1k --strict-spec` | 2048（规程） |
| T | `--profile g1k+think-full --wire nudge=think`（非注册组合，不能加 `--strict-spec`） | 4096 |

共同：内网网关 `http://100.64.0.4:8018/v1`（NO_PROXY）、`--sampling g1k-agent`、16 步、终答 4096 token、
单题 30 分钟、合并窗口 0、`--tool-catalog work-v1 --file-tools lines`。
套件：workbank 148（另报去掉 seeded-base700 的干净 112）、bfcl-product 60（中文 40 / irrelevance 20 分开报）。
顺序 A-k0、T-k0、A-k1、T-k1、A-k2、T-k2 交替，每批 workbank 48 + bfcl 16 并行，总并发 64；前后拍端点快照。

## 判定规则

1. 主指标：workbank 148 strict 三次均值。T 均值 − A 均值大于两组各自极差中较大者 → 记「T 更好」；否则「无法区分」。
2. 配对：三次合并后逐题 pass 次数比较，报翻转 +a/−b 与符号检验 p。
3. 副指标：bfcl-product 合计、中文 40、irrelevance 20，同样按均值与极差报。中文若三次都低于 A 的最低值，记为「稳定代价」。
4. 诊断：T 组思考块未闭合的生成，分「写满预算（finish=length）」与「提前结束（finish=stop）」两类计数；失分用 `run gate` 分层。
5. 结论只针对基模；即使 T 更好，也不直接改产品默认，需另议语料（带思考过程）与延迟。
