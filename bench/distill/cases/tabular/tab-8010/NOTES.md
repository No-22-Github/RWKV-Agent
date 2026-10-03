## Traps
- TR-MULTISRC: 工时表没有部门列，必须用花名册把工号映射到部门。不做映射、把全公司加班加起来是 263。
- TR-DEFN: 问的是加班，类型列还有「正常」；把研发部全部工时加起来是 872.5。

## Reference solution
1. data_query：人事/花名册.csv，filter {"部门":"研发部"}，select 工号 → 9 个工号。
2. data_query：考勤/2026-09-工时.csv，filter {"类型":"加班"}，group_by 工号，operation sum，field 小时。
3. 从分组结果里取这 9 个工号的值，用计算器求和：80.5 小时。
4. （可选）读 README 确认部门以花名册为准。
终答 1–2 句：研发部 9 月加班合计 80.5 小时（工时表按工号记录，已按花名册筛出研发部 9 人、只算类型为加班的记录）。判据：包含 80.5（独立词元）；用过 data_query；read_file 最多 1 次。

## Why the answer is unique
工号唯一对应部门，类型列只有正常/加班两值，合计唯一。
