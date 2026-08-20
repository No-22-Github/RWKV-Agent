# 预填锚点的位置决定 strict 分数 —— 兜底增益可被锚点位置替代

日期：2026-08-20（Asia/Shanghai）
模型：`rwkv7-g1i-7.2b-20260805-ctx16384`
判分：官方 `bfcl-eval==2026.3.23`，数据 commit `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`

## 结论

把预填锚点从 ` ```json ` 延长到 `{"name":"`（并行类别用 `[{"name":"`），non-live 四个 split 共 1000 题的 **strict 分数从 51.10% 升到 88.90%**，超过了当前带 `rwkv-wire-compat-v1` 兜底的 88.00%。

这意味着 M2.5 记录的那 63 个百分点兜底增益，**主要是锚点位置没选对的补偿，而不是模型能力缺口**。

两条通用结论：

1. **约束要卡在结构边界，不能卡进结构内部。** 预填到 `"arguments":{` 会让模型立刻闭合花括号，398/400 输出空参数。
2. **单调用与并行调用需要不同的锚点形状。** 单对象锚点会让并行题归零。

## 逐 split 结果

| split | n | 现状（仅围栏） | 现状+兜底 | `{"name":"` | `[{"name":"` |
|---|---:|---:|---:|---:|---:|
| `simple_python` | 400 | 28.75% | 91.25% | **93.25%** | — |
| `multiple` | 200 | 30.00% | 89.50% | **89.50%** | 88.50% |
| `parallel` | 200 | 88.00% | 88.00% | **0.00%** | **88.00%** |
| `parallel_multiple` | 200 | 80.00% | 80.00% | **0.00%** | **80.50%** |

按类别选择锚点后的合计（strict，无兜底）：

| 方案 | 1000 题 strict |
|---|---:|
| 现状 strict | 511/1000 = **51.10%** |
| 现状 + `rwkv-wire-compat-v1` | 880/1000 = 88.00% |
| **按类别选锚点，strict** | **889/1000 = 88.90%** |

`{"name":"` 与 `[{"name":"` 两档下 `arguments` 字符串化均为 **0**（1000 题全覆盖），strict 与 compat 同分，兜底解析器一次未触发。

## 为什么 `"arguments":{` 不行

预填到 `arguments` 的开花括号，模型的最省事补完就是立刻闭合：

```
{"name":"calculate_triangle_area","arguments":{}}
{"name":"math.factorial","arguments":{}}
```

**398/400 参数为空。** 已排除 stop token 截断：去掉 ` ``` ` stop 后输出为 `}}\n``` `，是模型自己写完的。

推测原因与既有观察一致 —— 模型对锚点的响应是「补完这个结构」而非「理解结构语义」。锚点停在 `{` 处，最短的合法补完就是 `}`。

停在 `{"name":"` 则同时做到两件事：锁定顶层结构（不可能再出现自造的 `id` 字段或 OpenAI 式 `type`/`function` 嵌套），同时把 `arguments` 整体留给模型按训练时见过的形态一次性生成。

参考项目的锚点位置与此吻合：`123123213weqw/rwkv-agent` 预填 `<tool_call>{"name":"`（`crates/agent-core/src/protocol.rs:17`），RWKV-LH 预填到 `{`。四个调研过的项目中没有一个预填进 `arguments` 内部。

## 为什么并行题需要数组锚点

`parallel` / `parallel_multiple` 在 `{"name":"` 下判 0，但并非解析失败 —— 分别有 140 和 132 条解析成功，只是**只含一个调用**，被判 `wrong_count`。单对象锚点物理上排除了数组形状。

改用 `[{"name":"` 后回到 88.00% / 80.50%，与现状持平（`parallel_multiple` 微涨 0.5pp）。

值得注意：并行两个 split 在现状下的字符串化本来就很少（3/200、2/200），所以它们的 strict 分数（88.00% / 80.00%）本来就不低，锚点延长在这里主要是保持而非提升。**该改动的收益集中在 `simple_python` 与 `multiple`** —— 这两个 split 的现状字符串化分别是 271/400 与 133/200。

## 落地方式

渲染器已按并行与否分支（`internal/bfcl/markdown.go:79-87` 依 `strings.Contains(entry.Category, "parallel")` 选择数组或单对象的指令文本），因此只需把同一分支延伸到预填字符串，不新增判断逻辑：

```
parallel / parallel_multiple  →  Assistant: ```json\n[{"name":"
其余                          →  Assistant: ```json\n{"name":"
```

按规格 §12，渲染变更属 **major**，7.2b 的 M2（strict 28.75%）与 M2.5（compat 91.25%）基线与新渲染不可比，需重跑并以新条目记录，不覆盖旧值。

**本轮未改动生产代码**，全部数据来自探针脚本，其渲染前缀已验证与生产渲染器逐字节一致。

## 限制

- **这是 harness 侧的约束补偿，不是模型缺陷被修复。** 模型「把 `arguments` 写成转义字符串」的倾向仍然存在，在模型自主开标签（不预填）的场景下会复现。数据侧的成因仍需排查，见 [`rwkv-g1i-toolcall-abstention-defect-20260820.md`](rwkv-g1i-toolcall-abstention-defect-20260820.md) 附带发现一。
- **只测了 7.2b、只测了 non-live 四个 split（1000 题）。** 全部 `live_*` 未测；`live_multiple` 最多 37 个工具，长工具表下行为未知。13.3b 未测，其 Markdown 下字符串化本就为 0/400，预期收益小。
- **负样本预期变差且未测。** `{"name":"` 的约束强于围栏，弃权只会更难；`irrelevance` / `live_irrelevance` 本轮未跑。该改动是用负样本换正样本与零兜底，方向明确但幅度未量化。
- 表中 `none` 列的 strict 值即 M2 基线口径；`现状+兜底` 列为 `rwkv-wire-compat-v1`。两列与新锚点列使用同一批渲染字节，仅锚点后缀不同。
