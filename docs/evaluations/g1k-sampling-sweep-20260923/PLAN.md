# g1k 采样参数扫描 — 预注册计划（2026-09-23）

按 `docs/evaluations/benchmark-protocol.md` 执行。本文件在开跑前写定；跑后只追加"偏离记录"，不改判定规则。

## 要回答的问题

`rwkv-g1k-7b-temp-3601` 在 `g1k` 格式下，用什么采样参数做 Agent 任务最好？
历史上所有 RWKV run 都是 `top_k=1`（温度无效），所以这是 g1k **第一次真正做采样实验**。

## 固定条件

| 项 | 值 |
|---|---|
| 模型 / 端点 | `rwkv-g1k-7b-temp-3601` @ api-7b.rwkvos.com，albatross-1.3.0，hard_max_bsz 169 |
| 二进制 | `bin/rwkv-cli`，由分支 `bench/g1k-sampling-sweep` 的干净 HEAD 编译（含 `g1k` 预设与 MatchPreset 修正）；每个 run 的实际 git HEAD、diff sha 与二进制 sha256 以其 `experiment.json` 为准 |
| 格式 | `--profile g1k --strict-spec` |
| 预算 | `--max-steps 16 --max-tokens 4096 --case-timeout 30m` |
| workbank | 148 题（含 draft），bank_version `sha256:11a561f56b4cd914fc93fe4b11d28d07a9ad0caf74df07c9b2f173ed2c1636af` |
| bfcl-product | 60 题 |
| 惩罚 | 除 `backend` 档外全部 0 / 0 / decay 1 |

## 扫描网格

**阶段 1：筛选（k=1）**，共 9 档，每档 workbank 与 bfcl-product 各一次。

| 档名 | T | top_k | top_p | 惩罚 |
|---|---|---|---|---|
| `greedy` | 1 | 1 | 1 | 0 |
| `t03-p10` | 0.3 | 65536 | 1.0 | 0 |
| `t03-p05` | 0.3 | 65536 | 0.5 | 0 |
| `t06-p10` | 0.6 | 65536 | 1.0 | 0 |
| `t06-p05` | 0.6 | 65536 | 0.5 | 0 |
| `t10-p10` | 1.0 | 65536 | 1.0 | 0 |
| `t10-p05` | 1.0 | 65536 | 0.5 | 0 |
| `backend` | 1.0 | 20 | 0.3 | 2.0 / 0.2 / 0.996 |
| `backend-nopen` | 1.0 | 20 | 0.3 | 0 |

**阶段 2：复测（k=3）**：阶段 1 按综合分排名前 3 的采样档，加上 `greedy`（greedy 在阶段 2 补到 k=2）。

**阶段 3（视阶段 2 结果决定是否跑）**：在胜出档上扫 presence penalty ∈ {0, 0.5, 1.0}，k=3。

## 指标与判定规则

- 每个 run 必须先过 `check_run.py` 闸门；不过的 run 重跑，不进入统计。
- **主指标**：workbank strict 通过数（作废计失败，分母 148）。
- **综合分**（只用于阶段 1 排名）：workbank strict 通过数 + bfcl-product strict 通过数。
  这样设的原因：g1k 在旧 40 题冻结集上贪心只有 0–3/40，workbank 可能贴地、区分不开；bfcl-product 历史 49/60，有区分度。
- **阶段 2 胜出规则**：
  1. 按 k=3 的 workbank strict 均值排序。
  2. 第一名与第二名的均值差 ≤ 两者 k 次极差中较大者时，视为无法区分，改用 bfcl-product 均值排序。
  3. 还分不开，选温度更低的档（方差小、更接近可复现）。
- **地板规则**：阶段 1 若所有档的 workbank strict 都 ≤ 5/148，workbank 在该模型上视为贴地，
  阶段 2 改用综合分排序，并在报告里如实写明"workbank 对 g1k 基座无区分度"。
- 附带报告（不参与判定）：作废数、protocol validity、`capability_gate.py` 分层、按 scenario 拆分。

## 执行方式

```bash
# 阶段 1
python3 .claude/skills/rwkv-bench/sweep.py --out runs/bench-20260923 \
  --arms greedy,t03-p10,t03-p05,t06-p10,t06-p05,t10-p10,t10-p05,backend,backend-nopen \
  --suites workbank,bfcl-product --k 0
python3 .claude/skills/rwkv-bench/rank.py runs/bench-20260923
# 阶段 2（<A>,<B>,<C> 为阶段 1 前三名）
python3 .claude/skills/rwkv-bench/sweep.py --out runs/bench-20260923 --arms <A>,<B>,<C> --suites workbank,bfcl-product --k 1-2
python3 .claude/skills/rwkv-bench/sweep.py --out runs/bench-20260923 --arms greedy --suites workbank,bfcl-product --k 1
python3 .claude/skills/rwkv-bench/rank.py runs/bench-20260923 --save docs/evaluations/g1k-sampling-sweep-20260923/rank.md
```

- 同一档的 workbank（`--case-parallelism 148`）与 bfcl-product（`--case-parallelism 20`）并行，合计 ≤ 169。
- run 目录：`runs/bench-20260923/g1k-{workbank,bfclp}-<档名>-k<i>/`。
- 端点快照：开跑前已存 `runs/bench-20260923/endpoint-before-*.json`；每个阶段结束后再存一次，模型 id 变化则该阶段作废。
- 预计耗时：workbank 每轮约 8–9 分钟，阶段 1 约 80 分钟，阶段 2 约 80 分钟。

## 偏离记录

- 2026-09-23 09:45 首次启动 greedy 后按用户要求中止，两个半成品 run 移入 `runs/bench-20260923/aborted/`，不计入。
  改为先把驱动与排名脚本写成正式版（`sweep.py` / `rank.py`），再择时开跑。
- 2026-09-23（阶段 1 进行中，用户提问后补充；不改判定规则，只加报告要求）：
  1. 排名之外，报告须按 scenario / level / trap 拆分各档对照 greedy 的得失，
     标出"总分持平但场景间此消彼长"的档。
  2. 选出的档在报告里的最终分数，用**新的一组副本**重跑得出，不沿用扫参阶段的分数（避免选择偏差）。
  3. 正式全量阶段，胜出档与 greedy 在全部 7 套上对照；胜出档在未参与扫参的套件（boundary / assistant /
     smoke / primitive）上若明显低于 greedy，报告须写明。
- 2026-09-23 10:25 阶段 1 首档（greedy）两个 run 被判需重跑：workbank 56/148 题、bfcl-product 14/60 题
  报 `context deadline exceeded`。根因是 CLI 单题超时默认 2 分钟，驱动未显式设置（旧 wire-check 批次用的是 30m）。
  中止整轮，驱动固定 `--case-timeout 30m` 后从头重跑阶段 1；此前 run 全部移入 `aborted/`，不计入。
  预算表补一行：单题超时 30m。
