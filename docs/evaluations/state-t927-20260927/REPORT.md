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
4. **直答→复读→答错的形态迁移**（详见 §5/§6）：state 把基模 83 题"不调工具直答"压到 5 题，
   代价是中段 checkpoint 复读海啸（s158 forced 93 题），到 s316 稳定在 48；剩余主桶是
   "走完流程答错"（s316 79 题），**但其中 25 题并非算错，而是终答违反 answer 契约被 harness 判死**，
   且至少 6 题答案内容本身正确——"答对了没收住"成了新的最大失分点（§6 深挖）。
5. 显著性提示：+15/−8 单副本符号检验 one-sided p=0.105（two-sided 0.210），方向明确但未过 0.05 线。
   如需硬结论可对 s316 + none 各补 2 副本（未预注册，未执行）。

## 1. 可比性与有效性

| 项 | 值 |
|---|---|
| 模型 / 端点 | `rwkv-g1k-7b-temp-3601` @ api-7b.rwkvos.com，albatross-1.3.0，hard_max_bsz 169；跑前/跑后快照模型 id 一致（`runs/bench-20260927-t927/endpoint-*.json`） |
| 分支 / 提交 | `distill/workflow-spec` @ `d5164cd`，工作区干净 |
| 二进制 | `bin/rwkv-cli`（HEAD `d5164cd` 构建，sha256 `3c2e16fa…9845e`），`bin/rwkv-lab bench sweep --state-id` |
| 格式 | `--profile g1k --strict-spec` |
| 采样 | `g1k-agent`（T 0.3 · top_p 0.5 · top_k 65536 · 双 penalty 0），固定不扫——隔离 checkpoint 变量；复读只由协议层 `duplicate_reject` 治理，解码层无惩罚 |
| 预算 | `--max-steps 16 --max-tokens 4096 --decision-max-tokens 2048 --case-timeout 30m`；`--remote-batch-wait 0s` |
| 并发 | 每套件硬编码 workbank 48 + bfclp 16（合计 64）。本轮应用户要求传 `--max-concurrency 96`，**实际未生效**（sweep 的套件并行度不随预算缩放，跑完已修复），真实在飞 64 |
| 耗时 | 每 arm 两套件并行 545–1105 s（约 9–18 分钟），7 arm 串行总量 ≈102 分钟 |
| workbank | 148 题含 draft，case 源 sha256 `2d9193e4…ef98f`；bfcl-product 60 题 |
| 有效性 | **14/14 run 一次过闸门**，invalid 0，infra_errors 0，无重跑 |

## 2. Arms 与主矩阵（strict，k=1）

| arm | state_id | 源文件 | workbank /148 | bfcl-product /60 | 耗时 |
|---|---|---|---|---|---|
| none | （不挂 state） | – | 9 | **47** | 617s |
| s79 | `t927-s79.pth` | state-step-00000079.pth | 5 | 34 | 545s |
| s158 | `t927-s158.pth` | state-step-00000158.pth | 8 | 14 | 927s |
| s237 | `t927-s237.pth` | state-step-00000237.pth | 11 | 24 | 1052s |
| **s316** | `t927-s316.pth` | state-step-00000316.pth | **16** | 26 | 784s |
| s395 | `t927-s395.pth` | state-step-00000395.pth | 12 | 11 | 1105s |
| fin | `t927-fin.pth` | state-final.pth | 12 | 21 | 1070s |

语料：用户 2026-09-27 交付 train-9-27.tar.gz（`train-1-1/lr2e-2/`，lr 2e-2，约 1000 条出头的蒸馏语料），
6 个 checkpoint（间隔 79 步）。上传端点 state_id = 短名文件名。

协议质量随训练单调改善（workbank，per-step）：

| 指标 | none | s79 | s158 | s237 | s316 | s395 | fin |
|---|---|---|---|---|---|---|---|
| protocol_validity | 367/503 | 503/619 | 1000/1183 | 797/929 | 734/839 | 834/967 | 805/919 |
| required_tool_completion | 6/16 | 7/16 | **16/16** | 11/16 | **16/16** | **16/16** | 15/16 |

