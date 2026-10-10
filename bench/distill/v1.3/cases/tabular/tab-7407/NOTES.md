## Traps
- TR-DUPROW: data/workorders.csv 里 9 月高新片区的 3 张工单（QQ-2609100、QQ-2609106、QQ-2609111）被原样重复写入一次，9 月锦江与 8 月也各有一张工单重复（不在本题过滤范围内）。按行数数会得到 18；README 写明工单号唯一标识一张工单，重试把同一张工单原样重复写入，所以答案是 15 张。

## Reference solution
1. 读 README.md：工单号唯一标识一张工单，导出重试导致少数行原样重复。
2. 用 data_query 聚合：{{"path":"data/workorders.csv","filter":{{"片区":"高新","工单月份":"2026-09"}},"operation":"distinct_count","field":"工单号"}}，得 15。
3. 终答只报数字 15。

## Why the answer is unique
decoy 18 把重复行当成不同的工单，但重复行与原行在每个字段上都完全一致，README 又写明工单号唯一标识一张工单，所以不存在把它们当多张工单的读法。8 月的行与高新以外的 9 月行不满足过滤条件。答案只有 15。
