## Traps
- Answer: 87.
- TR-MULTISRC: 10 files; the first one alone gives 11.
- Data volume: 10 data files, 78 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 财务/支付流水/*.csv | awk -F, '$5=="退款" && $6=="小程序"' | wc -l` -> 87
Final answer: 小程序退款 87 笔。

## Why the answer is unique
商户、币种、状态都是精确字段，鲜果铺二店按说明另算。
