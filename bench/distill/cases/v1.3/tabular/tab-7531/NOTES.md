## Traps
- TR-DECOY: 近名课程 Learn-to-Swim Intensive 与 Learn-to-Swim 并排出现，Intensive 在 8 月的合计为 1813.97，比正确答案更扎眼；题面问的是 Learn-to-Swim 本身，两者是不同课程，按 Intensive 作答不成立。

## Reference solution
1. 查询：{"path":"exports/enrolments_2026-08.csv","filter":{"enrol_month":"2026-08","program":"Learn-to-Swim"},"operation":"sum","field":"fee_gbp"}，得 602.75。
2. 终答只报数字 602.75。

## Why the answer is unique
filter 是精确相等，Learn-to-Swim 不会匹配 Learn-to-Swim Intensive；两列课程名逐行不同，7 月的行被月份条件排除。按题面条件求和只有一种结果，答案唯一为 602.75。
