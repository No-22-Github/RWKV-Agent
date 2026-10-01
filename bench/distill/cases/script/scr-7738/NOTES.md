## Traps
- None declared. The scoring run adds vats/2026-10.csv the model never saw (expect.run.hidden_files), so a script that hardcodes what it read during exploration fails the run check.

## Reference solution
1. Read vat_log.py: pandas only concatenates, groups by 缸组 and sums.
2. Read vats/2026-09.csv to confirm the columns.
3. Rewrite vat_log.py with csv + glob: per 缸组 a count and a grams sum in name order, then 总计.

## Why the answer is unique
汇总表按缸组名排序、每组一行：东缸组 3 笔 13050 克，中缸组 8000 克，西缸组 10650 克，评分运行补进的 10 月导出让表尾停在 总计,9,31700。版式由脚本说明固定，重写必须逐字节一致，漏读新导出或改排序都会得到不同的表。
