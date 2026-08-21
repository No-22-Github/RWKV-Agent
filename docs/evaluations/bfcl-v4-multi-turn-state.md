# BFCL v4 多轮：当前状态与 E8 准入

日期：2026-08-21。**本文是多轮实验的当前事实源。**

仓库外的 `RWKV-Agent-BFCL-实验手册-20260821.md` 退役为历史计划文档：它的 E5 阈值口径已废、且未定义多轮锚点与轮次终结（见 §4）。仓库外两份交接与探针报告是过程记录，结论以本文为准。

## 1. 固定环境

| 项 | 值 |
|---|---|
| 数据 commit | `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8` |
| 判分器 | `bfcl-eval==2026.3.23`，`--partial-eval` |
| 判分 handler | `rwkv-agent-bfcl-ab-v1`（decode-only stub） |
| RWKV | `rwkv7-g1i-7.2b-20260805-ctx16384`，`rwkv_lightning` 后端，text stop |
| RWKV 端点 | 公司内网，**支持高并发**（并行 HTTP ≤8 稳定；16–32 有 524 尾部） |
| Qwen | 本地 vLLM `Qwen/Qwen3-8B-FP8`，thinking 全关 |
| 构建 | **必须 `-tags chatcompletions`**，否则 Qwen 路径在发请求前即失败 |

## 2. E0–E7 已得结论

| 实验 | 结果 |
|---|---|
| E0 确定性 | RWKV 20/20 字节一致；Qwen c8 19/20（FP8 底噪，非并发） |
| E1 单轮基线 | RWKV 266/491 = **54.18%**；Qwen 313/491 = **63.75%** |
| E2 单轮增强 | RWKV **54.38%**；Qwen **64.15%**。delta≈0 |
| E3 弃权探针 | `finish_task` 选择率 RWKV **36.39%**、Qwen **55.07%**；有增益，未解决弃权缺陷 |
| E4 上游核对 | 判分语义全部核实；`STATELESS_CLASSES=["MathAPI"]` |
| E5 上下文普查 | v2 渲染：16K **758/800**、8K **736/800** |
| E6 sidecar GT | **200/200**，负向样本正确命中 |
| E7 单题闭环 | 闭环成立，但四格 0/1 测的是格式地板，**已被探针取代** |

单轮两档 delta 接近 0，印证了「单轮是地板、多轮才是重点」这个判断。

## 3. 多轮锚点（探针 A2，20 题首步 strict）

| 锚点 | 预填 | RWKV | Qwen |
|---|---|---:|---:|
| `fence` | ` ```json\n ` | 4/20 | 17/20 |
| `array` | ` ```json\n[ ` | 12/20 | 17/20 |
| `object` | ` ```json\n{"name":" ` | **20/20** | 13/20 |

RWKV 在 `fence`/`array` 的失败是 C1 记录的 `arguments` 字符串化缺陷；锚点伸到 `{"name":"` 才压得掉，与 C1 的 1000 题结论一致。

## 4. 轮次终结：手册最大的缺口，已诊断

**官方退出条件是「模型不发工具调用」**（`base_handler.py:265-293`）：无 `function_call` 时 `model_responses` 变成散文，`decode_execute` 解不出调用 → `is_empty_execute_response` → break。对 chat 模型，写散文就是它说「做完了」的自然方式。框架**没有**要求每步都调用；20 步上限只是保险丝。

我们的协议把这条路关了：prompt 明写「Output JSON only and no prose」，`object` 锚点还让 `[]` 都不可达。实测后果 —— 跨 60 次运行、207 个轮次、两档锚点、两个模型：**`empty_response` 恰好 0**，且换锚点分数不变（`object` 2/20 vs `array` 2/19），`instance_state_mismatch` 都是 12。

**但锚点不是主因。** 单题诊断（base_0 turn 1，GT 已完成）：

| 锚点 | 原样 | 加就近提醒 | 加 `finish_task`+提醒 |
|---|---|---|---|
| `fence` | 又调一次 | **`[]` 终结** | **`[]` 终结** |
| `array` | 又调一次 | `{}]` parse error | **`finish_task` 终结** |
| `object` | 又调一次 | 产出 `[]` 但被锚点拼成 `{"name":"[]` | **`finish_task` 终结** |

三条：

1. `fence` 原样给了完全自由，模型仍然又调一次 → 光开门不够。
2. 同一档只加一句就近提醒，模型立刻输出精确 `[]` → **是我们把终结规则埋在系统前言、离决策点太远，不是模型判断不出来。**
3. `finish_task` 在 `array`/`object` 两档都干净终结，且**与 `object` 锚点兼容**（顺着 `{"name":"` 往下写）。

所以「复读同一调用 20 次」是症状不是病因：没有出口时最省事的动作。给了出口即消失。

这也解开了锚点两难：`object` 的 RWKV 20/20 原本代价是 `[]` 不可达，换 `finish_task` 后代价消失。

## 5. E8 准入门禁

手册没有这两条，必须先过：

- **G1 轮次终结可用** —— 存在模型驱动、可区分的退出，且假阳性（未做完就终结）可测。不过则 §6.7 首要指标「挂在第几轮」是平的。
- **G2 锚点冻结** —— 与 G1 耦合（锚点决定出口可达性），一起定。

## 6. 待拍板（都改变「模型真实成绩」的定义）

1. 「精确重复同一调用」算不算隐式轮次终结、且在 baseline 生效？增强档已如此（成本 80→30 调用，分数不变），放进 baseline 是 harness 启发式进真实成绩口径。
2. OpenAI 式外壳（`{"type":"function","function":{...}}`）要不要进 wire-compat？会扩大增强档修复面，改变两档 delta 含义。

## 7. 已知边界

- `long_context` 2 题 GT 需同工具连跑 31 次，撞 `max-steps 20`，只有并行数组可能完成。照录。
- 渲染含 `initial_config` 的 v1 已废；v2 默认不渲染（官方也不给模型看状态）。成绩不可与公开榜单横比。
- E0 的「逐字节一致」门禁**不适用多轮**（解码长、有状态、首步分叉后全变），多轮确定性需另定口径。
- respond 分支至今零真机覆盖（有单测）。
- 不得向运行时泄露 `possible_answer/`、GT class 或 `path`；`pysidecar/dependency_test.go` 强制。
