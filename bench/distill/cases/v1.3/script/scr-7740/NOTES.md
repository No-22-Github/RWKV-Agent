## Traps
- None declared. The scoring run adds intakes/2026-10.csv the model never saw (expect.run.hidden_files), so a script that hardcodes what it read during exploration fails the run check.

## Reference solution
1. Read intake.py: the docstring fixes the sheet layout (per day: count, jin, yuan, then 总计).
2. Read intakes/2026-09.csv to confirm the export columns.
3. Write intake.py: sweep intakes/*.csv, aggregate per 日期, print in date order, then the 总计 line.

## Why the answer is unique
收茧单按日期排序、每天一行：2026-09-02 两笔 78 斤 10140 元，其余三天各一笔，评分运行补进的 10 月导出再加三行，表尾停在 总计,8,293,38090。版式由脚本说明固定，漏读新导出或改动列序都会得到不同的单。
