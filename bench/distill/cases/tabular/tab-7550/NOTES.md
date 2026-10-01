## Traps
- TR-DATEFMT: Pelican Bay 的日期写 DD/MM/YYYY（README 写明，其余船东是 YYYY-MM-DD）。只按 2026-09-05 过滤会漏掉 Pelican Bay 当天的渔获，当日最高变成别家船东的 1818.70；把 05/09/2026 的行算进来，当日最高是 Pelican Bay，共 5022.75。

## Reference solution
1. 读 README.md：Pelican Bay 用 DD/MM/YYYY，其余船东用 YYYY-MM-DD。
2. 查询一：{"path":"data/landings_2026-09.csv","filter":{"landing_date":"2026-09-05"},"operation":"sum","field":"value_gbp","group_by":"operator"}。
3. 查询二：同一文件 filter {"landing_date":"05/09/2026"} 再分组求和；合并后当日最高是 Pelican Bay，共 5022.75。
4. 终答只报数字 5022.75。

## Why the answer is unique
decoy 1818.70 漏掉了 Pelican Bay 当天的渔获，与 README 写明的日期格式矛盾；两种写法的行互不重叠，5 日之外的日子被日期条件排除。答案唯一为 5022.75。
