## Traps
- TR-RULEFILE: the --vat subtotal line's exact layout lives in specs/版式说明.md (全角冒号, trailing 克), not in the script docstring (decoy: 小计行没有按 specs/版式说明.md 的写法打印)
- The scoring run also adds vats/2026-10.csv the model never saw (expect.run.hidden_files), so a script that hardcodes the visible month fails the run check too.

## Reference solution
1. Read vat_sheet.py: the docstring points the subtotal layout at specs/版式说明.md.
2. Read specs/版式说明.md: the vat subtotal prints as <缸组>：小计 <醋醅克> 克 with a full-width colon.
3. Read vats/2026-09.csv to confirm the columns.
4. Add --vat <缸组名>: filter rows to the named vat after the existing date sort and append the spec's subtotal line; leave the no-flag behaviour untouched.

## Why the answer is unique
带 --vat 西缸组 时只打印西缸组的记录并按日期排序，小计行的写法由 specs/版式说明.md 固定（全角冒号、句尾带「克」字）：西缸组：小计 11730 克。不读版式说明就写不出这一行；评分运行补进的 10 月导出多出 2026-10-10,西缸组,4160，硬编码 9 月记录同样对不上。
