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
| 预算 | `--max-steps 16 --max-tokens 4096 --decision-max-tokens 2048 --case-timeout 30m`；传输 `--remote-batch-wait 0s` |
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
- 2026-09-23 11:00 重启后首档 greedy：workbank 撞满 30m（1801s），142/148 题首步自发 `<think>`、仅 73 闭合，
  85 题决策协议无效、14 题回复超 4MB（贪心复读失控）。根因：`--max-tokens` 只管终答，决策步落到协议默认 512。
  用户裁定：自发思考是模型缺陷，不修，只加上限防空转 → 驱动固定 `--decision-max-tokens 2048`，闸门增查该项。
  阶段 1 第三次从头跑；此前全部 run（含已过闸门但在 512 预算下的 bfclp-greedy）移入 `aborted/`。
  预算表补：决策步 2048。
- 后续（本轮之后，用户提出）：做矩阵，把"空思考预填（thinking=fast）"等格式维度与采样档交叉测；本轮先跑完采样扫描。
- 2026-09-23 11:10 第三次首档 greedy：workbank 132/148、bfcl-product 50/60 作废，全部为
  `response exceeded 4194304 bytes`。根因是 harness 缺陷：客户端把 10ms 内的并发请求合并成一个 batch，
  而 4 MiB 上限按整个合并响应计，不按单条；决策上限 512→2048 后每条响应变大，几乎每个 batch 都超限。
  （09-22 的 30 题作废、第二次尝试的 14 题作废同源。）已修：batch 上限按条数放大（单条保护不变），加回归测试。
  另记：`/v1/models` 的 `created` 是请求时刻而非加载时刻，不能用来判断后端是否重启。
  阶段 1 第四次从头跑；第三次的 run 移入 `aborted/attempt3-batch4mib/`。
- 2026-09-23 11:45 修复 4 MiB 后单跑 greedy 验证：作废归零，但 workbank 25/148、bfcl-product 1/60 撞满 30m。
  超时题每次回复仅 60–90 字符、30 分钟只发出 6–9 次调用。根因：客户端合并请求时整批响应结束才交付，
  复读到 2048 的成员拖住同批短回复（队头阻塞）。驱动改为 `--remote-batch-wait 0s`（每题独立请求，后端自己批处理）。
  该验证 run（workbank 2/148、bfcl-product 37/60）受阻塞污染，移入 `aborted/attempt4-hol/`，不计入。