"该调的工具链走完"从基模 6/16 提到 state 的 16/16——语料把"进入并走完工具循环"教会了，
这一点与 09-24 轮一致且更彻底。

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
代价是 notool 8→1（弃权被洗，与 09-24 轮同形状）。tabular 仍是全 arm 重灾区
（基模复读桶 12/20、state 侧最高只摸到 1）。

## 4. 配对翻转与显著性（对照 none，逐题）

workbank（符号检验，单副本）：

| arm | +翻正 | −翻负 | n | one-sided p |
|---|---|---|---|---|
| s79 | +4 | −8 | 12 | 0.194 |
| s158 | +8 | −9 | 17 | 0.500 |
| s237 | +10 | −8 | 18 | 0.407 |
| **s316** | **+15** | −8 | 23 | **0.105** |
| s395 | +12 | −9 | 21 | 0.332 |
| fin | +11 | −8 | 19 | 0.324 |

bfcl-product（同为对照 none）：s79 +7/−20、s158 +3/−36、s237 +5/−28、s316 +7/−28、
**s395 +0/−36**、fin +3/−32。s395 在 bfcl 上是灾难性的（一题没赚、丢 36 题），与其 workbank
回落同相——训过头主要表现在弃权进一步塌方，而 workbank 工具收益并未跟上。

解读：六个 checkpoint 的 workbank 翻转全部是净正，但绝对幅度（+4~+15）在单副本下都不足
0.05 显著线；净增益最大、翻正最多的 s316 是唯一接近显著的点。净损失的贡献主要来自 notool
（−7）与 web-0015 这类基模侥幸题；净增益集中在 web/script/config/docs。

## 5. 失败形态迁移（workbank，题数）

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

形态读法：训练先把"直答"换成"进循环"（s79 直答 44 剩、tools_wrong 涨到 33——开始动手但还不会做），
中段被复读海啸主导（s158 forced 93），后半段复读收敛（48）而"走完答错"成为主桶（79）。
**注意"走完答错"不是单一形态**，§6 把它拆开。

## 6. 终答契约拒绝深挖（s316 的 79 题"走完答错"）

s316 的 79 题"走完流程答错"里，有 **25 题的终答不是模型答案，而是 harness 的答案契约拒绝语**
（"I could not provide a reliable answer because the model output violated the answer contract.
Please retry."）。逐案看最后一步的原始输出，分两种形态：

**A. ✿ 分段续写（12/25）**——模型答出答案后不停止，紧接着生成语料分段符 `✿` 与下一段
User 提示词的续写，整段被判违例。例：cfg-0001 第 4 步输出
`8431✿text2✿User: The ledger service is being moved behind a new load balancer…`——
**8431 正确**（期望值就是它），因为没停被判死。

**B. answer 槽位污染（13/25）**——终答位置输出的不是答案：回显 `<tool_response>{…}` 片段
（code-0004/0011）、复读 harness 的 reminder 文本（cfg-0012 "…and the Tool results above to
continue t"）、复读退化为语料残余（cfg-0013 "Tool: the Tool / Never: / The Tool:"）、
或在 answer 里重新发起 `<tool_call>`（doc-0012）。

对 A+B 中可机械判分的 18 题（expected_number/output_equals 两类契约），**6 题被拒前的
答案内容本身正确**（cfg-0001 8431、fs-0003 4417、fs-0009 telemetry/gateway.yaml、code-0005
passed 等），另有 7 题契约类型超出简易判分无法判定。被拒后所有 case 直接以拒绝语作终答结束，
未出现第二次有效终答。

**训练侧含义（下一轮语料的最直接抓手）**：语料目前教会了"产出答案"，没教会"答案之后 EOS 停止、
answer 槽位只放答案"。补"终答即停"的样本密度（答案后无后续段落、不回显 tool_response、
不复读 reminder），§6 这 25 题里可判正确的 6 题起就是白捡的分，且 s395/fin 同桶 17/20 题同理。

## 7. bfcl-product 按类别（passed/n）

