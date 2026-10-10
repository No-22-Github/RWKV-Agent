## Traps
- TR-MULTISRC: 订单/团购订单.csv 只有 团长号、月份、订单数，没有「片区」；团长/团长名单.csv 有「片区」却没有数值。data_query 没有 join，要先用 团长/团长名单.csv 对「片区」做等值过滤拿到键集合（5 个），再到 订单/团购订单.csv 汇总。只看一张表答不出。
- TR-DEFN: 无额外口径坑，口径明确。
- 诱饵值：1043（忽略月份条件或把不属于该团长的行也算进去）。

## Reference solution
1. data_query：path 团长/团长名单.csv，filter {"片区":"东区"}，select 团长号 → 5 个键。
2. data_query：对 订单/团购订单.csv 汇总：group_by 团长号，operation sum，field 订单数，filter {"月份":"2026-10"}；取这 5 个键的合计相加。
3. 用计算器核对加总 / 比较，得 423。
终答 1–2 句：给出结果 423，并说明是按 团长/团长名单.csv 里属于「东区」的键、到 订单/团购订单.csv 汇总得出。判据：值判据（写法变体放 any）；用过 data_query；不限 read_file 次数（README、名册、流水各读一次是正常路径）。

## Changelog
- v2：S5：去掉 read_file 上限（连接题要读 README、名册/档案、流水三份文件，三遍老师全部因此判挂）；英文计数题改为 token 只认数字本身（老师写「2.」「3 Ale beers」，词表收不全）；「哪一台/哪个品种」题机台编号或货号也算对；tab-8447 判据单位由「元」改为题面问的「件」。

## Why the answer is unique
键集合由 团长/团长名单.csv 的等值过滤唯一确定（5 个键，均在 订单/团购订单.csv 中出现），每个键的数值逐行求和，没有歧义。
