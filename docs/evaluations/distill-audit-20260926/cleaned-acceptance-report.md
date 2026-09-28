# 离线数据验收报告

版本：`workspace-agent-distill-clean-v1`，2026-09-26。

状态：**offline_data_ready**。表示下列离线导出与回放检查通过，未验证训练收益。本轮不是旧 700 的第二次独立多 Agent 审查；旧审核结论与本轮审核范围分开记录。

| 验收项 | 结果 | 证据 |
|---|---|---|
| 上游冻结文件完整性 | 1794/1794 SHA256 一致 | source-manifest.json |
| 输入逐行去向 | 1586/1586 有决定；无遗漏 | selection-ledger.jsonl |
| 混合导出 | 1011 = train 910 + validation 101 | statistics.json |
| 新增导出 | 460 = train 359 + validation 101；每题一条 | new-only/ |
| 原始正文与掩码保真 | 1011/1011 一致；未改答案 | package-validation.json |
| 新目录二次完整回放 | 1011/1011，拒收 0；token 一致 | fresh-replay.json |
| 新增标量答案 | 377/377：298 数值、79 字符串 | strict-oracle-results.jsonl |
| 新增产物核验 | 9/9；含其他初始文件不变检查 | strict-oracle-results.jsonl |
| 新增脚本执行 | 7/7，在隐藏未来夹具上运行 | strict-oracle-results.jsonl |
| 未知 oracle 不再自动放行 | 数值/字符串/未知形状 3 个负向样例被拒绝 | tooling/strict_oracles.py |
| 专项审阅的能力边界回答 | 28；精确路径白名单 | policy.json |
| 闲聊 | 46；移除 11 条不可靠陈述 | selection-ledger.jsonl |
| 已识别分组跨 split | 0；382 组，33 组锁定训练侧 | split-groups.json |
| 精确重复正文 | 0 | package-validation.json |
| mask/格式/投影一致性 | 通过，损坏正文与越界 mask 两个负向样例被拒绝 | tooling/validate.py |
| 确定性重建 | 20 个数据/账本文件 SHA256 一致 | deterministic-rebuild.json |
| ZIP 异地解压与执行验证 | 通过；全包文件 SHA256 一致 | 交付 ZIP 同目录的 delivery-verification.json |

## 数量与质量口径

新增 460 条中 local 275、web_local 33、write 2、script 7、direct 69、smalltalk 46、refuse 28；共 804,672 World token。混合集共 1,999,562 token；两者最长均 4,091，均满足 <=4096。新增零调用 117/460（25.4%），混合零调用 117/1011（11.6%）。标签并不等于动作计数。

本轮记录了内容筛选、专项审阅和机器核验，不宣称所有答案有独立外部真值证明。386 个 oracle 主要来自题目作者；严格比较解决了未知格式放过和未核对答案的问题，不能从逻辑上消除题目与 oracle 的共同错误。旧 551 条延用历史 Agent 批准并重新回放，旧审核报告完整随包保存。

## 仍需保留的边界

- 双轮澄清未收；本集不能支持“澄清能力已覆盖”的说法。
- 新增写文件/脚本仅 9 条，复杂编辑覆盖主要依赖旧集。
- 旧 551 条均有测试种子来源；包含它们的训练实验须剔除已污染种子评测或单独报告。
- `text-only` 使用全文监督；`loss_spans` 只有被训练器实际读取才生效。
- 真实世界、中文、真实 web 和大仓库迁移未验证；没有 GPU 训练或 student 跑分。
- 老师 API 原始逐路径采样记录没有完整归档，无法独立证明历史模型身份和 pass@3。

具体规则、例外、来源与复现方式见包根目录 `CLEANING.md`、`README.md`。
