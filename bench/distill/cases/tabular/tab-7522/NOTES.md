## Traps
- TR-DECOY: data/drink_sales.csv 里「桂花轻乳」与目标系列「桂花乌龙」相邻。把轻乳的行（或两系列一起）求和会得到 704.18。7 月与 9 月的行是月份干扰项。

## Reference solution
1. data_query: {"path":"data/drink_sales.csv","filter":{"销售月份":"2026-08","饮品系列":"桂花乌龙"},"operation":"sum","field":"销售额"} -> 950.73。
2. 终答只报数字 950.73。

## Why the answer is unique
decoy 704.18 是「桂花轻乳」的合计，但题面点名「桂花乌龙」，README 写明两条系列分开统计，每行只属于一个系列，不存在混算的读法。7 月与 9 月的行被月份条件排除。答案只有 950.73。
