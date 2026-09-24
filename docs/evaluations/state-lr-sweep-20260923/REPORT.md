# State 学习率扫描报告（2026-09-24）

计划与预注册判定规则见 [PLAN.md](PLAN.md)，规程见 [`docs/evaluations/benchmark-protocol.md`](../benchmark-protocol.md)。

## 0. 结论

1. **state 显著增强 Agent 工具执行（workbank），但完全破坏弃权/追问行为（bfcl-product）**。
   两者是同一枚硬币：语料把"读文件再回答"训练成了默认动作，"不该调工具就不调"的反面样本
   （notool 场景、bfcl irrelevance/missing）没有守住。
2. **state 中最优：`lr2e2-s316`**（lr 2e-2 衰减，step 316，RMS 0.1030，ep4）：
   workbank 21/148 ×2 副本（**+13 over 无 state，+18/−5 配对翻转，符号检验 p=0.011**），
   且两副本逐题完全一致（极差 0）；bfcl 15.0 均值，是 state 组最高之一。
   次优 `lr3e3-s948`（lr 3e-3，step 948，RMS 0.0439，ep12）：workbank 19.0（p=0.043）、
   bfcl 15.5，与 lr2e2 合计差 1.5 在噪声内，无法区分。
3. **无 state 基模仍是"两套合计"最高者**（54.5 vs 最优 state 36.0）：bfcl 一套的差距
   （46.5 vs 15.0）大于 workbank 的收益（8 vs 21）。若目标是通用助手，不要挂这些 state；
   若目标是工具执行型 Agent（workbank 型任务），挂 `lr2e2-s316`。
4. **学习率不是单调越低越好**：workbank 均值 2e-2(21.0) > 3e-3(19.0) > 1e-2-flat(16.0) >
   1e-2(15.5) ≈ 5e-3(15.5)。RMS 与 workbank 分数无单调关系；1e-2 的恒定/衰减两版无法区分
   （16.0 vs 15.5，极差内）。
5. **`lr5e3-s790` 协议退化**（详见 §3）：坏工具名、复制目录占位符，两套均最差，不推荐。

## 1. 可比性与有效性

| 项 | 值 |
|---|---|
| 模型 / 端点 | `rwkv-g1k-7b-temp-3601` @ api-7b.rwkvos.com，albatross-1.3.0，hard_max_bsz 169；每次 sweep 调用有跑前/跑后快照（`runs/bench-20260923-state/endpoint-*.json`），模型 id 全程一致 |
| 分支 / 提交 | `main` @ `fd17e2a`，工作区干净；sweep.py 新增 `--state-id` 传递与 experiment.json 记录 |
| 二进制 | `bin/rwkv-cli`（HEAD `fd17e2a` 构建），sha256 记录于各 run 的 experiment.json |
| 格式 | `--profile g1k --strict-spec`（语料契约 `docs/corpus-g1k-wire-format.md` 逐字对齐） |
| 采样 | `g1k-agent`（T 0.3 · top_p 0.5），固定不扫——隔离 state 变量 |
| 预算 | `--max-steps 16 --max-tokens 4096 --decision-max-tokens 2048 --case-timeout 30m`；传输 `--remote-batch-wait 0s`；总并发 64（workbank 48 + bfcl 16） |
| state | 16.8MB × 32 tensors（rwkv_lightning state），上传端点 state_id=文件名（含 lr/step/RMS/epoch），sha256 记录于 run.json |
| workbank | 148 题含 draft；bfcl-product 60 题；smoke 10 题（试点） |
| 有效性 | **24/24 run 一次过闸门**（唯一次数：`lr1e2-s474` k1 首尝试遇端点抖动 96 条传输错误，sweep.py 按规程整轮重跑，重跑 0 错误），0 作废计失败 |

## 2. Arms

| arm | state_id | lr | step | RMS | epoch |
|---|---|---|---|---|---|
| `lr2e2-s316` | `g1k-20260923-lr2e-2-decay-ep4-s316-rms0.1030.pth` | 2e-2 衰减 | 316 | 0.1030 | 4 |
| `lr1e2f-s474` | `g1k-20260923-lr1e-2-flat-const-ep6-s474-rms0.0957.pth` | 1e-2 恒定 | 474 | 0.0957 | 6 |
| `lr1e2-s474` | `g1k-20260923-lr1e-2-decay-ep6-s474-rms0.0637.pth` | 1e-2 衰减 | 474 | 0.0637 | 6 |
| `lr5e3-s790` | `g1k-20260923-lr5e-3-decay-ep10-s790-rms0.0556.pth` | 5e-3 | 790 | 0.0556 | 10 |
| `lr3e3-s948` | `g1k-20260923-lr3e-3-decay-ep12-s948-rms0.0439.pth` | 3e-3 | 948 | 0.0439 | 12 |
| `none` | （不挂 state） | – | – | – | – |

语料：`/Users/no22/train.textonly.jsonl`，630 行，g1k wire 契约格式（`<tool_call>` 信封 +
`no_tool` 弃权出口 + 无 think）。三个 state 端点上已预先存在同名上传，lr5e-3/lr3e-3 两个本轮补传。

