# v1.3 数据集打包报告（M5）

日期：2026-10-01。产物：`local/runs/distill/dataset-v13/{train,validation}` + `rows-suffixed.jsonl`（含 loss_spans，给 mask 训练用）。

## 管线

1. 全部渲染行合并：b05（1341 distill + 188 base700）+ b06（590）+ b07（234）+ b08 closeout（97）= **2450 行**。
2. `bench/distill/tools/v1.3/build_v13_suffix.py`：每行末尾加 `\n\nUser:`，最后一个 loss span 延长到行尾（照 v1.2 build_v12 的 add_suffix 语义，断言保留：span 有序不重叠、非空、恰为后缀增量）。
3. 打包闸门：`corpus pack --max-tokens 8128 --exclude bench/distill/exclude.jsonl`；**4 行超 8128 硬上限（worst 18238，log-72xx 长日志题）走 exclude 剔除**。
4. 切分：按 case 基 id sha256 % 32 == 0 抽 **81 行（3.3%）作 validation**（held-out，不进 train）；train **2365 行**。

## 打包统计（train 2365 + validation 81 = 2446）

- **token**：p50 1659 / p99 4070 / max 6925；**>4096 token 的行 18/2423 = 0.74%**（目标 ≤15%）；**>8128：0**。
- **zero-call**：598/2365 = 25.3%（目标 22–28%）。
- kind：local 1316 / direct 434 / clarify 146 / refuse 104 / write 100 / web_local 99 / web 91 / smalltalk 87 / script 69。
- 来源：distill-b05 1341 / distill-b06 586 / distill-b07 234 / base700 188 / distill-b08 97。

## §5 目标构成表：目标 vs 实际

| 指标 | v1.3 目标 | 实际 | 判定 |
|---|---|---|---|
| 中文行 | ≥28% | 21.1% | ✗（缺口主因 N5-c 30 / N6-b 20 未出，见下） |
| 多轮行 ≥2 轮 | ~18% | 11.1% | ✗（N3 50 会话全额到货，但 N6 只 20/40） |
| 失败/部分回答如实汇报 | ≥160 行 | N4 94 行 + absent 重解 25 + N10 97 ≈ 216 | ✓ |
| 带「只给答案」模板 | ≤50% | 51.1% | ≈（差 1.1pp，存量 base700/b05 占比高） |
| UNKNOWN 契约 | ≤20% | 22.6% | ✗（存量 406 题删半句后仍有 204 全契约 + base700） |
| 裸 UNKNOWN 终答 | ≤25 且全在带契约题 | **0** | ✓ |
| 收尾恢复行 | ~100 | 98 | ✓ |
| data_query 占调用 | ≥10% | 3.4% | ✗（N11 到货 70 题，但存量调用基数大） |
| 工具目录非整套 | ~40% | 41.2% | ✓ |
| 首动作 list_files | ≤35% | 46.4% | ✗（存量拖累：b05 存量 62%→46%） |
| base700 占比 | ≤11% | 7.7% | ✓ |
| 零调用 | 22–28% | 25.3% | ✓ |
| write+script | ≥12% | 7.0% | ✗（N9 到货但存量占比低） |
| 单行 token | ≤8128 且 >4096 ≤15% | max 6925；0.74% | ✓ |

## 与规划的偏差（已按要求如实报告）

1. **v1.2 mixed（sha256 e33ff905…）与 tooling/build_v12.py 不在这台机器上**：base700 以同 wire_hash 的 base700-v22 渲染重建（670−119 恢复前缀 = 551 口径吻合），字节级复验未能执行。
2. **存量 1529 行 vs 规划 ~990**：v1.2 的行级清理策略不可复现，按 workflow S6 完整重放；比率指标受此拖累。
3. **N5 60/90 题、N6 20/40 会话未出**：批次中段子 Agent 基建故障（工具执行但写盘与结果丢失，多次重试无果），按实际交付收口。
4. 训练侧前置（mask + EOD、新管线重训 v1.2 基线 b00）不在本数据任务范围，§5 验收四套件评测待训练后执行。
