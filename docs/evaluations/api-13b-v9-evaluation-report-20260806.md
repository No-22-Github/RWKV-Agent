# RWKV 13.3B 20260806 Harness 修复复测

日期：2026-08-06
模型：`rwkv7-g1i-13.3b-20260805-ctx16384`（与 0805 报告同一模型，未换模型）
Harness：`rwkv-agent-eval-v8` 代码 + 2026-08-06 三项修复，默认 profile，greedy `top_k=1`、
`max_steps=6`、few-shot 关闭
对照：`runs/api-13b-v8-*-20260805-latest/`，同模型、同 profile

## 结论

**模型没变，只修了 Harness 和工具契约，boundary 严格任务从 `8/18` 升到 `10/18`，答案从
`9/18` 升到 `12/18`，工具错误从 29 降到 16。** `assistant` 与 `smoke` 在所有指标上逐项不变，
构成干净对照：改动只移动了它应该移动的东西。

最重要的发现与 A4 原假设相反：**`structured_query` 不是没帮上忙，而是在主动制造错误答案。**
撤掉它之后，`pb_jsonl_event_aggregate` 和 `pb_csv_reconcile_returns` 仅用 `read_file` 就答对了，
连 `calculator` 都没用——模型自己的算术是对的。原先有这个工具时，它给出 `355.72`（应为
`438.72`）和 `$1,499.50`（应为 `1248.50`）。**不合身的工具比没有工具更差。**

两个原先编造答案的 case 现在拿到了真实证据并给出正确事实：`pb_markdown_release_notes` 从
幻觉 `--migration-flag=2.4.0` 变成正确的 `--enable-v2-auth`；`pb_log_incident_root_cause` 从
占位符 `ERROR: service code request_id` 变成三项事实全对。两者仍因严格字符串格式判失败。

## 总分对照

| suite | 指标 | 0805 | 0806 | 变化 |
|---|---|---:|---:|---:|
| boundary | 严格任务 | 8/18 | **10/18** | **+2** |
| boundary | 答案正确 | 9/18 | **12/18** | **+3** |
| boundary | 工具错误 | 29 | **16** | **-45%** |
| boundary | 工具实际执行 | 41 | 45 | +4 |
| boundary | 重复调用 | 13 | 9 | -4 |
| boundary | 被拒调用 | 14 | 9 | -5 |
| boundary | 强制回答 | 16 | 14 | -2 |
| boundary | route / 协议 | 18/18 / 72/73 | 18/18 / 72/73 | 0 |
| boundary | 模型调用 | 91 | 91 | 0 |
| boundary | 墙钟 | 200.5s | 189.4s | -11s |
| assistant | 全部指标 | 1/6, 答案 4/6 | 1/6, 答案 4/6 | **0（对照）** |
| smoke | 全部指标 | 4/10, 答案 11/11 | 4/10, 答案 11/11 | **0（对照）** |

模型调用次数完全相同（91），说明分数变化不是靠多花预算换来的。

## 逐题变化

| case | 0805 | 0806 | 归因 |
|---|---|---|---|
| `pb_csv_sum` | 空答案 | **`42` 通过** | 撤掉 `structured_query`；改用 `read_file -> calculator` |
| `pb_jsonl_event_aggregate` | `5/4/355.72` | **`6/5/438.72` 通过** | 撤掉工具后仅 `read_file`，模型自算正确 |
| `pb_csv_reconcile_returns` | `SKU-17 $1,499.50` | **`SKU-17 1248.50` 通过** | 同上 |
| `pb_missing_file_recover` | 通过 | **失败** | 判分口径：答案仍为正确 `COBALT-7`，但少调 `list_files` |
| `pb_log_incident_root_cause` | 0 次成功，占位答案 | 3 次成功，事实全对 | 路径归一化生效；仍差严格格式 |
| `pb_markdown_release_notes` | 0 次成功，幻觉 flag | 2 次成功，flag 正确 | 路径归一化生效；仍差严格格式 |

## 8 个剩余失败的性质

**判分口径类 4 个（模型事实正确）：**

- `pb_log_incident_root_cause`：`ERROR service=worker request_id=req-8842 code=E_DB_DEADLOCK`
  三项事实全对，要求 `worker E_DB_DEADLOCK req-8842` 的顺序与裸格式。
- `pb_markdown_release_notes`：答案含正确的 `--enable-v2-auth`，但附带说明。
- `pb_config_precedence_resolve`：输出 `API_TIMEOUT=45 RETRIES=3 FEATURE_X=true` 完全正确，
  仅因 rubric 要求必须调用 `search_text` 而失败。0805 报告已标注这是 Harness 口径问题。
- `pb_missing_file_recover`：答案正确，rubric 要求 `list_files`，但模型 `search_text` 一次
  就成功，不再需要那一步。

