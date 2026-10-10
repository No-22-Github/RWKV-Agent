## Traps
- TR-MULTISRC: dispatch/dispatch_log.csv 只有 bc、mo、cs，没有「stl」；catalogue/beers.csv 有「stl」却没有数值。data_query 没有 join，要先用 catalogue/beers.csv 对「stl」做等值过滤拿到键集合（5 个），再到 dispatch/dispatch_log.csv 汇总。只看一张表答不出。
- TR-DEFN: 单价在 catalogue/beers.csv 的第 4 列，按数量不乘价会得到数量合计。
- 诱饵值：40872（忽略月份条件或把不属于该beer的行也算进去）。列名不直观（bc、label、stl、bc、mo、cs），写错会得到空结果或「field missing」报错，需改正后重查。

## Reference solution
1. data_query：path catalogue/beers.csv，filter {"stl":"Lager"}，select bc → 5 个键。
2. data_query：对 dispatch/dispatch_log.csv 汇总：group_by bc，operation sum，field cs, filter {"mo":"2026-05"}；每个键的合计乘 catalogue/beers.csv 表里的单价后相加。
3. 用计算器核对加总 / 比较，得 13309。
终答 1–2 句：给出结果 13309，并说明是按 catalogue/beers.csv 里属于「Lager」的键、到 dispatch/dispatch_log.csv 汇总得出。判据：值判据（写法变体放 any）；用过 data_query；不限 read_file 次数（README、名册、流水各读一次是正常路径）。

## Changelog
- v2：S5：去掉 read_file 上限（连接题要读 README、名册/档案、流水三份文件，三遍老师全部因此判挂）；英文计数题改为 token 只认数字本身（老师写「2.」「3 Ale beers」，词表收不全）；「哪一台/哪个品种」题机台编号或货号也算对；tab-8447 判据单位由「元」改为题面问的「件」。

## Why the answer is unique
键集合由 catalogue/beers.csv 的等值过滤唯一确定（5 个键，均在 dispatch/dispatch_log.csv 中出现），每个键的数值逐行求和，没有歧义，表头已在 README 中说明。
