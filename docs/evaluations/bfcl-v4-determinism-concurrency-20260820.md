# BFCL v4 确定性归因：并发不是原因，解码长度是

日期：2026-08-20（Asia/Shanghai）

## 结论

**没有观察到并发劣化。** 2026-08-19 记录的「16/32/48 并发结果不同」不是并发度造成的，而是两个独立因素叠加：

1. **主因 —— thinking 让解码变长。** 开启思维链后输出从 p50 36 token 涨到 p50 258 token，把每 token 都存在的 FP8 微小数值扰动积累成必然分叉。关闭 thinking 后，同一服务、同一并发下 result 稳定率从 84/96 升到 95/96。
2. **次因 —— 连续批处理带来固定量级的底噪。** 与并发度**高低无关**，只与「是否发生批处理」有关。并发 1 时完全消失（96/96，3 轮）。

c16 与 c48 的差异经配对检验不显著；把并发从 48 降到 16 不会改善确定性，只会损失吞吐。

## 实验设计

同一批 96 题（`simple_python_0..95`，与 2026-08-19 探针逐 ID 相同）、同一服务实例、`temperature=0`、`max_tokens=4096`。唯一变量是并发度与 thinking 开关。

- Model：`Qwen/Qwen3-8B-FP8`（vLLM，FP8，`max_model_len=24576`，hermes tool parser，`--reasoning-parser qwen3`）
- Endpoint：局域网自建 vLLM 服务的 `/v1/chat/completions`
- Transport：`chat-completions-native-fc`
- Hardware：NVIDIA GeForce RTX 4060 Ti
- 数据 commit：`6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`
- Thinking：`chat_template_kwargs.enable_thinking=false`（逐请求）

重复次数：c1 三轮，c16 六轮，c48 六轮。

## 结果一：thinking 是主因

同为 c16、`temperature=0`、同一批题，仅切换 thinking：

| 配置 | 两轮 result 一致 | 输出 token p50 | p90 |
|---|---:|---:|---:|
| thinking ON（2026-08-19） | 84/96 | 258 | 826 |
| thinking OFF（本轮） | **95/96** | 36 | 47 |

thinking 开启时，**思维链本身的重复一致率只有 12/96**，即约 88% 的题在完全相同的配置下重跑就会分叉。因果链是单向的：

```
reasoning 逐字节相同的 12 题 → result 不同的:  0
reasoning 分叉的      84 题 → result 不同的: 12
```

result 不一致不是独立现象，是思维链分叉的下游后果。分叉形态也符合数值误差累积：`simple_python_10` 两轮前 223 字节逐字节相同，随后在一个语义等价、logit 几乎相等的分支上翻面，而最终 `tool_calls` 完全一致。

按输出长度分桶（thinking ON），长度是唯一有解释力的变量：

| 输出 token | c16 稳定 | c48 稳定 |
|---|---:|---:|
| <200 | 9/23 | 7/24 |
| 200–500 | 3/49 | 3/46 |
| 500+ | **0/24** | **0/26** |

500 token 以上两个并发度都是 0，每个桶内 c16 与 c48 无差别。

## 结果二：并发度不是原因，批处理本身是底噪

关闭 thinking 后，逐并发度重复：

| 并发 | 重复轮数 | 6 轮全稳定题数 | 两两比较 result 不一致率 |
|---|---:|---:|---:|
| 1 | 3 | **96/96** | 0/288 = 0.00% |
| 16 | 6 | 94/96 | 19/1440 = 1.32% |
| 48 | 6 | 93/96 | 23/1440 = 1.60% |

**并发 1 完全确定。** c16 与 c48 的不稳定题几乎是同一批：

| 题 | c1 | c16（6 轮） | c48（6 轮） |
|---|---|---|---|
| `simple_python_80` | 稳定 | 3 种取值 | 3 种取值 |
| `simple_python_86` | 稳定 | 稳定 | 2 种取值 |
| `simple_python_89` | 稳定 | 2 种取值 | 2 种取值 |

配对检验（每题在 6 轮内是否全稳定，c16 对 c48）：`b=1`、`c=0`、`n=1`，**精确二项检验双侧 p = 1.000**。按 2026-08-19 的旧数据（每档 2 轮）做同样检验，`b=13`、`c=10`，**p = 0.678**。两次都远不显著。

所以正确的表述是「**是否批处理**」而不是「**批处理有多大**」。并发从 1 变成 16 引入了全部可观测的不确定性，从 16 再变成 48 没有可测的额外代价。

不稳定的三题都落在同一形态上——参数取值在语义等价的候选间翻面，而非函数名或结构出错：

