## Traps
- TR-DATEFMT: 收件日 列混了 2026/07/xx、dd-07-2026（日-月-年，README 说明）、Jul d, 2026、ISO 时间四种写法。把日-月-年读成月-日-年，范围内这类行会被算到别的月份，得到 4902。
- TR-HEADER: 列名不直观（任务号、收件日、纸张、页数），写错列名会报 field missing，需改正后重查。

## Reference solution
1. data_query：path 接单/打印任务.csv， group_by 收件日，operation sum, field 页数，得到各日期写法的分组结果（不超过 40 组）。
2. 按 README 的口径把每组归一到 7 月几日，挑出 3 日到 5 日（含）的 12 组。
3. 用计算器把各组的数值相加核对，得 6274。
终答 1–2 句：给出 6274 页，并说明日期列写法不统一、日-月-年已按 README 归一后再求和。判据：值判据（写法变体放 any）；read_file 最多 2 次（README + 表）。

## Changelog
- v2：S5：去掉 required data_query（表里日期混用三四种写法，data_query 只做等值筛选、没法归一日期，老师整读后按日期归并手算才是对的路径）；read_file 上限 1→2（README 说明日期写法，先读 README 再读表是正常路径）；计数题词表补「N 个 / N 条」；终答上限 500→600。

## Why the answer is unique
README 规定了短日期的读法，ISO 时间固定为 UTC 08:00、落在同一天，每个日期单元格都能唯一归到 7 月某日；范围含两端，结果唯一。