**真实模型失败 4 个：**

- `pb_long_context_small_need`：两次搜索后放弃，答"未找到"。
- `pb_loc_interest_8_months`：`30.33`，应为 `289.13`。时间段拆解仍然错误。
- `pb_eur_trip_card_vs_fx`：`EUR by 0.00`，应为 `2686.00`。**比 0805 的 `2690.35` 更差**。
- `pb_fx_column_trap`：输出整段推导过程，数值与格式均错。

因此语义口径约为 **14/18 事实正确**，严格口径 **10/18**。两个数都要保留，不能只报一个。

## 必须记录的负面结果

`pb_eur_trip_card_vs_fx` 从 `2690.35`（接近正确值 `2686.00`）退化到 `0.00`。这题的工具轨迹
是 `read_file -> read_file:X`，没有调用 `calculator`。撤掉 `structured_query` 改变了工具清单，
从而改变了每个 case 的 decision prompt；在 greedy 解码下 prompt 变化会改变输出。这是同一
原因既带来 3 个修复、也带来 1 个判分口径回退和 1 个答案退化的两面。

### 该因果链已用受控实验证实（2026-08-06 补）

trace 增加 prompt 记录后，对 `pb_missing_file_recover` 做了单题 A/B：同一模型、同一
profile，唯一差异是工具注册表。

| | 有 `structured_query` | 无（当前代码） |
|---|---|---|
| decision prompt | 2622 字节 | 2263 字节 |
| 工具清单 | 5 个 | 4 个 |
| 首个动作 | `search_text{query:"token", path:"config.yaml", case_sensitive:true}` | `search_text{query:"token", path:".", case_sensitive:false}` |
| 最终答案 | `COBALT-7` | `COBALT-7` |
| 严格判分 | 通过 | 失败（少调 `list_files`） |

两个 prompt 在第 1505 字节处首次分歧，差异正是 `structured_query` 的 359 字节工具说明行。
工具清单以 `Available tools:` 段落渲染进**每一个** decision prompt，因此撤掉一个工具会改变
suite 内所有 case 的 prompt，包括从不调用该工具的 case。

**结论：这不是能力回退，是工具清单变化在 greedy 解码下的轨迹漂移。** 两种配置的答案都正确，
差别只在是否经过 rubric 要求的 `list_files`。原先只能推断的因果链现在是直接证据。

这条实验也说明：**任何改动工具清单的实验都会连带移动无关 case 的分数**，因此单题分数变化
不能直接归因于该工具本身。今后此类改动应同时记录工具清单与 prompt 字节数。

## A4 门槛的当前状态

A4 指定的 5 题：`0/5 -> 2/5`。仍未达到原定 `>=3/5`。

| case | 状态 | 说明 |
|---|---|---|
| `pb_jsonl_event_aggregate` | **通过** | 撤掉工具后模型自算正确 |
| `pb_csv_reconcile_returns` | **通过** | 同上 |
| `pb_loc_interest_8_months` | 失败 | 调用了 `calculator`，但拆解错误 |
| `pb_eur_trip_card_vs_fx` | 失败 | 未调用 `calculator` |
| `pb_fx_column_trap` | 失败 | 未调用 `calculator` |

按 plan 2026-08-06 修订，这 5 题不再是同一门槛集合：通过的 2 题是聚合能力，
失败的 3 题是纯算术。**3 个失败中有 2 个根本没调用 `calculator`。** 因此当前瓶颈不是
「确定性工具算不对」，而是「模型不去用工具，或用了但表达式拆错」。这与 plan 第 2 节
「所有精确执行交给确定性工具」的前提一致，但说明「注册了工具」不等于「模型会用」。

## 判断与下一步优先级

1. **不把这轮记为模型能力提升。** 模型完全没变，提升来自 Harness 与工具契约修复。
2. 撤掉 `structured_query` 的决定被数据支持，且效果强于预期：它不只是不适配，而是在
   制造错误答案。窄工具契约的选择应当保持。
3. 优先补 trace 的 prompt 记录，否则每次工具清单变化导致的 greedy 轨迹漂移都只能靠推断。
4. 严格格式判分是当前最大的分数-语义缺口（4/8 个失败）。需要决定：是训练模型输出裸值，
   还是在 Harness 增加确定性的答案抽取层。这是产品决定，不是 bug。
5. 剩余 3 个算术失败中 2 个没调用 `calculator`。训练优先级应是「该算的时候去调工具」，
   而不是继续加工具。
6. `duplicate_tool_calls` 仍有 9 次，`forced_answers` 仍有 14/18。「证据够了就停」仍未学会，
   与 0805 结论一致。

原始产物：

- `runs/api-13b-v9-boundary-20260806/`
- `runs/api-13b-v9-assistant-20260806/`
- `runs/api-13b-v9-smoke-20260806/`
