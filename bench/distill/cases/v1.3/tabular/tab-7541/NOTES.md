## Traps
- TR-NEARNAME（恢复题，恢复行为是考点）: 题面只说「月结对账计入城北片区」，表里没有叫「对账片区」的列，只有一对近名列：计费片区（月结对账口径）与行政片区（车辆隶属行政区划）。第一次用猜测的列名聚合或过滤会收到 `field "..." is missing` 报错或 matched_rows 0。模型要从报错或空结果恢复：用不带 operation 的 data_query select 列出真实表头（或用预算内最多一次 read_file 看表头），再改用计费片区重查。README 写明月结对账按计费片区。
- 顺手按行政片区过滤会得到 16 笔；正确答案是按计费片区过滤的 19 笔。

## Reference solution
1. 读 README.md：月结对账按计费片区，行政片区与对账无关。
2. 查询：{"path":"data/dispatch_2026-09.csv","filter":{"派车月份":"2026-09","计费片区":"城北"},"operation":"count"}，得 19.0。（若第一次猜错列名报错：先 select 看全部列名，再按本步重查。）
3. 终答只报数字 19.0。

## Why the answer is unique
decoy 16 数的是行政片区为城北的单，但 README 写明对账按计费片区、行政片区与对账无关；两列并不逐行相同。答案唯一为 19.0。