## 3. 试点（smoke 10 题 × 6 arms，k=1）

全部过闸门、0 基础设施错误。trace 证据（state 生效的直接证据）：

- **none**：23 次模型调用中 11 次以 `<think>` 开头（基模自发思考）。
- **5 个 state 全部**：0 次think 开头，直接输出 `<tool_call>` 或纯文本终答——语料行为成功迁移。
- **lr5e3-s790 协议退化**：出现 `list_files.py` 这类带后缀工具名、参数原样复制目录占位符
  （`"path":"optional rela…"`）、裸 JSON 调用；该 arm smoke 0/10 且单批耗时 92s（其他 12–17s）。
- 试点分数（k=1，噪声大仅作管道验证）：none 4/10，lr1e2f 3/10，lr1e2/lr2e2/lr3e3 2/10，lr5e3 0/10。

## 4. 主矩阵（k=0-1，g1k-agent）

### 4.1 总表（strict，格式 `k0/k1（均）/总分`）

| arm | workbank /148 | bfcl-product /60 | 两套合计均值 |
|---|---|---|---|
| `none` | 8/8（**8.0**） | 43/50（**46.5**） | **54.5** |
| `lr2e2-s316` | 21/21（**21.0**） | 14/16（15.0） | 36.0 |
| `lr3e3-s948` | 19/19（19.0） | 13/18（**15.5**） | 34.5 |
| `lr1e2-s474` | 15/16（15.5） | 8/12（10.0） | 25.5 |
| `lr1e2f-s474` | 17/15（16.0） | 8/8（8.0） | 24.0 |
| `lr5e3-s790` | 14/17（15.5） | 4/6（5.0） | 20.5 |

### 4.2 逐题配对（k0，对照 `none`，符号检验）

| arm | workbank +翻正/−翻负 | p | bfcl +翻正/−翻负 | p |
|---|---|---|---|---|
| `lr2e2-s316` | +18/−5 | **0.011** | +4/−33 | **0.000** |
| `lr3e3-s948` | +18/−7 | **0.043** | +4/−34 | **0.000** |
| `lr1e2-s474` | +14/−7 | 0.189 | +2/−37 | **0.000** |
| `lr1e2f-s474` | +14/−5 | 0.064 | +7/−42 | **0.000** |
| `lr5e3-s790` | +11/−5 | 0.210 | +0/−39 | **0.000** |

### 4.3 workbank 按场景（k0+k1 通过次数和，分母 = 题数 × 2）

| 场景 | n | none | lr2e2 | lr3e3 | lr1e2f | lr1e2 | lr5e3 |
|---|---|---|---|---|---|---|---|
| web | 16 | 1/32 | **16/32** | **17/32** | 16/32 | 11/32 | 10/32 |
| nt（notool） | 12 | **12/24** | 5/24 | 3/24 | 4/24 | 3/24 | 6/24 |
| fs | 11 | 1/22 | 4/22 | **7/22** | 2/22 | 1/22 | 0/22 |
| cfg | 16 | 1/32 | **5/32** | 2/32 | 2/32 | 3/32 | 4/32 |
| log | 17 | 0/34 | **4/34** | 1/34 | 1/34 | 1/34 | 0/34 |
| doc | 12 | 0/24 | 4/24 | 4/24 | 4/24 | 3/24 | **5/24** |
| code | 12 | 1/24 | 2/24 | 1/24 | 1/24 | 1/24 | 2/24 |
| hyb | 12 | 0/24 | 0/24 | 1/24 | 1/24 | **4/24** | 2/24 |
| scr | 20 | 0/40 | 2/40 | 1/40 | 0/40 | 1/40 | 2/40 |
| tab | 20 | 0/40 | 0/40 | 1/40 | 1/40 | **3/40** | 0/40 |

**workbank 的全部增量来自 web 场景**（1/32 → 16–17/32，约 +15 题），加上 cfg/doc/fs/log 的
零星收益；notool 场景反而减半（12 → 3–6，弃权行为被洗掉）；script/tabular/code/hybrid 等
深水区场景仍接近 0。

### 4.4 bfcl-product 按类别（k0+k1 通过次数和）

| 类别 | n×2 | none | lr2e2 | lr3e3 | lr1e2f | lr1e2 | lr5e3 |
|---|---|---|---|---|---|---|---|
| irrelevance（不该调） | 40 | **27** | 3 | 3 | 0 | 1 | 10 |
| missing（该追问） | 20 | **18** | 0 | 0 | 0 | 1 | 0 |
| supplied（应调用） | 20 | **15** | 7 | 7 | 7 | 3 | 0 |
| state 多轮 | 20 | **17** | 11 | 11 | 5 | 10 | 0 |
| recovery 多轮 | 20 | **16** | 9 | **10** | 4 | 5 | 0 |

irrelevance/missing 两个"约束类"全军覆没（27→0–3、18→0–1），supplied 只剩一半，
多轮类保留约六成。与 workbank notool 下降互为印证：**state 学会了"调工具"，忘掉了"不调"**。
lr5e3 的 irrelevance 残留 10 是其协议坏掉（参数非法被拒）的副产品，不是弃权能力。

