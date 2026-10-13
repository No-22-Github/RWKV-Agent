## Traps
- Answer: 199. TR-DECOY: including 退款咨询 gives 362.
- TR-MULTISRC: 12 files; the first one alone gives 14.
- Data volume: 12 data files, 83 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 客服/工单导出/*.csv | awk -F, '$3=="退款" && $6>120 {print $1}' | sort -u | wc -l` -> 199
Final answer: 超过 120 分钟的退款工单有 199 个不同工单号。

## Why the answer is unique
类别和状态都是精确字段；README 写明退款咨询不算退款，按字段精确匹配只有一个结果。
