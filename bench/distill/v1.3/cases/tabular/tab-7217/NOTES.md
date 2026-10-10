## Traps
- TR-DATEFMT: River Gate 的终端把 entry_date 写成 MM/DD/YYYY（README 写明，其余闸口是 YYYY-MM-DD）。只按 2026-09-18 过滤会漏掉 River Gate 当天的 9 行，得 31；把 09/18/2026 的行也算进来，当天共 40 行。
- LNG: River Gate 当天的行集中在导出尾部、超出 read_file 的 64 KB 截断线。

## Reference solution
1. read_file README.md：River Gate 用 MM/DD/YYYY，其余闸口用 YYYY-MM-DD。
2. search_text "2026-09-18" 定位 ISO 行段并 read_lines，共 31 行。
3. search_text "09/18/2026" 定位 River Gate 行段（尾部）并 read_lines，共 9 行。
4. 两种写法的行互不重叠，合计 40；终答只报数字 40。

## Why the answer is unique
decoy 31 等于宣布 River Gate 当天没有人入场，与 README 写明的终端格式矛盾；两种写法的日期互不重叠，18 日之外的日子被日期条件排除。答案唯一为 40。
