## Traps
- Answer: 7364. TR-DECOY: summing complaints from every channel gives 26465.
- TR-MULTISRC: 12 files; the first one alone gives 729.
- Data volume: 12 data files, 85 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 客服/工单导出/*.csv | awk -F, '$2=="电话" && $3=="投诉" {s+=$6} END {print s}'` -> 7364
Final answer: 电话渠道投诉工单的处理时长合计 7364 分钟。

## Why the answer is unique
类别和状态都是精确字段；README 写明退款咨询不算退款，按字段精确匹配只有一个结果。
