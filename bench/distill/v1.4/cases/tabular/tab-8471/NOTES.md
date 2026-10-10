## Traps
- TR-MULTISRC: support/resolved_daily.csv 只有 ag、mo、closed_n，没有「grp」；support/agents.csv 有「grp」却没有数值。data_query 没有 join，要先用 support/agents.csv 对「grp」做等值过滤拿到键集合（4 个），再到 support/resolved_daily.csv 汇总。只看一张表答不出。
- TR-DEFN: 阈值「不少于」含等于，边界键的合计恰好等于阈值；按「大于」算会漏掉它，得 1。
- 诱饵值：1（忽略月份条件或把不属于该agent的行也算进去）。列名不直观（ag、fullname、grp、ag、mo、closed_n），写错会得到空结果或「field missing」报错，需改正后重查。

## Reference solution
1. data_query：path support/agents.csv，filter {"grp":"Platform"}，select ag → 4 个键。
2. data_query：对 support/resolved_daily.csv 汇总：group_by ag，operation sum，field closed_n, filter {"mo":"2026-04"}；与阈值 72 比较（含等于），数出达标的键。
3. 用计算器核对加总 / 比较，得 2。
终答 1–2 句：给出结果 2，并说明是按 support/agents.csv 里属于「Platform」的键、到 support/resolved_daily.csv 汇总得出。判据：值判据（写法变体放 any）；用过 data_query；不限 read_file 次数（README、名册、流水各读一次是正常路径）。

## Changelog
- v2：S5：去掉 read_file 上限（连接题要读 README、名册/档案、流水三份文件，三遍老师全部因此判挂）；英文计数题改为 token 只认数字本身（老师写「2.」「3 Ale beers」，词表收不全）；「哪一台/哪个品种」题机台编号或货号也算对；tab-8447 判据单位由「元」改为题面问的「件」。

## Why the answer is unique
键集合由 support/agents.csv 的等值过滤唯一确定（4 个键，均在 support/resolved_daily.csv 中出现），每个键的数值逐行求和，没有歧义，表头已在 README 中说明。
