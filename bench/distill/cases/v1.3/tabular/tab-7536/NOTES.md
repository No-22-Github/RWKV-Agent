## Traps
- TR-DATEFMT: Bowness Marina 的导出把 hire_date 写成 MM/DD/YYYY（README 写明，其余网点是 YYYY-MM-DD）。只按 2026-08-22 过滤会漏掉 Bowness Marina 当天的行，得 1067.60；正确答案要把 08/22/2026 的行也算进来，合计 1924.25。

## Reference solution
1. 读 README.md：Bowness Marina 用 MM/DD/YYYY，其余网点用 YYYY-MM-DD。
2. 查询一：{"path":"data/boat_hire_2026-08.csv","filter":{"hire_date":"2026-08-22"},"operation":"sum","field":"fee_gbp"}，得 1067.60。
3. 查询二：同一文件 filter {"hire_date":"08/22/2026"} 再求和，两次结果相加得 1924.25。
4. 终答只报数字 1924.25。

## Why the answer is unique
decoy 1067.60 只覆盖 ISO 日期的网点，等于宣布 Bowness Marina 当天没有收入，与 README 写明的导出格式矛盾；两种写法的行互不重叠，22 日之外的日子被日期条件排除。答案唯一为 1924.25。
