## Traps
- Answer: 33425.47. TR-DECOY: including 鲜果铺二店 gives 68212.49.
- TR-MULTISRC: 10 files; the first one alone gives 4145.57.
- Data volume: 10 data files, 78 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 财务/支付流水/*.csv | awk -F, '$2=="鲜果铺" && $4=="CNY" && $5=="成功" {s+=$3} END {printf "%.2f\n", s}'` -> 33425.47
Final answer: 鲜果铺人民币成功收款合计 33425.47 元（二店不算）。

## Why the answer is unique
商户、币种、状态都是精确字段，鲜果铺二店按说明另算。
