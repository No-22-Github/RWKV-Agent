# G1K wire 消融 07：think-fast 前缀（空 think 仪式）（2026-09-16，驳回）

分支 `ablation/g1k-format`。动机：bare 基座上 think 泄漏是活的失败模式
（`decision_protocol_invalid`；无出口对照里 22 个），而 think-fast 的半开前缀
`<think></think`（XML 路径即 `thinking=fast`，C1 配 `prefill=none`）机制上正好掐死
这条路。g1i（60 题 17/60，md-fence 语境）与 g1j（39→36）各有阴性先验，但 G1K bare
的失败形状可能翻转权衡——实测。

## 轨迹层结论（先读这个）：think 泄漏的真凶是"答案在 think 里 → EOS"训练脚本

对最终配置全部 5 个 `decision_protocol_invalid` case 的逐字节取证（全部
`finish=stop`、446–2369 字符，**远小于 512 决策预算，不是预算截断**）：

- 模型自开 `<think>` 后**真的在推理，且常常算出正确答案**：irrelevance_0 写出
  `area = (10*5)/2 = 25 square meters. We have no tool needed. We can just answer.`；
  irrelevance_7 算出 ∫3x²=124（正确）；irrelevance_11 在 "That's 30. But maybe…"
  里打转 2200 字符。
- 然后模型**不闭合 `</think>` 直接结束生成**——qwen36 训练脚本是
  "空 think → 答案 → EOS"，长推理里一旦产出"像答案的字符串"，行尾 EOS 被错误地
  提前触发（答案还在 think 里）。重试的 Correction 文本会被原样引用进新的 think
  （"…Decide with the evidence you already have instead of reasoning further."），
  再度不闭合而死。
- 更深一层：多处出现**许可寻求**——`But we must follow the instruction: "If new tool
  evidence is needed, output exactly one tool call…"`——模型在 think 里背诵行动契约、
  拿不准"直接回答是否合法"。这是 bare 删示范后的锚定缺口（no_tool 出口部分补偿了它）。
- 推论：这 5 例的推理内容是对的，死在收尾脚本上。**no-think 语料行（thinking=off
  契约）正好重训掉这个 EOS 脚本**；state tuning 后此失败模式应消失。

配置：`xml-v1+align-qwen36+no-tool+bare+one-stage+think-fast`，bfcl-product +
boundary 双验，与最终配置同日对照。

## 结果：双重分离，bfcl 大崩、boundary 小赚

| 指标 | 最终配置 | +think-fast |
| --- | --- | --- |
| bfcl-product | **49/60** | **35/60**（−14） |
| irrelevance | 12/20 | **1/20** |
| **irrelevance 梯度** | **0.55 次/case，首步 tool_call 1/20** | **2.90 次/case，首步 tool_call 19/20** |
| answer_accuracy | 56/59 | 52/59 |
| protocol / stage | 99.5% / 100% | 99.0% / 100% |
| boundary | 0/18 | **3/18**（+3） |
| bfcl outcomes（semantic_no_call / direct_final） | 29 / 34 | 50 / 20 |

## 机制：空 think 仪式是"行动"暗示，不是中性前缀

半开 `<think></think` 在字节上确实掐死了自开 think 截断（协议没有变差），但它把
模型推进"已思考 → 现在行动"的模式：首步 tool_call 从 1/20 拉回 19/20（R0 时代
的失败形状原样复活），探索后在 18 个 no-call 题上用 `no_tool` 收尾
（semantic_no_call 50 vs 29，其中 18 个因先调了工具而判负）——正是出口轮在带示例
基座上见过的"探索后弃权"形状。**空 think 仪式对 G1K 的作用等价于一条隐形的
"先探索再收尾"示范**，与 bare 删示范的方向正好相反；boundary +3 是同一机制在
重工具任务上的镜像收益。

这也解释了两条历史阴性先验：g1j 的 39→36、g1i 的 17/60，都是同一"行动暗示"
在各自题组上的表现。

## 决定

- **驳回**。最终基座维持 `xml-v1+align-qwen36+no-tool+bare+one-stage`
  （thinking=off）。think 泄漏（≈5 个协议失败）的代价远小于仪式的行为代价（−14）。
- **语料契约联动（重要）**：qwen36 语料的空 think 开头不是免费形状。若 state tuning
  保留空 think 开头，推理侧必须配 `thinking=fast` 接住它，且**think 后的内容必须是
  目标行为**（直答或单次工具调用），否则等于给语料加了一条"先探索"暗示范；若坚持
  `thinking=off`（推荐，本消融基座），语料 assistant 轮不得以任何 think 形态开头
  （`docs/corpus-g1k-wire-format.md` §8 已同步实测依据）。
- 产物 `runs/ablation-g1k/thinkfast-{bfcl,boundary}`。
