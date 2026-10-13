## Traps
- Answer: 赵一凡. TR-DECOY: counting 处理中 together with 已升级 gives 孙悦.
- Data volume: 12 data files, 81 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 客服/工单导出/*.csv | awk -F, '$4=="已升级" {print $5}' | sort | uniq -c | sort -rn | head -3` -> 赵一凡
Final answer: 被升级工单最多的是 赵一凡。

## Why the answer is unique
类别和状态都是精确字段；README 写明退款咨询不算退款，按字段精确匹配只有一个结果。
