# State checkpoint 扫描报告（2026-09-27，train-9-27 / lr2e-2 六 checkpoint）

计划与预注册判定规则见 [PLAN.md](PLAN.md)，规程见 [`docs/evaluations/benchmark-protocol.md`](../benchmark-protocol.md)。

## 0. 结论

1. **最优 checkpoint：`s316`（`t927-s316.pth` = 源包 `train-1-1/lr2e-2/state-step-00000316.pth`）**。
   workbank 16/148（无 state 基线 9，**+7**；配对翻转 +15/−8），bfcl-product 26/60（基线 47）。
   与第二名（s395/fin，各 12）差 4 > 预注册噪声 ±2，按规则不需补副本。
2. **workbank 随训练进度单调爬升后回落**：5 → 8 → 11 → **16** → 12 → 12（s79→s158→s237→s316→s395→fin）。
   峰值在 step 316（checkpoint 间隔 79 步，即约 4/5 训程处），其后两个点回落 4 题。
3. **bfcl-product 全部 state 低于基线 47**（26/34/14/24/11/21）——state 洗弃权的老问题仍在：
   irrelevance 20 题从基线 14 掉到 1–8，multiturn 从 17 掉到 0–12。**但 missing-required 守住了**
   （基线 16，state 最好 17），与旧语料（missing 18→0）相比是本语料的实质进步——追问/澄清行为被保留。
4. **直答→复读→答错的形态迁移**（详见 §4）：state 把基模 83 题"不调工具直答"压到 5 题，
   代价是中段 checkpoint 复读海啸（s158 forced 93 题），到 s316 稳定在 48；剩余主桶是
   "走完流程答错"（s316 79 题）——**教会了进工具循环，没教会读对/算对**，与 09-24 轮结论一致。
5. 显著性提示：+15/−8 单副本符号检验 one-sided p=0.105（two-sided 0.210），方向明确但未过 0.05 线。
   如需硬结论可对 s316 + none 各补 2 副本（未预注册，未执行）。

## 1. 可比性与有效性

| 项 | 值 |
|---|---|
| 模型 / 端点 | `rwkv-g1k-7b-temp-3601` @ api-7b.rwkvos.com，albatross-1.3.0，hard_max_bsz 169；跑前/跑后快照模型 id 一致（`runs/bench-20260927-t927/endpoint-*.json`） |
| 分支 / 提交 | `distill/workflow-spec` @ `d5164cd`，工作区干净 |
| 二进制 | `bin/rwkv-cli`（HEAD `d5164cd` 构建，sha256 `3c2e16fa…9845e`），`bin/rwkv-lab bench sweep --state-id` |
| 格式 | `--profile g1k --strict-spec` |
| 采样 | `g1k-agent`（T 0.3 · top_p 0.5 · top_k 65536 · 双 penalty 0），固定不扫——隔离 checkpoint 变量 |
| 预算 | `--max-steps 16 --max-tokens 4096 --decision-max-tokens 2048 --case-timeout 30m`；`--remote-batch-wait 0s` |
| 并发 | 每套件硬编码 workbank 48 + bfclp 16（合计 64）。本轮应用户要求传 `--max-concurrency 96`，**实际未生效**（sweep 的套件并行度不随预算缩放，见 §7 已列修复项），真实在飞 64 |
| workbank | 148 题含 draft，case 源 sha256 `2d9193e4…ef98f`；bfcl-product 60 题 |
| 有效性 | **14/14 run 一次过闸门**，invalid 0，infra_errors 0，无重跑 |

## 2. Arms 与主矩阵（strict，k=1）

| arm | state_id | 源文件 | workbank /148 | bfcl-product /60 |
|---|---|---|---|---|
| none | （不挂 state） | – | 9 | **47** |
| s79 | `t927-s79.pth` | state-step-00000079.pth | 5 | 34 |
| s158 | `t927-s158.pth` | state-step-00000158.pth | 8 | 14 |
| s237 | `t927-s237.pth` | state-step-00000237.pth | 11 | 24 |
| **s316** | `t927-s316.pth` | state-step-00000316.pth | **16** | 26 |
| s395 | `t927-s395.pth` | state-step-00000395.pth | 12 | 11 |
| fin | `t927-fin.pth` | state-final.pth | 12 | 21 |

语料：用户 2026-09-27 交付 train-9-27.tar.gz（`train-1-1/lr2e-2/`，lr 2e-2，约 1000 条出头的蒸馏语料），
6 个 checkpoint（间隔 79 步）。上传端点 state_id = 短名文件名。

## 3. workbank 按场景（passed/n）

