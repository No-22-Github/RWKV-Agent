## Traps
- Answer: 老张面馆.
- Data volume: 10 data files, 80 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 财务/支付流水/*.csv | awk -F, '$5=="失败" {print $2}' | sort | uniq -c | sort -rn | head -3` -> 老张面馆
Final answer: 失败最多的是 老张面馆。

## Why the answer is unique
商户、币种、状态都是精确字段，鲜果铺二店按说明另算。
