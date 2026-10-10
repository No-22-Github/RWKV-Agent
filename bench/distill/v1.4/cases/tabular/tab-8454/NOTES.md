## Traps
- TR-MULTISRC: 教务/报名流水.csv 只有 课程号、月份、报名人数，没有「类别」；教务/课程目录.csv 有「类别」却没有数值。data_query 没有 join，要先用 教务/课程目录.csv 对「类别」做等值过滤拿到键集合（6 个），再到 教务/报名流水.csv 汇总。只看一张表答不出。
- TR-DEFN: 无额外口径坑，口径明确。
- 诱饵值：370（忽略月份条件或把不属于该课程的行也算进去）。

## Reference solution
1. data_query：path 教务/课程目录.csv，filter {"类别":"技能类"}，select 课程号 → 6 个键。
2. data_query：对 教务/报名流水.csv 汇总：group_by 课程号，operation sum，field 报名人数，filter {"月份":"2026-10"}；取这 6 个键的合计相加。
3. 用计算器核对加总 / 比较，得 128。
终答 1–2 句：给出结果 128，并说明是按 教务/课程目录.csv 里属于「技能类」的键、到 教务/报名流水.csv 汇总得出。判据：值判据（写法变体放 any）；用过 data_query；不限 read_file 次数（README、名册、流水各读一次是正常路径）。

## Changelog
- v2：S5：去掉 read_file 上限（连接题要读 README、名册/档案、流水三份文件，三遍老师全部因此判挂）；英文计数题改为 token 只认数字本身（老师写「2.」「3 Ale beers」，词表收不全）；「哪一台/哪个品种」题机台编号或货号也算对；tab-8447 判据单位由「元」改为题面问的「件」。

## Why the answer is unique
键集合由 教务/课程目录.csv 的等值过滤唯一确定（6 个键，均在 教务/报名流水.csv 中出现），每个键的数值逐行求和，没有歧义。
