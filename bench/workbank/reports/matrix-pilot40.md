# workbank 试点横测报告 v2（bank v3 pilot，40 题，2026-09-17）

> **判决：未过闸（v1）；v2 修复后重测中。** v1 的「过闸带保留项」判决是错的：闸门②（L0≥L1≥L2）在 G1K 上字面不满足（L0 0% < L1 5%），不应被「地板效应」解释掉。本版报告按外部复核意见重写。
>
> 可比键（v1）：bank sha256:a593336b… · harness rwkv-agent-eval-v20 · tool_catalog work-v1（14a3c3d4…）
> v1 跑分配置：RWKV=xml-v1+align-qwen36+no-tool+bare+one-stage（51859aff…），DeepSeek=chat-completions native-chat（bc79a316…）；两配置 v1 均用默认 --max-steps 6 与默认救援参数——**v1 诊断证明该配置结构性地挡死了 ref_calls≥5 的 L2 参考路径（见 §3），v2 起改为 --max-steps 10 --same-tool-rescue-limit 6（可测量性修复，记录在 manifest）**。

## 1. v1 结果（保留存档）

| 配置 | 均值 | 极差 | L0 | L1 | L2 | 闸门② |
|---|---|---|---|---|---|---|
| deepseek-v4-flash | 49.4%（宽松判分 57.5%） | 5.0pp | 97%* | 62.5%* | 25%* | ✅（*去 nt/scr 结构性全灭场景后） |
| rwkv-g1k-7b | 2.5% | 0.0pp | 0% | 5.0% | 0% | ❌ L0<L1 |

## 2. 外部复核修正了 v1 报告的三个错误结论

1. **「2.5% 是能力地板」证据链有三处断口**（复核意见原文）：
   - labels.jsonl 的 45 条标签全部来自 DeepSeek 求解检查轮，G1K 的失败一条未标（已修：v2 补 193 条分层标签，238 总）；
   - 「action not allowed」不是独立失败模式，是 `ErrStageViolation`——answer stage 禁工具而模型仍发调用，属步数耗尽的下游症状（轨迹证实）；
   - GLM 40/40 是剥离 harness 的解题包、DeepSeek 走 native-chat，「xml-v1 wire × 多步文件任务」在 workbank 之前从未被单独验证。
2. **轨迹重读（fs-0001/log-0001/cfg-0001/doc-0001）：真死因不是「开局走偏」，是「收尾不能」。** 四题开局基本正常（fs-0001 step1 干净拿到带大小的清单、cfg-0001 step3 已读到端口），偏离点在证据到手后：模型从不主动停（FM-IGNORE/FM-LOOP，D-003 家族），6 步耗尽被强制 answer 后**仍只会输出 `<tool_call>`**，4/4 死于协议违规。
3. **「primitive transcript 能多步」的对照数据一直存在**：同模型同族 wire，单调用 bfcl-product 49/60 ✅、多步 boundary 3/18（消融期已有，当时误记为「倒退需按负载分流」）、长多步 workbank 1/40。开关在任务结构（多步收尾），且对 wire 变体敏感（boundary 的 thinkfast 变体下模型能在 answer stage 收尾，one-stage 下 4/4 不能）。用户建议的 primitive-orig30×xml-v1 直换实验被双重阻断（CLI guard + primitive 逐题 transcript 钉死），需 harness 使能后才能做；上述三角形是当前可得的替代隔离。

## 3. 六道双零 L2 逐题复核：4 题是题/harness 的错，2 题是模型的错

| 题 | 判定 | 根因 |
|---|---|---|
| cfg-0004 | **case_fault_unreachable** | 参考路径需 4 连读 + 写；`same_tool_rescue_limit=3` 触发后**连 replace_lines 都被禁**，模型从未获得写文件的机会 |
| doc-0004 | **case_fault_unreachable** | 同上；k3 模型已生成**完全正确**的清单全文，仅因无法写盘而 0 分 |
| log-0004 | **case_fault_unreachable** | 模型明确尝试读窗口标记文件，被 3 连读禁用硬拒；只能得 decoy 12 |
| tab-0004 | **case_fault_unreachable** | 模型答 `$23,609.60`——**数值正确且两个陷阱都破解**，判分器拒绝题面从未禁止的货币格式 → v3 已在题面补格式声明句 |
| code-0004 | model_fault | 不读规则文档、直落注册 decoy 10 |
| hyb-0004 | model_fault | 从不尝试 web 工具即答 UNKNOWN（G1K 反证数据可达） |

