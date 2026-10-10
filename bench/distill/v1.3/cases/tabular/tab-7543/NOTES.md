## Traps
- TR-DATEFMT: Dock Side 的票写 DD/MM/YYYY（README 写明，其余片区是 YYYY-MM-DD）。只按 2026-09-05 过滤会漏掉 Dock Side 当天的摊位，得 17 家；把 05/09/2026 的行也算进来，5 日当天不同的摊贩共 23 家。

## Reference solution
1. 读 README.md：Dock Side 用 DD/MM/YYYY，其余片区用 YYYY-MM-DD。
2. 查询一：{"path":"data/stalls_2026-09.csv","filter":{"trade_date":"2026-09-05"},"operation":"distinct_count","field":"vendor_code"}，得 17.0。
3. 查询二：同一文件 filter {"trade_date":"05/09/2026"} 再做 distinct_count，与上一步合并去重后得 23.0。
4. 终答只报数字 23.0。

## Why the answer is unique
decoy 17 等于宣布 Dock Side 当天没人出摊，与 README 写明的日期格式矛盾；两种写法的票互不重叠，5 日之外的日子被日期条件排除。答案唯一为 23.0。
