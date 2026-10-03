## Traps
- TR-RULEFILE: 可抵扣比例只写在 README（报销金额 × 94%）。不读 README 直接报市场部合计 28730.31 就错了。

## Reference solution
1. 读 README.md：可抵扣 = 报销金额 × 94%。
2. data_query：差旅/2026-09-报销.csv，filter {"部门":"市场部"}，sum 金额 → 28730.31。
3. calculator：28730.31 * 0.94，precision 2 → 27006.49。
终答一句话：市场部 9 月报销合计 28730.31 元，按 94% 可抵扣口径为 27006.49 元。判据：包含 27006.49（可去尾零/带千分位），调用过 calculator。

## Why the answer is unique
部门过滤精确，比例由 README 给定。
