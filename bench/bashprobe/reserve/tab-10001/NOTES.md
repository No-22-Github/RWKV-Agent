## Traps
- Answer: 167. TR-DECOY: counting 退款咨询 as refunds gives 307.
- TR-MULTISRC: 12 files; the first one alone gives 14.
- Data volume: 12 data files, 70 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 客服/工单导出/*.csv | awk -F, '$3=="退款" && $4=="已解决"' | wc -l` -> 167
Final answer: 已解决的退款工单共 167 张（类别精确等于「退款」，退款咨询不算）。

## Why the answer is unique
类别和状态都是精确字段；README 写明退款咨询不算退款，按字段精确匹配只有一个结果。