- `simple_python_80`：`location` 在 `"Manhattan"` / `"Manhattan, New York"` / `"Manhattan, New York City"` / `"Manhattan, City"` 间翻
- `simple_python_86`：仅参数**顺序**不同，语义完全相同（判分不受影响）
- `simple_python_89`：模型输出 `<tool_call>` 块缺一个右花括号，vLLM 的 hermes parser 时而解析成功、时而失败，导致 result 在「有调用」和「空」之间翻

`simple_python_89` 值得单独记一笔：它的输出 token 数在全部 12 轮里恒为 49，但服务端 `finish_reason` 在 `stop` 与 `tool_calls` 之间变化。**这一题的不确定性有一半来自服务端 parser 对残缺 JSON 的容错边界，不是采样。**

## 结果三：吞吐代价

| 并发 | 平均耗时（96 题） | 输出 tok/s | 延迟 p50 |
|---|---:|---:|---:|
| 1 | 116.53s | 30.4 | 1.19s |
| 16 | 9.58s | 370.0 | 1.44s |
| 48 | 4.47s | 792.7 | 1.68s |

用并发 1 换取完全确定性的代价是 **26 倍**耗时（相对 c48）。全量 3641 题按 c1 推算约 74 分钟，按 c48 约 3 分钟。

## 对矩阵的影响

规格 §2.2c 的确定性门禁要求「真实并发度下同一组题跑两遍逐字节相同，不过则整张矩阵作废」。按本轮数据：

- **Markdown baseline 档能过门禁。** 该档 `enable_thinking=false`，实测 c16 下 32/32 逐字节一致（`qwen-markdown-c16-probe-*`、`qwen-markdown-c16-t001-*`）。矩阵主体（5 格中的 4 格）无作废风险。
- **原生 FC 参考格过不了门禁，且调并发无法解决。** 它的不确定性来自 thinking，而 thinking 正是「对照模型最佳形态」的一部分（§2.4）。关掉 thinking 就不再是参考格。

因此参考格需要在规格里显式取得门禁豁免，理由是它不参与 §9.1 的 McNemar 配对检验、只作为上界的单次观测。**这一条必须写进规格，不能让它默默成为门禁的例外。**

## 对既有表述的修正

2026-08-19 的 `docs/evaluations/bfcl-v4-qwen-native-fc-alignment-20260819.md` 写的是「48 并发提升吞吐，但未消除 FP8/vLLM 动态批处理非确定性」。前半句成立，后半句的归因方向错了：它把原因指向动态批处理，而证据指向解码长度。这个区别有实际后果——**若以为是并发，就会去调并发，而调并发没有任何效果（p=1.000）**。

同一份报告的「`temperature=0.01` + 显式 `top_k=1` 没有改善稳定性而且更慢」也不成立。那一轮 c16 跑了 258.6 秒、吞吐 154.9 tok/s，而同配置 c48 是 72.9 秒、507.0 tok/s，相差 3.5 倍。一个吞吐差 3.5 倍的观测里混着服务器状态差异，不能用来判断采样参数。**该结论应撤回，需要时重测。**

以上两处不修改原文件，按 `INDEX.md` 维护规则第 6 条以本条目记录变化。

## 遗留问题

- `simple_python_89` 暴露的服务端 parser 容错边界（残缺 `<tool_call>` JSON 时而被接受）会在负样本判分上产生同类风险，值得单独排查。
- 本轮只在 `simple_python` 96 题上验证。`live_multiple` 等长工具文档 split 的 prefill 分块路径不同，结论未在其上复核。

## 复现命令

```bash
# 每轮换一个 --output；--concurrency 取 1 / 16 / 48
./dist/rwkv-cli bfcl-eval \
  --model Qwen/Qwen3-8B-FP8 \
  --api-url <vllm-endpoint>/v1/chat/completions \
  --tier adapter-health \
  --transport chat-completions-native-fc \
  --split simple_python \
  --case simple_python_0 ... --case simple_python_95 \
  --concurrency 16 \
  --temperature 0 \
  --max-tokens 4096 \
  --case-timeout 10m \
  --chat-template-thinking disabled \
  --output runs/bfcl/qwen-native-nothink-t0-c16-probe-a-20260820
```

产物：`runs/bfcl/qwen-native-nothink-t0-c{1,16,48}-probe-*-20260820`。

本轮为此打开了 `--chat-template-thinking` 在原生 FC transport 上的可用性（此前该 flag 被限制为仅 `chat-completions-wrapped`，导致无法在原生 FC 路径上关闭 thinking）。两条 transport 现在共用同一段 `enable_thinking` 推导逻辑。