| 场景 | n | none | s79 | s158 | s237 | s316 | s395 | fin |
|---|---|---|---|---|---|---|---|---|
| web | 16 | 1 | 3 | 1 | 3 | **6** | 5 | 3 |
| notool | 12 | **8** | 2 | 0 | 3 | 1 | 0 | 1 |
| script | 20 | 0 | 0 | 1 | 0 | 2 | 3 | 2 |
| config | 16 | 0 | 0 | 2 | 2 | 2 | 0 | 0 |
| docs | 12 | 0 | 0 | 2 | 2 | 2 | 1 | 1 |
| code | 12 | 0 | 0 | 1 | 0 | 1 | 0 | 2 |
| logs | 17 | 0 | 0 | 0 | 1 | 1 | 1 | 1 |
| hybrid | 12 | 0 | 0 | 1 | 0 | 1 | 1 | 1 |
| tabular | 20 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| filesystem | 11 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |

s316 的 +15 增益分布在 7 个场景（web +5 为主，cfg/doc/scr 各 +2），不是单场景暴走；
代价是 notool 8→1（弃权被洗，与 09-24 轮同形状）。

## 4. 失败形态迁移（workbank，题数）

| arm | PASS | 直答错（不调工具） | 直答 UNKNOWN | 复读→强制收尾 | 走完流程答错 |
|---|---|---|---|---|---|
| none | 9 | 60 | 23 | 51 | 5 |
| s79 | 5 | 25 | 19 | 66 | 33 |
| s158 | 8 | 8 | 0 | **93** | 39 |
| s237 | 11 | 13 | 0 | 68 | 56 |
| **s316** | **16** | 5 | 0 | 48 | **79** |
| s395 | 12 | 8 | 0 | 63 | 65 |
| fin | 12 | 10 | 1 | 58 | 67 |

（口径：forced = `forced_answers>0`；直答 = 全程 0 次工具调用；走完流程答错 = 有工具调用且自然终答错误。
none 的"直答 UNKNOWN 23 题"在所有 state 下归零——自发弃权完全消失。）

## 5. bfcl-product 按类别（passed/n）

| 类别 | n | none | s79 | s158 | s237 | s316 | s395 | fin |
|---|---|---|---|---|---|---|---|---|
| irrelevance（不该调） | 20 | **14** | 8 | 1 | 3 | 3 | 1 | 5 |
| missing-required（该追问） | 20 | 16 | 14 | 12 | 16 | **17** | 10 | 15 |
| multiturn | 20 | **17** | 12 | 1 | 5 | 6 | 0 | 1 |

missing-required 全 state 均值 14.0，s316 反超基线 1 题——本语料的 clarify 行为迁移成功；
irrelevance/multiturn 仍是 state 的固定失血点。

## 6. 泄漏口径

t927 语料为蒸馏管线自产题目（非 workbank 种子衍生），b01–b03 各批入库前均过管线自带
decontam 闸门（对 workbank 全量最近邻相似度打分，flagged 即下架；b03 抽样相似度 ≤0.04，
shelved 216/422/614 条见 `runs/distill/b0*/decontam-*.jsonl`）。故本轮按 148 题全量计分为主口径，
不适用 09-24 轮的"非种子 112 题"规则。

## 7. 局限与后续

- **k=1 单副本**：s316 vs none 符号检验 one-sided p=0.105，未过 0.05；结论方向明确（配对 +15/−8），
  如需硬显著性对 s316 + none 各补 2 副本即可（~50 分钟）。
- **并发未生效**：`--max-concurrency 96` 因 sweep 套件并行度硬编码（48/16）而无效果，
  实际在飞 64；本轮跑完后已修复（套件并行度随预算比例缩放，预算 ≤ spec 之和时行为不变）。
- state × 采样档未交叉（`g1k-agent-fast` 的抑复读惩罚对 s158 型复读海啸可能有直接收益，未测）。
- 剩余主桶"走完流程答错"（s316 79 题）是下一轮语料的头号目标：教读对/算对，不是教调工具。
- notool 12 题从 8 掉到 1：若想两套兼得，语料需补"不该调就不调"的负样本比重。

## 8. 复现

```bash
go build -o bin/rwkv-cli ./cmd/rwkv-cli && go build -o bin/rwkv-lab ./cmd/rwkv-lab
export RWKV_CF_ID=… RWKV_CF_SECRET=…
# 每 arm 一次调用（state 换 t927-{s79,s158,s237,s316,s395,fin}.pth；none 去掉 --state-id）
bin/rwkv-lab bench sweep --out runs/bench-20260927-t927 --arms g1k-agent \
  --suites workbank,bfcl-product --k 0 --state-id t927-s316.pth \
  --prefix s316 --max-concurrency 96
```

run 数据在 `runs/bench-20260927-t927/`（不入库）；state 文件在 `/home/no22/states/upload/`（不入库）。
