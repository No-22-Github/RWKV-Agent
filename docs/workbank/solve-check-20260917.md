# 试点求解检查归档（M3 §3 步骤 6，2026-09-17）

三路独立证据 + 每类失败的去向。目的：满足「强模型求解检查无法解释的失败 ≤10%」闸门的证据要求。

## 证据来源

1. **GLM 子 Agent 求解（40/40 可解）**：40 个净化解题包（剥离 NOTES/expect，web fixture 物化为本地页面）由 10 个独立解题 Agent 作答。全部 40 题答案值正确或文件态正确；未出现「答案不唯一」except code-0002（见下）。原始答案：/tmp/wb-solve/<id>/ANSWER.txt。
2. **DeepSeek k=2 经 agent-eval**（runs/workbank/deepseek-solve-k0/k1）：harness 路径第二来源，15/40 与 13/40。
3. **复核审查**（10 个审查员全审 40 题）：36 pass / 4 fix，返修全部落地。

## 失败分类与解释（GLM/DeepSeek 联合）

| 失败类 | 题数 | 解释 / 去向 |
|---|---|---|
| code-0002 汇总行歧义 | 1 题 | **真缺陷**：答案存在两种合理解读 → 已返修（题面声明 paste 为完整输出），NOTES 留痕。修复后唯一性由复核确认 |
| nt-0003/0004 诚实出口语义 | 2 题 | **判分设计缺陷**：契约的 UNKNOWN 出口与拒绝词表判分冲突 → 已返修（UNKNOWN/拒绝语均为通过通道；decoy 改为假装成功），NOTES 留痕 |
| DeepSeek decision 预算截断（runner error: output token limit） | k1 达 14 题次 | **跑分配置伪影**：DeepSeek reasoning tokens 计入 max_tokens，默认预算不足 → 终局 k=4 已用 --decision-max-tokens 4096；该失败类与题目无关 |
| DeepSeek function-call 参数非 JSON（FM-PROTOCOL） | 每轮 1-3 题 | **真实模型行为**（协议噪声）：ledger protocol_invalid_rate 已捕获；属于被测能力，不是题目缺陷 |
| nt 题无调用语义（DeepSeek 协议损坏/直接调用） | 4 题 | **真实 DEC 轴行为**：OpenAI 原生通道没有 G1K 的 no_tool 出口，DeepSeek 试图调用→判 fail 正确 |
| scr 题模型脚本未落盘/贴在回复里 | DeepSeek 全败主因 | **真实行为**：写文件/写脚本题要求 workspace 落盘，回复里贴代码不算完成——DONE 契约语义正确 |
| tab-0004 旧 decoy 不可推导 | 1 题 | 复核发现 → 已返修（decoy 重算为 1217.36） |

**未解释失败 = 0**。GLM 求解 40/40 正确 + 上述分类覆盖 DeepSeek k=2 全部失败类；3 题返修后（code-0002、nt-0003、nt-0004）自动闸门全绿。残余风险：solve-check 的 DeepSeek 通道在返修题上未重跑 k=2（终局 k=4 已含返修后题集，其 per-case 结果即回归证据）。
