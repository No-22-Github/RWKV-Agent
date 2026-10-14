## Traps
- TR-DEFN: 「不少于 20 件」含 20。按「多于 20」算会漏掉数量正好 20 的单，得 64633.10。

## Reference solution
1. data_query：path 采购/2026-09-采购单.csv，group_by 数量，operation sum，field 金额（data_query 只能按等值过滤，按数量分组后再挑 ≥20 的组）。
2. 用计算器把数量 20–40 各组的金额加起来：67649.10 元。
终答 1–2 句：数量不少于 20 件（含 20）的采购单金额合计 67649.10 元。判据：包含该金额（带或不带千分位）；用过 data_query；read_file 最多 1 次。

## Why the answer is unique
金额列已按数量×单价给出，按数量 ≥20 过滤后求和唯一。
