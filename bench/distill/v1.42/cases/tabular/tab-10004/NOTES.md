## Traps
- Turn 1: 46.
- Turn 2: 7.
- TR-MULTISRC: 12 files; the first one alone gives 1.
- Data volume: 12 data files, 69 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
Turn 1: bash: `cat 客服/工单导出/*.csv | awk -F, '$2=="小程序" && $3=="发票"' | wc -l` -> 46
Turn 2: bash: `cat 客服/工单导出/*.csv | awk -F, '$2=="小程序" && $3=="发票" && $4=="处理中"' | wc -l` -> 7
Final answer (last turn): 小程序发票工单里仍在处理中的有 7 张。

## Why the answer is unique
类别和状态都是精确字段；README 写明退款咨询不算退款，按字段精确匹配只有一个结果。
