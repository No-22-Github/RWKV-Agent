## Traps
- TR-DECOY: 套餐名近名，Commute Plus 在 9 月的电量合计为 1247.90，比 Commute 本身更大更醒目；filter 精确相等时 Commute 不匹配 Commute Plus，两档是不同资费，按 Plus 作答不成立。

## Reference solution
1. 查询：{"path":"data/sessions_2026-09.csv","filter":{"session_month":"2026-09","plan":"Commute"},"operation":"sum","field":"kwh_delivered"}，得 458.40。
2. 终答只报数字 458.40。

## Why the answer is unique
两档套餐名逐行不同，精确相等过滤下 Commute 的合计只有一种；8 月与 9 月外的行被月份条件排除。答案唯一为 458.40。