系统性根因：`--max-steps 6`（5 个工具槽）+ `same_tool_rescue_limit=3`（3 连读禁全部工具）联合杀死所有 ref_calls≥5 的 L2。**v2 跑分配置改为 `--max-steps 10 --same-tool-rescue-limit 6`**——这不是刷分调参：默认参数挡住的是题库自己声明的参考路径，测的是 harness 不是模型。根治性修复（rescue 保留写工具 / per-case max_turns 字段）留待 M4 评估。

## 4. 判分修复（v2 bank 改动，全部过闸）

- **nt 全系去掉 `require_active_no_call`**（native-chat 无 no_tool 出口，DeepSeek 结构性不可能通过，违反协议无关硬规则）→ 改为 `tools:[]` 纯零调用判定。
- **nt-0001 去掉 MiB→MB 单位歧义**（未声明的 L0 陷阱）→ 改同单位换算（9000 MiB/h）。定向重跑显示 DeepSeek 计算正确（9000）但用计算器且带单位——零调用判定在 notool 场景内保留（D-001 家族的克制测量），NOTES 已显式声明。
- **scr-0001 降档**：从「从零写脚本」改为「修现有脚本一行」（v2，分隔符错误），仍 expect.run 判分。定向重跑暴露新的真实失败模式：模型改错了行号（14 vs 17）且改后不验证——L0 的工具机械精度问题，记录在案。
- **tab-0004 v3**：题面补裸小数格式声明句（不带禁词、契约保持逐字节后缀）。

## 5. 宽松判分列（FM-FORMAT 分离，DeepSeek v1 数据）

严格 49.4% → 宽松 57.5%（+8.1pp）。纯格式损失的大户：**tab-0004 0/4→4/4**（值全对）、nt-0003 0/4→4/4（UNKNOWN 诚实出口，判分已修）、nt-0004 0/4→2/4、tab-0001/0002 各 +1。FM-FORMAT 是真实测量轴（契约纪律），但报告必须分列，否则会把「算对答错格式」误读成「不会算」。

## 6. v2 重测结果（--max-steps 10 --same-tool-rescue-limit 6）

（后台运行中，完成后回填）

## 7. 更新后的闸门判定

- 闸门①（极差 ≤5pp）：DeepSeek v1 恰 5.0pp 压线；G1K 0pp。**待 v2 复核。**
- 闸门②（L0≥L1≥L2）：DeepSeek v1 去结构性场景后成立；G1K v1 **不满足（L0 0% < L1 5%）→ 闸门②失败，v1 判「过闸」错误**。v2 待复核。
- 闸门③（无法解释的失败 ≤10%）：满足（GLM 40/40 + 失败分类归档 docs/solve-check-20260917.md）。
- **当前判决：v1 未过闸（闸门②失败 + nt/scr 结构性零分 + L2 四题不可达）。v2 修复判分与跑分配置后重测，以其结果为准。**

## 8. 对缺陷档案的更新建议

- D-003（重复调用直至触顶）：workbank 上跨两 wire 变体复现（workbank 4/4 answer-stage 不收尾 + boundary 重复 calculator），标签已入账，建议升级「候选」。
- **新观察 D-010（建议立项）**：G1K 在工具调用中使用训练残留的绝对路径约定（/home/node/.openclaw/、/workspace/、真实沙箱路径），部分被 harness 的绝对路径候选映射容忍——掩盖了路径纪律缺陷，建议 harness 记录 path-mapping 命中次数。
- answer-stage 收尾失败（one-stage wire 下 4/4、thinkfast 变体下可收尾）：wire×模型交互缺陷，需 primitive×xml 使能实验后才能归属。
