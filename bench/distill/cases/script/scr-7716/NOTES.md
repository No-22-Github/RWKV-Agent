## Traps
- None declared. The scoring run adds a second monthly file the model never saw (expect.run.hidden_files, kept inside bills/), so a top-3 computed from September's rows alone prints 牛肉面,255 / 阳春面,115 / 担担面,99 and misses the October bowls.

## Reference solution
1. 读 menu.py：榜单的口径与排序已定。
2. 读 bills/2026-09.csv，确认导出列。
3. 给 menu.py 加 --top 参数：带值时只打印榜单前 N 行（排序照旧、不带合计行），不带值或加值以外的调用保持现状。

## Why the answer is unique
合并两份导出（跑分时会再放入 bills/2026-10.csv）后，前 3 名正好是 牛肉面,343 / 阳春面,181 / 担担面,99，三行之外没有别的内容。排名由碗数决定，四个品类的名次之间没有并列；只按 9 月算的榜单是 牛肉面,255 / 阳春面,115 / 担担面,99，数值与期望输出不同；不加参数时的旧行为被题面钉死为逐字不变。
