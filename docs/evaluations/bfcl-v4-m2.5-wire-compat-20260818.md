# BFCL v4 M2.5 RWKV Wire-Format Compatibility Calibration

日期：2026-08-18（Asia/Shanghai）

## 结论

M2.5 使用 `rwkv-wire-compat-v1` 对 M2 已保存的 400 条原始输出做离线重解析,不重新调用模型。官方 `bfcl-eval==2026.3.23` 成绩由 strict 的 115/400（28.75%）提升到 365/400（91.25%）,增加 250 题、62.50 个百分点。

该结果证明 M2 的主要损失来自 RWKV 输出采用了另一种常见工具调用 wire format,而不是题意与参数理解整体只有三成。M2 strict 分数仍是零容错端到端基线,不得被 M2.5 覆盖。

## 输入证据

- Source run：`runs/bfcl/m2-smoke-20260818`
- Source trace：`runs/bfcl/m2-smoke-20260818/trace.jsonl`
- Source trace SHA-256：`9e58772bf8b9fb534e6294e24d3c668d8c38d5ff3ca414993fed91788cbd8b06`
- 模型：`rwkv7-g1i-7.2b-20260805-ctx16384`
- Split/题量：`simple_python`，400
- 原生成并发：64
- M2.5 新增模型调用：0
- 数据 commit：`6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`
- evaluator：`bfcl-eval==2026.3.23`

## Parser 边界

strict parser 保持不变。`rwkv-wire-compat-v1` 只有 strict 失败后才运行,并且只允许:

1. 把字符串化的 `arguments` 最多解包一层,解包结果必须是单个完整 JSON object。
2. 顶层字段与已选工具参数名精确匹配、且内层无同名字段时,把原值移入 `arguments`。
3. 顶层 `id` 不是工具参数时,作为调用 metadata 丢弃。

函数名修正、参数名/值修正、枚举或类型转换、补参数、删除 schema 参数、prose 截取、单引号修复、截断补全和递归解包全部禁止。parser 不读取 ground truth、`possible_answer/` 或题目 ID 语义。

## 结构修复结果

| 指标 | 数量 |
|---|---:|
| 总题数 | 400 |
| Strict 已接受且结果保持不变 | 125 |
| Compat 修复 | 271 |
| Compat 后仍解析失败 | 4 |
| Compat 后可进入 evaluator | 396 |

| Repair action | 次数 |
|---|---:|
| `arguments_unwrapped` | 271 |
| `call_id_dropped` | 30 |
| `top_level_argument_moved:additional_details` | 1 |
| `top_level_argument_moved:type` | 1 |

125 条 strict 已接受输出在 compat 结果中逐条比较,函数调用 result 零差异。4 条仍失败记录分别为 3 条截断 JSON 和 1 条单引号 JSON,符合禁止修复边界。

## 官方评分

| 模式 | 正确/总数 | 准确率 | 解析失败 |
|---|---:|---:|---:|
| M2 strict | 115/400 | 28.75% | 275 |
| M2.5 compat | 365/400 | 91.25% | 4 |
| Delta | +250 | +62.50 pp | -271 |

271 个修复案例中,250 个经官方 evaluator 判对,21 个仍有语义错误。加上 strict 已解析子集中的 10 个语义错误和 4 个无法解析输出,最终共 35 个失败。

| 剩余错误类型 | 数量 |
|---|---:|
| `value_error:string` | 14 |
| `simple_function_checker:missing_optional` | 4 |
| `simple_function_checker:wrong_count` | 4 |
| `type_error:nested` | 4 |
| `value_error:others` | 4 |
| `value_error:list/tuple` | 3 |
| `type_error:simple` | 1 |
| `value_error:dict_value` | 1 |

Score：`runs/bfcl/m2.5-rwkv-wire-compat-v1-20260818/score/rwkv-agent-bfcl-ab-v1/non_live/BFCL_v4_simple_python_score.json`

## 复现命令

```bash
go run ./cmd/rwkv-cli bfcl-reparse \
  --source runs/bfcl/m2-smoke-20260818 \
  --parser rwkv-wire-compat-v1 \
  --output runs/bfcl/m2.5-rwkv-wire-compat-v1-20260818

./scripts/bfcl.sh evaluate \
  --model rwkv-agent-bfcl-ab-v1 \
  --test-category simple_python \
  --result-dir runs/bfcl/m2.5-rwkv-wire-compat-v1-20260818/result \
  --score-dir runs/bfcl/m2.5-rwkv-wire-compat-v1-20260818/score
```

## 解释边界

- M2.5 测的是同一批原始输出在 parser 层的可恢复增量,不是一次新模型跑分。
- 91.25% 不能替代 28.75%;前者是兼容解析系统分,后者是 strict 零容错系统分。
- 当前 400 题每题只有一个候选工具,因此该结果不能外推到多工具选择、并行调用或完整 Agent 能力。
- M2.5 不是 M4 的第六格。compat 若纳入增强档,必须对 RWKV 与 Qwen Markdown 使用同一代码和配置。
- 在最终 351 题矩阵完成前,不得把本结果表述成 RWKV 与 Qwen 的正式能力对比。
