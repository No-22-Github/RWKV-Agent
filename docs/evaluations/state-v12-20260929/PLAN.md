# State checkpoint 扫描 PLAN（2026-09-29，train-1-2 / v1.2 语料）

## 0. 要回答的问题

1. v1.2 语料（v1.1 + b04 + 每行终答后接 `\n\nUser:`，修"终答无 EOS"bug）训出的 state，
   相比 t927 最优点 `s316` 与无 state 基线，workbank / bfcl-product 是否提升？
2. 两路训练哪路更好：suffix-only（与 t927 同参，只换数据）vs mixed（数据 + lr 同时变）？
3. 终答续写 `✿textN✿User:` 的形态是否消失（EOS 修复是否生效）？

被测对象：api-7b.rwkvos.com 当前模型 + state 文件（跑前快照记录模型 id，须与 t927 轮
`rwkv-g1k-7b-temp-3601` 一致，否则 t927 对照作废，只比 none）。

主指标：strict task_success。workbank 以**干净 112 题**为准（剔除 `bench/workbank/seeded-base700.txt` 里的 36 道泄漏种子题，见 t927 报告 §8 的 09-29 更正），148 全量只作参考；bfcl-product 60 题。
次指标：终答含 `✿` 的题数、answer 契约拒绝题数（t927 s316：25/148）。
前轮参照：[`../state-t927-20260927/REPORT.md`](../state-t927-20260927/REPORT.md)。

## 1. Arms

源文件：训练机 `~/no22/rwkv_lighting_cuda_train/train-1-2-*/`，本地同步至 `~/train-1-2-*/`，
19 个 .pth 与服务器 SHA256 逐一核对一致。mixed 的 `state-final.pth` 与 step-576 字节相同，不单列。

| 组 | arm | state_id（上传文件名） | 源文件 |
|---|---|---|---|
| 对照 | none | （不传 --state-id） | – |
| 对照 | t927 | `t927-s316.pth` | train-1-1/lr2e-2/state-step-00000316.pth |
| suffix-only（lr 2e-2，456 步，每 79 步） | s79 … s395 | `v12s-s{79,158,237,316,395}.pth` | state-step-000000NN.pth |
| | sfin | `v12s-fin.pth` | state-final.pth（step 456） |
| mixed（lr 1.5e-2，576 步，每 48 步） | m96 … m576 | `v12m-s{96,192,288,384,480,576}.pth` | 隔一取一 |

共 14 arm。mixed 先筛隔一个点（每 96 步 ≈ 2/3 epoch）；峰值落在哪里，就补跑它两侧的
48 步邻点（未跑的 6 个里挑，至多 2 个）。

## 2. 固定维度

- 格式：`--profile g1k --strict-spec`
- 采样：`g1k-agent`（与 t927 轮相同，不扫）
- 预算：`--max-steps 16 --max-tokens 4096 --decision-max-tokens 2048 --case-timeout 30m`，`--remote-batch-wait 0s`
- 并发：经 Cloudflare 单队列，总在飞 = 64（上限，不许加）
- 二进制：`local/bin/rwkv-cli` / `local/bin/rwkv-lab`，用执行当天 main 的最新提交编译（HEAD 写进报告），工作区干净
- 套件：workbank 148 题含 draft；bfcl-product 60 题

## 3. 判定规则（预注册）

1. 每 run 过 `rwkv-lab run check` 闸门，**并且**过 [`check_v12.py`](check_v12.py)（闸门对全部作废的 run 也会报 PASS，见 HANDOFF §4.1），任一不过就作废，不计分。
2. 筛选轮 k=1：主排序 workbank 干净 112 题 strict；差 ≤ 2 题看 bfcl-product；再并列取 step 小者并标"无法区分"。
3. 与 t927 / none 的差 ≤ 2 题（前轮噪声估计）→ 写"无法区分"。
4. 全场最优点若对 t927-s316 的配对翻转单侧 p > 0.05，对这两个 arm 各补 k=1、2 两个副本再判。
5. mixed 与 suffix-only 的比较只陈述，不归因于 lr（mixed 同时改了数据与 lr）。

## 4. 步骤

> 执行细节（命令、并发、有效性检查、出错处理）以 [HANDOFF.md](HANDOFF.md) 为准。2026-09-29 下午在本机试跑，全部作废（原因见 HANDOFF §2.4），改由 VPS 执行。

1. 跑前端点快照；`rwkv-cli state list` 确认 `t927-s316.pth` 仍在，12 个新文件上传。
2. 逐 arm `rwkv-lab bench sweep --state-id … --arms g1k-agent --suites workbank,bfcl-product --k 0`。
3. 跑后端点快照；`bench rank` / `run compare` 汇总；按规则补点、补副本。
4. 统计 `✿` 续写与契约拒绝题数，逐 arm 对比 t927。

## 5. 交付

`docs/evaluations/state-v12-20260929/REPORT.md`。runs/ 不入库；凭据不进任何入库文件。