| 类别 | n | none | s79 | s158 | s237 | s316 | s395 | fin |
|---|---|---|---|---|---|---|---|---|
| irrelevance（不该调） | 20 | **14** | 8 | 1 | 3 | 3 | 1 | 5 |
| missing-required（该追问） | 20 | 16 | 14 | 12 | 16 | **17** | 10 | 15 |
| multiturn | 20 | **17** | 12 | 1 | 5 | 6 | 0 | 1 |

missing-required 全 state 均值 14.0，s316 反超基线 1 题——本语料的 clarify 行为迁移成功；
irrelevance/multiturn 仍是 state 的固定失血点。

## 8. 泄漏口径

t927 语料为蒸馏管线自产题目（非 workbank 种子衍生），b01–b03 各批入库前均过管线自带
decontam 闸门（对 workbank 全量最近邻相似度打分，flagged 即下架；b03 抽样相似度 ≤0.04，
shelved 216/422/614 条见 `runs/distill/b0*/decontam-*.jsonl`）。故本轮按 148 题全量计分为主口径，
不适用 09-24 轮的"非种子 112 题"规则。

## 9. 训练侧解读与下一轮语料目标

**checkpoint 相位读法**（6 个点连成的曲线）：

- s79（1/5 训程）：半吊子状态——notool 已开始被洗（8→2）但工具循环还不稳（tools_wrong 33、
  复读 66），两套件双输（workbank −4、bfcl −13）。
- s158（2/5）：工具循环成型（rtc 16/16、直答几乎归零），但复读海啸最凶（forced 93、bfcl 14）。
- s237（3/5）：复读收敛中（68），workbank 开始反超基线（11）。
- **s316（4/5）：复读稳定（48）+ 场景铺开（7 类增益）+ missing-required 反超——峰值点。**
- s395 / fin（5/5 与收尾）：workbank 回落 4 题、bfcl 崩到 11（+0/−36）——过训的表现是弃权
  进一步塌方而非工具能力继续涨。

**下一轮语料的四个可动目标**（按预期收益排序）：

1. **终答即停 + answer 槽位纯度**（§6）：25 题（s395/fin 同桶 17/20 题）里至少 6 题白丢；
2. **tabular/logs 的复读治理**：两场景是 forced 桶重灾区（12/20、9/17），
   `g1k-agent-fast` 的抑复读惩罚未交叉测试，也值得一跑；
3. **读对/算对**（54 题真答错）：语料要教"把工具结果转成正确答案"，09-24 轮同一结论；
4. **notool 负样本保弃权**：12 题 8→1，若想 workbank/bfcl 两端兼得，这桶必须止住。

## 10. 局限

- **k=1 单副本**：s316 vs none 符号检验 one-sided p=0.105，未过 0.05；结论方向明确（配对 +15/−8），
  如需硬显著性对 s316 + none 各补 2 副本即可（~50 分钟）。
- **并发未生效**：`--max-concurrency 96` 因 sweep 套件并行度硬编码（48/16）而无效果，
  实际在飞 64；本轮跑完后已修复（套件并行度随预算比例缩放，预算 ≤ spec 之和时行为不变）。
- state × 采样档未交叉（`g1k-agent-fast` 的抑复读惩罚对 s158 型复读海啸可能有直接收益，未测）。
- §6 的契约判分只覆盖 expected_number/output_equals 两类，6/25 之外可能还有被拒的正确答案。
- smoke 未单独跑；state 生效的 trace 证据由 workbank 直答/复读形态迁移间接确认。

## 11. 复现

```bash
go build -o bin/rwkv-cli ./cmd/rwkv-cli && go build -o bin/rwkv-lab ./cmd/rwkv-lab
export RWKV_CF_ID=… RWKV_CF_SECRET=…
# 每 arm 一次调用（state 换 t927-{s79,s158,s237,s316,s395,fin}.pth；none 去掉 --state-id）
bin/rwkv-lab bench sweep --out runs/bench-20260927-t927 --arms g1k-agent \
  --suites workbank,bfcl-product --k 0 --state-id t927-s316.pth \
  --prefix s316 --max-concurrency 96
```

run 数据在 `runs/bench-20260927-t927/`（不入库；已另打包轨迹供离线查阅）；state 文件在
`/home/no22/states/upload/`（不入库）。
