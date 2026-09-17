# workbank changelog

## 2026-09-17 (pilot batch, 40 cases)

- 起草：10 个场景子 Agent 各 4 题（L0/L1/L1/L2），家族 fam-<scenario>-<slug>-01；author=llm:glm-drafter。
- 求解检查：GLM 子 Agent 40/40 可解 + DeepSeek 经 agent-eval k=2 双来源；发现 code-0002 答案不唯一、nt-0003/0004 判分与诚实出口冲突，均返修（见 docs/solve-check-20260917.md）。
- 复核：10 个审查 Agent 全审，36 pass / 4 fix；tab-0004 decoy 重算、cfg-0003 verify.py 死代码、nt-0003/0004 词表与 NOTES 同步，返修落地后自动闸门全绿。
- 第三方审计（评测子 Agent）：发现 canary 仅覆盖 case.json → 已补齐 NOTES.md/verify.py；verify_all 对 expect.run 形态空转 → 已加 run_expect_match 检查；tab-0004 NOTES 残留旧值 → 已修。
- **status 变更授权记录**：用户于 2026-09-17 明示「我不会 review 你 40 题，你自行判决」，据此由主 Agent 依据复核报告 + 第三方审计将 40 题置 reviewed（reviewer=human:delegated-20260917）。冻结（frozen）待下一批扩量时本批无返修再执行。
- 已知保留项（不阻断试点）：web/nt 题 sabotage 测试因无 files 可破坏而跳过（web 由 hitcheck 兜底）；每 scenario 单 family（10 簇）使 family 重采样 CI 粒度粗——M4 扩量时每 scenario 至少 2 个 family；nt-0001 对 DeepSeek 的 units 假阴性依赖严格契约，扩量时审视。

## 2026-09-17 (v2 — 外部复核驱动的修正)

- 判决修正：v1「过闸带保留项」→ **未过闸**（闸门②在 G1K 上字面失败 L0 0% < L1 5%；nt/scr 结构性零分；6 道双零 L2 中 4 题不可达）。
- nt 全系去 require_active_no_call → 零调用判定（协议无关）；nt-0001 去单位歧义（v2）。
- scr-0001 降档为修一行（v2）。
- tab-0004 补裸小数格式声明（v3）。
- 跑分配置 v2：--max-steps 10 --same-tool-rescue-limit 6（可测量性修复：默认参数挡死 ref_calls≥5 的 L2 参考路径，证据见 reports/matrix-pilot40.md §3）。
- G1K 分层补标签 193 条；6 道双零 L2 逐题复核归档（4 case_fault / 2 model_fault）。
