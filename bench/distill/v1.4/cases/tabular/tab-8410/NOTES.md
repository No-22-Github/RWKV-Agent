## Traps
- TR-DATEFMT: 下单日期 列混了 2026/06/xx、dd-06-2026（日-月-年，README 说明）、Jun d, 2026、ISO 时间四种写法。把日-月-年读成月-日-年，范围内这类行会被算到别的月份，得到 9535。

## Reference solution
1. data_query：path 订单/花店订单.csv， filter {"品类":"绿植"}, group_by 下单日期，operation sum, field 金额，得到各日期写法的分组结果（不超过 40 组）。
2. 按 README 的口径把每组归一到 6 月几日，挑出 3 日到 8 日（含）的 19 组。
3. 用计算器把各组的数值相加核对，得 11864。
终答 1–2 句：给出 11864 元，并说明日期列写法不统一、日-月-年已按 README 归一后再求和。判据：值判据（写法变体放 any）；read_file 最多 2 次（README + 表）。

## Changelog
- v2：S5：去掉 required data_query（表里日期混用三四种写法，data_query 只做等值筛选、没法归一日期，老师整读后按日期归并手算才是对的路径）；read_file 上限 1→2（README 说明日期写法，先读 README 再读表是正常路径）；计数题词表补「N 个 / N 条」；终答上限 500→600。

## Why the answer is unique
README 规定了短日期的读法，ISO 时间固定为 UTC 08:00、落在同一天，每个日期单元格都能唯一归到 6 月某日；范围含两端，类别用等值过滤，结果唯一。
