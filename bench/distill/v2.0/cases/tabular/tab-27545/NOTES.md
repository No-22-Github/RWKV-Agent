## Traps
- TR-NEARNAME（恢复题，恢复行为是考点）: 题面只说「月结派单口径计入城东片区」，表里没有叫「派单片区」或「计费片区」的列，只有一对近名列：服务片区（派单与月结计费口径）与住址片区（客户住址所属片区）。第一次用猜测的列名聚合或过滤会收到 `field "..." is missing` 报错或 matched_rows 0。模型要从报错或空结果恢复：用不带 operation 的 data_query select 列出真实表头（或用预算内最多一次 read_file 看表头），再改用服务片区重查。README 写明月结按服务片区。
- 顺手按住址片区过滤会得到 18 笔；正确答案是按服务片区过滤的 24 笔。

## Reference solution
1. 读 README.md：派单与月结按服务片区，住址片区与派单口径无关。
2. 查询：{"path":"data/workorders_2026-09.csv","filter":{"工单月份":"2026-09","服务片区":"城东"},"operation":"count"}，得 24.0。（若第一次猜错列名报错：先 select 看全部列名，再按本步重查。）
3. 终答只报数字 24.0。

## Why the answer is unique
decoy 18 数的是住址在城东的工单，但 README 写明派单口径按服务片区、住址片区与派单口径无关；两列并不逐行相同。答案唯一为 24.0。
