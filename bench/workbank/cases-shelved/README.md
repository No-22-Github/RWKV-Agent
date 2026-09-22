# 下架题（不参与跑分）

这里的题**不在** `cases/` 下，所以 `lint.py` / `verify_all.py` / `coverage.py` / `dedup.py`
和 `agent-eval --cases bench/workbank/cases` 都不会看到它们。要恢复，把目录移回
`cases/<scenario>/<id>/` 即可——题目文件本身没有改动。

## 2026-09-22 下架 4 题：上下文预算不可测

**下架理由不是题难，是这些题会从测量里消失。** 模型取数方式不对时，上游返回
`HTTP 400: maximum context length is 32768`，harness 记为 `invalid`（infra 作废）并把该题
**踢出分母**——选错工具不会失分，只会让这道题不被计算。

判据是目标模型 RWKV 的上下文只有 16k（实际可用更少）。在 32k 的 Qwen 端点上这些题已经在抖，
16k 下连正确路径也会炸，那时它们不是「难」，是「不可测」。

9B 实测（`runs/workbank/postfix-152-grad-k{0,1,2}`，152 题 × 3 轮，温度 0）：

| 题 | level | traps | 机制 | k0–k2 |
|---|---|---|---|---|
| log-0007 | L1 | TR-TRUNC | 单文件 77,867 B | 1 通过 / 2 作废 |
| log-0008 | L2 | TR-TRUNC, TR-DECOY | 单文件 81,541 B | 0 通过 / 1 失败 / 2 作废 |
| log-0020 | L2 | TR-LONG, TR-INJECT | 单文件 44,092 B | 2 通过 / 1 作废 |
| fs-0006  | L1 | TR-TRUNC | **831 个文件**，最大单文件仅 456 B——撑爆的是目录列表，不是单文件 | 0 通过 / 2 失败 / 1 作废 |

同一道题不同轮有时跑完有时作废，取决于模型这轮选了 `read_file` 还是 `search_text` / `read_lines`，
是取数运气而非能力。对照组：**log-0008（81.5 KB，全库最大）在模型走 search_text + read_lines 的那轮
完整跑完并被正常判错**——说明设计意图（用 grep 式取数而非整文件读入）本身是通的，
工具目录里的 `search_text` 就是 grep、`read_lines` 就是 sed 的位置，并不缺 bash。

## 保留未下架的两道（记录在案）

| 题 | 大小 | k0–k2 | 为什么留着 |
|---|---|---|---|
| doc-0012 | 47,844 B | **3/3 通过** | 32k 下工作正常，从未作废 |
| log-0018 | 39,921 B | **3/3 通过** | 同上（扩量轮已从 60,699 B 缩过一次） |

两道按 16k 口径同样超预算，但目前测得动。等真正在 RWKV 上跑过再按实测决定缩题还是下架。

## 配额缺口（有意留着，提醒后续补题或改配额）

`docs/tag-vocab.json` 的场景配额未随下架调整，所以 `coverage.py` 会报缺口：

- `logs` 20 → **17**（下架 3 道）
- `filesystem` 12 → **11**（下架 1 道）
- 全库 152 → **148**

`coverage.py` 只在偏差 >1 时报 gap，所以当前只报一条：`logs L2: need 5, have 3 (short 2)`。
`logs L1`（9/10）与 `filesystem L1`（5/6）在 ±1 容忍内，不报但同样是缺口。

陷阱普查全部仍 ≥3：TR-TRUNC 6→3、TR-LONG 4→3、TR-INJECT 4→3 恰好卡在下限，
**再下架任何一道带这三个陷阱的题都会跌破**。
