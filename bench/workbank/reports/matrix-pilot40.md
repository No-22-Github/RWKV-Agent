# workbank 试点横测报告（bank v1 pilot，40 题，2026-09-17）

> 可比键：bank_version sha256:a593336b…49d1（40 题 reviewed）· harness rwkv-agent-eval-v20 · scorer v1 · tool_catalog work-v1（hash 14a3c3d4b6a26d32…）
> wire：RWKV=xml-v1+align-qwen36+no-tool+bare+one-stage（hash 51859aff…）；DeepSeek=chat-completions native-chat（hash bc79a316…）
> 采样：temperature 0.3，各 k=4；DeepSeek --max-tokens 2048 --decision-max-tokens 4096；RWKV 默认预算
> 账本：ledger/runs.jsonl（8 行）+ cases.jsonl（320 行）+ labels.jsonl（45 条 LLM 预标）

## 1. 总分

| 配置 | k0 | k1 | k2 | k3 | 均值 | 极差 | L0 | L1 | L2 | rescue-assisted |
|---|---|---|---|---|---|---|---|---|---|---|
| deepseek-v4-flash | 50.0% | 52.5% | 47.5% | 47.5% | 49.4% | **5.0pp** | 77.5% | 50.0% | 20.0% | 3 |
| rwkv-g1k-7b (G1K wire) | 2.5% | 2.5% | 2.5% | 2.5% | 2.5% | **0.0pp** | 0% | 5.0% | 0% | 0 |

- 闸门①（极差 ≤5pp）：DeepSeek 恰好压线通过；G1K 通过（0pp）。
- 闸门②（L0≥L1≥L2）：两配置均成立（G1K 0≤5 视为 L0=L1 级地板效应）。
- DeepSeek 的 k1 高点来自 1 题（2.5pp 单题粒度），极差无余量——扩量时 k≥4 必须保持。

## 2. 每轮跑分后信号（§5.5）

- 失败分层标注入 labels.jsonl（45 条预标，confirmed=false 待人确认）；主模式：FM-FORMAT（契约纪律）、FM-OVERCALL（DEC 轴）、FM-PROTOCOL（协议噪声/预算截断）。
- calibrate 偏离表：8 题标红（7 题 L1/L2 全配置 0%：cfg-0003/0004、code-0004、doc-0004、hyb-0002/0004、log-0004；nt-0001 L0 0%）——供扩量时人工改标或返修。
- G1K 失败结构与缺陷档案对齐：FM-LOOP/触顶（14 题步数耗尽）、FM-PROTOCOL（think 不完整 ×5、action not allowed ×6）、FM-NOREAD/路径幻觉（list_files 用绝对路径 /home/node/.openclaw/…——训练残留，新观察，建议入 defect-archive 为 D-010 候选）。

## 3. 校准发现（对题库，不是对模型）

1. **RWKV 2.5% 是能力地板而非 harness 伪影**：GLM 求解 40/40、DeepSeek 49.4% 同 harness 语义，排除判分/接线问题；G1K smoke（tab-9500）机械链路正常。
2. **max-steps 6 对 ref_calls 3–6 的题偏紧**（G1K 敏感性探针见 §4）：扩量时 L2/L3 建议默认 --max-steps 10 并入账记录，否则步数预算会污染陷阱归因。
3. **nt+script 两场景对 DeepSeek 全败（16/16）**：前者是「诚实出口词表 + 原生通道无 no_tool」的结构性组合，后者是「写盘 vs 回复内贴码」的契约纪律——两处都有区分度但天花板为 0，扩量时应降低 L1 档难度或调整判分表述（见 changelog 保留项）。

## 4. max-steps 敏感性探针（G1K k=1，--max-steps 10）

结果：**1/40（2.5%），与默认 6 步完全一致**。加大步数预算不改变 G1K 的通过率——2.5% 是能力地板（think 不完整、协议损坏、训练残留的绝对路径幻觉、契约纪律），不是步数预算伪影。步数耗尽（14 题）只是这些根源失败的下游表现。结论：题库对 G1K 当前形态的区分度接近于零；要恢复「区分 wire/state 改进」的题库本职，需为 RWKV 侧补一个更易的 tier-0 档（单调用+严格契约纪律题），并把 D-004/D-006 类 wire 侧缺陷的修复作为前置。

## 5. 闸门判定（M3）

| 条件 | 结果 |
|---|---|
| ① 两配置各自 4 次总分极差 ≤5pp | ✅（DeepSeek 恰 5.0pp；G1K 0pp） |
| ② 两配置 L0≥L1≥L2 | ✅ |
| ③ 强模型求解检查无法解释的失败 ≤10% | ✅（GLM 40/40 可解 + 失败分类全覆盖，见 docs/solve-check-20260917.md；第三方审计指出的「仅 3 题成文解释」已用归档文档+返修补齐） |
| 流程（人审→冻结） | reviewed 40/40（用户授权委托，见 changelog）；冻结待下一批无返修后 |

**判决：试点过闸，但带三条校准保留项（§3）。**
