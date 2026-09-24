# State 学习率扫描 PLAN（2026-09-23）

## 0. 要回答的问题

同一语料 `/Users/no22/train.textonly.jsonl`（630 行，g1k wire 契约格式）下，5 个不同学习率
训练出的 state 哪个对 g1k 7B 的 Agent 能力（bfcl-product + workbank）提升最大？

被测对象：`rwkv-g1k-7b-temp-3601` @ api-7b.rwkvos.com（albatross-1.3.0）+ state 文件。

对照：无 state（`none`，端点默认行为）。同模型、同日、同二进制的 g1k-agent 无 state 基线
另见 `docs/evaluations/g1k-sampling-sweep-20260923/REPORT.md`（bfcl 46/50，workbank 6/8）。

主指标：strict task_success。bfcl-product 与 workbank 合计 + 分套件拆分。

## 1. Arms（6 个）

| arm | state_id（= 上传文件名） | lr | step | RMS | epoch | 备注 |
|---|---|---|---|---|---|---|
| lr2e-2 | `g1k-20260923-lr2e-2-decay-ep4-s316-rms0.1030.pth` | 2e-2 | 316 | 0.1030 | 4 | 用户标注 ep4 |
| lr1e-2-flat | `g1k-20260923-lr1e-2-flat-const-ep6-s474-rms0.0957.pth` | 1e-2 | 474 | 0.0957 | 6 | 恒定 lr |
| lr1e-2 | `g1k-20260923-lr1e-2-decay-ep6-s474-rms0.0637.pth` | 1e-2 | 474 | 0.0637 | 6 | 衰减版 |
| lr5e-3 | `g1k-20260923-lr5e-3-decay-ep10-s790-rms0.0556.pth` | 5e-3 | 790 | 0.0556 | 10 | |
| lr3e-3 | `g1k-20260923-lr3e-3-decay-ep12-s948-rms0.0439.pth` | 3e-3 | 948 | 0.0439 | 12 | |
| none | （不传 --state-id） | – | – | – | – | 对照 |

state 文件本地路径 `state_output/sweep_runs/sweep_runs/<lr>/state-step-<step>.pth`（16.8MB each），
其中 lr5e-3、lr3e-3 两个为本轮补传；其余 3 个端点上已存在同名 state。

## 2. 固定维度（隔离 state 变量）

- 格式：`--profile g1k --strict-spec`（语料契约逐字对齐，见 `docs/corpus-g1k-wire-format.md`）
- 采样：`g1k-agent`（T 0.3 · top_p 0.5），取自 2026-09-23 采样扫描结论，本轮不扫采样
- 预算：`--max-steps 16 --max-tokens 4096 --decision-max-tokens 2048 --case-timeout 30m`
- 传输：`--remote-batch-wait 0s`；总并发 ≤ 64
- 二进制：`bin/rwkv-cli` @ HEAD `fd17e2a` + sweep.py `--state-id` 扩展
- workbank 148 题含 draft，bank_version 与 case 源哈希由 sweep.py 记入 experiment.json

## 3. 判定规则（预注册）

1. 每个先过闸门（check_run.py），FAIL 作废不计分。
2. 主排序：bfcl-product + workbank 两套 k 副本合计分；并列看 workbank 均值；
   仍并列取 RMS 更小（训练更收敛）者，并标注"无法区分"。
3. 与 none 的差小于同 arm k 次极差的，写"无法区分"。

## 4. 步骤

1. smoke（10 题）× 6 arms，k=1：验证 state 接线生效、后端稳定，并给粗信号。
2. 主矩阵：{workbank, bfcl-product} × 6 arms × k=0-1（24 个 run），后台执行。
3. 若前两名合计差 ≤ 较大者极差，加跑 k=2（两 arms × 两套 × 2 副本）。
4. `rank.py` / `compare.py` 汇总，REPORT.md 出全矩阵与结论。

## 5. 交付

`docs/evaluations/state-lr-sweep-20260923/REPORT.md`：完整表格矩阵（arm × 套件 × 副本）、
与 none 的配对比较、最优 state 及其训练参数、局限性。
