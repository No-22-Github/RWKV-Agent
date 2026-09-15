# BFCL v4 A+B Qwen Markdown Baseline 全量诊断

## 结论

Qwen3-8B-FP8 使用 RWKV-Agent Markdown baseline、并发 16、显式 `temperature=0.01` 完成 BFCL v4 A+B 全量 3641 题生成与固定版本官方 evaluator 判分。

- 生成:3641 题,基础设施失败 0,跳过 0,严格解析失败 56
- 耗时:603.35 秒,约 6.03 题/秒
- 正样本:2064/2517,82.00%
- 负样本:115/1124,10.23%
- Prompt/completion tokens:2479061/137089

这是一轮 **baseline 全量诊断**,不是增强档,不能作为 M3 的 Qwen 增强档代表性校准。按规格不报告把正负样本混在一起的总平均。

## 环境

- 模型:`Qwen/Qwen3-8B-FP8`
- 服务:vLLM,FP8,`max_model_len=24576`
- Endpoint:局域网自建 vLLM 服务的 `/v1/chat/completions`
- Transport:`chat-completions-wrapped`
- Chat template thinking:disabled
- 并发:16
- Sampling:greedy语义,`top_k=1`,`effective_temperature=0.01`
- BFCL data commit:`6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`
- Evaluator:`bfcl-eval==2026.3.23`
- Run:`runs/bfcl/qwen-markdown-baseline-full-c16-t001-20260819`

vLLM 会把低于 `0.01` 的 temperature 钳制到 `0.01`;本轮显式传入 `0.01`,因此 `run.json` 与实际生效值一致。并发 32 的 32 题两轮门禁出现 1 题字节翻转;并发 16、显式 `0.01` 的两轮门禁为 32/32 字节一致,所以正式全量采用 16。

## 逐 Split

| Split | 正确/总数 | 准确率 | 解析失败 |
|---|---:|---:|---:|
| `simple_python` | 385/400 | 96.25% | 0 |
| `simple_java` | 52/100 | 52.00% | 13 |
| `simple_javascript` | 35/50 | 70.00% | 1 |
| `multiple` | 194/200 | 97.00% | 0 |
| `parallel` | 178/200 | 89.00% | 3 |
| `parallel_multiple` | 147/200 | 73.50% | 30 |
| `irrelevance` | 65/240 | 27.08% | 0 |
| `live_simple` | 203/258 | 78.68% | 1 |
| `live_multiple` | 825/1053 | 78.35% | 6 |
| `live_parallel` | 11/16 | 68.75% | 0 |
| `live_parallel_multiple` | 18/24 | 75.00% | 1 |
| `live_relevance` | 16/16 | 100.00% | 0 |
| `live_irrelevance` | 50/884 | 5.66% | 1 |

## 主要失败模式

1. **负样本调用偏置。** `irrelevance` 有 175 个 `decoder_success`,`live_irrelevance` 有 834 个。当前 baseline 在所有题末尾预填 `Assistant: ```json`,即使文字要求无相关工具时不调用,生成位置仍强烈暗示必须输出 JSON。负样本低分主要测到了这个 prompt 设计冲突,不能直接解释成模型不会拒调。
2. **并行多调用格式。** `parallel_multiple` 有 30 个严格解析失败,官方判分另有 40 个 wrong-count;说明 JSON 数组协议已打通,但多函数、多调用场景仍是主要格式弱项。
3. **Java 路径。** `simple_java` 有 13 个严格解析失败,另有 13 个 decoder wrong-output-format 和多类值转换错误。当前通用 Java/JS 字符串转换只满足基本契约,还不能视为已完成真实嵌套结构校准。
4. **Live 参数值。** `live_multiple` 的主要错误为 `value_error:string` 114、`value_error:others` 44、wrong function 30、missing optional 24;这部分主要是模型选择和参数值语义,不是基础设施问题。

## 比较边界

- 可以把本轮视为当前 Markdown baseline 在全量数据上的失败分布与吞吐诊断。
- 不得与未来 RWKV 抽样分直接比较;正式横向矩阵必须从同一冻结 manifest 提取 Qwen 子集。
- 不得用本轮触发 manifest v2;M3 预注册要求使用 Qwen3-8B **增强档**全量结果做代表性诊断。
- 本轮不包含 retry、wire compat、渐进式工具暴露或门控,因此不测“兜底的价值”。
