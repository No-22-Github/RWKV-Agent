## Traps
- TR-DECOY: 近名套餐 Corporate Standard Plus 在 8 月的平均单据金额为 267.86，与 Corporate Standard 并排出现；两者是不同套餐，精确相等过滤下 Plus 不会混入，按 Plus 作答不成立。

## Reference solution
1. 查询：{"path":"data/reports_2026-08.csv","filter":{"report_month":"2026-08","plan":"Corporate Standard"},"operation":"avg","field":"bill_gbp"}，得 146.31。
2. 终答只报数字 146.31。

## Why the answer is unique
平均只对 8 月 Corporate Standard 的行成立，行集合被精确相等过滤唯一确定；7 月的行与 Plus 的行都被排除。答案唯一为 146.31。
