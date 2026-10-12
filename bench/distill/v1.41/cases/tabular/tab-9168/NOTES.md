## Traps
- TR-DECOY: 「PM2.5-校准」 rows are instrument self-test signals with values up to 999; a substring match on PM2.5 gives 999. 传感器/说明.md pins exact matching.
- PM10 readings are larger too, so the maximum of the value column overall is higher.

## Reference solution
1. bash: `cat 传感器/*.tsv | awk -F'\t' '$2=="PM2.5" && $3+0>m {m=$3+0} END{print m}'`
Final answer: PM2.5 的最大读数是 188（只算指标恰好是 PM2.5 的行，校准信号不算）。

## Why the answer is unique
The metric is an exact column value and the maximum 188 is reached by exactly one row.

## Five alternative phrasings of the task
1. 传感器记录里，指标为 PM2.5 的读数最大是多少？口径见 传感器/说明.md。
2. 四个站点的数据里，PM2.5 的峰值是多少？按说明.md，校准信号不算。
3. 找出 传感器 目录下所有站点中 PM2.5 的最高读数。
4. 所有站点里 PM2.5 这个指标出现过的最大数值是几？
5. 按 传感器/说明.md 的规则，PM2.5 最大值多少？
