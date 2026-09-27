# State checkpoint 扫描 PLAN（2026-09-27，train-9-27）

## 0. 要回答的问题

用户 2026-09-27 交付的新一轮 state tuning 产物（train-1-1，lr2e-2，语料约 1000 条出头，
g1k wire 契约格式）共有 6 个 checkpoint，哪个对 g1k 7B 的 Agent 能力
（workbank + bfcl-product）提升最大？

被测对象：`rwkv-g1k-7b-temp-3601` @ api-7b.rwkvos.com（albatross-1.3.0）+ state 文件。

对照：无 state（`none`，端点默认行为）。同模型、同日、同二进制、同 bank。

主指标：strict task_success，workbank 与 bfcl-product 分套件 + 合计。
前轮参照：`docs/evaluations/state-lr-sweep-20260923/REPORT.md`（旧语料 lr2e-2-s316 workbank 最优）。

## 1. Arms（7 个）

| arm | state_id（= 上传文件名） | step | 备注 |
|---|---|---|---|
| s79 | `t927-s79.pth` | 79 | |
| s158 | `t927-s158.pth` | 158 | |
| s237 | `t927-s237.pth` | 237 | |
| s316 | `t927-s316.pth` | 316 | 旧语料轮的最优步数 |
| s395 | `t927-s395.pth` | 395 | |
| fin | `t927-fin.pth` | final | 训练收尾 |
| none | （不传 --state-id） | – | 对照 |

state 本地路径 `/home/no22/states/upload/t927-*.pth`（16.8MB each，源包
train-9-27.tar.gz 内 `train-1-1/lr2e-2/`）。checkpoint 间隔 ≈ 79 步（约每 1/5 训程一个）。

## 2. 固定维度（隔离 checkpoint 变量）

- 格式：`--profile g1k --strict-spec`
- 采样：`g1k-agent`（T 0.3 · top_p 0.5），沿 2026-09-23 采样扫描结论，本轮不扫采样
- 预算：`--max-steps 16 --max-tokens 4096 --decision-max-tokens 2048 --case-timeout 30m`
- 传输：`--remote-batch-wait 0s`；总并发 ≤ 64
- 二进制：`bin/rwkv-cli` @ HEAD `d5164cd`，`bin/rwkv-lab bench sweep --state-id`
- workbank 148 题含 draft，bank_version 与 case 源哈希由 sweep 记入 experiment.json
- bfcl-product 60 题

## 3. 判定规则（预注册）

1. 每 run 先过 `rwkv-lab run check` 闸门，FAIL 作废不计分。
2. 筛选轮 k=1（`--k 0`）：主排序 workbank strict；并列或差 ≤ 2 题看 bfcl-product；
   再并列取 step 更小（欠拟合侧）者并标"无法区分"。
3. 前两名合计差 ≤ 同配置极差估计（workbank 按前轮经验 ±2 题）→ 对前二加跑 k=1、2
   两副本再判，仍分不出写"无法区分"。
4. 与 none 的差小于该极差 → 写"无法区分"，不宣称提升。

## 4. 步骤

1. 端点前后快照（模型 id 每次开跑前由 sweep 自动核对）。
2. 主矩阵：{workbank, bfcl-product} × 7 arms × k=1，逐 arm 串行（并发预算内套件并行）。
3. 闸门全过后 `bench rank` / `run compare` 汇总；触发规则 3 则补副本。
4. REPORT.md 出全矩阵、与 none 配对比较、最优 checkpoint 结论。

## 5. 交付

`docs/evaluations/state-t927-20260927/REPORT.md`：arm × 套件分表、与 none 的配对翻转、
最优 checkpoint 及训练侧解读、局限性。runs/ 不入库；凭据不进任何入库文件。
