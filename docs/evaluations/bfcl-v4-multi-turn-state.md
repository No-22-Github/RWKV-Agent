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

## 4a. 轮次终结接线与门禁验证

`--finish-tool` 注入 E3 的 `finish_task` 并在每步决策前重述规则。拦截沿用 E3 纪律：只有**纯** `finish_task` 终结本轮，且它绝不进模拟器、绝不进官方 result；与真实调用混合时保留真实调用、不终结（控制工具不能掩盖错误调用）。渲染协议 `bfcl-multi-turn-json-finish-v1`。

单题门禁（`multi_turn_base_0`，`object` 锚点）：

| 模型 | 无 finish-tool | 有 finish-tool | 轮退出 |
|---|---:|---:|---|
| Qwen | 80 调用 | **44** | `finish_task` ×2、`step_limit` ×2 |
| RWKV | 80 调用 | **10** | `finish_task` ×4 |

机制在两个模型上都生效，复读消失。**但 RWKV 出现假阳性**：turn0 是 `cd, cd, finish_task`，而 GT 需要 `cd`+`mkdir`+`mv` —— 没做完就宣布完成。这个方向的错误直接判负，比复读更糟，必须在整体结果里单独量化（对比「挂在第几轮」与 GT 轮数）。

## 4b. 并发执行方式

端点是公司内网、支持高并发，因此 E8 用**单题 CLI × `xargs -P`** 取得并发，不建批量 runner：每题独立进程、独立 sidecar、独立模拟器状态，隔离性强于进程内批量，且天然可重入（worker 跳过已存在目录）。

踩过的坑，重跑时注意：

- 构建**必须** `-tags chatcompletions`，否则 Qwen 路径在发请求前失败。
- 传输参数要写进文件由 worker 读，不能走环境变量或 argv —— `xargs` 命令行会超长，且凭据不该进 argv（只传环境变量**名**）。
- macOS bash 3.2 没有 `mapfile`，用 `while read` 构数组。
- 并发追加同一个 `progress.log` 会丢行，**进度以 `case-*/` 目录数为准**。
- 后台驱动的进程树会被回收，前台分批跑（可重入）更可靠。

## 4c. E8 首个格位结果：Qwen baseline（200 题，已完成）

`multi_turn_base` 全 200 题，`object` 锚点 + `--finish-tool`，baseline 档，并发 16。

产物：`runs/bfcl-mt/e8-qwen-baseline-multi_turn_base-20260821`（每题一个 `case-N/` 子目录）

| 项 | 值 |
|---|---:|
| **官方分（`--partial-eval`）** | **38/200 = 19.00%** |
| 模型调用 | 2639（≈13 次/题） |
| 轮次总数 | 734 |
| **`finish_task` 终结** | **559** |
| `step_limit` 终结 | 28 |
| `parse_error` 终结 | 147 |
| infrastructure 失败 | 0 |

官方失败类型：`instance_state_mismatch` 73、`empty_turn_model_response` 64、`execution_response_mismatch` 25。

**这是本轮最重要的结果，两个维度都变了：**

1. **轮次终结从「完全不存在」变成「主要路径」** —— 734 轮里 559 轮由模型自己终结，撞上限的只有 28。对比修复前：207 轮里 **0** 个自然终结。§6.7 的「挂在第几轮」这个首要诊断指标因此第一次可用。
2. **分数从 10% 到 19%** —— 同锚点、同题集口径下（此前 `object` 无 finish-tool 是 2/20 = 10%），接近翻倍。调用量从 80 次/题降到 13 次/题，约 6 倍。

需要注意的代价与待查项：

- **147 个 parse_error 轮次（占 20%）是 `object` 锚点对 Qwen 的代价** —— 探针 A2 显示 Qwen 在该档首步只有 13/20，而 `array`/`fence` 都是 17/20。锚点是为 RWKV 选的（20/20 vs 12/20），Qwen 在付这个账。若最终只报 RWKV，这个代价可以接受；若要两模型横比，需在报告里明写锚点对 Qwen 不利。
- `empty_turn_model_response` 64 例需要拆开归因：可能来自 parse_error（该轮无产出），也可能来自 `finish_task` 假阳性（未做完就终结）。**两者方向相反，必须分开读**，拆法是比对失败轮次与 GT 轮数。
- 假阳性风险已在 §4a 的 RWKV 单题上观察到，需在全量结果里量化。

## 4d. 未完成的格位

| 格 | 状态 |
|---|---|
| Qwen baseline | ✅ 200/200，19.00% |
| RWKV baseline | ⏸ 最后确认 63/200，进程状态未知（工具通道故障，见下） |
| Qwen enhanced | ❌ 未开始 |
| RWKV enhanced | ❌ 未开始 |

重跑方式（worker 跳过已存在目录，可直接重入）：

```bash
go build -tags chatcompletions -o dist/rwkv-cli ./cmd/rwkv-cli
bash /tmp/e8run.sh rwkv baseline  multi_turn_base 16 e8   # 续跑
bash /tmp/e8run.sh qwen enhanced  multi_turn_base 16 e8
bash /tmp/e8run.sh rwkv enhanced  multi_turn_base 16 e8
bash /tmp/e8score.sh runs/bfcl-mt/<cell-dir> multi_turn_base
```

`/tmp/e8run.sh` 与 `/tmp/e8score.sh` 在 `/tmp`，会被系统清理；若已丢失，按 §4b 的约束重建（参数写文件、`while read` 构数组、进度数目录、前台分批）。**建议下次把这两个脚本移进 `scripts/`**，它们已经是正式产物而不是探针。

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
