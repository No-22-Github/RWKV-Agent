# BFCL v4 E8：Qwen enhanced `multi_turn_base`

评分日期：2026-08-22
生成日期：2026-08-21

## 结论

Qwen3-8B-FP8 在同一 Harness、同一 200 题 `multi_turn_base`、`object` 锚点和
`finish_task` 轮次终结协议下，enhanced 档经固定官方 evaluator 判为：

**57/200 = 28.50%**。

同组 baseline 为 38/200（19.00%），本次观测差值为 **+19 题、+9.50 pp**。
增强档显著减少了空轮和解析终止，但失败重心转向了“实际执行过、最终状态或返回值仍不对”；
因此不能把提升解释成已经解决了多轮任务规划。

| 指标 | Qwen baseline | Qwen enhanced | 变化 |
|---|---:|---:|---:|
| 官方正确 | 38/200 | **57/200** | **+19** |
| 准确率 | 19.00% | **28.50%** | **+9.50 pp** |
| 模型调用 | 2639 | 3599 | +960 |
| 其中 route 调用 | 0 | 1170 | +1170 |
| 执行 step | 2639 | 2429 | -210 |
| `finish_task` 终结 | 559 | 654 | +95 |
| parse-error 终结 | 147 | 7 | -140 |
| step-limit 终结 | 28 | 0 | -28 |
| loop-rescue 终结 | 0 | 61 | +61 |

enhanced 的 3599 次模型调用包含 1170 次路由调用；不能把它与 baseline 的 2639 次执行调用
直接当作同类成本。扣除路由后，enhanced 实际工具决策 step 为 2429，比 baseline 少 210。

## 官方失败分布

| 官方结果 | baseline | enhanced | 变化 |
|---|---:|---:|---:|
| 正确 | 38 | **57** | +19 |
| `instance_state_mismatch` | 73 | **94** | +21 |
| `execution_response_mismatch` | 25 | **36** | +11 |
| `empty_turn_model_response` | 64 | **13** | -51 |

143 个 enhanced 失败中，状态不匹配 94、执行返回不匹配 36、空轮 13。空轮减少 51 题，
但状态/返回类失败合计增加 32 题：增强档主要把失败从“没有形成有效轮次”推进成“进入执行后做错”。

## Harness 干预

enhanced 的 200 题全部触发 route decision。以下同时记录事件总数和至少触发一次的题数；
同一题可触发多次，因此两列不能相加：

| 事件 | 事件数 | 涉及题数 |
|---|---:|---:|
| route retry | 437 | 181 |
| catalog 收窄丢弃 class | 459 | 133 |
| correction retry | 142 | 87 |
| duplicate rejected | 150 | 62 |
| loop rescue | 61 | 52 |
| execution error feedback | 52 | 28 |
| route degraded | 1 | 1 |

734 个轮次的出口为：`finish_task` 654、`loop_rescue` 61、`route_respond` 12、
`parse_error` 7。198/200 题至少选择过一次 `finish_task`。

## 冻结配置与产物

- 数据：BFCL v4 commit `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`
- evaluator：`bfcl-eval==2026.3.23`，`--partial-eval`
- 模型注册名：`Qwen/Qwen3-8B-FP8`
- transport：`chat-completions-wrapped`，thinking disabled，temperature 0
- tier：`enhanced`；parser `rwkv-wire-compat-v1`
- render：`bfcl-multi-turn-json-finish-v1`，`object` anchor，`finish_task` enabled
- 上下文门禁：15360 prompt tokens，最多 1024 output tokens
- 生成源码：commit `2fba06dfc271b4abc41fe3e6adbcdd00ea990628`
- 生成二进制 SHA-256：`aaf77d95ebffd43d6760eb9607c243de179c1b8b90d2d255d1a5f7e93bed9ba0`
- 合并 result SHA-256：`499ce416c15262d08801a89038258a29aec862681759e2e1584a5d06fb87d87e`
- 官方 score JSONL SHA-256：`74bdbbc24a0c8d4a95f42dadd31b38b3cb978edd393f15571aa1f098177d694c`
- 本地完整运行：`runs/bfcl-mt/e8-qwen-enhanced-multi_turn_base-20260821`
- Git 归档：`archive/bfcl-v4-e8-qwen-enhanced-base-20260822/`

归档脚本会验证 200 个 case 的 ID、配置、summary、trace 和 result，再按自然 ID 顺序合并：

```bash
.venv/bin/python scripts/bfcl-mt-archive.py \
  --run-dir runs/bfcl-mt/e8-qwen-enhanced-multi_turn_base-20260821 \
  --split multi_turn_base \
  --expected-count 200 \
  --refresh-archive

./scripts/bfcl.sh evaluate \
  --model rwkv-agent-bfcl-ab-v1 \
  --test-category all \
  --partial-eval \
  --result-dir runs/bfcl-mt/e8-qwen-enhanced-multi_turn_base-20260821/result \
  --score-dir runs/bfcl-mt/e8-qwen-enhanced-multi_turn_base-20260821/score
```

## 边界

- 这是 `multi_turn_base` 全量 200 题，不是四个 multi-turn split 的完整 E8 矩阵。
- `--partial-eval` 输出里的 Base 28.50% 是本格主指标；CSV 的 Multi Turn Overall 7.12%
  把另外三个未跑 split 计入了分母，不可作为本格准确率。
- `object` 锚点是为 RWKV 首步 strict 20/20 选择的；Qwen 探针只有 13/20，横向报告必须注明不利条件。
- Qwen FP8/vLLM 存在已知输出底噪；+9.50 pp 是两次完整系统运行的观测差值，不是冻结同一首答后的纯离线 Harness 因果量。
- `finish_task` 改变了原始 BFCL 的自然终结外壳；baseline/enhanced 本组内一致，但不可直接对齐公开榜单。
