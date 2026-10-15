## Traps
- TR-DUPROW: 导出里有 2 行与前面完全相同的重复行(林晓的)，不去重得 125.5。
- TR-DATEFMT 类干扰: 文件含 8 月下旬的行，全部相加得 169.0。

## Reference solution
1. 读文件；2. 过滤林晓、日期 2026-09、去掉完全相同的重复行后求和 = 109.5。

## Why the answer is unique
同一天同人同工时的整行重复是导出故障，只计一次；总和 109.5。

EXAM-CANARY-ad013461
