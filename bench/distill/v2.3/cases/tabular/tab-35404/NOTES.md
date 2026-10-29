## Traps
- TR-DECOY: the tool the task naturally needs is not in this catalog (never_offer: data_query).

## Reference solution
bash: awk -F, '$2=="P6"{s+=$3;n++} END{printf "%.1f\n", s/n}' 人事/技术部薪资明细-2026.csv -> 21981.8

## Why the answer is unique
24 行，筛 P6 求平均；入职年份列是干扰。

Expected: 21981.8 | 21,981.80
