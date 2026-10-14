## Traps
- TR-NUMFMT: batches/*.csv writes 金额元 like 2,160 with a separator; int() on the raw cell crashes (decoy: int() 直接读带分节号的金额报 ValueError)
- The scoring run also adds batches/2026-10.csv the model never saw (expect.run.hidden_files), so a script that hardcodes the visible month fails the run check too.

## Reference solution
1. List the workspace to see the export and README.
2. Read day_tofu.py: pandas reads the amounts with thousands=','.
3. Read README.md: the 金额元 column carries separators such as 2,160.
4. Read batches/2026-09.csv to confirm the grouped amounts.
5. Rewrite day_tofu.py with csv + glob: strip the separators from 金额元, aggregate per 日期, print in date order, then 总计.

## Why the answer is unique
金额一栏带分节号，重写必须先剥掉再求和：2026-09-02 两炉 64 板 3840 元，评分运行补进的 10 月导出再加两天，表尾停在 总计,282,16920。版式由脚本说明固定；直接 int('2,160') 当场报错，漏掉分节号会得到 100 倍的错值。
