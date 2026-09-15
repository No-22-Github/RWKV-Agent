# G1K wire 消融总结（R0–R4，2026-09-15）

分支 `ablation/g1k-format`。目标：把基于 g1i 设计的对话/调用格式在 G1K 上重估，
买更薄的 harness 和更便宜的语料形状。全程单变量推进、每轮一 commit、无 state、
`--api-stop-tokens none`、bfcl-product 60 题。

## 全轮对比

| 轮 | 配置增量 | task_success | irr | miss | multi | answer | irr 梯度（次/case，首步 tool_call） | 固定前缀 B | 总请求 B | 结论 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R0 | legacy 基线 ×3 | 40/60 | 0/20 | 20/20 | 20/20 | 60/60 | 3.65（20/20） | 1974 | 812924 | 基线 |
| R1 | `align=qwen36` | 41/60 | 1/20 | 20/20 | 20/20 | 60/60 | 2.80（19/20） | 2057 | 792828 | **采纳** |
| R1.5 | +实质性 no-call 示范 | 39/60 | 0/20 | 19/20 | 20/20 | 59/60 | 2.95（20/20） | 2134 | 819033 | 驳回 |
| 出口 | `abstain=no-tool` | 41/60 | 2/20 | 19/20 | 20/20 | 59/60 | 2.65（18/20） | 2287 | 606596 | **采纳** |
| R2 | 砍两条违反训诫 | 40/60 | 1/20 | 19/20 | 20/20 | 59/60 | 2.85（18/20） | 2117 | 593863 | 驳回 |
| R3 | `control=bare` | **49/60** | **12/20** | 18/20 | 19/20 | 56/59 | **0.35（1/20）** | **1776** | **340674** | **采纳** |
| R3' | `control=greeting`（中间态） | 46/60 | 9/20 | 19/20 | 18/20 | 56/59 | 0.60（3/20） | 1853 | 407666 | 备选 |
| R4 | `stages=one` | 49/60 | 12/20 | 18/20 | 19/20 | 56/59 | 0.55（1/20） | 1776 | 360023 | **采纳** |

跨配置比较有 ±1-2 题批推理抖动（同配置确定性：R0 三遍逐题零翻转）。

## 最终配置

```
--profile xml-v1+align-qwen36+no-tool+bare+one-stage
```

对比 R0：**+9 题（40→49）**，irrelevance 0→12/20，首步 tool_call 20/20→1/20，
固定前缀 −198 B，全 run 请求字节 **−56%**（812924→360023）。

## 三条主要教训

1. **示例块是负资产，不是脚手架。** 决策 prompt 里的工具调用示范（"Find files under
   docs → 调工具"）被模型外溢到一切问题上——R0 全部失分的"发明检索任务"形状就是它
   教的。砍掉后 irrelevance 从地板跳到 12/20。这个模型的 in-context 示范通道很重
   （R1.5 加一条同事实示范被扰动 −2、R3 砍示范 +8，方向一致）：**示范必须严格是
   "想要的行为"的样本**。
2. **违反率 ≠ 价值。** "Never invoke tools merely because they are available" 被
   20/20 违反，但同时是出口轮唯一首步弃权 case 的行为锚点（R2 砍掉它该题确定性翻挂）。
   "规则写了但错误照样发生"筛选法会误杀弱锚定训诫。
3. **出口的收益依 regime 而变，最终基座上是第二大杠杆。** 带示例块时（R1 基座）
   分数持平（41→41），只是字节 −23%、forced_answers 54→8；但在 bare 基座上隔离实测
   （`bare+one-stage` 无出口对照）：**34/60 vs 49/60（−15 题）**——multiturn 全灭
   （9/20，10 个 recovery 全挂）、irrelevance 12→7/20、forced_answers 0→31、
   protocol 99.5%→83.2%、stage 88.1%。机制：bare 删掉示范后，`no_tool` 成为目录里
   唯一"非执行动作"的样本，承担全部干净收尾；拿掉后多轮收束 churn 到强制 answer，
   在 answer 位置继续发工具调用（11 次 stage violation）+ think 泄漏翻 4 倍（22 个
   protocol_invalid）。注意反面：boundary 上出口是减分的（报错后被当放弃口）——
   no_tool 是"no-call 型任务的收尾器"，不是万能弃权器。

## 跨套件定音分数卡（同日同端点，G1K）

| 套件（题数） | legacy R0-wire | 最终配置 | Δ | 说明 |
| --- | --- | --- | --- | --- |
| bfcl-product（60） | 40/60 | **49/60** | +9 | 混合负载，irrelevance 驱动 |
| assistant（6） | 1/6 | **3/6** | +2 | 多轮对话+工具 |
| smoke（10） | 2/10 | **4/10** | +2 | 端到端链路 |
| boundary（18） | **4/18** | 0/18 | **−4** | 严格工具序列+精确参数 |

boundary 归因链（逐变量）：legacy 4/18 → `align` 无出口 2/18 → +出口 1/18（8 次
semantic_no_call＝该调工具时弃权）→ +bare 0/18（12 次 direct_final＝凭空作答）。
**结论：最终配置是"弃权友好、示范自由"的形状，在 bfcl-product/assistant/smoke 上全面
占优；boundary 型重工具负载（严格工具序列、精确参数、多步执行）对 G1K 本就最难，
新配置每一项收益在它身上全部反向。生产默认应按负载分流：**

- 混合/含大量无工具需求任务（bfcl-product 形态）：`xml-v1+align-qwen36+no-tool+bare+one-stage`。
- 重工具任务（boundary 形态）：保留示例块、关掉出口的 legacy `xml-v1`（本次 4/18 最好）；
  或等语料把"该调工具就调"训练回来后再重估。

未跑：BFCL 官方 3641 题（仓库外 runner，本次未跑）。

Primitive 两套（fixture 内嵌，`--profile` 不适用——它们跑的是训练期 benchmark
transcript（md-fence+submit），不受本次消融 wire 的影响，是纯模型级数字）：

| 套件（题数） | G1K（2026-09-15） | 历史参照（09-07/09-09，api-7b 基模） |
| --- | --- | --- |
| primitive-orig30（30） | **20/30**（answer 100%，protocol 99.5%） | 18-21/30 |
| primitive-feedback30（30） | **16/30**（protocol 100%） | — |

值得注意：orig30 用的是**训练期 transcript 形状**，G1K 在其上表现正常（20/30、
answer 100%）——与 boundary（产品 XML + 严格工具序列）的挣扎形成对照，进一步支持
"G1K 的工具调用行为强依赖 transcript 形状与任务先验的匹配"这一结论。

## 语料建议（state tuning 的靶子）

格式契约已由 R1/R4 钉死：`System(+<tools> JSON 数组)` / `User` / `Assistant:
<tool_call>{json}</tool_call>` / `User: <tool_response>{json}</tool_response>` /
**纯文本终答（无 `<answer>`、无示例块、单阶段）**。行为靶子按剩余 11 题失分排序：

1. **实质性问题零工具直答**（irrelevance 余 8/20）：需要成规模的"工具目录在场 + 答案
   在脑内 → 直答"正样本；单条 in-context 示范已证不足，要靠训练灌入。
2. **think 泄漏**（bare 下 5 个 `<think>` 循环 → decision_protocol_invalid）：
   thinking=off 语料要钉死"不裸开 `<think>`"。
3. **报错后不弃权**（出口轮 supplied_5）：工具报错 → 重试/作答的区分样本。
4. **终答精度**（56/59）：答案格式与"不复述工具结果"的约束样本。
