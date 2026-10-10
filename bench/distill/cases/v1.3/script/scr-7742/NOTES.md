## Traps
- TR-SIGN: shops/*.csv records 退货 rows with positive amounts; the balance nets them minus, per README (decoy: 退货金额按正数加进了应收)
- The scoring run also adds shops/2026-10.csv the model never saw (expect.run.hidden_files), so a script that hardcodes the visible month fails the run check too.

## Reference solution
1. Read ledger.py: the docstring defines the --balance output (one line per shop, first-appearance order).
2. Read README.md: 退货 rows carry positive amounts and the balance nets them minus.
3. Read shops/2026-09.csv to confirm the 类目 values.
4. Add --balance: net each shop's 销货 plus and 退货 minus and print the balance lines; leave the no-flag behaviour untouched.

## Why the answer is unique
README 规定退货行金额也记成正数、应收按销货加、退货减：河湾饭庄 3180+2900-240=5840，南门食堂 1950-180=1770，西街早铺 5100；把退货当销货加进去就得到 6080/2130。评分运行补进的 10 月导出再改三家应收，表尾是 南门食堂,3980，先后顺序按第一次记账固定。