### 4.5 稳定性

- lr2e2-s316 两副本 workbank 逐题完全一致（21/21），bfcl 14/16；
  lr3e3 workbank 19/19。state 后行为非常稳定，副本间极差远小于无 state 的采样扫描。
- 端点在 00:0x 有一次抖动（lr1e2 k1 首尝试 96 条传输错误），重跑干净，不影响其他 arm。

## 5. 与无 state 基线的外部对照

同模型、同日采样扫描（`g1k-sampling-sweep-20260923`，g1k-agent）：
bfcl 46/50，workbank 6/8，smoke 3/2 —— 本轮 `none`（43/50、8/8、4/10）与其一致，
端点与 harness 未漂移。

## 6. 局限

- k=2 副本、共享端点；lr2e2 与 lr3e3 的合计差（36.0 vs 34.5）在 bfcl 极差内，读作"无法区分"，
  靠预注册平局规则（workbank 均值）取 lr2e2。
- 只测了 `g1k-agent` 一档采样；state × 采样档（如 `g1k-agent-fast` 的抑复读惩罚）未交叉。
- 只测了本语料、thinking=off；语料内的 notool 反面样本占比不足是 bfcl 倒退的头号嫌疑，
  补训（回放基模行为做正则）比换解码参数更可能同时保住两端。
- smoke 已参与管道验证，不计分。

## 7. 复现

```bash
go build -o bin/rwkv-cli ./cmd/rwkv-cli
export RWKV_CF_ID=… RWKV_CF_SECRET=…
# 每 arm 一次调用（--state-id 为本轮 sweep.py 新增）
python3 .claude/skills/rwkv-bench/sweep.py --out runs/bench-20260923-state \
  --arms g1k-agent --suites workbank,bfcl-product --k 0-1 \
  --prefix st-lr2e2-s316 --state-id g1k-20260923-lr2e-2-decay-ep4-s316-rms0.1030.pth
# none 对照去掉 --state-id
```

run 数据在 `runs/bench-20260923-state/`（不入库）；state 文件在 `state_output/`（不入库）。

## 8. 复核勘误（2026-09-24）

逐题与逐轨迹复核（`runs/bench-20260923-state/` 的 summary.json / trace.jsonl，对照
`~/train.textonly.jsonl`）发现以下问题，以本节为准：

1. **题目泄漏**：148 题中 32 题（各类 `*-0001..0004` + `web-0003`）的 prompt、轨迹与答案原样在
   训练集中。去掉后的干净 116 题：none 8/8，lr2e2 16/19，lr3e3 13/14——增益真实，但应按干净集报告。
2. **§0.2 / §4.5 "lr2e2 两副本逐题完全一致" 不实**：两副本总分同为 21，交集仅 8 题（lr3e3 交集 11/19）。
3. **§0.4 学习率结论不成立**：各 arm 的 lr、epoch、step 共变，无法归因到学习率。
4. **§1 "语料契约逐字对齐" 只对第 1 步成立**：g1k 预设 `usermsg=split` 在每次成功调用后插入
   "Use the Tool results above…" User 块（lr2e2 第 2 步起 490/624 个 prompt），训练集 0 次；
   重复拒绝与强制收尾块训练集也 0 次。
5. **失败归因**（lr2e2 workbank k0+k1 共 296 次）：通过 42、流程完整但答案错 103、重复调用→强制
   answer 链 102（answer 阶段 no_tool 被拒 43 次，其中仅 2 次答案正确）、退化复读 20。
   基模主要败在首步长 think 不行动（113）与复读（69）——state 教会了进入工具循环，未教会读对/算对。
6. **语料构成**：630/630 行首动作为 tool_call（0 条直答/追问）、59% 以 `list_files` 起手、中文 prompt 0 条，
   与 bfcl-product 失败形状（首步 `list_files` 仪式、irrelevance/missing 全灭）一一对应。
7. **泄漏范围大于第 1 条所述**：训练集 700 条的 36 个种子（`parent_seed_id`）全部是 workbank 题，
   anchor 分支即原题、b/r/v/x 为其变体。干净 116 题不是种子，但与种子同场景同模板，workbank
   上的增益应视为偏乐观的上界。分集规则与闸门见 [`docs/harness-corpus-render.md`](../../harness-corpus-render.md)。
8. **泄漏分级与干净考卷**（2026-09-24）：700 条相对 36 道种子题——L1 原题 36、L2 逐字复用种子题
   工作区 56、L3 表面相似（`scripts/decontam.py`）113、L4 仅同族改写 495；相对其余 **112 道非种子题**
   仅 1 条专有名弱重叠（0.4）。按 112 题重算 workbank（k0/k1）：none 8/8、lr2e2 16/16、lr3e3 11/11、
   lr1e2f 10/7、lr1e2 9/8、lr5e3 9/13——干净增益约 +8（lr2e2），其余 arm 在 +1~+3 之间。
   此后 workbank 对挂过该语料的模型只按非种子 112 题计分，36 道种子题单列、不作结论。
